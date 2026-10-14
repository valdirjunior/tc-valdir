# Interpretação integrada dos resultados - v1.0

Data: 14/10/2026. Nota de análise para o TC de Valdir Rugiski Junior. Destino sugerido no repositório: `docs/interpretacao-integrada-resultados-v1_0.md`.

## Leitura principal

As composições de perfis produziram diferenças no desempenho do tráfego simulado. AGR e MIX_A tiveram menor tempo médio de viagem que REF nas três demandas, com intervalos simultâneos abaixo de zero no procedimento exploratório adotado. CAU teve maior tempo médio nas três. Isso responde à comparação central dentro do modelo, mas não estabelece uma classificação única de desempenho por todas as métricas.

Em particular, menor tempo de viagem não significa necessariamente menor tempo parado ou menor extensão de fila. O tempo de viagem também depende do deslocamento entre paradas e dos parâmetros de velocidade dos perfis. O principal achado conjunto é a existência de resultados diferentes conforme a dimensão observada e o carregamento da rede.

Esta nota interpreta resultados já calculados. Não executa novas simulações, não altera a família de 18 contrastes e não acrescenta testes para as outras métricas. Todas as seeds foram preservadas. O texto final do TCC deve ser preparado no chat de escrita a partir destes registros.

## Como ler os números

Cada número das tabelas é a média das 30 execuções da combinação demanda/composição. Tempo de viagem e tempo parado estão em segundos por viagem. A velocidade é a média das velocidades individuais das viagens, em km/h.

Para filas, soma-se a extensão exportada das faixas em cada instante e depois calcula-se a média nos primeiros 600 s. O resultado é expresso em metros agregados, não como uma fila contínua única ou número de veículos. A cobertura espacial é fixa, com faixas externas e internas.

A vazão representa chegadas nos primeiros 600 s, convertidas para equivalente por hora. Exemplo: a média de 500,57 chegadas em dez minutos em REF/625 corresponde a 3.003,4 veíc./h equivalentes. Ela descreve o escoamento nessa janela, não capacidade máxima ou regime estacionário.

As viagens completas são acompanhadas também depois de 600 s. Assim, o tempo médio inclui viagens que terminam durante a drenagem, enquanto fila e vazão desta tabela usam a janela [0,600). As definições completas permanecem no protocolo de métricas v0.2.

## Composições comparadas

| Cenário | Cautelosos | Normais | Agressivos |
|---|---:|---:|---:|
| REF | 0% | 100% | 0% |
| EQU | 33% | 34% | 33% |
| CAU | 60% | 40% | 0% |
| AGR | 0% | 40% | 60% |
| MIX_C | 60% | 20% | 20% |
| MIX_N | 20% | 60% | 20% |
| MIX_A | 20% | 20% | 60% |

Proporções nominais; as quantidades inteiras efetivas por execução são conferidas pelo consolidador. REF contém somente o perfil normal; os cenários AGR e CAU também contêm normais.

## Médias com 300 veículos

| Cenário | Viagem (s) | Velocidade (km/h) | Parado (s) | Filas (m agregados) | Vazão (veíc./h) |
|---|---:|---:|---:|---:|---:|
| REF | 85,94 | 41,86 | 1,48 | 3,75 | 1542,20 |
| EQU | 87,14 | 41,51 | 1,21 | 3,08 | 1539,80 |
| CAU | 92,09 | 39,18 | 1,39 | 3,58 | 1524,00 |
| AGR | 80,94 | 44,43 | 1,07 | 2,68 | 1556,80 |
| MIX_C | 90,86 | 39,83 | 1,31 | 3,34 | 1526,80 |
| MIX_N | 86,79 | 41,61 | 1,45 | 3,78 | 1539,60 |
| MIX_A | 83,37 | 43,31 | 1,09 | 2,73 | 1548,20 |

## Médias com 450 veículos

| Cenário | Viagem (s) | Velocidade (km/h) | Parado (s) | Filas (m agregados) | Vazão (veíc./h) |
|---|---:|---:|---:|---:|---:|
| REF | 90,77 | 40,00 | 4,18 | 17,46 | 2281,00 |
| EQU | 91,13 | 39,81 | 3,03 | 12,54 | 2284,00 |
| CAU | 97,27 | 37,40 | 4,01 | 16,97 | 2252,60 |
| AGR | 84,54 | 42,78 | 2,93 | 12,07 | 2316,80 |
| MIX_C | 95,53 | 38,05 | 3,43 | 14,39 | 2265,00 |
| MIX_N | 91,20 | 39,87 | 3,60 | 15,02 | 2283,20 |
| MIX_A | 86,88 | 41,67 | 2,54 | 10,35 | 2303,80 |

