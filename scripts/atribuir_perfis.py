import argparse
import random
import xml.etree.ElementTree as ET
from pathlib import Path


COMPOSICOES = {
    "REF": [
        ("normal", 1.00),
    ],

    "EQU": [
        ("cauteloso", 0.33),
        ("normal", 0.34),
        ("agressivo", 0.33),
    ],

    "CAU": [
        ("cauteloso", 0.60),
        ("normal", 0.40),
    ],

    "AGR": [
        ("agressivo", 0.60),
        ("normal", 0.40),
    ],

    "MIX_C": [
        ("cauteloso", 0.60),
        ("normal", 0.20),
        ("agressivo", 0.20),
    ],

    "MIX_N": [
        ("normal", 0.60),
        ("cauteloso", 0.20),
        ("agressivo", 0.20),
    ],

    "MIX_A": [
        ("agressivo", 0.60),
        ("normal", 0.20),
        ("cauteloso", 0.20),
    ],
}


def calcular_quantidades(total, composicao):
    valores = [
        (perfil, total * proporcao)
        for perfil, proporcao in composicao
    ]

    quantidades = {
        perfil: int(valor)
        for perfil, valor in valores
    }

    restantes = total - sum(quantidades.values())

    ordem = sorted(
        valores,
        key=lambda item: item[1] - int(item[1]),
        reverse=True
    )

    for perfil, _ in ordem[:restantes]:
        quantidades[perfil] += 1

    return quantidades


def atribuir_perfis(entrada, saida, cenario, seed):
    entrada = Path(entrada)
    saida = Path(saida)

    tree = ET.parse(entrada)
    root = tree.getroot()

    elementos = list(root.findall("vehicle"))

    if not elementos:
        elementos = list(root.findall("trip"))

    if not elementos:
        raise RuntimeError(
            "Nenhum <vehicle> ou <trip> encontrado no arquivo."
        )

    total = len(elementos)
    composicao = COMPOSICOES[cenario]

    quantidades = calcular_quantidades(total, composicao)

    # A mesma seed gera a mesma ordenação dos veículos.
    # Isso melhora a comparabilidade entre composições.
    rng = random.Random(seed)

    indices = list(range(total))
    rng.shuffle(indices)

    posicao = 0

    for perfil, _ in composicao:
        quantidade = quantidades[perfil]

        for indice in indices[posicao:posicao + quantidade]:
            elementos[indice].set("type", perfil)

        posicao += quantidade

    ET.indent(tree, space="    ")

    saida.parent.mkdir(parents=True, exist_ok=True)

    tree.write(
        saida,
        encoding="UTF-8",
        xml_declaration=True
    )

    print(f"Cenário: {cenario}")
    print(f"Total de veículos: {total}")

    for perfil in ("cauteloso", "normal", "agressivo"):
        print(
            f"  {perfil}: "
            f"{quantidades.get(perfil, 0)}"
        )

    print(f"Arquivo: {saida}")


def main():
    parser = argparse.ArgumentParser(
        description="Atribui perfis comportamentais aos veículos."
    )

    parser.add_argument(
        "--entrada",
        required=True
    )

    parser.add_argument(
        "--saida",
        required=True
    )

    parser.add_argument(
        "--cenario",
        required=True,
        choices=COMPOSICOES.keys()
    )

    parser.add_argument(
        "--seed",
        type=int,
        default=42
    )

    args = parser.parse_args()

    atribuir_perfis(
        args.entrada,
        args.saida,
        args.cenario,
        args.seed
    )


if __name__ == "__main__":
    main()