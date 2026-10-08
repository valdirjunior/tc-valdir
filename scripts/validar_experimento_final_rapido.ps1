param(
    [string]$PastaSaida = ".\output\experimento_final\baseline_v1",
    [switch]$Detalhado
)

$ErrorActionPreference = "Stop"

if (-not (Test-Path $PastaSaida)) {
    throw "Pasta nao encontrada: $PastaSaida"
}

$cenariosEsperados = @("REF", "EQU", "CAU", "AGR", "MIX_C", "MIX_N", "MIX_A")
$arquivosObrigatorios = @(
    "rotas.rou.xml",
    "tripinfo.xml",
    "stats.xml",
    "summary.xml",
    "queues.xml",
    "lanechanges.xml",
    "collisions.xml",
    "warnings.log",
    "sumo.log",
    "execucao.txt",
    "EXECUCAO_OK.txt"
)

$registro = Join-Path $PastaSaida "registro_execucoes.csv"
if (-not (Test-Path $registro)) {
    throw "registro_execucoes.csv nao encontrado."
}

$linhasRegistro = @(Import-Csv $registro -Delimiter ";")

# ------------------------------------------------------------------
# Funcoes de leitura STREAMING.
# Nao carregam XMLs inteiros na memoria.
# ------------------------------------------------------------------

function Get-XmlElementCount {
    param(
        [Parameter(Mandatory=$true)][string]$Arquivo,
        [Parameter(Mandatory=$true)][string]$Elemento
    )

    $settings = New-Object System.Xml.XmlReaderSettings
    $settings.IgnoreComments = $true
    $settings.IgnoreWhitespace = $true
    $settings.DtdProcessing = [System.Xml.DtdProcessing]::Ignore

    $reader = [System.Xml.XmlReader]::Create($Arquivo, $settings)
    $count = 0

    try {
        while ($reader.Read()) {
            if ($reader.NodeType -eq [System.Xml.XmlNodeType]::Element -and
                $reader.Name -eq $Elemento) {
                $count++
            }
        }
    }
    finally {
        $reader.Close()
    }

    return $count
}

function Get-SummaryFinal {
    param(
        [Parameter(Mandatory=$true)][string]$Arquivo
    )

    $settings = New-Object System.Xml.XmlReaderSettings
    $settings.IgnoreComments = $true
    $settings.IgnoreWhitespace = $true
    $settings.DtdProcessing = [System.Xml.DtdProcessing]::Ignore

    $reader = [System.Xml.XmlReader]::Create($Arquivo, $settings)

    $ultimoTime = $null
    $ultimoEnded = $null
    $ultimoRunning = $null
    $ultimoLoaded = $null
    $achouStep = $false

    try {
        while ($reader.Read()) {
            if ($reader.NodeType -eq [System.Xml.XmlNodeType]::Element -and
                $reader.Name -eq "step") {

                $achouStep = $true

                $v = $reader.GetAttribute("time")
                if ($null -ne $v -and $v -ne "") { $ultimoTime = [double]$v }

                $v = $reader.GetAttribute("ended")
                if ($null -ne $v -and $v -ne "") { $ultimoEnded = [int]$v }

                $v = $reader.GetAttribute("running")
                if ($null -ne $v -and $v -ne "") { $ultimoRunning = [int]$v }

                $v = $reader.GetAttribute("loaded")
                if ($null -ne $v -and $v -ne "") { $ultimoLoaded = [int]$v }
            }
        }
    }
    finally {
        $reader.Close()
    }

    if (-not $achouStep) {
        throw "Summary sem elementos <step>."
    }

    return [pscustomobject]@{
        time = $ultimoTime
        ended = $ultimoEnded
        running = $ultimoRunning
        loaded = $ultimoLoaded
    }
}

function Test-FileNonEmpty {
    param([Parameter(Mandatory=$true)][string]$Arquivo)

    if (-not (Test-Path $Arquivo -PathType Leaf)) {
        return $false
    }

    return ((Get-Item $Arquivo).Length -gt 0)
}

# ------------------------------------------------------------------
# Cabecalho
# ------------------------------------------------------------------

Write-Host ""
Write-Host "================================================================"
Write-Host " VALIDACAO RAPIDA DO EXPERIMENTO FINAL"
Write-Host "================================================================"
Write-Host "Pasta: $PastaSaida"
Write-Host "Registros: $($linhasRegistro.Count)"
Write-Host ""

$statusAgrupado = $linhasRegistro | Group-Object status | Sort-Object Name
foreach ($grupo in $statusAgrupado) {
    Write-Host ("Status {0}: {1}" -f $grupo.Name, $grupo.Count)
}

