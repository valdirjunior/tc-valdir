from pathlib import Path
import csv
import statistics
import xml.etree.ElementTree as ET


# ============================================================
# CONFIGURAÇÃO
# ============================================================

PASTA_EXPERIMENTOS = Path("output/experimentos")
PASTA_ANALISE = Path("output/analise")

ARQUIVO_BRUTO = PASTA_ANALISE / "resultados_brutos.csv"
ARQUIVO_RESUMO = PASTA_ANALISE / "resumo_por_cenario.csv"

ORDEM_CENARIOS = [
    "REF",
    "EQU",
    "CAU",
    "AGR",
    "MIX_C",
    "MIX_N",
    "MIX_A",
]

# Métricas que receberão resumo estatístico entre seeds.
#
# timeLoss continua sendo coletado, mas fica fora deste conjunto
# principal porque os perfis possuem speedFactor diferente.
METRICAS_PRINCIPAIS = [
    "speed",
    "duration",
    "waitingTime",
    "departDelay",
]


# ============================================================
# FUNÇÕES AUXILIARES
# ============================================================

def valor_float(elemento, atributo, padrao=0.0):
    if elemento is None:
        return padrao

    valor = elemento.get(atributo)

    if valor is None:
        return padrao

    return float(valor)


def valor_int(elemento, atributo, padrao=0):
    if elemento is None:
        return padrao

    valor = elemento.get(atributo)

    if valor is None:
        return padrao

    return int(float(valor))


def extrair_seed(nome):
    return int(nome.replace("seed_", ""))


def extrair_fluxo(nome):
    return int(nome.replace("fluxo_", ""))


def ler_stats(caminho, seed, fluxo, cenario):
    tree = ET.parse(caminho)
    root = tree.getroot()

    vehicles = root.find("vehicles")
    safety = root.find("safety")
    teleports = root.find("teleports")
    trip = root.find("vehicleTripStatistics")

    loaded = valor_int(vehicles, "loaded")
    inserted = valor_int(vehicles, "inserted")
    running = valor_int(vehicles, "running")
    waiting = valor_int(vehicles, "waiting")

    completed = valor_int(trip, "count")

    collisions = valor_int(safety, "collisions")
    emergency_stops = valor_int(safety, "emergencyStops")
    emergency_braking = valor_int(safety, "emergencyBraking")

    total_teleports = valor_int(teleports, "total")

    if inserted > 0:
        completion_rate = completed / inserted * 100
    else:
        completion_rate = 0.0

    problemas = []

    if inserted != fluxo:
        problemas.append(
            f"inseridos={inserted}, esperado={fluxo}"
        )

    if completed != inserted:
        problemas.append(
            f"concluidos={completed}/{inserted}"
        )

    if running > 0:
        problemas.append(
            f"running={running}"
        )

    if waiting > 0:
        problemas.append(
            f"waiting={waiting}"
        )

    if collisions > 0:
        problemas.append(
            f"collisions={collisions}"
        )

    if total_teleports > 0:
        problemas.append(
            f"teleports={total_teleports}"
        )

    if emergency_stops > 0:
        problemas.append(
            f"emergencyStops={emergency_stops}"
        )

    if emergency_braking > 0:
        problemas.append(
            f"emergencyBraking={emergency_braking}"
        )

    status = "OK" if not problemas else "ATENCAO"

    return {
        "seed": seed,
        "fluxo": fluxo,
        "cenario": cenario,

        "loaded": loaded,
        "inserted": inserted,
        "completed": completed,
        "completionRate": completion_rate,
        "running": running,
        "waiting": waiting,

        "collisions": collisions,
        "teleports": total_teleports,
        "emergencyStops": emergency_stops,
        "emergencyBraking": emergency_braking,

        "routeLength": valor_float(trip, "routeLength"),
        "speed": valor_float(trip, "speed"),
        "duration": valor_float(trip, "duration"),
        "waitingTime": valor_float(trip, "waitingTime"),

        # Mantido para diagnóstico/complemento.
        "timeLoss": valor_float(trip, "timeLoss"),

        "departDelay": valor_float(trip, "departDelay"),
        "totalTravelTime": valor_float(
            trip,
            "totalTravelTime"
        ),
        "totalDepartDelay": valor_float(
            trip,
            "totalDepartDelay"
        ),

        "status": status,
        "problemas": "; ".join(problemas),
    }


def media(valores):
    return statistics.mean(valores)


def desvio(valores):
    if len(valores) < 2:
        return ""
    return statistics.stdev(valores)


# ============================================================
# LEITURA DOS EXPERIMENTOS
# ============================================================

