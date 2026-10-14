# Protocolo estatístico do tempo médio de viagem - v1.0

Data: 14/10/2026. Procedimento adotado nesta etapa do TC. Esta versão é um registro posterior à descritiva, não pré-registro ou aprovação do orientador. A simulação permanece congelada e todos os resultados se referem ao modelo simplificado.

## Pergunta, unidade e família

Pergunta: qual a diferença de tempo médio de viagem entre cada composição e REF, mantendo a demanda e o bloco de seed?

Para seed s, demanda d e composição c, `D_s,d,c = Y_s,d,c - Y_s,d,REF`, onde Y é a média de `tripinfo.duration` nas viagens completas daquela execução. A estimativa é a média das 30 diferenças. Segundos são a unidade principal; uma diferença negativa significa menor tempo de viagem após inserção.

A família contém seis composições (EQU, CAU, AGR, MIX_C, MIX_N, MIX_A) em três demandas (300, 450, 625): 18 contrastes. REF é compartilhado. Não são grupos independentes e veículos não são repetições independentes do efeito da composição.

Um bloco de seed é o vetor completo das 18 diferenças. Reamostrar vetores mantém as correspondências entre composições e demandas. “Bloco” aqui não é trecho de uma série temporal; não há reamostragem de instantes ou veículos.

## Decisão e sustentação

Adota-se estimação de magnitude com intervalos simultâneos aproximados por bootstrap max-t studentizado, em uma etapa. Não se adota um procedimento stepdown. As outras métricas ficam descritivas nesta etapa, fora desta família inferencial.

Romano e Wolf (2005), seções 4-5 e apêndice B.1, fundamentam regiões conjuntas, padronização por erro padrão, reamostragem de vetores e extensão bilateral por máximo absoluto. Aqui essas ideias são adaptadas a médias de diferenças entre simulações. Sua teoria é assintótica, não garantia exata com 30 observações.

Fonte primária: https://users.ssc.wisc.edu/~behansen/718/RomanoWolf2005.pdf — algoritmo 4.2, pp. 1253-1254; extensão bilateral, p. 1256; bootstrap de Efron, p. 1275. DOI: 10.1111/j.1468-0262.2005.00615.x. Consulta: 14/10/2026.

DiCiccio e Efron (1996), seção 5, p. 199, apresentam o erro de estimação bootstrap dividido pelo erro padrão da respectiva amostra. Também discutem possíveis instabilidades do bootstrap-t. Essa base da padronização complementa a referência de simultaneidade.

https://www.math.wustl.edu/~kuffner/AlastairYoung/LeeYoung1996b.pdf

## Cálculo implementado

Denotar por j um dos 18 contrastes e n=30. Calcular a média `m_j` e o erro padrão `SE_j = SD_amostral(D_j)/sqrt(n)`, com divisor n-1 no SD.

Para cada uma das B reamostragens:

1. Sortear 30 índices de seed, com reposição e probabilidades iguais. Usar o mesmo vetor de índices nos 18 contrastes.
2. Calcular `m*_j` e `SE*_j` nessa amostra.
3. Calcular `T*_j = (m*_j - m_j)/SE*_j`.
4. Guardar `M* = max_j(abs(T*_j))`.

Usar `c = quantil_0.95(M*)` e publicar os intervalos `m_j ± c*SE_j`. A região conjunta é o produto desses 18 intervalos. A simetria em torno da estimativa vem da calibração pelo máximo absoluto; os dados não foram assumidos simétricos por isso.

Parâmetros computacionais desta entrega: B=1.000.000; NumPy `default_rng`; seed principal 20261016 e conferência 20261017; lotes de 1.000; quantil empírico com método `higher`. As seeds computacionais não são seeds de simulação.

SE zero em uma reamostragem recebe máximo infinito, sem descarte silencioso. Se o quantil final não for finito, a publicação deve parar. Não houve casos de SE zero na produção.

## Cobertura e leitura

