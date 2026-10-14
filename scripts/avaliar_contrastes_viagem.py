"""Avaliação exploratória dos 18 contrastes médios de viagem, pareados por seed.

ICs simultâneos nominais de 95%, bootstrap studentizado max-t em uma etapa.
Não executa simulações, não altera a entrada e não exclui seeds. Requer os
scripts/estimar_incerteza_pareada.py já entregue, NumPy, pandas, SciPy e Matplotlib.
"""
from pathlib import Path
import argparse, hashlib, io, json, sys, zipfile
from datetime import datetime, timezone
import numpy as np
import pandas as pd
from scipy.stats import norm, skew
import scipy
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from estimar_incerteza_pareada import matrix_from_zip, estimate, SEED as BCA_SEED

VERSION = '1.0.0'
N = 30
FAMILY_SIZE = 18
LEVEL = .95
RESAMPLES = 1000000
MAIN_SEED = 20261016
CHECK_SEED = 20261017
BATCH = 1000
METHOD = 'BOOTSTRAP_MAX_T_SINGLE_STEP'
COMPLEMENTS = {
    'trip_speed_mean_kmh': ('Velocidade média individual', 'km/h'),
    'waiting_time_mean_s': ('Tempo parado médio', 's'),
    'queue_total_mean_m_0_600': ('Soma média das extensões de fila, 0-600 s', 'm agregados'),
    'completion_flow_vph_0_600': ('Vazão de conclusão, 0-600 s', 'veíc./h'),
    'depart_delay_mean_s': ('Atraso médio de inserção', 's'),
    'system_time_mean_s': ('Tempo médio de sistema', 's'),
    'network_clearance_after600_s': ('Drenagem após 600 s', 's'),
}


def sha(data):
    return hashlib.sha256(data).hexdigest()


def max_statistics(matrix, means, indices):
    """Mesmos índices para os 18 contrastes; SD recalculado em cada amostra."""
    sample = matrix[:, indices]
    sampled_mean = sample.mean(axis=-1)
    sampled_se = sample.std(axis=-1, ddof=1)/np.sqrt(matrix.shape[-1])
    numerator = sampled_mean-means[:, None]
    absolute = np.full_like(sampled_se, np.inf)
    np.divide(np.abs(numerator), sampled_se, out=absolute, where=sampled_se > 0)
    # Variância zero recebe infinito conservador; não apagar reamostragens.
    return absolute.max(axis=0), absolute.argmax(axis=0), int((sampled_se == 0).sum())


def bootstrap_max_t(matrix, seed, resamples=RESAMPLES, batch=BATCH):
    means = matrix.mean(axis=-1)
    random = np.random.default_rng(seed)
    maxima = np.empty(resamples)
    drivers = np.empty(resamples, dtype=np.uint8)
    zero_count = 0
    for start in range(0, resamples, batch):
        end = min(start+batch, resamples)
        indices = random.integers(0, matrix.shape[-1], size=(end-start, matrix.shape[-1]))
        maxima[start:end], drivers[start:end], zeros = max_statistics(matrix, means, indices)
        zero_count += zeros
    critical = float(np.quantile(maxima, LEVEL, method='higher'))
    if not np.isfinite(critical):
        raise ValueError('Quantil não finito; investigar degeneração sem descartar amostras')
    return maxima, drivers, critical, zero_count


