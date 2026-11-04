# TC — Simulação de comportamento de motoristas no tráfego urbano

Repositório técnico do Trabalho de Conclusão de Curso em Ciência da Computação do Instituto Federal Catarinense (IFC) — Campus Videira.

**Tema:** Análise do impacto de comportamentos de motoristas no tráfego urbano por meio de simulação computacional.

O estudo utiliza o **SUMO (Simulation of Urban MObility)** para comparar perfis sintéticos de motoristas em um cenário urbano simplificado baseado no entorno da Praça Nereu Ramos, em Videira/SC.

## Experimento final

O delineamento utilizado no TC combina:

- 3 perfis de condução: cauteloso, normal e agressivo;
- 7 composições de perfis;
- 3 níveis de demanda: 300, 450 e 625 veículos;
- 30 sementes pseudoaleatórias (1000–1029);
- 630 execuções no total.

Para cada combinação de semente e demanda, a mesma realização de viagens é reutilizada entre as sete composições, preservando o pareamento dos cenários.

A análise final do TC é **descritiva** e considera tempo médio de viagem, velocidade média, tempo parado, filas e vazão, além de uma análise espacial das filas por faixa.

## Estrutura do repositório

- `config/`: rede viária final, configurações de demanda, perfis e arquivos auxiliares.
- `mapa/`: dados geográficos de origem utilizados na construção do cenário.
- `referencia/`: versões preservadas da rede para comparação e rastreabilidade.
- `scripts/`: scripts de geração, execução, validação, consolidação e análise.
- `testes/`: testes automatizados do processo de consolidação e análise.
- `output/analise/`: resultados consolidados e produtos de análise selecionados para versionamento.
- `docs/`: documentação técnica, protocolos, checkpoints e registros de desenvolvimento.

## Pipeline principal

Os principais arquivos associados ao experimento final são:

- `scripts/gerar_demanda_v2.py` — geração da demanda sintética;
- `scripts/atribuir_perfis.py` — atribuição das composições de perfis;
- `scripts/executar_experimento_final.ps1` — execução automatizada da matriz experimental;
- `scripts/validar_experimento_final_rapido.ps1` — verificação estrutural da coleta;
- `scripts/consolidar_experimento.py` — consolidação das 630 execuções;
- `scripts/analisar_descritivamente.py` — análise descritiva;
- `scripts/analisar_filas_espacialmente.py` — análise espacial das filas;
- `scripts/gerar_figuras_filas_tcc.py` — geração das figuras espaciais utilizadas no TC.

A coleta bruta do experimento final é volumosa e não é integralmente versionada no GitHub. Os resultados consolidados e materiais selecionados para análise estão em `output/analise/`.

## Reprodução da análise

Com a coleta oficial disponível em `output/experimento_final/baseline_v1/`, a consolidação pode ser executada com:

```powershell
python .\scripts\consolidar_experimento.py --entrada .\output\experimento_final\baseline_v1 --saida .\output\analise\nova_consolidacao
```

A análise descritiva pode ser reproduzida a partir da consolidação:

```powershell
python .\scripts\analisar_descritivamente.py --entrada .\output\analise\baseline_v1_consolidado_v1\resultados_consolidacao.zip --saida .\output\analise\nova_descritiva
```

A documentação detalhada das métricas e da consolidação está em:

- `docs/Protocolo_metricas_SUMO_v0_2.md`;
- `docs/README_consolidacao.md`;
- `docs/README-analises.md`;
- `docs/README-filas-espacial.md`.

## Materiais históricos e exploratórios

O repositório preserva checkpoints, scripts de testes preliminares e algumas análises exploratórias produzidas durante o desenvolvimento. Esses materiais documentam decisões e verificações realizadas ao longo do projeto, mas **não substituem o pipeline final descrito acima**.

Em particular, arquivos relacionados a estimativas de incerteza ou avaliação estatística foram etapas exploratórias e **não fazem parte da análise final apresentada no TC**, que permaneceu descritiva.

## Escopo

O cenário é uma representação simplificada de uma região urbana real. A demanda é sintética e os perfis de condução são abstrações computacionais, sem calibração empírica com dados de motoristas ou contagens de tráfego de Videira. Portanto, os resultados devem ser interpretados no contexto comparativo do experimento simulado.

## Ferramentas

- SUMO 1.27.1
- Python
- PowerShell
- NetEdit
- OpenStreetMap

## Autor

Valdir Rugiski Junior  
Ciência da Computação — IFC Campus Videira

Orientador: Prof. Fábio José Rodrigues Pinheiro
