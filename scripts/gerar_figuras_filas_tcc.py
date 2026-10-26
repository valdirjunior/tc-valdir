"""Redesenha duas figuras a partir dos resumos espaciais oficiais já publicados.

Não executa SUMO, não recalcula médias e não modifica entradas. Requer NumPy,
pandas e Matplotlib. Os arquivos PDF/PNG/SVG são variantes da mesma figura.
"""
from pathlib import Path
import argparse
import hashlib
import json
import sys

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from matplotlib.colors import Normalize
from matplotlib.ticker import FuncFormatter
from matplotlib.text import Text

VERSION = '2.0.0'
SCENARIOS = ['REF', 'EQU', 'CAU', 'AGR', 'MIX_C', 'MIX_N', 'MIX_A']
STEMS = ['resultado_filas_faixas_625_v2', 'resultado_mapa_filas_ref625_v2']
INK = '#16354A'
MUTED = '#516574'
BLUE = '#145A86'
REPOSITORIES = {
    'tc-valdir': '2eb4fd70d767650541c43ab3c8728d7fe16995ab',
    'tc-valdir-texto': 'e800e1f6cca6c95605e7a7e3aaaf72373ed87aa7',
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def pt(value, places=2):
    return f'{value:.{places}f}'.replace('.', ',')


def luminance(rgb):
    channels = np.asarray(rgb[:3], dtype=float)
    linear = np.where(channels <= .04045, channels/12.92,
                      ((channels+.055)/1.055)**2.4)
    return float(linear @ np.array([.2126, .7152, .0722]))


def text_color(rgb):
    lum = luminance(rgb)
    black, white = (lum+.05)/.05, 1.05/(lum+.05)
    return ('#000000', black) if black >= white else ('#FFFFFF', white)


def read_inputs(folder, label_path):
    manifest_path = folder/'manifesto_analise_espacial.json'
    source_manifest = json.loads(manifest_path.read_text(encoding='utf-8-sig'))
    paths = [folder/'resumo_por_faixa.csv', folder/'metadados_faixas.csv']
    for path in paths:
        if sha(path) != source_manifest['files_sha256'][path.name]:
            raise ValueError('Arquivo não corresponde ao manifesto oficial: '+path.name)
    summary = pd.read_csv(paths[0], sep=';', encoding='utf-8-sig', float_precision='round_trip')
    metadata = pd.read_csv(paths[1], sep=';', encoding='utf-8-sig', float_precision='round_trip')
    config = json.loads(label_path.read_text(encoding='utf-8-sig'))
    labels = {r['lane_id']: r for r in config['lanes']}
    if len(labels) != len(config['lanes']):
        raise ValueError('IDs duplicados no mapeamento editorial')
    primary = summary[(summary.demand_vehicles == 625)
                      & (summary.window_end_s == 600)].copy()
    if primary.duplicated(['scenario', 'lane_id']).any():
        raise ValueError('Resumo duplicado')
    if len(primary) != 198*7 or not primary.n_seeds.eq(30).all():
        raise ValueError('Exigir 198 faixas, sete composições e 30 execuções')
    if set(primary.scenario) != set(SCENARIOS):
        raise ValueError('Composições diferentes da coleta oficial')
    if not np.isfinite(primary.queue_mean_m).all() or (primary.queue_mean_m < 0).any():
        raise ValueError('Média inválida')
    ref = primary[primary.scenario == 'REF'].set_index('lane_id')
    if not ref.category.value_counts().to_dict() == {'internal': 104, 'external': 94}:
        raise ValueError('Universo de faixas diferente do original')
    top = ref.queue_mean_m.nlargest(10).index.tolist()
    if top != source_manifest['graph_lane_ids']:
        raise ValueError('Seleção das dez faixas diverge da figura original')
    if set(top) != set(labels):
        raise ValueError('Exigir rótulo explícito e único para cada uma das dez faixas')
    if len({labels[lane]['label'] for lane in top}) != 10:
        raise ValueError('Rótulos ambíguos')
    pivot = primary.pivot(index='lane_id', columns='scenario', values='queue_mean_m')
    pivot = pivot.reindex(index=top, columns=SCENARIOS)
    shapes = {row.lane_id: np.asarray(json.loads(row.lane_shape), dtype=float)
              for row in metadata.itertuples()}
    if set(ref.index) != set(shapes):
        raise ValueError('Geometrias não correspondem às 198 faixas')
    if any(p.ndim != 2 or p.shape[1] != 2 or len(p) < 2
           or not np.isfinite(p).all() for p in shapes.values()):
        raise ValueError('Geometria inválida')
    return primary, ref, pivot, shapes, labels, source_manifest, paths+[manifest_path, label_path]


def style():
    plt.rcParams.update({
        'font.family': 'DejaVu Sans', 'font.size': 11,
        'text.color': INK, 'axes.labelcolor': INK,
        'xtick.color': INK, 'ytick.color': INK,
        'pdf.fonttype': 42, 'ps.fonttype': 42, 'svg.fonttype': 'none',
        'figure.facecolor': 'white', 'savefig.facecolor': 'white',
        'axes.spines.top': False, 'axes.spines.right': False,
    })


def finish(fig, output, stem):
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    bounds = fig.bbox
    outside = []
    for artist in fig.findobj(match=Text):
        if artist.get_visible() and artist.get_text().strip():
            box = artist.get_window_extent(renderer)
            if box.x0 < -1 or box.y0 < -1 or box.x1 > bounds.x1+1 or box.y1 > bounds.y1+1:
                outside.append(artist.get_text())
    if outside:
        raise ValueError('Texto fora da figura: '+repr(outside))
    for suffix in ['pdf', 'png', 'svg']:
        meta = {'Title': stem, 'Creator': 'gerar_figuras_filas_tcc.py'}
        if suffix == 'pdf':
            meta.update(CreationDate=None, ModDate=None)
        elif suffix == 'svg':
            meta['Date'] = None
        fig.savefig(output/f'{stem}.{suffix}', dpi=320, metadata=meta)
    plt.close(fig)


def colorbar(fig, rect, mappable):
    ax = fig.add_axes(rect)
    cb = fig.colorbar(mappable, cax=ax, orientation='horizontal', ticks=[0, 5, 10, 15, 20])
    cb.outline.set_visible(False)
    if cb.solids is not None:
        cb.solids.set_rasterized(False)
        cb.solids.set_edgecolor('face')
    cb.ax.tick_params(labelsize=9.5, length=3, color='#8A9BA7', pad=3)
    cb.ax.xaxis.set_major_formatter(FuncFormatter(lambda x, pos: pt(x, 0)))
    cb.set_label('Extensão média de fila (m)', fontsize=10.5, labelpad=5)


def draw_comparison(pivot, labels, output):
    values = pivot.to_numpy()
    fig = plt.figure(figsize=(7.4, 6.2))
    fig.text(.03, .957, 'Filas por faixa e composição', fontsize=14, weight='bold')
    fig.text(.03, .916, '625 veículos, 30 execuções por composição, 0 a 600 s',
             fontsize=10.5, color=MUTED)
    ax = fig.add_axes([.435, .16, .535, .70])
    lab = fig.add_axes([.03, .16, .395, .70], sharey=ax)
    norm = Normalize(0, float(values.max()))
    cmap = plt.get_cmap('Blues')
    im = ax.pcolormesh(np.arange(8)-.5, np.arange(11)-.5, values,
                       cmap=cmap, norm=norm, shading='flat', rasterized=False,
                       edgecolors='face', linewidth=0, antialiased=False)
    ax.set_xlim(-.5, 6.5)
    ax.set_ylim(9.5, -.5)
    ax.set_xticks(range(7), SCENARIOS)
    ax.tick_params(axis='x', top=True, labeltop=True, bottom=False, labelbottom=False,
                   length=0, pad=7, labelsize=10.5)
    ax.tick_params(axis='y', left=False, labelleft=False)
    for tick in ax.get_xticklabels():
        if tick.get_text() == 'REF': tick.set_weight('bold')
    ax.set_xticks(np.arange(-.5, 7, 1), minor=True)
    ax.set_yticks(np.arange(-.5, 10, 1), minor=True)
    ax.grid(which='minor', color='white', linewidth=1.2)
    ax.tick_params(which='minor', bottom=False, left=False, top=False)
    for spine in ax.spines.values(): spine.set_visible(False)
    ax.axvline(.5, color='white', linewidth=2.5)
    lab.set_xlim(0, 1)
    lab.axis('off')
    lab.text(0, 1.035, 'Faixa ou movimento', transform=lab.transAxes,
             fontsize=10.5, weight='bold')
    for row, lane in enumerate(pivot.index):
        lab.text(0, row, '\n'.join(labels[lane]['label_lines']),
                 ha='left', va='center', fontsize=10.6, linespacing=1.25)
    contrasts = []
    for i in range(values.shape[0]):
        for j in range(values.shape[1]):
            val = values[i, j]
            ink, contrast = text_color(cmap(norm(val)))
            contrasts.append(contrast)
            ax.text(j, i, pt(val), ha='center', va='center', color=ink,
                    fontsize=10.6, weight='bold' if j == 0 else 'normal')
    colorbar(fig, [.435, .101, .535, .020], im)
    fig.text(.03, .014, 'Mesmas dez faixas selecionadas em REF; comparação descritiva.',
             fontsize=8.8, color=MUTED)
    finish(fig, output, STEMS[0])
    return {'linear_color_limits_m': [norm.vmin, norm.vmax],
            'min_cell_text_contrast_ratio': min(contrasts)}


def midpoint(shape):
    distance = np.r_[0, np.cumsum(np.linalg.norm(np.diff(shape, axis=0), axis=1))]
    return [float(np.interp(distance[-1]/2, distance, shape[:, axis])) for axis in [0, 1]]


def draw_map(ref, shapes, labels, output):
    values = ref.queue_mean_m
    selected = ref[ref.category == 'external'].queue_mean_m.nlargest(6).index.tolist()
    fig = plt.figure(figsize=(7.4, 6.2))
    fig.text(.03, .957, 'Concentração espacial das filas', fontsize=14, weight='bold')
    fig.text(.03, .916, 'REF, 625 veículos, média de 30 execuções entre 0 e 600 s',
             fontsize=10.5, color=MUTED)
    ax = fig.add_axes([.025, .15, .57, .72])
    legend = fig.add_axes([.64, .19, .34, .65])
    norm, cmap = Normalize(0, float(values.max())), plt.get_cmap('Blues')
    ax.add_collection(LineCollection([shapes[lane] for lane in values.index],
                                    colors='#D4DDE4', linewidths=1.2, zorder=1))
    ordered = values[values > 0].sort_values()
    collection = LineCollection([shapes[lane] for lane in ordered.index],
                                array=ordered.to_numpy(), cmap=cmap, norm=norm,
                                linewidths=2.6, capstyle='round', zorder=2)
    ax.add_collection(collection)
    ax.autoscale()
    ax.margins(.09)
    ax.set_aspect('equal')
    ax.axis('off')
    for i, lane in enumerate(selected):
        offset = {0: (18, -5), 2: (-18, 10)}.get(i, (8, 9))
        ax.annotate(str(i+1), midpoint(shapes[lane]), xytext=offset,
                    textcoords='offset points', ha='center', va='center',
                    fontsize=10, weight='bold', color=BLUE,
                    bbox={'boxstyle': 'circle,pad=.28', 'facecolor': 'white',
                          'edgecolor': BLUE, 'linewidth': 1},
                    arrowprops={'arrowstyle': '-', 'color': '#738A9A', 'linewidth': .8},
                    zorder=4)
    legend.axis('off')
    legend.text(0, .99, 'Faixas destacadas', fontsize=11.3, weight='bold', va='top')
    for i, lane in enumerate(selected):
        y = .84-i*.143
        name = 'Rua Vitória' if lane == '98384533_2' else labels[lane]['label']
        legend.text(.015, y-.025, str(i+1), ha='center', va='center',
                    fontsize=9.5, color=BLUE, weight='bold',
                    bbox={'boxstyle': 'circle,pad=.25', 'facecolor': 'white',
                          'edgecolor': BLUE, 'linewidth': 1})
        legend.text(.13, y, name, ha='left', va='top', fontsize=10.3)
        legend.text(.13, y-.052, pt(values[lane])+' m', ha='left', va='top',
                    fontsize=11, weight='bold', color=BLUE)
    # Escala métrica na geometria local original; sem rotação ou projeção nova.
    xlim, ylim = ax.get_xlim(), ax.get_ylim()
    x0, y0 = xlim[0]+30, ylim[0]+20
    ax.plot([x0, x0+100], [y0, y0], color=INK, linewidth=1.5, zorder=3)
    ax.text(x0+50, y0+13, '100 m', ha='center', va='bottom', fontsize=9, color=MUTED)
    ax.set_xlim(xlim); ax.set_ylim(ylim)
    colorbar(fig, [.04, .101, .55, .020], collection)
    fig.text(.64, .105, 'Rede simulada.\nValores por faixa.', fontsize=9, color=MUTED)
    finish(fig, output, STEMS[1])
    return {'linear_color_limits_m': [norm.vmin, norm.vmax],
            'selected_external_lane_ids': selected, 'map_lanes': len(values),
            'positive_lanes_colored': len(ordered)}


def main():
    root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--entrada', type=Path,
                        default=root/'output/analise/baseline_v1_filas_espacial_v1')
    parser.add_argument('--rotulos', type=Path,
                        default=root/'config/analise/rotulos_figuras_filas_tcc.json')
    parser.add_argument('--saida', type=Path,
                        default=root/'output/analise/baseline_v1_figuras_filas_tcc_v2')
    args = parser.parse_args()
    if args.saida.exists():
        raise ValueError('Escolher pasta de saída nova; arquivos existentes são preservados')
    primary, ref, pivot, shapes, labels, source_manifest, source_paths = read_inputs(
        args.entrada, args.rotulos)
    before = {str(p.resolve()): sha(p) for p in source_paths}
    args.saida.mkdir(parents=True)
    style()
    heat = draw_comparison(pivot, labels, args.saida)
    spatial = draw_map(ref, shapes, labels, args.saida)
    matrix = pivot.copy()
    matrix.insert(0, 'rotulo', [labels[lane]['label'] for lane in pivot.index])
    matrix.to_csv(args.saida/'valores_figura5_APOIO.csv', sep=';', encoding='utf-8-sig',
                  index_label='lane_id', float_format='%.17g')
    ref[['queue_mean_m', 'category']].to_csv(args.saida/'valores_figura6_APOIO.csv', sep=';',
                  encoding='utf-8-sig', index_label='lane_id', float_format='%.17g')
    mapping = pd.DataFrame([{'ordem_figura5': i+1, 'lane_id': lane,
                            'rotulo': labels[lane]['label'], 'fonte': labels[lane]['source']}
                           for i, lane in enumerate(pivot.index)])
    mapping.to_csv(args.saida/'mapeamento_rotulos_APOIO.csv', sep=';', index=False,
                   encoding='utf-8-sig')
    after = {str(p.resolve()): sha(p) for p in source_paths}
    if before != after: raise RuntimeError('Uma entrada foi alterada')
    manifest = {
        'version': VERSION, 'scope': 'APRESENTACAO_VISUAL_SEM_REANALISE',
        'repositories_consulted': REPOSITORIES,
        'demand_vehicles': 625, 'window_s': [0, 600], 'n_runs_per_composition': 30,
        'scenarios': SCENARIOS, 'same_top10_lane_ids': list(pivot.index),
        'queue_means_recomputed': False, 'lanes_aggregated_or_merged': False,
        'input_files_unchanged': before == after,
        'input_files_sha256': {p.name: sha(p) for p in source_paths},
        'original_analysis_version': source_manifest['version'],
        'comparison': heat, 'spatial_map': spatial,
        'palette': 'Blues', 'normalization': 'LINEAR_FROM_ZERO_AS_IN_ORIGINAL',
        'label_semantics': 'Uma linha por faixa original; ligações nomeadas pelas conexões da rede congelada',
        'script_sha256': sha(Path(__file__)),
        'versions': {'python': sys.version.split()[0], 'numpy': np.__version__,
                     'pandas': pd.__version__, 'matplotlib': matplotlib.__version__},
        'files_sha256': {p.name: sha(p) for p in args.saida.iterdir() if p.is_file()},
    }
    (args.saida/'manifesto_figuras_filas_tcc_v2.json').write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print('Figuras prontas: 70 células e 198 faixas preservadas; entradas inalteradas.')


if __name__ == '__main__':
    main()
