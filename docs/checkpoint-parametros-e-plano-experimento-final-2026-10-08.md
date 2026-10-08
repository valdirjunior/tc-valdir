# Checkpoint — Fundamentação dos perfis e plano para o experimento final
**Data:** 2026-10-08

## 1. Estado atual

A etapa de busca bibliográfica dirigida para fundamentar os perfis de motoristas pode ser considerada encerrada.

A configuração principal permanece baseada nos três perfis aprovados no PTC:

- **cauteloso**
- **normal**
- **agressivo**

A parametrização principal não pretende reproduzir empiricamente os motoristas de Videira. Ela representa perfis sintéticos, comparáveis e reprodutíveis, construídos a partir de:

1. tendências comportamentais descritas na literatura;
2. parâmetros documentados do SUMO;
3. valores próximos a padrões e faixas já utilizadas em estudos;
4. testes preliminares de plausibilidade e estabilidade no cenário.

A **Sensibilidade A** permanece como experimento exploratório complementar. Ela não substitui o baseline e não deve ser apresentada como calibração empírica.

---

## 2. Baseline dos perfis — configuração a congelar

| Parâmetro | Cauteloso | Normal | Agressivo | Situação |
|---|---:|---:|---:|---|
| `tau` | 1.25 | 1.00 | 0.75 | fundamentação forte |
| `minGap` | 3.0 | 2.5 | 2.0 | fundamentação forte |
| `accel` | 2.5 | 2.6 | 2.9 | fundamentação forte |
| `decel` | 4.0 | 4.5 | 5.0 | fundamentação forte |
| `sigma` | 0.5 | 0.5 | 0.5 | controle; padrão mantido |
| `speedFactor` | 0.90 | 1.00 | 1.10 | fundamentação boa |
| `speedDev` | 0.10 | 0.10 | 0.10 | controle; padrão mantido |
| `lcAssertive` | 0.80 | 1.00 | 1.20 | fundamentação adequada |
| `impatience` | -0.25 | 0.00 | 0.25 | direção fundamentada; amplitude sintética moderada |

### Configurações globais relevantes

- `jmTimegapMinor = 0.80`
- `--time-to-impatience 45`
- `lcStrategic = 1.0`
- `lcStrategicLookahead`: padrão do SUMO
- `--time-to-teleport -1`
- `--collision.check-junctions true`
- `--collision.action warn`
- passo de simulação: `0.1 s`
- demanda gerada no intervalo `0–600 s`
- fim fixo da simulação: `1800 s`

---

## 3. Rastreabilidade resumida

### `tau`

Interpretação: headway temporal mínimo desejado no modelo de car-following.

Base:
- perfil normal coincide com referência/padrão usado amplamente no SUMO;
- Mecheva et al. (2022) examinam valores que incluem 0.75, 1.0 e 1.25;
- estudos sobre agressividade indicam menores headways para motoristas mais agressivos.

**Decisão:** manter `1.25 / 1.00 / 0.75`.

### `minGap`

Interpretação: espaço mínimo desejado atrás do veículo líder.

Base:
- 2.5 m é referência comum do SUMO;
- Mecheva et al. examinam 1–3 m;
- estudos de direção agressiva indicam menores espaçamentos;
- Camlica et al. (2022) e outros trabalhos usam gaps menores em perfis agressivos.

**Decisão:** manter `3.0 / 2.5 / 2.0`.

### `accel`

Base:
- 2.6 m/s² é referência comum para o perfil normal;
- Mecheva et al. examinam a faixa utilizada no baseline;
- literatura de perfis agressivos utiliza acelerações maiores;
- Andrade et al. relacionam condução agressiva a acelerações mais rápidas.

**Decisão:** manter `2.5 / 2.6 / 2.9`.

### `decel`

Base:
- 4.5 m/s² é referência comum para o perfil normal;
- Mecheva et al. incluem 4.0, 4.5 e 5.0 entre valores examinados;
- estudos de perfis agressivos utilizam maior capacidade/intensidade de desaceleração.

**Decisão:** manter `4.0 / 4.5 / 5.0`.

### `speedFactor`

Interpretação: fator aplicado à velocidade desejada em relação ao limite.

Base:
- direção conceitual sustentada: cauteloso tende a respeitar mais o limite; agressivo tende a desejar velocidades maiores;
- estudos em SUMO utilizam fatores distintos para representar estilos de condução;
- valores do baseline são moderados em torno de 1.0.

**Decisão:** manter `0.90 / 1.00 / 1.10`.

