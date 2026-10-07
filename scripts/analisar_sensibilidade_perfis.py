from pathlib import Path
from statistics import mean, pstdev
import argparse
import csv
import re
import xml.etree.ElementTree as ET

parser = argparse.ArgumentParser()
parser.add_argument("--base", required=True)
parser.add_argument("--label", default="sensibilidade")
parser.add_argument("--fluxos", nargs="+", type=int, required=True)
parser.add_argument("--seeds", nargs="+", type=int, required=True)
args = parser.parse_args()

BASE = Path(args.base)
CENARIOS = ["REF", "EQU", "CAU", "AGR", "MIX_C", "MIX_N", "MIX_A"]

def parse_summary(path: Path, fluxo: int):
    if not path.exists():
        return None

    root = ET.parse(path).getroot()
    clear_time = None
    last = None

    for step in root.findall("step"):
        t = float(step.get("time", "0"))
        loaded = int(step.get("loaded", "0"))
        inserted = int(step.get("inserted", "0"))
        running = int(step.get("running", "0"))
        waiting = int(step.get("waiting", "0"))
        ended = int(step.get("ended", "0"))

        last = {
            "time": t,
            "loaded": loaded,
            "inserted": inserted,
            "running": running,
            "waiting": waiting,
            "ended": ended,
        }

        if (
            clear_time is None
            and t >= 600
            and loaded >= fluxo
            and running == 0
            and waiting == 0
            and ended >= fluxo
        ):
            clear_time = t

    if last is None:
        return None

    last["clear_time"] = clear_time
    return last

def parse_tripinfo(path: Path):
    if not path.exists():
        return None

    root = ET.parse(path).getroot()
    rows = []
    for ti in root.findall("tripinfo"):
        rows.append({
            "duration": float(ti.get("duration", "0")),
            "waiting": float(ti.get("waitingTime", "0")),
            "timeloss": float(ti.get("timeLoss", "0")),
            "departDelay": float(ti.get("departDelay", "0")),
        })

    if not rows:
        return {
            "n": 0,
            "duration": None,
            "waiting": None,
            "timeloss": None,
            "departDelay": None,
        }

    return {
        "n": len(rows),
        "duration": mean(r["duration"] for r in rows),
        "waiting": mean(r["waiting"] for r in rows),
        "timeloss": mean(r["timeloss"] for r in rows),
        "departDelay": mean(r["departDelay"] for r in rows),
    }

def parse_warnings(path: Path):
    if not path.exists():
        return 0, 0

    txt = path.read_text(encoding="utf-8", errors="ignore")
    emerg = len(re.findall(r"emergency braking", txt, re.I))
    coll = len(re.findall(r"collision", txt, re.I))
    return emerg, coll

def fmt(v, digits=1):
    if v is None:
        return "-"
    return f"{v:.{digits}f}"

all_rows = []

