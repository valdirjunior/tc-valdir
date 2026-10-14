# Checkpoint: avaliação estatística do tempo de viagem

Data: 14/10/2026. Complementa os checkpoints de análise e fundamentação, cuja publicação o pesquisador informou ter concluído.

## Procedimento adotado nesta etapa

- Família única: 18 diferenças médias ante REF, seis composições × três demandas.
- Unidade de reamostragem: vetor de seed com os 18 contrastes; todas as 30 seeds mantidas.
- ICs simultâneos bilaterais, nível conjunto nominal de 95%, bootstrap studentizado max-t em uma etapa, B=1.000.000.
- Cobertura aproximada, condicionada aos pressupostos; estágio exploratório posterior à descritiva e a pilotos. Sem p-valores, sem stepdown e sem alegação de aprovação do orientador.

O procedimento está documentado no [protocolo estatístico v1.0](protocolo-estatistico-viagem-v1_0.md). Seus pressupostos e limites precisam acompanhar a escrita. O protocolo é o procedimento usado, não um plano anterior à coleta.

## Resultados principais

Crítico max-t: 3,722934447. Segunda seed: 3,723686534. Maior mudança de limite: cerca de 0,00126 s; nenhuma classificação de inclusão de zero mudou. Nenhuma reamostragem teve erro padrão zero.

AGR e MIX_A têm diferenças negativas com intervalos abaixo de zero nas três demandas; CAU tem diferenças positivas com intervalos acima de zero nas três. EQU/300, MIX_C/300-450 e MIX_N/300 ficam acima de zero.

Cinco intervalos incluem zero: EQU/450, MIX_N/450, EQU/625, MIX_C/625 e MIX_N/625. Não interpretar isso como equivalência. Em 625, AGR tem diferença média -14,192 s, IC [-18,446; -9,938]; MIX_A tem -12,022 s, IC [-18,261; -5,784].

Algumas classificações diferem das obtidas com os BCa marginais anteriores. Os novos limites mudam tanto o tratamento da simultaneidade quanto o procedimento de construção, portanto não isolar esses mecanismos sem análise adicional.

## Complementos e diagnósticos

Há 126 resumos descritivos de diferenças para as outras quatro métricas do PTC mais atraso de inserção, tempo de sistema e drenagem. Eles não pertencem à família inferencial de viagem. Tempo de sistema foi reconciliado como duração + atraso por seed.

Os 540 cálculos leave-one-out são diagnósticos de influência; não substituem as estimativas integrais. A seed 1027 mais influencia cinco dos seis contrastes de viagem em 625; em CAU/625 a maior influência é da seed 1014. Nenhuma foi excluída.

O arquivo de viabilidade BCa/Bonferroni explica por que não foi publicada essa combinação: quantis muito extremos em contrastes assimétricos. Não constitui validação de cobertura do método adotado.

## Caminhos canônicos e continuidade

| Item | Caminho |
|---|---|
| Procedimento | `docs/protocolo-estatistico-viagem-v1_0.md` |
| Script | `scripts/avaliar_contrastes_viagem.py` |
| ICs e relatório | `output/analise/baseline_v1_estatistica_v1/` |
| Referências adicionais | `docs/referencias-estatistica-viagem.bib` |
| Instalação e reprodução | `docs/README-estatistica-viagem.md` |

A simulação e o texto final do TCC não foram modificados. O chat de escrita pode utilizar esta etapa, mantendo a distinção entre evidência exploratória do modelo, relevância prática e comportamento real. A análise espacial de filas e eventuais contrastes entre demandas permanecem escopos adicionais, não resultados desta entrega.