### `lcAssertive`

Interpretação: disposição para aceitar gaps menores durante mudança de faixa.

Base:
- documentação atual do SUMO: valores maiores representam maior assertividade;
- trabalhos recentes utilizam diferenciação de `lcAssertive` entre estilos de condução;
- TransAID encontrou valores aproximadamente 0.8–0.9 para comportamento lateral mais conservador e usou distribuição com média próxima de 1.2 para veículos conduzidos manualmente;
- outros trabalhos mostram que valores acima de 1 são plausíveis/calibráveis.

**Decisão:** manter `0.80 / 1.00 / 1.20`.

### `impatience`

Interpretação: nível-base de impaciência em interações de prioridade; maior impaciência aumenta a disposição de realizar a manobra mesmo perturbando mais o fluxo prioritário.

Base:
- o modelo do SUMO admite nível-base negativo e positivo em torno do valor normal 0;
- estudos utilizam valores maiores para comportamentos mais assertivos/agressivos;
- valores elevados podem produzir aceitação excessiva de gaps;
- `-0.25 / 0 / +0.25` representa diferenciação deliberadamente moderada.

**Decisão:** manter `-0.25 / 0 / +0.25`.

A amplitude específica é uma decisão metodológica sintética, não uma calibração empírica.

---

## 4. Parâmetros globais de plausibilidade do cenário

### `--time-to-impatience = 45 s`

Este valor **não foi retirado diretamente da literatura**.

A literatura e a documentação sustentam:
- o mecanismo de crescimento da impaciência durante espera;
- a relação entre maior espera, maior impaciência e aceitação de gaps menores;
- a necessidade de cautela porque impaciência elevada pode produzir perturbações artificiais no fluxo prioritário.

O valor de 45 s foi escolhido nos testes preliminares do projeto porque tempos maiores produziram rejeição prolongada de oportunidades de passagem e filas persistentemente artificiais no cenário.

**Classificação metodológica:** ajuste preliminar de plausibilidade do cenário, não calibração empírica.

### `jmTimegapMinor = 0.80 s`

Interpretação: intervalo temporal mínimo para que um veículo sem prioridade passe diante de um veículo prioritário.

Base:
- Ferrarotti et al. (2024) tratam explicitamente `jmTimegapMinor` como parâmetro calibrável em um roundabout real;
- Bagheri et al. (2023) tratam o gap mínimo diante de fluxo prioritário como parâmetro relevante para calibração de gap acceptance;
- trabalhos recentes mostram que a aceitação de gaps depende fortemente do local, comportamento e condições de tráfego.

O valor específico `0.80 s` não é apresentado como valor universal na literatura.

No projeto, ele foi adotado após testes preliminares em que o comportamento padrão produzia rejeição prolongada de gaps considerados visualmente plausíveis.

**Classificação metodológica:** ajuste preliminar de plausibilidade do cenário, não calibração empírica.

---

## 5. Referências que devem ser preservadas para a escrita final

### Fundamentação principal dos perfis

- Mecheva, Furnadzhiev e Kakanakov (2022) — faixas de parâmetros comportamentais no SUMO.
- Park et al. (2019) — diferenças entre condução normal/agressiva, incluindo headway e espaçamento.
- Andrade et al. (2024) — características de perfis cauteloso/agressivo.
- Makridis et al. (2023) — heterogeneidade de motoristas e cautela com indicadores isolados.
- Camlica et al. (2022) — parametrização explícita de comportamento normal/agressivo no SUMO.
- Dias, Machado e Pereira (2013) — representação de personalidade de motoristas no SUMO.
- Chah et al. (2024) — perfis simulados no SUMO.
- Hegazy e Moustafa (2017) — relação entre parâmetros e agressividade.

### `lcAssertive`

- Yavuz e Ozen (2025) — diferenciação de comportamento defensivo/normal/agressivo.
- TransAID — sensibilidade e parametrização do modelo LC2013; faixas de `lcAssertive`.
- Schrader/Bittle (2024) — análise de sensibilidade e dificuldade de definir limites universais para parâmetros de lane changing/junction.

### `impatience` e gap acceptance

- Erdmann e Krajzewicz — mecanismo de interseções e impaciência no SUMO.
- Tshibangu-Muabila et al. (2023) — uso explícito de diferentes níveis de impaciência.
- Bagheri et al. (2023) — calibração de gap acceptance e problemas de gaps irrealisticamente pequenos.
- Reddy et al. (2025) — comportamento de gap acceptance de motoristas humanos e implementação no SUMO.

