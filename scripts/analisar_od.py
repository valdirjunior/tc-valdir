from pathlib import Path
from collections import Counter, defaultdict
import argparse
import csv
import xml.etree.ElementTree as ET


def extrair_od(arquivo):
    """
    Retorna uma lista de:
    (id_veiculo, origem, destino, edges)
    """
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
        origem = edges[0]
        destino = edges[-1]

        viagens.append((veiculo_id, origem, destino, edges))

    # Suporte adicional caso algum arquivo contenha <trip>
    for trip in raiz.findall("trip"):
        veiculo_id = trip.get("id", "")
        origem = trip.get("from")
        destino = trip.get("to")

        if origem and destino:
            viagens.append(
                (veiculo_id, origem, destino, [origem, destino])
            )

    return viagens


def percentual(parte, total):
    if total == 0:
        return 0.0
    return 100.0 * parte / total


def mostrar_exemplos_rotas(arquivo, pares, limite=3):
    if not arquivo.exists():
        print()
        print(f"[AVISO] Nao foi possivel mostrar rotas exemplo: {arquivo}")
        return

    viagens = extrair_od(arquivo)
    encontrados = defaultdict(list)

    for veiculo_id, origem, destino, edges in viagens:
        par = (origem, destino)

        if par in pares and len(encontrados[par]) < limite:
            encontrados[par].append((veiculo_id, edges))

    for origem, destino in pares:
        print()
        print("=" * 70)
        print(f"ROTAS EXEMPLO: {origem} -> {destino}")
        print("=" * 70)

        exemplos = encontrados.get((origem, destino), [])

        if not exemplos:
            print("Nenhuma rota encontrada.")
            continue

        for veiculo_id, edges in exemplos:
            print()
            print(f"Veiculo: {veiculo_id}")
            print(" -> ".join(edges))


