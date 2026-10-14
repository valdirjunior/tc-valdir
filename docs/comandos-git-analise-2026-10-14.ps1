# Execute na raiz do tc-valdir, apos instalar a entrega.
# Estes comandos nao sao executados pelo instalador.

git status --short

git add -- .gitignore README.md `
    scripts/consolidar_experimento.py `
    scripts/analisar_descritivamente.py `
    scripts/estimar_incerteza_pareada.py `
    scripts/instalar_entrega_analise.py `
    testes/test_consolidacao.py `
    docs/Protocolo_metricas_SUMO_v0_2.md `
    docs/README_consolidacao.md `
    docs/README-analises.md `
    docs/checkpoint-analise-2026-10-14.md `
    docs/comandos-git-analise-2026-10-14.ps1 `
    docs/entrega-analise-2026-10-14.json `
    output/analise/baseline_v1_consolidado_v1 `
    output/analise/baseline_v1_descritiva_v1 `
    output/analise/baseline_v1_incerteza_v0_1

git diff --cached --stat

git commit -m "Organiza consolidacao e analises do experimento oficial"

git push
