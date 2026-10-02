# Classificação das entradas e saídas da rede

Classificação qualitativa utilizada durante a preparação da demanda.

Níveis:

- ALTA: via com participação importante no fluxo do cenário;
- MÉDIA: via com participação relevante, mas secundária em relação aos principais acessos;
- BAIXA: via com menor participação no fluxo geral.

Os níveis ainda não representam contagens reais de tráfego e serão utilizados inicialmente para testes de distribuição da demanda.

## Entradas

| Edge | Nível | Observação |
|---|---|---|
| `-102361495#0` | BAIXA | Rua Antônio Marafon |
| `-102361574.302` | BAIXA | Rua Osvaldo Cruz |
| `-103925179#1` | MÉDIA | Rua Brasil |
| `-1377929346#0` | ALTA | Rua Saul Brandalise |
| `320316411#0.175` | ALTA | Avenida Dom Pedro II |
| `99429224#2` | ALTA | Rua XV de Novembro |
| `99631677` | BAIXA | Rua Santa Catarina |
| `99643286#2` | MÉDIA | Rua XV de Novembro |

## Saídas

| Edge | Nível | Observação |
|---|---|---|
| `-99643286#2` | MÉDIA | Rua XV de Novembro |
| `102361495#0` | BAIXA | Rua Antônio Marafon |
| `102361574` | BAIXA | Rua Osvaldo Cruz |
| `103925179#1` | MÉDIA | Rua Brasil |
| `103925196#0` | BAIXA | Rua Padre Anchieta |
| `1377929346#0` | ALTA | Rua Saul Brandalise |
| `98384536#0` | ALTA | Rua Nicolau Cavon |
| `99429213#1` | MÉDIA | Rua Antônio Fávero  |

## Observações dos testes

A preencher após as primeiras simulações ponderadas.