"""Análise descritiva do TC/SUMO. Sem testes inferenciais e sem exclusão de seeds.

Entrada: resultados_consolidacao.zip do consolidador 1.0.0.
Dependências usadas: numpy, pandas, matplotlib, reportlab.
"""
from pathlib import Path
import argparse, csv, hashlib, io, json, math, shutil, sys, zipfile
from datetime import datetime, timezone
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak

SCENARIOS = ["REF", "EQU", "CAU", "AGR", "MIX_C", "MIX_N", "MIX_A"]
DEMANDS = [300, 450, 625]
PALETTE = dict(zip(SCENARIOS, ["#243746", "#8661a8", "#277da1", "#d1495b", "#72a8be", "#40916c", "#e49d30"]))
METRICS = {
 "travel_time_mean_s": ("Tempo médio de viagem", "s", "principal"),
 "trip_speed_mean_kmh": ("Velocidade média de viagem", "km/h", "principal"),
 "waiting_time_mean_s": ("Tempo parado médio", "s", "principal"),
 "queue_total_mean_m_0_600": ("Soma das filas: média 0-600 s", "m agregados", "principal"),
 "completion_flow_vph_0_600": ("Vazão de conclusão 0-600 s", "veículos/h", "principal"),
 "queue_total_mean_m_0_1800": ("Soma das filas: média 0-1800 s", "m agregados", "complementar"),
 "queue_lane_max_m_0_1800": ("Maior fila em uma faixa 0-1800 s", "m", "complementar"),
 "depart_delay_mean_s": ("Atraso médio de inserção", "s", "complementar"),
 "system_time_mean_s": ("Tempo médio desde partida programada", "s", "complementar"),
 "network_clearance_after600_s": ("Drenagem após 600 s", "s", "complementar"),
 "last_arrival_s": ("Última chegada", "s", "complementar"),
 "vehicles_with_waiting_pct": ("Viagens com tempo parado", "%", "complementar"),
 "waiting_share_pct": ("Fração do tempo acumulado parado", "%", "complementar"),
 "time_loss_mean_s": ("Tempo perdido ante ideal individual", "s", "complementar"),
 "emergency_braking_per1000trips": ("Frenagens por mil viagens", "eventos/1000 viagens", "complementar"),
}
SOURCES = [
 ("NIST/SEMATECH. Measures of Scale", "https://www.itl.nist.gov/div898/handbook/eda/section3/eda356.htm"),
 ("NIST/SEMATECH. Box Plot", "https://www.itl.nist.gov/div898/handbook/eda/section3/eda337.htm"),
 ("NIST/SEMATECH. Measures of Skewness and Kurtosis", "https://www.itl.nist.gov/div898/handbook/eda/section3/eda35b.htm"),
 ("Eclipse SUMO 1.27.1. MSDevice_Tripinfo.cpp", "https://github.com/eclipse-sumo/sumo/blob/v1_27_1/src/microsim/devices/MSDevice_Tripinfo.cpp"),
 ("Eclipse SUMO 1.27.1. MSQueueExport.cpp", "https://github.com/eclipse-sumo/sumo/blob/v1_27_1/src/microsim/output/MSQueueExport.cpp"),
]


def digest(data): return hashlib.sha256(data).hexdigest()
def ensure(condition, message):
 if not condition: raise ValueError(message)


