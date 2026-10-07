from pathlib import Path
import xml.etree.ElementTree as ET
import re

BASE = Path("output/teste_lc_global")
CONFIGS = ["lc075", "lc050"]
CASES = [
    (49, "REF", "problema"),
    (51, "AGR", "problema"),
    (47, "REF", "controle"),
    (50, "AGR", "controle"),
]

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

print()
print("=" * 92)
print("RESUMO - TESTE GLOBAL DE lcStrategic")
print("=" * 92)
print(f"{'config':<8} {'seed':>5} {'cenário':<8} {'tipo':<9} {'limpou_em':>10} {'ACT_final':>10} {'BUF_final':>10} {'emerg':>7} {'coll':>6}")
print("-" * 92)

for cfg in CONFIGS:
    for seed, scenario, kind in CASES:
        d = BASE / cfg / f"seed_{seed}" / "fluxo_650" / scenario
        clear, act, buf = first_clear_time(d / "summary.xml")
        emergency, collisions = count_warnings(d / "warnings.log")
        clear_txt = "-" if clear is None else f"{clear:.0f}s"
        act_txt = "-" if act is None else str(act)
        buf_txt = "-" if buf is None else str(buf)

        print(
            f"{cfg:<8} {seed:>5} {scenario:<8} {kind:<9} "
            f"{clear_txt:>10} {act_txt:>10} {buf_txt:>10} "
            f"{emergency:>7} {collisions:>6}"
        )

print()
print("Leitura sugerida:")
print("- Se 0.75 já elimina os travamentos, preferir 0.75 antes de 0.50.")
print("- Se 0.75 falhar e 0.50 funcionar, inspecionar visualmente 0.50 antes de adotar.")
print("- Os casos de controle devem continuar escoando sem comportamento estranho.")
print("- Este é um teste de sensibilidade; ainda não congela o valor final.")