O objetivo nominal é cobertura conjunta de 95% para os 18 efeitos, sob a aproximação bootstrap e os pressupostos. Não significa 95% de probabilidade posterior para um efeito fixo, nem 95% de garantia empírica demonstrada neste conjunto. Intervalo contendo zero não comprova equivalência.

A definição de cobertura simultânea distingue o evento de todos os intervalos cobrirem seus parâmetros dos eventos individuais. Ver também Stark, *Statistics 240 Lecture Notes*, seção 1.4: https://www.stat.berkeley.edu/~stark/Teach/S240/Notes/ch7.pdf .

Pressupostos: vetores das diferentes seeds adequados como repetições independentes do mesmo mecanismo gerador; variâncias positivas e momentos que permitam aproximação da distribuição das médias; aproximação bootstrap suficientemente boa. As dependências dentro do bloco são preservadas, não eliminadas. Seeds numericamente distintas, por si só, não são prova desses pressupostos.

n=30 permanece limitado, especialmente para eventos raros. Milhão de reamostragens reduz erro Monte Carlo; não acrescenta evidência experimental ou calibração de campo.

## Viabilidade avaliada e transparência da escolha

Antes da produção foram examinados dois pilotos: quantis BCa/Bonferroni com B=100.000 e max-t com B=100.000. Os resultados desses pilotos já eram conhecidos quando esta versão foi adotada; não atribuir à escolha caráter confirmatório.

Bonferroni exigiria nível individual `1 - 0.05/18 = 0.997222...` para cobertura conjunta nominal de 95%, se as coberturas individuais fossem adequadas. A desigualdade não depende de independência entre os intervalos, mas não corrige falhas de cobertura do método-base.

Fonte do princípio: NIST, *Bonferroni's method*: https://www.itl.nist.gov/div898/handbook/prc/section4/prc473.htm . A aplicação a BCa seria uma adaptação, não a fórmula ANOVA apresentada pelo NIST.

O diagnóstico mostrou que a assimetria de MIX_A/625 levaria o quantil inferior BCa a cerca de 0,0000044. Mesmo com dois milhões de reamostragens, isso corresponderia a cerca de nove amostras esperadas na cauda. Não foram publicados intervalos BCa/Bonferroni. Esse diagnóstico trata viabilidade numérica; não demonstra que max-t tenha cobertura perfeita ou seja universalmente superior.

Os ICs BCa marginais anteriores continuam como etapa exploratória histórica. A mudança atual inclui simultaneidade e padronização; diferenças nos limites não devem ser atribuídas apenas ao aumento de B ou isoladamente à correção de multiplicidade.

## Conferências e análises complementares

O cálculo de produção é repetido com outra seed para medir variação Monte Carlo. Os resultados oficiais permanecem os da principal. A conferência não é usada para escolher o intervalo mais favorável e não mede cobertura real.

As 540 médias leave-one-out medem influência aritmética. São diagnósticos, não resultados oficiais com 29 seeds. A base integral e todos os intervalos preservam as 30 seeds. Mudança de média, isoladamente, não torna uma seed inválida.

Velocidade individual média, tempo parado, filas e vazão mantêm suas definições e janelas do protocolo v0.2. Atraso de inserção, tempo de sistema e drenagem ajudam na interpretação. Seus 126 resumos de diferenças são descritivos e não recebem conclusões inferenciais simultâneas por estes intervalos.

Não foi calculado p-valor. A apresentação principal deve trazer magnitude, intervalo, contexto e limitações. Tampouco foi fixado limiar retrospectivo de relevância prática. Comparar efeitos entre demandas, outros pares de composições ou outras métricas com inferência exige registrar o escopo adicional.

## Reprodução e arquivos

Script: `scripts/avaliar_contrastes_viagem.py`, dependente do `scripts/estimar_incerteza_pareada.py` anterior. Resultados: `output/analise/baseline_v1_estatistica_v1/`. O manifesto registra entrada, versões, seeds, parâmetros, scripts e hashes. As referências adicionais estão em `docs/referencias-estatistica-viagem.bib`.
