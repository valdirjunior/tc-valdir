# Fundamentação da avaliação dos resultados - versão 0.1

Data: 14/10/2026. Documento de trabalho para o TC de Valdir Rugiski Junior. Complementa `checkpoint-analise-2026-10-14.md` e `Protocolo_metricas_SUMO_v0_2.md`. Não substitui o PTC aprovado nem constitui redação final do TCC.

## 1. Resultado desta etapa

A avaliação pode ser organizada em torno da magnitude das diferenças de tempo médio de viagem, sua variabilidade entre seeds e sua interpretação conjunta com velocidade, tempo parado, filas e vazão. A sustentação bibliográfica precisa distinguir quatro questões: pertinência das métricas, semântica dos campos do simulador, desenho das comparações e procedimento estatístico.

Esta etapa verificou os trechos pertinentes do PTC e de oito artigos anexados, além de fontes metodológicas externas. Não foi uma revisão sistemática ou leitura integral de todos os PDFs. As escolhas analíticas abaixo foram registradas após a análise descritiva; não apresentá-las como pré-registro ou decisões previamente aprovadas pelo orientador.

## 2. O que já estava previsto no PTC

Na cópia `PTC - Valdir - ajustado banca.pdf`:

| Localização | Previsão | Consequência para a avaliação atual |
|---|---|---|
| PDF p. 33; página impressa 32; seção 3.6 | Comparar composições mantendo o fluxo e fluxos mantendo a composição; três níveis de carregamento | Organizar resultados por demanda e composição, preservando os fatores controlados |
| PDF p. 34; impressa 33; seção 3.7 | Tempo médio de viagem, velocidade média, tempo parado, filas e vazão | Preservar essas cinco dimensões; identificar claramente qualquer complemento |
| PDF pp. 34-35; impressas 33-34; seção 3.8 | REF como base para parte das comparações; múltiplas seeds; consolidação e avaliação posterior da necessidade de estatística adicional | O pareamento e os procedimentos atuais devem ser descritos como o que foi efetivamente executado |
| PDF pp. 35-36; impressas 34-35; seção 3.9 | Cenário simplificado e comparação entre simulações | Não transformar a análise em previsão calibrada do trânsito real |

O PTC não fixa BCa, 100.000 reamostragens, uma família de 18 intervalos ou um teste específico. A priorização do tempo médio de viagem foi reafirmada pelo pesquisador na etapa de análise. Esses detalhes precisam ter seu próprio registro metodológico.

## 3. Matriz de evidências dos artigos anexados

As páginas abaixo são posições no PDF, contando a capa como p. 1. As chaves são as do `.bib` recebido. Cada linha identifica também o limite do uso da referência.

| Fonte e localização examinada | Evidência pertinente | Uso nesta avaliação | O que a fonte não valida automaticamente |
|---|---|---|---|
| `lopez_2018`, PDF pp. 1-2, 6-7; DOI 10.1109/ITSC.2018.8569938 | Descreve o SUMO, saídas para processamento e integração; discute calibração/validação | Contextualizar a ferramenta e a automação | Fórmulas exatas dos campos da versão 1.27.1, nossas janelas e a escolha do bootstrap |
| `mecheva_2022`, PDF pp. 5-6, 10; DOI 10.3390/s22249801 | Usa SUMO/Python, dados de detectores e exploração de modelos/parâmetros de seguimento | Sustentar que parâmetros comportamentais e processamento automatizado são objetos de pesquisa | Que nossos valores de perfil foram empiricamente calibrados ou que os valores do artigo podem ser transplantados sem considerar rede, dados e versão |
| `makridis_2023`, PDF pp. 4, 8, 10, 12; DOI 10.1080/21680566.2022.2125458 | Distingue heterogeneidade entre e dentro de motoristas; desenvolve caracterização que considera velocidade e dinâmica do veículo | Fundamentar a cautela ao interpretar perfis como conjuntos de parâmetros e usar dispersão como descrição | Que um parâmetro isolado mede agressividade universalmente; sua normalização não foi implementada neste TC |
| `andrade_2024`, PDF pp. 1-3; DOI 10.5753/ssv.2024.32626 | O experimento é em Euro Truck Simulator 2, com telemetria, condução cautelosa/agressiva e análise de área de radar | Discussão de obtenção e caracterização de comportamento em ambiente simulado | Uso experimental de SUMO por esses autores, parâmetros Krauss ou fórmulas das cinco métricas do TC; SUMO aparece nos trabalhos relacionados do artigo |
| `park_2019`, PDF pp. 3, 6, 8-10; DOI 10.1016/j.trf.2019.05.017 | Combina simuladores de condução e VISSIM em rodovia; representa seguir de perto, mudança abrupta de faixa e desaceleração súbita; avalia risco e velocidade | Comparar cuidadosamente a definição de agressividade e distinguir mobilidade de segurança | Que sua redução de velocidade contradiz automaticamente nosso menor tempo de viagem; nem que sua ANOVA/HSD é apropriada para nossos blocos pareados |
| `zhai_2021`, PDF pp. 1-2, 5, 12; DOI 10.1088/1674-1056/abf7ae | Propõe modelo heterogêneo de seguimento; analisa estabilidade conforme a participação de motoristas tímidos/agressivos | Discussão de efeitos coletivos condicionados ao modelo e à composição | Igualdade entre estabilidade de fluxo e tempo médio de viagem; nem transferência direta de parâmetros para Krauss/SUMO |
| `balakrishna_2007`, PDF pp. 2-5; DOI 10.3141/1999-21 | Trata calibração de oferta e demanda a partir de medições; explicita componentes e ruído de simulação | Distinguir comparação controlada de validação empírica | Que coerência interna, ausência de erros ou repetição de seeds comprova aderência ao trânsito de Videira |
| `cobos_2020`, PDF pp. 1-2, 5-6, 8; DOI 10.1109/ACCESS.2020.2999081 | Calibração multiobjetivo com contagens/velocidades e comparação de algoritmos | Contextualizar compromissos entre indicadores e delimitar calibração | Uma nota ponderada de desempenho para nosso TC; seus testes com algoritmos não justificam automaticamente testes sobre nossos cenários |

