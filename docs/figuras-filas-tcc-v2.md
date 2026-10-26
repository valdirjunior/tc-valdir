# Figuras espaciais de filas para o TCC - apresentação v2

Data: 25/10/2026. Esta entrega atualiza somente a apresentação das figuras identificadas no LaTeX por `fig:filas-faixas-625` e `fig:mapa-filas-ref625`, atualmente Figuras 5 e 6.

## Estado consultado no GitHub

- Texto: `valdirjunior/tc-valdir-texto`, commit `e800e1f6cca6c95605e7a7e3aaaf72373ed87aa7`.
- Projeto/análise: `valdirjunior/tc-valdir`, commit `2eb4fd70d767650541c43ab3c8728d7fe16995ab`.
- Lidos os checkpoints de análise e análise espacial de 14/10, o capítulo atual, as chamadas das figuras e o script espacial.
- Os PNGs atualmente usados no texto são idênticos aos PNGs do pacote espacial v1, conforme os hashes de objetos Git. Os resumos e metadados locais também coincidem com os arquivos publicados nesses commits.

Esta entrega foi preparada sem modificar os repositórios remotos. Os checkpoints de 14/10 são históricos; não se retomou nem alterou o procedimento estatístico de outras etapas.

## O que mudou

### Figura 5

- Mesmas dez faixas, na mesma ordem, e mesmas sete composições.
- IDs técnicos substituídos por nomes de vias ou descrições dos movimentos.
- Duas faixas da Rua Vitória distinguidas por seus destinos: sentido Rua Nicolau Cavon e conversão para a praça. Não foram somadas nem tratadas como uma única faixa.
- Ligações internas descritas como Rua Vitória para Rua Nicolau Cavon e Praça Nereu Ramos para Rua Pedro Andreazza. As conexões foram verificadas no snapshot congelado.
- Fonte maior, grade branca discreta, valores com duas casas e destaque para REF como coluna de referência.
- Paleta sequencial azul, com cor do texto escolhida pelo contraste de luminância de cada célula. O destaque de REF não indica significância estatística.

### Figura 6

- Mesmo cenário REF/625, mesma janela [0,600) e média das mesmas 30 execuções.
- Mesmas geometrias e valores das 198 faixas: 94 externas e 104 internas.
- Os seis marcadores continuam identificando as mesmas seis faixas externas destacadas no mapa original. São referências visuais, não IDs de rede.
- Removidos IDs técnicos, eixos de coordenadas locais e texto técnico extenso.
- Nomes legíveis e valores em uma legenda compacta, hierarquia tipográfica e uma escala de distância de 100 m.
- Orientação e proporções da geometria preservadas.

Nos dois gráficos, a normalização continua linear a partir de zero, com os máximos originais de cada figura: 23,3509677778 m na comparação e 23,300025 m no mapa. Não houve escala logarítmica, recorte de valores baixos, suavização ou transformação das médias.

Os PDFs são vetoriais, com fontes incorporadas e sem imagens raster embutidas. PNGs de 320 dpi e SVGs também estão incluídos.

## Preservação dos resultados

O gerador lê exclusivamente `resumo_por_faixa.csv`, `metadados_faixas.csv` e o manifesto já publicados. Confere seus hashes antes de desenhar. Não relê os 249.480 registros brutos nem recalcula as médias.

As verificações independentes confirmaram:

- igualdade numérica dos 70 valores da comparação;
- igualdade numérica dos 198 valores do mapa;
- manutenção das faixas, composições, seleção e ordem;
- correspondência dos novos rótulos de movimento com as conexões da rede congelada;
- ausência de IDs técnicos nos textos dos PDFs;
- ausência de cortes de texto e revisão visual dos PDFs renderizados;
- entradas preservadas.

Os três CSVs com sufixo `APOIO` mantêm a ligação entre IDs, rótulos e valores para rastreabilidade interna. Eles não devem ser transformados em rótulos da figura principal.

## Arquivos e organização

No repositório de análise:

- `scripts/gerar_figuras_filas_tcc.py`: nova versão dedicada da etapa gráfica, separada do consolidador e da análise completa.
- `config/analise/rotulos_figuras_filas_tcc.json`: nomes editoriais e sua correspondência com IDs.
- `output/analise/baseline_v1_figuras_filas_tcc_v2/`: imagens, apoio interno e manifesto.
- `atualizar_gitignore_figuras_v2.patch`: inclusão de uma exceção para versionar a nova pasta de figuras.

O script `analisar_filas_espacialmente.py` original foi revisado e preservado. O novo gerador evita executar novamente suas etapas de consolidação, agregação e contrastes apenas para redesenhar imagens.

No repositório de texto:

- `tc/images/resultado_filas_faixas_625_v2.pdf`;
- `tc/images/resultado_mapa_filas_ref625_v2.pdf`;
- `atualizar_figuras_filas_v2.patch`: altera apenas os dois caminhos em `tc/conteudo/resultados_discussao.tex`.

As legendas, os labels, a ordem das figuras, os números e as conclusões do capítulo são preservados. Nenhum pacote LaTeX adicional é necessário para usar esses PDFs com o compilador PDF já utilizado.

### Atualização manual do LaTeX

~~~latex
\includegraphics[width=\textwidth]{images/resultado_filas_faixas_625_v2.pdf}

\includegraphics[width=\textwidth]{images/resultado_mapa_filas_ref625_v2.pdf}
~~~

Copiar os PDFs da pasta de texto do pacote para `tc/images/` e trocar as chamadas antigas por essas duas. O patch é uma alternativa à edição manual, não uma segunda alteração obrigatória.

### Reprodução opcional

As figuras estão prontas. Para reproduzir depois, com os arquivos copiados para `tc-valdir` e as dependências NumPy, pandas e Matplotlib disponíveis:

~~~powershell
python .\scripts\gerar_figuras_filas_tcc.py --saida .\output\analise\baseline_v1_figuras_filas_tcc_v2_reproducao
~~~

O programa exige uma pasta de saída nova para preservar as versões já existentes. Não executa Git nem SUMO.

Para versionar a saída v2, o patch de `.gitignore` acrescenta somente:

~~~gitignore
# Figuras espaciais para o TCC - apresentacao v2
!output/analise/baseline_v1_figuras_filas_tcc_v2/
~~~

## Revisão textual leve, opcional

Não foi aplicada ao capítulo, para manter a entrega principal limitada às imagens. Três ajustes de redação possíveis no texto consultado:

1. Abertura da seção espacial: pode ser reduzida a “Para localizar a retenção descrita pelo indicador global, analisou-se a extensão média de fila por faixa nas mesmas 30 execuções, incluindo as faixas internas e externas consideradas na análise.”
2. Na discussão, “características de condução não devem ser representadas de forma adequada por um único indicador isolado” tem construção ambígua. Uma formulação mais precisa é “a aceleração isolada não basta para caracterizar a agressividade”, mantendo a referência a Makridis.
3. O parágrafo iniciado por “Os resultados obtidos dialogam ainda com a ideia de heterogeneidade” retoma Zhai e Makridis já discutidos na mesma seção. Pode ser suprimido ou integrado aos parágrafos anteriores, sem retirar achados.

Essas sugestões não mudam resultados, recorte ou conclusões. A aplicação e a conferência da paginação ficam no fluxo do chat de escrita.