def load(zip_path):
 with zipfile.ZipFile(zip_path) as z:
  ensure(z.testzip() is None, "ZIP com falha de CRC")
  payload = {name: z.read(name) for name in ("base_execucoes.csv", "validacao_consolidacao.csv", "manifesto_consolidacao.json", "dicionario_metricas.csv")}
 manifest = json.loads(payload["manifesto_consolidacao.json"])
 ensure(manifest.get("success") is True and manifest.get("scope") == "COLETA_INTEGRAL", "Entrada não é consolidação integral concluída")
 for name in ("base_execucoes.csv", "validacao_consolidacao.csv", "dicionario_metricas.csv"):
  ensure(digest(payload[name]) == manifest["published_files"][name]["sha256"], f"Hash divergente: {name}")
 d = pd.read_csv(io.BytesIO(payload["base_execucoes.csv"]), sep=";", encoding="utf-8-sig")
 validation = pd.read_csv(io.BytesIO(payload["validacao_consolidacao.csv"]), sep=";", encoding="utf-8-sig")
 dictionary = pd.read_csv(io.BytesIO(payload["dicionario_metricas.csv"]), sep=";", encoding="utf-8-sig")
 ensure(len(d) == 630 and len(validation) == 630, "Cobertura diferente de 630")
 expected = {(s, f, c) for s in range(1000, 1030) for f in DEMANDS for c in SCENARIOS}
 keys = list(d[["seed", "demand_vehicles", "scenario"]].itertuples(index=False, name=None))
 ensure(set(keys) == expected and len(set(keys)) == 630, "Chaves incompletas/duplicadas")
 ensure(set(dictionary.campo) == set(d.columns), "Dicionário diverge da base")
 ensure(set(validation.status) == {"OK"} and set(d.validation_status) == {"OK"}, "Diagnósticos precisam de investigação")
 ensure(set(validation[["seed", "demand_vehicles", "scenario"]].itertuples(index=False, name=None)) == expected, "Chaves da validação divergentes")
 ensure((d.trip_count == d.demand_vehicles).all(), "Quantidade de viagens incoerente")
 ensure((d.completed_count_0_1800 == d.demand_vehicles).all(), "Nem toda demanda concluiu")
 ensure(np.allclose(d.system_time_mean_s, d.travel_time_mean_s + d.depart_delay_mean_s, atol=1e-7), "Tempo de sistema incoerente")
 ensure(np.allclose(d.network_clearance_after600_s, np.maximum(0, d.last_arrival_s-600), atol=1e-7), "Tempo de drenagem incoerente")
 ensure(np.allclose(d.completion_flow_vph_0_600, 6*d.completed_count_0_600, atol=1e-7), "Vazão em 600 s incoerente")
 ensure(np.allclose(d.completion_flow_vph_0_1800, 2*d.demand_vehicles, atol=1e-7), "Vazão integral incoerente")
 ensure((d.groupby(["seed", "demand_vehicles"]).demand_base_sha256.nunique() == 1).all(), "Demanda-base mudou dentro de um bloco")
 ensure((d.profile_cauteloso_count + d.profile_normal_count + d.profile_agressivo_count == d.trip_count).all(), "Composição não soma a demanda")
 for horizon in (600, 1800):
  for prefix in ("queue", "queue_slow_experimental"):
   total = d[f"{prefix}_total_mean_m_0_{horizon}"]
   parts = d[f"{prefix}_external_mean_m_0_{horizon}"] + d[f"{prefix}_internal_mean_m_0_{horizon}"]
   ensure(np.allclose(total, parts, rtol=0, atol=1e-7), "Decomposição de filas incoerente")
  ensure((d[f"queue_lane_max_m_0_{horizon}"] <= d[f"queue_sum_max_m_0_{horizon}"]+1e-7).all(), "Máximo de fila incoerente")
 ensure((d.queue_lane_max_m_0_600 <= d.queue_lane_max_m_0_1800+1e-7).all(), "Máximo temporal incoerente")
 ensure(np.allclose(d.emergency_braking_count, d.emergency_braking_log_count), "Frenagens/avisos divergem")
 d = d.copy()
 d["trip_speed_mean_kmh"] = 3.6*d.trip_speed_mean_mps
 for field in METRICS:
  ensure(np.isfinite(d[field]).all() and (d[field]>=0).all(), f"Métrica não finita/negativa: {field}")
 audit = {"rows": len(d), "unique_keys": len(expected), "groups": 21, "seeds_per_group": 30,
          "total_trips_across_runs": int(d.trip_count.sum()), "emergency_braking": int(d.emergency_braking_count.sum()),
          "collisions": int(d.collision_count.sum()), "teleports": int(d.teleport_count.sum()),
          "source_zip_sha256": digest(zip_path.read_bytes()), "source_csv_sha256": digest(payload["base_execucoes.csv"]),
          "validation_OK_count": len(validation), "direct_raw_XML_scope": "Amostra previamente examinada: 3 execuções; a coleta integral foi verificada pelo consolidador local.",
          "lane_table_scope": "filas_por_faixa.csv não integra o ZIP recebido; não foi reexaminado diretamente nesta etapa."}
 return d, manifest, audit


def describe(values):
 a = np.asarray(values, dtype=float)
 n = len(a); mean = float(a.mean()); sd = float(a.std(ddof=1)); q1, q3 = np.quantile(a, [.25, .75], method="linear")
 m2 = float(np.mean((a-mean)**2)); m3 = float(np.mean((a-mean)**3))
 skew = math.sqrt(n*(n-1))/(n-2)*m3/(m2**1.5) if n>2 and m2>0 else np.nan
 return dict(n=n, mean=mean, sd_between_seeds=sd, median=float(np.median(a)), q1=float(q1), q3=float(q3),
             iqr=float(q3-q1), minimum=float(a.min()), maximum=float(a.max()),
             cv_pct=100*sd/mean if mean != 0 else np.nan, adjusted_skewness=skew)


