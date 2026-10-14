"""Análise espacial descritiva de filas, com todas as seeds e faixas fixas.

Não executa SUMO nem altera entradas. Bibliotecas: NumPy, pandas e Matplotlib.
Os rótulos OSM por ID-base são auxiliares; a geometria vem da rede congelada.
"""
from pathlib import Path
import argparse, hashlib, json, re, sys
from datetime import datetime, timezone
import xml.etree.ElementTree as ET
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from matplotlib.colors import Normalize

SCENARIOS = ['REF','EQU','CAU','AGR','MIX_C','MIX_N','MIX_A']
KEYS = ['seed','demand_vehicles','scenario']
META = ['lane_id','edge_id','category','edge_from','edge_to','lane_length_m']
VERSION = '1.0.0'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def format_pt(value, places=2):
    return f'{value:.{places}f}'.replace('.', ',')


def validate(lanes, base, manifest, lane_path, base_path, net_path, demand_path):
    if not manifest['success'] or manifest['scope'] != 'COLETA_INTEGRAL':
        raise ValueError('Exigir consolidação integral bem sucedida')
    for path in [lane_path, base_path]:
        if sha(path) != manifest['published_files'][path.name]['sha256']:
            raise ValueError(f'Hash divergente: {path.name}')
    for path in [net_path, demand_path]:
        if sha(path) != manifest['snapshot_hashes'][path.name]:
            raise ValueError(f'Snapshot divergente: {path.name}')
    expected = {(s,d,c) for s in range(1000,1030) for d in [300,450,625] for c in SCENARIOS}
    keys=list(base[KEYS].itertuples(index=False,name=None))
    if len(keys)!=630 or set(keys)!=expected or not base.validation_status.eq('OK').all():
        raise ValueError('Base de execuções incompleta, duplicada ou não validada')
    if len(lanes)!=249480 or lanes.duplicated(KEYS+['lane_id','window_end_s']).any():
        raise ValueError('Tabela por faixa incompleta/duplicada')
    if set(lanes[KEYS].itertuples(index=False,name=None))!=expected:
        raise ValueError('Execuções por faixa não correspondem à base')
    if not lanes.window_begin_s.eq(0).all() or set(lanes.window_end_s)!={600,1800}:
        raise ValueError('Janelas inesperadas')
    if not lanes.sample_count.eq(lanes.window_end_s).all():
        raise ValueError('Número de amostras inesperado')
    if lanes.lane_id.nunique()!=198 or not lanes.groupby(KEYS+['window_end_s']).size().eq(198).all():
        raise ValueError('Cobertura espacial incompleta')
    for column in META[1:]:
        if not lanes.groupby('lane_id')[column].nunique(dropna=False).eq(1).all():
            raise ValueError('Metadado variável: '+column)
    metrics=['queue_mean_m','queue_max_m','queue_presence_pct','slow_experimental_mean_m',
             'slow_experimental_max_m','slow_experimental_presence_pct']
    if not np.isfinite(lanes[metrics]).all().all() or (lanes[metrics]<0).any().any():
        raise ValueError('Indicador ausente, negativo ou não finito')
    for prefix in ['queue','slow_experimental']:
        if (lanes[prefix+'_presence_pct']>100+1e-8).any():
            raise ValueError('Presença maior que 100%')
        if (lanes[prefix+'_mean_m']>lanes[prefix+'_max_m']+1e-7).any():
            raise ValueError('Média maior que máximo')
        if lanes.loc[lanes[prefix+'_max_m']==0,prefix+'_max_time_s'].notna().any():
            raise ValueError('Zero de fila recebeu instante de máximo')
        active=lanes[prefix+'_max_m']>0
        if lanes.loc[active,prefix+'_max_time_s'].isna().any():
            raise ValueError('Máximo positivo sem instante')
    reconciliations=[]
    indexed=base.set_index(KEYS).sort_index()
    for end in [600,1800]:
        group=lanes[lanes.window_end_s==end]
        for source,target in [('queue_mean_m','queue'),('slow_experimental_mean_m','queue_slow_experimental')]:
            for category in ['total','external','internal']:
                selected=group if category=='total' else group[group.category==category]
                sums=selected.groupby(KEYS)[source].sum().sort_index()
                expected_values=indexed[f'{target}_{category}_mean_m_0_{end}']
                residual=float((sums-expected_values).abs().max())
                if residual>1e-7:raise ValueError('Reconciliação falhou')
                reconciliations.append({'window_end_s':end,'indicator':source,'category':category,'max_absolute_residual_m':residual})
    return reconciliations


