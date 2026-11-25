param([switch]$BenchmarksOnly)
$ErrorActionPreference = 'Stop'
$lab = 'E:/CyberCity2085-3d-lab/generated/phase2'
$output = Join-Path $lab 'texture_review155'
New-Item -ItemType Directory -Force $output | Out-Null
$variants = @('amjviz_wardrobe150','amjviz_budget154_1024')
if (-not $BenchmarksOnly) {
    foreach ($variant in $variants) {
        foreach ($facing in @('front','side','back')) {
            & (Join-Path $PSScriptRoot 'run_godot.ps1') -Scene res://main.tscn -SceneArguments @("--model=$lab/$variant/human_actions.glb",'--neutral',"--view=$facing",'--clip=Hard stand','--clip-fraction=0','--ortho-size=2.05',"--capture=$output/${variant}_${facing}.png")
            if ($LASTEXITCODE -ne 0) { throw "Native render failed: $variant/$facing" }
        }
    }
}
# Sequential native processes: never overlap this pair with other GPU experiments.
foreach ($variant in @('source','budget')) {
    $humanFlag = if ($variant -eq 'source') {'--wardrobe150-study'} else {'--wardrobe-budget154'}
    & (Join-Path $PSScriptRoot 'run_godot.ps1') -SceneArguments @($humanFlag,'--robot-action-bundle','--source-opacity-study','--tactical','--facades-study',"--benchmark-output=$output/${variant}_benchmark.json","--capture=$output/${variant}_tactical.png")
    if ($LASTEXITCODE -ne 0) { throw "Benchmark failed: $variant" }
}
