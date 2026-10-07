# Checkpoint — fundamentação dos perfis de motoristas
**Data:** 2026-10-07

## Situação deste checkpoint

As simulações ficam pausadas temporariamente. O foco passa a ser a fundamentação teórica e técnica dos parâmetros usados para representar os perfis cauteloso, normal e agressivo.

A decisão metodológica central é:

> Os valores dos perfis não serão escolhidos porque produzem diferenças maiores ou resultados visualmente mais interessantes. Os valores deverão ser sustentados por literatura, pela documentação do SUMO e, apenas de forma complementar, por testes preliminares de plausibilidade e estabilidade no cenário.

A configuração chamada **Sensibilidade A** permanece apenas como experimento exploratório. Ela não foi adotada como configuração definitiva.

---

## Relação com o PTC aprovado

O próprio PTC já estabelece que a escolha dos parâmetros dos perfis deve considerar três fontes:

1. literatura sobre comportamento de motoristas;
2. parâmetros configuráveis no SUMO;
3. testes preliminares no cenário construído.

Portanto, os testes computacionais servem para verificar plausibilidade, estabilidade e sensibilidade, mas não substituem a justificativa teórica dos valores escolhidos.

---

## Baseline atualmente preservado

Arquivo:

`config/perfis/perfis.add.xml`

| Parâmetro | Cauteloso | Normal | Agressivo |
|---|---:|---:|---:|
| tau | 1.25 | 1.00 | 0.75 |
| minGap | 3.0 | 2.5 | 2.0 |
| accel | 2.5 | 2.6 | 2.9 |
| decel | 4.0 | 4.5 | 5.0 |
| sigma | 0.5 | 0.5 | 0.5 |
| speedFactor | 0.90 | 1.00 | 1.10 |
| speedDev | 0.10 | 0.10 | 0.10 |
| lcAssertive | 0.80 | 1.00 | 1.20 |
| impatience | -0.25 | 0.00 | 0.25 |
| jmTimegapMinor | 0.80 | 0.80 | 0.80 |

Configuração global usada nos testes:

- `--time-to-impatience 45`;
- `lcStrategic = 1.0`;
- `lcStrategicLookahead`: padrão do SUMO;
- `--time-to-teleport -1`;
- `--collision.check-junctions true`;
- `--collision.action warn`.

---

## Sensibilidade A — somente exploratória

A Sensibilidade A aumentou deliberadamente o contraste dos perfis para verificar o impacto dessa escolha sobre os resultados.

| Parâmetro | Cauteloso | Normal | Agressivo |
|---|---:|---:|---:|
| tau | 1.40 | 1.00 | 0.65 |
| minGap | 3.50 | 2.50 | 1.70 |
| accel | 2.30 | 2.60 | 3.10 |
| decel | 3.80 | 4.50 | 5.20 |
| speedFactor | 0.85 | 1.00 | 1.15 |
| lcAssertive | 0.70 | 1.00 | 1.35 |
| impatience | -0.40 | 0.00 | 0.40 |
| jmTimegapMinor | 0.80 | 0.80 | 0.80 |

Resultado geral: a separação entre cenários aumentou, mas isso **não constitui justificativa para adotar os valores**.

---

## Evidências já encontradas na literatura

### Mecheva, Furnadzhiev e Kakanakov (2022)

Artigo: *Modeling Driver Behavior in Road Traffic Simulation*.

O trabalho usa SUMO e apresenta faixas de valores examinadas para parâmetros de modelos de car-following.

Valores apresentados no artigo:

- `minGap`: 1; 1.5; 2; 2.5; 3 m;
- `accel`: 2.5; 2.6; 2.7; 2.8; 2.9 m/s²;
- `decel`: inclui 4; 4.3; 4.5; 4.8; 5; 5.3 e 5.8 m/s²;
- `sigma`: 0; 0.25; 0.5; 0.75; 1;
- `tau`: 0.25; 0.5; 0.75; 0.9; 1; 1.25 s.

Observação importante: os valores do **baseline** para `tau`, `minGap`, `accel` e `decel` permanecem dentro das faixas explicitamente examinadas nesse estudo. A Sensibilidade A ultrapassa essas faixas em vários pontos (`tau=1.40`, `minGap=3.50`, `accel=2.30/3.10`, `decel=3.80`), o que reduz sua sustentação direta por esta referência.

Isso não prova que a Sensibilidade A esteja incorreta, mas indica que o baseline é atualmente mais fácil de defender teoricamente.

### Park et al. (2019)

Artigo: *Understanding impacts of aggressive driving on freeway safety and mobility: A multi-agent driving simulation approach*.