def map_lanes(lanes, net_path, demand_path, osm_path):
    net=ET.parse(net_path).getroot()
    edges={e.get('id'):e for e in net.findall('edge')}
    geometry={l.get('id'):l for e in edges.values() for l in e.findall('lane')}
    junctions={j.get('id'):j for j in net.findall('junction')}
    ways={}
    if osm_path:
        ways={w.get('id'):{t.get('k'):t.get('v') for t in w.findall('tag')}
              for w in ET.parse(osm_path).getroot().findall('way')}
    demand=json.loads(demand_path.read_text(encoding='utf-8-sig'))
    named={r['edge']:r.get('nome','') for key in ['origens','destinos'] for r in demand.get(key,[])}
    metadata=lanes[META].drop_duplicates().sort_values('lane_id').copy()
    output=[]
    for row in metadata.itertuples(index=False):
        if row.lane_id not in geometry:raise ValueError('Faixa ausente da rede: '+row.lane_id)
        lane=geometry[row.lane_id];edge=edges[row.edge_id]
        if abs(float(lane.get('length'))-row.lane_length_m)>1e-7:
            raise ValueError('Comprimento divergente da rede')
        actual='internal' if edge.get('function')=='internal' else 'external'
        if actual!=row.category:raise ValueError('Categoria divergente')
        match=re.match(r'^-?(\d+)(?:[#.]|$)',row.edge_id)
        osm_id=match.group(1) if match else ''
        osm_name=ways.get(osm_id,{}).get('name','')
        network_name=edge.get('name','')
        demand_name=named.get(row.edge_id,'')
        junction_id=row.edge_id[1:].rsplit('_',1)[0] if row.category=='internal' else ''
        if junction_id and junction_id not in junctions:junction_id=''
        if row.category=='internal':name='Interna da junção '+(junction_id or row.edge_id);origin='JUNCAO_REDE'
        elif network_name:name=network_name;origin='NOME_REDE'
        elif osm_name:name=osm_name;origin='OSM_ID_BASE'
        elif demand_name:name=demand_name;origin='ROTULO_DEMANDA_CONGELADA'
        else:name='Trecho sem nome';origin='SEM_NOME'
        points=[tuple(map(float,p.split(','))) for p in lane.get('shape','').split()]
        if len(points)<2:raise ValueError('Geometria de faixa insuficiente')
        output.append(dict(zip(META,row),mapped_name=name,name_source=origin,osm_way_id=osm_id,
                           osm_name=osm_name,demand_label=demand_name,junction_id=junction_id,
                           lane_shape=json.dumps(points,separators=(',',':'))))
    return pd.DataFrame(output),net


