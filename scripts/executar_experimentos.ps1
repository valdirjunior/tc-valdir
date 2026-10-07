param(
    [int[]]$Seeds = @(42, 43, 44, 45, 46),
    [int[]]$Fluxos = @(650)
)

$ErrorActionPreference = "Stop"

# ============================================================
# Arquivos principais
# ============================================================

$rede = ".\config\nereu_ramos.net.xml"

$configDemanda = ".\config\demanda\demanda_v2.json"
$scriptDemanda = ".\scripts\gerar_demanda_v2.py"

$perfis = ".\config\perfis\perfis.add.xml"
$scriptPerfis = ".\scripts\atribuir_perfis.py"

# A geração v2 cria sua própria estrutura seed/fluxo/REF.
# Usamos esta pasta apenas como área temporária e depois copiamos
# os arquivos-base para a pasta oficial de cada experimento.
$pastaGeracaoDemanda = ".\output\_geracao_demanda_v2"

# ============================================================
# Tempos
# ============================================================

$inicioDemanda = 0
$fimDemanda = 600
$fimSimulacao = 1800

# ============================================================
# Cenários comportamentais
# ============================================================

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
    $perfis,
    $scriptPerfis
)

foreach ($arquivo in $arquivosObrigatorios) {
    if (-not (Test-Path $arquivo)) {
        throw "Arquivo obrigatório não encontrado: $arquivo"
    }
}

Write-Host ""
Write-Host "========================================"
Write-Host " EXECUÇÃO DOS EXPERIMENTOS"
Write-Host " Demanda: V2.1 ponderada"
Write-Host " Seeds: $($Seeds -join ', ')"
Write-Host " Fluxos: $($Fluxos -join ', ')"
Write-Host "========================================"

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
        Write-Host " Fluxo $fluxo - gerando demanda V2.1"
        Write-Host "----------------------------------------"

        # ----------------------------------------------------
        # Geração da demanda V2.1
        # ----------------------------------------------------
        #
        # O script:
        # - usa os pesos 5/4/3/2/1 do demanda_v2.json;
        # - aplica penalização aos retornos ao mesmo corredor;
        # - mantém os retornos possíveis;
        # - usa a mesma seed para garantir reprodutibilidade;
        # - distribui a demanda entre 0 e 600 s;
        # - roteia as viagens com duarouter.
        #
        # Essa demanda-base será reutilizada nas sete composições,
        # alterando apenas os perfis dos motoristas.

        python $scriptDemanda `
            --net $rede `
            --config $configDemanda `
            --output-root $pastaGeracaoDemanda `
            --fluxo $fluxo `
            --seed $seed `
            --begin $inicioDemanda `
            --end $fimDemanda

        if ($LASTEXITCODE -ne 0) {
            throw "Erro ao gerar demanda V2.1 para seed $seed / fluxo $fluxo."
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

        # Copia a realização da demanda para a pasta oficial do experimento.
        # Assim cada seed/fluxo mantém sua própria demanda-base registrada.
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
        # Execução das sete composições comportamentais
        # ----------------------------------------------------

        foreach ($cenario in $cenarios) {

            $pastaCenario = "$pastaBase\$cenario"

            New-Item `
                -ItemType Directory `
                -Force `
                $pastaCenario | Out-Null

            $rota = "$pastaCenario\rotas.rou.xml"

            Write-Host ""
            Write-Host "========================================"
            Write-Host " $seed / $fluxo / $cenario"
            Write-Host "========================================"

            # Mantém a mesma realização da demanda para todos os cenários
            # da mesma seed/fluxo e altera somente os tipos de motorista.
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
            #
            # Mantidos os parâmetros já usados nos testes:
            # - horizonte de 1800 s;
            # - step-length de 0,1 s;
            # - time-to-impatience = 90 s;
            # - teleporte desativado;
            # - colisões registradas sem remoção automática.

            sumo `
                -n $rede `
                -r $rota `
                -a $perfis `
                --begin 0 `
                --end $fimSimulacao `
                --step-length 0.1 `
                --time-to-impatience 90 `
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
Write-Host "========================================"
Write-Host " EXPERIMENTOS CONCLUÍDOS"
Write-Host "========================================"
