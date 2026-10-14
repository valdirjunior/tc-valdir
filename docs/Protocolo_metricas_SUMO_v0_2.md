# Protocolo de extração e comparação de métricas — TC / SUMO

Versão 0.2 — 14 de outubro de 2026

**Status:** proposta técnica fundamentada na inspeção da amostra oficial. A simulação permanece congelada. Esta versão resolve as pendências de formato e significado dos dados da amostra; não escolhe um teste estatístico e não representa aprovação formal do orientador. O desfecho central proposto continua sendo o tempo médio de viagem.

## 1. Material examinado e alcance da conferência

Foi examinado o pacote `amostra_analise_seed1000_20261014_161018_53e217.zip`, com 48 arquivos. Ele contém:

- REF / seed 1000 / demandas 300, 450 e 625, com todas as saídas preservadas;
- demanda-base das três combinações;
- manifesto, registro das execuções e tempo de execução;
- snapshot da rede, perfis, configuração da demanda e scripts de geração, atribuição e execução.

O registro possui 630 chaves únicas seed × demanda × composição, todas com status OK. Os arquivos de saída examinados, porém, abrangem apenas três dessas execuções. Isso não constitui nova validação dos 630 conjuntos de XML. O relatório de validação integral informado pelo pesquisador permanece uma informação separada.

Os cinco hashes SHA256 constantes do manifesto correspondem aos arquivos do snapshot: rede, configuração da demanda, perfis, gerador e atribuidor. Esta verificação estabelece coerência documental e não calibração empírica da rede.

### Configuração efetivamente registrada

| Item | Valor |
|---|---|
| Simulador | Eclipse SUMO 1.27.1 |
| Modelo de acompanhamento | Krauss |
| Seed da amostra | 1000 |
| Demanda programada | 0 a 600 s |
| Início/fim da simulação | 0 / 1800 s |
| Passo de simulação | 0,1 s |
| Período de `queues.xml` | 1 s |
| Período de `summary.xml` | 1 s |
| Escrita de viagens inacabadas | Ativada |
| Teleporte por tempo de retenção | Desativado (`time-to-teleport = -1`) |
| Ação de colisão | Aviso |
| Verificação de colisões nos cruzamentos | Ativada |

Nas três execuções, todos os veículos foram inseridos e concluíram o percurso: 300, 450 e 625. Não há viagens com `arrival < 0`, IDs duplicados, remoções indicadas por `vaporized`, veículos ativos ou aguardando inserção no final, teleportes ou colisões registrados. `stopTime` é zero para todos os veículos da amostra. As rotas de REF correspondem às respectivas rotas-base, exceto pela atribuição do tipo normal.

O código de atribuição confirma que a realização de demanda-base é reutilizada entre as composições dentro de seed × demanda. A conferência direta das sete rotas de cada bloco será feita pelo consolidador na coleta completa.

## 2. Objetivo e princípios preservados

O PTC prevê tempo médio de viagem, velocidade média, tempo parado, formação/comprimento de filas e vazão. As seções 3.7 e 3.8 orientam a comparação entre composições com o mesmo nível de demanda e a utilização de REF como referência.

As escolhas abaixo explicitam a operacionalização sem alterar a rede ou os perfis. Não excluir seeds por congestionamento, frenagens ou resultados inconvenientes. Valores extremos plausíveis fazem parte do experimento. Inconsistências técnicas devem ser registradas e investigadas, sem exclusão silenciosa nem substituição de valores.

A execução é a unidade da base central; a seed é o bloco de comparação dentro de cada demanda. Veículos de uma mesma execução não são repetições independentes do tratamento comportamental.

Os XML brutos preservam informação para extrações adicionais. Não é necessário exportar toda variável disponível agora ou inserir todo indicador no TCC. A escolha de indicadores principais, fórmulas e contrastes antecede a avaliação comparativa das composições.

## 3. População, janelas e notação

Para cada execução, considerar N viagens concluídas válidas, verificando N contra a demanda esperada. Definir:

- T_i = `duration`, s;
- L_i = `routeLength`, m;
- W_i = `waitingTime`, s;
- D_i = `departDelay`, s;
- A_i = `arrival`, s;
- q_l(t) = `queueing_length` exportado para a faixa l no instante t, m.

### Duas janelas de saída e uma população de viagens

**Viagens completas:** médias por veículo incluem todos os veículos programados, inclusive os que chegaram depois de 600 s. Não recortar as viagens em 600 s nem utilizar apenas os que chegaram cedo.

**Janela principal para vazão de conclusão e filas durante a geração:** [0,600). Essa proposta foi registrada na versão 0.1, antes da leitura da amostra. Uma chegada exatamente em 600 s fica fora dessa janela.

**Janela integral para filas e vazão complementar:** [0,1800), igual para todas as execuções. Foi confirmada a existência desse horizonte comum. Registrar também os indicadores dessa janela para não ocultar a drenagem e os picos posteriores a 600 s. Não trocar a janela principal porque uma delas produz diferenças maiores.

A simulação continua até 1800 s mesmo depois de toda a rede esvaziar. Logo, seu horário de término não é o instante de limpeza da rede. As médias temporais na janela integral incluem os zeros após a última fila e têm interpretação distinta das médias no período de geração.

É um experimento de demanda finita, incluindo carregamento e drenagem. Não representa regime estacionário. Não inserir aquecimento, filtros temporais ou novo período de observação depois de examinar as diferenças entre composições.

## 4. Tempo médio de viagem — desfecho central proposto

Fonte: `tripinfo.xml/duration`.

T_medio = Σ_i T_i / N

Unidade: s por viagem.

Campo: `travel_time_mean_s`.

O código da versão utilizada calcula a duração desde a inserção efetiva até a chegada. Na amostra, `duration = arrival − depart` para todos os 1375 veículos. Não incluir `departDelay` nessa métrica.

Registrar como complementos:

- `depart_delay_mean_s` = Σ_i D_i / N;
- `system_time_mean_s` = Σ_i (T_i + D_i) / N;
- `travel_time_median_s`;
- `travel_time_p95_s`.

O tempo de sistema corresponde à partida programada até a chegada quando a diferença entre a partida programada e efetiva é `departDelay`. Essa identidade foi conferida na amostra. Permite observar retenção na entrada, que a duração interna isolada não representa.

O percentil 95 descreve a cauda das viagens, não um intervalo de confiança. A média de `stats.xml/vehicleTripStatistics.duration` serve para checagem cruzada entre saídas do mesmo simulador, não como validação independente da realidade.

## 5. Velocidade média de viagem

### Métrica principal

v_i = L_i / T_i

v_medio = Σ_i v_i / N

Fonte: `tripinfo.xml`, campos `routeLength` e `duration`.

Unidade: m/s; para apresentação, km/h = 3,6 × m/s.

Campo: `trip_speed_mean_mps`.

Cada veículo tem o mesmo peso. O tempo de viagem inclui retenções dentro do percurso. Esta definição foi proposta na versão 0.1 pela interpretação por veículo. O código `MSDevice_Tripinfo.cpp` da tag `v1_27_1` confirma a acumulação de L_i/T_i na estatística de velocidade de viagens; os valores calculados também correspondem ao campo `stats.xml/speed`, dentro do arredondamento.

### Complemento com outra ponderação

v_agregado = Σ_i L_i / Σ_i T_i

Campo: `aggregate_trip_speed_mps`.

Essa razão pondera as velocidades de viagem pelo tempo T_i. Não é igual à média aritmética das velocidades individuais e não deve ter o mesmo nome. Descreve distância por tempo acumulado dos veículos; não utilizar a duração de relógio da simulação no denominador.

### Velocidade instantânea

`summary.xml/meanSpeed` descreve os veículos presentes naquele instante, não as viagens completas. Na amostra, esse campo vale −1 quando a rede está vazia. Esse sentinela não é velocidade negativa e não deve entrar numa média numérica. Não substituir a métrica principal pela média dos registros temporais.

Controles: T_i > 0, comprimento de percurso, IDs e igualdade das rotas programadas entre composições. A diferença entre velocidades de viagem pode refletir tanto tempos de percurso quanto a distribuição de comprimentos; o pareamento das rotas ajuda a controlar isso.