def summarize(lanes, metadata):
    group=['demand_vehicles','scenario','window_end_s','lane_id']
    summary=lanes.groupby(group).agg(n_seeds=('seed','nunique'),queue_mean_m=('queue_mean_m','mean'),
        sd_between_seeds_m=('queue_mean_m','std'),queue_presence_mean_pct=('queue_presence_pct','mean'),
        queue_max_mean_m=('queue_max_m','mean'),queue_max_observed_m=('queue_max_m','max'),
        slow_experimental_mean_m=('slow_experimental_mean_m','mean')).reset_index()
    summary=summary.merge(metadata.drop(columns='lane_shape'),on='lane_id',validate='many_to_one')
    contrast=[]
    for (d,end,lane),g in lanes.groupby(['demand_vehicles','window_end_s','lane_id'],sort=True):
        p=g.pivot(index='seed',columns='scenario',values='queue_mean_m').sort_index()
        for scenario in SCENARIOS[1:]:
            delta=p[scenario]-p.REF
            contrast.append({'demand_vehicles':d,'window_end_s':end,'lane_id':lane,'scenario':scenario,
                             'reference':'REF','n_pairs':30,'mean_delta_m':delta.mean(),
                             'sd_delta_m':delta.std(ddof=1),'median_delta_m':delta.median(),
                             'negative_pairs':int((delta<0).sum()),'positive_pairs':int((delta>0).sum()),
                             'zero_pairs':int((delta==0).sum()),'role':'DESCRITIVO_SEM_TESTE'})
    contrast=pd.DataFrame(contrast).merge(metadata[['lane_id','mapped_name','name_source','category']],on='lane_id',validate='many_to_one')
    early=lanes[lanes.window_end_s==600].set_index(KEYS+['lane_id']).sort_index()
    full=lanes[lanes.window_end_s==1800].set_index(KEYS+['lane_id']).reindex(early.index)
    late_mean=(full.queue_mean_m*1800-early.queue_mean_m*600)/1200
    early_count=np.rint(early.queue_presence_pct*6)
    full_count=np.rint(full.queue_presence_pct*18)
    late_count=full_count-early_count
    if (late_mean< -1e-7).any() or (late_count<0).any() or (late_count>1200).any():
        raise ValueError('Fase 600-1800 inconsistente')
    negative_roundoff=int((late_mean<0).sum())
    late=pd.DataFrame({'queue_mean_m_600_1800':late_mean.clip(lower=0),
                       'presence_pct_600_1800':late_count/12}).reset_index()
    late_summary=late.groupby(['demand_vehicles','scenario','lane_id']).agg(
        n_seeds=('seed','nunique'),queue_mean_m_600_1800=('queue_mean_m_600_1800','mean'),
        presence_pct_600_1800=('presence_pct_600_1800','mean')).reset_index()
    late_summary=late_summary.merge(metadata.drop(columns='lane_shape'),on='lane_id',validate='many_to_one')
    return summary,contrast,late_summary,negative_roundoff


