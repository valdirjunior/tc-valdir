param(
    [switch]$Gui
)

$ErrorActionPreference = "Stop"

$rede = ".\config\nereu_ramos.net.xml"
$perfis = ".\config\perfis\perfis.add.xml"
$fimSimulacao = 2400
$fluxo = 650

$casos = @(
    @{ Seed = 49; Cenario = "REF" },
    @{ Seed = 51; Cenario = "AGR" }
)

$executavel = if ($Gui) { "sumo-gui" } else { "sumo" }

foreach ($caso in $casos) {
    $seed = $caso.Seed
    $cenario = $caso.Cenario

    $rota = ".\output\experimentos\seed_$seed\fluxo_$fluxo\$cenario\rotas.rou.xml"
    $saida = ".\output\diagnostico_2400\seed_$seed\fluxo_$fluxo\$cenario"

    if (-not (Test-Path $rota)) {
        throw "Rota não encontrada: $rota"
    }

    New-Item -ItemType Directory -Force $saida | Out-Null

    Write-Host ""
    Write-Host "============================================================"
    Write-Host " DIAGNOSTICO 2400 s - seed $seed / $cenario"
    Write-Host " Rota existente reutilizada; demanda NÃO será regenerada."
    Write-Host "============================================================"

    $argsSumo = @(
        "-n", $rede,
        "-r", $rota,
        "-a", $perfis,
        "--begin", "0",
        "--end", "$fimSimulacao",
        "--step-length", "0.1",
        "--time-to-impatience", "60",
        "--seed", "$seed",
        "--time-to-teleport", "-1",
        "--collision.check-junctions", "true",
        "--collision.action", "warn",
        "--tripinfo-output", "$saida\tripinfo.xml",
        "--statistic-output", "$saida\stats.xml",
        "--summary-output", "$saida\summary.xml",
        "--summary-output.period", "1",
        "--queue-output", "$saida\queues.xml",
        "--queue-output.period", "1",
        "--lanechange-output", "$saida\lanechanges.xml",
        "--collision-output", "$saida\collisions.xml",
        "--error-log", "$saida\warnings.log"
    )

    & $executavel @argsSumo

    if ($LASTEXITCODE -ne 0) {
        throw "Erro no diagnóstico: seed $seed / $cenario."
    }
}

Write-Host ""
Write-Host "============================================================"
Write-Host " DIAGNOSTICO CONCLUIDO"
Write-Host " Saidas: .\output\diagnostico_2400"
Write-Host "============================================================"
