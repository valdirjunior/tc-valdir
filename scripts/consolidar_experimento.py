#!/usr/bin/env python3
"""Consolida baseline_v1 sem executar SUMO nem modificar arquivos de entrada.

Python >= 3.10, somente biblioteca padrão. Protocolo 0.2, SUMO 1.27.1.
Uma falha impede a publicação de bases parciais como se fossem completas.
"""
from __future__ import annotations

import argparse
import ast
import csv
import hashlib
import json
import math
import re
import statistics
import sys
import time
import xml.etree.ElementTree as ET
import zipfile
from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal, ROUND_FLOOR
from pathlib import Path

VERSION = "1.0.0"
PROTOCOL = "0.2"
SCENARIOS = ("REF", "EQU", "CAU", "AGR", "MIX_C", "MIX_N", "MIX_A")
SEEDS = tuple(range(1000, 1030))
DEMANDS = (300, 450, 625)
HORIZONS = (600, 1800)
TYPES = ("cauteloso", "normal", "agressivo")
REQUIRED = ("tripinfo.xml", "stats.xml", "summary.xml", "queues.xml",
            "rotas.rou.xml", "collisions.xml", "warnings.log", "sumo.log",
            "execucao.txt", "EXECUCAO_OK.txt")
FIELDS: dict[str, dict] = {}


class DataError(ValueError):
    pass


def require(condition, message):
    if not condition:
        raise DataError(message)


def xml(path):
    try:
        return ET.parse(path).getroot()
    except (ET.ParseError, OSError) as exc:
        raise DataError(f"XML ausente ou inválido ({path.name}): {exc}") from exc


def read_text(path):
    return path.read_text(encoding="utf-8-sig")


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def number(element, attribute):
    try:
        value = float(element.attrib[attribute])
    except (KeyError, ValueError) as exc:
        raise DataError(f"Campo numérico ausente/inválido: {element.tag}@{attribute}") from exc
    require(math.isfinite(value), f"Valor não finito: {element.tag}@{attribute}")
    return value


def integer(element, attribute):
    value = number(element, attribute)
    require(value >= 0 and value.is_integer(), f"Contagem inválida: {element.tag}@{attribute}")
    return int(value)


def quantile(values, probability):
    """Quantil com interpolação linear entre estatísticas de ordem."""
    require(bool(values), "Quantil sem observações")
    ordered = sorted(values)
    index = (len(ordered) - 1) * probability
    lower = math.floor(index)
    upper = math.ceil(index)
    return ordered[lower] + (ordered[upper] - ordered[lower]) * (index - lower)


def count_arrivals(arrivals, horizon):
    """Janela fechada à esquerda e aberta à direita, sem arredondar chegadas."""
    return sum(0 <= arrival < horizon for arrival in arrivals)


def set_field(row, name, value, unit, definition, role="complementar"):
    row[name] = value
    FIELDS[name] = {"unidade": unit, "definicao": definition, "papel": role}


def distribution(row, prefix, values, label, primary=False):
    for suffix, value, definition in (
        ("mean_s", statistics.fmean(values), f"Média entre viagens: {label}"),
        ("median_s", statistics.median(values), f"Mediana entre viagens: {label}"),
        ("sd_within_run_s", statistics.pstdev(values), f"Desvio-padrão populacional entre viagens (divisor N): {label}"),
        ("p95_s", quantile(values, 0.95), f"Percentil 95 linear entre viagens: {label}"),
    ):
        set_field(row, f"{prefix}_{suffix}", value, "s", definition,
                  "principal" if primary and suffix == "mean_s" else "complementar")


def canonical(element, ignore_type=False):
    attrs = tuple(sorted((k, v) for k, v in element.attrib.items()
                         if not (ignore_type and k == "type")))
    return element.tag, attrs, (element.text or "").strip(), tuple(canonical(c) for c in element)


def vehicle_map(path):
    vehicles = xml(path).findall("vehicle")
    result = {}
    for vehicle in vehicles:
        ident = vehicle.get("id")
        require(ident is not None and ident not in result, f"ID ausente/duplicado em {path.name}: {ident}")
        require(vehicle.find("route") is not None, f"Rota inline ausente para {ident} em {path.name}")
        result[ident] = vehicle
    require(bool(result), f"Nenhum veículo em {path.name}")
    return result


