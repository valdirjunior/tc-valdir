$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "============================================================"
Write-Host " TESTE LOCAL - EDGE 157964297"
Write-Host " lcStrategic temporariamente reduzido nos primeiros 120 m"
Write-Host " Rotas existentes; demanda nao sera regenerada"
Write-Host "============================================================"

python .\scripts\teste_lc_157964297.py --seed 49 --cenario REF --threshold 120 --lc-strategic 0 --end 1800
if ($LASTEXITCODE -ne 0) { throw "Falha no teste seed 49 / REF" }

python .\scripts\teste_lc_157964297.py --seed 51 --cenario AGR --threshold 120 --lc-strategic 0 --end 1800
if ($LASTEXITCODE -ne 0) { throw "Falha no teste seed 51 / AGR" }

Write-Host ""
Write-Host "============================================================"
Write-Host " TESTES CONCLUIDOS"
Write-Host " Saidas: .\output\diagnostico_lc_157964297"
Write-Host "============================================================"