As duas cópias de `makridis_2023` têm hashes binários diferentes, mas o texto extraído normalizado coincide página a página. São uma única obra bibliográfica, não duas evidências independentes. Os arquivos originais foram preservados.

Não foi realizada aqui uma auditoria da origem de cada valor numérico dos perfis congelados. A pertinência conceitual de uma fonte não é prova de que ela justifica todos esses números.

## 4. Fontes adicionais para desenho e incerteza

### Repetições e comparação de alternativas

O guia FHWA de 2019, capítulo 6, orienta avaliar a variabilidade entre seeds e o número de repetições com base na precisão. Ele também recomenda investigar instabilidade quando a dispersão exige muitas repetições. Sua orientação não é uma regra de que 30 execuções sejam sempre suficientes, nem motivo para excluir uma seed extrema.

Fonte: *Traffic Analysis Toolbox Volume III*, publicação FHWA-HOP-18-036, abril de 2019, capítulo 6, seções “Determine Required Number of Replications” e “Example Problem: Alternative Analysis”.

https://ops.fhwa.dot.gov/publications/fhwahop18036/chapter6.htm

O guia FHWA de 2004, seção 6.6.1, menciona o uso da mesma seed para reduzir variação entre alternativas. A seção 6.5.2 alerta para congestionamento além dos limites espaciais/temporais, inclusive veículos impedidos de entrar. Isso fundamenta acompanhar atendimento da demanda e atraso de inserção. A aplicação ao nosso pareamento e às viagens completas é uma adaptação ao desenho do TC.

https://ops.fhwa.dot.gov/trafficanalysistools/tat_vol3/sect6.htm

### BCa: base científica e implementação

DiCiccio e Efron (1996), seção 2, pp. 191-193, apresentam intervalos BCa a partir de quantis ajustados da distribuição bootstrap, com correção de viés e aceleração. Essa é uma base científica para a classe de intervalos usada. A teoria assintótica não garante cobertura exata para as nossas 30 seeds, e o artigo não determina a quantidade de reamostragens adotada no TC.

Referência: DiCiccio, T. J.; Efron, B. *Bootstrap Confidence Intervals*. Statistical Science, 11(3), 189-228, 1996. DOI: 10.1214/ss/1032280214. O PDF inclui discussão; a leitura pertinente foi nas pp. 189-193, não uma verificação integral das demonstrações.

Cópia do artigo consultada em servidor universitário:
https://www.math.wustl.edu/~kuffner/AlastairYoung/LeeYoung1996b.pdf

A documentação do SciPy 1.17.0 especifica BCa, o eixo de reamostragem e o uso de índices comuns para amostras pareadas. É a referência da implementação, distinta da fundamentação científica. Neste TC, a matriz já contém diferenças pareadas e é reamostrada pela dimensão das seeds.