def composition_counts(total, composition):
    raw = [(name, Decimal(str(weight)) * total) for name, weight in composition]
    counts = {name: int(value.to_integral_value(rounding=ROUND_FLOOR)) for name, value in raw}
    remainder = total - sum(counts.values())
    order = sorted(raw, key=lambda item: item[1] - counts[item[0]], reverse=True)
    for name, _ in order[:remainder]:
        counts[name] += 1
    return {name: counts.get(name, 0) for name in TYPES}


@dataclass
class Lane:
    ident: str
    edge: str
    category: str
    length: float
    name: str
    origin: str
    destination: str


@dataclass
class Accumulator:
    total: float = 0.0
    positive: int = 0
    maximum: float = 0.0
    max_time: float | None = None
    max_lane: str = ""

    def add(self, value, timestamp, lane=""):
        self.total += value
        self.positive += int(value > 0)
        if value > self.maximum:
            self.maximum, self.max_time, self.max_lane = value, timestamp, lane


def load_snapshot(base):
    folder = base / "_config_snapshot"
    manifest = read_text(base / "manifesto.txt")
    require("Eclipse SUMO sumo 1.27.1" in manifest, "Manifesto não identifica SUMO 1.27.1")
    hashes = {}
    mapping = {"rede": "nereu_ramos.net.xml", "demanda": "demanda_v2.json",
               "perfis": "perfis_final.add.xml", "gerador_demanda": "gerar_demanda_v2.py",
               "atribuidor_perfis": "atribuir_perfis.py"}
    for key, name in mapping.items():
        match = re.search(rf"^{key} = ([A-Fa-f0-9]{{64}})\s*$", manifest, re.M)
        require(match is not None, f"Hash ausente no manifesto: {key}")
        value = sha256(folder / name)
        require(value == match.group(1).lower(), f"Snapshot diverge do manifesto: {name}")
        hashes[name] = value
    # Apenas ler dados literais; nunca executar código Python do snapshot.
    syntax = ast.parse(read_text(folder / "atribuir_perfis.py"))
    compositions = None
    for node in syntax.body:
        if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "COMPOSICOES" for t in node.targets):
            compositions = ast.literal_eval(node.value)
    require(isinstance(compositions, dict) and set(compositions) == set(SCENARIOS), "Composições do snapshot não correspondem à matriz oficial")
    for scenario, composition in compositions.items():
        require(all(name in TYPES and weight > 0 for name, weight in composition), f"Composição inválida: {scenario}")
        require(abs(sum(weight for _, weight in composition) - 1) < 1e-9, f"Pesos não somam 1: {scenario}")
    lanes = {}
    for edge in xml(folder / "nereu_ramos.net.xml").findall("edge"):
        category = "internal" if edge.get("function") == "internal" else "external"
        for lane in edge.findall("lane"):
            allow = set((lane.get("allow") or "").split())
            disallow = set((lane.get("disallow") or "").split())
            if (allow and not {"all", "passenger"}.intersection(allow)) or "passenger" in disallow or "all" in disallow:
                continue
            ident = lane.get("id")
            require(ident is not None and ident not in lanes, "ID de faixa ausente/duplicado no snapshot")
            lanes[ident] = Lane(ident, edge.get("id", ""), category, number(lane, "length"),
                               edge.get("name", ""), edge.get("from", ""), edge.get("to", ""))
    require(bool(lanes), "Nenhuma faixa passenger elegível no snapshot")
    return lanes, compositions, hashes


def load_registry(base):
    with (base / "registro_execucoes.csv").open(encoding="utf-8-sig", newline="") as handle:
        result = {}
        for entry in csv.DictReader(handle, delimiter=";"):
            key = int(entry["seed"]), int(entry["fluxo"]), entry["cenario"]
            require(key not in result, f"Chave duplicada no registro: {key}")
            require(entry["status"] == "OK" and entry["exit_code"] == "0", f"Execução não OK no registro: {key}")
            result[key] = entry
    expected = {(s, d, c) for s in SEEDS for d in DEMANDS for c in SCENARIOS}
    require(set(result) == expected, f"Registro não corresponde às 630 chaves oficiais (observadas {len(result)})")
    return result


