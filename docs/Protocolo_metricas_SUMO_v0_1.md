# Proposta de protocolo de métricas e comparação — TC / SUMO

Versão 0.1 — 9 de outubro de 2026

**Status:** proposta metodológica anterior à inspeção dos resultados comparativos. Não representa decisões já aprovadas pelo orientador. Não altera a simulação congelada e não contém resultados experimentais.

## 1. Escopo e informações disponíveis

O objetivo é avaliar diferenças no desempenho do tráfego associadas às composições de perfis de motoristas na rede simplificada do entorno da Praça Nereu Ramos, em Videira/SC.

Segundo o registro fornecido pelo pesquisador, a coleta contém 630 execuções: 30 seeds (1000–1029), três demandas (300, 450 e 625 veículos programados entre 0 e 600 s) e sete composições (REF, EQU, CAU, AGR, MIX_C, MIX_N e MIX_A). Cada combinação seed × demanda compartilha a realização de demanda entre as sete composições. Os totais de validação informados não foram rechecados nesta etapa.

Foram consultadas as seções 3.7 e 3.8 do PTC ajustado após a banca e a documentação oficial do SUMO. Os arquivos da coleta `baseline_v1` não estão anexados nesta etapa. A disponibilidade dos campos, a versão utilizada, a resolução temporal e as configurações de saída precisam ser conferidas antes da implementação.

O PTC prevê tempo médio de viagem, velocidade média, tempo parado, formação/comprimento de filas e vazão. Também prevê comparar composições com a mesma demanda e usar REF como referência. As propostas abaixo operacionalizam esse escopo.

## 2. Princípios de análise

- Manter todas as seeds; congestionamento e valores extremos plausíveis fazem parte do experimento.
- Definir a métrica principal e os complementos antes de comparar seus valores entre cenários.
- Não escolher uma fórmula porque produz diferenças maiores ou significância estatística.
- Usar cada execução como unidade de consolidação e cada seed como bloco de comparação dentro de uma demanda.
- Considerar o resultado global da composição. Diferenças entre tipos de veículos dentro de uma execução são análises secundárias, sujeitas à interação entre os veículos e à atribuição dos perfis às rotas.
- Preservar os XML brutos. Não é necessário transformar toda informação disponível em coluna ou tabela do TCC; ela poderá ser extraída depois por uma regra documentada.
- Se houver inconsistência técnica, registrar e investigar, sem excluir silenciosamente uma execução ou inventar seu resultado.

## 3. Notação, população e janelas

Para uma execução:

- N: número de viagens válidas concluídas;
- T_i: `duration` do veículo i, em segundos;
- L_i: `routeLength` do veículo i, em metros;
- W_i: `waitingTime` do veículo i, em segundos;
- D_i: `departDelay` do veículo i, em segundos;
- A_i: `arrival` do veículo i, em segundos;
- H = 600 s: horizonte comum de avaliação durante a programação da demanda;
- q_l(t): comprimento de fila na faixa l no instante t, em metros.

**População de viagens:** todos os veículos esperados na execução, acompanhados até concluírem o percurso, inclusive quando chegam após 600 s. A condição N = demanda esperada deve ser verificada com os IDs e os arquivos de entrada e saída.

**Janela comum para vazão e filas:** propor [0,600). Uma chegada exatamente em 600 s fica fora da contagem dessa janela. A mesma convenção deve valer em todas as execuções. A fase posterior será tratada como drenagem, sem descartar as viagens que terminam nela.

As duas perspectivas são complementares: as métricas de viagem descrevem a experiência completa da coorte gerada; as métricas temporais descrevem o que a rede realizou durante o horizonte comum. Esta é uma avaliação de demanda finita, incluindo o carregamento inicial, e não uma estimativa de regime estacionário. Não propor aquecimento ou recorte de congestionamento após observar os resultados.

## 4. Tempo médio de viagem — desfecho central proposto

**Fonte:** `tripinfo.xml`, atributo `duration`.

T_medio = (Σ_i T_i) / N

**Unidade:** s por viagem. Quanto menor, menor o tempo médio de percurso, sob as mesmas condições experimentais.

O campo mede a duração após a inserção efetiva do veículo. Não incluir `departDelay` nessa métrica. Como complemento essencial à avaliação da demanda, registrar:

D_medio = (Σ_i D_i) / N

Tempo_sistema_medio = (Σ_i (T_i + D_i)) / N

O segundo complemento acompanha o tempo desde a partida programada até a chegada, quando a diferença entre partida programada e efetiva corresponde a `departDelay`. Isso evita que a retenção na entrada fique oculta quando se observa apenas o percurso dentro da rede.

