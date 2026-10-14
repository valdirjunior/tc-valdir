"""ICs marginais BCa para diferenças médias pareadas do TC/SUMO.

Análise inicial de incerteza, sem p-valores e sem controle simultâneo de 18 ICs.
Não modifica a entrada e não executa novas simulações. Bibliotecas: NumPy,
pandas, SciPy e Matplotlib. Parâmetros documentados e definidos no código.
"""
from pathlib import Path
import argparse, hashlib, io, json, sys, warnings, zipfile
from datetime import datetime, timezone
import numpy as np
import pandas as pd
import scipy
from scipy.stats import bootstrap
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

SCENARIOS = ("EQU", "CAU", "AGR", "MIX_C", "MIX_N", "MIX_A")
DEMANDS = (300, 450, 625)
SEED = 20261014
CHECK_SEED = 20261015
RESAMPLES = 100000
LEVEL = 0.95
SOURCE = "https://docs.scipy.org/doc/scipy-1.17.0/reference/generated/scipy.stats.bootstrap.html"


def sha(data):
    return hashlib.sha256(data).hexdigest()


def matrix_from_zip(path):
    with zipfile.ZipFile(path) as archive:
        if archive.testzip() is not None:
            raise ValueError("ZIP corrompido")
        payload = archive.read("base_execucoes.csv")
        manifest = json.loads(archive.read("manifesto_consolidacao.json"))
    if not manifest.get("success") or manifest.get("scope") != "COLETA_INTEGRAL":
        raise ValueError("Exigir consolidação integral bem sucedida")
    if sha(payload) != manifest["published_files"]["base_execucoes.csv"]["sha256"]:
        raise ValueError("Hash da base diverge do manifesto")
    data = pd.read_csv(io.BytesIO(payload), sep=";", encoding="utf-8-sig")
    expected = {(s, f, c) for s in range(1000, 1030) for f in DEMANDS for c in ("REF",)+SCENARIOS}
    keys = list(data[["seed", "demand_vehicles", "scenario"]].itertuples(index=False, name=None))
    if len(keys) != 630 or set(keys) != expected or len(set(keys)) != 630:
        raise ValueError("Matriz experimental incompleta/duplicada")
    differences, labels = [], []
    for demand in DEMANDS:
        group = data[data.demand_vehicles == demand]
        if not (group.groupby("seed").demand_base_sha256.nunique() == 1).all():
            raise ValueError("Demanda mudou dentro do bloco")
        pivot = group.pivot(index="seed", columns="scenario", values="travel_time_mean_s").sort_index()
        for scenario in SCENARIOS:
            differences.append((pivot[scenario]-pivot.REF).to_numpy())
            labels.append((demand, scenario))
    matrix = np.asarray(differences)
    if matrix.shape != (18, 30) or not np.isfinite(matrix).all():
        raise ValueError("Exigir 18 contrastes completos de 30 pares")
    if np.any(matrix.std(axis=-1, ddof=1) == 0):
        raise ValueError("Há contraste degenerado: investigar antes de calcular BCa")
    return matrix, labels, sha(payload)


def estimate(matrix, seed):
    # A última dimensão é seed. Cada índice sorteado recupera a coluna inteira,
    # preservando o bloco em todos os contrastes/demandas. As diferenças já são
    # pareadas; nunca são sorteados cenário e REF independentemente.
    with warnings.catch_warnings(record=True) as messages:
        warnings.simplefilter("always")
        result = bootstrap((matrix,), np.mean, axis=-1, paired=True,
                           vectorized=True, n_resamples=RESAMPLES, batch=1000,
                           confidence_level=LEVEL, alternative="two-sided", method="BCa",
                           rng=np.random.default_rng(seed))
    if messages or not np.isfinite(result.confidence_interval.low).all() or not np.isfinite(result.confidence_interval.high).all():
        raise ValueError("Bootstrap emitiu aviso/limite não finito: " + " | ".join(str(m.message) for m in messages))
    return result