def carregar_resultados():
    resultados = []

    if not PASTA_EXPERIMENTOS.exists():
        raise RuntimeError(
            f"Pasta não encontrada: {PASTA_EXPERIMENTOS}"
        )

    for pasta_seed in sorted(
        PASTA_EXPERIMENTOS.glob("seed_*")
    ):
        if not pasta_seed.is_dir():
            continue

        seed = extrair_seed(pasta_seed.name)

        for pasta_fluxo in sorted(
            pasta_seed.glob("fluxo_*")
        ):
            if not pasta_fluxo.is_dir():
                continue

            fluxo = extrair_fluxo(pasta_fluxo.name)

            for cenario in ORDEM_CENARIOS:
                pasta_cenario = pasta_fluxo / cenario
                stats = pasta_cenario / "stats.xml"

                if not stats.exists():
                    print(
                        "AVISO: arquivo ausente: "
                        f"{stats}"
                    )
                    continue

                resultado = ler_stats(
                    stats,
                    seed,
                    fluxo,
                    cenario
                )

                resultados.append(resultado)

    return resultados


# ============================================================
# CSV BRUTO
# ============================================================

def salvar_resultados_brutos(resultados):
    campos = [
        "seed",
        "fluxo",
        "cenario",

        "loaded",
        "inserted",
        "completed",
        "completionRate",
        "running",
        "waiting",

        "collisions",
        "teleports",
        "emergencyStops",
        "emergencyBraking",

        "routeLength",
        "speed",
        "duration",
        "waitingTime",
        "timeLoss",
        "departDelay",

        "totalTravelTime",
        "totalDepartDelay",

        "status",
        "problemas",
    ]

    with ARQUIVO_BRUTO.open(
        "w",
        newline="",
        encoding="utf-8-sig"
    ) as arquivo:

        writer = csv.DictWriter(
            arquivo,
            fieldnames=campos,
            delimiter=";"
        )

        writer.writeheader()
        writer.writerows(resultados)


# ============================================================
# RESUMO POR CENÁRIO
# ============================================================

def salvar_resumo(resultados):
    grupos = {}

    for resultado in resultados:
        chave = (
            resultado["fluxo"],
            resultado["cenario"]
        )

        grupos.setdefault(chave, [])
        grupos[chave].append(resultado)

    campos = [
        "fluxo",
        "cenario",
        "n",

        "speed_media",
        "speed_dp",
        "speed_min",
        "speed_max",

        "duration_media",
        "duration_dp",
        "duration_min",
        "duration_max",

        "waitingTime_media",
        "waitingTime_dp",
        "waitingTime_min",
        "waitingTime_max",

        "departDelay_media",
        "departDelay_dp",
        "departDelay_min",
        "departDelay_max",

        "collisions_total",
        "teleports_total",
        "simulacoes_com_problemas",
    ]

    linhas = []

    for (fluxo, cenario), grupo in grupos.items():
        linha = {
            "fluxo": fluxo,
            "cenario": cenario,
            "n": len(grupo),
        }

        for metrica in METRICAS_PRINCIPAIS:
            valores = [
                item[metrica]
                for item in grupo
            ]

            linha[f"{metrica}_media"] = media(valores)
            linha[f"{metrica}_dp"] = desvio(valores)
            linha[f"{metrica}_min"] = min(valores)
            linha[f"{metrica}_max"] = max(valores)

        linha["collisions_total"] = sum(
            item["collisions"]
            for item in grupo
        )

        linha["teleports_total"] = sum(
            item["teleports"]
            for item in grupo
        )

        linha["simulacoes_com_problemas"] = sum(
            item["status"] != "OK"
            for item in grupo
        )

        linhas.append(linha)

    ordem = {
        nome: indice
        for indice, nome in enumerate(ORDEM_CENARIOS)
    }

    linhas.sort(
        key=lambda x: (
            x["fluxo"],
            ordem.get(x["cenario"], 999)
        )
    )

    with ARQUIVO_RESUMO.open(
        "w",
        newline="",
        encoding="utf-8-sig"
    ) as arquivo:

        writer = csv.DictWriter(
            arquivo,
            fieldnames=campos,
            delimiter=";"
        )

        writer.writeheader()
        writer.writerows(linhas)


# ============================================================
# RELATÓRIO NO TERMINAL
# ============================================================

def exibir_resumo(resultados):
    print()
    print("========================================")
    print(" RESUMO DA ANÁLISE")
    print("========================================")
    print()

    print(
        f"Simulações encontradas: {len(resultados)}"
    )

    problemas = [
        r for r in resultados
        if r["status"] != "OK"
    ]

    print(
        f"Simulações sem problemas: "
        f"{len(resultados) - len(problemas)}"
    )

    print(
        f"Simulações com atenção: {len(problemas)}"
    )

    if problemas:
        print()
        print("Problemas encontrados:")

        for resultado in problemas:
            print(
                f"  seed={resultado['seed']} | "
                f"fluxo={resultado['fluxo']} | "
                f"{resultado['cenario']} | "
                f"{resultado['problemas']}"
            )

    print()
    print(f"CSV bruto: {ARQUIVO_BRUTO}")
    print(f"Resumo:    {ARQUIVO_RESUMO}")
    print()


# ============================================================
# MAIN
# ============================================================

def main():
    PASTA_ANALISE.mkdir(
        parents=True,
        exist_ok=True
    )

    resultados = carregar_resultados()

    if not resultados:
        raise RuntimeError(
            "Nenhum resultado foi encontrado."
        )

    salvar_resultados_brutos(resultados)
    salvar_resumo(resultados)
    exibir_resumo(resultados)


if __name__ == "__main__":
    main()