param(
    [int[]]$Seeds = (1000..1029),
    [int[]]$Fluxos = @(300, 450, 625),
    [string]$PastaSaida = ".\output\experimento_final\baseline_v1",
    [switch]$Retomar,
    [switch]$Sobrescrever
)

$ErrorActionPreference = "Stop"

# ------------------------------------------------------------
# Cronometragem da coleta oficial
# ------------------------------------------------------------

$inicioExperimento = Get-Date
$cronometroExperimento = [System.Diagnostics.Stopwatch]::StartNew()

# ============================================================
# EXPERIMENTO FINAL - TC
#
# Objetivo deste script:
# - executar as simulacoes oficiais;
# - preservar as saidas brutas;
# - NAO realizar analise estatistica;
# - NAO alterar rede, demanda ou perfis durante a coleta.
#
# Seeds oficiais padrao: 1000..1029 (30 repeticoes).
# O numero 1000 e apenas uma convencao organizacional.
# ============================================================

$rede = ".\config\nereu_ramos.net.xml"
$configDemanda = ".\config\demanda\demanda_v2.json"
$perfis = ".\config\perfis\perfis_final.add.xml"

$scriptDemanda = ".\scripts\gerar_demanda_v2.py"
$scriptPerfis = ".\scripts\atribuir_perfis.py"

$inicioDemanda = 0
$fimDemanda = 600
$fimSimulacao = 1800
$passo = 0.1
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
    $perfis,
    $scriptDemanda,
    $scriptPerfis
)

foreach ($arquivo in $arquivosObrigatorios) {
    if (-not (Test-Path $arquivo)) {
        throw "Arquivo obrigatorio nao encontrado: $arquivo"
    }
}

# ------------------------------------------------------------
# Protecao contra sobrescrita acidental
# ------------------------------------------------------------

if ((Test-Path $PastaSaida) -and -not $Retomar -and -not $Sobrescrever) {
    $conteudo = Get-ChildItem $PastaSaida -Force -ErrorAction SilentlyContinue
    if ($conteudo) {
        throw @"
A pasta de saida ja existe e nao esta vazia:
$PastaSaida

Use:
  -Retomar       para continuar uma coleta interrompida
ou
  -Sobrescrever  para apagar a pasta e iniciar novamente.
"@
    }
}

if ($Sobrescrever -and (Test-Path $PastaSaida)) {
    Write-Host "Removendo coleta anterior: $PastaSaida"
    Remove-Item $PastaSaida -Recurse -Force
}

New-Item -ItemType Directory -Force $PastaSaida | Out-Null

# Pasta temporaria apenas para a saida intermediaria do gerador V2.
$pastaGeracaoTemp = ".\output\_tmp_experimento_final"
New-Item -ItemType Directory -Force $pastaGeracaoTemp | Out-Null

# ------------------------------------------------------------
# Snapshot da configuracao e manifesto de reproducibilidade
# ------------------------------------------------------------

$pastaSnapshot = Join-Path $PastaSaida "_config_snapshot"
New-Item -ItemType Directory -Force $pastaSnapshot | Out-Null

Copy-Item $rede (Join-Path $pastaSnapshot "nereu_ramos.net.xml") -Force
Copy-Item $configDemanda (Join-Path $pastaSnapshot "demanda_v2.json") -Force
Copy-Item $perfis (Join-Path $pastaSnapshot "perfis_final.add.xml") -Force
Copy-Item $scriptDemanda (Join-Path $pastaSnapshot "gerar_demanda_v2.py") -Force
Copy-Item $scriptPerfis (Join-Path $pastaSnapshot "atribuir_perfis.py") -Force

if ($PSCommandPath -and (Test-Path $PSCommandPath)) {
    Copy-Item $PSCommandPath (Join-Path $pastaSnapshot "executar_experimento_final.ps1") -Force
}

$gitCommit = "indisponivel"
$gitStatus = "indisponivel"
try {
    $gitCommit = (git rev-parse HEAD 2>$null | Out-String).Trim()
    $gitStatus = (git status --porcelain 2>$null | Out-String).Trim()
    if ([string]::IsNullOrWhiteSpace($gitStatus)) {
        $gitStatus = "working tree clean"
    }
} catch {}

$sumoVersion = "indisponivel"
try {
    $sumoVersion = (sumo --version 2>&1 | Out-String).Trim()
} catch {
    throw "Nao foi possivel executar 'sumo --version'. Verifique o PATH do SUMO."
}