for fluxo in args.fluxos:
    rows = []

    for seed in args.seeds:
        for cenario in CENARIOS:
            d = BASE / f"seed_{seed}" / f"fluxo_{fluxo}" / cenario
            s = parse_summary(d / "summary.xml", fluxo)
            t = parse_tripinfo(d / "tripinfo.xml")
            emerg, coll = parse_warnings(d / "warnings.log")

            if s is None or t is None:
                row = {
                    "label": args.label,
                    "fluxo": fluxo,
                    "seed": seed,
                    "cenario": cenario,
                    "clear": None,
                    "act": None,
                    "buf": None,
                    "ended": None,
                    "inserted": None,
                    "trips": 0,
                    "duration": None,
                    "waiting": None,
                    "timeloss": None,
                    "departDelay": None,
                    "emerg": emerg,
                    "coll": coll,
                }
            else:
                row = {
                    "label": args.label,
                    "fluxo": fluxo,
                    "seed": seed,
                    "cenario": cenario,
                    "clear": s["clear_time"],
                    "act": s["running"],
                    "buf": s["waiting"],
                    "ended": s["ended"],
                    "inserted": s["inserted"],
                    "trips": t["n"],
                    "duration": t["duration"],
                    "waiting": t["waiting"],
                    "timeloss": t["timeloss"],
                    "departDelay": t["departDelay"],
                    "emerg": emerg,
                    "coll": coll,
                }

            rows.append(row)
            all_rows.append(row)

    print()
    print("=" * 154)
    print(f"RELATÓRIO - {args.label} - FLUXO {fluxo}")
    print("=" * 154)
    print(
        f"{'seed':>4} {'cenário':<7} {'limpou_em':>10} {'ACT':>5} {'BUF':>5} "
        f"{'ended':>6} {'trips':>6} {'dur.med':>9} {'wait.med':>9} "
        f"{'loss.med':>9} {'depDelay':>9} {'emerg':>6} {'coll':>5}"
    )
    print("-" * 154)

    for r in rows:
        clear = "-" if r["clear"] is None else f"{r['clear']:.0f}s"
        act = "-" if r["act"] is None else str(r["act"])
        buf = "-" if r["buf"] is None else str(r["buf"])
        ended = "-" if r["ended"] is None else str(r["ended"])

        print(
            f"{r['seed']:>4} {r['cenario']:<7} {clear:>10} "
            f"{act:>5} {buf:>5} {ended:>6} {r['trips']:>6} "
            f"{fmt(r['duration']):>9} {fmt(r['waiting']):>9} "
            f"{fmt(r['timeloss']):>9} {fmt(r['departDelay']):>9} "
            f"{r['emerg']:>6} {r['coll']:>5}"
        )

    valid = [r for r in rows if r["ended"] is not None]
    completed = [
        r for r in valid
        if r["ended"] >= fluxo and r["act"] == 0 and r["buf"] == 0
    ]
    not_completed = [r for r in valid if r not in completed]

    print()
    print("=" * 154)
    print(f"RESUMO GERAL - {args.label} - FLUXO {fluxo}")
    print("=" * 154)
    print(f"Execuções completas: {len(completed)}/{len(rows)}.")

    clear_vals = [r["clear"] for r in completed if r["clear"] is not None]
    if clear_vals:
        print(f"Tempo médio de limpeza: {mean(clear_vals):.1f} s.")
        if len(clear_vals) > 1:
            print(f"Desvio-padrão do tempo de limpeza: {pstdev(clear_vals):.1f} s.")

    print(f"Frenagens emergenciais totais: {sum(r['emerg'] for r in rows)}.")
    print(f"Colisões registradas: {sum(r['coll'] for r in rows)}.")

    if not_completed:
        print()
        print("CASOS NÃO COMPLETOS ATÉ 1800 s:")
        for r in not_completed:
            print(
                f"  seed {r['seed']} / {r['cenario']}: "
                f"ended={r['ended']} ACT={r['act']} BUF={r['buf']} trips={r['trips']}"
            )
    else:
        print("Nenhum caso permaneceu congestionado até o fim.")

    print()
    print("RESUMO POR CENÁRIO:")
    for cenario in CENARIOS:
        cr = [r for r in rows if r["cenario"] == cenario and r["duration"] is not None]
        if not cr:
            print(f"  {cenario:<7}: sem dados.")
            continue

        ok = [
            r for r in cr
            if r["ended"] is not None
            and r["ended"] >= fluxo
            and r["act"] == 0
            and r["buf"] == 0
        ]
        clear_vals = [r["clear"] for r in ok if r["clear"] is not None]

        print(
            f"  {cenario:<7}: completos {len(ok)}/{len(cr)} | "
            f"limpeza média={fmt(mean(clear_vals) if clear_vals else None)}s | "
            f"duração média={mean(r['duration'] for r in cr):.1f}s | "
            f"espera média={mean(r['waiting'] for r in cr):.1f}s | "
            f"timeLoss médio={mean(r['timeloss'] for r in cr):.1f}s | "
            f"departDelay médio={mean(r['departDelay'] for r in cr):.1f}s"
        )

# CSV consolidado para comparação posterior.
BASE.mkdir(parents=True, exist_ok=True)
csv_path = BASE / "resumo_execucoes.csv"
fields = [
    "label", "fluxo", "seed", "cenario", "clear", "act", "buf",
    "ended", "inserted", "trips", "duration", "waiting", "timeloss",
    "departDelay", "emerg", "coll"
]
with csv_path.open("w", newline="", encoding="utf-8-sig") as f:
    w = csv.DictWriter(f, fieldnames=fields, delimiter=";")
    w.writeheader()
    w.writerows(all_rows)

print()
print(f"CSV consolidado salvo em: {csv_path}")