$seeds = @($linhasRegistro.seed | Sort-Object -Unique)
$fluxos = @($linhasRegistro.fluxo | Sort-Object {[int]$_} -Unique)
$cenariosEncontrados = @($linhasRegistro.cenario | Sort-Object -Unique)

$esperadoPeloDesenho = $seeds.Count * $fluxos.Count * $cenariosEsperados.Count

Write-Host ""
Write-Host "Desenho detectado:"
Write-Host "  seeds:    $($seeds.Count) ($($seeds[0])..$($seeds[-1]))"
Write-Host "  fluxos:   $($fluxos -join ', ')"
Write-Host "  cenarios: $($cenariosEncontrados -join ', ')"
Write-Host "  esperado: $esperadoPeloDesenho execucoes"

$problemas = New-Object System.Collections.Generic.List[string]
$resultados = New-Object System.Collections.Generic.List[object]

if ($linhasRegistro.Count -ne $esperadoPeloDesenho) {
    $problemas.Add("Quantidade de registros diferente do desenho detectado: $($linhasRegistro.Count) != $esperadoPeloDesenho")
}

foreach ($cenario in $cenariosEsperados) {
    if ($cenario -notin $cenariosEncontrados) {
        $problemas.Add("Cenario ausente no registro: $cenario")
    }
}

$naoOk = @($linhasRegistro | Where-Object { $_.status -ne "OK" })
if ($naoOk.Count -gt 0) {
    $problemas.Add("Existem $($naoOk.Count) registros com status diferente de OK.")
}

# ------------------------------------------------------------------
# Validacao por execucao
# ------------------------------------------------------------------

$total = $linhasRegistro.Count
$indice = 0

foreach ($linha in $linhasRegistro) {
    $indice++

    if (($indice % 25) -eq 0 -or $indice -eq 1 -or $indice -eq $total) {
        $pct = [math]::Round(($indice / $total) * 100, 1)
        Write-Host ("Validando {0}/{1} ({2}%)..." -f $indice, $total, $pct)
    }

    $seed = [int]$linha.seed
    $fluxo = [int]$linha.fluxo
    $cenario = [string]$linha.cenario

    $pastaCenario = Join-Path $PastaSaida "seed_$seed\fluxo_$fluxo\$cenario"

    if (-not (Test-Path $pastaCenario -PathType Container)) {
        $problemas.Add("Pasta ausente: $pastaCenario")
        continue
    }

    foreach ($nome in $arquivosObrigatorios) {
        $arquivo = Join-Path $pastaCenario $nome

        if (-not (Test-Path $arquivo -PathType Leaf)) {
            $problemas.Add("Arquivo ausente: $arquivo")
            continue
        }

        # Logs podem legitimamente ser vazios; XMLs e metadados nao.
        if ($nome -notin @("warnings.log", "sumo.log")) {
            if (-not (Test-FileNonEmpty $arquivo)) {
                $problemas.Add("Arquivo vazio: $arquivo")
            }
        }
    }

    $rotas = Join-Path $pastaCenario "rotas.rou.xml"
    $tripinfo = Join-Path $pastaCenario "tripinfo.xml"
    $summary = Join-Path $pastaCenario "summary.xml"
    $collisions = Join-Path $pastaCenario "collisions.xml"
    $warnings = Join-Path $pastaCenario "warnings.log"

    $nRotas = $null
    $nTripinfo = $null
    $ended = $null
    $running = $null
    $loaded = $null
    $timeFinal = $null
    $nCollisions = 0
    $nEmergency = 0

    if (Test-Path $rotas) {
        try {
            $nRotas = Get-XmlElementCount -Arquivo $rotas -Elemento "vehicle"
            if ($nRotas -ne $fluxo) {
                $problemas.Add("seed=$seed fluxo=$fluxo cenario=${cenario}: rotas=$nRotas, esperado=$fluxo")
            }
        }
        catch {
            $problemas.Add("Falha ao ler rotas: seed=$seed fluxo=$fluxo cenario=$cenario -> $($_.Exception.Message)")
        }
    }

    if (Test-Path $tripinfo) {
        try {
            $nTripinfo = Get-XmlElementCount -Arquivo $tripinfo -Elemento "tripinfo"
            if ($nTripinfo -ne $fluxo) {
                $problemas.Add("seed=$seed fluxo=$fluxo cenario=${cenario}: tripinfo=$nTripinfo, esperado=$fluxo")
            }
        }
        catch {
            $problemas.Add("Falha ao ler tripinfo: seed=$seed fluxo=$fluxo cenario=$cenario -> $($_.Exception.Message)")
        }
    }

    if (Test-Path $summary) {
        try {
            $final = Get-SummaryFinal -Arquivo $summary
            $ended = $final.ended
            $running = $final.running
            $loaded = $final.loaded
            $timeFinal = $final.time

            if ($null -ne $ended -and $null -ne $running) {
                if (($ended + $running) -ne $fluxo) {
                    $problemas.Add("seed=$seed fluxo=$fluxo cenario=${cenario}: ended+running=$($ended+$running), esperado=$fluxo")
                }
            }
        }
        catch {
            $problemas.Add("Falha ao ler summary: seed=$seed fluxo=$fluxo cenario=$cenario -> $($_.Exception.Message)")
        }
    }

    if (Test-Path $collisions) {
        try {
            $nCollisions = Get-XmlElementCount -Arquivo $collisions -Elemento "collision"
        }
        catch {
            $problemas.Add("Falha ao ler collisions: seed=$seed fluxo=$fluxo cenario=$cenario -> $($_.Exception.Message)")
        }
    }

    if (Test-Path $warnings) {
        $nEmergency = @(Select-String -Path $warnings -Pattern "emergency braking" -SimpleMatch).Count
    }

    $resultados.Add([pscustomobject]@{
        seed = $seed
        fluxo = $fluxo
        cenario = $cenario
        rotas = $nRotas
        tripinfo = $nTripinfo
        ended = $ended
        running = $running
        loaded = $loaded
        time_final = $timeFinal
        emergency = $nEmergency
        collisions = $nCollisions
        status = $linha.status
    })
}

