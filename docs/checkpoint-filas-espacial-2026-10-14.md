# Checkpoint: análise espacial descritiva de filas

Data: 14/10/2026. O pesquisador enviou `filas_por_faixa.csv`. A tabela tem 249.480 registros e hash idêntico ao manifesto da consolidação. Cobre todas as 630 execuções e 198 faixas em duas janelas. As estatísticas locais reconciliam com os indicadores globais.

## Resultados para continuidade

Em REF/625, cinco faixas representam 62,34% da extensão agregada média de fila; dez representam 82,67%. As cinco principais são `-E5_0`, `203038544#1_2`, `-E6_0`, `98384533_2` e `:1138208969_3_0`.

Os nomes auxiliares dos quatro trechos externos são Farroupilha e Nicolau Cavon, da configuração de demanda, e Praça Nereu Ramos e Rua Vitória, do OSM por ID-base. A faixa interna corresponde ao movimento do trecho da Rua Vitória para o da Rua Nicolau Cavon, conforme conexão `via` na rede.

AGR/MIX_A reduzem as médias em locais importantes, mas há aumento em `99370098#0_0` (Rua Nicolau Cavon): 2,92 m em REF, 3,58 m em AGR e 3,93 m em MIX_A. A redução global não implica redução em cada faixa.

Os nomes originais da tabela estavam vazios. O mapeamento mantém fontes explícitas: 73 faixas externas por OSM, oito por demanda e 13 sem nome. Internas são identificadas por junção. O mapa usa geometria do snapshot congelado e não representa congestionamento real.

## Método e limites

As comparações são descritivas, pareadas pelas mesmas 30 seeds. Não há testes ou intervalos por faixa; esta etapa não está coberta pela família inferencial de 18 contrastes de viagem. Todas as observações, zeros válidos e faixas foram preservados.

A seleção dos gráficos usa REF/625 na mesma coleta e é exploratória. As tabelas completas incluem as outras demandas, janelas e faixas. Médias da fase [600,1800) foram derivadas por diferenças de áreas/contagens; máximos e episódios contínuos não foram inferidos.

Comprimentos exportados que ultrapassam o comprimento nominal da faixa não foram chamados de taxa de ocupação ou prova de bloqueio. Presença em amostras não foi tratada como duração de episódio contínuo.

## Caminhos

| Item | Caminho |
|---|---|
| Leitura principal | `docs/analise-filas-espacial-v1_0.md` |
| Script reprodutível | `scripts/analisar_filas_espacialmente.py` |
| Tabelas, mapas e manifesto | `output/analise/baseline_v1_filas_espacial_v1/` |
| Organização e reprodução opcional | `docs/README-filas-espacial.md` |

Não foram executadas novas simulações nem alterados os resultados anteriores ou o texto final do TCC. O próximo aprofundamento possível é temporal, com séries de fila da coleta existente para movimentos/localizações explicitamente escolhidos; os resumos por faixa não bastam para reconstruir episódios.
