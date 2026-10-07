param(
    [switch]$Gui
)

$ErrorActionPreference = "Stop"

$rede = ".\config\nereu_ramos.net.xml"
$perfisBase = ".\config\perfis\perfis.add.xml"
$fluxo = 650
$fim = 1800

# Teste de sensibilidade da distância global de planejamento estratégico.
# O padrão do SUMO é 3000 m.
$valoresLookahead = @(
    @{ Nome = "la300"; Valor = "300" },
    @{ Nome = "la150"; Valor = "150" },
    @{ Nome = "la100"; Valor = "100" }
)

# Dois casos que já travaram + dois controles que já haviam escoado.
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

$perfilTesteDir = ".\output\teste_lc_lookahead\perfis"
New-Item -ItemType Directory -Force $perfilTesteDir | Out-Null

function Criar-PerfilTeste {
    param(
        [string]$Lookahead,
        [string]$Saida
    )

    [xml]$xml = Get-Content -Raw -Encoding UTF8 $perfisBase

    foreach ($vType in $xml.additional.vType) {
        # Volta explicitamente ao comportamento-base de lcStrategic.
        $vType.SetAttribute("lcStrategic", "1.0")

        # Limita a distância considerada na escolha estratégica de faixa.
        $vType.SetAttribute("lcStrategicLookahead", $Lookahead)
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
Write-Host " TESTE GLOBAL DE lcStrategicLookahead"
Write-Host " Valores: 300 m, 150 m e 100 m"
Write-Host " lcStrategic = 1.0"
Write-Host " Demanda/rotas existentes serao reutilizadas"
Write-Host " time-to-impatience = 60"
Write-Host "============================================================"

foreach ($cfg in $valoresLookahead) {
    $nome = $cfg.Nome
    $valor = $cfg.Valor
    $perfilTeste = Join-Path $perfilTesteDir "perfis_$nome.add.xml"

    Criar-PerfilTeste -Lookahead $valor -Saida $perfilTeste

    Write-Host ""
    Write-Host "------------------------------------------------------------"
    Write-Host " lcStrategicLookahead = $valor m"
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

        $saida = ".\output\teste_lc_lookahead\$nome\seed_$seed\fluxo_$fluxo\$cenario"
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

python .\scripts\analisar_lc_lookahead.py
if ($LASTEXITCODE -ne 0) {
    throw "Falha na análise dos resultados."
}
