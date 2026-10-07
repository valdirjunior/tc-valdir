from pathlib import Path
from collections import Counter
import argparse, xml.etree.ElementTree as ET

PARES=[
("-1377929346#0","103925179#1","Saul -> Brasil"),
("-103925179#1","1377929346#0.14","Brasil -> Saul"),
]

def pct(a,b): return 0 if not b else 100*a/b

ap=argparse.ArgumentParser()
ap.add_argument("--base-dir",type=Path,default=Path("output/teste_demanda_v2"))
ap.add_argument("--fluxo",type=int,default=650)
ap.add_argument("--seeds",type=int,nargs="+",default=[42,43,44,45,46])
a=ap.parse_args()

agg=Counter(); aggo=Counter()
for seed in a.seeds:
    arq=a.base_dir/f"seed_{seed}"/f"fluxo_{a.fluxo}"/"REF"/"rotas.rou.xml"
    if not arq.exists():
        print("[AVISO]",arq); continue
    od=Counter(); org=Counter()
    for v in ET.parse(arq).getroot().findall("vehicle"):
        r=v.find("route")
        if r is None: continue
        e=r.get("edges","").split()
        if not e: continue
        org[e[0]]+=1; od[(e[0],e[-1])]+=1
    agg.update(od); aggo.update(org)
    print(f"SEED {seed}")
    for o,d,n in PARES:
        q=od[(o,d)]
        print(f"  {n:16}: {q:3} ({pct(q,org[o]):5.2f}% da origem)")
print("AGREGADO")
for o,d,n in PARES:
    q=agg[(o,d)]
    print(f"  {n:16}: {q:4} ({pct(q,aggo[o]):5.2f}% da origem)")
