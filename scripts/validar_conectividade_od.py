import csv
import os
import sys
import xml.etree.ElementTree as ET
from pathlib import Path


# ------------------------------------------------------------
# SUMOLIB
# ------------------------------------------------------------

SUMO_HOME = os.environ.get("SUMO_HOME")

if not SUMO_HOME:
    raise RuntimeError("SUMO_HOME não está definido.")

sys.path.append(
    str(Path(SUMO_HOME) / "tools")
)

import sumolib


# ------------------------------------------------------------
# CONFIGURAÇÃO
# ------------------------------------------------------------

REDE = Path("config/nereu_ramos.net.xml")

ORIGENS = Path(
    "config/demanda/demanda_1061.src.xml"
)

DESTINOS = Path(
    "config/demanda/demanda_1061.dst.xml"
)

SAIDA = Path(
    "output/analise/conectividade_od.csv"
)


def carregar_pesos(caminho):
    root = ET.parse(caminho).getroot()

    dados = []

    for edge in root.findall(".//edge"):
        dados.append(
            (
                edge.get("id"),
                float(edge.get("value", "1"))
            )
        )

    return dados


def main():

    net = sumolib.net.readNet(
        str(REDE)
    )

    origens = carregar_pesos(ORIGENS)
    destinos = carregar_pesos(DESTINOS)

    SAIDA.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    resultados = []

    print()
    print("========================================")
    print(" CONECTIVIDADE ORIGEM -> DESTINO")
    print("========================================")
    print()

    sem_rota = 0
    total = 0

    for origem_id, peso_origem in origens:

        origem = net.getEdge(origem_id)

        for destino_id, peso_destino in destinos:

            total += 1

            destino = net.getEdge(destino_id)

            caminho, custo = net.getShortestPath(
                origem,
                destino,
                vClass="passenger"
            )

            if caminho is None:

                sem_rota += 1

                resultados.append({
                    "origem": origem_id,
                    "peso_origem": peso_origem,
                    "destino": destino_id,
                    "peso_destino": peso_destino,
                    "conectado": "NAO",
                    "distancia_m": "",
                    "num_edges": "",
                    "rota": "",
                })

                print(
                    f"SEM ROTA | "
                    f"{origem_id} -> {destino_id}"
                )

            else:

                ids = [
                    edge.getID()
                    for edge in caminho
                ]

                resultados.append({
                    "origem": origem_id,
                    "peso_origem": peso_origem,
                    "destino": destino_id,
                    "peso_destino": peso_destino,
                    "conectado": "SIM",
                    "distancia_m": round(custo, 2),
                    "num_edges": len(ids),
                    "rota": " ".join(ids),
                })

    with SAIDA.open(
        "w",
        newline="",
        encoding="utf-8-sig"
    ) as arquivo:

        campos = [
            "origem",
            "peso_origem",
            "destino",
            "peso_destino",
            "conectado",
            "distancia_m",
            "num_edges",
            "rota",
        ]

        writer = csv.DictWriter(
            arquivo,
            fieldnames=campos,
            delimiter=";"
        )

        writer.writeheader()
        writer.writerows(resultados)

    print()
    print("----------------------------------------")
    print(f"Pares OD analisados: {total}")
    print(f"Com rota:            {total - sem_rota}")
    print(f"Sem rota:            {sem_rota}")
    print("----------------------------------------")
    print()
    print(f"CSV: {SAIDA}")
    print()


if __name__ == "__main__":
    main()