def discover(base, sample):
    present = {}
    for seed_folder in base.glob("seed_*"):
        require(seed_folder.is_dir(), f"Entrada inesperada: {seed_folder.name}")
        seed = int(seed_folder.name.removeprefix("seed_"))
        require(seed in SEEDS, f"Seed fora da matriz: {seed}")
        for demand_folder in seed_folder.glob("fluxo_*"):
            demand = int(demand_folder.name.removeprefix("fluxo_"))
            require(demand in DEMANDS, f"Demanda fora da matriz: {demand}")
            for folder in demand_folder.iterdir():
                if folder.is_dir() and folder.name != "demanda":
                    require(folder.name in SCENARIOS, f"Cenário desconhecido: {folder.name}")
                    present[(seed, demand, folder.name)] = folder
    expected = {(s, d, c) for s in SEEDS for d in DEMANDS for c in SCENARIOS}
    require(bool(present), "Nenhuma execução disponível")
    missing = sorted(expected - set(present))
    require(sample or not missing,
            f"Coleta incompleta: {len(present)}/630 diretórios; faltam {len(missing)}. "
            "Para examinar uma amostra explicitamente, use --modo-amostra.")
    return [(key, present[key]) for key in sorted(present, key=lambda k: (k[0], k[1], SCENARIOS.index(k[2])))], missing


def check_configuration(folder, key):
    metadata = dict(line.split("=", 1) for line in read_text(folder / "execucao.txt").splitlines() if "=" in line)
    require((int(metadata["seed"]), int(metadata["fluxo"]), metadata["cenario"]) == key,
            "Metadados execucao.txt divergem do diretório")
    for name, value in {"sim_end": 1800, "demand_begin": 0, "demand_end": 600, "step_length": 0.1}.items():
        require(float(metadata[name]) == value, f"Configuração inesperada em execucao.txt: {name}")
    # A configuração registrada no cabeçalho de stats.xml é um comentário XML.
    text = read_text(folder / "stats.xml")
    require("Eclipse SUMO sumo 1.27.1" in text, "Cabeçalho de stats.xml não identifica SUMO 1.27.1")
    match = re.search(r"<sumoConfiguration\b.*?</sumoConfiguration>", text, re.S)
    require(match is not None, "Configuração gerada ausente no cabeçalho de stats.xml")
    configuration = ET.fromstring(match.group())
    expected = {"begin": "0", "end": "1800", "step-length": "0.1",
                "queue-output.period": "1", "summary-output.period": "1",
                "time-to-teleport": "-1", "time-to-impatience": "45",
                "tripinfo-output.write-unfinished": "true",
                "collision.action": "warn", "collision.check-junctions": "true", "seed": str(key[0])}
    for tag, value in expected.items():
        node = configuration.find(f".//{tag}")
        require(node is not None and node.get("value") == value, f"Configuração inesperada no cabeçalho: {tag}")
    for name in ("tripinfo.xml", "queues.xml", "summary.xml", "collisions.xml"):
        require("Eclipse SUMO sumo 1.27.1" in read_text(folder / name)[:500], f"Versão inesperada no cabeçalho de {name}")


