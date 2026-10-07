from pathlib import Path
import argparse, json, os, random, shutil, subprocess
import xml.etree.ElementTree as ET
from collections import Counter

def localizar_duarouter():
    if os.environ.get("SUMO_HOME"):
        for nome in ("duarouter.exe","duarouter"):
            p = Path(os.environ["SUMO_HOME"]) / "bin" / nome
            if p.exists(): return str(p)
    for nome in ("duarouter","duarouter.exe"):
        p = shutil.which(nome)
        if p: return p
    raise RuntimeError("duarouter nao encontrado")

def carregar(path):
    return json.loads(path.read_text(encoding="utf-8"))

def fatores(cfg):
    padrao = float(cfg.get("fator_retorno_mesmo_corredor", 0.20))
    out = {}
    for p in cfg.get("pares_penalizados", []):
        f = float(p.get("fator", padrao))
        if not 0 <= f <= 1: raise ValueError("Fator fora de 0..1")
        out[(p["origem"],p["destino"])] = f
    return out

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--net", type=Path, default=Path("config/nereu_ramos.net.xml"))
    ap.add_argument("--config", type=Path, default=Path("config/demanda/demanda_v2.json"))
    ap.add_argument("--output-root", type=Path, default=Path("output/teste_demanda_v2"))
    ap.add_argument("--fluxo", type=int, required=True)
    ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--begin", type=float, default=0.0)
    ap.add_argument("--end", type=float, default=600.0)
    a = ap.parse_args()

    cfg = carregar(a.config)
    fs = fatores(cfg)
    rng = random.Random(a.seed)
    orgs = [x["edge"] for x in cfg["origens"]]
    powo = [float(x["peso"]) for x in cfg["origens"]]
    dests = cfg["destinos"]
    periodo = (a.end-a.begin)/a.fluxo

    viagens=[]
    for i in range(a.fluxo):
        o = rng.choices(orgs, weights=powo, k=1)[0]
        dids=[d["edge"] for d in dests]
        pd=[float(d["peso"])*fs.get((o,d["edge"]),1.0) for d in dests]
        d=rng.choices(dids, weights=pd, k=1)[0]
        viagens.append((str(i), a.begin+i*periodo, o, d))

    pasta=a.output_root/f"seed_{a.seed}"/f"fluxo_{a.fluxo}"/"REF"
    pasta.mkdir(parents=True, exist_ok=True)
    trips=pasta/"demanda.trips.xml"
    routes=pasta/"rotas.rou.xml"

    raiz=ET.Element("routes")
    for vid,dep,o,d in viagens:
        ET.SubElement(raiz,"trip",{"id":vid,"depart":f"{dep:.3f}","from":o,"to":d,"departLane":"best"})
    arv=ET.ElementTree(raiz); ET.indent(arv, space="    "); arv.write(trips,encoding="UTF-8",xml_declaration=True)

    orgc=Counter(o for _,_,o,_ in viagens); od=Counter((o,d) for _,_,o,d in viagens)
    print(f"Total de viagens: {len(viagens)}")
    print("PARES COM AJUSTE:")
    for (o,d),f in sorted(fs.items()):
        q=od[(o,d)]; to=orgc[o]; p=(100*q/to if to else 0)
        print(f"  {o} -> {d}: fator={f:.2f}; {q} ({p:.2f}% da origem)")

    cmd=[localizar_duarouter(),"--net-file",str(a.net),"--route-files",str(trips),"--output-file",str(routes),"--seed",str(a.seed)]
    subprocess.run(cmd,check=True)
    n=len(ET.parse(routes).getroot().findall("vehicle"))
    print(f"Rotas validas: {n}")
    if n != a.fluxo: raise RuntimeError(f"Esperado {a.fluxo}, obtido {n}")
    print("Status: OK")

if __name__=="__main__":
    main()
