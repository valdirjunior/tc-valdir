param(
    [int[]]$Seeds = @(47, 48, 49, 50, 51),
    [int[]]$Fluxos = @(700)
)

$ErrorActionPreference = "Stop"

# ============================================================
# Arquivos principais
# ============================================================

$rede = ".\config\nereu_ramos.net.xml"

$configDemanda = ".\config\demanda\demanda_v2.json"
$scriptDemanda = ".\scripts\gerar_demanda_v2.py"

$perfisBase = ".\config\perfis\perfis.add.xml"
$scriptPerfis = ".\scripts\atribuir_perfis.py"

$pastaGeracaoDemanda = ".\output\_geracao_demanda_v2"

# Perfil temporário usado nesta validação.
# O arquivo original NÃO é alterado.
$pastaConfigTeste = ".\output\_config_testes"
$perfisTeste = "$pastaConfigTeste\perfis_imp45_jm080.add.xml"

# ============================================================
# Configuração congelada após validação de 650
# ============================================================

$inicioDemanda = 0
$fimDemanda = 600
$fimSimulacao = 1800

$timeToImpatience = 45
$jmTimegapMinor = "0.80"

$cenarios = @(
    "REF",
    "EQU",
    "CAU",
    "AGR",
    "MIX_C",
    "MIX_N",
    "MIX_A"
)

# ============================================================
# Validação inicial
# ============================================================

$arquivosObrigatorios = @(
    $rede,
    $configDemanda,
    $scriptDemanda,
    $perfisBase,
    $scriptPerfis
)

foreach ($arquivo in $arquivosObrigatorios) {
    if (-not (Test-Path $arquivo)) {
        throw "Arquivo obrigatório não encontrado: $arquivo"
    }
}

# ============================================================
# Cria perfil temporário com a configuração congelada
# ============================================================

New-Item -ItemType Directory -Force $pastaConfigTeste | Out-Null

[xml]$xml = Get-Content -Raw -Encoding UTF8 $perfisBase

foreach ($vType in $xml.additional.vType) {
    # Mantém a estrutura relativa dos perfis (impatience individual etc.)
    # e aplica apenas os ajustes de validação já escolhidos.
    $vType.SetAttribute("jmTimegapMinor", $jmTimegapMinor)
    $vType.SetAttribute("lcStrategic", "1.0")

    # Garante que o experimento NÃO herde o teste de lookahead.
    if ($vType.HasAttribute("lcStrategicLookahead")) {
        $vType.RemoveAttribute("lcStrategicLookahead")
    }
}

$settings = New-Object System.Xml.XmlWriterSettings
$settings.Indent = $true
$settings.Encoding = New-Object System.Text.UTF8Encoding($false)

$writer = [System.Xml.XmlWriter]::Create($perfisTeste, $settings)
$xml.Save($writer)
$writer.Close()

Write-Host ""
Write-Host "================================================================"
Write-Host " TESTE DE FLUXO ALTO"
Write-Host " Demanda: V2.3 ponderada"
Write-Host " Seeds: $($Seeds -join ', ')"
Write-Host " Fluxos: $($Fluxos -join ', ')"
Write-Host " time-to-impatience: $timeToImpatience s"
Write-Host " jmTimegapMinor: $jmTimegapMinor s"
Write-Host " lcStrategic: 1.0"
Write-Host " lcStrategicLookahead: padrão do SUMO"
Write-Host "================================================================"

