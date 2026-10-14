# Consolidação da coleta oficial SUMO — versão 1.0.0

Este pacote contém um analisador separado da simulação. Ele lê os arquivos da coleta congelada, verifica consistência e extrai métricas segundo o protocolo 0.2. Não executa SUMO, não altera rede/perfis/demanda e não escolhe um teste estatístico.

## Instalação no projeto

1. Extraia o ZIP em uma pasta temporária.
2. Copie `scripts/consolidar_experimento.py` para a pasta `scripts` do projeto `tc-valdir`.
3. Guarde estes documentos e o protocolo em `docs`, se desejar. Os testes são opcionais para execução local.

Requisito: Python 3.10 ou mais recente. O Python 3.14.7 da `.venv` do projeto atende ao requisito. Não é necessário instalar pandas, NumPy, SUMO ou outras dependências para este processamento.

## Processar as 630 execuções

No PowerShell, com a `.venv` ativada e na raiz do projeto:

```powershell
python .\scripts\consolidar_experimento.py --entrada .\output\experimento_final\baseline_v1 --saida .\output\analise\baseline_v1_consolidado_v1
```

Use uma pasta de saída que ainda não exista. O analisador recusa sobrescrever análises anteriores ou escrever dentro da coleta bruta. Para repetir, escolha outro nome de saída; não apague a coleta. O comando somente lê os arquivos da entrada.

O progresso é mostrado a cada dez execuções. Ao terminar, o código de saída é zero se a extração foi concluída, ou 2 se houve falha. Um aviso de frenagem, por si só, não é erro nem motivo para excluir uma execução.

Se tudo passar, anexe na conversa:

**`output/analise/baseline_v1_consolidado_v1/resultados_consolidacao.zip`**

Esse ZIP reúne a base central, relatório de consistência, manifesto e dicionário. A tabela maior de filas por faixa fica na pasta de análise, sem entrar no ZIP de envio inicial. Não é necessário enviar novamente os dados brutos completos.

## Arquivos produzidos

| Arquivo | Conteúdo |
|---|---|
| `base_execucoes.csv` | 630 linhas esperadas; uma por seed × demanda × composição |
| `filas_por_faixa.csv` | Uma linha por execução × faixa × janela; inclui zeros e separa principal/experimental em colunas |
| `validacao_consolidacao.csv` | Uma linha de diagnóstico por execução; avisos e erros explícitos |
| `dicionario_metricas.csv` | Definição, unidade e papel dos 91 campos da base central |
| `manifesto_consolidacao.json` | Versões, convenções, cobertura, hashes do snapshot/entradas/CSV e duração do processamento |
| `resultados_consolidacao.zip` | Arquivos pequenos necessários à próxima etapa da análise |

Na rede examinada, a tabela por faixa tem 198 faixas × 2 janelas × 630 execuções = 249.480 linhas. Ela ocupa mais espaço que a base central. Os comprimentos médios da rede são somas entre faixas; não descrevem uma fila contínua única.

CSV: UTF-8 com BOM, separador `;`, decimal `.`, valores numéricos com 12 algarismos significativos. No Excel em português, utilize importação de texto/CSV com decimal ponto para evitar interpretação indevida. IDs de faixas e veículos são texto. A base pode ser lida em Python com `csv.DictReader` ou, posteriormente, `pandas.read_csv(..., sep=';')`.

Não há arredondamento das operações intermediárias. O percentil utiliza interpolação linear; o desvio-padrão dentro de uma execução usa divisor N. A dispersão entre seeds será calculada em etapa posterior.

## Em caso de erro

O programa não publica uma base de métricas parcial como se fosse integral. Ele mantém `validacao_consolidacao.csv` e `manifesto_consolidacao.json`, com `success=false`. Resultados válidos de outras execuções não tornam a coleta parcial uma base final.

Se falhar, envie esses dois arquivos, ou cole a mensagem do console. Não remova seeds e não refaça simulações para favorecer a análise. Um erro de consistência exige investigar a causa; não implica automaticamente que a coleta seja inválida.

