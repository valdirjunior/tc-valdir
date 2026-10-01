# Checkpoint — Preparação do cenário e definição preliminar da demanda

**Data:** 01/10/2026  
**Projeto:** TC — Análise do impacto de comportamentos de motoristas no tráfego urbano por meio de simulação computacional  
**Ferramenta:** Eclipse SUMO 1.27.1  
**Cenário:** entorno da Praça Nereu Ramos, Videira/SC

## 1. Objetivo deste checkpoint

Este documento registra o estado atual da preparação do cenário de simulação antes
da definição definitiva dos perfis de motoristas e da execução dos experimentos oficiais.

O objetivo desta etapa não é reproduzir com exatidão o trânsito real de Videira, mas
construir uma rede funcional e uma distribuição de demanda plausível, capaz de produzir
interações, filas e gargalos adequados para a posterior comparação dos diferentes perfis
de motoristas.

---

## 2. Construção e preparação da rede

A rede foi construída a partir de dados do OpenStreetMap e convertida para o formato
do SUMO com o `netconvert`.

Arquivo principal atual:

`config/nereu_ramos.net.xml`

Após a importação, a rede foi ajustada manualmente no NetEdit.

Entre os principais ajustes realizados estão:

- recorte da rede para a região de interesse;
- remoção de trechos externos desnecessários;
- correção de sentidos de circulação;
- correção de conexões entre lanes;
- bloqueio de retornos inadequados;
- reconstrução de trechos cuja geometria ou circulação não representava adequadamente
  a situação observada;
- ajustes na circulação ao redor da Praça Nereu Ramos;
- tratamento do trecho de convergência de duas faixas para uma;
- revisão das prioridades das conexões;
- ajuste das velocidades das vias.

As velocidades utilizadas atualmente ficaram concentradas em:

- 40 km/h na região central;
- 50 km/h em vias externas/principais compatíveis com esse limite.

A representação é propositalmente simplificada e não busca funcionar como um gêmeo
digital exato do trânsito da região.

---

## 3. Validação preliminar da rede

Foram realizados diversos testes preliminares com `randomTrips.py` para verificar:

- continuidade das rotas;
- funcionamento das entradas e saídas;
- conexões entre vias;
- comportamento em cruzamentos;
- mudanças de faixa;
- formação de filas;
- ocorrência de teleports;
- colisões;
- frenagens de emergência.

Testes antigos com demanda totalmente aleatória mostraram que determinadas vias de
baixo movimento real recebiam tráfego excessivo. Em cargas elevadas, essa distribuição
produzia filas consideradas pouco plausíveis.

A partir dessa observação, decidiu-se controlar probabilisticamente as entradas e
saídas da rede.

---

## 4. Classificação das entradas da rede

As entradas foram classificadas qualitativamente de acordo com o conhecimento local
sobre a importância relativa das vias.

| Edge | Nível | Via |
|---|---|---|
| `-102361495#0` | BAIXA | Rua Antônio Marafon |
| `-102361574.302` | BAIXA | Rua Osvaldo Cruz |
| `-103925179#1` | MÉDIA | Rua Brasil |
| `-1377929346#0` | ALTA | Rua Saul Brandalise |
| `320316411#0.175` | ALTA | Avenida Dom Pedro II |
| `99429224#2` | ALTA | Rua XV de Novembro |
| `99631677` | BAIXA | Rua Santa Catarina |
| `99643286#2` | MÉDIA | Rua XV de Novembro |

---

## 5. Classificação das saídas da rede

| Edge | Nível | Via |
|---|---|---|
| `-99643286#2` | MÉDIA | Rua XV de Novembro |
| `102361495#0` | BAIXA | Rua Antônio Marafon |
| `102361574` | BAIXA | Rua Osvaldo Cruz |
| `103925179#1` | MÉDIA | Rua Brasil |
| `103925196#0` | BAIXA | Rua Padre Anchieta |
| `1377929346#0` | ALTA | Rua Saul Brandalise |
| `98384536#0` | ALTA | Rua Nicolau Cavon |
| `99429213#1` | MÉDIA | Rua Antônio Fávero |

---

## 6. Ponderação preliminar da demanda

Foi adotada inicialmente a proporção:

- ALTA = 10
- MÉDIA = 6
- BAIXA = 1

Arquivos:

`config/demanda/demanda_1061.src.xml`

`config/demanda/demanda_1061.dst.xml`

A proporção não representa uma contagem real de tráfego. Ela funciona como uma
ponderação relativa das probabilidades de utilização das entradas e saídas.

A diferença elevada entre BAIXA e as demais categorias foi proposital, pois algumas
vias da região possuem fluxo significativamente inferior ao das principais vias do recorte.

A categoria MÉDIA foi posicionada mais próxima da ALTA por representar vias ainda
bastante movimentadas, embora menos dominantes que os principais acessos.

---

## 7. Validação da distribuição 10:6:1

Foi gerado inicialmente um conjunto de 300 viagens no intervalo de 0 a 600 segundos,
utilizando `seed = 42`.

Foram geradas 300 viagens e todas as 300 resultaram em rotas válidas.

### Origens observadas

| Edge | Quantidade |
|---|---:|
| `99429224#2` | 76 |
| `320316411#0.175` | 63 |
| `-1377929346#0` | 57 |
| `99643286#2` | 40 |
| `-103925179#1` | 38 |
| `99631677` | 13 |
| `-102361495#0` | 9 |
| `-102361574.302` | 4 |

A distribuição observada foi compatível com os pesos definidos.

A inspeção visual também indicou uma distribuição considerada plausível, com maior
concentração nas vias principais e baixa utilização das vias classificadas como BAIXA.

---

## 8. Teste com 300 veículos

Resultados globais:

- veículos carregados: 300;
- veículos inseridos: 300;
- distância média: 679,10 m;
- velocidade média: 11,42 m/s;
- duração média da viagem: 61,38 s;
- tempo médio parado: 1,54 s;
- time loss médio: 6,55 s;
- atraso médio de inserção: aproximadamente 0 s;
- teleports: 0;
- colisões: 0;
- emergency stops: 0;
- emergency braking: 0;
- warnings: 0.

A inspeção visual mostrou pequenas filas e retenções em interseções, sem formação de
gargalos generalizados.

Um dos pontos de maior espera ocorreu em uma interseção já conhecida por apresentar
restrição de capacidade no cenário real. Nesse ponto, foi observado tempo de espera
relativamente elevado, mas sem comprometimento geral da rede.

O teste de 300 veículos foi considerado funcional e plausível.

---

## 9. Teste com 600 veículos

Foi gerado um segundo conjunto utilizando a mesma ponderação 10:6:1, mantendo
a janela de geração de 600 segundos.

Resultados globais:

- veículos carregados: 600;
- veículos inseridos: 600;
- distância média: 672,55 m;
- velocidade média: 10,37 m/s;
- duração média da viagem: 72,16 s;
- tempo médio parado: 6,71 s;
- time loss médio: 17,83 s;
- atraso médio de inserção: 0,09 s;
- teleports: 0;
- colisões: 0;
- emergency stops: 0;
- emergency braking: 0;
- warnings: 0.

Comparado ao teste de 300 veículos, a carga maior produziu:

- redução da velocidade média;
- aumento do tempo médio de viagem;
- aumento expressivo do tempo parado;
- aumento do time loss;
- maior formação de filas.

A rede, entretanto, continuou capaz de inserir e concluir todas as viagens sem
teleports ou eventos de segurança.

---

## 10. Gargalo identificado no teste de 600 veículos

Durante a inspeção visual do teste de 600 veículos foi observado um comportamento
específico em uma interseção já conhecida como ponto de retenção.

Veículos que aguardavam em uma aproximação sem prioridade permaneciam parados mesmo
quando, visualmente, existiam lacunas aparentemente suficientes para realizar a entrada.

Embora os veículos da via prioritária ainda estivessem relativamente distantes, os
veículos aguardando evitavam entrar na corrente principal.

Esse comportamento provocou crescimento significativo da fila e, em determinados
momentos, retenção considerada superior ao comportamento esperado para o local.

A hipótese levantada foi de que o fenômeno não decorria apenas do volume de tráfego,
mas também da configuração de aceitação de oportunidades do modelo de motorista padrão
do SUMO.

---

## 11. Ajuste do comportamento de espera em cruzamentos

Durante os testes com maior carregamento da rede foi identificada uma retenção
excessiva em uma interseção já reconhecida como ponto de gargalo da região.