**Campos:** `travel_time_mean_s`, `depart_delay_mean_s`, `system_time_mean_s`.

**Complementos descritivos inicialmente úteis:** mediana e percentil 95 de T_i. O percentil 95 descreve a cauda das viagens; não é um intervalo de confiança.

**Validação:** comparar a média com `vehicleTripStatistics.duration` de `stats.xml`, considerando a população efetivamente incluída e a precisão dos arquivos. Essa é uma checagem cruzada entre saídas do mesmo simulador, não validação independente do modelo de tráfego.

## 5. Velocidade média — distinguir as agregações

### Principal proposta: média das velocidades de viagem por veículo

v_i = L_i / T_i

v_medio_viagens = (Σ_i v_i) / N

**Fonte:** `tripinfo.xml`, `routeLength` e `duration`.

**Unidade:** m/s; apresentação em km/h = 3,6 × m/s.

**Campo:** `trip_speed_mean_mps`.

Cada viagem tem o mesmo peso. O denominador inclui os períodos de retenção durante o percurso. Essa definição responde: qual é a média das velocidades de viagem experimentadas pelos veículos da execução?

### Complemento: razão entre distância total e tempo total

v_agregado = (Σ_i L_i) / (Σ_i T_i)

**Campo:** `aggregate_trip_speed_mps`.

Como L_i = v_i × T_i, essa razão é uma média de v_i ponderada por T_i. As viagens demoradas recebem maior peso. Ela descreve distância percorrida por unidade de tempo acumulado dos veículos, sem confundir esse tempo com a duração de relógio da simulação.

As duas fórmulas são legítimas e podem divergir. Preservá-las com nomes distintos e usar a primeira como principal é uma proposta baseada na interpretação por viagem, não em qual mostrará o melhor resultado. Não atribuir automaticamente à segunda o significado de velocidade espacial de um detector ou segmento.

### Média instantânea da rede

`summary.xml/meanSpeed` representa outra perspectiva: veículos presentes naquele instante. A média desses valores ao longo do tempo depende da ponderação temporal e da quantidade de veículos presentes. Não substituir silenciosamente a velocidade de viagem por essa estatística. Sua utilidade inicial é descrever a evolução temporal da rede.

**Controles:** verificar T_i > 0 e manter comprimentos de percurso e demanda pareados. Conferir a fórmula efetiva de `stats.xml/speed` na versão da coleta antes de usá-lo como validação. Não assumir que corresponde à razão das somas.

## 6. Tempo parado — média por viagem

**Fonte:** `tripinfo.xml`, `waitingTime`.

W_medio = (Σ_i W_i) / N

**Unidade:** s por viagem.

**Campo:** `waiting_time_mean_s`.

Na documentação consultada, `waitingTime` acumula o período com velocidade ≤ 0,1 m/s, excluindo paradas programadas. Portanto, é uma definição operacional de parada ou movimento praticamente nulo; não equivale a todo o tempo em trânsito lento.

Incluir os veículos com W_i = 0 na média. Calcular apenas entre os que pararam mudaria a pergunta e elevaria o valor por construção.

**Complementos propostos:**

- `vehicles_with_waiting_pct` = 100 × quantidade de veículos com W_i > 0 / N;
- `waiting_share_pct` = 100 × Σ_i W_i / Σ_i T_i.

O segundo complemento é a fração do tempo acumulado das viagens que se enquadra no critério de parada. Não é a média dos percentuais individuais W_i/T_i; essa outra agregação daria pesos diferentes.

Não confundir `waitingTime` com `stopTime`, `departDelay` ou o atributo `waiting` de `summary.xml`.

## 7. Filas — extensão e persistência, com conferência técnica pendente

**Fonte prevista:** `queues.xml`, saída de filas do SUMO.

O comprimento registrado é uma extensão medida a partir do cruzamento até o último veículo considerado na fila. Não corresponde à soma dos comprimentos dos veículos nem pode ser convertido em quantidade de veículos dividindo-o por um comprimento médio.

### Pendência anterior à decisão definitiva

Inspecionar a versão do SUMO, os atributos presentes, o período de saída, as opções de agregação e o critério de fila usado na coleta. A documentação atual distingue `queueing_length` e `queueing_length_experimental` e apresenta opções de limiar de velocidade e omissão de registros vazios. Não transportar automaticamente o limiar de `waitingTime` para o campo de fila.

**Proposta inicial:** utilizar `queueing_length` como medida principal, se os arquivos confirmarem seu significado e formato na versão utilizada. Se o campo experimental estiver disponível, guardá-lo com identificação própria para complemento, sem trocar o principal ao observar os resultados.