def trips_metrics(folder, key, composition, row):
    seed, demand, scenario = key
    base_routes = vehicle_map(folder.parent / "demanda" / "base.rou.xml")
    routes = vehicle_map(folder / "rotas.rou.xml")
    require(len(base_routes) == demand and set(base_routes) == set(routes), "IDs/quantidade das rotas divergem da demanda-base")
    for ident in routes:
        require(canonical(routes[ident], True) == canonical(base_routes[ident], True), f"Partida/rota programada mudou: veículo {ident}")
        require(0 <= number(routes[ident], "depart") < 600, f"Partida programada fora de [0,600): {ident}")
    type_counts = Counter(v.get("type") for v in routes.values())
    require(dict(type_counts) == {k: v for k, v in composition_counts(demand, composition).items() if v},
            f"Quantidades de perfis divergem do atribuidor: {dict(type_counts)}")
    vehicles = xml(folder / "tripinfo.xml").findall("tripinfo")
    ident_counts = Counter(v.get("id") for v in vehicles)
    require(len(vehicles) == demand and len(ident_counts) == demand and set(ident_counts) == set(routes), "IDs/contagem de tripinfo divergem da demanda")
    values = {name: [] for name in ("duration", "routeLength", "waitingTime", "departDelay", "timeLoss", "arrival", "depart", "waitingCount")}
    for trip in vehicles:
        ident = trip.get("id")
        require(trip.get("vType") == routes[ident].get("type"), f"Perfil de tripinfo diverge da rota: {ident}")
        require(trip.get("vaporized") == "", f"Veículo removido ou campo vaporized ausente: {ident}")
        for name in values:
            value = number(trip, name)
            require(value >= 0, f"Viagem inacabada/valor negativo: {ident}/{name}")
            values[name].append(value)
        duration, arrival, depart = values["duration"][-1], values["arrival"][-1], values["depart"][-1]
        require(duration > 0 and values["routeLength"][-1] > 0, f"Duração/distância não positiva: {ident}")
        require(arrival < 1800 + 1e-8, f"Chegada após o horizonte integral: {ident}")
        require(abs(arrival - depart - duration) <= 0.015, f"Duração incoerente: {ident}")
        require(abs(depart - number(routes[ident], "depart") - values["departDelay"][-1]) <= 0.015, f"departDelay incoerente: {ident}")
        require(values["waitingTime"][-1] <= duration + 0.01, f"Espera excede duração: {ident}")
        require(number(trip, "stopTime") == 0, f"Parada programada inesperada: {ident}")
    set_field(row, "trip_count", demand, "veículos", "Viagens concluídas e IDs conferidos", "controle")
    for name in TYPES:
        set_field(row, f"profile_{name}_count", type_counts[name], "veículos", f"Quantidade efetivamente atribuída de {name}", "controle")
        set_field(row, f"profile_{name}_pct", 100 * type_counts[name] / demand, "%", f"Composição efetivamente atribuída de {name}", "controle")
    distribution(row, "travel_time", values["duration"], "duration", True)
    distribution(row, "waiting_time", values["waitingTime"], "waitingTime", True)
    distribution(row, "depart_delay", values["departDelay"], "departDelay")
    system = [a + b for a, b in zip(values["duration"], values["departDelay"])]
    set_field(row, "system_time_mean_s", statistics.fmean(system), "s", "Média de duration + departDelay")
    set_field(row, "time_loss_mean_s", statistics.fmean(values["timeLoss"]), "s", "Média de timeLoss; referencial individual inclui speedFactor")
    speeds = [length / duration for length, duration in zip(values["routeLength"], values["duration"])]
    set_field(row, "trip_speed_mean_mps", statistics.fmean(speeds), "m/s", "Média aritmética de routeLength/duration por veículo", "principal")
    set_field(row, "aggregate_trip_speed_mps", sum(values["routeLength"]) / sum(values["duration"]), "m/s", "Distância total/tempo acumulado das viagens")
    set_field(row, "route_length_mean_m", statistics.fmean(values["routeLength"]), "m", "Comprimento médio efetivamente percorrido", "controle")
    set_field(row, "vehicles_with_waiting_pct", 100 * sum(w > 0 for w in values["waitingTime"]) / demand, "%", "Percentual das viagens com waitingTime > 0")
    set_field(row, "waiting_share_pct", 100 * sum(values["waitingTime"]) / sum(values["duration"]), "%", "Tempo parado total/duração total das viagens")
    set_field(row, "waiting_count_mean", statistics.fmean(values["waitingCount"]), "episódios/viagem", "Média de waitingCount")
    last = max(values["arrival"])
    set_field(row, "last_arrival_s", last, "s", "Instante da última chegada, não fim configurado")
    set_field(row, "network_clearance_after600_s", max(0.0, last - 600), "s", "Drenagem da coorte após 600 s, com toda a demanda concluída")
    for horizon in HORIZONS:
        count = count_arrivals(values["arrival"], horizon)
        set_field(row, f"completed_count_0_{horizon}", count, "veículos", f"Chegadas com 0 <= arrival < {horizon}", "controle")
        set_field(row, f"completion_flow_vph_0_{horizon}", count / horizon * 3600, "veículos/h", f"Taxa equivalente de conclusões em [0,{horizon}); não capacidade",
                  "principal" if horizon == 600 else "complementar")
        set_field(row, f"completed_share_pct_0_{horizon}", count / demand * 100, "%", f"Fração da demanda concluída em [0,{horizon})")
    route_fingerprint = sha256(folder.parent / "demanda" / "base.rou.xml")
    set_field(row, "demand_base_sha256", route_fingerprint, "SHA256", "Hash da demanda-base do bloco seed/demanda", "controle")
    return values, speeds


BRAKING = re.compile(r"Vehicle '([^']+)' performs emergency braking .*?time=([-+]?\d+(?:\.\d+)?(?:[eE][-+]?\d+)?)\.")


