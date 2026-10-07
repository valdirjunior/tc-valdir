# Checkpoint — cenário, demanda, perfis e definição preliminar dos fluxos
**Data:** 2026-10-07

## Objetivo deste checkpoint

Registrar o estado atual do cenário de simulação antes de novos testes de sensibilidade dos perfis de motoristas e de possíveis ampliações do número de sementes pseudoaleatórias.

Este checkpoint representa a configuração-base atualmente considerada estável para comparação entre cenários. Alterações futuras nos perfis deverão ser tratadas como testes de sensibilidade e não devem sobrescrever os resultados obtidos com esta configuração.

## Cenário e demanda

- Rede baseada no entorno da Praça Nereu Ramos, em Videira/SC.
- Rede atual: `config/nereu_ramos.net.xml`.
- Demanda atual: versão V2.3 ponderada.
- Configuração da demanda: `config/demanda/demanda_v2.json`.
- Geração de viagens: `scripts/gerar_demanda_v2.py`.
- Atribuição dos perfis: `scripts/atribuir_perfis.py`.
- Intervalo de geração da demanda: 0 a 600 s.
- Fim da simulação: 1800 s.
- Teleportes desativados (`--time-to-teleport -1`).

A mesma realização de demanda é reutilizada entre as diferentes composições de perfis para uma mesma combinação de seed e fluxo, variando apenas a composição comportamental.

## Configuração comportamental-base

Perfis utilizados:

- cauteloso;
- normal;
- agressivo.

Parâmetros-base dos perfis:

| Perfil | tau | minGap | accel | decel | speedFactor | speedDev | lcAssertive | impatience |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Cauteloso | 1.25 | 3.0 | 2.5 | 4.0 | 0.90 | 0.10 | 0.80 | -0.25 |
| Normal | 1.00 | 2.5 | 2.6 | 4.5 | 1.00 | 0.10 | 1.00 | 0.00 |
| Agressivo | 0.75 | 2.0 | 2.9 | 5.0 | 1.10 | 0.10 | 1.20 | 0.25 |

Configuração adicional utilizada nas execuções atuais:

- `--time-to-impatience 45`;
- `jmTimegapMinor = 0.80`;
- `lcStrategic = 1.0`;
- `lcStrategicLookahead`: valor padrão do SUMO;
- `--collision.check-junctions true`;
- `--collision.action warn`.

## Composições testadas

- `REF`: 0% cauteloso, 100% normal, 0% agressivo;
- `EQU`: aproximadamente 33% cauteloso, 34% normal e 33% agressivo;
- `CAU`: 60% cauteloso, 40% normal, 0% agressivo;
- `AGR`: 0% cauteloso, 40% normal, 60% agressivo;
- `MIX_C`: 60% cauteloso, 20% normal, 20% agressivo;
- `MIX_N`: 20% cauteloso, 60% normal, 20% agressivo;
- `MIX_A`: 20% cauteloso, 20% normal, 60% agressivo.

## Testes de carregamento

Foram testados volumes mais elevados para identificar a região de estabilidade da rede.

Resumo dos testes:

| Fluxo | Execuções avaliadas | Execuções completas | Observação |
|---:|---:|---:|---|
| 625 | 140 | 140 | estável nas seeds 42–61 |
| 650 | 70 | 69 | um congestionamento persistente (`seed 43 / CAU`) |
| 675 | 35 | 33 | dois congestionamentos persistentes |
| 700 | 35 | 33 | dois congestionamentos persistentes |
| 750 | 35 | 33 | dois congestionamentos persistentes |

Os testes indicam que volumes acima de 625 entram com maior frequência em uma região sensível a combinações específicas de demanda, composição de perfis e seed.

## Níveis de fluxo atualmente adotados como baseline

- fluxo baixo: **300 veículos em 600 s**;
- fluxo médio: **450 veículos em 600 s**;
- fluxo alto: **625 veículos em 600 s**.

Para esses três níveis foram executadas as seeds 42–61, totalizando:

- 20 seeds;
- 7 composições;
- 3 níveis de fluxo;
- **420 execuções**.

Resultado da validação:

- **420/420 execuções concluídas**;
- **0 colisões**;
- nenhum congestionamento persistente até 1800 s.

As frenagens emergenciais observadas foram mantidas como diagnóstico e não constituíram critério automático de invalidação.

## Padrão preliminar observado

Os três níveis de fluxo apresentaram regimes distintos:

- 300 veículos: circulação predominantemente livre, com baixos tempos de espera;
- 450 veículos: nível intermediário, com maior interação entre veículos e aumento moderado das perdas;
- 625 veículos: rede mais carregada, com aumento claro de espera e `timeLoss`, porém mantendo estabilidade nas 20 seeds utilizadas.

Também foram observadas diferenças mensuráveis entre as composições de perfis, especialmente no fluxo alto. Esses resultados ainda não constituem a análise final do trabalho.

## Limitações conhecidas

Permanece uma limitação visual relacionada à mudança de faixa antecipada em determinados trechos, especialmente no corredor da Rua da Caixa Econômica em direção à Praça/Nicolau Cavon. Alguns veículos ocupam antecipadamente a faixa necessária para sua rota, deixando a faixa adjacente menos utilizada do que ocorre no trânsito real.

Foram realizados testes com `lcStrategic` e `lcStrategicLookahead`, mas as alterações globais não produziram melhora visual suficiente para justificar sua adoção e, em alguns casos, introduziram instabilidade. A configuração-base mantém esses parâmetros sem novos ajustes globais.

A demanda é qualitativa e simplificada, construída a partir de conhecimento local e verificações de plausibilidade, não constituindo calibração empírica do trânsito real.

## Próximos passos

1. Preservar esta configuração como baseline reprodutível.
2. Caso sejam executadas novas seeds, manter os mesmos parâmetros e níveis de fluxo.
3. Avaliar uma análise de sensibilidade dos perfis, aumentando de forma controlada a distância entre parâmetros cauteloso/normal/agressivo.
4. Executar qualquer variante de perfil em arquivos e diretórios separados, sem sobrescrever o baseline.
5. Comparar as variantes com a configuração-base antes de decidir se alguma alteração deve integrar o experimento principal.
6. Após o fechamento dos perfis, consolidar as métricas finais, gráficos e análise dos resultados.

## Observação metodológica

Qualquer ampliação da diferença entre os perfis deverá ser tratada inicialmente como **teste de sensibilidade**, e não como substituição automática da configuração-base. A eventual adoção de novos valores deverá ser justificada pelos efeitos observados e pela coerência com a fundamentação teórica e com o objetivo aprovado do trabalho.