### Conjunto fixo de faixas

Definir L faixas externas elegíveis da rede congelada, permitidas aos veículos do experimento, com regra baseada na geometria e permissões. Guardar a lista. Não usar apenas as faixas que aparecem com fila em cada execução como denominador.

Se forem selecionadas aproximações específicas, estabelecer a seleção com base na rede e no objetivo do estudo, antes de olhar qual cenário apresentou filas maiores. A opção de cobertura ampla é manter todas as faixas externas elegíveis e gerar também dados por faixa.

### Principais medidas propostas para [0,600)

1. **Extensão agregada média das filas**

Q_soma(t) = Σ_l q_l(t)

Q_medio = (1/H) × integral de 0 a H de Q_soma(t) dt

**Campo:** `queue_total_mean_m_0_600`.

É a média temporal da soma das extensões nas faixas monitoradas. Unidade: m somados entre faixas. Não descrever como uma única fila contínua na cidade. Opcionalmente dividir Q_medio por L e chamar de comprimento médio por faixa, preservando o mesmo denominador entre execuções.

2. **Maior extensão de fila observada em uma faixa**

q_max = max_{l,t em [0,H)} q_l(t)

**Campo:** `queue_lane_max_m_0_600`.

Guardar a faixa e o instante correspondentes. Esse máximo é diferente do máximo temporal da soma Q_soma(t).

3. **Persistência das filas por faixa**

P_l = 100/H × integral de 0 a H de indicador(q_l(t) > 0) dt

**Campo por faixa:** `queue_presence_pct_0_600`.

Permite distinguir uma fila extensa e episódica de retenção persistente. Para uma síntese da rede, é possível usar a média de P_l nas L faixas fixas; ela significa a proporção de observações faixa × tempo com fila, não a porcentagem de veículos em fila.

### Integração e registros vazios

Com amostras regulares que representem intervalos equivalentes, a integral pode ser estimada por soma dos valores multiplicados pelo passo temporal. Quando os intervalos variam, usar pesos temporais e registrar a convenção da estimativa. Se a saída for instantânea e espaçada, declarar que a integral é aproximada e que picos entre amostras podem não ser observados.

Incluir os períodos sem fila como zero somente quando o formato e as opções de saída confirmarem que a ausência significa ausência de fila. Não preencher um arquivo truncado ou uma lacuna desconhecida com zero. Uma média apenas dos registros positivos responde outra pergunta e tende a superestimar a média temporal completa.

Para estudar pontos de retenção previstos no PTC, gerar uma tabela auxiliar por seed × demanda × cenário × faixa. A base central continua com uma linha por execução.

**Complemento da drenagem:** preservar a evolução após 600 s e, se útil, integrar a carga de filas nessa fase. Não comparar médias calculadas em horizontes de duração variável como se tivessem a mesma exposição temporal.

## 8. Vazão — conclusões no horizonte comum

C_H = quantidade de viagens com 0 ≤ A_i < 600

F_H = C_H / 600 × 3600 = 6 × C_H

**Fonte primária:** `tripinfo.xml`, `arrival` e ID da viagem.

**Unidade:** veículos/h, taxa equivalente para a janela de dez minutos.

**Campos:** `completed_count_0_600`, `completion_flow_vph_0_600`.

É uma taxa de conclusão de viagens da rede, não fluxo num detector, não volume programado de entrada e não capacidade máxima da rede. A taxa nominal de geração seria demanda/600 × 3600; não deve ser apresentada como resultado de vazão de saída.

**Complemento:** `completed_share_pct_0_600` = 100 × C_H / demanda esperada. Indica a parcela da demanda que concluiu no horizonte comum.

Contar apenas o total final N não discrimina cenários se todos concluem. Dividir N pelo término variável da execução mistura conclusão e duração da drenagem; se calculado, deve ter nome e interpretação próprios, sem substituir F_H.

Não usar automaticamente `summary.xml/ended` como chegadas: a documentação inclui nesse contador veículos removidos por outras causas. Usar `arrived`, quando disponível, para checagem cruzada, respeitando a convenção temporal do arquivo.

## 9. Complementos selecionados

