from pathlib import Path
from collections import Counter
import argparse
import xml.etree.ElementTree as ET


CORREDOR_XV = ["98384536#0", "E2", "E7"]
DESTINOS_XV = {"E4", "-99643286#2"}
MOVIMENTO_PROBLEMATICO = ("203038544#1", "313365849")


def extrair_rotas(arquivo):
    raiz = ET.parse(arquivo).getroot()
    viagens = []

    for veiculo in raiz.findall("vehicle"):
        rota = veiculo.find("route")
        if rota is None:
            continue

        edges = rota.get("edges", "").strip().split()
        if not edges:
            continue

        viagens.append({
            "id": veiculo.get("id", ""),
            "origem": edges[0],
            "destino": edges[-1],
            "edges": edges,
        })

    return viagens


def contem_sequencia_adjacente(edges, seq):
    n = len(seq)
    return any(edges[i:i+n] == seq for i in range(len(edges) - n + 1))


def contem_transicao(edges, a, b):
    return any(x == a and y == b for x, y in zip(edges, edges[1:]))


def pct(n, d):
    return 0.0 if d == 0 else 100.0 * n / d


def main():
    parser = argparse.ArgumentParser(
        description="Diagnostica o fluxo destinado à XV de Novembro."
    )
    parser.add_argument(
        "--routes",
        type=Path,
        default=Path("output/experimentos/seed_43/fluxo_650/REF/rotas.rou.xml"),
    )
    args = parser.parse_args()

    if not args.routes.exists():
        raise FileNotFoundError(args.routes)

    viagens = extrair_rotas(args.routes)

    xv = [v for v in viagens if v["destino"] in DESTINOS_XV]
    corredor = [v for v in xv if contem_sequencia_adjacente(v["edges"], CORREDOR_XV)]
    problema = [
        v for v in xv
        if contem_transicao(v["edges"], *MOVIMENTO_PROBLEMATICO)
    ]

    print()
    print("=" * 78)
    print("DIAGNOSTICO DO FLUXO PARA A XV DE NOVEMBRO")
    print("=" * 78)
    print(f"Arquivo: {args.routes}")
    print(f"Veiculos totais: {len(viagens)}")
    print()

    destinos = Counter(v["destino"] for v in xv)

    print("DESTINOS DA XV")
    for destino in ["E4", "-99643286#2"]:
        qtd = destinos[destino]
        print(
            f"  {destino:15} {qtd:4} "
            f"({pct(qtd, len(viagens)):6.2f}% do total)"
        )

    print()
    print(
        f"Total destinado à XV: {len(xv)} "
        f"({pct(len(xv), len(viagens)):.2f}% dos 650)"
    )

    print()
    print("CORREDOR 98384536#0 -> E2 -> E7")
    print(
        f"  Veiculos da XV que usam o corredor: {len(corredor)} "
        f"({pct(len(corredor), len(xv)):.2f}% dos destinos XV)"
    )

    por_destino_corredor = Counter(v["destino"] for v in corredor)
    for destino in ["E4", "-99643286#2"]:
        total_destino = destinos[destino]
        usa = por_destino_corredor[destino]
        print(
            f"  {destino:15}: {usa}/{total_destino} "
            f"({pct(usa, total_destino):.2f}%)"
        )

    print()
    print("MOVIMENTO PROBLEMATICO 203038544#1 -> 313365849")
    print(
        f"  Veiculos destinados à XV que fazem esse movimento: {len(problema)} "
        f"({pct(len(problema), len(xv)):.2f}% dos destinos XV)"
    )

    por_destino_problema = Counter(v["destino"] for v in problema)
    for destino in ["E4", "-99643286#2"]:
        total_destino = destinos[destino]
        usa = por_destino_problema[destino]
        print(
            f"  {destino:15}: {usa}/{total_destino} "
            f"({pct(usa, total_destino):.2f}%)"
        )

    print()
    print("ORIGENS DOS VEICULOS DA XV QUE USAM O CORREDOR")
    for origem, qtd in Counter(v["origem"] for v in corredor).most_common():
        print(f"  {origem:25} {qtd:4}")

    print()
    print("ORIGENS DOS VEICULOS DA XV QUE FAZEM O MOVIMENTO PROBLEMATICO")
    for origem, qtd in Counter(v["origem"] for v in problema).most_common():
        print(f"  {origem:25} {qtd:4}")


if __name__ == "__main__":
    main()
