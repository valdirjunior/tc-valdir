param(
    [int[]]$Seeds = @(42, 43, 44, 45, 46)
)

$ErrorActionPreference = "Stop"

$rede = ".\config\nereu_ramos.net.xml"
$perfis = ".\config\perfis\perfis.add.xml"

$cenarios = @(
    "REF",
    "EQU",
    "CAU",
    "AGR",
    "MIX_C",
    "MIX_N",
    "MIX_A"
)

foreach ($seed in $Seeds) {

    foreach ($cenario in $cenarios) {

        $rota = ".\output\experimentos\seed_$seed\fluxo_750\$cenario\rotas.rou.xml"

        $saida = ".\output\diagnostico_750\seed_$seed\$cenario"

        New-Item -ItemType Directory -Force $saida | Out-Null

        Write-Host ""
        Write-Host "Seed $seed / $cenario"

        sumo `
            -n $rede `
            -r $rota `
            -a $perfis `
            --begin 0 `
            --end 2400 `
            --step-length 0.1 `
            --time-to-impatience 90 `
            --time-to-teleport -1 `
            --seed $seed `
            --collision.check-junctions true `
            --collision.action warn `
            --tripinfo-output "$saida\tripinfo.xml" `
            --tripinfo-output.write-unfinished true `
            --statistic-output "$saida\stats.xml" `
            --summary-output "$saida\summary.xml" `
            --summary-output.period 1 `
            --collision-output "$saida\collisions.xml" `
            --error-log "$saida\warnings.log"

        if ($LASTEXITCODE -ne 0) {
            throw "Erro em seed=$seed / cenario=$cenario"
        }
    }
}

Write-Host ""
Write-Host "Diagnostico do fluxo 750 concluido."