def diagnose_bca_tails(matrix, labels):
    # Apenas auditoria de viabilidade, usando o desenho BCa anterior B=100.000.
    # Não gera/publica intervalos Bonferroni-BCa e não escolhe limites pelo sinal.
    original = estimate(matrix, BCA_SEED)
    distribution = original.bootstrap_distribution
    means = matrix.mean(axis=-1)[:, None]
    z0 = norm.ppf(((distribution < means).sum(axis=-1)
                  +(distribution <= means).sum(axis=-1))/(2*distribution.shape[-1]))
    centered = matrix-matrix.mean(axis=-1)[:, None]
    acceleration = (centered**3).sum(axis=-1)/(6*(centered**2).sum(axis=-1)**1.5)
    probabilities = np.array([(1-LEVEL)/(2*FAMILY_SIZE), 1-(1-LEVEL)/(2*FAMILY_SIZE)])
    normal_quantiles = norm.ppf(probabilities)
    adjusted = norm.cdf(z0[:, None]+(z0[:, None]+normal_quantiles)
                        /(1-acceleration[:, None]*(z0[:, None]+normal_quantiles)))
    return pd.DataFrame([
        {'demand_vehicles': d, 'scenario': c, 'diagnostic_bootstrap_seed': BCA_SEED,
         'diagnostic_resamples': 100000, 'bca_bias_correction_z0': z0[j],
         'bca_acceleration': acceleration[j], 'adjusted_lower_quantile': adjusted[j, 0],
         'adjusted_upper_quantile': adjusted[j, 1],
         'expected_smaller_tail_count_at_two_million': 2000000*min(adjusted[j, 0], 1-adjusted[j, 1]),
         'role': 'VIABILIDADE_COMPUTACIONAL_NAO_IC_PUBLICADO'}
        for j, (d, c) in enumerate(labels)])


def load_full_base(path):
    with zipfile.ZipFile(path) as archive:
        data = pd.read_csv(io.BytesIO(archive.read('base_execucoes.csv')), sep=';', encoding='utf-8-sig')
    if not data.validation_status.eq('OK').all():
        raise ValueError('Há execução sem validação OK')
    data['trip_speed_mean_kmh'] = 3.6*data.trip_speed_mean_mps
    return data


