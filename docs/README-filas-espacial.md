# Organização da análise espacial das filas

Os resultados já estão calculados e conferidos. Para acompanhar a análise, basta ler `docs/analise-filas-espacial-v1_0.md` e consultar os gráficos. Os comandos de reprodução abaixo são opcionais e não precisam ser executados pelo pesquisador agora.

## Guardar no repositório

Extraia `Analise_Espacial_Filas_SUMO_v1.zip` em Downloads. Na raiz do `tc-valdir`, o único comando de instalação é:

```powershell
python "$env:USERPROFILE\Downloads\Analise_Espacial_Filas_SUMO_v1\scripts\instalar_analise_espacial.py" --repositorio .
```

Ajuste o caminho se extrair em outra pasta. O instalador apenas copia os arquivos, confere hashes/conflitos e libera a nova pasta de resultados no `.gitignore`. Acrescenta um link ao README. Usa biblioteca padrão; não instala pacotes, não executa testes, análise ou simulação. Não substitui arquivos locais diferentes, não apaga a tabela original e não faz commit/push.

Quando for versionar esta entrega, os caminhos são:

```powershell
git add -- .gitignore README.md `
    scripts/analisar_filas_espacialmente.py `
    scripts/instalar_analise_espacial.py `
    docs/analise-filas-espacial-v1_0.md `
    docs/checkpoint-filas-espacial-2026-10-14.md `
    docs/README-filas-espacial.md `
    docs/entrega-espacial-filas-v1.json `
    output/analise/baseline_v1_filas_espacial_v1

git diff --cached --stat
git commit -m "Analisa distribuicao espacial das filas"
git push
```

Esses comandos publicam os arquivos para os outros chats após revisão do conteúdo preparado. São distintos do cálculo estatístico, que já foi feito. O arquivo bruto por faixa não foi duplicado no pacote; permanece no seu local original de consolidação.

## Reprodução opcional

O script usa NumPy, pandas e Matplotlib; versões constam no manifesto. Não precisa reproduzir para utilizar os resultados.

```powershell
python .\scripts\analisar_filas_espacialmente.py `
    --por-faixa .\output\analise\baseline_v1_consolidado_v1\filas_por_faixa.csv `
    --base .\output\analise\baseline_v1_consolidado_v1\base_execucoes.csv `
    --manifesto .\output\analise\baseline_v1_consolidado_v1\manifesto_consolidacao.json `
    --rede .\output\experimento_final\baseline_v1\_config_snapshot\nereu_ramos.net.xml `
    --demanda .\output\experimento_final\baseline_v1\_config_snapshot\demanda_v2.json `
    --osm .\mapa\nereu_ramos.osm `
    --saida .\output\analise\reproducao_espacial_filas
```

Os caminhos de entrada precisam apontar para os arquivos efetivamente preservados. A pasta de saída precisa ser nova e não é liberada automaticamente para versionamento. O script exige que tabela, base, rede e demanda correspondam ao manifesto. O OSM fornece rótulos auxiliares; seu hash também é registrado. Uma mudança desse arquivo pode mudar nomes, sem alterar as estatísticas numéricas das filas.