Na inspeção visual, veículos aguardando em uma aproximação sem prioridade
permaneciam parados mesmo quando existiam lacunas aparentemente suficientes
para realizar a entrada na corrente principal. Embora a existência de filas nesse
ponto seja coerente com a dinâmica observada na região, o tempo de hesitação dos
veículos simulados produzia retenções consideradas excessivas, principalmente
no teste com 600 veículos.

A partir dessa observação, foi investigado o parâmetro global
`time-to-impatience` do SUMO, relacionado ao tempo necessário para o aumento
progressivo da impaciência dos veículos durante situações de espera.

A configuração inicialmente utilizada correspondia a 180 segundos.

Para avaliar a influência desse parâmetro, foram executados testes com 120, 90 e
60 segundos. Em todos os casos foram mantidos constantes:

- a rede viária;
- os mesmos 600 veículos;
- as mesmas rotas;
- a distribuição de demanda;
- a semente pseudoaleatória;
- os demais parâmetros da simulação.

Os resultados obtidos foram:

| `time-to-impatience` | Velocidade média | Duração média | Waiting time | Time loss | Emergency braking |
|---:|---:|---:|---:|---:|---:|
| 180 s | 10,37 m/s | 72,16 s | 6,71 s | 17,83 s | 0 |
| 120 s | 10,58 m/s | 68,55 s | 4,99 s | 14,23 s | 1 |
| 90 s | 10,67 m/s | 66,98 s | 3,96 s | 12,65 s | 0 |
| 60 s | 10,74 m/s | 66,24 s | 3,48 s | 11,91 s | 0 |

A redução do parâmetro produziu diminuição progressiva do tempo parado e do
`time loss`.

Na inspeção visual, os valores de 60 e 90 segundos apresentaram comportamento
bastante semelhante. Em ambos os casos, os veículos passaram a aproveitar as
oportunidades de entrada com maior frequência, mantendo a formação de filas no
gargalo, porém sem a retenção excessiva observada anteriormente.

O valor de 120 segundos ainda apresentou maior hesitação e registrou uma
ocorrência de frenagem de emergência. A configuração de 180 segundos foi
considerada excessivamente conservadora para a dinâmica da interseção analisada.

### Decisão adotada

Foi definido:

`time-to-impatience = 90`

O valor de 90 segundos apresentou comportamento visual próximo ao obtido com
60 segundos e resultados quantitativos semelhantes, ao mesmo tempo em que
representa uma alteração menos intensa em relação à configuração inicialmente
utilizada.

O parâmetro será mantido constante como configuração-base nos experimentos
posteriores, evitando que sua variação interfira nas comparações entre os
diferentes cenários comportamentais.

---

## 12. Definição da distribuição da demanda

Os testes preliminares com geração totalmente aleatória de viagens mostraram
uma distribuição pouco plausível entre as vias da rede. Algumas ruas conhecidas
por possuir baixo movimento no cenário real recebiam quantidade excessiva de
veículos, enquanto acessos de maior importância não apresentavam a diferença
de fluxo esperada.

Por esse motivo, as entradas e saídas da rede foram classificadas
qualitativamente em três níveis:

- ALTA;
- MÉDIA;
- BAIXA.

A classificação foi baseada no conhecimento local sobre a importância relativa
dos acessos da região estudada.

Foi adotada a seguinte ponderação:

- ALTA = 10;
- MÉDIA = 6;
- BAIXA = 1.

Essa ponderação não representa contagens reais de tráfego. Seu objetivo é
estabelecer probabilidades relativas para a seleção das origens e destinos das
viagens.

A categoria MÉDIA foi propositalmente posicionada mais próxima da categoria
ALTA, pois as vias classificadas nesse nível ainda apresentam circulação
significativa, enquanto as vias classificadas como BAIXA possuem movimento
consideravelmente inferior.

Os pesos foram aplicados por meio dos arquivos:

`config/demanda/demanda_1061.src.xml`

`config/demanda/demanda_1061.dst.xml`

No teste inicial com 300 viagens, todas as viagens geradas produziram rotas
válidas e a distribuição observada foi compatível com a ponderação definida.

A inspeção visual também indicou maior presença de veículos nos acessos
classificados como ALTA e MÉDIA e baixa utilização relativa das vias
classificadas como BAIXA.

