from pathlib import Path
import re
import xml.etree.ElementTree as ET

BASE = Path("output/teste_jm_timegap")
CONFIGS = ["jm080", "jm060"]
CASES = [
    (49, "REF", "problema"),
    (51, "AGR", "problema"),
    (47, "REF", "controle"),
    (50, "AGR", "controle"),
]

def summary(path):
    if not path.exists():
        return None, None, None
    root = ET.parse(path).getroot()
    clear = None
    last = None
    for s in root.findall("step"):
        t = float(s.get("time", "0"))
        loaded = int(s.get("loaded", "0"))
        running = int(s.get("running", "0"))
        waiting = int(s.get("waiting", "0"))
        last = (running, waiting)
        if clear is None and t >= 600 and loaded >= 650 and running == 0 and waiting == 0:
            clear = t
    if last is None:
        return None, None, None
    return clear, last[0], last[1]

def warnings(path):
    if not path.exists():
        return 0, 0
    txt = path.read_text(encoding="utf-8", errors="ignore")
    return (
        len(re.findall(r"emergency braking", txt, re.I)),
        len(re.findall(r"collision", txt, re.I)),
    )

print()
print("=" * 86)
print("RESUMO - jmTimegapMinor")
print("=" * 86)
print(f"{'config':<7} {'seed':>5} {'cenario':<8} {'tipo':<9} {'limpou_em':>10} {'ACT':>6} {'BUF':>6} {'emerg':>7} {'coll':>6}")
print("-" * 86)

for cfg in CONFIGS:
    for seed, scenario, kind in CASES:
        d = BASE / cfg / f"seed_{seed}" / "fluxo_650" / scenario
        clear, act, buf = summary(d / "summary.xml")
        emerg, coll = warnings(d / "warnings.log")
        clear_txt = "-" if clear is None else f"{clear:.0f}s"
        act_txt = "-" if act is None else str(act)
        buf_txt = "-" if buf is None else str(buf)
        print(f"{cfg:<7} {seed:>5} {scenario:<8} {kind:<9} {clear_txt:>10} {act_txt:>6} {buf_txt:>6} {emerg:>7} {coll:>6}")

print()
print("IMPORTANTE:")
print("- Este teste isola jmTimegapMinor; nao muda a demanda.")
print("- Nao escolher valor apenas porque esvazia mais rapido.")
print("- Se a espera visual no cruzamento nao mudar de forma clara, o problema provavelmente nao e jmTimegapMinor.")
print("- Nesse caso, parar de ajustar esse parametro e revisar a logica de conflito da junction.")
