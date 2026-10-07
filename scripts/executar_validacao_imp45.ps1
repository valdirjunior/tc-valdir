$ErrorActionPreference = "Stop"

$rede = ".\config\nereu_ramos.net.xml"
$perfisBase = ".\config\perfis\perfis.add.xml"
$perfilTeste = ".\output\validacao_imp45\perfis\perfis_imp45_jm080.add.xml"

$fluxo = 650
$fim = 1800
$timeToImpatience = 45

$seeds = 47..51
$cenarios = @("REF", "EQU", "CAU", "AGR", "MIX_C", "MIX_N", "MIX_A")

if (-not (Test-Path $rede)) { throw "Rede não encontrada: $rede" }
if (-not (Test-Path $perfisBase)) { throw "Perfis não encontrados: $perfisBase" }

New-Item -ItemType Directory -Force (Split-Path $perfilTeste) | Out-Null

# Cópia temporária dos perfis para validação:
# - jmTimegapMinor = 0.80
# - lcStrategic = 1.0
# - lcStrategicLookahead removido para usar o padrão do SUMO
# - impatience individual dos perfis é preservada
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

Write-Host ""
Write-Host "================================================================"
Write-Host " VALIDACAO AMPLIADA - impatience 45 s + jmTimegapMinor 0.80 s"
Write-Host " Seeds: 47 a 51"
Write-Host " Cenarios: REF, EQU, CAU, AGR, MIX_C, MIX_N, MIX_A"
Write-Host " Total esperado: 35 simulacoes"
Write-Host "================================================================"

$contador = 0
$total = $seeds.Count * $cenarios.Count

foreach ($seed in $seeds) {
    foreach ($cenario in $cenarios) {
        $contador++

        $rota = ".\output\experimentos\seed_$seed\fluxo_$fluxo\$cenario\rotas.rou.xml"
        if (-not (Test-Path $rota)) {
            throw "Rota não encontrada: $rota"
        }

        $saida = ".\output\validacao_imp45\seed_$seed\fluxo_$fluxo\$cenario"
        New-Item -ItemType Directory -Force $saida | Out-Null

        Write-Host ""
        Write-Host "[$contador/$total] seed $seed / $cenario"

        & sumo `
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
}

Write-Host ""
Write-Host "================================================================"
Write-Host " 35 SIMULACOES CONCLUIDAS"
Write-Host "================================================================"

python .\scripts\analisar_validacao_imp45.py
if ($LASTEXITCODE -ne 0) {
    throw "Falha na análise dos resultados."
}