foreach ($seed in $Seeds) {

    Write-Host ""
    Write-Host "========================================"
    Write-Host " SEED $seed"
    Write-Host "========================================"

    foreach ($fluxo in $Fluxos) {

        $pastaBase = ".\output\experimentos\seed_$seed\fluxo_$fluxo"
        $pastaDemanda = "$pastaBase\demanda"

        New-Item -ItemType Directory -Force $pastaDemanda | Out-Null

        $baseTrips = "$pastaDemanda\base.trips.xml"
        $baseRoutes = "$pastaDemanda\base.rou.xml"

        Write-Host ""
        Write-Host "----------------------------------------"
        Write-Host " Fluxo $fluxo - gerando demanda V2.3"
        Write-Host "----------------------------------------"

        # ----------------------------------------------------
        # Geração da demanda V2.3
        # ----------------------------------------------------

        python $scriptDemanda `
            --net $rede `
            --config $configDemanda `
            --output-root $pastaGeracaoDemanda `
            --fluxo $fluxo `
            --seed $seed `
            --begin $inicioDemanda `
            --end $fimDemanda

        if ($LASTEXITCODE -ne 0) {
            throw "Erro ao gerar demanda V2.3 para seed $seed / fluxo $fluxo."
        }

        $pastaGerada = "$pastaGeracaoDemanda\seed_$seed\fluxo_$fluxo\REF"
        $tripsGeradas = "$pastaGerada\demanda.trips.xml"
        $rotasGeradas = "$pastaGerada\rotas.rou.xml"

        if (-not (Test-Path $tripsGeradas)) {
            throw "Arquivo de trips não encontrado após a geração: $tripsGeradas"
        }

        if (-not (Test-Path $rotasGeradas)) {
            throw "Arquivo de rotas não encontrado após a geração: $rotasGeradas"
        }

        Copy-Item $tripsGeradas $baseTrips -Force
        Copy-Item $rotasGeradas $baseRoutes -Force

        $quantidade = (
            Select-String -Path $baseRoutes -Pattern "<vehicle "
        ).Count

        if ($quantidade -ne $fluxo) {
            throw "Fluxo ${fluxo}: esperados $fluxo veículos, encontrados $quantidade."
        }

        Write-Host ""
        Write-Host "Demanda-base validada:"
        Write-Host "  Seed: $seed"
        Write-Host "  Fluxo: $fluxo"
        Write-Host "  Veículos: $quantidade"
        Write-Host "  Trips: $baseTrips"
        Write-Host "  Rotas: $baseRoutes"

        # ----------------------------------------------------
        # Sete composições comportamentais
        # ----------------------------------------------------

        foreach ($cenario in $cenarios) {

            $pastaCenario = "$pastaBase\$cenario"
            New-Item -ItemType Directory -Force $pastaCenario | Out-Null

            $rota = "$pastaCenario\rotas.rou.xml"

            Write-Host ""
            Write-Host "========================================"
            Write-Host " $seed / $fluxo / $cenario"
            Write-Host "========================================"

            # Mesma realização de demanda dentro da mesma seed/fluxo.
            # Só a composição de perfis é alterada.
            python $scriptPerfis `
                --entrada $baseRoutes `
                --saida $rota `
                --cenario $cenario `
                --seed $seed

            if ($LASTEXITCODE -ne 0) {
                throw "Erro na atribuição de perfis em $seed / $fluxo / $cenario."
            }

            # ------------------------------------------------
            # SUMO
            # ------------------------------------------------

            sumo `
                -n $rede `
                -r $rota `
                -a $perfisTeste `
                --begin 0 `
                --end $fimSimulacao `
                --step-length 0.1 `
                --time-to-impatience $timeToImpatience `
                --seed $seed `
                --time-to-teleport -1 `
                --collision.check-junctions true `
                --collision.action warn `
                --tripinfo-output "$pastaCenario\tripinfo.xml" `
                --statistic-output "$pastaCenario\stats.xml" `
                --summary-output "$pastaCenario\summary.xml" `
                --summary-output.period 1 `
                --queue-output "$pastaCenario\queues.xml" `
                --queue-output.period 1 `
                --lanechange-output "$pastaCenario\lanechanges.xml" `
                --collision-output "$pastaCenario\collisions.xml" `
                --error-log "$pastaCenario\warnings.log"

            if ($LASTEXITCODE -ne 0) {
                throw "Erro na simulação em $seed / $fluxo / $cenario."
            }
        }
    }
}

Write-Host ""
Write-Host "================================================================"
Write-Host " EXPERIMENTOS CONCLUÍDOS"
Write-Host "================================================================"

python .\scripts\analisar_fluxos_altos.py --fluxos $Fluxos --seeds $Seeds

if ($LASTEXITCODE -ne 0) {
    throw "Falha na análise dos resultados."
}
