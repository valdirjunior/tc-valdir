from pathlib import Path
from collections import Counter, defaultdict
import csv
import xml.etree.ElementTree as ET


PASTA_EXPERIMENTOS = Path("output/experimentos")
PASTA_SAIDA = Path("output/analise")

ARQUIVO_SAIDA = PASTA_SAIDA / "distribuicao_demanda.csv"


def analisar_rota(arquivo):
    tree = ET.parse(arquivo)
    root = tree.getroot()

    origens = Counter()
    destinos = Counter()
    passagens = Counter()
    total = 0

    for vehicle in root.findall("vehicle"):
        route = vehicle.find("route")

        if route is None:
            continue

        edges = route.get("edges", "").split()

        if not edges:
            continue

        total += 1

        origens[edges[0]] += 1
        destinos[edges[-1]] += 1

        for edge in set(edges):
            passagens[edge] += 1

    return total, origens, destinos, passagens


def main():
    PASTA_SAIDA.mkdir(parents=True, exist_ok=True)

    linhas = []

    acumulado = defaultdict(
        lambda: {
            "origem": 0,
            "destino": 0,
            "passagem": 0,
            "total_rotas": 0,
        }
    )

    arquivos = sorted(
        PASTA_EXPERIMENTOS.glob(
            "seed_*/fluxo_*/demanda/base.rou.xml"
        )
    )

    if not arquivos:
        raise RuntimeError(
            "Nenhum arquivo base.rou.xml encontrado."
        )

    for arquivo in arquivos:
        seed = arquivo.parts[-4].replace("seed_", "")
        fluxo = arquivo.parts[-3].replace("fluxo_", "")

        total, origens, destinos, passagens = analisar_rota(
            arquivo
        )

        edges = set(origens) | set(destinos) | set(passagens)

        for edge in sorted(edges):
            origem = origens[edge]
            destino = destinos[edge]
            passagem = passagens[edge]

            linhas.append({
                "seed": seed,
                "fluxo": fluxo,
                "edge": edge,
                "origem": origem,
                "origem_pct": origem / total * 100,
                "destino": destino,
                "destino_pct": destino / total * 100,
                "passagem": passagem,
                "passagem_pct": passagem / total * 100,
            })

            chave = (fluxo, edge)

            acumulado[chave]["origem"] += origem
            acumulado[chave]["destino"] += destino
            acumulado[chave]["passagem"] += passagem
            acumulado[chave]["total_rotas"] += total

    with ARQUIVO_SAIDA.open(
        "w",
        newline="",
        encoding="utf-8-sig",
    ) as f:

        campos = [
            "seed",
            "fluxo",
            "edge",
            "origem",
            "origem_pct",
            "destino",
            "destino_pct",
            "passagem",
            "passagem_pct",
        ]

        writer = csv.DictWriter(
            f,
            fieldnames=campos,
            delimiter=";",
        )

        writer.writeheader()
        writer.writerows(linhas)

    print()
    print("Distribuição média por fluxo:")
    print()

    for (fluxo, edge), dados in sorted(
        acumulado.items()
    ):
        total = dados["total_rotas"]

        destino_pct = (
            dados["destino"] / total * 100
            if total else 0
        )

        origem_pct = (
            dados["origem"] / total * 100
            if total else 0
        )

        if dados["origem"] > 0 or dados["destino"] > 0:
            print(
                f"fluxo={fluxo:>3} | "
                f"{edge:<25} | "
                f"origem={origem_pct:6.2f}% | "
                f"destino={destino_pct:6.2f}%"
            )

    print()
    print(f"CSV gerado: {ARQUIVO_SAIDA}")


if __name__ == "__main__":
    main()