def calculate(d):
 summaries, pair_rows, contrast_rows, flagged = [], [], [], []
 for demand in DEMANDS:
  groups = {c: d[(d.demand_vehicles == demand)&(d.scenario == c)].sort_values("seed").set_index("seed") for c in SCENARIOS}
  for scenario in SCENARIOS:
   for metric, (label, unit, role) in METRICS.items():
    a = groups[scenario][metric]
    ensure(len(a) == 30, "Grupo sem 30 seeds")
    stats = describe(a)
    summaries.append(dict(demand_vehicles=demand, scenario=scenario, metric=metric, label=label, unit=unit, role=role, **stats))
    lo, hi = stats["q1"]-1.5*stats["iqr"], stats["q3"]+1.5*stats["iqr"]
    for seed, value in a.items():
     if value<lo or value>hi:
      flagged.append(dict(demand_vehicles=demand, scenario=scenario, metric=metric, seed=int(seed), value=value,
                          fence_low=lo, fence_high=hi, scope="valor_da_execucao", action="MANTIDO"))
  for scenario in SCENARIOS[1:]:
   for metric, (label, unit, role) in METRICS.items():
    left, right = groups[scenario][metric], groups["REF"][metric]
    ensure(left.index.equals(right.index), "Pareamento desalinhado")
    delta = left-right
    percentage = pd.Series(np.nan, index=right.index, dtype=float)
    valid = right != 0
    percentage.loc[valid] = 100*delta.loc[valid]/right.loc[valid]
    stats = describe(delta)
    ensure(abs(stats["mean"]-(left.mean()-right.mean()))<1e-8, "Diferença média não reconciliada")
    contrast_rows.append(dict(demand_vehicles=demand, scenario=scenario, reference="REF", metric=metric, label=label, unit=unit, role=role,
        n_pairs=30, mean_delta=stats["mean"], sd_delta=stats["sd_between_seeds"], median_delta=stats["median"],
        q1_delta=stats["q1"], q3_delta=stats["q3"], minimum_delta=stats["minimum"], maximum_delta=stats["maximum"],
        adjusted_skewness_delta=stats["adjusted_skewness"], negative_pairs=int((delta<0).sum()), positive_pairs=int((delta>0).sum()),
        zero_pairs=int((delta==0).sum()), n_percent_pairs=int(valid.sum()), mean_paired_pct=percentage.mean(), median_paired_pct=percentage.median(),
        pct_of_group_means=100*(left.mean()-right.mean())/right.mean() if right.mean()!=0 else np.nan))
    for seed in left.index:
     pair_rows.append(dict(seed=int(seed), demand_vehicles=demand, scenario=scenario, reference="REF", metric=metric, unit=unit,
                          value=left.loc[seed], reference_value=right.loc[seed], delta=delta.loc[seed], paired_pct=percentage.loc[seed]))
    if metric == "travel_time_mean_s":
     lo, hi = stats["q1"]-1.5*stats["iqr"], stats["q3"]+1.5*stats["iqr"]
     for seed, value in delta.items():
      if value<lo or value>hi:
       flagged.append(dict(demand_vehicles=demand, scenario=scenario, metric=metric, seed=int(seed), value=value,
                           fence_low=lo, fence_high=hi, scope="diferenca_pareada", action="MANTIDO"))
 return pd.DataFrame(summaries), pd.DataFrame(pair_rows), pd.DataFrame(contrast_rows), pd.DataFrame(flagged)