def stats_and_summary(folder, key, row, values, speeds, warnings):
    root = xml(folder / "stats.xml")
    vehicles, trips, safety, teleports, performance = (root.find(tag) for tag in ("vehicles", "vehicleTripStatistics", "safety", "teleports", "performance"))
    require(all(node is not None for node in (vehicles, trips, safety, teleports, performance)), "Elementos obrigatórios ausentes de stats.xml")
    for attribute in ("loaded", "inserted"):
        require(integer(vehicles, attribute) == key[1], f"stats/vehicles@{attribute} diverge da demanda")
    require(integer(vehicles, "running") == 0 and integer(vehicles, "waiting") == 0, "Veículos ativos ou não inseridos ao final")
    require(integer(trips, "count") == key[1], "População das estatísticas diverge de tripinfo")
    require(number(performance, "begin") == 0 and number(performance, "end") == 1800, "Horizonte de stats.xml divergente")
    for attribute in ("duration", "routeLength", "waitingTime", "departDelay", "timeLoss", "speed"):
        calculated = statistics.fmean(speeds if attribute == "speed" else values[attribute])
        observed = number(trips, attribute)
        require(abs(calculated - observed) <= 0.0100001, f"Média {attribute} diverge de stats.xml: calculada={calculated}, stats={observed}")
    for attribute, source in (("totalTravelTime", "duration"), ("totalDepartDelay", "departDelay")):
        require(abs(number(trips, attribute) - sum(values[source])) <= 0.005 * (key[1] + 1) + 1e-7,
                f"Total {attribute} diverge além da precisão dos campos")
    braking = integer(safety, "emergencyBraking")
    collisions = integer(safety, "collisions")
    teleport_count = integer(teleports, "total")
    for name, value, label in (("emergency_braking_count", braking, "Eventos safety@emergencyBraking"),
                               ("emergency_stops_count", integer(safety, "emergencyStops"), "Eventos safety@emergencyStops; não sinônimo de frenagens"),
                               ("collision_count", collisions, "Colisões registradas em stats.xml"),
                               ("teleport_count", teleport_count, "Teleportes registrados em stats.xml")):
        set_field(row, name, value, "eventos", label, "controle" if name != "emergency_braking_count" else "complementar")
    set_field(row, "emergency_braking_per1000trips", braking / key[1] * 1000, "eventos/1000 viagens", "Frenagens registradas por mil viagens; não risco real de acidente")
    if collisions or teleport_count:
        warnings.append(f"Há {collisions} colisões e {teleport_count} teleportes; manter execução e examinar a interpretação")
    require(len(xml(folder / "collisions.xml").findall("collision")) == collisions, "XML de colisões diverge do contador")
    events = {(ident, float(timestamp)) for ident, timestamp in BRAKING.findall(read_text(folder / "warnings.log"))}
    set_field(row, "emergency_braking_log_count", len(events), "eventos", "Pares distintos veículo/instante em warnings.log; sumo.log não é somado", "controle")
    set_field(row, "emergency_braking_vehicle_count", len({ident for ident, _ in events}), "veículos", "Veículos distintos com aviso de frenagem em warnings.log")
    if len(events) != braking:
        warnings.append(f"Frenagens: stats={braking}, avisos únicos={len(events)}; conferir critérios de emissão/completude do log")
    last, count = None, 0
    for _, step in ET.iterparse(folder / "summary.xml", events=("end",)):
        if step.tag != "step":
            continue
        timestamp = number(step, "time")
        require(abs(timestamp - count) < 1e-8, f"Grade de summary.xml incompleta/duplicada em {timestamp}")
        require(number(step, "running") >= 0 and number(step, "waiting") >= 0, "Contagens negativas no summary")
        last = dict(step.attrib)
        count += 1
        step.clear()
    require(count == 1800 and last is not None, f"summary.xml possui {count}/1800 amostras")
    require(int(last["arrived"]) == key[1] and int(last["inserted"]) == key[1] and int(last["ended"]) == key[1], "Contadores finais de summary divergem da demanda")
    require(int(last["running"]) == 0 and int(last["waiting"]) == 0, "Pendências no summary final")
    require(int(last["discarded"]) == 0, "Veículos descartados no summary")