$hashRede = (Get-FileHash $rede -Algorithm SHA256).Hash
$hashDemanda = (Get-FileHash $configDemanda -Algorithm SHA256).Hash
$hashPerfis = (Get-FileHash $perfis -Algorithm SHA256).Hash
$hashGerador = (Get-FileHash $scriptDemanda -Algorithm SHA256).Hash
$hashAtribuidor = (Get-FileHash $scriptPerfis -Algorithm SHA256).Hash

$manifesto = @"
EXPERIMENTO FINAL - TC
======================

Criado em: $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")

Seeds:
$($Seeds -join ", ")

Fluxos/demandas:
$($Fluxos -join ", ")

Cenarios:
$($cenarios -join ", ")

Demanda:
inicio = $inicioDemanda s
fim = $fimDemanda s

Simulacao:
fim = $fimSimulacao s
step-length = $passo s
time-to-impatience = $timeToImpatience s
time-to-teleport = -1
collision.check-junctions = true
collision.action = warn
tripinfo-output.write-unfinished = true

Perfis:
arquivo = $perfis
jmTimegapMinor = 0.80 nos tres perfis
lcStrategic = 1.0 nos tres perfis
lcStrategicLookahead = padrao do SUMO

Git:
commit = $gitCommit
status =
$gitStatus

SHA256:
rede = $hashRede
demanda = $hashDemanda
perfis = $hashPerfis
gerador_demanda = $hashGerador
atribuidor_perfis = $hashAtribuidor

SUMO:
$sumoVersion

OBSERVACAO:
Os numeros das seeds sao identificadores de inicializacao do
gerador pseudoaleatorio. A escolha da faixa 1000..1029 e
organizacional e foi definida antes da coleta oficial.
"@

$manifesto | Set-Content (Join-Path $PastaSaida "manifesto.txt") -Encoding UTF8

# Registro simples das execucoes.
$registro = Join-Path $PastaSaida "registro_execucoes.csv"
if (-not (Test-Path $registro) -or $Sobrescrever) {
    "seed;fluxo;cenario;inicio;fim;exit_code;status" |
        Set-Content $registro -Encoding UTF8
}

Write-Host ""
Write-Host "================================================================"
Write-Host " EXPERIMENTO FINAL"
Write-Host "================================================================"
Write-Host "Seeds:   $($Seeds -join ', ')"
Write-Host "Fluxos:  $($Fluxos -join ', ')"
Write-Host "Cenarios: $($cenarios -join ', ')"
Write-Host "Saida:   $PastaSaida"
Write-Host "Perfis:  $perfis"
Write-Host "Git:     $gitCommit"
Write-Host "================================================================"
Write-Host ""

# ------------------------------------------------------------
# Funcao: gera (ou reutiliza) a demanda-base da seed/fluxo
# ------------------------------------------------------------

