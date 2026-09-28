# Checkpoint do TC — Simulação no SUMO

**Data:** 28/09/2026

## Situação atual

A rede de simulação baseada no entorno da Praça Nereu Ramos, em Videira/SC, já está funcional no SUMO.

Nesta etapa foram realizados ajustes manuais no NetEdit, incluindo sentidos de circulação, conexões entre faixas, prioridades, geometria de alguns trechos e velocidades das vias.

Os limites de velocidade utilizados atualmente estão entre **40 km/h e 50 km/h**, conforme o trecho da rede.

Também já é possível executar as simulações sem utilizar a interface gráfica, gerando automaticamente arquivos com métricas e informações individuais das viagens.

## Testes preliminares da rede

Foram executados dois testes de carga utilizando tráfego gerado pelo `randomTrips.py`.

| Métrica | 300 veículos | 600 veículos |
|---|---:|---:|
| Distância média da viagem | 600,19 m | 597,83 m |
| Velocidade média | 10,68 m/s (38,4 km/h) | 8,11 m/s (29,2 km/h) |
| Duração média da viagem | 58,05 s | 101,24 s |
| Tempo médio parado | 1,65 s | 26,36 s |
| Time loss médio | 8,31 s | 51,65 s |
| Atraso médio de inserção | 0,29 s | 7,67 s |
| Teleports | 0 | 0 |
| Colisões | 0 | 0 |
| Frenagens de emergência | 0 | 0 |

O teste com 300 veículos apresentou tráfego relativamente estável. Com 600 veículos já foi possível observar aumento significativo de congestionamento, tempo de viagem e tempo parado, mas a rede continuou funcionando sem teleports ou colisões.

## Observação sobre a demanda

A demanda utilizada nesses testes ainda é aleatória e tem finalidade de **validação técnica da rede**, não de representar fielmente o trânsito real de Videira.

Durante os testes foi identificado que a geração totalmente aleatória pode atribuir tráfego excessivo a vias que possuem pouco fluxo na realidade.

Por isso, a próxima etapa deverá considerar uma distribuição de demanda que dê maior participação às vias principais e menor participação às vias secundárias.

## Próximas etapas

- discutir e definir a distribuição dos fluxos de veículos;
- definir os parâmetros dos perfis cauteloso, normal e agressivo;
- estruturar os cenários experimentais;
- automatizar as execuções com Python;
- executar múltiplas repetições utilizando sementes controladas;
- coletar e consolidar as métricas para análise.

A interface gráfica do SUMO deverá ser utilizada principalmente para inspeção visual e demonstração, enquanto as execuções em maior quantidade poderão ser realizadas automaticamente em segundo plano.