https://docs.scipy.org/doc/scipy-1.17.0/reference/generated/scipy.stats.bootstrap.html

Todas essas páginas foram consultadas em 14/10/2026. Não atribuir ao guia FHWA o método BCa, nem ao SciPy a decisão de priorizar tempo de viagem.

## 5. Definições e origem dos cálculos

O protocolo v0.2 já registra documentação e código do SUMO na tag `v1_27_1`. A implementação de extração, seus manifestos e as conferências da base são as referências técnicas dos cálculos. Os artigos acima sustentam a pertinência da avaliação, não substituem essa semântica.

Para seed s, demanda d, composição c e N viagens completas:

| Dimensão | Cálculo por execução | Campo/fonte técnica | Interpretação e limite |
|---|---|---|---|
| Tempo médio de viagem | `Y = sum(duration_i) / N` | `tripinfo.duration`; `MSDevice_Tripinfo.cpp` v1.27.1 | Tempo desde a inserção até a chegada; excluir `departDelay` deste indicador, mas examiná-lo separadamente |
| Velocidade média de viagem | `3.6 * sum(routeLength_i / duration_i) / N` | `tripinfo.routeLength`, `duration`; conferência com `stats.xml` | Média das velocidades individuais em km/h; não confundir com razão das somas |
| Tempo parado médio | `sum(waitingTime_i) / N` | `tripinfo.waitingTime`; acumulador do SUMO | Incluir zeros; respeitar critério do simulador e não chamar todo trânsito lento de parada |
| Filas | Média no tempo da soma dos comprimentos exportados nas 198 faixas fixas, com decomposição internas/externas | `queues.xml`, `MSQueueExport.cpp` v1.27.1 | Metros agregados de extensão; não é uma fila contínua única nem número de veículos |
| Vazão de conclusão | `3600 * count(0 <= arrival_i < 600) / 600` | `tripinfo.arrival` | Viagens concluídas por hora equivalente na janela; não é capacidade máxima nem fluxo estacionário |

As janelas [0,600) e [0,1800) são escolhas ligadas ao desenho experimental. O período completo de viagens inclui a drenagem posterior a 600 s. O protocolo documenta linhas esparsas de fila, zeros válidos e a distinção entre campos principal/experimental.

Para comparar composições na mesma demanda:

`delta_s,d,c = Y_s,d,c - Y_s,d,REF`

`efeito_medio_d,c = sum(delta_s,d,c) / 30`

Para o desfecho temporal, valores negativos indicam menor tempo médio que REF. A unidade observacional da comparação é a execução; a unidade de reamostragem é o bloco de seed, com correspondências preservadas. Não usar todos os veículos de todas as execuções como se fossem milhares de repetições independentes do efeito da composição.

As diferenças são dadas primeiro em segundos. A média dos percentuais calculados par a par e o percentual entre médias agregadas são estimandos diferentes; os dois já estão identificados na análise descritiva. Não escolher a apresentação conforme o percentual mais favorável.

## 6. Proposta operacional para a avaliação acadêmica

**Proposta desta etapa; ainda sem aprovação metodológica do orientador:**

1. Manter tempo médio de viagem como desfecho central e seis contrastes ante REF em cada uma das três demandas. São 18 contrastes, não todos os 21 pares possíveis de composições por demanda.
2. Apresentar médias/DP entre seeds, medianas/IQR quando úteis, 30 diferenças pareadas por contraste e magnitude absoluta do efeito.
3. Manter os IC95% BCa marginais v0.1 como estimativas exploratórias de incerteza. Registrar n=30, B=100.000, seed da análise, pareamento, versões e conferência Monte Carlo. O número B não aumenta o número de repetições experimentais.
4. Usar as outras quatro métricas previstas no PTC para interpretar fluidez, retenção e escoamento, inicialmente de forma descritiva. Apresentar seus resultados mesmo quando o sentido difere do tempo de viagem.
5. Usar atraso de inserção/tempo de sistema, drenagem e registros operacionais para avaliar limitações e coerência. Zero colisões ou teleportes não demonstra segurança real. Frenagem de emergência não deve ser chamada automaticamente de acidente ou risco quantificado.
6. Se forem realizadas declarações de significância ou uma conclusão inferencial conjunta dos 18 contrastes, definir a família e o procedimento de controle de multiplicidade antes dessa nova etapa. Não tratar os ICs marginais como simultâneos.

