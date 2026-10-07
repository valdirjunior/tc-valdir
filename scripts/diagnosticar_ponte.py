from pathlib import Path
from collections import Counter
import argparse
import xml.etree.ElementTree as ET

PONTE = "98384533"
RAMO_01 = "203038544#0"
RAMO_2 = "99370098#0"
TRECHO_PRACA = "203038544#1"
FAVERO = "99429213#0"
ANEL = "313365849"
SAIDA_SAUL = "E1"
CONTORNO = "305933406"

NOMES_DESTINOS = {
    "1377929346#0.14": "Saul Brandalise",
    "103925179#1": "Rua Brasil",
    "99429213#1": "Antonio Favero",
    "102361495#0": "Antonio Marafon",
    "102361574": "Osvaldo Cruz",
    "103925196#0": "Padre Anchieta",
    "E4": "XV de Novembro",
    "-99643286#2": "XV secundaria",
    "E5": "Farroupilha",
    "E6": "Nicolau Cavon",
    "E8": "Sete de Setembro",
    "E9": "Duque de Caxias",
}

def carregar_rotas(path):
    raiz = ET.parse(path).getroot()
    dados = []
    for v in raiz.findall("vehicle"):
        rota = v.find("route")
        if rota is None:
            continue
        edges = rota.get("edges", "").split()
        if edges:
            dados.append((v.get("id", ""), edges))
    return dados

def pct(n, d):
    return 0.0 if d == 0 else 100.0 * n / d

def analisar(path):
    rotas = carregar_rotas(path)

    passam_ponte = []
    ramo01 = []
    ramo2 = []

    for vid, edges in rotas:
        if PONTE not in edges:
            continue
        passam_ponte.append((vid, edges))
        i = edges.index(PONTE)
        depois = edges[i+1:]
        if RAMO_01 in depois:
            ramo01.append((vid, edges))
        elif RAMO_2 in depois:
            ramo2.append((vid, edges))

    destinos_01 = Counter(edges[-1] for _, edges in ramo01)
    destinos_2 = Counter(edges[-1] for _, edges in ramo2)

    split_01 = Counter()
    for _, edges in ramo01:
        if TRECHO_PRACA not in edges:
            split_01["outro"] += 1
            continue
        j = edges.index(TRECHO_PRACA)
        tail = edges[j+1:]
        if FAVERO in tail:
            split_01["Favero"] += 1
        elif ANEL in tail:
            k = tail.index(ANEL)
            depois_anel = tail[k+1:]
            if SAIDA_SAUL in depois_anel:
                split_01["313 -> E1"] += 1
            elif CONTORNO in depois_anel:
                split_01["313 -> 305933406"] += 1
            else:
                split_01["313 -> outro"] += 1
        else:
            split_01["outro"] += 1

    return {
        "total_rotas": len(rotas),
        "ponte": len(passam_ponte),
        "ramo01": len(ramo01),
        "ramo2": len(ramo2),
        "destinos01": destinos_01,
        "destinos2": destinos_2,
        "split01": split_01,
    }

def imprimir(seed, r):
    print()
    print("=" * 78)
    print(f"SEED {seed}")
    print("=" * 78)
    print(f"Total de rotas: {r['total_rotas']}")
    print(f"Passam pela ponte {PONTE}: {r['ponte']}")
    print(f"  faixas 0/1 -> {RAMO_01}: {r['ramo01']} ({pct(r['ramo01'], r['ponte']):.2f}%)")
    print(f"  faixa 2    -> {RAMO_2}: {r['ramo2']} ({pct(r['ramo2'], r['ponte']):.2f}%)")

    print()
    print("DESTINOS DO RAMO DAS FAIXAS 0/1")
    for edge, qtd in r["destinos01"].most_common():
        nome = NOMES_DESTINOS.get(edge, edge)
        print(f"  {nome:22} {qtd:4} ({pct(qtd, r['ramo01']):6.2f}%)")

    print()
    print("DIVISAO APOS 203038544#1")
    for chave, qtd in r["split01"].most_common():
        print(f"  {chave:24} {qtd:4} ({pct(qtd, r['ramo01']):6.2f}%)")

    print()
    print("DESTINOS DO RAMO DA FAIXA 2")
    for edge, qtd in r["destinos2"].most_common():
        nome = NOMES_DESTINOS.get(edge, edge)
        print(f"  {nome:22} {qtd:4} ({pct(qtd, r['ramo2']):6.2f}%)")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base-dir", type=Path, default=Path("output/teste_demanda_v2"))
    ap.add_argument("--fluxo", type=int, default=650)
    ap.add_argument("--seeds", type=int, nargs="+", default=[42, 43, 44, 45, 46])
    args = ap.parse_args()

    for seed in args.seeds:
        arq = args.base_dir / f"seed_{seed}" / f"fluxo_{args.fluxo}" / "REF" / "rotas.rou.xml"
        if not arq.exists():
            print(f"[AVISO] Nao encontrado: {arq}")
            continue
        imprimir(seed, analisar(arq))

if __name__ == "__main__":
    main()