function Obter-DemandaBase {
    param(
        [int]$Seed,
        [int]$Fluxo,
        [string]$PastaFluxo
    )

    $pastaDemanda = Join-Path $PastaFluxo "demanda"
    New-Item -ItemType Directory -Force $pastaDemanda | Out-Null

    $tripsBase = Join-Path $pastaDemanda "base.trips.xml"
    $rotasBase = Join-Path $pastaDemanda "base.rou.xml"

    $demandaValida = $false

    if ((Test-Path $tripsBase) -and (Test-Path $rotasBase)) {
        $quantidadeExistente = (Select-String -Path $rotasBase -Pattern "<vehicle ").Count
        if ($quantidadeExistente -eq $Fluxo) {
            $demandaValida = $true
        }
    }

    if (-not $demandaValida) {
        Write-Host "[seed $Seed / fluxo $Fluxo] Gerando demanda-base V2.3..."

        # IMPORTANTE:
        # Esta funcao retorna somente o caminho de rotasBase.
        # A saida textual do gerador precisa ser consumida aqui;
        # caso contrario, o PowerShell a inclui no valor retornado
        # pela funcao e ela acaba sendo enviada como argumento para
        # atribuir_perfis.py.
        $saidaGerador = & python $scriptDemanda `
            --net $rede `
            --config $configDemanda `
            --output-root $pastaGeracaoTemp `
            --fluxo $Fluxo `
            --seed $Seed `
            --begin $inicioDemanda `
            --end $fimDemanda 2>&1

        $exitGerador = $LASTEXITCODE

        foreach ($linha in $saidaGerador) {
            Write-Host $linha
        }

        if ($exitGerador -ne 0) {
            throw "Erro ao gerar demanda em seed $Seed / fluxo $Fluxo."
        }

        $pastaGerada = Join-Path $pastaGeracaoTemp "seed_$Seed\fluxo_$Fluxo\REF"
        $tripsGeradas = Join-Path $pastaGerada "demanda.trips.xml"
        $rotasGeradas = Join-Path $pastaGerada "rotas.rou.xml"

        if (-not (Test-Path $tripsGeradas)) {
            throw "Trips geradas nao encontradas para seed $Seed / fluxo $Fluxo."
        }

        if (-not (Test-Path $rotasGeradas)) {
            throw "Rotas geradas nao encontradas para seed $Seed / fluxo $Fluxo."
        }

        Copy-Item $tripsGeradas $tripsBase -Force
        Copy-Item $rotasGeradas $rotasBase -Force
    }
    else {
        Write-Host "[seed $Seed / fluxo $Fluxo] Demanda-base ja existe e foi validada."
    }

    $quantidade = (Select-String -Path $rotasBase -Pattern "<vehicle ").Count
    if ($quantidade -ne $Fluxo) {
        throw "Seed $Seed / fluxo ${Fluxo}: esperados $Fluxo veiculos, encontrados $quantidade."
    }

    return [string]$rotasBase
}

# ------------------------------------------------------------
# Execucoes
# ------------------------------------------------------------

$totalExecucoes = $Seeds.Count * $Fluxos.Count * $cenarios.Count
$indiceExecucao = 0

foreach ($seed in $Seeds) {
    foreach ($fluxo in $Fluxos) {

        $pastaFluxo = Join-Path $PastaSaida "seed_$seed\fluxo_$fluxo"
        New-Item -ItemType Directory -Force $pastaFluxo | Out-Null

        $rotasBase = Obter-DemandaBase -Seed $seed -Fluxo $fluxo -PastaFluxo $pastaFluxo

        foreach ($cenario in $cenarios) {
            $indiceExecucao++

            $pastaCenario = Join-Path $pastaFluxo $cenario
            $marcadorOK = Join-Path $pastaCenario "EXECUCAO_OK.txt"

            if ($Retomar -and (Test-Path $marcadorOK)) {
                Write-Host "[$indiceExecucao/$totalExecucoes] seed=$seed fluxo=$fluxo cenario=$cenario -> ja concluido, pulando."
                continue
            }

            # Se a execucao estava incompleta, limpa somente a pasta do cenario.
            if (Test-Path $pastaCenario) {
                Remove-Item $pastaCenario -Recurse -Force
            }
            New-Item -ItemType Directory -Force $pastaCenario | Out-Null

            $rotaCenario = Join-Path $pastaCenario "rotas.rou.xml"

            Write-Host ""
            Write-Host "================================================================"
            Write-Host " [$indiceExecucao/$totalExecucoes]"
            Write-Host " seed=$seed | fluxo=$fluxo | cenario=$cenario"
            Write-Host "================================================================"

            # A mesma demanda-base e usada para os sete cenarios.
            # Muda somente a composicao dos tipos comportamentais.
            python $scriptPerfis `
                --entrada $rotasBase `
                --saida $rotaCenario `
                --cenario $cenario `
                --seed $seed

            if ($LASTEXITCODE -ne 0) {
                throw "Erro na atribuicao de perfis: seed $seed / fluxo $fluxo / cenario $cenario."
            }

            $inicioExec = Get-Date

            $tripinfo = Join-Path $pastaCenario "tripinfo.xml"
            $stats = Join-Path $pastaCenario "stats.xml"
            $summary = Join-Path $pastaCenario "summary.xml"
            $queues = Join-Path $pastaCenario "queues.xml"
            $lanechanges = Join-Path $pastaCenario "lanechanges.xml"
            $collisions = Join-Path $pastaCenario "collisions.xml"
            $warnings = Join-Path $pastaCenario "warnings.log"
            $sumolog = Join-Path $pastaCenario "sumo.log"

            sumo `
                -n $rede `
                -r $rotaCenario `
                -a $perfis `
                --begin 0 `
                --end $fimSimulacao `
                --step-length $passo `
                --seed $seed `
                --time-to-impatience $timeToImpatience `
                --time-to-teleport -1 `
                --collision.check-junctions true `
                --collision.action warn `
                --tripinfo-output $tripinfo `
                --tripinfo-output.write-unfinished true `
                --statistic-output $stats `
                --summary-output $summary `
                --summary-output.period 1 `
                --queue-output $queues `
                --queue-output.period 1 `
                --lanechange-output $lanechanges `
                --collision-output $collisions `
                --error-log $warnings `
                --log $sumolog `
                --no-step-log true

            $exitCode = $LASTEXITCODE
            $fimExec = Get-Date

            if ($exitCode -ne 0) {
                "$seed;$fluxo;$cenario;$($inicioExec.ToString('s'));$($fimExec.ToString('s'));$exitCode;ERRO_SUMO" |
                    Add-Content $registro -Encoding UTF8

                throw "SUMO retornou erro: seed $seed / fluxo $fluxo / cenario $cenario."
            }

            # Saidas essenciais para as metricas previstas no PTC.
            $saidasEssenciais = @(
                $tripinfo,
                $stats,
                $summary,
                $queues
            )

            foreach ($saida in $saidasEssenciais) {
                if (-not (Test-Path $saida)) {
                    "$seed;$fluxo;$cenario;$($inicioExec.ToString('s'));$($fimExec.ToString('s'));$exitCode;SAIDA_AUSENTE" |
                        Add-Content $registro -Encoding UTF8

                    throw "Saida essencial ausente: $saida"
                }
            }

            # Metadados da execucao individual.
            @"
seed=$seed
fluxo=$fluxo
cenario=$cenario
inicio=$($inicioExec.ToString("s"))
fim=$($fimExec.ToString("s"))
sim_end=$fimSimulacao
demand_begin=$inicioDemanda
demand_end=$fimDemanda
step_length=$passo
time_to_impatience=$timeToImpatience
jmTimegapMinor=0.80
perfil_file=$perfis
git_commit=$gitCommit
"@ | Set-Content (Join-Path $pastaCenario "execucao.txt") -Encoding UTF8

            "OK - $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" |
                Set-Content $marcadorOK -Encoding UTF8

            "$seed;$fluxo;$cenario;$($inicioExec.ToString('s'));$($fimExec.ToString('s'));$exitCode;OK" |
                Add-Content $registro -Encoding UTF8
        }
    }
}