def plots(d, pairs, folder):
 plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9, "axes.titlesize": 11, "axes.labelsize": 9,
                      "axes.spines.top": False, "axes.spines.right": False, "figure.facecolor": "white", "savefig.facecolor": "white"})
 def save(fig, name):
  fig.savefig(folder/(name+".png"), dpi=220, bbox_inches="tight")
  fig.savefig(folder/(name+".svg"), bbox_inches="tight")
  plt.close(fig)
 jitter = np.linspace(-.16,.16,30)
 fig, axes = plt.subplots(1, 3, figsize=(7.2,3.2), sharey=True, layout="constrained")
 for ax, demand in zip(axes, DEMANDS):
  data=[d[(d.demand_vehicles==demand)&(d.scenario==c)].sort_values("seed").travel_time_mean_s.to_numpy() for c in SCENARIOS]
  box=ax.boxplot(data, tick_labels=SCENARIOS, patch_artist=True, showfliers=False, widths=.55,
                  medianprops={"color":"#172b3a","linewidth":1.2}, whiskerprops={"color":"#69808e"}, capprops={"color":"#69808e"})
  for i,(scenario, values) in enumerate(zip(SCENARIOS,data),1):
   box["boxes"][i-1].set_facecolor(PALETTE[scenario]);box["boxes"][i-1].set_alpha(.28)
   ax.scatter(i+jitter,values,s=9,color=PALETTE[scenario],alpha=.7,zorder=3)
   ax.scatter(i,values.mean(),marker="D",s=18,c="#172b3a",zorder=5)
  ax.set_title(f"{demand} veículos");ax.tick_params(axis="x",labelrotation=65,labelsize=8);ax.grid(axis="y",alpha=.18);ax.set_ylim(70,170)
 axes[0].set_ylabel("Tempo médio por execução (s)")
 save(fig,"01_tempos_por_seed")

 fig,axes=plt.subplots(1,3,figsize=(7.2,3.3),sharey=True,layout="constrained")
 for ax,demand in zip(axes,DEMANDS):
  for y,scenario in enumerate(SCENARIOS[1:]):
   a=pairs[(pairs.demand_vehicles==demand)&(pairs.scenario==scenario)&(pairs.metric=="travel_time_mean_s")].sort_values("seed").delta.to_numpy()
   ax.scatter(a,y+jitter,s=11,c=PALETTE[scenario],alpha=.7)
   ax.scatter(a.mean(),y,marker="D",s=24,c="#172b3a",zorder=5)
  ax.axvline(0,color="#536878",linewidth=1);ax.set_title(f"{demand} veículos");ax.set_xlabel("Diferença ante REF (s)");ax.grid(axis="x",alpha=.18)
  ax.set_xlim({300:(-8,8),450:(-12,12),625:(-60,40)}[demand])
 axes[0].set_yticks(range(6),SCENARIOS[1:]);axes[0].invert_yaxis()
 save(fig,"02_diferencas_pareadas")

 fig,axes=plt.subplots(2,2,figsize=(7.2,4.7),layout="constrained")
 for ax,(field,label,unit) in zip(axes.ravel(),[("trip_speed_mean_kmh","Velocidade média","km/h"),("waiting_time_mean_s","Tempo parado","s"),
                                    ("queue_total_mean_m_0_600","Soma das filas: média 0-600 s","m agregados"),("completion_flow_vph_0_600","Vazão de conclusão 0-600 s","veículos/h")]):
  for scenario in SCENARIOS:
   mean=[];sd=[]
   for demand in DEMANDS:
    a=d[(d.demand_vehicles==demand)&(d.scenario==scenario)][field]
    mean.append(a.mean());sd.append(a.std(ddof=1))
   ax.errorbar(DEMANDS,mean,yerr=sd,marker="o",markersize=3,linewidth=1.2,elinewidth=.65,capsize=1.5,color=PALETTE[scenario],label=scenario,alpha=.9)
  ax.set_title(label);ax.set_ylabel(unit);ax.set_xticks(DEMANDS);ax.set_xlabel("Veículos programados");ax.grid(alpha=.15)
  if field!="trip_speed_mean_kmh":ax.set_ylim(bottom=0)
 handles,labels=axes[0,0].get_legend_handles_labels()
 fig.legend(handles,labels,ncol=7,loc="outside lower center",frameon=False,fontsize=8)
 save(fig,"03_metricas_complementares")

 fig,axes=plt.subplots(2,3,figsize=(7.2,4.3),layout="constrained")
 for ax,scenario in zip(axes.ravel(),SCENARIOS[1:]):
  a=pairs[(pairs.demand_vehicles==625)&(pairs.scenario==scenario)&(pairs.metric=="travel_time_mean_s")].delta.to_numpy()
  ax.hist(a,bins=8,color=PALETTE[scenario],alpha=.68,edgecolor="white")
  ax.axvline(a.mean(),c="#172b3a",lw=1.3);ax.axvline(np.median(a),c="#172b3a",lw=1.2,ls="--")
  ax.set_title(scenario);ax.set_xlabel("Diferença ante REF (s)");ax.set_ylabel("Seeds");ax.grid(axis="y",alpha=.12)
 save(fig,"04_distribuicoes_625")


def format_pt(value, decimals=2, sign=False):
 if value is None or not np.isfinite(value): return "n.a."
 return (f"{value:+.{decimals}f}" if sign else f"{value:.{decimals}f}").replace(".",",")


