from pathlib import Path
from collections import Counter
import argparse
import csv
import xml.etree.ElementTree as ET


EDGES_CIRCUITO = [
    "99370105#0",   # parte superior
    "203038544#1",  # lado esquerdo (lanes _1 e _2 pertencem a esta edge)
    "313365849",    # parte inferior
    "305933406",    # lado direito
]

LANE_ESQUERDA_1 = "203038544#1_1"
LANE_ESQUERDA_2 = "203038544#1_2"


def extrair_rotas(arquivo):
    arvore = ET.parse(arquivo)
    raiz = arvore.getroot()

    viagens = []

    for veiculo in raiz.findall("vehicle"):
        veiculo_id = veiculo.get("id", "")
        route = veiculo.find("route")

        if route is None:
            continue

        edges_texto = route.get("edges", "").strip()
        if not edges_texto:
            continue

        edges = edges_texto.split()

        viagens.append({
            "id": veiculo_id,
            "origem": edges[0],
            "destino": edges[-1],
            "edges": edges,
        })

    return viagens


def contem_em_ordem(edges, sequencia):
    pos = -1

    for alvo in sequencia:
        try:
            pos = edges.index(alvo, pos + 1)
        except ValueError:
            return False

    return True


def contar_transicoes_adjacentes(edges):
    return Counter(zip(edges, edges[1:]))


def percentual(parte, total):
    if total == 0:
        return 0.0
    return 100.0 * parte / total


def analisar_lanechanges(arquivo):
    resultado = {
        "arquivo_encontrado": arquivo.exists(),
        "total": 0,
        "1_para_2": 0,
        "2_para_1": 0,
        "motivos_1_para_2": Counter(),
        "motivos_2_para_1": Counter(),
    }

    if not arquivo.exists():
        return resultado

    arvore = ET.parse(arquivo)
    raiz = arvore.getroot()

    for change in raiz.iter("change"):
        resultado["total"] += 1

        origem = change.get("from", "")
        destino = change.get("to", "")
        motivo = change.get("reason", "desconhecido")

        if origem == LANE_ESQUERDA_1 and destino == LANE_ESQUERDA_2:
            resultado["1_para_2"] += 1
            resultado["motivos_1_para_2"][motivo] += 1

        if origem == LANE_ESQUERDA_2 and destino == LANE_ESQUERDA_1:
            resultado["2_para_1"] += 1
            resultado["motivos_2_para_1"][motivo] += 1

    return resultado


