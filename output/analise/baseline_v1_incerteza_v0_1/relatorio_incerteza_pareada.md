# Incerteza das diferenças médias pareadas - versão 0.1

**Status:** etapa exploratória calculada após a análise descritiva. Não é pré-registro nem aprovação metodológica do orientador. O método não altera a simulação congelada.

## Método

Desfecho: tempo médio de viagem por execução. Para cada seed/demanda, diferença = cenário - REF. Estimando: média dessas diferenças sob as condições fixas do modelo. Foram mantidos todos os 30 pares em cada contraste.

Bootstrap não paramétrico por blocos de seed, 100.000 reamostragens de tamanho 30 com reposição. IC bilateral marginal de 95%, método BCa. Gerador: NumPy default_rng, seed de análise 20261014; essa seed não é uma das seeds de simulação. Implementação: scipy.stats.bootstrap.

A matriz 18 × 30 é reamostrada pela dimensão das seeds com os mesmos índices em todos os contrastes. Isso preserva correspondências entre composições e demandas. A inferência pressupõe realizações de seed adequadas como repetições da variabilidade do modelo. Não representa incerteza de calibração ao trânsito real.

Os ICs não foram corrigidos para as 18 comparações: não fornecem cobertura simultânea de 95% do conjunto nem uma declaração conjunta de significância. Não foram calculados p-valores. IC que inclui zero não comprova equivalência ou ausência de efeito.

## Resultados

| Demanda | Cenário | Diferença média (s) | IC95% BCa marginal (s) |
|---|---|---:|---|
| 300 | EQU | 1,202 | [1,013; 1,377] |
| 300 | CAU | 6,145 | [5,966; 6,301] |
| 300 | AGR | -5,006 | [-5,191; -4,849] |
| 300 | MIX_C | 4,917 | [4,716; 5,090] |
| 300 | MIX_N | 0,849 | [0,687; 0,994] |
| 300 | MIX_A | -2,569 | [-2,789; -2,334] |
| 450 | EQU | 0,359 | [-0,017; 0,719] |
| 450 | CAU | 6,505 | [6,067; 7,069] |
| 450 | AGR | -6,229 | [-6,701; -5,746] |
| 450 | MIX_C | 4,765 | [4,343; 5,194] |
| 450 | MIX_N | 0,430 | [0,005; 0,852] |
| 450 | MIX_A | -3,883 | [-4,359; -3,408] |
| 625 | EQU | -4,977 | [-9,214; -2,747] |
| 625 | CAU | 9,579 | [7,302; 12,828] |
| 625 | AGR | -14,192 | [-17,066; -12,426] |
| 625 | MIX_C | 1,888 | [-2,091; 4,195] |
| 625 | MIX_N | -3,102 | [-6,036; -0,998] |
| 625 | MIX_A | -12,022 | [-17,257; -9,780] |

## Leitura e limitações

AGR e MIX_A têm ICs marginais abaixo de zero nas três demandas. EQU/450 e MIX_C/625 têm ICs atravessando zero. Em MIX_N/450, o limite inferior fica a poucos milésimos de segundo do zero; a diferença é pequena e não deve ser apresentada como conclusão firme, especialmente sem tratar multiplicidade.

As diferenças altas e as execuções congestionadas permanecem nos cálculos. BCa ajusta os quantis para viés e assimetria na aproximação bootstrap; isso não elimina limitações de amostra de 30 seeds ou garante cobertura exata.

Foi feita uma verificação computacional independente com seed 20261015, mantendo B=100.000. A maior mudança de limite foi 0,038 s. Os resultados principais permanecem os da seed previamente registrada; a verificação não é usada para escolher limites mais favoráveis. Cem mil reamostragens não aumentam n: continuam sendo 30 pares, não 100.000 execuções experimentais.

## Fonte e reprodução

https://docs.scipy.org/doc/scipy-1.17.0/reference/generated/scipy.stats.bootstrap.html

A documentação descreve BCa e reamostragem pareada. A escolha de usá-los nesta etapa, de 95% e de B=100.000 é uma decisão analítica aqui registrada. A precisão Monte Carlo observada é verificada separadamente da incerteza entre seeds.

O manifesto registra versões, parâmetros e hashes. Para reproduzir, usar o script scripts/estimar_incerteza_pareada.py do repositório com uma pasta de saída nova. Nenhuma nova simulação é necessária.
