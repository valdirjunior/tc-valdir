# Rastreabilidade dos parâmetros dos perfis de motoristas
**Versão de trabalho — 2026-10-07**

## Objetivo

Este documento registra a origem, a interpretação e o grau de sustentação dos parâmetros usados para representar os perfis **cauteloso**, **normal** e **agressivo** no SUMO.

A regra metodológica adotada é:

> Os parâmetros do experimento principal devem ser escolhidos a partir da literatura, da semântica atual do SUMO e de testes preliminares de plausibilidade. Testes de sensibilidade podem demonstrar impacto dos parâmetros, mas não serão usados como justificativa única para escolher seus valores.

A configuração denominada **Sensibilidade A** permanece como experimento exploratório e não é considerada, neste momento, a configuração definitiva.

---

## 1. Baseline atual

| Parâmetro | Cauteloso | Normal | Agressivo |
|---|---:|---:|---:|
| `tau` | 1.25 | 1.00 | 0.75 |
| `minGap` | 3.0 | 2.5 | 2.0 |
| `accel` | 2.5 | 2.6 | 2.9 |
| `decel` | 4.0 | 4.5 | 5.0 |
| `sigma` | 0.5 | 0.5 | 0.5 |
| `speedFactor` | 0.90 | 1.00 | 1.10 |
| `speedDev` | 0.10 | 0.10 | 0.10 |
| `lcAssertive` | 0.80 | 1.00 | 1.20 |
| `impatience` | -0.25 | 0.00 | 0.25 |
| `jmTimegapMinor` | 0.80 | 0.80 | 0.80 |

Parâmetros globais relevantes:

- `--time-to-impatience 45`;
- `lcStrategic = 1.0`;
- `lcStrategicLookahead`: padrão do SUMO;
- `--time-to-teleport -1`;
- `--collision.check-junctions true`;
- `--collision.action warn`.

---

## 2. Quadro de rastreabilidade

