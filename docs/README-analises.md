# Organização das análises oficiais

O projeto mantém o padrão existente: código em `scripts/`, documentação e checkpoints em `docs/`, dados e resultados em `output/`. Os resultados selecionados para versionamento ficam em subpastas oficiais de `output/analise/`.

## Etapas

| Pasta | Função |
|---|---|
| `output/experimento_final/baseline_v1/` | Coleta bruta congelada; não é alterada por esta entrega |
| `output/analise/baseline_v1_consolidado_v1/` | Base de 630 execuções, dicionário, validação, manifesto e tabela por faixa gerada localmente |
| `output/analise/baseline_v1_descritiva_v1/` | Resumos, pares, gráficos e relatório descritivo |
| `output/analise/baseline_v1_incerteza_v0_1/` | ICs BCa marginais de tempo de viagem e conferência Monte Carlo |

Os scripts da raiz `scripts/` são os pontos de execução. A cópia do script na pasta de resultados descritivos foi preservada como snapshot da entrega original e tem o mesmo conteúdo. Não criar métodos diferentes editando essa cópia: versionar as mudanças no script canônico e registrar a nova etapa.

O checkpoint atual é `docs/checkpoint-analise-2026-10-14.md`. O protocolo de extração atual é `docs/Protocolo_metricas_SUMO_v0_2.md`; v0.1 permanece histórico.

## Instalar o pacote desta entrega

Extraia `Entrega_Analise_TC_2026_10_14.zip` fora do repositório, por exemplo em Downloads. Na raiz do `tc-valdir`, com a `.venv` ativa, execute o instalador da pasta extraída:

```powershell
python "$env:USERPROFILE\Downloads\Entrega_Analise_TC_2026_10_14\scripts\instalar_entrega_analise.py" --repositorio .
```

Se escolheu outra pasta de extração, ajuste o caminho. O instalador usa apenas biblioteca padrão. Ele verifica hashes, preserva arquivos existentes idênticos e recusa substituir arquivos de conteúdo diferente. Adiciona exceções específicas de análise ao `.gitignore` e um link de continuidade ao README. Não executa simulação, commit ou push.

Para conferir sem instalar, acrescentar `--verificar`. Se houver conflito, o diagnóstico identifica os caminhos e a cópia não começa; investigar antes de substituir qualquer arquivo.

A entrega preserva o conteúdo da base e dos manifestos recebidos. `filas_por_faixa.csv`, já existente na consolidação local, permanece no lugar e não é apagado ou substituído. Não foi incluído de novo no pacote porque não foi reenviado. Os demais arquivos da coleta bruta também permanecem no lugar.

## Versionamento

O `.gitignore` do GitHub ignora `output/*`. As exceções acrescentadas liberam somente as três pastas oficiais de análise, mantendo o comportamento das demais saídas. Copiar um resultado para o computador não o publica no GitHub.

Os comandos seletivos estão em `docs/comandos-git-analise-2026-10-14.ps1`. Eles precisam ser executados pelo pesquisador após a instalação e revisão. Os outros chats podem ser orientados a consultar o checkpoint no repositório depois do push; eles não recebem automaticamente mudanças do clone local.

## Reprodução

O uso dos resultados não exige reproduzir a etapa. Para reprodução:

```powershell
python .\scripts\consolidar_experimento.py --entrada .\output\experimento_final\baseline_v1 --saida .\output\analise\nova_consolidacao
python .\scripts\analisar_descritivamente.py --entrada .\output\analise\baseline_v1_consolidado_v1\resultados_consolidacao.zip --saida .\output\analise\nova_descritiva
python .\scripts\estimar_incerteza_pareada.py --entrada .\output\analise\baseline_v1_consolidado_v1\resultados_consolidacao.zip --saida .\output\analise\nova_incerteza
```

As pastas novas precisam não existir. Só o consolidador usa exclusivamente biblioteca padrão. Os outros scripts usam NumPy, pandas, Matplotlib e ReportLab, com SciPy adicional na etapa de incerteza; versões testadas constam dos manifestos. Não é necessário executar esses comandos agora: os resultados desta entrega já foram calculados.

Uma nova pasta de resultados só deve ser liberada para versionamento depois de ter sua função e versão identificadas. Não remover a validação para contornar erros ou excluir seeds com resultados inconvenientes.
