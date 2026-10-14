# Avaliação dos contrastes médios de viagem - versão 1.0

**Status:** procedimento adotado nesta etapa exploratória, após a descritiva e após pilotos de viabilidade. Não é pré-registro, validação de campo ou aprovação do orientador.

## Método e alcance

Estimando: média entre seeds da diferença cenário - REF do tempo médio de viagem por execução. Família única de 18 contrastes (seis composições × três demandas). Todos os 30 pares foram preservados.

Foi usado bootstrap max-t studentizado em uma etapa, com os mesmos índices de seed nos 18 contrastes. O máximo absoluto é calibrado no quantil 0,95; o erro padrão é recalculado em cada amostra. Os intervalos têm cobertura conjunta nominal aproximada de 95%, sob pressupostos de repetição independente dos vetores de seed, momentos adequados e aproximação bootstrap. Não são intervalos BCa corrigidos nem o procedimento stepdown completo.

B=1,000,000; RNG default_rng; seed principal 20261016, conferência 20261017; quantil com interpolação `higher`. Crítico principal = 3.722934447; conferência = 3.723686534. Amostras com erro padrão zero: 0 na principal, 0 na conferência; nenhuma foi removida.

Fonte do procedimento geral: Romano e Wolf (2005), seções 4 e 5 e apêndice B.1. O protocolo do repositório explicita a adaptação a médias de diferenças de simulação.

https://users.ssc.wisc.edu/~behansen/718/RomanoWolf2005.pdf

## Resultados

| Demanda | Cenário | Diferença média (s) | IC simultâneo nominal 95% (s) |
|---|---|---:|---|
| 300 | EQU | 1,202 | [0,850; 1,554] |
| 300 | CAU | 6,145 | [5,822; 6,469] |
| 300 | AGR | -5,006 | [-5,335; -4,678] |
| 300 | MIX_C | 4,917 | [4,557; 5,278] |
| 300 | MIX_N | 0,849 | [0,551; 1,146] |
| 300 | MIX_A | -2,569 | [-3,008; -2,129] |
| 450 | EQU | 0,359 | [-0,352; 1,070] |
| 450 | CAU | 6,505 | [5,552; 7,458] |
| 450 | AGR | -6,229 | [-7,153; -5,305] |
| 450 | MIX_C | 4,765 | [3,945; 5,585] |
| 450 | MIX_N | 0,430 | [-0,389; 1,250] |
| 450 | MIX_A | -3,883 | [-4,802; -2,964] |
| 625 | EQU | -4,977 | [-10,730; 0,776] |
| 625 | CAU | 9,579 | [4,386; 14,772] |
| 625 | AGR | -14,192 | [-18,446; -9,938] |
| 625 | MIX_C | 1,888 | [-3,846; 7,621] |
| 625 | MIX_N | -3,102 | [-7,836; 1,632] |
| 625 | MIX_A | -12,022 | [-18,261; -5,784] |

## Interpretação

5 dos 18 intervalos atravessam zero. Isso não comprova equivalência. AGR e MIX_A apresentam diferenças negativas com intervalos abaixo de zero nas três demandas. CAU e MIX_C/300-450 apresentam diferenças positivas; MIX_C/625 atravessa zero. EQU/450-625 e MIX_N/450-625 também atravessam zero; em 300 seus intervalos ficam acima de zero.

Essas conclusões se referem ao tempo de viagem dos perfis parametrizados na rede simplificada. Não são recomendação de agressividade real. A classificação decorre dos ICs simultâneos deste procedimento aproximado, e não de uma garantia exata com 30 seeds.

## Conferência e influência

A maior mudança de limite ao repetir o cálculo com a segunda seed foi 0,001 s; 0 classificações de inclusão de zero mudaram. A estabilidade Monte Carlo mede a execução numérica, não a cobertura estatística real.

As 540 verificações leave-one-out são diagnósticos de influência aritmética. A estimativa oficial e seus intervalos usam todas as seeds; nenhum resultado reduzido substitui a base integral. O resumo informa quais seeds mais deslocam cada média.

O diagnóstico BCa/Bonferroni usa o piloto anterior B=100.000 para avaliar quantis ajustados. Em MIX_A/625 a cauda exigida corresponde a cerca de nove observações esperadas mesmo com B=2.000.000. Esse foi um motivo computacional para não publicar essa combinação como solução da multiplicidade.

## Métricas complementares

A tabela complementar contém 126 resumos pareados: velocidade, tempo parado, filas, vazão, atraso de inserção, tempo de sistema e drenagem. São descritivos, sem IC/teste. Não pertencem à família inferencial de 18 contrastes de viagem.

Tempo de sistema foi reconciliado por seed como duração + atraso de inserção. Vazão refere-se à janela [0,600), filas a metros agregados na mesma janela. A versão integral de todas as métricas permanece na descritiva anterior.

## Limitações e continuidade

n=30 permanece uma amostra limitada. A reamostragem não representa erro de calibração ao mundo real e não garante capturar situações raras ausentes na coleta. Assimetria e influência de extremos motivam cautela. Um método posterior à inspeção dos dados permanece exploratório mesmo que trate multiplicidade.

Não foram calculados p-valores, todos os pares entre composições, novos contrastes entre demandas ou limiares retrospectivos de relevância prática. A recomendação para a escrita é reportar magnitude, intervalo e contexto das outras métricas. Novas perguntas exigem registrar outra família/etapa.