def main():
    parser = argparse.ArgumentParser(
        description="Analisa pares origem-destino das rotas dos experimentos."
    )

    parser.add_argument(
        "--fluxo",
        type=int,
        default=650,
        help="Fluxo a analisar. Padrao: 650",
    )

    parser.add_argument(
        "--seeds",
        type=int,
        nargs="+",
        default=[42, 43, 44, 45, 46],
        help="Seeds a analisar.",
    )

    parser.add_argument(
        "--base-dir",
        type=Path,
        default=Path("output/experimentos"),
        help="Diretorio base que contem seed_X/fluxo_Y/REF/rotas.rou.xml",
    )

    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("output/analise"),
        help="Diretorio em que os CSVs da analise serao gravados.",
    )

    args = parser.parse_args()

    fluxo = args.fluxo
    seeds = args.seeds
    base_dir = args.base_dir

    pasta_saida = args.output_dir
    pasta_saida.mkdir(parents=True, exist_ok=True)

    linhas_detalhadas = []
    agregado_od = Counter()
    agregado_origens = Counter()
    agregado_destinos = Counter()
    dados_por_seed = {}

    for seed in seeds:
        arquivo = (
            base_dir
            / f"seed_{seed}"
            / f"fluxo_{fluxo}"
            / "REF"
            / "rotas.rou.xml"
        )

        if not arquivo.exists():
            print(f"[AVISO] Arquivo nao encontrado: {arquivo}")
            continue

        viagens = extrair_od(arquivo)
        total = len(viagens)

        contagem_od = Counter()
        contagem_origem = Counter()
        contagem_destino = Counter()

        for _, origem, destino, _ in viagens:
            contagem_od[(origem, destino)] += 1
            contagem_origem[origem] += 1
            contagem_destino[destino] += 1

            agregado_od[(origem, destino)] += 1
            agregado_origens[origem] += 1
            agregado_destinos[destino] += 1

        dados_por_seed[seed] = {
            "total": total,
            "od": contagem_od,
            "origem": contagem_origem,
            "destino": contagem_destino,
        }

        for (origem, destino), quantidade in sorted(
            contagem_od.items(),
            key=lambda x: x[1],
            reverse=True,
        ):
            linhas_detalhadas.append({
                "seed": seed,
                "fluxo": fluxo,
                "origem": origem,
                "destino": destino,
                "veiculos": quantidade,
                "pct_total_seed": percentual(quantidade, total),
                "pct_da_origem": percentual(
                    quantidade,
                    contagem_origem[origem],
                ),
            })

    arquivo_detalhado = pasta_saida / f"od_fluxo_{fluxo}_por_seed.csv"

    with arquivo_detalhado.open(
        "w",
        newline="",
        encoding="utf-8-sig",
    ) as f:
        campos = [
            "seed",
            "fluxo",
            "origem",
            "destino",
            "veiculos",
            "pct_total_seed",
            "pct_da_origem",
        ]

        writer = csv.DictWriter(
            f,
            fieldnames=campos,
            delimiter=";",
        )
        writer.writeheader()

        for linha in linhas_detalhadas:
            linha = linha.copy()
            linha["pct_total_seed"] = f"{linha['pct_total_seed']:.2f}"
            linha["pct_da_origem"] = f"{linha['pct_da_origem']:.2f}"
            writer.writerow(linha)

    arquivo_agregado = pasta_saida / f"od_fluxo_{fluxo}_agregado.csv"
    total_agregado = sum(agregado_od.values())

    with arquivo_agregado.open(
        "w",
        newline="",
        encoding="utf-8-sig",
    ) as f:
        campos = [
            "origem",
            "destino",
            "veiculos",
            "pct_total",
            "pct_da_origem",
        ]

        writer = csv.DictWriter(
            f,
            fieldnames=campos,
            delimiter=";",
        )
        writer.writeheader()

        for (origem, destino), quantidade in agregado_od.most_common():
            writer.writerow({
                "origem": origem,
                "destino": destino,
                "veiculos": quantidade,
                "pct_total": f"{percentual(quantidade, total_agregado):.2f}",
                "pct_da_origem": f"{percentual(quantidade, agregado_origens[origem]):.2f}",
            })

    print()
    print("=" * 70)
    print(f"ANALISE OD - FLUXO {fluxo}")
    print("=" * 70)
    print(f"Base analisada: {base_dir}")
    print(f"Seeds analisadas: {seeds}")
    print(f"Viagens totais agregadas: {total_agregado}")
    print()

    print("20 MAIORES PARES ORIGEM -> DESTINO")
    print()

    for (origem, destino), quantidade in agregado_od.most_common(20):
        pct_total = percentual(quantidade, total_agregado)
        pct_origem = percentual(
            quantidade,
            agregado_origens[origem],
        )

        print(
            f"{origem:25} -> {destino:25} "
            f"{quantidade:4} "
            f"({pct_total:5.2f}% total; "
            f"{pct_origem:5.2f}% da origem)"
        )

    saul_origem = "-1377929346#0"

    print()
    print("=" * 70)
    print(
        f"DESTINOS DOS VEICULOS QUE ENTRAM PELA SAUL "
        f"({saul_origem})"
    )
    print("=" * 70)

    destinos_saul = Counter()

    for (origem, destino), quantidade in agregado_od.items():
        if origem == saul_origem:
            destinos_saul[destino] += quantidade

    total_saul = sum(destinos_saul.values())

    print(f"Total saindo da origem Saul: {total_saul}")
    print()

    for destino, quantidade in destinos_saul.most_common():
        print(
            f"{destino:25} "
            f"{quantidade:4} "
            f"({percentual(quantidade, total_saul):5.2f}%)"
        )

    suspeitos = [
        ("-1377929346#0", "99429213#1"),
        ("-1377929346#0", "103925179#1"),
        ("-1377929346#0", "1377929346#0.14"),
        ("-E4", "E4"),
        ("-103925179#1", "103925179#1"),
    ]

    print()
    print("=" * 70)
    print("PARES ESPECIFICOS PARA INVESTIGACAO")
    print("=" * 70)

    for origem, destino in suspeitos:
        quantidade = agregado_od[(origem, destino)]

        print()
        print(f"{origem} -> {destino}")
        print(f"Total nas seeds: {quantidade}")

        if agregado_origens[origem] > 0:
            print(
                "Percentual dos veiculos dessa origem: "
                f"{percentual(quantidade, agregado_origens[origem]):.2f}%"
            )

        for seed in seeds:
            if seed not in dados_por_seed:
                continue

            qtd_seed = dados_por_seed[seed]["od"][(origem, destino)]
            total_origem_seed = dados_por_seed[seed]["origem"][origem]

            print(
                f"  seed {seed}: "
                f"{qtd_seed:3} "
                f"({percentual(qtd_seed, total_origem_seed):5.2f}%)"
            )

    print()
    print("Arquivos gerados:")
    print(f"  {arquivo_detalhado}")
    print(f"  {arquivo_agregado}")

    pares_circulares = [
        ("-1377929346#0", "1377929346#0.14"),
        ("-E4", "E4"),
        ("-103925179#1", "103925179#1"),
    ]

    seed_exemplo = 42 if 42 in seeds else seeds[0]
    arquivo_exemplo = (
        base_dir
        / f"seed_{seed_exemplo}"
        / f"fluxo_{fluxo}"
        / "REF"
        / "rotas.rou.xml"
    )

    mostrar_exemplos_rotas(
        arquivo_exemplo,
        pares_circulares,
    )


if __name__ == "__main__":
    main()
