param(
    [int[]]$Seeds = @(42..71),
    [int[]]$Fluxos = @(625),
    [string]$NomeTeste = "sens_a"
)

$ErrorActionPreference = "Stop"

# ============================================================
# Sensibilidade de perfis
# Mantem rede, demanda, seeds e parametros globais do baseline.
# Altera SOMENTE os parametros dos vTypes em
# config/perfis/perfis_sensibilidade_a.add.xml
# ============================================================

$rede = ".\config\nereu_ramos.net.xml"
$configDemanda = ".\config\demanda\demanda_v2.json"
$scriptDemanda = ".\scripts\gerar_demanda_v2.py"
$scriptPerfis = ".\scripts\atribuir_perfis.py"
$perfis = ".\config\perfis\perfis_sensibilidade_a.add.xml"

$pastaBaseline = ".\output\experimentos"
$pastaSaida = ".\output\sensibilidade_perfis\$NomeTeste"
$pastaGeracaoDemanda = ".\output\_geracao_demanda_v2"

$inicioDemanda = 0
$fimDemanda = 600
$fimSimulacao = 1800
$timeToImpatience = 45

$cenarios = @(
    "REF",
    "EQU",
    "CAU",
    "AGR",
    "MIX_C",
    "MIX_N",
    "MIX_A"
)

$arquivosObrigatorios = @(
    $rede,
    $configDemanda,
    $scriptDemanda,
    $scriptPerfis,
    $perfis,
    ".\scripts\analisar_sensibilidade_perfis.py"
)

foreach ($arquivo in $arquivosObrigatorios) {
    if (-not (Test-Path $arquivo)) {
        throw "Arquivo obrigatorio nao encontrado: $arquivo"
    }
}

Write-Host ""
Write-Host "================================================================"
Write-Host " SENSIBILIDADE DE PERFIS - $NomeTeste"
Write-Host " Seeds: $($Seeds -join ', ')"
Write-Host " Fluxos: $($Fluxos -join ', ')"
Write-Host " Perfis: $perfis"
Write-Host " time-to-impatience: $timeToImpatience s"
Write-Host " jmTimegapMinor: 0.80 (definido no arquivo de perfis)"
Write-Host " lcStrategic: 1.0"
Write-Host " lcStrategicLookahead: padrao do SUMO"
Write-Host " Saida: $pastaSaida"
Write-Host "================================================================"

foreach ($seed in $Seeds) {
    foreach ($fluxo in $Fluxos) {

        $pastaBaseTeste = "$pastaSaida\seed_$seed\fluxo_$fluxo"
        $pastaDemandaTeste = "$pastaBaseTeste\demanda"
        New-Item -ItemType Directory -Force $pastaDemandaTeste | Out-Null

        $baseTripsTeste = "$pastaDemandaTeste\base.trips.xml"
        $baseRoutesTeste = "$pastaDemandaTeste\base.rou.xml"

        # ----------------------------------------------------
        # Reutiliza prioritariamente a demanda-base do baseline.
        # Isso garante comparação pareada com exatamente as mesmas
        # rotas da seed/fluxo, quando elas estiverem disponíveis.
        # ----------------------------------------------------

        $baselineTrips = "$pastaBaseline\seed_$seed\fluxo_$fluxo\demanda\base.trips.xml"
        $baselineRoutes = "$pastaBaseline\seed_$seed\fluxo_$fluxo\demanda\base.rou.xml"

        if ((Test-Path $baselineTrips) -and (Test-Path $baselineRoutes)) {
            Copy-Item $baselineTrips $baseTripsTeste -Force
            Copy-Item $baselineRoutes $baseRoutesTeste -Force
            Write-Host "[$seed/$fluxo] Demanda-base reutilizada do baseline."
        }
        else {
            Write-Host "[$seed/$fluxo] Baseline nao encontrado; regenerando demanda V2.3 deterministicamente."

            python $scriptDemanda `
                --net $rede `
                --config $configDemanda `
                --output-root $pastaGeracaoDemanda `
                --fluxo $fluxo `
                --seed $seed `
                --begin $inicioDemanda `
                --end $fimDemanda

            if ($LASTEXITCODE -ne 0) {
                throw "Erro ao gerar demanda em seed $seed / fluxo $fluxo."
            }

            $pastaGerada = "$pastaGeracaoDemanda\seed_$seed\fluxo_$fluxo\REF"
            $tripsGeradas = "$pastaGerada\demanda.trips.xml"
            $rotasGeradas = "$pastaGerada\rotas.rou.xml"

            if (-not (Test-Path $tripsGeradas) -or -not (Test-Path $rotasGeradas)) {
                throw "Arquivos de demanda nao encontrados após geracao para seed $seed / fluxo $fluxo."
            }

            Copy-Item $tripsGeradas $baseTripsTeste -Force
            Copy-Item $rotasGeradas $baseRoutesTeste -Force
        }

        $quantidade = (Select-String -Path $baseRoutesTeste -Pattern "<vehicle ").Count
        if ($quantidade -ne $fluxo) {
            throw "Seed $seed / fluxo ${fluxo}: esperados $fluxo veiculos, encontrados $quantidade."
        }

        foreach ($cenario in $cenarios) {
            $pastaCenario = "$pastaBaseTeste\$cenario"
            New-Item -ItemType Directory -Force $pastaCenario | Out-Null

            $rota = "$pastaCenario\rotas.rou.xml"

            Write-Host ""
            Write-Host "----------------------------------------"
            Write-Host " $NomeTeste | seed $seed | fluxo $fluxo | $cenario"
            Write-Host "----------------------------------------"

            # Mesma demanda-base. Apenas os tipos comportamentais
            # são atribuídos de acordo com a composição do cenario.
            python $scriptPerfis `
                --entrada $baseRoutesTeste `
                --saida $rota `
                --cenario $cenario `
                --seed $seed

            if ($LASTEXITCODE -ne 0) {
                throw "Erro na atribuicao de perfis em $seed / $fluxo / $cenario."
            }

            sumo `
                -n $rede `
                -r $rota `
                -a $perfis `
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
                throw "Erro na simulacao em $seed / $fluxo / $cenario."
            }
        }
    }
}

Write-Host ""
Write-Host "================================================================"
Write-Host " SENSIBILIDADE CONCLUÍDA"
Write-Host "================================================================"

python .\scripts\analisar_sensibilidade_perfis.py `
    --base $pastaSaida `
    --label $NomeTeste `
    --fluxos $Fluxos `
    --seeds $Seeds

if ($LASTEXITCODE -ne 0) {
    throw "Falha na analise dos resultados."
}
