from pathlib import Path
import xml.etree.ElementTree as ET
import re

BASE = Path("output/teste_lc_lookahead")
CONFIGS = ["la300", "la150", "la100"]
CASES = [
    (49, "REF", "problema"),
    (51, "AGR", "problema"),
    (47, "REF", "controle"),
    (50, "AGR", "controle"),
]

ALVOS = ("157964297", "98384533")

def first_clear_time(summary_path: Path):
    if not summary_path.exists():
        return None, None, None

    root = ET.parse(summary_path).getroot()
    last = None
    first_clear = None

    for step in root.findall("step"):
        t = float(step.get("time", "0"))
        loaded = int(step.get("loaded", "0"))
        running = int(step.get("running", "0"))
        waiting = int(step.get("waiting", "0"))
        ended = int(step.get("ended", "0"))
        last = (t, loaded, running, waiting, ended)

        if t >= 600 and running == 0 and waiting == 0 and loaded >= 650 and first_clear is None:
            first_clear = t

    if last is None:
        return None, None, None

    return first_clear, last[2], last[3]

def count_warnings(path: Path):
    if not path.exists():
        return 0, 0
    txt = path.read_text(encoding="utf-8", errors="ignore")
    emergency = len(re.findall(r"emergency braking", txt, re.I))
    collisions = len(re.findall(r"collision", txt, re.I))
    return emergency, collisions

def lanechange_counts(path: Path):
    total = strategic = alvo = alvo_strategic = 0
    if not path.exists():
        return total, strategic, alvo, alvo_strategic

    root = ET.parse(path).getroot()
    for ch in root.findall(".//change"):
        total += 1
        reason = ch.get("reason", "")
        origem = ch.get("from", "")
        destino = ch.get("to", "")
        is_strategic = "strategic" in reason
        is_alvo = any(origem.startswith(edge + "_") or destino.startswith(edge + "_") for edge in ALVOS)

        if is_strategic:
            strategic += 1
        if is_alvo:
            alvo += 1
        if is_alvo and is_strategic:
            alvo_strategic += 1

    return total, strategic, alvo, alvo_strategic

print()
print("=" * 122)
print("RESUMO - TESTE GLOBAL DE lcStrategicLookahead")
print("=" * 122)
print(
    f"{'config':<7} {'seed':>5} {'cenário':<8} {'tipo':<9} "
    f"{'limpou_em':>10} {'ACT':>6} {'BUF':>6} {'emerg':>6} {'coll':>5} "
    f"{'LC_total':>9} {'LC_strat':>9} {'LC_alvos':>9} {'strat_alvos':>11}"
)
print("-" * 122)

for cfg in CONFIGS:
    for seed, scenario, kind in CASES:
        d = BASE / cfg / f"seed_{seed}" / "fluxo_650" / scenario
        clear, act, buf = first_clear_time(d / "summary.xml")
        emergency, collisions = count_warnings(d / "warnings.log")
        total_lc, strategic_lc, target_lc, target_strategic = lanechange_counts(d / "lanechanges.xml")

        clear_txt = "-" if clear is None else f"{clear:.0f}s"
        act_txt = "-" if act is None else str(act)
        buf_txt = "-" if buf is None else str(buf)

        print(
            f"{cfg:<7} {seed:>5} {scenario:<8} {kind:<9} "
            f"{clear_txt:>10} {act_txt:>6} {buf_txt:>6} "
            f"{emergency:>6} {collisions:>5} "
            f"{total_lc:>9} {strategic_lc:>9} {target_lc:>9} {target_strategic:>11}"
        )

print()
print("ALVOS DE TROCA DE FAIXA CONTABILIZADOS:")
print("  - edge 157964297")
print("  - ponte 98384533")
print()
print("Leitura:")
print("- Primeiro procure diferença VISUAL real no momento das trocas.")
print("- Depois compare se 49/REF e 51/AGR deixam de sustentar o congestionamento.")
print("- 100 m é um teste forte: se produzir trocas tardias/urgentes demais, descarte.")
print("- Não escolher o menor valor apenas por ter menor tempo de esvaziamento.")