## Médias com 625 veículos

| Cenário | Viagem (s) | Velocidade (km/h) | Parado (s) | Filas (m agregados) | Vazão (veíc./h) |
|---|---:|---:|---:|---:|---:|
| REF | 108,67 | 36,36 | 15,84 | 103,12 | 3003,40 |
| EQU | 103,69 | 36,64 | 10,34 | 66,43 | 3058,60 |
| CAU | 118,25 | 33,45 | 16,65 | 113,52 | 2928,40 |
| AGR | 94,48 | 39,88 | 9,00 | 58,10 | 3132,40 |
| MIX_C | 110,56 | 34,70 | 12,33 | 80,01 | 3006,40 |
| MIX_N | 105,57 | 36,41 | 12,34 | 79,98 | 3037,60 |
| MIX_A | 96,65 | 38,72 | 8,14 | 51,16 | 3121,00 |


## 1. AGR e MIX_A: padrão favorável de mobilidade, com diferenças entre métricas

AGR e MIX_A apresentam, nas três demandas, médias de tempo de viagem, tempo parado e extensão de filas menores que REF; as médias de velocidade e vazão são maiores. A convergência descritiva torna a interpretação mais consistente do que olhar apenas o tempo de viagem. A evidência inferencial desta entrega, porém, é somente para tempo de viagem.

Na demanda 625, REF teve tempo médio de 108,67 s; AGR, 94,48 s; MIX_A, 96,65 s. As diferenças são -14,19 s e -12,02 s, respectivamente. Os intervalos simultâneos exploratórios são [-18,45; -9,94] e [-18,26; -5,78] s.

AGR teve o menor tempo médio de viagem nas três demandas. MIX_A teve médias menores de tempo parado e filas que AGR em 450 e 625. Em 625:

| Indicador | AGR | MIX_A | Leitura descritiva |
|---|---:|---:|---|
| Tempo médio de viagem | 94,48 s | 96,65 s | AGR completa as viagens em menor tempo médio |
| Tempo parado médio | 9,00 s | 8,14 s | MIX_A acumula menor espera média |
| Soma média das extensões de fila | 58,10 m | 51,16 m | MIX_A tem menor extensão agregada média |
| Vazão de conclusão, 0-600 s | 3.132,4 veíc./h | 3.121,0 veíc./h | AGR tem média um pouco maior de conclusões na janela |

Essas diferenças não ocorrem em todas as seeds. Em 625, MIX_A teve menos espera e menor soma média de filas que AGR em 17 dos 30 pares; nos outros 13 ocorreu o contrário. Seu tempo de viagem foi maior que o de AGR em 24 dos 30 pares. São contagens descritivas, não um novo teste de comparação AGR versus MIX_A.

Ambas as composições têm 60% do perfil agressivo. AGR combina os 40% restantes com normais; MIX_A combina 20% normais e 20% cautelosos. A comparação muda a composição e suas interações; não mede isoladamente um parâmetro ou uma proporção contínua. Não foi demonstrado por estes agregados qual mecanismo espacial explica a diferença de filas.

## 2. CAU: viagem mais demorada nem sempre significa mais tempo parado

Em 300 veículos, CAU teve viagem média de 92,09 s ante 85,94 s de REF, mas tempo parado médio de 1,39 s ante 1,48 s. Em 450, a viagem também foi mais demorada, com espera média ligeiramente menor. Portanto, a diferença de duração não pode ser explicada apenas pelo tempo contabilizado como espera.

O snapshot congelado configura fatores de velocidade distintos para os perfis: 0,90 no cauteloso, 1,00 no normal e 1,10 no agressivo. Também mudam tau, minGap, aceleração e outros parâmetros. Isso oferece uma hipótese de interpretação para diferenças de deslocamento, mas não separa quanto da duração decorre de cada parâmetro. Não atribuir todo o efeito exclusivamente à velocidade desejada ou ao espaçamento.

Em 625, CAU reúne médias de viagem mais demorada, velocidade menor, espera maior, maior extensão de filas e menor vazão que REF. Nessa demanda, as cinco dimensões apontam na mesma direção descritiva. Para o tempo de viagem, a diferença média é +9,58 s, com intervalo simultâneo exploratório [4,39; 14,77] s.

