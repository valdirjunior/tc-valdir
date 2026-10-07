import argparse
import csv
import os
import sys
from pathlib import Path

if "SUMO_HOME" not in os.environ:
    raise SystemExit("SUMO_HOME não está definido.")

tools = Path(os.environ["SUMO_HOME"]) / "tools"
sys.path.append(str(tools))

import traci
from sumolib import checkBinary


EDGE_ALVO = "157964297"
LANE_0 = f"{EDGE_ALVO}_0"
LANE_1 = f"{EDGE_ALVO}_1"


def parse_args():
    p = argparse.ArgumentParser(
        description="Teste diagnóstico: atrasar apenas a troca de faixa estratégica na edge 157964297."
    )
    p.add_argument("--seed", type=int, required=True)
    p.add_argument("--cenario", required=True, choices=["REF", "EQU", "CAU", "AGR", "MIX_C", "MIX_N", "MIX_A"])
    p.add_argument("--fluxo", type=int, default=650)
    p.add_argument("--threshold", type=float, default=120.0,
                   help="Posição em metros até a qual lcStrategic será temporariamente reduzido.")
    p.add_argument("--lc-strategic", type=float, default=0.0,
                   help="Valor temporário de lcStrategic antes do threshold.")
    p.add_argument("--end", type=float, default=1800.0)
    p.add_argument("--gui", action="store_true")
    return p.parse_args()


def main():
    args = parse_args()

    rede = Path("config/nereu_ramos.net.xml")
    perfis = Path("config/perfis/perfis.add.xml")
    rota = Path(f"output/experimentos/seed_{args.seed}/fluxo_{args.fluxo}/{args.cenario}/rotas.rou.xml")

    if not rede.exists():
        raise SystemExit(f"Rede não encontrada: {rede}")
    if not perfis.exists():
        raise SystemExit(f"Perfis não encontrados: {perfis}")
    if not rota.exists():
        raise SystemExit(f"Rotas não encontradas: {rota}")

    pasta = Path(
        f"output/diagnostico_lc_157964297/seed_{args.seed}/"
        f"fluxo_{args.fluxo}/{args.cenario}/threshold_{int(args.threshold)}"
    )
    pasta.mkdir(parents=True, exist_ok=True)

    binario = checkBinary("sumo-gui" if args.gui else "sumo")

    cmd = [
        binario,
        "-n", str(rede),
        "-r", str(rota),
        "-a", str(perfis),
        "--begin", "0",
        "--end", str(args.end),
        "--step-length", "0.1",
        "--time-to-impatience", "60",
        "--seed", str(args.seed),
        "--time-to-teleport", "-1",
        "--collision.check-junctions", "true",
        "--collision.action", "warn",
        "--tripinfo-output", str(pasta / "tripinfo.xml"),
        "--statistic-output", str(pasta / "stats.xml"),
        "--summary-output", str(pasta / "summary.xml"),
        "--summary-output.period", "1",
        "--queue-output", str(pasta / "queues.xml"),
        "--queue-output.period", "1",
        "--lanechange-output", str(pasta / "lanechanges.xml"),
        "--collision-output", str(pasta / "collisions.xml"),
        "--error-log", str(pasta / "warnings.log"),
    ]

    print("=" * 72)
    print("TESTE LOCAL DE TROCA DE FAIXA")
    print(f"Seed/cenário : {args.seed} / {args.cenario}")
    print(f"Edge alvo    : {EDGE_ALVO}")
    print(f"Comprimento  : ~210,64 m")
    print(f"Regra teste  : lcStrategic={args.lc_strategic} enquanto posição < {args.threshold:.1f} m")
    print("Depois do threshold, o valor original do veículo é restaurado.")
    print("As rotas existentes são reutilizadas; a demanda NÃO é regenerada.")
    print("=" * 72)

    traci.start(cmd)

    originais = {}
    modificados = set()
    veiculos_afetados = set()
    ultimo_segundo = -1

    csv_path = pasta / "ocupacao_157964297.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(["tempo", "lane0", "lane1", "total_edge", "veiculos_com_lcStrategic_reduzido"])

        try:
            while traci.simulation.getMinExpectedNumber() > 0:
                traci.simulationStep()
                tempo = traci.simulation.getTime()

                ids = set(traci.vehicle.getIDList())

                # Restaura veículos que já saíram da edge antes de qualquer nova alteração.
                for vid in list(modificados):
                    if vid not in ids:
                        modificados.discard(vid)
                        originais.pop(vid, None)
                        continue

                    if traci.vehicle.getRoadID(vid) != EDGE_ALVO:
                        try:
                            traci.vehicle.setParameter(
                                vid, "laneChangeModel.lcStrategic", originais[vid]
                            )
                        except traci.TraCIException:
                            pass
                        modificados.discard(vid)
                        originais.pop(vid, None)

                # Aplica a alteração apenas dentro da edge e apenas antes do threshold.
                for vid in ids:
                    if traci.vehicle.getRoadID(vid) != EDGE_ALVO:
                        continue

                    pos = traci.vehicle.getLanePosition(vid)

                    if vid not in originais:
                        try:
                            originais[vid] = traci.vehicle.getParameter(
                                vid, "laneChangeModel.lcStrategic"
                            )
                        except traci.TraCIException:
                            # Os perfis atuais usam o padrão do LC2013 (= 1.0).
                            originais[vid] = "1.0"

                    if pos < args.threshold:
                        traci.vehicle.setParameter(
                            vid, "laneChangeModel.lcStrategic", str(args.lc_strategic)
                        )
                        modificados.add(vid)
                        veiculos_afetados.add(vid)
                    elif vid in modificados:
                        traci.vehicle.setParameter(
                            vid, "laneChangeModel.lcStrategic", originais[vid]
                        )
                        modificados.discard(vid)

                segundo = int(tempo)
                if segundo != ultimo_segundo:
                    ultimo_segundo = segundo
                    lane0 = traci.lane.getLastStepVehicleNumber(LANE_0)
                    lane1 = traci.lane.getLastStepVehicleNumber(LANE_1)
                    w.writerow([f"{tempo:.1f}", lane0, lane1, lane0 + lane1, len(modificados)])

                if tempo >= args.end:
                    break

        finally:
            # Tenta restaurar antes do fechamento, apenas por segurança.
            for vid in list(modificados):
                if vid in traci.vehicle.getIDList():
                    try:
                        traci.vehicle.setParameter(
                            vid, "laneChangeModel.lcStrategic", originais.get(vid, "1.0")
                        )
                    except traci.TraCIException:
                        pass
            traci.close()

    print()
    print(f"Veículos que receberam a alteração local: {len(veiculos_afetados)}")
    print(f"Saídas: {pasta}")
    print(f"Ocupação da edge: {csv_path}")
    print()
    print("Compare principalmente:")
    print("  1) ACT/BUF ao final;")
    print("  2) lanechanges.xml na edge 157964297;")
    print("  3) ocupacao_157964297.csv (uso das duas faixas);")
    print("  4) formação visual do gargalo.")


if __name__ == "__main__":
    main()