Dessa forma, a ponderação 10:6:1 foi mantida como configuração da demanda para
os cenários experimentais.

---

## 13. Testes para definição dos níveis de demanda

Após a definição da ponderação das entradas e saídas e do
`time-to-impatience = 90`, foram realizados testes com diferentes quantidades
de veículos gerados durante uma janela de 600 segundos.

Foram avaliadas cargas de:

- 300 veículos;
- 450 veículos;
- 600 veículos;
- 750 veículos;
- 900 veículos.

Os principais resultados foram:

| Veículos | Velocidade média | Duração média | Waiting time | Time loss | Depart delay | Teleports |
|---:|---:|---:|---:|---:|---:|---:|
| 300 | 11,46 m/s | 61,19 s | 1,34 s | 6,36 s | 0,00 s | 0 |
| 450 | 11,10 m/s | 63,19 s | 2,32 s | 8,91 s | 0,07 s | 0 |
| 600 | 10,67 m/s | 66,98 s | 3,96 s | 12,65 s | 0,09 s | 0 |
| 750 | 9,01 m/s | 90,66 s | 11,71 s | 35,77 s | 1,87 s | 0 |

Os cenários de 300, 450, 600 e 750 veículos foram concluídos integralmente,
sem teleports, colisões ou warnings.

### Teste com 300 veículos

O cenário apresentou circulação predominantemente fluida, com pequenas filas
e retenções localizadas nas interseções.

A rede manteve boa capacidade de circulação e todos os veículos concluíram
normalmente suas viagens.

Esse nível apresentou interação suficiente entre os veículos sem produzir
congestionamento significativo.

### Teste com 450 veículos

A carga de 450 veículos apresentou aumento moderado das retenções em comparação
ao cenário de 300 veículos.

Apesar disso, o comportamento geral permaneceu relativamente próximo ao
observado na carga menor, sem uma alteração expressiva no regime de
funcionamento da rede.

### Teste com 600 veículos

Com 600 veículos, tornou-se mais perceptível o aumento da interação entre os
veículos e da formação de filas.

O cenário permaneceu estável e todos os veículos foram inseridos e concluíram
suas viagens, porém houve aumento do tempo parado e do `time loss`.

A inspeção visual mostrou maior carregamento dos principais gargalos, sem
comprometer o funcionamento geral da rede após o ajuste do
`time-to-impatience`.

### Teste com 750 veículos

A carga de 750 veículos apresentou uma alteração mais acentuada no desempenho
da rede.

Foram registrados:

- velocidade média de 9,01 m/s;
- duração média de viagem de 90,66 s;
- tempo médio parado de 11,71 s;
- `time loss` médio de 35,77 s.

Apesar da maior retenção, todos os 750 veículos foram inseridos e concluíram
suas viagens, sem teleports, colisões, frenagens de emergência ou warnings.

Na inspeção visual foi possível perceber claramente o aumento das filas nos
principais pontos de gargalo em comparação ao cenário de 600 veículos.

As filas observadas ocorreram principalmente em pontos onde já eram esperadas
restrições de circulação, sem indicar colapso generalizado da rede.

### Teste de estresse com 900 veículos

O cenário com 900 veículos ultrapassou a faixa considerada adequada para os
experimentos.

Dos 900 veículos carregados:

- 753 foram inseridos;
- 147 ainda aguardavam inserção ao término da simulação;
- 211 permaneciam em circulação;
- apenas 542 viagens haviam sido concluídas.

Também foram registrados 64 teleports:

- 43 associados a congestionamento (`jam`);
- 15 associados a espera por prioridade (`yield`);
- 6 associados a posicionamento inadequado de faixa (`wrongLane`).

O teste apresentou retenções prolongadas e propagação do congestionamento por
diversos trechos da rede.

Por esse motivo, a carga de 900 veículos foi mantida apenas como teste de
estresse e não será utilizada como nível de demanda nos experimentos oficiais.

---

## 14. Níveis de demanda definidos

Com base nos testes quantitativos e nas inspeções visuais, foram definidos os
seguintes níveis de demanda:

| Nível | Quantidade de veículos | Janela de geração |
|---|---:|---:|
| BAIXO | 300 | 600 s |
| MÉDIO | 600 | 600 s |
| ALTO | 750 | 600 s |