| Complemento | Cálculo / unidade | Finalidade e cuidado |
|---|---|---|
| Atraso médio de inserção | média de D_i, s | Retenção antes da entrada na rede |
| Tempo médio desde partida programada | média de T_i + D_i, s | Experiência completa da demanda |
| Tempo perdido (`timeLoss`) | média do campo, s | Tempo abaixo da velocidade ideal individual; interpretar junto aos perfis |
| Tempo de drenagem da coorte | max(0, max_i A_i − 600), s | Tempo após o horizonte de geração até a última chegada; exigir que toda a demanda conclua |
| Frenagens de emergência | eventos e 1000 × eventos/N | Eventos por mil viagens; não são probabilidade de acidente |
| Viagens com frenagem registrada | IDs únicos / N, se identificáveis | Distinguir quantidade de eventos de quantidade de veículos afetados |
| Comprimento médio de percurso | média de L_i, m | Controle da comparabilidade das viagens |
| Teleportes, remoções, colisões, veículos pendentes | contagens | Controle de integridade e interpretação |

O SUMO define `timeLoss` em relação a uma velocidade ideal que incorpora `speedFactor`. Se esse parâmetro varia entre perfis, o referencial também varia; uma comparação direta desse campo não mede exclusivamente atraso de congestionamento relativo a uma velocidade comum. Não somar `waitingTime` a `timeLoss` como se fossem perdas disjuntas.

Para frenagens, conferir se a versão registra `safety.emergencyBraking`; na ausência desse campo, interpretar as mensagens específicas nos logs, verificando completude e deduplicação entre arquivos. Não tratar `emergencyStops` como sinônimo automático e não somar o mesmo aviso de `warnings.log` e `sumo.log` duas vezes. Os 120 eventos mencionados pelo pesquisador são um total da coleta, não um resultado por composição.

A ausência de colisões registradas limita-se às condições e critérios de detecção da simulação. Os indicadores complementares de frenagem não sustentam, por si, conclusões sobre segurança viária real.

## 10. Estrutura da consolidação

**Base central:** 630 linhas esperadas, chave única `(seed, demand_vehicles, scenario)`.

Registrar identificação, versão do simulador/protocolo, caminhos relativos dos arquivos, contagens de controle e métricas definidas. Propor nomes explícitos com unidade e janela, como os apresentados acima.

**Tabelas auxiliares, quando necessárias:**

- viagens: chave da execução + ID do veículo, tipo, duração, distância, espera, atraso e chegada;
- filas por faixa: chave da execução + faixa, média, máximo, persistência e janela;
- eventos: chave da execução + veículo, instante e tipo de evento;
- resultados pareados: seed + demanda + cenário comparado + métrica + REF + diferença.

Não é obrigatório exportar todas essas tabelas de imediato. Os arquivos brutos continuam sendo a fonte. Separar tabelas auxiliares evita comprimir trajetórias e dados por faixa em uma linha artificialmente extensa.

**Desvio-padrão:** se armazenado entre todos os veículos de uma execução como descrição da população daquela execução, adotar divisor N (`ddof=0`) e explicitar isso. Entre as 30 seeds, usar desvio-padrão amostral com divisor 29 (`ddof=1`). São variações distintas.

**Percentis:** propor interpolação linear explicitamente registrada na implementação. Não confundir quantis entre veículos com quantis entre médias de execuções.

## 11. Como associar as métricas ao efeito das composições

Para cada demanda d, cenário c diferente de REF e seed s:

delta_{s,d,c} = Y_{s,d,c} − Y_{s,d,REF}

percentual_{s,d,c} = 100 × delta_{s,d,c} / Y_{s,d,REF}

Comparar a distribuição das 30 diferenças pareadas, mantendo o mesmo nível de demanda. Se REF = 0, o percentual é indefinido; guardar a diferença absoluta e marcar o percentual como não aplicável, sem inserir uma constante artificial no denominador.

**Pergunta central:** a mudança de composição altera o tempo médio de viagem para a mesma demanda?

**Perguntas explicativas:** a diferença acompanha mudanças no tempo parado, na velocidade de viagem, nas filas, no atraso de inserção ou nas conclusões até 600 s? As métricas devem ser interpretadas em conjunto, sem exigir que todas melhorem simultaneamente.

Velocidade e tempo de viagem são relacionados pelas distâncias percorridas; concordância entre ambos não representa duas evidências independentes. Filas em metros também podem refletir espaçamentos e comprimento das faixas, além de quantidade de veículos retidos. Uma diferença global entre composições não identifica isoladamente qual parâmetro comportamental a provocou.

O desenho sustenta atribuição ao conjunto de perfis parametrizados sob as condições controladas e conferidas da simulação. Não permite extrapolar automaticamente para motoristas reais ou para o tráfego real de Videira.

## 12. Estatística: sequência proposta, sem teste escolhido

