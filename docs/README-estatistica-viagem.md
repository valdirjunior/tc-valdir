# Instalação e reprodução: avaliação estatística de viagem

Extraia `Estatistica_Viagem_SUMO_v1.zip` em Downloads, mantendo a pasta `Estatistica_Viagem_SUMO_v1`. Na raiz do repositório local, execute:

```powershell
python "$env:USERPROFILE\Downloads\Estatistica_Viagem_SUMO_v1\scripts\instalar_estatistica_viagem.py" --repositorio .
```

Ajuste o caminho se extrair em outro local. O instalador usa somente biblioteca padrão, confere hashes/dependência, bloqueia conflitos antes de copiar e preserva os arquivos existentes. Acrescenta a exceção da nova pasta ao `.gitignore` e uma referência no README. Não executa simulação, cálculo estatístico, commit ou push. Para apenas verificar, acrescentar `--verificar`.

O script dependente `scripts/estimar_incerteza_pareada.py` precisa ser o da entrega anterior. Se estiver alterado, investigar a diferença em vez de substituir a versão local para contornar o diagnóstico.

## Versionar

```powershell
git add -- .gitignore README.md `
    scripts/avaliar_contrastes_viagem.py `
    scripts/instalar_estatistica_viagem.py `
    testes/test_estatistica_viagem.py `
    docs/protocolo-estatistico-viagem-v1_0.md `
    docs/checkpoint-estatistica-viagem-2026-10-14.md `
    docs/README-estatistica-viagem.md `
    docs/referencias-estatistica-viagem.bib `
    docs/entrega-estatistica-viagem-v1.json `
    output/analise/baseline_v1_estatistica_v1

git diff --cached --stat
git commit -m "Avalia contrastes de viagem com intervalos simultaneos"
git push
```

Revise o conteúdo preparado antes do commit. O novo ponto de entrada para outros chats é `docs/checkpoint-estatistica-viagem-2026-10-14.md` após o push.

## Reprodução opcional

Os resultados já estão calculados. A reprodução requer NumPy, pandas, SciPy e Matplotlib, nas versões registradas no manifesto; o instalador não instala bibliotecas nem altera o ambiente Python.

```powershell
python .\scripts\avaliar_contrastes_viagem.py --entrada .\output\analise\baseline_v1_consolidado_v1\resultados_consolidacao.zip --saida .\output\analise\reproducao_estatistica_viagem
python -m unittest discover -s .\testes -p test_estatistica_viagem.py -v
```

A pasta de reprodução precisa ser nova e não é liberada automaticamente para versionamento. O arquivo `distribuicao_max_t.npz` preserva os máximos da produção e os índices dos contrastes que geraram cada máximo. A ordem é demanda 300/450/625 e, dentro de cada demanda, EQU/CAU/AGR/MIX_C/MIX_N/MIX_A. A segunda distribuição é usada somente para conferência e seus limites/crítico estão nos arquivos de resultado.