def format_pt(number):
    return f"{number:.3f}".replace(".", ",")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--entrada", type=Path, required=True)
    parser.add_argument("--saida", type=Path, required=True)
    args = parser.parse_args()
    if args.saida.exists():
        raise ValueError("Usar pasta de saída nova")
    matrix, labels, source_hash = matrix_from_zip(args.entrada)
    result = estimate(matrix, SEED)
    check = estimate(matrix, CHECK_SEED)
    means = matrix.mean(axis=-1)
    lo, hi = result.confidence_interval
    check_lo, check_hi = check.confidence_interval
    table = pd.DataFrame([
        {"demand_vehicles": f, "scenario": c, "reference": "REF", "metric": "travel_time_mean_s",
         "n_pairs": 30, "mean_delta_s": means[j], "median_delta_s": float(np.median(matrix[j])),
         "ci95_bca_low_s": lo[j], "ci95_bca_high_s": hi[j],
         "bootstrap_standard_error_s": result.standard_error[j],
         "contains_zero": bool(lo[j] <= 0 <= hi[j]), "coverage_scope": "MARGINAL_NAO_SIMULTANEO"}
        for j, (f, c) in enumerate(labels)])
    stability = pd.DataFrame([
        {"demand_vehicles": f, "scenario": c, "main_bootstrap_seed": SEED,
         "check_bootstrap_seed": CHECK_SEED, "check_low_s": check_lo[j], "check_high_s": check_hi[j],
         "low_endpoint_difference_s": abs(lo[j]-check_lo[j]),
         "high_endpoint_difference_s": abs(hi[j]-check_hi[j]),
         "zero_membership_changed": bool((lo[j] <= 0 <= hi[j]) != (check_lo[j] <= 0 <= check_hi[j]))}
        for j, (f, c) in enumerate(labels)])
    args.saida.mkdir(parents=True)
    table.to_csv(args.saida/"ic95_bca_tempo_viagem.csv", sep=";", index=False, encoding="utf-8-sig", float_format="%.12g")
    stability.to_csv(args.saida/"conferencia_monte_carlo.csv", sep=";", index=False, encoding="utf-8-sig", float_format="%.12g")
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9, "axes.spines.top": False, "axes.spines.right": False})
    palette = ("#8661a8", "#277da1", "#d1495b", "#72a8be", "#40916c", "#e49d30")
    fig, axes = plt.subplots(1, 3, figsize=(7.2, 3.1), sharey=True, layout="constrained")
    for panel, (ax, demand) in enumerate(zip(axes, DEMANDS)):
        for y, color in enumerate(palette):
            j = panel*6+y
            ax.plot([lo[j], hi[j]], [y, y], color=color, linewidth=2)
            ax.scatter(means[j], y, s=24, c=color, zorder=4)
        ax.axvline(0, c="#69808e", linewidth=1)
        ax.set_title(f"{demand} veículos")
        ax.set_xlabel("Diferença média ante REF (s)")
        ax.grid(axis="x", alpha=.15)
    axes[0].set_yticks(range(6), SCENARIOS); axes[0].invert_yaxis()
    for suffix in ("png", "svg"):
        fig.savefig(args.saida/f"05_ic95_pareados_viagem.{suffix}", dpi=220, bbox_inches="tight")
    plt.close(fig)
    lines = ["# Incerteza das diferenças médias pareadas - versão 0.1", "",
             "**Status:** etapa exploratória calculada após a análise descritiva. Não é pré-registro nem aprovação metodológica do orientador. O método não altera a simulação congelada.", "",
             "## Método", "",
             "Desfecho: tempo médio de viagem por execução. Para cada seed/demanda, diferença = cenário - REF. Estimando: média dessas diferenças sob as condições fixas do modelo. Foram mantidos todos os 30 pares em cada contraste.", "",
             f"Bootstrap não paramétrico por blocos de seed, 100.000 reamostragens de tamanho 30 com reposição. IC bilateral marginal de 95%, método BCa. Gerador: NumPy default_rng, seed de análise {SEED}; essa seed não é uma das seeds de simulação. Implementação: scipy.stats.bootstrap.", "",
             "A matriz 18 × 30 é reamostrada pela dimensão das seeds com os mesmos índices em todos os contrastes. Isso preserva correspondências entre composições e demandas. A inferência pressupõe realizações de seed adequadas como repetições da variabilidade do modelo. Não representa incerteza de calibração ao trânsito real.", "",
             "Os ICs não foram corrigidos para as 18 comparações: não fornecem cobertura simultânea de 95% do conjunto nem uma declaração conjunta de significância. Não foram calculados p-valores. IC que inclui zero não comprova equivalência ou ausência de efeito.", "",
             "## Resultados", "",
             "| Demanda | Cenário | Diferença média (s) | IC95% BCa marginal (s) |",
             "|---|---|---:|---|" ]
    for r in table.itertuples():
        lines.append(f"| {r.demand_vehicles} | {r.scenario} | {format_pt(r.mean_delta_s)} | [{format_pt(r.ci95_bca_low_s)}; {format_pt(r.ci95_bca_high_s)}] |")
    max_change = max(stability.low_endpoint_difference_s.max(), stability.high_endpoint_difference_s.max())
    lines += ["", "## Leitura e limitações", "",
              "AGR e MIX_A têm ICs marginais abaixo de zero nas três demandas. EQU/450 e MIX_C/625 têm ICs atravessando zero. Em MIX_N/450, o limite inferior fica a poucos milésimos de segundo do zero; a diferença é pequena e não deve ser apresentada como conclusão firme, especialmente sem tratar multiplicidade.", "",
              "As diferenças altas e as execuções congestionadas permanecem nos cálculos. BCa ajusta os quantis para viés e assimetria na aproximação bootstrap; isso não elimina limitações de amostra de 30 seeds ou garante cobertura exata.", "",
              f"Foi feita uma verificação computacional independente com seed {CHECK_SEED}, mantendo B=100.000. A maior mudança de limite foi {format_pt(max_change)} s. Os resultados principais permanecem os da seed previamente registrada; a verificação não é usada para escolher limites mais favoráveis. Cem mil reamostragens não aumentam n: continuam sendo 30 pares, não 100.000 execuções experimentais.", "",
              "## Fonte e reprodução", "", SOURCE, "",
              "A documentação descreve BCa e reamostragem pareada. A escolha de usá-los nesta etapa, de 95% e de B=100.000 é uma decisão analítica aqui registrada. A precisão Monte Carlo observada é verificada separadamente da incerteza entre seeds.", "",
              "O manifesto registra versões, parâmetros e hashes. Para reproduzir, usar o script scripts/estimar_incerteza_pareada.py do repositório com uma pasta de saída nova. Nenhuma nova simulação é necessária."]
    (args.saida/"relatorio_incerteza_pareada.md").write_text("\n".join(lines)+"\n", encoding="utf-8")
    manifest = {"stage": "INCERTEZA_EXPLORATORIA", "method": "BCa", "confidence_level": LEVEL,
                "coverage_scope": "MARGINAL_NAO_SIMULTANEO", "primary_metric": "travel_time_mean_s",
                "n_pairs_per_contrast": 30, "contrast_count": 18, "resamples": RESAMPLES,
                "bootstrap_seed": SEED, "verification_seed": CHECK_SEED, "same_seed_indices_across_contrasts": True,
                "max_endpoint_change_s": float(max_change), "zero_membership_change_count": int(stability.zero_membership_changed.sum()),
                "seeds_excluded": 0, "p_values_computed": False, "simulation_changed": False,
                "analysis_choice_made_after_descriptive_review": True, "source_csv_sha256": source_hash,
                "script_sha256": sha(Path(__file__).read_bytes()), "created_at_utc": datetime.now(timezone.utc).isoformat(),
                "versions": {"python": sys.version.split()[0], "scipy": scipy.__version__, "numpy": np.__version__, "pandas": pd.__version__, "matplotlib": matplotlib.__version__},
                "source": SOURCE, "files_sha256": {p.name: sha(p.read_bytes()) for p in args.saida.iterdir() if p.is_file()}}
    (args.saida/"manifesto_incerteza.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"ICs calculados: 18 contrastes, 30 pares, B={RESAMPLES}. Máxima variação Monte Carlo: {max_change:.6f} s.")
    print(f"Saída: {args.saida.resolve()}. ICs marginais; sem testes de hipótese.")


if __name__ == "__main__":
    main()