def report(d, summaries, contrasts, audit, target, charts):
 regular=font_manager.findfont(font_manager.FontProperties(family="DejaVu Sans"))
 bold=font_manager.findfont(font_manager.FontProperties(family="DejaVu Sans",weight="bold"))
 pdfmetrics.registerFont(TTFont("DV",regular));pdfmetrics.registerFont(TTFont("DV-Bold",bold))
 pdfmetrics.registerFontFamily("DV",normal="DV",bold="DV-Bold",italic="DV",boldItalic="DV-Bold")
 styles=getSampleStyleSheet()
 styles.add(ParagraphStyle(name="BodyDV",fontName="DV",fontSize=9.1,leading=13.1,textColor=colors.HexColor("#243746"),spaceAfter=7))
 styles.add(ParagraphStyle(name="SmallDV",parent=styles["BodyDV"],fontSize=8,leading=11,spaceAfter=5))
 styles.add(ParagraphStyle(name="TitleDV",fontName="DV-Bold",fontSize=20,leading=25,textColor=colors.HexColor("#16354a"),spaceAfter=12))
 styles.add(ParagraphStyle(name="HeadingDV",fontName="DV-Bold",fontSize=13,leading=17,textColor=colors.HexColor("#16354a"),spaceAfter=9))
 styles.add(ParagraphStyle(name="CellDV",fontName="DV",fontSize=7.8,leading=10.5))
 story=[]
 def p(text,style="BodyDV"):story.append(Paragraph(text,styles[style]))
 def h(text):p(text,"HeadingDV")
 def table(rows,widths=None,size=8.2):
  formatted=[[Paragraph(str(v),styles["CellDV"]) if isinstance(v,str) else v for v in row] for row in rows]
  t=Table(formatted,colWidths=widths,repeatRows=1,hAlign="LEFT")
  t.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,0),colors.HexColor("#e8f0f4")),("TEXTCOLOR",(0,0),(-1,0),colors.HexColor("#16354a")),
                        ("FONTNAME",(0,0),(-1,-1),"DV"),("FONTSIZE",(0,0),(-1,-1),size),("VALIGN",(0,0),(-1,-1),"MIDDLE"),
                        ("LEFTPADDING",(0,0),(-1,-1),6),("RIGHTPADDING",(0,0),(-1,-1),6),("TOPPADDING",(0,0),(-1,-1),5),
                        ("BOTTOMPADDING",(0,0),(-1,-1),5),("LINEBELOW",(0,0),(-1,0),.8,colors.HexColor("#7693a5")),
                        ("ROWBACKGROUNDS",(0,1),(-1,-1),[colors.white,colors.HexColor("#f6f8fa")])]))
  story.extend([t,Spacer(1,9)])
 def picture(name,width=510):
  img=Image(str(charts/(name+".png")));img.drawHeight=width*img.imageHeight/img.imageWidth;img.drawWidth=width
  story.extend([img,Spacer(1,5)])
 def newpage():story.append(PageBreak())
 def get(demand,scenario,metric="travel_time_mean_s"):
  return summaries[(summaries.demand_vehicles==demand)&(summaries.scenario==scenario)&(summaries.metric==metric)].iloc[0]

 p("Análise descritiva inicial<br/>Comportamentos de motoristas no SUMO","TitleDV")
 p("TC de Ciência da Computação - IFC Campus Videira<br/>Coleta oficial baseline_v1 - 14 de outubro de 2026","SmallDV")
 h("Cobertura e integridade")
 table([["Verificação","Resultado"],["Combinações seed × demanda × composição","630 chaves únicas, 21 grupos de 30 seeds"],
        ["Diagnósticos recebidos","630 OK; zero erros e zero avisos"],["Viagens nas execuções","288.750 concluídas; demanda conferida em cada execução"],
        ["Frenagens / colisões / teleportes","120 eventos / 0 / 0"],["Identidade dos arquivos","Hashes de base, validação e dicionário correspondem ao manifesto"]],[245,265])
 p("A base agregada foi reexaminada nesta etapa. A validação dos 630 conjuntos de XML é registrada pelo consolidador executado localmente. Aqui foram examinados diretamente os XML de três execuções na etapa anterior. A tabela completa de filas por faixa não integra o ZIP recebido.")
 h("Como ler os resultados")
 p("Cada observação é uma execução. Dentro de cada demanda, os sete cenários compartilham a demanda programada da mesma seed. As comparações ante REF preservam esses 30 pares. Veículos individuais não são tratados como repetições independentes do efeito da composição.")
 table([["Métrica principal","Operacionalização","Unidade"],["Tempo médio de viagem","Média de duration, para todas as viagens concluídas","s"],
        ["Velocidade média de viagem","Média de routeLength/duration por veículo; ×3,6","km/h"],
        ["Tempo parado","Média do acumulador waitingTime, incluindo zeros","s"],
        ["Filas","Média da soma dos comprimentos exportados em [0,600)","m agregados"],
        ["Vazão de conclusão","Chegadas em [0,600)/600 ×3600","veículos/h"]],[137,293,80])
 p("A média entre seeds dá o mesmo peso a cada execução. O desvio-padrão usa divisor 29; a mediana e o intervalo interquartil acompanham a média. Este relatório é descritivo: não apresenta testes de hipótese, p-valores ou intervalos de confiança.","SmallDV")

 newpage();h("1. Tempo médio de viagem e variação entre seeds")
 picture("01_tempos_por_seed")
 p("Pontos: 30 seeds por composição/demanda. Caixa: quartis e mediana. Losango: média. Os extremos permanecem como pontos. A escala vertical é comum aos três painéis.","SmallDV")
 rows=[["Composição","300 veículos<br/>média ± DP (s)","450 veículos<br/>média ± DP (s)","625 veículos<br/>média ± DP (s)"]]
 for c in SCENARIOS:
  rows.append([c]+[f"{format_pt(get(f,c)['mean'])} ± {format_pt(get(f,c)['sd_between_seeds'])}" for f in DEMANDS])
 table(rows,[87,141,141,141])
 p("<b>Observação.</b> AGR e MIX_A apresentam médias inferiores a REF nos três níveis de demanda. CAU apresenta a maior média entre as composições em cada nível. A dispersão aumenta especialmente em REF e CAU na demanda 625.")
 p(f"Na demanda 625, REF tem média {format_pt(get(625,'REF')['mean'])} s e mediana {format_pt(get(625,'REF')['median'])} s. CAU tem média {format_pt(get(625,'CAU')['mean'])} s e mediana {format_pt(get(625,'CAU')['median'])} s. As diferenças entre esses resumos refletem influência das execuções na cauda superior.")
 p("<b>Limitação.</b> Os perfis alteram speedFactor, aceleração, espaçamento e outros parâmetros simultaneamente. A comparação identifica o efeito do conjunto parametrizado. Não isola a contribuição de um único parâmetro e não demonstra que condução agressiva melhora o trânsito real.")

 newpage();h("2. Diferenças pareadas de tempo de viagem ante REF")
 picture("02_diferencas_pareadas")
 p("Diferença = cenário - REF na mesma seed/demanda. Valores negativos indicam menor tempo. Losango: média. Cada painel usa escala horizontal própria, indicada pelos eixos; a dispersão visual não deve ser comparada sem observar a escala.","SmallDV")
 rows=[["Demanda","Cenário","Δ média<br/>(s)","Δ mediana<br/>(s)","DP de Δ<br/>(s)","Seeds com<br/>Δ&lt;0", "% pareado<br/>médio"]]
 for demand in DEMANDS:
  for c in SCENARIOS[1:]:
   r=contrasts[(contrasts.demand_vehicles==demand)&(contrasts.scenario==c)&(contrasts.metric=="travel_time_mean_s")].iloc[0]
   rows.append([str(demand),c,format_pt(r.mean_delta,2,True),format_pt(r.median_delta,2,True),format_pt(r.sd_delta),f"{int(r.negative_pairs)}/30",format_pt(r.mean_paired_pct,2,True)+"%"])
 table(rows,[54,59,76,83,74,77,87])
 p("O percentual médio é a média de 100×(cenário-REF)/REF calculada nos 30 pares. Ele não é, em geral, o percentual obtido dividindo a diferença das médias pela média de REF. Ambas as convenções estão identificadas nas tabelas exportadas.","SmallDV")

 newpage();h("3. Velocidade, tempo parado, filas e vazão")
 picture("03_metricas_complementares")
 p("Pontos/linhas: médias entre seeds. Barras: ±1 desvio-padrão entre seeds, não intervalos de confiança. As linhas unem apenas os três níveis observados; não representam previsão entre demandas.","SmallDV")
 rows=[["625 veículos","Velocidade<br/>(km/h)","Tempo parado<br/>(s)","Soma das filas<br/>(m agregados)","Conclusões 0-600<br/>(veíc./h)"]]
 for c in SCENARIOS:
  rows.append([c]+[format_pt(get(625,c,m)['mean'],2 if m!="completion_flow_vph_0_600" else 1) for m in
                 ("trip_speed_mean_kmh","waiting_time_mean_s","queue_total_mean_m_0_600","completion_flow_vph_0_600")])
 table(rows,[90,91,105,114,110])
 p("<b>Observação.</b> Na demanda 625, AGR e MIX_A têm menor tempo de viagem e maiores taxas de conclusão que REF. MIX_A apresenta menor tempo parado e menor soma média de filas que AGR, apesar de ter tempo médio de viagem maior. Portanto, os indicadores não produzem uma ordenação única das composições.")
 p("<b>Interpretação e limites.</b> As métricas indicam efeitos diferentes sobre deslocamento e retenção. Velocidade e duração compartilham uma relação matemática com a distância, por isso não são evidências independentes. A extensão de fila também depende de espaçamentos e segmentação da rede. A taxa em dez minutos não estima a capacidade máxima da rede.","SmallDV")

 newpage();h("4. Assimetria e execuções na cauda das diferenças")
 picture("04_distribuicoes_625")
 p("Demanda 625, 30 diferenças pareadas por painel. Linha contínua: média. Tracejada: mediana. Os oito intervalos dos histogramas são uma escolha de visualização, não um teste de normalidade.","SmallDV")
 rows=[["Cenário","Δ média (s)","Δ mediana (s)","Assimetria ajustada","Seeds Δ&lt;0"]]
 for c in SCENARIOS[1:]:
  r=contrasts[(contrasts.demand_vehicles==625)&(contrasts.scenario==c)&(contrasts.metric=="travel_time_mean_s")].iloc[0]
  rows.append([c,format_pt(r.mean_delta,2,True),format_pt(r.median_delta,2,True),format_pt(r.adjusted_skewness_delta),f"{int(r.negative_pairs)}/30"])
 table(rows,[75,100,105,145,85])
 p("Há assimetria e diferenças extremas em alguns contrastes. Por exemplo, na seed 1027/demanda 625, REF apresenta 149,99 s; MIX_A, 97,39 s: diferença de -52,60 s. Essa execução permanece na média e nos gráficos. Valores além das cercas de 1,5×IQR foram sinalizados apenas para inspeção, sem exclusão.")
 p("O padrão impede escolher um procedimento inferencial apenas pela quantidade de cenários ou pela aparência de médias agregadas. Em métodos pareados, a distribuição das diferenças ou dos resíduos pertinentes precisa ser considerada. O desvio-padrão e a mediana mostram aspectos diferentes dessas 30 realizações.","SmallDV")

 newpage();h("5. Inserção, drenagem e frenagens de emergência")
 rows=[["625 veículos","Atraso de<br/>inserção (s)","Tempo de<br/>sistema (s)","Drenagem após<br/>600 s (s)"]]
 for c in SCENARIOS:
  rows.append([c]+[format_pt(get(625,c,m)['mean']) for m in ("depart_delay_mean_s","system_time_mean_s","network_clearance_after600_s")])
 table(rows,[91,139,139,141])
 p("Tempo de sistema = duration + departDelay. Drenagem = última chegada - 600 s, com toda a demanda concluída. As execuções vão até 1800 s, mas esse término configurado não é o instante em que a rede foi limpa. As médias de atraso de inserção variam entre as composições e complementam a duração interna.")
 rows=[["Composição","Eventos em 300","Eventos em 450","Eventos em 625","Total"]]
 for c in SCENARIOS:
  counts=[int(d[(d.scenario==c)&(d.demand_vehicles==f)].emergency_braking_count.sum()) for f in DEMANDS]
  rows.append([c]+[str(v) for v in counts]+[str(sum(counts))])
 table(rows,[86,113,113,113,85])
 p("Foram registrados 120 eventos no conjunto de 288.750 viagens das execuções, equivalentes a aproximadamente 0,42 evento por mil viagens. O contador principal corresponde aos avisos únicos do log; avisos repetidos entre arquivos não foram somados.")
 p("<b>Limitação.</b> A quantidade de eventos é pequena, seus critérios dependem do modelo e dos parâmetros de condução, e cada viagem é repetida sob diferentes composições. Esses números não representam probabilidade de acidente real. A ausência de colisões se refere aos critérios configurados e às condições desta simulação.")
 h("O que permanece para a investigação espacial")
 p("A base central contém sínteses da rede e a identificação de máximos por faixa. Para comparar persistentemente aproximações e cruzamentos, será necessária a tabela filas_por_faixa.csv gerada localmente. Ela não é necessária para os resumos globais apresentados aqui.")

 newpage();h("6. Cálculos, fontes e próximos procedimentos")
 p("Para uma métrica Y por execução e uma composição/demanda, n=30: média = soma(Y)/30; DP = raiz[soma((Y-média)²)/29]; IQR = Q3-Q1. Quartis e percentis usam interpolação linear. O coeficiente de assimetria é Fisher-Pearson ajustado, com o segundo momento calculado com divisor n [1-3].")
 p("Para cada seed: Δ = Y_cenário - Y_REF; Δ% = 100×Δ/Y_REF. Se Y_REF=0, o percentual é não aplicável e fica vazio nas tabelas; a diferença absoluta permanece. Os resumos informam quantos percentuais puderam ser calculados.")
 h("Proposta para a etapa inferencial")
 p("Manter tempo médio de viagem como desfecho central e os seis contrastes ante REF dentro de cada demanda como comparações principais. Se forem testados todos os níveis, haverá 18 contrastes do desfecho central. Definir como tratar multiplicidade antes de produzir p-valores.")
 p("Priorizar magnitude do efeito e incerteza de estimativas pareadas. Uma possibilidade a avaliar é intervalo para a diferença média por reamostragem dos blocos de seed, acompanhado da diferença mediana como descrição complementar. Não reamostrar veículos como se fossem repetições independentes. Esta possibilidade ainda não foi aplicada nem congelada como decisão.")
 p("Não há teste específico escolhido neste relatório. Os extremos observados são mantidos; não se altera o perfil ou a demanda em função dos resultados. Uma decisão inferencial deve respeitar a pergunta, as hipóteses do procedimento e o pareamento, e pode ser discutida com o orientador.")
 h("Fontes e rastreabilidade")
 p("Fonte dos resultados: resultados_consolidacao.zip, base_execucoes.csv e manifesto_consolidacao.json. Protocolo de extração: versão 0.2. Nenhum resultado foi gerado por nova simulação nesta etapa.","SmallDV")
 for i,(label,url) in enumerate(SOURCES,1):
  p(f'[{i}] {label}. <link href="{url}" color="#277da1">{url}</link>',"SmallDV")
 p("Documentação estatística consultada em 14/10/2026. As fontes [1-3] fundamentam os resumos e gráficos descritivos; [4-5] registram a implementação dos campos na versão usada. Elas não impõem a seleção dos contrastes ou do desfecho central.","SmallDV")
 p("SHA256 da base recebida:<br/>"+audit["source_csv_sha256"],"SmallDV")
 p("O pacote contém resumos completos para todas as métricas selecionadas, diferenças por seed, diagnósticos mantidos, gráficos PNG/SVG e o script de reprodução. A planilha bruta de 630 linhas permanece como fonte sem alterações.","SmallDV")

 def footer(canvas,doc):
  canvas.saveState();w,hh=A4
  canvas.setStrokeColor(colors.HexColor("#c4d4df"));canvas.line(42,hh-28,w-42,hh-28)
  canvas.setFont("DV",7);canvas.setFillColor(colors.HexColor("#69808e"))
  canvas.drawString(42,hh-21,"TC - análise descritiva da coleta SUMO baseline_v1")
  canvas.drawString(42,23,"30 seeds por grupo. Nenhuma seed excluída. Sem testes inferenciais nesta etapa.")
  canvas.drawRightString(w-42,23,str(doc.page));canvas.restoreState()
 document=SimpleDocTemplate(str(target),pagesize=A4,rightMargin=42,leftMargin=42,topMargin=43,bottomMargin=42,
                           title="Análise descritiva inicial do experimento SUMO",author="Valdir Rugiski Junior")
 document.build(story,onFirstPage=footer,onLaterPages=footer)