O resultado não classifica prudência real como prejudicial. CAU é uma composição específica de parâmetros no modelo e na rede estudada, não uma medição de motoristas cautelosos reais de Videira.

## 3. MIX_C: o caso que mostra por que uma métrica não substitui as outras

Em 625, MIX_C teve tempo médio de viagem de 110,56 s ante 108,67 s de REF. Ao mesmo tempo, sua espera média foi menor: 12,33 s ante 15,84 s; a soma média das extensões de fila também foi menor: 80,01 m ante 103,12 m.

Assim, uma composição pode ter menor retenção medida por esses indicadores sem apresentar menor duração total da viagem. A diferença temporal de MIX_C foi +1,89 s, com intervalo simultâneo [-3,85; 7,62] s. Esse intervalo não permite afirmar diferença de média temporal pelo procedimento adotado, nem comprova equivalência.

As métricas de fila e espera acima são descritivas. Não lhes atribuir significância estatística com base no intervalo calculado para tempo de viagem. Tampouco chamar a menor extensão de fila de menor quantidade de veículos em fila, pois o comprimento também envolve espaçamento e segmentação da rede.

## 4. EQU e MIX_N: distinguir a média observada da precisão da comparação

EQU e MIX_N tiveram tempos médios um pouco maiores que REF em 300 e 450, e menores em 625. Em 300, seus intervalos de tempo ficam acima de zero. Em 450 e 625, incluem zero no procedimento simultâneo adotado.

Em 625, EQU teve diferença média de -4,98 s, com intervalo [-10,73; 0,78]; MIX_N, -3,10 s, com intervalo [-7,84; 1,63]. As médias favorecem essas composições, mas sua incerteza não permite a mesma conclusão temporal obtida para AGR/MIX_A nesta etapa.

Ainda assim, EQU e MIX_N apresentam médias menores de espera e filas que REF em 625. Esses resultados permanecem relevantes para descrever o funcionamento do cenário, com o cuidado de não trocar uma comparação temporal incerta por uma conclusão inferencial não calculada em outra métrica.

## 5. O carregamento muda o contexto da comparação

Em REF, de 300 para 625 veículos, o tempo médio passa de 85,94 para 108,67 s; o tempo parado, de 1,48 para 15,84 s; a extensão agregada média das filas, de 3,75 para 103,12 m. A fração média de viagens concluídas nos primeiros 600 s cai de 85,68% para 80,09%, embora o número absoluto de chegadas aumente.

Isso mostra a necessidade de separar volume atendido de fluidez: uma demanda maior pode produzir mais chegadas por hora equivalente e, simultaneamente, viagens mais demoradas e mais retenção. Não interpretar o aumento de vazão entre demandas como prova de melhora operacional.

As diferenças médias de tempo de AGR e MIX_A ante REF são maiores, em magnitude, em 625 do que em 300. Esse padrão não vale automaticamente para todas as composições: MIX_C, por exemplo, tem diferença positiva menor em 625. Não foi calculado teste de interação ou intervalo para a diferença entre efeitos de demandas distintas. A observação é descritiva.

## 6. Entrada e drenagem ajudam a conferir a interpretação

O tempo de viagem começa na inserção do veículo na rede. Por isso, a avaliação também acompanha o atraso até conseguir entrar e o tempo de sistema, que é a soma desse atraso com a duração.

| Indicador, demanda 625 | REF | AGR | MIX_A | CAU |
|---|---:|---:|---:|---:|
| Duração média da viagem (s) | 108,67 | 94,48 | 96,65 | 118,25 |
| Atraso médio de inserção (s) | 1,42 | 0,42 | 0,39 | 1,62 |
| Tempo médio de sistema (s) | 110,09 | 94,90 | 97,04 | 119,87 |
| Drenagem após 600 s (s) | 226,17 | 177,76 | 179,58 | 246,48 |

Em AGR e MIX_A, a menor duração vem acompanhada de menor atraso médio de entrada e menor tempo médio de sistema que REF. A drenagem média também é mais curta. Esses complementos mantêm a interpretação temporal observada, dentro do cenário.

Todas as viagens da coleta foram concluídas até o horizonte de 1800 s. O tempo de drenagem acima é calculado pela última chegada menos 600 s em cada execução, e não pelo fim configurado de 1800 s. A vazão do horizonte integral não discrimina composições dentro da mesma demanda, pois todas atendem a mesma quantidade total de viagens; por isso a janela de 600 s é mais informativa para o escoamento durante o carregamento.