def queues_metrics(folder, lanes, row, lane_writer):
    # Somente registros positivos atualizam os acumuladores; denominadores incluem os zeros.
    lane_acc = {(h, criterion, ident): Accumulator() for h in HORIZONS
                for criterion in ("stopped", "slow") for ident in lanes}
    totals = {(h, criterion, group): Accumulator() for h in HORIZONS
              for criterion in ("stopped", "slow") for group in ("all", "external", "internal")}
    maxima = {(h, criterion, group): Accumulator() for h in HORIZONS
              for criterion in ("stopped", "slow") for group in ("all", "external", "internal")}
    count = 0
    for _, data in ET.iterparse(folder / "queues.xml", events=("end",)):
        if data.tag != "data":
            continue
        timestamp = number(data, "timestep")
        require(abs(timestamp - count) < 1e-8, f"Grade de queues.xml incompleta/duplicada em {timestamp}")
        lane_container = data.find("lanes")
        require(lane_container is not None, f"Bloco de filas sem elemento lanes: {timestamp}")
        current = {(criterion, group): 0.0 for criterion in ("stopped", "slow") for group in ("all", "external", "internal")}
        seen = set()
        for lane in lane_container.findall("lane"):
            ident = lane.get("id")
            require(ident in lanes and ident not in seen, f"Faixa desconhecida/duplicada no bloco {timestamp}: {ident}")
            seen.add(ident)
            for criterion, attribute in (("stopped", "queueing_length"), ("slow", "queueing_length_experimental")):
                value = number(lane, attribute)
                require(value >= 0, f"Comprimento de fila negativo: {ident}/{timestamp}")
                category = lanes[ident].category
                for group in ("all", category):
                    current[criterion, group] += value
                for horizon in HORIZONS:
                    if timestamp < horizon:
                        lane_acc[horizon, criterion, ident].add(value, timestamp, ident)
                        for group in ("all", category):
                            # add atualiza o máximo individual; total deste acumulador não é utilizado.
                            maxima[horizon, criterion, group].add(value, timestamp, ident)
        for horizon in HORIZONS:
            if timestamp < horizon:
                for criterion in ("stopped", "slow"):
                    for group in ("all", "external", "internal"):
                        totals[horizon, criterion, group].add(current[criterion, group], timestamp)
        count += 1
        data.clear()
    require(count == 1800, f"queues.xml possui {count}/1800 amostras; lacunas não viram zero")
    for horizon in HORIZONS:
        for criterion in ("stopped", "slow"):
            prefix = "queue" if criterion == "stopped" else "queue_slow_experimental"
            role = "principal" if criterion == "stopped" and horizon == 600 else "complementar"
            for group in ("all", "external", "internal"):
                label = "total" if group == "all" else group
                aggregate = totals[horizon, criterion, group]
                maximum = maxima[horizon, criterion, group]
                eligible = [ident for ident, lane in lanes.items() if group == "all" or lane.category == group]
                positive_samples = sum(lane_acc[horizon, criterion, ident].positive for ident in eligible)
                set_field(row, f"{prefix}_{label}_mean_m_0_{horizon}", aggregate.total / horizon, "m agregados entre faixas",
                          f"Média da soma dos comprimentos exportados ({criterion}/{group}), {horizon} amostras com zeros", role)
                set_field(row, f"{prefix}_{label}_presence_pct_0_{horizon}", 100 * positive_samples / (horizon * len(eligible)), "% faixa × tempo",
                          f"Proporção de observações faixa/tempo com comprimento >0 ({criterion}/{group})")
                if group == "all":
                    set_field(row, f"{prefix}_sum_max_m_0_{horizon}", aggregate.maximum, "m agregados entre faixas", "Máximo temporal da soma dos comprimentos entre faixas")
                    set_field(row, f"{prefix}_lane_max_m_0_{horizon}", maximum.maximum, "m", "Maior comprimento exportado em uma faixa")
                    set_field(row, f"{prefix}_lane_max_id_0_{horizon}", maximum.max_lane, "ID", "Faixa do máximo; primeira ocorrência na ordem do arquivo", "controle")
                    set_field(row, f"{prefix}_lane_max_time_s_0_{horizon}", maximum.max_time, "s", "Instante do máximo; vazio quando todos os valores são zero", "controle")
            for ident, lane in sorted(lanes.items()):
                # Uma linha por faixa/janela, com critério principal e experimental em colunas distintas.
                if criterion != "stopped":
                    continue
                stopped = lane_acc[horizon, "stopped", ident]
                slow = lane_acc[horizon, "slow", ident]
                lane_writer.writerow({"seed": row["seed"], "demand_vehicles": row["demand_vehicles"], "scenario": row["scenario"],
                    "lane_id": ident, "edge_id": lane.edge, "category": lane.category, "edge_name": lane.name,
                    "edge_from": lane.origin, "edge_to": lane.destination, "lane_length_m": lane.length,
                    "window_begin_s": 0, "window_end_s": horizon, "sample_count": horizon,
                    "queue_mean_m": stopped.total / horizon, "queue_max_m": stopped.maximum,
                    "queue_presence_pct": 100 * stopped.positive / horizon, "queue_max_time_s": stopped.max_time,
                    "slow_experimental_mean_m": slow.total / horizon, "slow_experimental_max_m": slow.maximum,
                    "slow_experimental_presence_pct": 100 * slow.positive / horizon, "slow_experimental_max_time_s": slow.max_time})


