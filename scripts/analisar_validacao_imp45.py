from pathlib import Path
from statistics import mean
import re
import xml.etree.ElementTree as ET

BASE = Path("output/validacao_imp45")
SEEDS = range(47, 52)
CENARIOS = ["REF", "EQU", "CAU", "AGR", "MIX_C", "MIX_N", "MIX_A"]

def read_summary(path):
    if not path.exists():
        return None

    root = ET.parse(path).getroot()
    clear_time = None
    last = None
    max_running = 0
    max_waiting = 0

    for step in root.findall("step"):
        t = float(step.get("time", "0"))
        loaded = int(step.get("loaded", "0"))
        running = int(step.get("running", "0"))
        waiting = int(step.get("waiting", "0"))
        ended = int(step.get("ended", "0"))

        max_running = max(max_running, running)
        max_waiting = max(max_waiting, waiting)
        last = {
            "time": t,
            "loaded": loaded,
            "running": running,
            "waiting": waiting,
            "ended": ended,
        }

        if t >= 600 and loaded >= 650 and running == 0 and waiting == 0 and clear_time is None:
            clear_time = t

    if last is None:
        return None

    last["clear_time"] = clear_time
    last["max_running"] = max_running
    last["max_waiting"] = max_waiting
    return last

def read_tripinfo(path):
    if not path.exists():
        return {"n": 0, "duration": None, "waiting": None, "timeloss": None}

    root = ET.parse(path).getroot()
    vals = []
    for ti in root.findall("tripinfo"):
        vals.append((
            float(ti.get("duration", "0")),
            float(ti.get("waitingTime", "0")),
            float(ti.get("timeLoss", "0")),
        ))

    if not vals:
        return {"n": 0, "duration": None, "waiting": None, "timeloss": None}

    return {
        "n": len(vals),
        "duration": mean(v[0] for v in vals),
        "waiting": mean(v[1] for v in vals),
        "timeloss": mean(v[2] for v in vals),
    }

def read_warnings(path):
    if not path.exists():
        return 0, 0
    txt = path.read_text(encoding="utf-8", errors="ignore")
    emerg = len(re.findall(r"emergency braking", txt, re.I))
    coll = len(re.findall(r"collision", txt, re.I))
    return emerg, coll

rows = []

for seed in SEEDS:
    for cenario in CENARIOS:
        d = BASE / f"seed_{seed}" / "fluxo_650" / cenario
        s = read_summary(d / "summary.xml")
        t = read_tripinfo(d / "tripinfo.xml")
        emerg, coll = read_warnings(d / "warnings.log")

        if s is None:
            rows.append({
                "seed": seed, "cenario": cenario, "clear": None,
                "act": None, "buf": None, "ntrip": t["n"],
                "duration": t["duration"], "waiting": t["waiting"],
                "timeloss": t["timeloss"], "emerg": emerg, "coll": coll
            })
        else:
            rows.append({
                "seed": seed, "cenario": cenario, "clear": s["clear_time"],
                "act": s["running"], "buf": s["waiting"], "ntrip": t["n"],
                "duration": t["duration"], "waiting": t["waiting"],
                "timeloss": t["timeloss"], "emerg": emerg, "coll": coll
            })

print()
print("=" * 132)
print("VALIDAÇÃO AMPLIADA - time-to-impatience 45 s / jmTimegapMinor 0.80 s / fluxo 650")
print("=" * 132)
print(
    f"{'seed':>4} {'cenário':<7} {'limpou_em':>10} {'ACT':>5} {'BUF':>5} {'trips':>6} "
    f"{'dur.med':>9} {'wait.med':>9} {'loss.med':>9} {'emerg':>6} {'coll':>5}"
)
print("-" * 132)

for r in rows:
    clear = "-" if r["clear"] is None else f"{r['clear']:.0f}s"
    act = "-" if r["act"] is None else str(r["act"])
    buf = "-" if r["buf"] is None else str(r["buf"])
    dur = "-" if r["duration"] is None else f"{r['duration']:.1f}"
    wait = "-" if r["waiting"] is None else f"{r['waiting']:.1f}"
    loss = "-" if r["timeloss"] is None else f"{r['timeloss']:.1f}"

    print(
        f"{r['seed']:>4} {r['cenario']:<7} {clear:>10} {act:>5} {buf:>5} {r['ntrip']:>6} "
        f"{dur:>9} {wait:>9} {loss:>9} {r['emerg']:>6} {r['coll']:>5}"
    )

cleared = [r for r in rows if r["clear"] is not None]
not_cleared = [r for r in rows if r["clear"] is None]

print()
print("=" * 132)
print(f"Resumo geral: {len(cleared)}/{len(rows)} simulações limparam até 1800 s.")
if cleared:
    print(f"Tempo médio de limpeza entre as que limparam: {mean(r['clear'] for r in cleared):.1f} s.")
print(f"Frenagens emergenciais totais: {sum(r['emerg'] for r in rows)}.")
print(f"Colisões registradas: {sum(r['coll'] for r in rows)}.")

if not_cleared:
    print()
    print("CASOS QUE NÃO LIMPARAM:")
    for r in not_cleared:
        print(f"  seed {r['seed']} / {r['cenario']}: ACT={r['act']} BUF={r['buf']} trips={r['ntrip']}")
else:
    print("Nenhum caso permaneceu congestionado até o fim.")

print()
print("RESUMO POR CENÁRIO:")
for cenario in CENARIOS:
    cr = [r for r in rows if r["cenario"] == cenario]
    ok = [r for r in cr if r["clear"] is not None]
    avg_clear = mean(r["clear"] for r in ok) if ok else None
    avg_wait = mean(r["waiting"] for r in cr if r["waiting"] is not None)
    avg_loss = mean(r["timeloss"] for r in cr if r["timeloss"] is not None)

    clear_txt = "-" if avg_clear is None else f"{avg_clear:.1f}s"
    print(
        f"  {cenario:<7}: limparam {len(ok)}/5 | "
        f"limpeza média={clear_txt} | espera média={avg_wait:.1f}s | timeLoss médio={avg_loss:.1f}s"
    )