O estudo compara comportamento normal e agressivo a partir de dados experimentais e posteriormente parametriza um simulador microscópico (VISSIM).

Resultados úteis:

- espaçamento médio de aproximadamente 62.2 m para normal e 32.4 m para agressivo;
- gap temporal mínimo de 0.7 s para normal e 0.4 s para agressivo;
- aceleração observada no comportamento agressivo significativamente maior;
- comportamento agressivo inclui seguimento próximo, mudança de faixa abrupta e desaceleração repentina.

Uso no TCC: esta referência sustenta fortemente a **direção das diferenças** entre perfis, especialmente menor headway/gap e acelerações mais intensas no agressivo. Os valores não devem ser copiados diretamente porque o estudo usa VISSIM, cenário rodoviário e outra metodologia de calibração.

### Zhai, Wu e Luo (2021)

Artigo: *Heterogeneous traffic flow modeling with drivers’ timid and aggressive characteristics*.

O estudo trata explicitamente da heterogeneidade entre motoristas agressivos e tímidos/cautelosos.

A literatura discutida pelo artigo relaciona heterogeneidade a:

- distância de segurança;
- tempo de reação;
- aceleração;
- velocidade máxima e mínima;
- headway psicológico;
- antecipação do estado do tráfego.

Os autores descrevem motoristas agressivos como mais propensos a acelerar aproveitando o estado previsto do tráfego, enquanto motoristas tímidos são mais avessos ao risco e prudentes na aceleração.

Uso no TCC: sustenta a construção conceitual dos perfis e a direção esperada de parâmetros, mas não fornece diretamente os valores do `vType` do SUMO adotados neste projeto.

### Makridis et al. (2023)

Artigo: *Characterising driver heterogeneity within stochastic traffic simulation*.

O trabalho reforça a importância da heterogeneidade de motoristas e destaca que parâmetros de car-following são frequentemente usados para representar comportamentos distintos.

Ponto metodológico importante: os autores alertam que **aceleração isoladamente não é suficiente para caracterizar a agressividade de um motorista**, porque a aceleração observável também depende das capacidades do veículo e das condições de tráfego.

Uso no TCC: reforça a decisão de definir o perfil por um **conjunto de parâmetros**, e não apenas por `accel`.

### Andrade et al. (2024)

Artigo: *Inferring Driver Behavior Profiles Using Digital Twins in Simulated Environments*.

O estudo compara condução cautelosa e agressiva em ambiente simulado.

Características descritas:

- cauteloso: respeito aos limites de velocidade, ausência de acelerações abruptas e técnicas suaves;
- agressivo: acelerações rápidas e violações frequentes dos limites de velocidade;
- cauteloso apresenta comportamento mais estável e controlado;
- agressivo apresenta manobras mais bruscas e reativas.

Uso no TCC: boa sustentação qualitativa para `speedFactor` e aceleração, mas não fornece valores diretamente transferíveis ao SUMO deste trabalho.

---

## Referências externas adicionais identificadas

### Chah et al. (2024)

*Building a Database of Simulated Driver Behaviors Using the SUMO Simulator*  
Lecture Notes in Networks and Systems, v. 1066, p. 536–555.  
DOI: `10.1007/978-3-031-66428-1_34`.

É especialmente relevante porque define três classes diretamente no SUMO: **slow, normal e dangerous**.

Tabela publicada:

| Perfil | minGap | accel | decel | tau | speedFactor |
|---|---:|---:|---:|---:|---:|
| Dangerous | 1.0 | 4.0 | 3.0 | 0.7 | 1.20 |
| Normal | 2.5 | 2.0 | 3.0 | 2.0 | 1.20 |
| Slow | 2.5 | 1.0 | 3.0 | 3.0 | 0.90 |

Limitação: o estudo trabalha com IDM/EIDM e possui objetivo diferente (perfilamento/alertas). Portanto, é uma referência direta de **parametrização comportamental no SUMO**, mas seus valores não devem ser transplantados automaticamente para o modelo Krauss usado neste TC.

### Camlica et al. (2022)

*Aggressive Driver Behavior Detection using Parallel Convolutional Neural Networks on Simulated and Real Driving Data*.  
9th International Conference on Internet of Things: Systems, Management and Security (IoTSMS), IEEE, 2022.

O trabalho utiliza SUMO e apresenta parâmetros para motorista normal e agressivo:

| Parâmetro | Normal | Agressivo |
|---|---:|---:|
| accel | 2.6 | 3.2 |
| decel | 4.5 | 5.5 |
| sigma | 0.5 | 0.3 |
| maxSpeed | 23 | 35 |
| minGap | 2.5 | 0.9 |
| tau | 1.5 | 1.0 |
| impatience | 0 | 1 |
| lcAssertive | 0 | 0.9 |

Essa referência é útil por tratar diretamente de SUMO e direção agressiva. Entretanto, o trabalho utilizou versão antiga do SUMO e alguns valores, especialmente de `lcAssertive`, devem ser avaliados com cautela à luz da semântica atual da ferramenta.

---

## Documentação atual do SUMO

Para veículo de passageiros/Krauss, a documentação atual apresenta como referências padrão:

- `accel = 2.6 m/s²`;
- `decel = 4.5 m/s²`;
- `sigma = 0.5`;
- `tau = 1.0 s`;
- `minGap = 2.5 m`;
- `speedFactor = 1.0`.

Esses valores coincidem com o perfil normal atualmente usado no baseline.

Semântica relevante:

- `tau`: headway temporal mínimo desejado;
- `minGap`: espaço mínimo em relação ao líder;
- `speedFactor`: multiplicador da velocidade desejada em relação ao limite;
- `lcAssertive`: valores maiores aceitam gaps longitudinais menores em mudanças de faixa;
- `impatience`: maior valor representa maior disposição para impor frenagem a veículos com prioridade;
- valores negativos de `impatience` podem ser usados como base para retardar o crescimento da impaciência;
- `jmTimegapMinor`: gap temporal mínimo ao cruzar uma ligação secundária em conflito com veículo prioritário.

---

## Avaliação provisória por parâmetro

| Parâmetro | Situação atual |
|---|---|
| `tau` | **bem fundamentável**: literatura, SUMO e estudos de agressividade sustentam diferenças por perfil |
| `minGap` | **bem fundamentável**: literatura e estudos empíricos sustentam menor espaçamento no agressivo |
| `accel` | **fundamentável**, mas não deve caracterizar o perfil isoladamente |
| `decel` | **fundamentável**, porém precisa ser apresentado como intensidade/conforto de frenagem no modelo, não capacidade física absoluta |
| `speedFactor` | **fundamentação razoável**, especialmente qualitativa; buscar mais suporte quantitativo |
| `lcAssertive` | **ainda precisa de suporte mais forte para os valores numéricos escolhidos** |
| `impatience` | **ainda precisa de suporte mais forte para os valores numéricos escolhidos** |
| `sigma` | mantido igual para todos; não é atualmente dimensão diferenciadora dos perfis |
| `jmTimegapMinor` | configuração global atual; não está diferenciada por perfil; justificar separadamente dos perfis |

---

## Conclusão provisória deste checkpoint

A literatura consultada até aqui favorece **manter o baseline como candidato principal**, e não adotar automaticamente a Sensibilidade A.

Razões:

1. o perfil normal do baseline coincide com vários valores padrão atuais do SUMO/Krauss;
2. `tau`, `minGap`, `accel` e `decel` do baseline permanecem dentro das faixas examinadas por Mecheva et al. (2022);
3. as tendências cauteloso ↔ normal ↔ agressivo são coerentes com Park et al. (2019), Zhai et al. (2021), Andrade et al. (2024), Chah et al. (2024) e Camlica et al. (2022);
4. a Sensibilidade A foi útil para mostrar que aumentar a separação altera os resultados, mas vários valores foram escolhidos exploratoriamente e ainda não possuem base suficiente para uso definitivo.

Nenhuma decisão definitiva é tomada neste checkpoint.

---

## Próximas tarefas antes de voltar às simulações

1. Fazer busca bibliográfica dirigida principalmente para:
   - `lcAssertive`;
   - `impatience`;
   - `speedFactor`;
   - gap acceptance em interseções;
   - perfis de motorista implementados especificamente em SUMO/Krauss.

2. Construir um quadro final de rastreabilidade:
   - parâmetro;
   - significado no SUMO;
   - valor normal;
   - tendência esperada por perfil;
   - valores encontrados na literatura;
   - valor escolhido;
   - referência;
   - justificativa.

3. Só depois decidir:
   - manter o baseline;
   - ajustar alguns parâmetros isolados com base bibliográfica;
   - ou adotar nova configuração.

4. Após congelar os perfis definitivos, executar uma rodada final limpa das seeds e salvar todos os arquivos de saída necessários para a análise.

---

## Regra metodológica registrada

**Experimentos de sensibilidade podem mostrar o efeito de um parâmetro, mas não serão usados como única justificativa para escolher seu valor. A escolha final deverá ser teoricamente rastreável e defensável perante a banca.**