# ------------------------------------------------------------------
# Resumo
# ------------------------------------------------------------------

$resultadosArray = $resultados.ToArray()

$execucoesComRunning = @(
    $resultadosArray |
    Where-Object { $null -ne $_.running -and $_.running -gt 0 }
)

$execucoesComColisao = @(
    $resultadosArray |
    Where-Object { $_.collisions -gt 0 }
)

$totalEmergency = ($resultadosArray | Measure-Object emergency -Sum).Sum
if ($null -eq $totalEmergency) { $totalEmergency = 0 }

$totalCollisions = ($resultadosArray | Measure-Object collisions -Sum).Sum
if ($null -eq $totalCollisions) { $totalCollisions = 0 }

Write-Host ""
Write-Host "================================================================"
Write-Host " RESUMO"
Write-Host "================================================================"
Write-Host "Execucoes registradas:        $($linhasRegistro.Count)"
Write-Host "Execucoes verificadas:        $($resultadosArray.Count)"
Write-Host "Status OK:                    $(@($linhasRegistro | Where-Object {$_.status -eq 'OK'}).Count)"
Write-Host "Com veiculos ativos no fim:   $($execucoesComRunning.Count)"
Write-Host "Emergency braking (eventos):  $totalEmergency"
Write-Host "Colisoes (eventos):           $totalCollisions"
Write-Host "Problemas estruturais:        $($problemas.Count)"

if ($execucoesComRunning.Count -gt 0) {
    Write-Host ""
    Write-Host "Execucoes com running > 0:"
    $execucoesComRunning |
        Sort-Object fluxo, seed, cenario |
        Format-Table seed, fluxo, cenario, ended, running, tripinfo -AutoSize
}

if ($execucoesComColisao.Count -gt 0) {
    Write-Host ""
    Write-Host "Execucoes com colisao:"
    $execucoesComColisao |
        Sort-Object fluxo, seed, cenario |
        Format-Table seed, fluxo, cenario, collisions -AutoSize
}

if ($Detalhado) {
    Write-Host ""
    Write-Host "Todas as execucoes:"
    $resultadosArray |
        Sort-Object seed, fluxo, cenario |
        Format-Table seed, fluxo, cenario, rotas, tripinfo, ended, running, emergency, collisions, status -AutoSize
}

if ($problemas.Count -eq 0) {
    Write-Host ""
    Write-Host "================================================================"
    Write-Host " RESULTADO: PIPELINE VALIDADO"
    Write-Host " Nenhum problema estrutural encontrado."
    Write-Host "================================================================"
    exit 0
}
else {
    Write-Host ""
    Write-Host "================================================================"
    Write-Host " RESULTADO: PROBLEMAS ENCONTRADOS"
    Write-Host "================================================================"

    foreach ($p in $problemas) {
        Write-Host " - $p"
    }

    exit 1
}
