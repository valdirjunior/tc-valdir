param(
    [switch]$Gui
)

$ErrorActionPreference = "Stop"

$rede = ".\config\nereu_ramos.net.xml"
$perfisBase = ".\config\perfis\perfis.add.xml"
$fluxo = 650
$fim = 1800

$valoresLC = @(
    @{ Nome = "lc075"; Valor = "0.75" },
    @{ Nome = "lc050"; Valor = "0.50" }
)

$casos = @(
    @{ Seed = 49; Cenario = "REF"; Tipo = "problema" },
    @{ Seed = 51; Cenario = "AGR"; Tipo = "problema" },
    @{ Seed = 47; Cenario = "REF"; Tipo = "controle" },
    @{ Seed = 50; Cenario = "AGR"; Tipo = "controle" }
)

if (-not (Test-Path $rede)) {
    throw "Rede não encontrada: $rede"
}

if (-not (Test-Path $perfisBase)) {
    throw "Perfis não encontrados: $perfisBase"
}

$perfilTesteDir = ".\output\teste_lc_global\perfis"
New-Item -ItemType Directory -Force $perfilTesteDir | Out-Null

function Criar-PerfilTeste {
    param(
        [string]$Valor,
        [string]$Saida
    )

    [xml]$xml = Get-Content -Raw -Encoding UTF8 $perfisBase

    foreach ($vType in $xml.additional.vType) {
        $vType.SetAttribute("lcStrategic", $Valor)
    }

    $settings = New-Object System.Xml.XmlWriterSettings
    $settings.Indent = $true
    $settings.Encoding = New-Object System.Text.UTF8Encoding($false)

    $writer = [System.Xml.XmlWriter]::Create($Saida, $settings)
    $xml.Save($writer)
    $writer.Close()
}

$executavel = if ($Gui) { "sumo-gui" } else { "sumo" }

Write-Host ""
Write-Host "============================================================"
Write-Host " TESTE GLOBAL DE lcStrategic"
Write-Host " Valores: 0.75 e 0.50"
Write-Host " Demanda/rotas existentes serao reutilizadas"
Write-Host " time-to-impatience = 60"
Write-Host "============================================================"

foreach ($cfg in $valoresLC) {
    $nome = $cfg.Nome
    $valor = $cfg.Valor
    $perfilTeste = Join-Path $perfilTesteDir "perfis_$nome.add.xml"

    Criar-PerfilTeste -Valor $valor -Saida $perfilTeste

    Write-Host ""
    Write-Host "------------------------------------------------------------"
    Write-Host " lcStrategic = $valor"
    Write-Host " Perfil temporario: $perfilTeste"
    Write-Host "------------------------------------------------------------"

    foreach ($caso in $casos) {
        $seed = $caso.Seed
        $cenario = $caso.Cenario
        $tipo = $caso.Tipo

        $rota = ".\output\experimentos\seed_$seed\fluxo_$fluxo\$cenario\rotas.rou.xml"
        if (-not (Test-Path $rota)) {
            throw "Rota não encontrada: $rota"
        }

        $saida = ".\output\teste_lc_global\$nome\seed_$seed\fluxo_$fluxo\$cenario"
        New-Item -ItemType Directory -Force $saida | Out-Null

        Write-Host ""
        Write-Host "[$nome] seed $seed / $cenario / $tipo"

        & $executavel `
            -n $rede `
            -r $rota `
            -a $perfilTeste `
            --begin 0 `
            --end $fim `
            --step-length 0.1 `
            --time-to-impatience 60 `
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
            throw "Erro em $nome / seed $seed / $cenario"
        }
    }
}

Write-Host ""
Write-Host "============================================================"
Write-Host " SIMULACOES CONCLUIDAS"
Write-Host "============================================================"

python .\scripts\analisar_lc_global.py
if ($LASTEXITCODE -ne 0) {
    throw "Falha na análise dos resultados."
}