def make_plots(summary, metadata, output):
    primary=summary[(summary.demand_vehicles==625)&(summary.window_end_s==600)]
    ref=primary[primary.scenario=='REF'].set_index('lane_id')
    top=ref.queue_mean_m.nlargest(10).index.tolist()
    pivot=primary.pivot(index='lane_id',columns='scenario',values='queue_mean_m').reindex(index=top,columns=SCENARIOS)
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':9,'axes.spines.top':False,'axes.spines.right':False})
    fig,ax=plt.subplots(figsize=(9.3,5.4),layout='constrained')
    im=ax.imshow(pivot.to_numpy(),cmap='YlOrRd',aspect='auto',vmin=0)
    labels=[]
    for i,lane in enumerate(top):
        row=ref.loc[lane]
        name=row.mapped_name.replace('Interna da junção ','Junção ')
        labels.append(f'{name}\n{lane}')
    ax.set_yticks(range(len(top)),labels);ax.set_xticks(range(7),SCENARIOS)
    for i in range(len(top)):
        for j in range(7):
            value=pivot.iloc[i,j]
            ax.text(j,i,format_pt(value),ha='center',va='center',fontsize=8,
                    color='white' if value>pivot.to_numpy().max()*.55 else '#17222b')
    ax.set_title('625 veículos: médias de extensão de fila por faixa, 0-600 s\nDez faixas selecionadas pela referência REF; 30 seeds; comparação descritiva',pad=12)
    fig.colorbar(im,ax=ax,label='Comprimento médio exportado (m)',shrink=.8)
    for suffix in ['png','svg']:fig.savefig(output/f'07_faixas_comparacao_625.{suffix}',dpi=220,bbox_inches='tight')
    plt.close(fig)
    values=ref.queue_mean_m
    shapes={r.lane_id:json.loads(r.lane_shape) for r in metadata.itertuples()}
    fig,(ax,legend)=plt.subplots(1,2,figsize=(9.3,6),gridspec_kw={'width_ratios':[1.6,1]},layout='constrained')
    norm=Normalize(0,float(values.max()));cmap=plt.get_cmap('YlOrRd')
    all_segments=[shapes[lane] for lane in values.index]
    ax.add_collection(LineCollection(all_segments,colors='#d5dce2',linewidths=1.1,zorder=1))
    ordered=values[values>0].sort_values()
    collection=LineCollection([shapes[lane] for lane in ordered.index],array=ordered.to_numpy(),
                              cmap=cmap,norm=norm,linewidths=2.3,zorder=2)
    ax.add_collection(collection);ax.autoscale();ax.margins(.09);ax.set_aspect('equal')
    ax.set_xlabel('Coordenada local X (m)');ax.set_ylabel('Coordenada local Y (m)')
    selected=ref[ref.category=='external'].queue_mean_m.nlargest(6).index.tolist()
    for i,lane in enumerate(selected):
        shape=np.asarray(shapes[lane]);dist=np.r_[0,np.cumsum(np.linalg.norm(np.diff(shape,axis=0),axis=1))]
        mid=[np.interp(dist[-1]/2,dist,shape[:,axis]) for axis in [0,1]]
        offset={0:(18,-5),2:(-18,10)}.get(i,(8,8))
        ax.annotate(str(i+1),mid,xytext=offset,textcoords='offset points',ha='center',va='center',
                    fontsize=9,bbox={'boxstyle':'circle,pad=.25','facecolor':'white','edgecolor':'#263c4b'},
                    arrowprops={'arrowstyle':'-','color':'#526979','linewidth':.7},zorder=4)
    legend.axis('off');legend.text(0,.98,'Maiores médias em faixas externas',va='top',weight='bold')
    for i,lane in enumerate(selected):
        row=ref.loc[lane]
        legend.text(0,.88-i*.115,f'{i+1}. {row.mapped_name}\n{lane}  |  {format_pt(row.queue_mean_m)} m',va='top',fontsize=9)
    legend.text(0,.12,'Geometria: rede congelada do SUMO.\nNomes: OSM por ID-base ou rótulo da demanda.\nNão é mapa de congestionamento real.',va='top',fontsize=8,color='#536671')
    fig.colorbar(collection,ax=ax,label='Média de fila exportada (m)',shrink=.65)
    fig.suptitle('Distribuição espacial das filas em REF / 625 veículos\nJanela 0-600 s; média de 30 seeds; faixas externas e internas',fontsize=11)
    for suffix in ['png','svg']:fig.savefig(output/f'08_mapa_filas_REF625.{suffix}',dpi=220,bbox_inches='tight')
    plt.close(fig)
    return top


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ['por-faixa','base','manifesto','rede','demanda','saida']:p.add_argument('--'+name,type=Path,required=True)
    p.add_argument('--osm',type=Path)
    args=p.parse_args()
    if args.saida.exists():raise ValueError('Usar pasta de saída nova')
    lanes=pd.read_csv(args.por_faixa,sep=';',encoding='utf-8-sig')
    base=pd.read_csv(args.base,sep=';',encoding='utf-8-sig')
    manifest=json.loads(args.manifesto.read_text(encoding='utf-8-sig'))
    reconciliations=validate(lanes,base,manifest,args.por_faixa,args.base,args.rede,args.demanda)
    metadata,net=map_lanes(lanes,args.rede,args.demanda,args.osm)
    summary,contrast,late,roundoff=summarize(lanes,metadata)
    concentration=[]
    for demand in [300,450,625]:
        ref=summary[(summary.demand_vehicles==demand)&(summary.scenario=='REF')&(summary.window_end_s==600)]
        for k in [1,2,5,10]:
            top=ref.nlargest(k,'queue_mean_m')
            concentration.append({'demand_vehicles':demand,'scenario':'REF','window_end_s':600,'top_k':k,
                                  'top_mean_sum_m':top.queue_mean_m.sum(),'total_mean_sum_m':ref.queue_mean_m.sum(),
                                  'share_pct':100*top.queue_mean_m.sum()/ref.queue_mean_m.sum(),
                                  'selected_lane_ids':' | '.join(top.lane_id),'selection':'REF_MESMA_COLETA_EXPLORATORIA'})
    decomposition=[]
    for (demand,scenario),group in contrast[contrast.window_end_s==600].groupby(['demand_vehicles','scenario']):
        decomposition.append({'demand_vehicles':demand,'scenario':scenario,'reference':'REF',
                              'total_mean_delta_m':group.mean_delta_m.sum(),
                              'positive_contributions_m':group.loc[group.mean_delta_m>0,'mean_delta_m'].sum(),
                              'negative_contributions_m':group.loc[group.mean_delta_m<0,'mean_delta_m'].sum(),
                              'positive_lanes':int((group.mean_delta_m>0).sum()),
                              'negative_lanes':int((group.mean_delta_m<0).sum()),
                              'unchanged_lanes':int((group.mean_delta_m==0).sum()),'role':'DESCRITIVO_SEM_TESTE'})
    args.saida.mkdir(parents=True)
    tables={'metadados_faixas.csv':metadata,'resumo_por_faixa.csv':summary,
            'contrastes_pareados_por_faixa.csv':contrast,'fase_600_1800_derivada.csv':late,
            'concentracao_REF.csv':pd.DataFrame(concentration),'decomposicao_diferencas.csv':pd.DataFrame(decomposition),
            'reconciliacao.csv':pd.DataFrame(reconciliations)}
    for name,table in tables.items():table.to_csv(args.saida/name,sep=';',index=False,encoding='utf-8-sig',float_format='%.12g')
    selected=make_plots(summary,metadata,args.saida)
    source_paths=[args.por_faixa,args.base,args.manifesto,args.rede,args.demanda]+([args.osm] if args.osm else [])
    info={'version':VERSION,'scope':'ESPACIAL_DESCRITIVA_EXPLORATORIA','rows_received':len(lanes),'runs':630,
          'lanes':198,'external_lanes':94,'internal_lanes':104,'seeds_excluded':0,'lanes_excluded':0,
          'windows':[[0,600],[0,1800]],'derived_window':[600,1800],
          'negative_roundoff_values_clipped_in_derived_window':roundoff,'negative_roundoff_tolerance_m':1e-7,
          'hypothesis_tests_or_confidence_intervals_computed':False,'top_selection':'REF625, mean queue length; same cohort; exploratory',
          'graph_lane_ids':selected,'name_source_counts':metadata.name_source.value_counts().to_dict(),
          'original_lane_name_field_nonempty_count':int(lanes.edge_name.notna().sum()),
          'beyond_lane_length_rows':int((lanes.queue_max_m>lanes.lane_length_m+1e-7).sum()),
          'interpretation_limit':'Exported queue extent can exceed lane length; no occupancy or spillback inferred. Presence is not continuous episode duration.',
          'source_files_sha256':{path.name:sha(path) for path in source_paths},
          'osm_repository':'valdirjunior/tc-valdir/mapa/nereu_ramos.osm' if args.osm else None,
          'osm_git_blob_sha':hashlib.sha1(b'blob '+str(args.osm.stat().st_size).encode()+b'\0'+args.osm.read_bytes()).hexdigest() if args.osm else None,
          'script_sha256':sha(Path(__file__)),'created_at_utc':datetime.now(timezone.utc).isoformat(),
          'versions':{'python':sys.version.split()[0],'numpy':np.__version__,'pandas':pd.__version__,'matplotlib':matplotlib.__version__},
          'files_sha256':{path.name:sha(path) for path in args.saida.iterdir() if path.is_file()}}
    (args.saida/'manifesto_analise_espacial.json').write_text(json.dumps(info,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(f'Validação OK: {len(lanes)} registros, 630 execuções, 198 faixas. {len(summary)} resumos, {len(contrast)} contrastes descritivos.')


if __name__=='__main__':main()