As checagens cobrem a matriz oficial, hashes do snapshot, versão e configuração, rotas e partidas compartilhadas, quantidades efetivas de perfis, IDs e viagens concluídas, médias do SUMO, grade temporal e contadores. Uma tolerância de 0,01 é usada na conferência das médias com `stats.xml`, considerando o arredondamento dos campos; totais usam tolerância escalada pela população.

O contador `safety@emergencyBraking` é a fonte principal de frenagens. `warnings.log` fornece IDs e instantes como complemento. O mesmo aviso em `sumo.log` não é somado novamente. Divergências entre contador e avisos são registradas para investigação, mantendo o contador principal.

## Testar uma amostra explicitamente

Se desejar processar o pacote de amostra antes da coleta completa, extraia seus arquivos numa pasta própria e execute:

```powershell
python .\scripts\consolidar_experimento.py --entrada .\amostra_seed1000 --saida .\output\analise\teste_amostra_v1 --modo-amostra
```

O modo amostra verifica os arquivos presentes e registra as chaves ausentes, sem exigir os 630 diretórios. Os nomes das bases e do ZIP contêm `AMOSTRA`, e o manifesto informa o alcance. Nunca usar esse modo para declarar a coleta completa validada.

## Testes incluídos e limites da validação

Foram executados 12 testes, incluindo:

- resultados conhecidos nas três execuções reais de REF/seed 1000;
- correspondência das filas e de sua decomposição externa/interna;
- inclusão de faixas sem fila no denominador;
- ausência de alterações nos hashes dos arquivos da amostra;
- bloqueio de viagem inacabada, lacuna temporal e perfil alterado;
- recusa de publicar a amostra como coleta integral;
- convenção da chegada em 600 s e ausência de horário inventado quando não há fila;
- deduplicação de avisos e arredondamento das composições.

Para executar os testes básicos no pacote extraído:

```powershell
python -m unittest discover -s .\testes -v
```

Para incluir a integração com a amostra real extraída:

```powershell
$env:SUMO_AMOSTRA = (Resolve-Path .\amostra_seed1000).Path
python -m unittest discover -s .\testes -v
```

Os testes de corrupção trabalham em cópias temporárias. Não alteram a amostra. Sem a variável `SUMO_AMOSTRA`, os testes de integração são explicitamente pulados.

O script foi verificado na amostra disponibilizada; os outros 627 conjuntos de XML ainda precisam passar pelo processamento no computador do pesquisador. A aprovação nos testes não constitui calibração do modelo ao trânsito real. Não foram feitos testes inferenciais nem conclusões sobre o efeito dos perfis.

## Leitura da tabela de filas por faixa

`category` identifica `external` ou `internal`, conforme o snapshot. A geometria e as permissões definem um conjunto fixo de faixas, sem seleção pelos resultados. IDs internos podem não ter nome de rua ou extremos identificados no mesmo elemento XML; nesses casos as células permanecem vazias, sem nomes inventados.

- `window_begin_s`, `window_end_s`: janela [início,fim), em segundos.
- `sample_count`: 600 ou 1800 observações de 1 s, inclusive zeros.
- `queue_mean_m`, `queue_max_m`: média temporal e máximo de `queueing_length` daquela faixa.
- `queue_presence_pct`: percentual de observações da faixa com comprimento principal >0.
- `queue_max_time_s`: primeira ocorrência observada do máximo; vazio se todos os comprimentos são zero.
- `slow_experimental_*`: os mesmos resumos de `queueing_length_experimental`, com seu critério próprio.

Uma faixa ausente em um bloco existente recebe zero na série exportada; uma lacuna de blocos é erro. As saídas registram amostras de 1 s, embora o passo da simulação seja 0,1 s. As filas entre amostras não são reconstruídas.

O significado específico dos campos de filas e as referências do código SUMO 1.27.1 estão em `Protocolo_metricas_SUMO_v0_2.md`.