def main():
 parser=argparse.ArgumentParser(description=__doc__)
 parser.add_argument("--entrada",type=Path,required=True)
 parser.add_argument("--saida",type=Path,required=True)
 args=parser.parse_args();ensure(not args.saida.exists(),"Usar pasta de saída nova")
 d,source_manifest,audit=load(args.entrada)
 summaries,pairs,contrasts,flags=calculate(d)
 output=args.saida;output.mkdir(parents=True)
 tables=output/"tabelas";tables.mkdir();charts=output/"graficos";charts.mkdir();scripts=output/"scripts";scripts.mkdir()
 for name,frame in (("resumo_por_cenario.csv",summaries),("diferencas_pareadas_por_seed.csv",pairs),
                    ("resumo_contrastes_pareados.csv",contrasts),("observacoes_para_inspecao_MANTIDAS.csv",flags)):
  frame.to_csv(tables/name,sep=";",index=False,encoding="utf-8-sig",float_format="%.12g",na_rep="")
 plots(d,pairs,charts)
 report_path=output/"Analise_Descritiva_SUMO_v1.pdf"
 report(d,summaries,contrasts,audit,report_path,charts)
 shutil.copyfile(__file__,scripts/"analisar_descritivamente.py")
 metadata={"analysis_version":"1.0", "scope":"DESCRITIVO_SEM_INFERENCIA", "created_at_utc":datetime.now(timezone.utc).isoformat(),
           "audit":audit,"seeds_excluded":0,"scenario_order":SCENARIOS,"metrics":METRICS,
           "within_group_sd_ddof":1,"quantile_method":"linear","skewness":"adjusted Fisher-Pearson",
           "outlier_rule":"1.5 IQR; sinalização sem exclusão","primary_percentage_summary":"mean of per-seed paired percentages",
           "no_confidence_intervals_or_hypothesis_tests":True,"source_consolidator_version":source_manifest["analyzer_version"],
           "runtime_versions":{"python":sys.version.split()[0],"numpy":np.__version__,"pandas":pd.__version__,"matplotlib":matplotlib.__version__},
           "files_sha256":{p.relative_to(output).as_posix():digest(p.read_bytes()) for p in output.rglob("*") if p.is_file()}}
 (output/"manifesto_analise.json").write_text(json.dumps(metadata,ensure_ascii=False,indent=2),encoding="utf-8")
 (output/"LEIA-ME.md").write_text("""# Análise descritiva SUMO - versão 1

O relatório reúne a primeira leitura da coleta integral. Nenhuma seed foi excluída e nenhum teste inferencial ou intervalo de confiança foi aplicado. A unidade de comparação é a execução/seed, respeitando a demanda e o pareamento com REF.

## Conteúdo
- Analise_Descritiva_SUMO_v1.pdf: resultados, cálculos, interpretação e limitações.
- tabelas/resumo_por_cenario.csv: 21 grupos × 15 métricas, com média, DP amostral, mediana, quartis, amplitude, CV e assimetria.
- tabelas/diferencas_pareadas_por_seed.csv: 30 seeds × 18 contrastes × 15 métricas; valores individuais, REF, diferença absoluta e percentual pareado.
- tabelas/resumo_contrastes_pareados.csv: magnitude, dispersão e sinais das diferenças; percentuais por seed e das médias identificados separadamente.
- tabelas/observacoes_para_inspecao_MANTIDAS.csv: observações além das cercas de 1,5×IQR; todas permanecem na análise.
- graficos/: PNG em 220 dpi e SVG vetorial para exportação. Barras representam DP, não intervalos de confiança.
- manifesto_analise.json: escopo, convenções e hashes.
- scripts/analisar_descritivamente.py: reprodução dos cálculos e gráficos.

CSV: separador ponto e vírgula, decimal ponto, UTF-8 com BOM. Percentuais não aplicáveis têm célula vazia; não foram convertidos em zero. Valores no PDF são arredondados apenas para apresentação. Em resumo_por_cenario, métricas de fila máxima são resumos entre os máximos de cada execução, não máximos de uma fila média.

Não é necessário executar o script para utilizar os arquivos. Para reprodução, ele usa NumPy, pandas, Matplotlib e ReportLab; as versões verificadas estão no manifesto. Recebe o ZIP produzido pelo consolidador:

python scripts/analisar_descritivamente.py --entrada resultados_consolidacao.zip --saida exploracao_reproduzida

A pasta de saída precisa ser nova. A extração e as estatísticas originais permanecem inalteradas. As 630 saídas XML completas não foram reenviadas: a inspeção desta etapa é da base e dos diagnósticos do processamento local, com conferência direta anterior de uma amostra de três execuções.
""",encoding="utf-8")
 print(json.dumps({"output":str(output.resolve()),"groups":len(summaries),"paired_rows":len(pairs),"contrasts":len(contrasts),"flags_retained":len(flags),"audit":audit},ensure_ascii=False))


if __name__=="__main__":main()