def main():
    parser = argparse.ArgumentParser(
        description=(
            "Diagnostica a concentracao de rotas no circuito da Praca Nereu Ramos "
            "e, quando disponivel, as trocas entre as lanes 203038544#1_1 e #1_2."
        )
    )

    parser.add_argument(
        "--routes",
        type=Path,
        default=Path(
            "output/experimentos/seed_43/fluxo_650/REF/rotas.rou.xml"
        ),
        help="Arquivo de rotas a analisar.",
    )

    parser.add_argument(
        "--lanechanges",
        type=Path,
        default=Path(
            "output/experimentos/seed_43/fluxo_650/REF/lanechanges.xml"
        ),
        help="Arquivo lanechanges.xml correspondente.",
    )

    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("output/analise"),
    )

    args = parser.parse_args()

    if not args.routes.exists():
        raise FileNotFoundError(f"Arquivo de rotas nao encontrado: {args.routes}")

    viagens = extrair_rotas(args.routes)
    total = len(viagens)

    uso_edges = Counter()
    transicoes = Counter()
    destinos_por_edge = {edge: Counter() for edge in EDGES_CIRCUITO}
    origens_por_edge = {edge: Counter() for edge in EDGES_CIRCUITO}

    circuito_completo = []
    usa_algum = []
    usa_313 = []
    usa_305 = []
    destino_e6 = []

    for viagem in viagens:
        edges = viagem["edges"]
        conjunto = set(edges)

        for edge in EDGES_CIRCUITO:
            if edge in conjunto:
                uso_edges[edge] += 1
                destinos_por_edge[edge][viagem["destino"]] += 1
                origens_por_edge[edge][viagem["origem"]] += 1

        transicoes.update(contar_transicoes_adjacentes(edges))

        if any(edge in conjunto for edge in EDGES_CIRCUITO):
            usa_algum.append(viagem)

        if "313365849" in conjunto:
            usa_313.append(viagem)

        if "305933406" in conjunto:
            usa_305.append(viagem)

        if contem_em_ordem(edges, EDGES_CIRCUITO):
            circuito_completo.append(viagem)

        if viagem["destino"] == "E6":
            destino_e6.append(viagem)

    print()
    print("=" * 78)
    print("DIAGNOSTICO DO CIRCUITO DA PRACA")
    print("=" * 78)
    print(f"Arquivo: {args.routes}")
    print(f"Veiculos totais: {total}")
    print()

    print("USO DAS EDGES DO CIRCUITO")
    for edge in EDGES_CIRCUITO:
        qtd = uso_edges[edge]
        print(
            f"  {edge:15} {qtd:4} "
            f"({percentual(qtd, total):6.2f}% dos veiculos)"
        )

    print()
    print(
        "Veiculos que usam pelo menos uma edge do circuito: "
        f"{len(usa_algum)} ({percentual(len(usa_algum), total):.2f}%)"
    )
    print(
        "Veiculos que percorrem as quatro edges na ordem "
        "topo -> esquerda -> baixo -> direita: "
        f"{len(circuito_completo)} "
        f"({percentual(len(circuito_completo), total):.2f}%)"
    )

    print()
    print("TRANSICOES ADJACENTES IMPORTANTES")
    pares = [
        ("203038544#1", "313365849"),
        ("313365849", "305933406"),
    ]

    for origem, destino in pares:
        qtd = transicoes[(origem, destino)]
        print(
            f"  {origem} -> {destino}: "
            f"{qtd} ({percentual(qtd, total):.2f}% do total)"
        )

    print()
    print("DESTINOS DOS VEICULOS QUE PASSAM PELA EDGE 313365849")
    for destino, qtd in destinos_por_edge["313365849"].most_common(15):
        print(
            f"  {destino:25} {qtd:4} "
            f"({percentual(qtd, len(usa_313)):6.2f}% dos usuarios da edge)"
        )

    print()
    print("DESTINOS DOS VEICULOS QUE PASSAM PELA EDGE 305933406")
    for destino, qtd in destinos_por_edge["305933406"].most_common(15):
        print(
            f"  {destino:25} {qtd:4} "
            f"({percentual(qtd, len(usa_305)):6.2f}% dos usuarios da edge)"
        )

    print()
    print("VEICULOS COM DESTINO E6 (NICOLAU CAVON)")
    print(f"  Total: {len(destino_e6)}")

    if destino_e6:
        e6_usa_313 = sum(
            1 for v in destino_e6 if "313365849" in set(v["edges"])
        )
        e6_usa_305 = sum(
            1 for v in destino_e6 if "305933406" in set(v["edges"])
        )
        e6_circuito = sum(
            1 for v in destino_e6
            if contem_em_ordem(v["edges"], EDGES_CIRCUITO)
        )

        print(
            f"  Passam pela 313365849: {e6_usa_313} "
            f"({percentual(e6_usa_313, len(destino_e6)):.2f}%)"
        )
        print(
            f"  Passam pela 305933406: {e6_usa_305} "
            f"({percentual(e6_usa_305, len(destino_e6)):.2f}%)"
        )
        print(
            f"  Fazem circuito completo: {e6_circuito} "
            f"({percentual(e6_circuito, len(destino_e6)):.2f}%)"
        )

    print()
    print("PRINCIPAIS DESTINOS DOS VEICULOS QUE FAZEM O CIRCUITO COMPLETO")
    destinos_circuito = Counter(v["destino"] for v in circuito_completo)

    for destino, qtd in destinos_circuito.most_common(15):
        print(
            f"  {destino:25} {qtd:4} "
            f"({percentual(qtd, len(circuito_completo)):6.2f}%)"
        )

    print()
    print("PRINCIPAIS ORIGENS DOS VEICULOS QUE FAZEM O CIRCUITO COMPLETO")
    origens_circuito = Counter(v["origem"] for v in circuito_completo)

    for origem, qtd in origens_circuito.most_common(15):
        print(
            f"  {origem:25} {qtd:4} "
            f"({percentual(qtd, len(circuito_completo)):6.2f}%)"
        )

    # Lane changes
    lc = analisar_lanechanges(args.lanechanges)

    print()
    print("=" * 78)
    print("TROCAS ENTRE AS LANES 203038544#1_1 E 203038544#1_2")
    print("=" * 78)

    if not lc["arquivo_encontrado"]:
        print(f"Arquivo nao encontrado: {args.lanechanges}")
        print(
            "Sem o lanechanges.xml nao e possivel separar o comportamento "
            "entre as lanes _1 e _2 usando apenas rotas."
        )
    else:
        print(f"Arquivo: {args.lanechanges}")
        print(f"Total de lane changes no arquivo: {lc['total']}")
        print(f"{LANE_ESQUERDA_1} -> {LANE_ESQUERDA_2}: {lc['1_para_2']}")
        print(f"{LANE_ESQUERDA_2} -> {LANE_ESQUERDA_1}: {lc['2_para_1']}")

        if lc["motivos_1_para_2"]:
            print()
            print("Motivos _1 -> _2:")
            for motivo, qtd in lc["motivos_1_para_2"].most_common():
                print(f"  {motivo}: {qtd}")

        if lc["motivos_2_para_1"]:
            print()
            print("Motivos _2 -> _1:")
            for motivo, qtd in lc["motivos_2_para_1"].most_common():
                print(f"  {motivo}: {qtd}")

    # CSV por veículo
    args.output_dir.mkdir(parents=True, exist_ok=True)
    csv_saida = args.output_dir / "diagnostico_circuito_seed43_fluxo650_REF.csv"

    with csv_saida.open("w", newline="", encoding="utf-8-sig") as f:
        campos = [
            "veiculo",
            "origem",
            "destino",
            "usa_99370105_0",
            "usa_203038544_1",
            "usa_313365849",
            "usa_305933406",
            "circuito_completo",
            "rota",
        ]

        writer = csv.DictWriter(
            f,
            fieldnames=campos,
            delimiter=";",
        )
        writer.writeheader()

        for viagem in viagens:
            edges = viagem["edges"]
            conjunto = set(edges)

            writer.writerow({
                "veiculo": viagem["id"],
                "origem": viagem["origem"],
                "destino": viagem["destino"],
                "usa_99370105_0": int("99370105#0" in conjunto),
                "usa_203038544_1": int("203038544#1" in conjunto),
                "usa_313365849": int("313365849" in conjunto),
                "usa_305933406": int("305933406" in conjunto),
                "circuito_completo": int(
                    contem_em_ordem(edges, EDGES_CIRCUITO)
                ),
                "rota": " ".join(edges),
            })

    print()
    print(f"CSV gerado: {csv_saida}")


if __name__ == "__main__":
    main()
