param(
    [switch]$Gui
)

$ErrorActionPreference = "Stop"

$rede = ".\config\nereu_ramos.net.xml"
$perfisBase = ".\config\perfis\perfis.add.xml"
$perfilTeste = ".\output\teste_impaciencia_45\perfis\perfis_imp45.add.xml"

$fluxo = 650
$fim = 1800
$timeToImpatience = 45

$casos = @(
    @{ Seed = 49; Cenario = "REF" },
    @{ Seed = 51; Cenario = "AGR" }
)

if (-not (Test-Path $rede)) { throw "Rede não encontrada: $rede" }
if (-not (Test-Path $perfisBase)) { throw "Perfis não encontrados: $perfisBase" }

New-Item -ItemType Directory -Force (Split-Path $perfilTeste) | Out-Null

# Cria uma cópia temporária dos perfis:
# - mantém os valores de impatience já definidos nos perfis;
# - fixa jmTimegapMinor em 0.80;
# - volta lcStrategic ao padrão 1.0;
# - remove eventual lcStrategicLookahead para não misturar os testes.
[xml]$xml = Get-Content -Raw -Encoding UTF8 $perfisBase

foreach ($vType in $xml.additional.vType) {
    $vType.SetAttribute("jmTimegapMinor", "0.80")
    $vType.SetAttribute("lcStrategic", "1.0")

    if ($vType.HasAttribute("lcStrategicLookahead")) {
        $vType.RemoveAttribute("lcStrategicLookahead")
    }
}

$settings = New-Object System.Xml.XmlWriterSettings
$settings.Indent = $true
$settings.Encoding = New-Object System.Text.UTF8Encoding($false)

$writer = [System.Xml.XmlWriter]::Create($perfilTeste, $settings)
$xml.Save($writer)
$writer.Close()

$executavel = if ($Gui) { "sumo-gui" } else { "sumo" }

Write-Host ""
Write-Host "============================================================"
Write-Host " TESTE FINAL DE SENSIBILIDADE DA IMPACIENCIA"
Write-Host " time-to-impatience = 45 s"
Write-Host " jmTimegapMinor = 0.80 s"
Write-Host " lcStrategic = 1.0"
Write-Host " lcStrategicLookahead = padrão do SUMO"
Write-Host " Perfis de impatience mantidos como estão"
Write-Host "============================================================"

foreach ($caso in $casos) {
    $seed = $caso.Seed
    $cenario = $caso.Cenario

    $rota = ".\output\experimentos\seed_$seed\fluxo_$fluxo\$cenario\rotas.rou.xml"
    if (-not (Test-Path $rota)) {
        throw "Rota não encontrada: $rota"
    }

    $saida = ".\output\teste_impaciencia_45\seed_$seed\fluxo_$fluxo\$cenario"
    New-Item -ItemType Directory -Force $saida | Out-Null

    Write-Host ""
    Write-Host "seed $seed / $cenario"

    & $executavel `
        -n $rede `
        -r $rota `
        -a $perfilTeste `
        --begin 0 `
        --end $fim `
        --step-length 0.1 `
        --time-to-impatience $timeToImpatience `
        --seed $seed `
        --time-to-teleport -1 `
        --collision.check-junctions true `
        --collision.action warn `
        --tripinfo-output "$saida\tripinfo.xml" `
        --statistic-output "$saida\stats.xml" `
        --summary-output "$saida\summary.xml" `
        --summary-output.period 1 `
        --queue-output "$saida\queues.xml" `
        --queue-output.period 1 `
        --lanechange-output "$saida\lanechanges.xml" `
        --collision-output "$saida\collisions.xml" `
        --error-log "$saida\warnings.log"

    if ($LASTEXITCODE -ne 0) {
        throw "Erro em seed $seed / $cenario"
    }
}

Write-Host ""
Write-Host "============================================================"
Write-Host " TESTE CONCLUIDO"
Write-Host "============================================================"
Write-Host ""
Write-Host "Para inspeção visual, rode:"
Write-Host "  .\scripts\testar_impaciencia_45.ps1 -Gui"
Write-Host ""
