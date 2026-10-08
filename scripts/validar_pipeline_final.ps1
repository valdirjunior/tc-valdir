param(
    [string]$PastaSaida = ".\output\teste_pipeline_final"
)

$ErrorActionPreference = "Stop"

if (-not (Test-Path $PastaSaida)) {
    throw "Pasta nao encontrada: $PastaSaida"
}

$cenarios = @("REF", "EQU", "CAU", "AGR", "MIX_C", "MIX_N", "MIX_A")
$arquivosEssenciais = @("rotas.rou.xml", "tripinfo.xml", "stats.xml", "summary.xml", "queues.xml", "EXECUCAO_OK.txt")

$registro = Join-Path $PastaSaida "registro_execucoes.csv"
if (-not (Test-Path $registro)) {
    throw "registro_execucoes.csv nao encontrado."
}

$linhasRegistro = Import-Csv $registro -Delimiter ";"

Write-Host ""
Write-Host "================================================================"
Write-Host " VALIDACAO DO PIPELINE"
Write-Host "================================================================"
Write-Host "Pasta: $PastaSaida"
Write-Host "Registros: $($linhasRegistro.Count)"
Write-Host ""

$statusAgrupado = $linhasRegistro | Group-Object status | Sort-Object Name
foreach ($grupo in $statusAgrupado) {
    Write-Host ("Status {0}: {1}" -f $grupo.Name, $grupo.Count)
}

$resultados = @()
$problemas = New-Object System.Collections.Generic.List[string]

foreach ($linha in $linhasRegistro) {
    $seed = [int]$linha.seed
    $fluxo = [int]$linha.fluxo
    $cenario = $linha.cenario

    if ($cenario -notin $cenarios) {
        $problemas.Add("Cenario inesperado no registro: $cenario")
        continue
    }

    $pastaCenario = Join-Path $PastaSaida "seed_$seed\fluxo_$fluxo\$cenario"

    foreach ($nome in $arquivosEssenciais) {
        $arquivo = Join-Path $pastaCenario $nome
        if (-not (Test-Path $arquivo)) {
            $problemas.Add("Arquivo ausente: $arquivo")
        }
    }

    $rotas = Join-Path $pastaCenario "rotas.rou.xml"
    $tripinfo = Join-Path $pastaCenario "tripinfo.xml"
    $summary = Join-Path $pastaCenario "summary.xml"
    $stats = Join-Path $pastaCenario "stats.xml"
    $queues = Join-Path $pastaCenario "queues.xml"
    $collisions = Join-Path $pastaCenario "collisions.xml"
    $warnings = Join-Path $pastaCenario "warnings.log"

    $nRotas = $null
    $nTripinfo = $null
    $endedFinal = $null
    $runningFinal = $null
    $loadedFinal = $null
    $emergency = 0
    $nCollisions = 0

    try {
        [xml]$xmlRotas = Get-Content $rotas -Raw
        $nRotas = @($xmlRotas.SelectNodes("/routes/vehicle")).Count
        if ($nRotas -ne $fluxo) {
            $problemas.Add("seed=$seed fluxo=$fluxo cenario=${cenario}: rotas=$nRotas, esperado=$fluxo")
        }
    } catch {
        $problemas.Add("XML invalido em $rotas : $($_.Exception.Message)")
    }

    try {
        [xml]$xmlTrip = Get-Content $tripinfo -Raw
        $nTripinfo = @($xmlTrip.SelectNodes("/tripinfos/tripinfo")).Count

        # write-unfinished=true deve preservar um tripinfo por veiculo inserido.
        if ($nTripinfo -ne $fluxo) {
            $problemas.Add("seed=$seed fluxo=$fluxo cenario=${cenario}: tripinfo=$nTripinfo, esperado=$fluxo")
        }
    } catch {
        $problemas.Add("XML invalido em $tripinfo : $($_.Exception.Message)")
    }

    try {
        [xml]$xmlSummary = Get-Content $summary -Raw
        $steps = @($xmlSummary.SelectNodes("/summary/step"))
        if ($steps.Count -eq 0) {
            $problemas.Add("Summary sem steps: $summary")
        } else {
            $ultimo = $steps[-1]

            if ($null -ne $ultimo.ended -and "$($ultimo.ended)" -ne "") {
                $endedFinal = [int]$ultimo.ended
            }
            if ($null -ne $ultimo.running -and "$($ultimo.running)" -ne "") {
                $runningFinal = [int]$ultimo.running
            }
            if ($null -ne $ultimo.loaded -and "$($ultimo.loaded)" -ne "") {
                $loadedFinal = [int]$ultimo.loaded
            }

            if ($null -ne $endedFinal -and $null -ne $runningFinal) {
                if (($endedFinal + $runningFinal) -ne $fluxo) {
                    $problemas.Add("seed=$seed fluxo=$fluxo cenario=${cenario}: ended+running=$($endedFinal+$runningFinal), esperado=$fluxo")
                }
            }
        }
    } catch {
        $problemas.Add("XML invalido em $summary : $($_.Exception.Message)")
    }

    foreach ($arquivoXml in @($stats, $queues)) {
        try {
            [xml]$null = Get-Content $arquivoXml -Raw
        } catch {
            $problemas.Add("XML invalido em $arquivoXml : $($_.Exception.Message)")
        }
    }

    if (Test-Path $collisions) {
        try {
            [xml]$xmlCol = Get-Content $collisions -Raw
            $nCollisions = @($xmlCol.SelectNodes("/collisions/collision")).Count
        } catch {
            $problemas.Add("XML invalido em $collisions : $($_.Exception.Message)")
        }
    }

    if (Test-Path $warnings) {
        $emergency = @(Select-String -Path $warnings -Pattern "emergency braking" -SimpleMatch).Count
    }

    $resultados += [pscustomobject]@{
        seed = $seed
        fluxo = $fluxo
        cenario = $cenario
        rotas = $nRotas
        tripinfo = $nTripinfo
        ended = $endedFinal
        running = $runningFinal
        emergency = $emergency
        collisions = $nCollisions
        status = $linha.status
    }
}

Write-Host ""
Write-Host "Resumo por execucao:"
$resultados |
    Sort-Object seed, fluxo, cenario |
    Format-Table seed, fluxo, cenario, rotas, tripinfo, ended, running, emergency, collisions, status -AutoSize

Write-Host ""
Write-Host "Contagens de arquivos:"
foreach ($nome in @(
    "EXECUCAO_OK.txt",
    "tripinfo.xml",
    "stats.xml",
    "summary.xml",
    "queues.xml",
    "lanechanges.xml",
    "collisions.xml",
    "warnings.log",
    "sumo.log"
)) {
    $qtd = @(Get-ChildItem $PastaSaida -Recurse -File -Filter $nome).Count
    Write-Host ("  {0,-20} {1}" -f $nome, $qtd)
}

Write-Host ""
Write-Host "Totais diagnosticos:"
Write-Host ("  emergency braking: {0}" -f (($resultados | Measure-Object emergency -Sum).Sum))
Write-Host ("  collisions:        {0}" -f (($resultados | Measure-Object collisions -Sum).Sum))

Write-Host ""
if ($problemas.Count -eq 0) {
    Write-Host "================================================================"
    Write-Host " RESULTADO: PIPELINE VALIDADO"
    Write-Host " Nenhum problema estrutural encontrado."
    Write-Host "================================================================"
    exit 0
}
else {
    Write-Host "================================================================"
    Write-Host " RESULTADO: PROBLEMAS ENCONTRADOS"
    Write-Host "================================================================"

    foreach ($p in $problemas) {
        Write-Host " - $p"
    }

    exit 1
}