O nível BAIXO representa uma condição de circulação predominantemente fluida,
mantendo pequenas interações e retenções entre os veículos.

O nível MÉDIO apresenta aumento perceptível da interação e da formação de filas,
mas sem comprometimento da estabilidade da rede.

O nível ALTO representa uma condição de congestionamento mais significativo,
com aumento claro dos tempos de viagem, espera e perda de tempo, porém ainda
sem provocar colapso operacional da rede.

A carga de 450 veículos foi utilizada como ponto intermediário durante a
calibração, mas apresentou comportamento ainda relativamente próximo ao cenário
de 300 veículos.

A carga de 900 veículos foi utilizada exclusivamente como teste de estresse,
permitindo identificar uma faixa de saturação que não será utilizada nas
simulações oficiais.

Dessa forma, ficam definidos para os experimentos:

- ponderação das entradas e saídas: 10:6:1;
- janela de geração: 600 segundos;
- nível baixo: 300 veículos;
- nível médio: 600 veículos;
- nível alto: 750 veículos;
- `time-to-impatience`: 90 segundos.

---

## 15. Pendência técnica antes do congelamento completo do cenário

Embora a rede, a distribuição da demanda e os níveis de fluxo tenham apresentado
comportamento satisfatório, permanece uma observação relacionada às mudanças de
faixa.

Durante as inspeções visuais foi percebida uma tendência de alguns veículos
realizarem mudanças estratégicas de faixa com grande antecedência.

Em determinados trechos com duas faixas disponíveis, os veículos tendem a se
posicionar antecipadamente na faixa necessária para movimentos posteriores,
mesmo quando seria possível permanecer distribuídos entre as duas faixas por
mais tempo.

Esse comportamento pode reduzir artificialmente a utilização de uma das faixas
e influenciar a formação de filas.

Antes do congelamento definitivo do cenário, deverá ser verificado se essa
antecipação:

1. decorre do comportamento padrão do modelo de mudança de faixa do SUMO;
2. pode ser ajustada por parâmetros do modelo de condução;
3. deverá fazer parte da diferenciação entre os perfis de motorista; ou
4. pode ser mantida como uma simplificação aceitável do cenário.

Nenhuma alteração nesse comportamento foi definida até o momento.

---

## 16. Situação atual do cenário

Neste ponto, encontram-se definidos:

- a rede viária funcional;
- os limites de velocidade;
- a estrutura de entradas e saídas;
- a classificação qualitativa dos acessos;
- a ponderação 10:6:1 da demanda;
- `time-to-impatience = 90`;
- os níveis de demanda baixo, médio e alto.

Os níveis definidos são:

- BAIXO: 300 veículos;
- MÉDIO: 600 veículos;
- ALTO: 750 veículos.

Ainda permanecem como etapas anteriores às simulações oficiais:

- verificar o comportamento das mudanças de faixa antecipadas;
- finalizar os parâmetros dos perfis cauteloso, normal e agressivo;
- definir as composições dos perfis em cada cenário;
- definir as sementes e o número de repetições;
- preparar a automação das execuções e da coleta das métricas.

Após a conclusão desses pontos, a configuração experimental deverá ser congelada
e não deverá mais ser alterada durante a coleta oficial dos resultados.

---

## 17. Organização do desenvolvimento do TCC

Conforme discutido com o orientador, o desenvolvimento será organizado
conceitualmente em duas etapas.

### Etapa 1 — Preparação do cenário experimental

Esta etapa compreende:

- construção e correção da rede;
- definição das velocidades;
- validação da circulação;
- definição da distribuição da demanda;
- definição dos níveis de fluxo;
- configuração dos parâmetros-base do simulador;
- definição dos perfis de motorista;
- testes preliminares e calibração do cenário.

Esta é a etapa atualmente em desenvolvimento.

### Etapa 2 — Execução dos experimentos

A segunda etapa será iniciada após o congelamento da configuração experimental.

Ela compreenderá:

- geração dos cenários experimentais;
- execução sistemática das simulações;
- repetições com sementes pseudoaleatórias definidas;
- coleta das métricas;
- consolidação dos dados;
- comparação entre os níveis de demanda e as composições de perfis;
- análise e discussão dos resultados.

A organização definitiva dessas etapas em capítulos e seções será realizada
durante a escrita do TCC.