## 6. Tempo parado por viagem

W_medio = Σ_i W_i / N

Fonte: `tripinfo.xml/waitingTime`.

Unidade: s por viagem.

Campo: `waiting_time_mean_s`.

Usar o acumulador de espera do SUMO, operacionalmente associado a movimento praticamente nulo, com limiar de velocidade de 0,1 m/s e exclusão de paradas programadas. O código da versão também considera a condição de aceleração no acumulador; não tentar reconstruir essa medida a partir de uma contagem simplificada de velocidades do `summary.xml`.

Incluir os veículos com W_i = 0. Uma média apenas entre veículos que pararam responderia a outra pergunta.

Complementos:

- `vehicles_with_waiting_pct` = 100 × quantidade de veículos com W_i > 0 / N;
- `waiting_share_pct` = 100 × Σ_i W_i / Σ_i T_i;
- `waiting_count_mean` = média de `waitingCount`.

`waiting_share_pct` é a proporção do tempo acumulado das viagens que foi registrado como espera. Não confundir com a média de W_i/T_i por veículo. Não confundir `waitingTime` com `stopTime`, atraso de inserção ou `summary.xml/waiting`.

## 7. Filas — significado específico da versão 1.27.1

Fonte: `queues.xml`, blocos `<data timestep>` e seus registros `<lane>`.

### Distinções confirmadas no código da versão

1. `queueing_length` é a maior distância entre o fim da faixa e a traseira de um veículo com espera corrente registrada. É uma extensão espacial associada à retenção, não a quantidade de veículos parados.
2. O cálculo não verifica se todos os veículos entre esse ponto e o fim da faixa formam uma fila contínua. Não afirmar que é uma contagem ou uma fila necessariamente compacta.
3. `queueing_length_experimental` utiliza veículo com velocidade < 5 km/h e posição longitudinal > 25% do comprimento da faixa, medida desde o início. Manter esse campo como complemento com nome próprio; não o tratar como equivalente ao primeiro.
4. `queueing_time` é o máximo das esperas correntes dos veículos considerados na faixa. Não é a soma de `waitingTime` das viagens. A documentação genérica usa uma descrição ambígua; para esta versão, o código foi usado para resolver a definição. Não somar esse campo no tempo para obter tempo total parado.
5. Uma linha de faixa só é escrita se um dos dois comprimentos ultrapassar 1 m. A existência de uma linha não implica `queueing_length > 0`: há linhas com o primeiro campo zero e o experimental positivo.

Na amostra, os três `queues.xml` contêm 1800 blocos temporais consecutivos, em 0,1,...,1799 s. Os blocos sem faixas são registros válidos vazios. No horizonte de 600 s existem 600 observações, em 0,...,599 s; no integral, 1800.

### Zeros e omissões

Para uma faixa elegível ausente num bloco temporal existente, atribuir zero **à série de comprimentos exportados**. Não declarar que isso prova ausência física de qualquer retenção: a saída possui seu critério e limiar de exportação. Com veículos de comprimento usual, o corte de 1 m tende a ter pouca influência, mas não modificar o valor para compensá-lo.

Não transformar lacunas de tempo, arquivo truncado ou erro de leitura em zero. Exigir a grade temporal completa e crescente. Para presença de fila segundo o campo principal, usar `queueing_length > 0`, não a existência do elemento `<lane>`.

### Cobertura espacial proposta

A rede congelada possui 94 faixas externas e 104 internas, todas permitindo veículos passenger conforme seus atributos. Os arquivos incluem registros internos dos cruzamentos.

A versão 0.1 propunha a cobertura externa com complementos locais. Refinamento técnico nesta versão: manter a cobertura completa das 198 faixas elegíveis, com decomposição fixa em externas e internas. O motivo é o significado de avaliação global da rede, que inclui seus cruzamentos, e a abrangência real do arquivo; não diferenças entre composições, que ainda não foram examinadas.

O conjunto é definido pelo snapshot e pelas permissões, nunca pelas faixas que apareceram com fila em uma execução. Não atribuir a cada faixa interna o significado de uma rua independente. A tabela por faixa deve guardar edge, nome, origem/destino quando disponíveis e indicação `internal`.

