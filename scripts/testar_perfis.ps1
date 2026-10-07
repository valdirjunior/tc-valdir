param(
    [int]$Seed = 42
)

$ErrorActionPreference = "Stop"

# ============================================================
# CONFIGURAÇÃO
# ============================================================

$rede = ".\config\nereu_ramos.net.xml"
$pesos = ".\config\demanda\demanda_1061"
$perfis = ".\config\perfis\perfis.add.xml"
$scriptPerfis = ".\scripts\atribuir_perfis.py"

$inicioDemanda = 0
$fimDemanda = 600
$fimSimulacao = 1200

# Por enquanto estamos validando os extremos + referência.
# Depois podemos incluir "EQU".
$cenarios = @("REF", "CAU", "AGR")

# Neste teste queremos analisar os fluxos ainda não avaliados.
$fluxos = @(300, 600)

# ============================================================
# PREPARAÇÃO
# ============================================================

Write-Host ""
Write-Host "========================================"
Write-Host " TESTE DE PERFIS - SEED $Seed"
Write-Host "========================================"
Write-Host ""

foreach ($fluxo in $fluxos) {

    # N veículos distribuídos ao longo de 600 s:
    # 300 -> período 2 s
    # 600 -> período 1 s
    # 750 -> período 0.8 s
    $periodo = $fimDemanda / $fluxo

    $pastaFluxo = ".\output\teste_perfis\analise_$fluxo"
    New-Item -ItemType Directory -Force $pastaFluxo | Out-Null

    $baseTrips = ".\output\teste_perfis\base_$fluxo.trips.xml"
    $baseRoutes = ".\output\teste_perfis\base_$fluxo.rou.xml"

    Write-Host ""
    Write-Host "----------------------------------------"
    Write-Host " Fluxo: $fluxo veículos"
    Write-Host " Período: $periodo s"
    Write-Host "----------------------------------------"

    # ========================================================
    # 1. GERAR DEMANDA BASE
    # ========================================================

    Write-Host "Gerando demanda base..."

    python "$env:SUMO_HOME\tools\randomTrips.py" `
        -n $rede `
        -o $baseTrips `
        -r $baseRoutes `
        -b $inicioDemanda `
        -e $fimDemanda `
        -p $periodo `
        --weights-prefix $pesos `
        --edge-permission passenger `
        --seed $Seed

    if ($LASTEXITCODE -ne 0) {
        throw "Erro ao gerar demanda para fluxo $fluxo."
    }

    # Confere quantidade realmente roteada
    $quantidade = (
        Select-String -Path $baseRoutes -Pattern "<vehicle "
    ).Count

    Write-Host "Veículos roteados: $quantidade / $fluxo"

    if ($quantidade -ne $fluxo) {
        throw "Esperados $fluxo veículos, mas foram encontrados $quantidade."
    }

    # ========================================================
    # 2. GERAR COMPOSIÇÕES
    # ========================================================

    foreach ($cenario in $cenarios) {

        $nome = $cenario.ToLower()
        $rota = ".\output\teste_perfis\${nome}_$fluxo.rou.xml"

        Write-Host ""
        Write-Host "Criando cenário $cenario..."

        python $scriptPerfis `
            --entrada $baseRoutes `
            --saida $rota `
            --cenario $cenario `
            --seed $Seed

        if ($LASTEXITCODE -ne 0) {
            throw "Erro ao atribuir perfis no cenário $cenario."
        }

        # ====================================================
        # 3. EXECUTAR SUMO
        # ====================================================

        Write-Host "Executando SUMO: $cenario / $fluxo..."

        sumo `
            -n $rede `
            -r $rota `
            -a $perfis `
            --begin 0 `
            --end $fimSimulacao `
            --step-length 0.1 `
            --time-to-impatience 90 `
            --seed $Seed `
            --collision.check-junctions true `
            --collision.action warn `
            --tripinfo-output "$pastaFluxo\${nome}_tripinfo.xml" `
            --statistic-output "$pastaFluxo\${nome}_stats.xml" `
            --summary-output "$pastaFluxo\${nome}_summary.xml" `
            --summary-output.period 1 `
            --queue-output "$pastaFluxo\${nome}_queues.xml" `
            --queue-output.period 1 `
            --lanechange-output "$pastaFluxo\${nome}_lanechanges.xml" `
            --collision-output "$pastaFluxo\${nome}_collisions.xml" `
            --error-log "$pastaFluxo\${nome}_warnings.log"

        if ($LASTEXITCODE -ne 0) {
            throw "Erro na simulação $cenario / $fluxo."
        }

        Write-Host "Concluído: $cenario / $fluxo"
    }
}

Write-Host ""
Write-Host "========================================"
Write-Host " TODOS OS TESTES FORAM CONCLUÍDOS"
Write-Host "========================================"