## O que está sustentado e o que permanece em aberto

| Afirmação | Situação |
|---|---|
| Composições alteraram o tempo médio no modelo | Sustentada por contrastes temporais com incerteza, nas condições e pressupostos registrados |
| AGR/MIX_A tiveram menor tempo que REF nas três demandas | Estimativas negativas e intervalos simultâneos abaixo de zero nesta etapa exploratória |
| Existe um melhor cenário por todas as dimensões | Os resultados mostram divergências entre indicadores; não foi definido critério único de preferência |
| Menor tempo parado equivale a menor tempo de viagem | Os exemplos de CAU e MIX_C mostram que essa equivalência não vale aqui |
| As diferenças de fila/espera/vazão são estatisticamente confirmadas | Não avaliado inferencialmente nesta entrega; resultados descritivos |
| O efeito foi causado isoladamente por tau, velocidade ou outro parâmetro | Não identificado pelo desenho atual, que modifica conjuntos de parâmetros |
| O local mais congestionado ou a persistência espacial da fila foi identificado | Não por estas estatísticas globais; requer a tabela por faixa e, conforme a pergunta, a série temporal |
| Zero colisões/teleportes comprova segurança | Os contadores registram o comportamento operacional do simulador, não uma avaliação validada de segurança real |
| Direção agressiva deve ser incentivada em vias reais | Não decorre destas comparações de perfis parametrizados |

Não foi criada uma nota única somando indicadores com unidades e prioridades diferentes. A discussão deve apresentar ganhos e perdas por dimensão, com o tempo de viagem como desfecho central.

## Próximo dado necessário

Para avançar da leitura global para a localização das filas, será necessária a tabela `filas_por_faixa.csv`, já gerada pelo consolidador local. Ela permite comparar faixas e decompor resultados espaciais. Métricas resumidas de presença e comprimento não substituem a série temporal quando a pergunta envolve duração de episódios contínuos ou propagação da fila.

Essa etapa pode aproveitar os dados já coletados. Não requer uma nova simulação para começar a análise espacial. A necessidade de outros arquivos será avaliada conforme a cobertura real da tabela.

## Rastreabilidade e reprodução

Fontes: base oficial de 630 execuções; resumo descritivo entregue; 18 intervalos simultâneos entregues; snapshots congelados de perfis e atribuição de composições. Os valores das cinco métricas nas 21 combinações foram conferidos por cálculo independente das médias e reconciliados com a descritiva arquivada.

As comparações AGR versus MIX_A nesta nota são diferenças descritivas pareadas e contagens dos sinais nos mesmos 30 blocos. Não pertencem à família inferencial ante REF. Não foram introduzidas novas hipóteses testadas, exclusões de seeds ou métricas de risco.

Consultar em conjunto:

- `docs/Protocolo_metricas_SUMO_v0_2.md` para definição dos campos e janelas;
- `docs/fundamentacao-avaliacao-v0_1.md` para fontes e limites de aplicação da literatura;
- `docs/protocolo-estatistico-viagem-v1_0.md` para o procedimento e pressupostos;
- `docs/checkpoint-estatistica-viagem-2026-10-14.md` para o estado da etapa estatística;
- `output/analise/baseline_v1_consolidado_v1/base_execucoes.csv` para a base;
- `output/analise/baseline_v1_descritiva_v1/tabelas/` e `output/analise/baseline_v1_estatistica_v1/` para as tabelas de resultados.

Os comandos de testes e reprodução dessas entregas são opcionais para quem apenas consulta os resultados. As verificações já foram executadas na preparação dos pacotes.

### SHA-256 das fontes locais examinadas

- `base_execucoes.csv`: `6494e415f8e37cdbe06c1c68dd7fef6c08f6c52773e461441ffe07b935cd0701`
- `contrastes_viagem_ic_simultaneos.csv`: `8159c8b25d14eb6b1a41dde8c9060f0da988fc35cb6de12aeb3421931d92a7cd`
- `perfis_final.add.xml`: `51215246a7c28bcbf7e71e97646adc4874bab8e9d147890923ba219b6e145eeb`
- `atribuir_perfis.py`: `878b67958d4aa343ad84d952f5c47b6c68f42718dc7a397ec33e371f2e96fc10`
