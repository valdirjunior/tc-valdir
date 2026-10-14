# Checkpoint da análise oficial - 14/10/2026

Este documento é o ponto de entrada para os chats de análise, escrita e controle do TC. Registra o estado alcançado, os caminhos canônicos e as decisões que ainda não estão fechadas. Não pressupõe que a conversa de outro chat contenha os detalhes desta etapa.

## Experimento e alcance

- Tema: impacto de comportamentos de motoristas no tráfego urbano simulado, entorno da Praça Nereu Ramos, Videira/SC.
- Simulação congelada e coleta definitiva concluída. Não recalibrar rede, perfis ou demanda em função dos resultados.
- 30 seeds, 1000 a 1029; demandas 300, 450, 625 programadas em [0,600); sete composições REF, EQU, CAU, AGR, MIX_C, MIX_N, MIX_A.
- 630 execuções; SUMO 1.27.1; passo 0,1 s; fim configurado em 1800 s; saídas de filas/summary em 1 s.
- A demanda é compartilhada entre composições dentro da mesma seed/demanda; preservar o pareamento. Veículos não são repetições experimentais independentes.
- A coleta integral passou pelo consolidador local: 630 OK, zero erros/avisos; 288.750 viagens nas execuções; 120 eventos de frenagem; zero colisões/teleportes.
- A base recebida, seus hashes, cobertura e invariantes foram conferidos. A inspeção direta prévia dos XML aqui abrangia três execuções de REF/seed 1000. Não afirmar que os 630 conjuntos foram reenviados e reexecutados pelo assistente.

## Caminhos canônicos

| Item | Caminho |
|---|---|
| Dados brutos congelados | `output/experimento_final/baseline_v1/` |
| Protocolo atual de extração | `docs/Protocolo_metricas_SUMO_v0_2.md` |
| Consolidador | `scripts/consolidar_experimento.py` |
| Base oficial, 630 linhas | `output/analise/baseline_v1_consolidado_v1/base_execucoes.csv` |
| Dicionário de campos | `output/analise/baseline_v1_consolidado_v1/dicionario_metricas.csv` |
| Validação e manifesto | Mesma pasta de consolidação |
| Análise descritiva e reprodução | `scripts/analisar_descritivamente.py` |
| Relatório descritivo | `output/analise/baseline_v1_descritiva_v1/Analise_Descritiva_SUMO_v1.pdf` |
| Tabelas e gráficos descritivos | `output/analise/baseline_v1_descritiva_v1/tabelas/` e `graficos/` |
| ICs bootstrap exploratórios | `scripts/estimar_incerteza_pareada.py` |
| Resultados de incerteza | `output/analise/baseline_v1_incerteza_v0_1/` |

O protocolo v0.1 é histórico. Para a análise atual, consultar v0.2 e os manifestos de cada etapa. O fim em 1800 s não é o tempo de limpeza da rede: esse tempo vem da última chegada. A tabela completa de filas por faixa permanece na pasta de consolidação do pesquisador; não precisou ser reenviada para as comparações globais.

## Métricas e cuidados de interpretação

- Tempo médio de viagem: média de `duration`; desfecho central proposto.
- Velocidade: média de `routeLength/duration` por veículo. A razão entre as somas é outra agregação, registrada como complemento.
- Tempo parado: média de `waitingTime`, incluindo zeros e seguindo o acumulador do SUMO; não confundir com todo tempo em trânsito lento.
- Filas: estatísticas dos comprimentos exportados, com faixas externas e internas. Soma em metros agregados não é uma fila contínua única. `queueing_time` não é soma de esperas das viagens.
- Vazão: conclusões em [0,600)/600 ×3600; não é geração de demanda, capacidade máxima ou vazão estacionária.
- Complementos: atraso de inserção, tempo de sistema, drenagem, perdas de tempo e frenagens. `timeLoss` depende do referencial de velocidade ideal individual.
- Janelas de fila: [0,600) e [0,1800), identificadas separadamente. Incluir os zeros válidos; não converter lacunas de arquivos em zero.

## Resultados descritivos já obtidos

Nenhuma seed foi excluída. Médias, DP amostral entre seeds, medianas, quartis, valores extremos, diferenças absolutas pareadas e percentuais foram calculados.

- AGR e MIX_A tiveram menor tempo médio que REF nos 30 pares de cada demanda.
- Na demanda 625, diferenças médias ante REF: AGR -14,192 s; MIX_A -12,022 s; EQU -4,977 s; CAU +9,579 s; MIX_C +1,888 s; MIX_N -3,102 s.
- Os contrastes são mais variáveis e assimétricos na demanda 625. Extremos plausíveis permanecem na análise.
- MIX_A tem tempo de viagem maior que AGR em 625, mas menor tempo parado e menor soma média de filas. Não existe ordenação única por todas as métricas.
- Os perfis variam conjuntos de parâmetros, incluindo velocidade desejada. Não atribuir uma diferença a um único parâmetro nem extrapolar automaticamente ao trânsito real.

## Incerteza: etapa atual, ainda exploratória

Foi calculado IC bilateral BCa de 95% para a média das 30 diferenças pareadas, em cada um dos 18 contrastes de tempo de viagem. Reamostragem por blocos de seed, B=100.000, seed computacional 20261014. Uma segunda seed, 20261015, foi usada somente para conferir estabilidade Monte Carlo; a maior mudança de limite foi cerca de 0,038 s. Os limites principais não foram escolhidos em função dessa conferência.

Os ICs são marginais, não simultâneos. Não há p-valores ou ajuste para as 18 comparações, e a multiplicidade continua pendente. A etapa não constitui pré-registro ou aprovação do orientador. BCa foi adotado como proposta de avaliação de incerteza após a leitura descritiva.

Em EQU/450 e MIX_C/625, os ICs marginais atravessam zero. MIX_N/450 tem limite inferior muito próximo de zero. Não concluir equivalência quando um intervalo contém zero nem declarar confirmação conjunta a partir dos 18 intervalos individuais.

## Próximos passos

1. Versionar esta entrega e apontar os demais chats para este checkpoint.
2. Definir o procedimento inferencial final e o tratamento da multiplicidade, se houver testes confirmatórios.
3. Decidir quais métricas complementares e gráficos serão utilizados no texto final, preservando as cinco previstas no PTC.
4. Se for feita análise espacial, consultar `filas_por_faixa.csv`; não inferir persistência localizada apenas do ID do máximo.
5. Transportar escolhas e resultados para o chat de escrita somente com nomes, unidades, janelas e limitações consistentes com estes arquivos.

O texto oficial do TCC não foi reescrito nesta etapa. Todos os resultados se referem ao modelo simplificado e aos perfis parametrizados, não a uma calibração empírica de motoristas de Videira.
