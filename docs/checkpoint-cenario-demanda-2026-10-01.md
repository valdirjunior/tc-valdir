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

## 11. Teste diagnóstico de impaciência

Foi realizado um teste mantendo:

- a mesma rede;
- os mesmos 600 veículos;
- as mesmas rotas;
- a mesma distribuição de demanda;
- a mesma seed;
- os demais parâmetros da simulação.

A única alteração foi:

`--time-to-impatience 60`

O comportamento padrão utilizado anteriormente correspondia a um crescimento de
impaciência mais lento.

Com o novo valor, observou-se visualmente uma alteração significativa no comportamento
da interseção problemática.

Os veículos aguardando passaram a aproveitar oportunidades de entrada mais rapidamente.

Ainda houve formação de filas, como esperado para o local, porém:

- as filas foram significativamente menores;
- os veículos apresentaram menor hesitação;
- o gargalo continuou existindo, mas deixou de provocar o travamento exagerado observado
  anteriormente;
- o comportamento visual foi considerado mais plausível.

O teste reforça a hipótese de que parte da retenção observada anteriormente estava
associada ao comportamento de aceitação de oportunidades na interseção, e não exclusivamente
ao nível de demanda.

### Situação do parâmetro

O valor de 60 s NÃO está definido definitivamente.

Ele deve ser tratado neste momento como valor experimental/candidato.

Ainda deverá ser decidido se:

1. `time-to-impatience` será uma configuração-base comum a todos os veículos; ou
2. a impaciência fará parte da diferenciação entre os perfis de motorista.

Essa decisão deverá considerar a documentação do SUMO, literatura sobre comportamento
de motoristas e os testes com os perfis cauteloso, normal e agressivo.

---

## 12. Situação atual da demanda

A proporção 10:6:1 apresentou bom comportamento nos testes realizados até o momento.

Ela deve ser mantida como configuração candidata enquanto são avaliados diferentes
níveis de carregamento da rede.

Ainda não foram definidos definitivamente os níveis de fluxo BAIXO, MÉDIO e ALTO.

Até o momento:

- 300 veículos apresentaram circulação fluida com retenções localizadas;
- 600 veículos produziram maior interação e filas, permanecendo tecnicamente estáveis;
- parte da fila excessiva inicialmente observada com 600 veículos foi atribuída à
  dinâmica de impaciência/aceitação de oportunidades no cruzamento analisado.

Testes adicionais deverão ser realizados antes da definição final dos níveis de demanda.

---

## 13. Decisões que ainda NÃO estão fechadas

Os seguintes pontos permanecem em avaliação:

- níveis definitivos de demanda baixa, média e alta;
- valor definitivo de `time-to-impatience`;
- participação da impaciência na definição dos perfis;
- valores finais dos parâmetros dos perfis cauteloso, normal e agressivo;
- número definitivo de repetições das simulações;
- conjunto final de sementes pseudoaleatórias.

---

## 14. Próximas etapas

1. Executar novamente o cenário de 600 veículos com `time-to-impatience = 60`,
   registrando todas as saídas quantitativas.
2. Comparar os resultados com a execução de 600 veículos usando o comportamento padrão.
3. Avaliar se são necessários testes intermediários de `time-to-impatience`, como
   90 ou 120 segundos.
4. Definir a configuração-base do comportamento em cruzamentos.
5. Continuar os testes de carga para determinar os níveis baixo, médio e alto.
6. Finalizar a definição dos perfis de motorista.
7. Congelar a configuração do cenário.
8. Iniciar as simulações oficiais e a coleta sistemática dos resultados.

---

## 15. Organização prevista para o desenvolvimento do TCC

Após conversa com o orientador, o desenvolvimento será organizado conceitualmente
em duas etapas.

### Etapa 1 — Preparação do cenário experimental

Inclui:

- construção da rede;
- correções da malha;
- definição das velocidades;
- validação da circulação;
- definição e calibração da demanda;
- definição dos perfis de motorista;
- definição dos níveis de fluxo;
- definição dos parâmetros e procedimentos experimentais.

Esta é a etapa atualmente em desenvolvimento.

### Etapa 2 — Execução dos experimentos

Começará quando a rede, a demanda, os perfis e os demais parâmetros forem considerados
estáveis.

Inclui:

- geração dos cenários experimentais;
- execução das simulações oficiais;
- repetições com sementes definidas;
- coleta das métricas;
- consolidação dos dados;
- comparação dos perfis e níveis de demanda;
- análise e discussão dos resultados.

A separação definitiva em capítulos e os títulos das seções ainda deverão ser ajustados
durante a escrita final.