### `jmTimegapMinor`

- Ferrarotti et al. (2024) — calibração explícita de `jmTimegapMinor` em roundabout real.
- Bagheri et al. (2023) — calibração de parâmetros relacionados a gap acceptance no SUMO.

### Apoio conceitual

- Lawrence et al. (2021/2022) — gap acceptance e perfis de risco em pedestres; não usar como justificativa numérica para `jmTimegapMinor`.
- estudo HATLAS sobre time-to-impatience — apenas relação conceitual entre espera e limiar de impaciência; não corresponde ao parâmetro do SUMO.

---

## 6. Sensibilidade A

A Sensibilidade A fica preservada como experimento complementar.

Uso recomendado no TCC:

> análise exploratória de sensibilidade em que a diferença entre os perfis cauteloso e agressivo foi deliberadamente ampliada para observar como uma maior separação paramétrica afeta as métricas do tráfego.

Não descrever a Sensibilidade A como:
- calibração;
- representação empiricamente validada;
- configuração principal.

Ela serve para mostrar a sensibilidade do sistema à magnitude da heterogeneidade comportamental.

---

## 7. Decisão de congelamento

A menos que seja identificado um defeito de implementação, **não alterar mais**:

- rede;
- demanda V2.3;
- composições dos cenários;
- níveis de demanda 300 / 450 / 625;
- perfis baseline;
- `jmTimegapMinor`;
- `time-to-impatience`;
- demais configurações globais.

Mudanças futuras só devem ocorrer se houver:
1. erro técnico verificável; ou
2. decisão metodológica explícita discutida com o orientador.

Resultados desfavoráveis, congestionamento ou variabilidade não são motivos para retunar.

---

## 8. Próxima etapa recomendada — preparação da coleta oficial

Antes da rodada oficial:

1. revisar o script de execução para garantir que **todos os arquivos de saída sejam preservados**;
2. revisar o analisador para contemplar as métricas aprovadas no PTC:
   - tempo médio de viagem;
   - velocidade média;
   - tempo parado;
   - filas;
   - vazão;
3. preservar também métricas diagnósticas:
   - `timeLoss`;
   - `departDelay`;
   - tempo de limpeza;
   - frenagens emergenciais;
   - colisões;
4. testar o pipeline completo com poucas execuções apenas para verificar arquivos e parsing, sem retunar comportamento.

### Política de seeds recomendada

Separar metodologicamente os conjuntos:

- seeds `42–71`: histórico de desenvolvimento, pilotos, validações e sensibilidade;
- experimento principal final: usar **30 seeds novas**, ainda não utilizadas no ajuste do cenário.

Exemplo recomendado: `1001–1030`.

O valor numérico da seed não representa intensidade ou cenário; serve apenas para inicializar o gerador pseudoaleatório. A separação em outra faixa facilita documentar quais execuções são pilotos e quais pertencem ao experimento final.

Com 30 seeds, 3 níveis de demanda e 7 composições:

**30 × 3 × 7 = 630 execuções oficiais.**

A configuração deve permanecer fixa durante todas elas.

---

## 9. Após a coleta oficial

Produzir uma base por execução (uma linha por seed × nível de demanda × cenário) e consolidar:

- média;
- desvio-padrão;
- mediana quando pertinente;
- intervalo de confiança, caso seja adotado;
- diferenças absolutas e percentuais;
- comparação pareada entre cenários usando a mesma seed.

A análise estatística inferencial pode ser decidida depois de observar a distribuição e variabilidade dos resultados. Não é necessário definir testes estatísticos antes de inspecionar a base final.

---

## 10. Regra de escrita

No TCC, distinguir sempre:

1. **parâmetros dos perfis**, cuja direção e faixas são fundamentadas na literatura;
2. **ajustes globais de plausibilidade**, como `jmTimegapMinor=0.80` e `time-to-impatience=45`;
3. **Sensibilidade A**, que é uma perturbação experimental exploratória;
4. **calibração empírica**, que não foi realizada para motoristas de Videira.

Formulação-base:

> Os perfis foram definidos como abstrações computacionais fundamentadas em tendências comportamentais descritas na literatura e operacionalizadas por parâmetros do SUMO. Os valores foram mantidos próximos a referências e faixas previamente utilizadas, enquanto parâmetros globais relacionados ao funcionamento das interseções foram ajustados em testes preliminares de plausibilidade. O objetivo não foi calibrar individualmente o comportamento de motoristas reais de Videira, mas construir cenários controlados e reprodutíveis para comparação.