| Parâmetro | Significado operacional no SUMO atual | Evidência disponível | Avaliação do baseline | Decisão provisória |
|---|---|---|---|---|
| `tau` | Headway temporal mínimo desejado no modelo de car-following. No Krauss é baseado no espaço líquido entre líder e seguidor. Não deve ser descrito simplesmente como “tempo de reação fisiológico”. | SUMO: padrão 1.0. Mecheva et al. (2022): valores examinados 0.25, 0.5, 0.75, 0.9, 1 e 1.25 s. Park et al. (2019): agressivos apresentam gaps temporais menores. Dias et al. (2013): parâmetros agressivos usam valores de `tau` menores que perfis corteses em diversas classes. Camlica et al. (2022): normal 1.5 e agressivo 1.0. | **FORTE.** Os três valores estão dentro da literatura examinada e a direção CAU > NOR > AGR é sustentada. | **Manter 1.25 / 1.00 / 0.75.** |
| `minGap` | Espaço mínimo mantido atrás do líder, em metros. | SUMO: padrão 2.5 m. Mecheva: 1–3 m examinados. Park: agressivos mantêm espaçamento muito menor. Dias: perfis agressivos utilizam gaps menores. Camlica: 2.5 m normal e 0.9 m agressivo. | **FORTE.** O baseline é conservador em relação a estudos mais extremos e permanece dentro da faixa de Mecheva. | **Manter 3.0 / 2.5 / 2.0.** |
| `accel` | Capacidade/aceleração usada pelo modelo do veículo. | SUMO: padrão 2.6 m/s². Mecheva: 2.5–2.9 m/s² examinados. Dias: agressivos apresentam valores maiores que corteses; perfil agressivo de meia-idade chega a 2.9. Camlica: 2.6 normal e 3.2 agressivo. Andrade: agressivo caracterizado por acelerações rápidas, cauteloso por evitar acelerações bruscas. Makridis alerta que aceleração isolada não caracteriza agressividade. | **FORTE**, desde que tratada como um componente do perfil, não como indicador isolado. | **Manter 2.5 / 2.6 / 2.9.** |
| `decel` | Capacidade/intensidade de desaceleração usada pelo modelo. Não representa apenas frenagem de emergência. | SUMO: padrão 4.5 m/s². Mecheva inclui 4.0, 4.5 e 5.0 entre valores examinados. Dias usa maior desaceleração em diversos perfis agressivos. Camlica: 4.5 normal e 5.5 agressivo. | **FORTE.** Valores e direção são compatíveis com referências. | **Manter 4.0 / 4.5 / 5.0.** |
| `speedFactor` | Multiplicador da velocidade desejada em relação ao limite da via. Valores >1 permitem desejar velocidades acima do limite, sujeito aos demais limites do veículo. | SUMO: padrão 1.0 e `speedDev=0.1`. Andrade: cauteloso respeita limites; agressivo apresenta violações frequentes de velocidade. Chah et al. (2024): perfil slow 0.90 e dangerous 1.20. Estudos de calibração usam faixas aproximadamente entre 0.9 e 1.15/1.2. | **BOA.** A direção é bem sustentada e 0.90/1.10 são alterações moderadas. | **Manter 0.90 / 1.00 / 1.10**, salvo evidência contrária. |
| `lcAssertive` | Disposição para aceitar gaps longitudinais menores na faixa-alvo. O gap requerido é dividido por esse valor. Padrão atual = 1. Valores >1 significam maior assertividade. | Documentação atual do SUMO sustenta claramente a direção. Estudo do DLR usa 1.0 para veículo automatizado e 1.2 para veículo convencional mais assertivo. Outros estudos usam `lcAssertive` para modelar heterogeneidade. Camlica usa 0/0.9, mas em SUMO 0.12.3, portanto não é diretamente transferível para a semântica atual. | **MÉDIA.** A direção 0.8 < 1 < 1.2 é defensável, mas o triplo exato ainda não tem uma fonte direta. | **Manter provisoriamente.** Fazer uma última busca dirigida antes de congelar. |
| `impatience` | Valor-base da impaciência em cruzamentos: aumenta a disposição de realizar uma manobra mesmo impondo desaceleração a veículos prioritários. Valores negativos são permitidos e retardam o crescimento da impaciência. | SUMO: padrão 0.0; semântica explícita e suporte a valores negativos. Camlica usa 0 para normal e 1 para agressivo. Literatura comportamental associa agressividade à impaciência, mas ainda não foi encontrada fonte que justifique especificamente -0.25/0/+0.25. | **MÉDIA/FRACA para os valores exatos.** Direção é defensável; magnitude é escolha sintética. | **Investigar antes de congelar.** Não alterar ainda. |
| `sigma` | Imperfeição/aleatoriedade longitudinal do modelo Krauss. | SUMO: padrão 0.5. Mecheva examina 0–1. | **FORTE como controle.** Não está sendo usado para distinguir perfis. | **Manter 0.5 nos três.** |
| `speedDev` | Desvio da distribuição de `speedFactor`. | SUMO: padrão 0.1 para passageiros. | **FORTE como controle.** | **Manter 0.10 nos três.** |
| `jmTimegapMinor` | Gap temporal mínimo para passar por ligação secundária antes/depois de veículo prioritário que ainda não entrou no cruzamento. | SUMO atual: padrão 1.0 s. Valores menores representam aceitação de gaps menores. O valor 0.80 foi escolhido no projeto após testes de plausibilidade visual, não por calibração empírica. A própria equipe do SUMO já informou que não conhece calibração específica que tenha originado o padrão de 1 s. | **FRACA como valor teórico.** É parâmetro global do cenário, não diferença entre perfis. | **Manter provisoriamente 0.80**, mas documentar como ajuste de plausibilidade do cenário e discutir se requer validação adicional/orientador. |
| `--time-to-impatience` | Tempo usado para crescimento da impaciência dinâmica. | SUMO atual: padrão 180 s. O projeto testou 60 s e 45 s e adotou 45 s após observar rejeição excessiva de gaps e filas artificiais. | **FRACA como valor derivado de literatura.** Justificativa é experimental/plausibilidade do cenário. | **Não mexer agora.** Registrar claramente como ajuste preliminar e considerar discutir com orientador. |
| `lcStrategic` | Intensidade/eagerness de mudanças estratégicas de faixa. | SUMO: padrão 1.0. Testes do projeto com 0.75 e 0.50 não produziram ganho convincente e alguns introduziram instabilidade. | **FORTE como controle padrão.** | **Manter 1.0.** |