### Indicadores por execução

Para cada janela J, com M_J observações igualmente espaçadas de 1 s:

Q_soma(t) = Σ_l q_l(t)

Q_medio_J = Σ_{t em J} Q_soma(t) / M_J

**Principal:** média da soma dos comprimentos exportados, em metros agregados entre faixas. Campo `queue_total_mean_m_0_600`; complemento `queue_total_mean_m_0_1800`.

Calcular a mesma medida para faixas externas e internas separadamente. A soma das duas médias deve reproduzir a média total. É uma decomposição espacial, não duas evidências independentes.

**Máximo:** q_max_J = max_{l,t em J} q_l(t). Campos `queue_lane_max_m_0_600` e `queue_lane_max_m_0_1800`, acompanhados da faixa e do instante. Não confundir com o máximo temporal da soma Q_soma(t).

**Persistência por faixa:** P_l,J = 100 × quantidade de observações com q_l(t) > 0 / M_J. Unidade: % das observações temporais. Como síntese da rede, a média sobre o conjunto fixo das faixas significa proporção de observações faixa × tempo com fila exportada.

As médias discretas equivalem à aproximação de uma integral com peso de 1 s por amostra. São estatísticas da grade registrada, não uma reconstrução exata dos passos de 0,1 s. Um pico ou parada ocorrido inteiramente entre amostras pode não ser observado. Para [0,600), cada amostra recebe peso de 1/600; para [0,1800), 1/1800.

Não converter comprimentos em quantidade de veículos pela divisão por um comprimento médio. Não reduzir um comprimento por ultrapassar o comprimento geométrico da faixa sem investigar: a fórmula inclui a traseira do veículo.

Para o campo experimental, produzir somente indicadores auxiliares claramente identificados. Preservar a tabela por faixa, inclusive faixas sem registros positivos, para localizar retenções sem mudar o denominador entre execuções.

## 8. Vazão de conclusão de viagens

C_600 = quantidade de veículos com 0 ≤ A_i < 600

F_600 = C_600 / 600 × 3600 = 6 × C_600

Fonte primária: `tripinfo.xml/arrival` e identificação da viagem concluída.

Unidade: veículos/h, taxa equivalente na janela de dez minutos.

Campos: `completed_count_0_600`, `completion_flow_vph_0_600` e `completed_share_pct_0_600` = 100 × C_600 / demanda esperada.

A pergunta é quantas viagens foram concluídas durante o horizonte de geração. Não é volume de entrada programado, fluxo em um detector, capacidade máxima ou vazão estacionária. O carregamento inicial e o tempo necessário para atravessar a rede fazem parte da interpretação.

Como complemento integral, registrar C_1800 e F_1800 = C_1800/1800 × 3600. Se todos concluem, F_1800 vale duas vezes a demanda: 600, 900 ou 1250 veículos/h. É uma medida válida de taxa no horizonte integral, mas não distingue composições da mesma demanda nesta situação. Não ocultar essa ausência de discriminação.

Contagem final de viagens é também controle de atendimento da demanda. Não dividir automaticamente N pelo horário da última chegada e chamar de capacidade da rede.

`summary.xml/arrived` pode auxiliar a conferência; `ended` também inclui remoções. Com registros de 1 s e chegadas em passos de 0,1 s, o corte exato de uma janela deve vir de `tripinfo.xml`. Na amostra REF/450, o contador em 599 s é 380, mas 382 viagens têm chegada <600 s. Isso é compatível com chegadas ocorridas entre amostras, não divergência no número final. Não usar o contador da amostra anterior ao corte como se contasse todas as chegadas da janela.

## 9. Complementos e controles

