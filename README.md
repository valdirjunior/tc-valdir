# TC - Valdir

Projeto de Trabalho de Conclusão de Curso em Ciência da Computação,
desenvolvido no Instituto Federal Catarinense (IFC), Campus Videira.

## Tema

Análise do impacto de comportamentos de motoristas no tráfego urbano
por meio de simulação computacional.

## Ferramentas

- SUMO (Simulation of Urban MObility)
- Python
- Visual Studio Code

## Área de estudo

Entorno da Praça Nereu Ramos, em Videira/SC.

## Estrutura do projeto

- `mapa/`: dados geográficos de origem.
- `config/`: rede viária oficial e configurações da simulação.
- `referencia/`: rede originalmente importada, preservada para comparação.
- `scripts/`: scripts de automação e processamento.
- `output/`: arquivos gerados durante as simulações.

## Estado atual

Coleta oficial concluída e consolidada. Análise descritiva finalizada; avaliação inicial de incerteza pareada disponível. Procedimento inferencial final em discussão.

## Analise dos resultados

Estado e caminhos atuais: [checkpoint da analise](docs/checkpoint-analise-2026-10-14.md).
Organizacao e reproducao: [guia das analises](docs/README-analises.md).
Scripts em scripts/; entregas oficiais versionadas em output/analise/.


## Avaliacao estatistica do tempo de viagem

Procedimento e resultados atuais: [checkpoint estatistico](docs/checkpoint-estatistica-viagem-2026-10-14.md).
ICs simultaneos aproximados para 18 contrastes; etapa exploratoria, com todas as 30 seeds.


## Analise espacial das filas

Localizacao e comparacoes descritivas: [checkpoint espacial](docs/checkpoint-filas-espacial-2026-10-14.md).
Todas as 630 execucoes e 198 faixas preservadas; nomes com origem documentada.
