param([string]$Output = 'E:/CyberCity2085-3d-lab/generated/phase2/renderpeople_nathan01/gpu_window.json', [string[]]$ProcessNames = @('Godot*'), [ValidateRange(1,240)][int]$SampleCount=24, [ValidateRange(100,1000)][int]$IntervalMilliseconds=400)
$ErrorActionPreference = 'Stop'
$target = [IO.Path]::GetFullPath($Output)
if (-not $target.StartsWith('E:\CyberCity2085-3d-lab\',[StringComparison]::OrdinalIgnoreCase)) {
    throw 'GPU evidence must stay inside the E: experiment directory.'
}
$samples = @()
for ($sampleIndex = 0; $sampleIndex -lt $SampleCount; $sampleIndex++) {
    $used = & nvidia-smi --id=0 --query-gpu=memory.used --format=csv,noheader,nounits
    if ($LASTEXITCODE -ne 0) { throw 'NVIDIA memory query failed' }
    $processIds = @(Get-Process -Name $ProcessNames -ErrorAction SilentlyContinue | ForEach-Object { $_.Id })
    $samples += [ordered]@{utc = (Get-Date).ToUniversalTime().ToString('o'); global_used_mib = [int]$used.Trim(); process_ids = $processIds; process_names = $ProcessNames; godot_process_ids = @(Get-Process -Name 'Godot*' -ErrorAction SilentlyContinue | ForEach-Object { $_.Id })}
    Start-Sleep -Milliseconds $IntervalMilliseconds
}
$evidence = [ordered]@{
    samples = $samples
    requested_sample_count = $SampleCount
    interval_milliseconds = $IntervalMilliseconds
    scope = 'Observed GPU-wide used memory on device0 and live requested process PIDs (Godot IDs retained separately). Not exclusive process VRAM, not a guaranteed allocation peak, and not GPU execution timing.'
}
$evidence | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath $target -Encoding UTF8
Write-Output "GPU_WINDOW_RECORDED $target"
