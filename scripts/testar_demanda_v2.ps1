param(
    [int]$Fluxo = 650,
    [int[]]$Seeds = @(42, 43, 44, 45, 46)
)

$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "========================================"
Write-Host " TESTE DA DEMANDA V2"
Write-Host " Fluxo: $Fluxo"
Write-Host " Seeds: $($Seeds -join ', ')"
Write-Host "========================================"
Write-Host ""

foreach ($seed in $Seeds) {
    Write-Host ""
    Write-Host "----------------------------------------"
    Write-Host " GERANDO SEED $seed"
    Write-Host "----------------------------------------"

    python .\scripts\gerar_demanda_v2.py `
        --fluxo $Fluxo `
        --seed $seed `
        --output-root .\output\teste_demanda_v2

    if ($LASTEXITCODE -ne 0) {
        throw "Falha ao gerar a seed $seed."
    }
}

Write-Host ""
Write-Host "========================================"
Write-Host " ANALISANDO DISTRIBUICAO OD"
Write-Host "========================================"
Write-Host ""

python .\scripts\analisar_od.py `
    --base-dir .\output\teste_demanda_v2 `
    --output-dir .\output\analise_demanda_v2 `
    --fluxo $Fluxo `
    --seeds $Seeds

if ($LASTEXITCODE -ne 0) {
    throw "Falha na analise OD."
}

Write-Host ""
Write-Host "========================================"
Write-Host " TESTE CONCLUIDO"
Write-Host "========================================"
Write-Host ""
Write-Host "Rotas:"
Write-Host "  output\teste_demanda_v2"
Write-Host ""
Write-Host "Analise:"
Write-Host "  output\analise_demanda_v2"
Write-Host ""