---

## 3. O que o artigo de Camlica et al. (2022) realmente sustenta

Camlica et al. (2022) utiliza SUMO em conjunto com Webots para gerar comportamento normal e agressivo.

A tabela publicada no artigo apresenta:

| Parâmetro | Normal | Agressivo |
|---|---:|---:|
| `accel` | 2.6 | 3.2 |
| `decel` | 4.5 | 5.5 |
| `sigma` | 0.5 | 0.3 |
| `maxSpeed` | 23 | 35 |
| `minGap` | 2.5 | 0.9 |
| `tau` | 1.5 | 1.0 |
| `impatience` | 0 | 1 |
| `lcAssertive` | 0 | 0.9 |

O próprio artigo informa que os parâmetros foram definidos a partir de documentação e estudos anteriores.

Entretanto, há uma limitação importante: o estudo usa **SUMO 0.12.3**, enquanto este TCC utiliza uma versão muito mais recente. Por isso, parâmetros cujo significado ou faixa evoluíram — especialmente `lcAssertive` — não devem ser copiados diretamente.

Uso recomendado da referência:

- forte para sustentar a **direção** de `accel`, `decel`, `minGap`, `tau` e `impatience`;
- útil como exemplo de perfis comportamentais explícitos no SUMO;
- não usar isoladamente para justificar numericamente `lcAssertive` na versão atual.

---

## 4. Dias, Machado e Pereira (2013)

O trabalho *Simulating the Impact of Drivers' Personality on City Transit* é relevante porque representa personalidade de motoristas diretamente no SUMO.

Os autores partem dos parâmetros padrão:

- `accel = 2.6`;
- `decel = 4.5`;
- `minGap = 2.5`;
- `tau = 1.0`.

Depois constroem perfis diferenciados. Exemplos:

| Tipo | accel | decel | minGap | tau |
|---|---:|---:|---:|---:|
| jovem cortês, homem | 2.5 | 4.5 | 2.5 | 1.0 |
| jovem agressivo, homem | 3.1 | 5.5 | 1.2 | 1.0 |
| meia-idade cortês, homem | 2.4 | 4.1 | 2.5 | 1.5 |
| meia-idade agressivo, homem | 2.9 | 5.0 | 1.6 | 1.3 |
| idoso cortês, homem | 2.3 | 3.8 | 2.5 | 1.9 |
| idoso agressivo, homem | 2.6 | 4.5 | 2.0 | 1.7 |

Limitação declarada pelos próprios autores: os valores são **tentativos**, e eles deram mais atenção às diferenças entre tipos do que aos valores absolutos.

Isso torna o artigo útil para sustentar a lógica relativa dos perfis, mas não como fonte de calibração exata.

---

## 5. Sensibilidade A

A Sensibilidade A deve ser preservada como **análise exploratória de sensibilidade**.

Formulação metodológica sugerida:

> Foi realizada adicionalmente uma análise exploratória de sensibilidade, na qual se ampliou deliberadamente a diferença entre os parâmetros dos perfis cauteloso e agressivo em relação ao perfil normal. Essa parametrização não foi adotada como representação empiricamente calibrada dos condutores, mas utilizada para avaliar se uma maior separação comportamental produziria alterações correspondentes nas métricas de desempenho do tráfego.