Uma avaliação baseada em magnitude e incerteza pode responder à pergunta do trabalho sem tornar p-valores o centro da discussão. A decisão de realizar testes ainda precisa ser explicitada. O método final deve corresponder ao estimando escolhido: média de diferenças, mediana ou distribuição não são a mesma pergunta.

Não escolher uma ANOVA só pelo número de composições. Tampouco adotar Wilcoxon ou Friedman porque aparecem em um artigo relacionado: esses procedimentos não se tornam testes de diferença de médias automaticamente. Não usar um teste de normalidade como seletor automático de método; examinar especialmente as diferenças pareadas e o desenho.

## 7. Precisão, horizonte e interpretação

**Precisão com 30 seeds.** O número congelado permite descrever a incerteza obtida, mas sua suficiência depende da precisão desejada. Ainda não foi fixada uma diferença mínima de interesse ou tolerância de erro com justificativa externa. Não inventar um limiar retrospectivo para declarar que a amostra “tem poder suficiente”. Extremos plausíveis permanecem na análise; avaliar sua influência e origem é diferente de excluí-los.

**Início e drenagem.** O experimento é de demanda finita, com partidas programadas em 600 s e acompanhamento até 1800 s. A análise inclui o carregamento e a drenagem. Não apresentar as médias como estimativas de regime estacionário nem excluir um aquecimento depois de observar os resultados. Uma análise em outra janela seria uma pergunta adicional, registrada separadamente.

**Atraso de inserção.** Um cenário pode ter bons tempos após inserção e ainda atrasar a entrada de veículos. Comparar `duration`, `departDelay` e sua soma ajuda a verificar isso. O atendimento integral até o horizonte é necessário para evitar comparar apenas subconjuntos selecionados de viagens concluídas.

**Composição versus parâmetro isolado.** A mudança entre cenários modifica conjuntos de parâmetros e quantidades de perfis. O efeito estimado é dessa composição na rede e demanda fixadas; não é efeito isolado de tau, minGap, velocidade desejada ou aceleração.

**Mobilidade e segurança.** O resultado temporal de AGR/MIX_A não autoriza recomendar agressividade real. O rótulo do perfil não reproduz automaticamente as manobras ou mecanismos estudados por Park et al. Mesmo Zhai et al., que encontra efeitos estabilizadores em seu modelo, usa outro desfecho e outra estrutura. Confrontar definições e condições vem antes de classificar um achado como concordante ou contraditório.

**Efeito conforme a demanda.** O PTC prevê examinar mudanças conforme o carregamento. Para uma comparação quantitativa adicional, a pergunta pode ser formulada como `delta_s,625,c - delta_s,300,c`, preservando o bloco. Isso seria um contraste novo, não calculado nesta nota, e precisa entrar no escopo da eventual inferência. Não confundir aumento de tempo entre demandas com efeito exclusivo do comportamento.

## 8. Decisões fechadas e pendências

| Questão | Estado atual |
|---|---|
| Experimento e seeds | Congelados; preservar as 630 execuções e todas as 30 seeds |
| Semântica/extração das métricas | Protocolo v0.2 e consolidador v1.0 já publicados |
| Descritiva e pares | Calculados e versionados |
| BCa marginal do tempo de viagem | Calculado e versionado como exploratório |
| Fundamentação científica do BCa | Fonte adicional consultada nesta nota; resultados não recalculados |
| Hierarquia de desfechos | Tempo de viagem central; cinco dimensões do PTC preservadas; proposta registrada |
| Testes e multiplicidade | Não fechados; não declarar confirmação conjunta |
| Limiar de relevância prática/poder | Não definido; não inventar a posteriori |
| Origem de cada número dos perfis | Fora desta auditoria; verificar documentação de configuração se isso for exigido na escrita |
| Análise espacial de filas | Depende da tabela por faixa; os máximos globais não demonstram persistência em um local |
| Escrita final | Será feita no chat de escrita, usando o PTC aprovado e os resultados/limites registrados |

## 9. Arquivos e continuidade

As oito obras anexadas já constam do `.bib` recebido. `referencias-metodos-analise.bib` fornece apenas entradas adicionais para as fontes metodológicas consultadas; conferir a integração ao arquivo bibliográfico canônico no chat de escrita. Não renomear chaves existentes nem substituir a bibliografia original.

Esta entrega é apenas documentação. Não muda os scripts, a simulação ou os resultados anteriores. Seu manifesto registra hashes dos PDFs/BibTeX usados e dos novos arquivos. A identificação dos anexos serve à rastreabilidade; esta nota não pressupõe que todos os PDFs estejam publicados no GitHub.