LANE_COLUMNS = ("seed", "demand_vehicles", "scenario", "lane_id", "edge_id", "category", "edge_name", "edge_from", "edge_to",
                "lane_length_m", "window_begin_s", "window_end_s", "sample_count", "queue_mean_m", "queue_max_m", "queue_presence_pct",
                "queue_max_time_s", "slow_experimental_mean_m", "slow_experimental_max_m", "slow_experimental_presence_pct", "slow_experimental_max_time_s")


def csv_value(value):
    return format(value, ".12g") if isinstance(value, float) else value


class CsvWriter:
    def __init__(self, handle, columns):
        self.writer = csv.DictWriter(handle, fieldnames=columns, delimiter=";")
        self.writer.writeheader()

    def writerow(self, row):
        self.writer.writerow({key: csv_value(value) for key, value in row.items()})


def write_csv(path, columns, rows):
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = CsvWriter(handle, columns)
        for row in rows:
            writer.writerow(row)


def process_run(base, key, folder, lanes, compositions, lane_writer):
    for name in REQUIRED:
        require((folder / name).is_file(), f"Arquivo obrigatório ausente: {name}")
    check_configuration(folder, key)
    row = {}
    for name, value, definition in (("seed", key[0], "Seed do bloco"), ("demand_vehicles", key[1], "Veículos programados em [0,600)"),
                                    ("scenario", key[2], "Composição da execução"), ("sumo_version", "1.27.1", "Versão conferida"),
                                    ("protocol_version", PROTOCOL, "Versão do protocolo de métricas")):
        set_field(row, name, value, "identificador", definition, "controle")
    for group in ("external", "internal"):
        set_field(row, f"queue_{group}_lane_count", sum(l.category == group for l in lanes.values()), "faixas", "Denominador espacial fixo definido pelo snapshot", "controle")
    values, speeds = trips_metrics(folder, key, compositions[key[2]], row)
    warnings = []
    stats_and_summary(folder, key, row, values, speeds, warnings)
    queues_metrics(folder, lanes, row, lane_writer)
    set_field(row, "validation_status", "OK_COM_AVISOS" if warnings else "OK", "status", "Integridade da extração; avisos não excluem a execução", "controle")
    provenance = {name: {"sha256": sha256(folder / name), "size_bytes": (folder / name).stat().st_size}
                  for name in REQUIRED if name != "EXECUCAO_OK.txt"}
    return row, warnings, provenance


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--entrada", type=Path, default=Path("output/experimento_final/baseline_v1"))
    parser.add_argument("--saida", type=Path, help="Pasta nova de análise; padrão: pasta irmã analise_<datahora>")
    parser.add_argument("--modo-amostra", action="store_true", help="Processar somente diretórios disponíveis e marcar explicitamente como AMOSTRA")
    args = parser.parse_args(argv)
    base = args.entrada.resolve()
    if not base.is_dir():
        print(f"ERRO: pasta de entrada não encontrada: {base}", file=sys.stderr)
        return 2
    output = (args.saida or base.parent / ("analise_" + datetime.now().strftime("%Y%m%d_%H%M%S"))).resolve()
    if output == base or output.is_relative_to(base) or base.is_relative_to(output):
        print("ERRO: a pasta de análise não pode sobrepor a coleta bruta.", file=sys.stderr)
        return 2
    if output.exists():
        print(f"ERRO: pasta de saída já existe; use uma pasta nova: {output}", file=sys.stderr)
        return 2
    output.mkdir(parents=True)
    started = time.perf_counter()
    results, diagnostics, run_provenance = [], [], []
    failure = False
    lane_temporary = output / "filas_por_faixa.tmp"
    metadata = {"analyzer_version": VERSION, "protocol_version": PROTOCOL, "mode": "AMOSTRA" if args.modo_amostra else "INTEGRAL",
                "python_version": sys.version.split()[0], "sumo_version": "1.27.1",
                "created_at_utc": datetime.now(timezone.utc).isoformat(), "expected_official_runs": 630,
                "windows": [{"begin_s": 0, "end_s": h, "end_inclusive": False} for h in HORIZONS],
                "csv_separator": ";", "csv_decimal_separator": ".", "csv_float_significant_digits": 12,
                "analyzer_sha256": sha256(Path(__file__)), "source_directory": str(base),
                "quantile_method": "linear", "within_run_sd_ddof": 0,
                "scope_note": "Não executa testes inferenciais nem estima efeitos entre composições."}
    try:
        lanes, compositions, hashes = load_snapshot(base)
        registry = load_registry(base)
        runs, missing = discover(base, args.modo_amostra)
        metadata.update({"available_runs": len(runs), "missing_run_count": len(missing),
                         "missing_runs": [list(key) for key in missing], "snapshot_hashes": hashes,
                         "lane_count": len(lanes), "run_provenance": run_provenance,
                         "registry_sha256": sha256(base / "registro_execucoes.csv"), "manifest_sha256": sha256(base / "manifesto.txt")})
        with lane_temporary.open("w", encoding="utf-8-sig", newline="") as handle:
            lane_writer = CsvWriter(handle, LANE_COLUMNS)
            for index, (key, folder) in enumerate(runs, 1):
                require(key in registry, f"Execução sem registro: {key}")
                try:
                    row, warnings, provenance = process_run(base, key, folder, lanes, compositions, lane_writer)
                    results.append(row)
                    run_provenance.append({"seed": key[0], "demand_vehicles": key[1], "scenario": key[2],
                                           "relative_directory": folder.relative_to(base).as_posix(), "files": provenance})
                    diagnostics.append({"seed": key[0], "demand_vehicles": key[1], "scenario": key[2],
                                        "status": row["validation_status"], "message": " | ".join(warnings) or "Verificações concluídas"})
                except (DataError, ET.ParseError, OSError, ValueError, KeyError, TypeError) as exc:
                    failure = True
                    diagnostics.append({"seed": key[0], "demand_vehicles": key[1], "scenario": key[2], "status": "ERRO", "message": str(exc)})
                    print(f"ERRO seed={key[0]} demanda={key[1]} cenário={key[2]}: {exc}", file=sys.stderr, flush=True)
                if index == 1 or index % 10 == 0 or index == len(runs):
                    print(f"Processadas {index}/{len(runs)}; válidas={len(results)}; erros={sum(d['status']=='ERRO' for d in diagnostics)}", flush=True)
    except (DataError, ET.ParseError, OSError, ValueError, KeyError, TypeError, SyntaxError) as exc:
        failure = True
        diagnostics.append({"seed": "", "demand_vehicles": "", "scenario": "", "status": "ERRO_GLOBAL", "message": str(exc)})
        print(f"ERRO: {exc}", file=sys.stderr, flush=True)
    success = not failure and bool(results)
    metadata.update({"success": success, "validated_runs": len(results),
                     "error_count": sum(d["status"] in ("ERRO", "ERRO_GLOBAL") for d in diagnostics),
                     "elapsed_seconds": time.perf_counter() - started,
                     "scope": "AMOSTRA" if args.modo_amostra else "COLETA_INTEGRAL"})
    write_csv(output / "validacao_consolidacao.csv", ("seed", "demand_vehicles", "scenario", "status", "message"), diagnostics)
    if success:
        name = "base_execucoes_AMOSTRA.csv" if args.modo_amostra else "base_execucoes.csv"
        write_csv(output / name, tuple(FIELDS), results)
        lane_temporary.rename(output / ("filas_por_faixa_AMOSTRA.csv" if args.modo_amostra else "filas_por_faixa.csv"))
        dictionary = [{"campo": key, **value} for key, value in FIELDS.items()]
        write_csv(output / "dicionario_metricas.csv", ("campo", "unidade", "definicao", "papel"), dictionary)
        metadata["published_files"] = {p.name: {"sha256": sha256(p), "size_bytes": p.stat().st_size}
                                       for p in output.glob("*.csv")}
    else:
        # Remover apenas o arquivo temporário produzido por esta execução.
        if lane_temporary.exists():
            lane_temporary.unlink()
        metadata["published_files"] = {}
    (output / "manifesto_consolidacao.json").write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nSaída: {output}")
    if success:
        archive_name = "resultados_consolidacao_AMOSTRA.zip" if args.modo_amostra else "resultados_consolidacao.zip"
        with zipfile.ZipFile(output / archive_name, "x", compression=zipfile.ZIP_DEFLATED) as archive:
            for filename in (name, "validacao_consolidacao.csv", "manifesto_consolidacao.json", "dicionario_metricas.csv"):
                archive.write(output / filename, filename)
        print(f"Consolidação {metadata['scope']} concluída: {len(results)} linhas; {len(FIELDS)} campos. Dados brutos preservados.")
        print(f"Envie {archive_name} para a próxima etapa; a tabela grande de filas permanece disponível separadamente.")
        return 0
    print("Consolidação não publicada: consulte validacao_consolidacao.csv. Nenhuma execução foi excluída silenciosamente.", file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