1. Verificar a base e o pareamento, antes de calcular testes.
2. Descrever cada cenário/demanda com média, desvio-padrão entre seeds, mediana e amplitude ou intervalo interquartil quando útil.
3. Examinar gráficos dos valores por seed e das diferenças pareadas; verificar assimetrias e extremos plausíveis.
4. Estimar diferenças médias ou medianas pareadas e sua incerteza. Se houver bootstrap, reamostrar os blocos de seed completos, preservando as correspondências entre cenários.
5. Definir a família de comparações e a necessidade de correção por multiplicidade antes de testes confirmatórios. Proposta inicial: desfecho central = tempo médio de viagem; demais métricas explicam e complementam.
6. Escolher testes conforme a pergunta e a distribuição relevante. Para procedimentos pareados, avaliar as diferenças ou resíduos do modelo apropriado; não escolher um teste apenas pela normalidade de cada grupo isoladamente.

Não considerar cada veículo uma repetição independente do efeito da composição. Não tratar as 630 linhas como observações independentes sem respeitar o bloqueio por seed/demanda. Caso se adote um modelo conjunto entre demandas, considerar como as seeds e as realizações de demanda foram geradas entre esses níveis.

A média dos percentuais por seed e o percentual calculado a partir das médias agregadas são resumos diferentes. Apresentá-los com identificação explícita. Intervalos de confiança refletem a variabilidade das realizações simuladas sob o modelo e o procedimento adotado; não medem o erro em relação ao trânsito real.

## 13. Verificações antes de congelar a versão 1.0

- Manifesto, snapshot e versão do SUMO, inclusive opções de precisão, passo temporal, parada e fim.
- Lista de viagens esperadas e programações/rotas correspondentes entre composições da mesma seed/demanda.
- Contagem e IDs únicos em `tripinfo.xml`; chegadas válidas; ausência de viagens pendentes, remoções inesperadas e duplicatas.
- `running = 0` e `waiting = 0` no final. Ausência de veículos ativos, isoladamente, não garante que todos tenham sido inseridos.
- Correspondência das médias de viagem com `stats.xml`, tolerâncias baseadas na precisão real dos campos.
- Semântica e cobertura de `queues.xml`; presença ou omissão dos zeros; conjunto fixo de faixas; estimativa temporal.
- Fonte dos eventos de frenagem, deduplicação e eventual correspondência com o contador estatístico.

Inspeções técnicas podem ajustar a operacionalização por disponibilidade ou semântica, mas não por diferenças entre cenários. Registrar toda alteração e sua razão. Com esses pontos resolvidos, a proposta pode tornar-se protocolo 1.0 para o script separado de consolidação.

## 14. Fontes e papel de cada uma

**Texto-base:** PTC de Valdir ajustado após a banca, seções 3.7 e 3.8. Consultado na cópia fornecida. Fundamenta quais métricas e comparações foram previstas, sem impor todas as fórmulas de agregação.

**Documentação oficial, consultada em 09/10/2026:**

1. Eclipse SUMO / DLR. *TripInfo*. https://sumo.dlr.de/docs/Simulation/Output/TripInfo.html — definição dos campos de viagem, espera, atraso e perda de tempo.
2. Eclipse SUMO / DLR. *Statistic Output*. https://sumo.dlr.de/docs/Simulation/Output/StatisticOutput.html — estatísticas agregadas e atenção à demanda não atendida.
3. Eclipse SUMO / DLR. *Summary*. https://sumo.dlr.de/docs/Simulation/Output/Summary.html — contadores e velocidade instantânea.
4. Eclipse SUMO / DLR. *QueueOutput*. https://sumo.dlr.de/docs/Simulation/Output/QueueOutput.html — campos de fila e opções temporais/de saída, sujeitos à conferência com a versão usada.
5. Eclipse SUMO / DLR. *Safety*. https://sumo.dlr.de/docs/Simulation/Safety.html — critérios de colisão e limites dos indicadores de segurança.

A documentação sustenta o significado do dado fornecido pelo simulador. As médias, razões, janelas e contrastes deste protocolo são operações e escolhas analíticas explicitadas aqui; não atribuir à documentação uma recomendação de desenho que ela não faz. A escolha de 600 s se apoia no horizonte experimental informado, não em um limiar universal da literatura.

O artigo de López et al. (2018), já presente no arquivo bibliográfico fornecido, é uma referência geral do simulador, não foi utilizado aqui para atribuir fórmulas específicas. A vinculação de artigos empíricos às escolhas de análise e a referência do eventual procedimento inferencial permanecem para revisão bibliográfica dirigida. Não há necessidade de uma citação para cada soma aritmética, mas conceitos especializados e métodos inferenciais devem ter fontes pertinentes.
