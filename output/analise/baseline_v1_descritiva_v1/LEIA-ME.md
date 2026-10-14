# Análise descritiva SUMO - versão 1

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