| Indicador | Cálculo / fonte | Cuidado |
|---|---|---|
| Atraso de inserção | Média de `departDelay`, s | Separado da duração interna |
| Tempo desde partida programada | Média de T_i + D_i, s | Incluir retenção antes da entrada |
| Tempo perdido | Média de `timeLoss`, s | Referência depende da velocidade ideal individual, incluindo `speedFactor` |
| Última chegada | max_i A_i, s | Não é o fim configurado de 1800 s |
| Drenagem após geração | max(0, max_i A_i − 600), s | Exigir que toda a demanda tenha concluído |
| Frenagens de emergência | `stats.xml/safety@emergencyBraking` | Campo presente na versão da coleta |
| Frenagens por mil viagens | 1000 × eventos / N | Eventos, não porcentagem de motoristas ou risco real de acidente |
| Veículos com aviso de frenagem | IDs únicos em `warnings.log` | Não contar duas vezes o mesmo aviso de `sumo.log` |
| Comprimento de percurso | Média de L_i, m | Controle da demanda e rotas |
| Colisões e teleportes | Contadores e XML de colisões | Coerência técnica, não validação de segurança real |
| Pendências / remoções | `arrival`, `vaporized`, `running`, `waiting`, IDs | Não remover resultados silenciosamente |

`timeLoss` já inclui perdas ligadas a retenção. Não somá-lo a `waitingTime` como se fossem parcelas independentes. Os perfis têm `speedFactor` diferente, por isso o referencial de velocidade ideal varia. Usá-lo para complemento interpretativo, sem defini-lo como único atraso absoluto comparável a uma velocidade comum.

Na amostra, há um evento de frenagem em REF/450. Ele aparece uma vez em `warnings.log`, uma vez em `sumo.log` e como `emergencyBraking = 1` em `stats.xml`: é um evento, não dois. REF/300 e REF/625 têm zero no contador. `emergencyStops` é um atributo diferente.

A última chegada foi 729,8 / 740,1 / 829,7 s para REF/300, REF/450 e REF/625. Os tempos de drenagem após 600 s são 129,8 / 140,1 / 229,7 s. A continuidade da simulação até 1800 s não aumenta esses tempos.

## 10. Cálculos de conferência na amostra

Estes números provêm somente de seed 1000 e composição REF. Servem para verificar a extração. Não estimam efeito dos perfis ou médias entre seeds.

| Demanda | Viagens concluídas | Tempo médio (s) | Velocidade média de viagem (m/s) | Tempo parado médio (s) | Conclusões <600 s | Vazão 0–600 (veíc./h) |
|---|---:|---:|---:|---:|---:|---:|
| 300 | 300 | 87,19200 | 11,58150 | 1,40133 | 256 | 1536 |
| 450 | 450 | 89,83467 | 11,17767 | 3,49533 | 382 | 2292 |
| 625 | 625 | 108,37248 | 10,02759 | 15,78432 | 503 | 3018 |

As médias de duração, distância, espera, atraso e perda de tempo correspondem às estatísticas do SUMO dentro do arredondamento. Velocidades pela razão das somas: 11,44602 / 10,96209 / 9,10975 m/s. A diferença entre essa razão e a média individual confirma que os indicadores precisam de nomes distintos.

| Demanda | Soma das filas: média 0–600 (m agregados) | Média 0–1800 (m agregados) | Máximo em uma faixa 0–600 (m) | Máximo em uma faixa 0–1800 (m) |
|---|---:|---:|---:|---:|
| 300 | 3,29537 | 1,20596 | 12,63 | 12,63 |
| 450 | 15,46060 | 5,38839 | 42,62 | 42,62 |
| 625 | 92,21490 | 39,74296 | 93,16 | 116,70 |

Os valores das duas janelas têm significados distintos. Por exemplo, um máximo posterior a 600 s pertence à fase de drenagem. A média da soma entre faixas não significa uma única fila contínua daquele tamanho. Não comparar demandas e atribuir a diferença aos comportamentos: nesta amostra todos os veículos são do tipo normal.

## 11. Consolidação e verificações para as 630 execuções

Base central: uma linha por `(seed, demand_vehicles, scenario)`, 630 linhas esperadas na coleta integral.

Além das métricas, registrar versão do simulador e do protocolo, caminhos relativos, demanda esperada, número de viagens, proporções efetivamente atribuídas, estado de validação e indicadores de controle. Não substituir pela composição nominal os números efetivamente observados nas rotas.