def format_pt(value):
    return f'{value:.3f}'.replace('.', ',')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--entrada', type=Path, required=True)
    parser.add_argument('--saida', type=Path, required=True)
    args = parser.parse_args()
    if args.saida.exists():
        raise ValueError('A pasta de saída precisa ser nova')
    matrix, labels, source_hash = matrix_from_zip(args.entrada)
    data = load_full_base(args.entrada)
    means = matrix.mean(axis=-1)
    standard_errors = matrix.std(axis=-1, ddof=1)/np.sqrt(N)
    tails = diagnose_bca_tails(matrix, labels)
    maxima, drivers, critical, zeros = bootstrap_max_t(matrix, MAIN_SEED)
    _, _, check_critical, check_zeros = bootstrap_max_t(matrix, CHECK_SEED)
    print(f'Bootstrap concluído. Crítico principal={critical:.9f}, conferência={check_critical:.9f}.', flush=True)
    lower, upper = means-critical*standard_errors, means+critical*standard_errors
    check_lower, check_upper = means-check_critical*standard_errors, means+check_critical*standard_errors
    table = pd.DataFrame([
        {'demand_vehicles': d, 'scenario': c, 'reference': 'REF', 'metric': 'travel_time_mean_s',
         'n_pairs': N, 'family_size': FAMILY_SIZE, 'mean_delta_s': means[j],
         'median_delta_s': np.median(matrix[j]), 'sd_delta_s': matrix[j].std(ddof=1),
         'standard_error_mean_s': standard_errors[j], 'adjusted_skewness_delta': skew(matrix[j], bias=False),
         'critical_max_t': critical, 'ci95_simultaneous_low_s': lower[j],
         'ci95_simultaneous_high_s': upper[j], 'contains_zero': bool(lower[j] <= 0 <= upper[j]),
         'method': METHOD, 'coverage': 'SIMULTANEA_NOMINAL_95_APROXIMADA', 'stage': 'EXPLORATORIA'}
        for j, (d, c) in enumerate(labels)])
    monte_carlo = pd.DataFrame([
        {'demand_vehicles': d, 'scenario': c, 'check_low_s': check_lower[j], 'check_high_s': check_upper[j],
         'absolute_endpoint_change_s': abs(critical-check_critical)*standard_errors[j],
         'zero_membership_changed': bool((lower[j] <= 0 <= upper[j]) != (check_lower[j] <= 0 <= check_upper[j]))}
        for j, (d, c) in enumerate(labels)])
    influences, influence_summary = [], []
    for j, (demand, scenario) in enumerate(labels):
        leave_one_out = (matrix[j].sum()-matrix[j])/(N-1)
        shifts = leave_one_out-means[j]
        largest = int(np.argmax(np.abs(shifts)))
        influence_summary.append({'demand_vehicles': demand, 'scenario': scenario,
                                  'full_mean_delta_s': means[j], 'most_influential_seed': largest+1000,
                                  'max_absolute_leave_one_out_shift_s': abs(shifts[largest]),
                                  'min_leave_one_out_mean_s': leave_one_out.min(),
                                  'max_leave_one_out_mean_s': leave_one_out.max(),
                                  'full_estimate_keeps_all_30_seeds': True})
        for i in range(N):
            influences.append({'demand_vehicles': demand, 'scenario': scenario, 'seed_examined': 1000+i,
                               'observed_delta_s': matrix[j, i], 'full_mean_delta_s': means[j],
                               'diagnostic_leave_one_out_mean_s': leave_one_out[i], 'shift_s': shifts[i],
                               'role': 'DIAGNOSTICO_INFLUENCIA_NAO_SUBSTITUI_ESTIMATIVA_INTEGRAL'})
    complements = []
    for demand, scenario in labels:
        group = data[data.demand_vehicles == demand]
        differences = {}
        for metric, (label, unit) in COMPLEMENTS.items():
            pivot = group.pivot(index='seed', columns='scenario', values=metric).sort_index()
            delta = (pivot[scenario]-pivot.REF).to_numpy()
            if not np.isfinite(delta).all() or len(delta) != N:
                raise ValueError(f'Complemento incompleto/não finito: {metric}')
            differences[metric] = delta
            complements.append({'demand_vehicles': demand, 'scenario': scenario, 'reference': 'REF',
                                'metric': metric, 'label': label, 'unit': unit, 'n_pairs': N,
                                'mean_delta': delta.mean(), 'median_delta': np.median(delta),
                                'sd_delta': delta.std(ddof=1), 'negative_pairs': int((delta < 0).sum()),
                                'positive_pairs': int((delta > 0).sum()), 'zero_pairs': int((delta == 0).sum()),
                                'role': 'DESCRITIVO_SEM_IC_OU_TESTE'})
        j = labels.index((demand, scenario))
        if not np.allclose(differences['system_time_mean_s'], matrix[j]+differences['depart_delay_mean_s'], atol=2e-7, rtol=0):
            raise ValueError('Tempo de sistema não reconcilia duração + atraso de inserção')
    args.saida.mkdir(parents=True)
    frames = {'contrastes_viagem_ic_simultaneos.csv': table, 'conferencia_monte_carlo.csv': monte_carlo,
              'diagnostico_caudas_bca_bonferroni.csv': tails,
              'influencia_por_seed_DIAGNOSTICO.csv': pd.DataFrame(influences),
              'resumo_influencia.csv': pd.DataFrame(influence_summary),
              'metricas_complementares_descritivas.csv': pd.DataFrame(complements)}
    for name, frame in frames.items():
        frame.to_csv(args.saida/name, sep=';', index=False, encoding='utf-8-sig', float_format='%.12g')
    np.savez_compressed(args.saida/'distribuicao_max_t.npz', max_t=maxima, argmax_contrast_index=drivers)
    plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 10,
                         'axes.spines.top': False, 'axes.spines.right': False})
    fig, axes = plt.subplots(1, 3, figsize=(9.4, 4.0), sharey=True, sharex=True, layout='constrained')
    colors = ('#8661a8', '#277da1', '#d1495b', '#72a8be', '#40916c', '#e49d30')
    for k, (ax, demand) in enumerate(zip(axes, (300, 450, 625))):
        for y, color in enumerate(colors):
            j = 6*k+y
            ax.plot([lower[j], upper[j]], [y, y], color=color, linewidth=2.2)
            ax.scatter(means[j], y, color=color, s=30, zorder=3)
        ax.axvline(0, color='#637987', linewidth=1)
        ax.set_title(f'{demand} veículos'); ax.set_xlabel('Diferença média ante REF (s)')
        ax.grid(axis='x', alpha=.17)
    axes[0].set_yticks(range(6), ('EQU','CAU','AGR','MIX_C','MIX_N','MIX_A'))
    axes[0].invert_yaxis()
    fig.suptitle('Tempo médio de viagem: ICs simultâneos nominais de 95%\nBootstrap max-t; família de 18 contrastes; 30 seeds; B = 1.000.000', fontsize=11)
    for suffix in ('png', 'svg'):
        fig.savefig(args.saida/f'06_ic_simultaneos_viagem.{suffix}', dpi=220, bbox_inches='tight')
    plt.close(fig)
    report = ['# Avaliação dos contrastes médios de viagem - versão 1.0', '',
              '**Status:** procedimento adotado nesta etapa exploratória, após a descritiva e após pilotos de viabilidade. Não é pré-registro, validação de campo ou aprovação do orientador.', '',
              '## Método e alcance', '',
              'Estimando: média entre seeds da diferença cenário - REF do tempo médio de viagem por execução. Família única de 18 contrastes (seis composições × três demandas). Todos os 30 pares foram preservados.', '',
              'Foi usado bootstrap max-t studentizado em uma etapa, com os mesmos índices de seed nos 18 contrastes. O máximo absoluto é calibrado no quantil 0,95; o erro padrão é recalculado em cada amostra. Os intervalos têm cobertura conjunta nominal aproximada de 95%, sob pressupostos de repetição independente dos vetores de seed, momentos adequados e aproximação bootstrap. Não são intervalos BCa corrigidos nem o procedimento stepdown completo.', '',
              f'B={RESAMPLES:,}; RNG default_rng; seed principal {MAIN_SEED}, conferência {CHECK_SEED}; quantil com interpolação `higher`. Crítico principal = {critical:.9f}; conferência = {check_critical:.9f}. Amostras com erro padrão zero: {zeros} na principal, {check_zeros} na conferência; nenhuma foi removida.', '',
              'Fonte do procedimento geral: Romano e Wolf (2005), seções 4 e 5 e apêndice B.1. O protocolo do repositório explicita a adaptação a médias de diferenças de simulação.', '',
              'https://users.ssc.wisc.edu/~behansen/718/RomanoWolf2005.pdf', '',
              '## Resultados', '',
              '| Demanda | Cenário | Diferença média (s) | IC simultâneo nominal 95% (s) |',
              '|---|---|---:|---|']
    for row in table.itertuples():
        report.append(f'| {row.demand_vehicles} | {row.scenario} | {format_pt(row.mean_delta_s)} | [{format_pt(row.ci95_simultaneous_low_s)}; {format_pt(row.ci95_simultaneous_high_s)}] |')
    count_zero = int(table.contains_zero.sum())
    report += ['', '## Interpretação', '',
               f'{count_zero} dos 18 intervalos atravessam zero. Isso não comprova equivalência. AGR e MIX_A apresentam diferenças negativas com intervalos abaixo de zero nas três demandas. CAU e MIX_C/300-450 apresentam diferenças positivas; MIX_C/625 atravessa zero. EQU/450-625 e MIX_N/450-625 também atravessam zero; em 300 seus intervalos ficam acima de zero.', '',
               'Essas conclusões se referem ao tempo de viagem dos perfis parametrizados na rede simplificada. Não são recomendação de agressividade real. A classificação decorre dos ICs simultâneos deste procedimento aproximado, e não de uma garantia exata com 30 seeds.', '',
               '## Conferência e influência', '',
               f'A maior mudança de limite ao repetir o cálculo com a segunda seed foi {format_pt(monte_carlo.absolute_endpoint_change_s.max())} s; {int(monte_carlo.zero_membership_changed.sum())} classificações de inclusão de zero mudaram. A estabilidade Monte Carlo mede a execução numérica, não a cobertura estatística real.', '',
               'As 540 verificações leave-one-out são diagnósticos de influência aritmética. A estimativa oficial e seus intervalos usam todas as seeds; nenhum resultado reduzido substitui a base integral. O resumo informa quais seeds mais deslocam cada média.', '',
               'O diagnóstico BCa/Bonferroni usa o piloto anterior B=100.000 para avaliar quantis ajustados. Em MIX_A/625 a cauda exigida corresponde a cerca de nove observações esperadas mesmo com B=2.000.000. Esse foi um motivo computacional para não publicar essa combinação como solução da multiplicidade.', '',
               '## Métricas complementares', '',
               'A tabela complementar contém 126 resumos pareados: velocidade, tempo parado, filas, vazão, atraso de inserção, tempo de sistema e drenagem. São descritivos, sem IC/teste. Não pertencem à família inferencial de 18 contrastes de viagem.', '',
               'Tempo de sistema foi reconciliado por seed como duração + atraso de inserção. Vazão refere-se à janela [0,600), filas a metros agregados na mesma janela. A versão integral de todas as métricas permanece na descritiva anterior.', '',
               '## Limitações e continuidade', '',
               'n=30 permanece uma amostra limitada. A reamostragem não representa erro de calibração ao mundo real e não garante capturar situações raras ausentes na coleta. Assimetria e influência de extremos motivam cautela. Um método posterior à inspeção dos dados permanece exploratório mesmo que trate multiplicidade.', '',
               'Não foram calculados p-valores, todos os pares entre composições, novos contrastes entre demandas ou limiares retrospectivos de relevância prática. A recomendação para a escrita é reportar magnitude, intervalo e contexto das outras métricas. Novas perguntas exigem registrar outra família/etapa.']
    (args.saida/'relatorio_estatistico.md').write_text('\n'.join(report)+'\n', encoding='utf-8')
    manifest = {'version': VERSION, 'method': METHOD, 'family': '18_contrastes_viagem_ante_REF',
                'n_pairs': N, 'family_size': FAMILY_SIZE, 'nominal_joint_confidence': LEVEL,
                'coverage_is_approximate': True, 'stage': 'EXPLORATORIA_POS_DESCRITIVA',
                'analysis_pilots_examined_before_production': ['BCa_Bonferroni_tail_feasibility_B100000', 'max_t_B100000'],
                'resamples': RESAMPLES, 'main_seed': MAIN_SEED, 'check_seed': CHECK_SEED, 'batch': BATCH,
                'quantile_method': 'higher', 'critical_value': critical, 'check_critical_value': check_critical,
                'zero_se_bootstrap_count': zeros, 'check_zero_se_count': check_zeros,
                'max_endpoint_monte_carlo_difference_s': float(monte_carlo.absolute_endpoint_change_s.max()),
                'zero_membership_change_count': int(monte_carlo.zero_membership_changed.sum()),
                'p_values_computed': False, 'stepdown_implemented': False, 'seeds_excluded': 0,
                'simulation_changed': False, 'primary_input_csv_sha256': source_hash,
                'script_sha256': sha(Path(__file__).read_bytes()),
                'dependency_script_sha256': sha((Path(__file__).parent/'estimar_incerteza_pareada.py').read_bytes()),
                'created_at_utc': datetime.now(timezone.utc).isoformat(),
                'versions': {'python': sys.version.split()[0], 'numpy': np.__version__, 'pandas': pd.__version__,
                             'scipy': scipy.__version__, 'matplotlib': matplotlib.__version__},
                'files_sha256': {p.name: sha(p.read_bytes()) for p in args.saida.iterdir() if p.is_file()}}
    (args.saida/'manifesto_estatistico.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(f'18 intervalos; {count_zero} incluem zero; 126 resumos complementares; todas as 30 seeds mantidas.', flush=True)


if __name__ == '__main__':
    main()