Write-Host ""
Write-Host "================================================================"
Write-Host " COLETA FINAL CONCLUIDA"
Write-Host "================================================================"
Write-Host "Pasta: $PastaSaida"
Write-Host "Registro: $registro"
Write-Host "Manifesto: $(Join-Path $PastaSaida 'manifesto.txt')"
Write-Host ""
Write-Host "Este script NAO analisa os resultados."
Write-Host "A analise sera executada posteriormente a partir dos XMLs salvos."
Write-Host "================================================================"

# ------------------------------------------------------------
# Finaliza e registra o tempo total da coleta
# ------------------------------------------------------------

$cronometroExperimento.Stop()
$fimExperimento = Get-Date

$arquivoTempo = Join-Path $PastaSaida "tempo_execucao.txt"

$registroTempo = @"
EXPERIMENTO FINAL - TEMPO DE EXECUCAO
=====================================

Inicio: $($inicioExperimento.ToString("yyyy-MM-dd HH:mm:ss"))
Fim: $($fimExperimento.ToString("yyyy-MM-dd HH:mm:ss"))

Duracao:
$($cronometroExperimento.Elapsed.ToString())

Duracao em minutos:
$([math]::Round($cronometroExperimento.Elapsed.TotalMinutes, 2))

Duracao em horas:
$([math]::Round($cronometroExperimento.Elapsed.TotalHours, 3))

Numero de execucoes previstas:
$($Seeds.Count * $Fluxos.Count * $cenarios.Count)
"@

$registroTempo | Set-Content $arquivoTempo -Encoding UTF8

Write-Host ""
Write-Host "Tempo total da coleta:"
Write-Host "  Inicio:  $($inicioExperimento.ToString('yyyy-MM-dd HH:mm:ss'))"
Write-Host "  Fim:     $($fimExperimento.ToString('yyyy-MM-dd HH:mm:ss'))"
Write-Host "  Duracao: $($cronometroExperimento.Elapsed)"
Write-Host "  Horas:   $([math]::Round($cronometroExperimento.Elapsed.TotalHours, 3))"
Write-Host ""
Write-Host "Tempo salvo em: $arquivoTempo"