Saídas auxiliares recomendadas:

- tabela por faixa e janela, incluindo identificação interna/externa e zeros;
- relatório de consistência por execução;
- manifesto do processamento, definições e versões;
- posteriormente, tabela de contrastes pareados.

Valores individuais permanecem recuperáveis nos XML. Se houver exportação por viagem, identificar execução e ID do veículo.

O consolidador deve verificar:

1. Cobertura da matriz esperada, unicidade da chave e coerência com o registro de execuções.
2. XML completos e arquivos obrigatórios. A grade de filas deve ser crescente e completa: 1800 amostras em 0...1799 s. Ausência de uma execução nunca deve virar uma linha normal de métricas zero.
3. IDs únicos e correspondência entre demanda-base, rotas de cenário e `tripinfo.xml`; rotas e partidas iguais dentro de seed × demanda, descontando o atributo de perfil.
4. T_i > 0; viagens completas; `arrival − depart = duration` dentro da precisão; `depart − partida_programada = departDelay` dentro da precisão.
5. N = demanda; sem veículos ativos ou aguardando inserção no final. `running = 0`, isoladamente, não garante atendimento total.
6. Tipos efetivos e quantidades de perfis compatíveis com o atribuidor congelado, que usa arredondamento por maiores restos.
7. Contadores de `stats.xml` e totais finais de `summary.xml`; médias e totais com tolerância baseada nos arredondamentos de cada campo.
8. Faixas de `queues.xml` presentes no snapshot; cobertura espacial fixa; critérios principal e experimental separados.
9. Colisões, teleportes, remoções, frenagens e eventuais diferenças entre logs e contadores. Eventos plausíveis de frenagem não invalidam uma execução.

Por padrão, uma falha estrutural deve interromper a publicação de uma base apresentada como completa e produzir diagnóstico. Não excluir silenciosamente linhas problemáticas. Um modo de amostra pode processar explicitamente só os diretórios disponíveis, deixando registrada a cobertura 3/630; essa base não é a coleta integral.

Percentis: adotar interpolação linear e registrar a convenção. Se armazenado desvio-padrão entre todos os veículos da execução como descrição daquela população, usar divisor N (`ddof=0`). O desvio-padrão entre as 30 seeds será amostral, com divisor 29 (`ddof=1`). Não confundir essas duas dispersões.

## 12. Comparação do efeito das composições

Para cada demanda d, composição c diferente de REF e seed s:

delta_{s,d,c} = Y_{s,d,c} − Y_{s,d,REF}

delta_pct_{s,d,c} = 100 × delta_{s,d,c}/Y_{s,d,REF}

São 30 diferenças pareadas por contraste. Se REF = 0, o percentual é indefinido: conservar a diferença absoluta e marcar o percentual como não aplicável. Não inserir um denominador artificial.

Pergunta central: a composição altera o tempo médio de viagem para a mesma realização de demanda? As demais métricas ajudam a interpretar mecanismos e consequências dentro da simulação: retenção, propagação espacial, entrada, saída e drenagem.

O desenho controla a demanda programada, mas não permite atribuir isoladamente uma diferença a um único parâmetro: os perfis mudam conjuntos de parâmetros. Mesma seed também não implica identidade de todas as sequências aleatórias internas após a evolução do tráfego divergir.

Tempo de viagem e velocidade são matematicamente relacionados pelas distâncias; resultados concordantes não são duas evidências independentes. A extensão das filas também pode refletir espaçamento dos veículos e segmentação da rede, não apenas quantidade de veículos.

Para o TCC, distinguir observação, interpretação e limitação. Conclusões dizem respeito aos perfis parametrizados e à rede simplificada, não automaticamente aos motoristas reais ou ao trânsito real de Videira.

## 13. Estatística ainda não escolhida

Após a base integral ser conferida:

1. Descrever valores por composição/demanda e variabilidade entre seeds: média, desvio-padrão, mediana e intervalo interquartil quando útil.
2. Examinar diferenças pareadas, extremos plausíveis e distribuição relevante para a pergunta inferencial.
3. Estimar magnitude e incerteza do efeito. Se houver bootstrap, reamostrar blocos de seed completos, preservando o pareamento.
4. Definir previamente a família de contrastes e a necessidade de ajuste por multiplicidade. Tempo médio de viagem permanece o desfecho central proposto.
5. Escolher procedimento estatístico e referência pertinente. Não decidir ANOVA ou outro teste só porque há sete cenários. Não escolher um teste apenas pela normalidade separada dos grupos.

A média dos percentuais pareados e o percentual calculado a partir das médias agregadas são diferentes. Indicar qual foi utilizado. Intervalos de confiança descrevem variabilidade sob o modelo/procedimento de simulação, não erro de previsão em relação ao trânsito real.

## 14. Fontes verificadas e registro das alterações

### Material do trabalho

- PTC ajustado após a banca: seções 3.7 e 3.8, consultadas na versão anterior para identificar métricas e comparações previstas.
- Pacote oficial da amostra, manifesto, snapshot e registro: fonte dos dados e da configuração examinada nesta versão.

### Documentação e código primários

- Eclipse SUMO / DLR. *TripInfo*. https://sumo.dlr.de/docs/Simulation/Output/TripInfo.html — campos das viagens. Consulta: 14/10/2026.
- Eclipse SUMO / DLR. *Statistic Output*. https://sumo.dlr.de/docs/Simulation/Output/StatisticOutput.html — campos agregados. Consulta inicial: 09/10/2026.
- Eclipse SUMO / DLR. *Summary*. https://sumo.dlr.de/docs/Simulation/Output/Summary.html — contadores e estatísticas temporais. Consulta inicial: 09/10/2026.
- Eclipse SUMO / DLR. *QueueOutput*. https://sumo.dlr.de/docs/Simulation/Output/QueueOutput.html — documentação geral. Consulta: 14/10/2026. Algumas opções da documentação atual não estão no código da versão 1.27.1, portanto não foram assumidas como opções usadas na coleta.
- Eclipse SUMO. `MSQueueExport.cpp`, tag `v1_27_1`, blob `995bbad79edf7235b9d0407627dc34c1586d8081`. https://github.com/eclipse-sumo/sumo/blob/v1_27_1/src/microsim/output/MSQueueExport.cpp — conferido diretamente para resolver significado das filas, regra de exportação e espera por faixa.
- Eclipse SUMO. `MSDevice_Tripinfo.cpp`, tag `v1_27_1`, blob `dd71a176c57c7fd67c6a967cce6d59e44665d220`. https://github.com/eclipse-sumo/sumo/blob/v1_27_1/src/microsim/devices/MSDevice_Tripinfo.cpp — conferido diretamente para duração, velocidade e espera de viagens.

A documentação e o código sustentam a semântica dos dados. As médias, janelas, contrastes e a prioridade do desfecho são escolhas analíticas explicitadas neste protocolo. A janela de 600 s se apoia no desenho experimental, não em um limite universal da literatura.

López et al. (2018) é referência geral do simulador já presente no arquivo bibliográfico. Não lhe atribuir fórmulas específicas que não foram verificadas. A referência para o procedimento estatístico será selecionada quando esse procedimento for definido.

### Alterações em relação à versão 0.1

- Conferência efetiva da amostra e dos hashes, sem estender a validade aos XML não anexados.
- Identificação do fim fixo em 1800 s e da grade registrada em 1 s.
- Confirmação da média individual de velocidade também utilizada por `stats.xml`.
- Especificação de filas pela implementação da versão 1.27.1, inclusive ambiguidade de `queueing_time`, campo experimental e linhas esparsas.
- Proposta de cobertura completa de faixas externas e internas, com decomposição espacial fixa.
- Preservação da janela principal de 600 s e acréscimo do horizonte integral como complemento obrigatório de extração temporal.
- Definição exata das chegadas pelo `tripinfo`, sem arredondar o corte pelo `summary`.
- Contador `emergencyBraking` como fonte principal de eventos e logs como complemento sem duplicação.

Nenhuma alteração foi motivada por comparação entre composições: a amostra examinada contém somente REF. Os valores apresentados são conferência técnica de extração, não avaliação final do impacto dos comportamentos.