O resultado pode ser usado para mostrar que a magnitude da heterogeneidade comportamental influencia a magnitude dos efeitos simulados.

Não usar a Sensibilidade A como argumento para escolher os parâmetros do experimento principal.

---

## 6. Estado atual da decisão

### Parâmetros que já podem ser considerados suficientemente defendidos

- `tau`;
- `minGap`;
- `accel`;
- `decel`;
- `speedFactor`;
- `sigma` (controle);
- `speedDev` (controle);
- `lcStrategic` (controle).

### Parâmetros que ainda merecem investigação curta e dirigida

- `lcAssertive`: direção bem sustentada; valores exatos ainda não.
- `impatience`: direção sustentada; valores -0.25/0/+0.25 ainda não.
- `jmTimegapMinor = 0.80`: ajuste global de plausibilidade, não calibrado.
- `--time-to-impatience = 45`: ajuste global de plausibilidade, não derivado diretamente da literatura.

---

## 7. Próxima etapa

Não executar novas simulações ainda.

Realizar apenas uma rodada bibliográfica curta, focada em:

1. estudos recentes que usem `lcAssertive` no SUMO para motoristas humanos/heterogêneos;
2. estudos que usem `impatience` ou parâmetros de aceitação de prioridade/interseção;
3. literatura de gap acceptance aplicável a cruzamentos não semaforizados;
4. verificar se há justificativa externa razoável para `jmTimegapMinor` e `time-to-impatience`, ou se eles devem ser apresentados explicitamente como ajustes preliminares de plausibilidade.

Depois dessa busca:

- se não surgir evidência que contradiga o baseline, **congelar o baseline**;
- se surgir evidência clara contra algum valor, fazer apenas ajuste pontual;
- atualizar a metodologia do TCC somente após essa decisão.

---

## 8. Referências prioritárias

- CAMLICA, Z.; QUESENBERRY, J.; CARBALLO, D.; CROWLEY, M. *Aggressive Driver Behavior Detection using Parallel Convolutional Neural Networks on Simulated and Real Driving Data*. 2022 9th International Conference on Internet of Things: Systems, Management and Security (IOTSMS), 2022. DOI: 10.1109/IOTSMS58070.2022.10061930.
- DIAS, J. A. C.; MACHADO, P.; PEREIRA, F. C. *Simulating the Impact of Drivers' Personality on City Transit*. World Conference on Transport Research, 2013.
- MECHEVA, T.; FURNADZHIEV, R.; KAKANAKOV, N. *Modeling Driver Behavior in Road Traffic Simulation*. Sensors, 2022.
- PARK, S. et al. *Understanding impacts of aggressive driving on freeway safety and mobility: A multi-agent driving simulation approach*. Transportation Research Part F, 2019.
- ZHAI, C.; WU, W.; LUO, S. *Heterogeneous traffic flow modeling with drivers’ timid and aggressive characteristics*. Chinese Physics B, 2021.
- MAKRIDIS, M. A. et al. *Characterising driver heterogeneity within stochastic traffic simulation*. Transportmetrica B, 2023.
- ANDRADE, M. et al. *Inferring Driver Behavior Profiles Using Digital Twins in Simulated Environments*. 2024.
- SUMO Documentation. *Definition of Vehicles, Vehicle Types, and Routes*; *Simulation/Safety*.

---

## Regra para a escrita final

Na metodologia, não afirmar que os perfis representam motoristas reais de Videira de forma calibrada.

Formulação adequada:

> Os perfis foram definidos como abstrações computacionais baseadas em tendências comportamentais descritas na literatura e operacionalizadas por parâmetros do SUMO. Os valores adotados foram mantidos próximos a referências e valores padrão da ferramenta, e sua plausibilidade foi verificada por testes preliminares no cenário. O objetivo foi produzir perfis comparáveis e reprodutíveis, e não calibrar individualmente motoristas reais.
