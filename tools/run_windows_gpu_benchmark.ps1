param(
    [string]$Godot = 'E:\Godot\Godot_v4.6.3\Godot_v4.6.3-stable_win64_console.exe',
    [string]$Map = 'wasteland_outdoor_01_dust_road_ambush',
    [string]$Size = '2560x1440',
    [int]$Frames = 2400
)
$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
$out = Join-Path $root 'work\gpu-benchmark\system-sampled'
$report = Join-Path $root 'docs\reports\windows_gpu_benchmark_system.json'
New-Item -ItemType Directory -Force -Path $out | Out-Null
$stdout = Join-Path $out 'godot.stdout.log'
$stderr = Join-Path $out 'godot.stderr.log'
$arguments = @('--path', (Join-Path $root 'godot\combat_missions_ui'), '--audio-driver', 'Dummy', '--script', 'tests/capture_combat_21.gd', '--', '--all-maps', '--map', $Map, '--size', $Size, '--art-review', '--entities', '--gpu-benchmark', '--benchmark-frames', $Frames, '--output', $out)
$process = Start-Process -FilePath $Godot -ArgumentList $arguments -PassThru -NoNewWindow -RedirectStandardOutput $stdout -RedirectStandardError $stderr
$started = Get-Date
$cpuStart = $null
$cpuLast = 0.0
$gpu = @()
$gpuMemory = @()
while (-not $process.HasExited) {
    $process.Refresh()
    $cpuNow = (Get-Process 'Godot_v4.6.3-stable_win64*' -ErrorAction SilentlyContinue | Measure-Object -Property CPU -Sum).Sum
    if ($null -eq $cpuNow) { $cpuNow = 0.0 }
    if ($null -eq $cpuStart) { $cpuStart = $cpuNow }
    $cpuLast = $cpuNow
    $sample = & nvidia-smi --query-gpu=utilization.gpu,memory.used --format=csv,noheader,nounits 2>$null | Select-Object -First 1
    if ($sample -match '^\s*([0-9]+)\s*,\s*([0-9]+)') {
        $gpu += [int]$Matches[1]
        $gpuMemory += [int]$Matches[2]
    }
    Start-Sleep -Milliseconds 500
}
$process.WaitForExit()
$process.Refresh()
$elapsed = ((Get-Date) - $started).TotalSeconds
$cpuSeconds = [Math]::Max(0.0, $cpuLast - $(if ($null -eq $cpuStart) { 0.0 } else { $cpuStart }))
$native = Get-Content (Join-Path $out 'native-report.json') -Raw | ConvertFrom-Json
$b = $native[0].gpu_benchmark
$completed = (Get-Content $stdout -Raw) -match 'COMBAT_21_CAPTURE_PASSED'
$result = [ordered]@{
    status = if ($completed -and $b.adapter -match 'NVIDIA' -and $gpu.Count -gt 0 -and $b.frames -eq $Frames) { 'PASS' } else { 'FAIL' }
    measured_at = (Get-Date).ToString('o')
    godot = $Godot
    map = "$Map.png"
    resolution = $Size
    native = $b
    system = [ordered]@{
        logical_processors = [Environment]::ProcessorCount
        elapsed_seconds = [Math]::Round($elapsed, 3)
        process_cpu_seconds = [Math]::Round($cpuSeconds, 3)
        average_total_cpu_percent = [Math]::Round(($cpuSeconds / [Math]::Max($elapsed, .001) / [Environment]::ProcessorCount) * 100.0, 2)
        gpu_samples = $gpu.Count
        average_gpu_percent = if ($gpu.Count) { [Math]::Round(($gpu | Measure-Object -Average).Average, 2) } else { $null }
        peak_gpu_percent = if ($gpu.Count) { ($gpu | Measure-Object -Maximum).Maximum } else { $null }
        average_gpu_memory_mib = if ($gpuMemory.Count) { [Math]::Round(($gpuMemory | Measure-Object -Average).Average, 2) } else { $null }
        peak_gpu_memory_mib = if ($gpuMemory.Count) { ($gpuMemory | Measure-Object -Maximum).Maximum } else { $null }
    }
    wrapper_exit_code = $process.ExitCode
    completion_marker = $completed
    stdout = (Resolve-Path $stdout).Path
    stderr = (Resolve-Path $stderr).Path
    limits = 'Single Windows machine and representative animated 1440p combat; this does not establish minimum-spec performance.'
}
$result | ConvertTo-Json -Depth 8 | Set-Content -Encoding utf8 $report
$result | ConvertTo-Json -Depth 8
if ($result.status -ne 'PASS') { exit 1 }
