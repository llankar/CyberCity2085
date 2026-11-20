param(
    [string]$Godot = 'E:\Godot\Godot_v4.6.3\Godot_v4.6.3-stable_win64_console.exe',
    [string]$Map = 'wasteland_outdoor_01_dust_road_ambush',
    [string]$Size = '2560x1440',
    [int]$Frames = 2400,
    [string]$ProjectDirectory,
    [string]$OutputDirectory
)
$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
$project = if ($ProjectDirectory) { (Resolve-Path -LiteralPath $ProjectDirectory).Path } else { Join-Path $root 'godot\combat_missions_ui' }
$out = if ($OutputDirectory) { [IO.Path]::GetFullPath($OutputDirectory) } else { Join-Path $root 'work\gpu-benchmark\system-sampled' }
New-Item -ItemType Directory -Force -Path $out | Out-Null
$stdout = Join-Path $out 'godot.stdout.log'
$stderr = Join-Path $out 'godot.stderr.log'
$fixture = Join-Path $root 'godot\combat_missions_ui\tests\capture_combat_21.gd'
$arguments = @('--path', ('"{0}"' -f $project), '--audio-driver', 'Dummy', '--script', ('"{0}"' -f $fixture), '--', '--all-maps', '--map', $Map, '--size', $Size, '--art-review', '--entities', '--gpu-benchmark', '--benchmark-frames', $Frames, '--output', ('"{0}"' -f $out))
$process = Start-Process -FilePath $Godot -ArgumentList $arguments -PassThru -NoNewWindow -RedirectStandardOutput $stdout -RedirectStandardError $stderr
$null = $process.Handle
$started = Get-Date
$rendererId = $process.Id
$consoleWrapper = [IO.Path]::GetFileNameWithoutExtension($Godot).EndsWith('_console')
$cpuSeconds = 0.0
$peakWorkingSet = 0L
$gpu = @()
$gpuMemory = @()
while (-not $process.HasExited) {
    $process.Refresh()
    if ($consoleWrapper -and $rendererId -eq $process.Id) {
        $child = Get-CimInstance Win32_Process -Filter "ParentProcessId=$($process.Id)" |
            Where-Object { $_.Name -eq ([IO.Path]::GetFileName($Godot) -replace '_console\.exe$', '.exe') } |
            Select-Object -First 1
        if ($child) { $rendererId = [int]$child.ProcessId }
    }
    $renderer = Get-Process -Id $rendererId -ErrorAction SilentlyContinue
    if ($renderer) {
        $cpuSeconds = [Math]::Max($cpuSeconds, $renderer.CPU)
        $peakWorkingSet = [Math]::Max($peakWorkingSet, $renderer.PeakWorkingSet64)
    }
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
$native = Get-Content (Join-Path $out 'native-report.json') -Raw | ConvertFrom-Json
$b = $native[0].gpu_benchmark
$completed = (Get-Content $stdout -Raw) -match 'COMBAT_21_CAPTURE_PASSED'
$result = [ordered]@{
    status = if ($completed -and $process.ExitCode -eq 0 -and $peakWorkingSet -gt 0 -and $b.adapter -match 'NVIDIA' -and $gpu.Count -gt 0 -and $b.frames -eq $Frames) { 'PASS' } else { 'FAIL' }
    measured_at = (Get-Date).ToString('o')
    godot = $Godot
    map = "$Map.png"
    resolution = $Size
    native = $b
    system = [ordered]@{
        logical_processors = [Environment]::ProcessorCount
        elapsed_seconds = [Math]::Round($elapsed, 3)
        process_cpu_seconds = [Math]::Round($cpuSeconds, 3)
        renderer_pid = $rendererId
        peak_renderer_working_set_mib = [Math]::Round($peakWorkingSet / 1MB, 2)
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
    limits = "CPU and process memory sample the benchmark renderer during startup and rendering. GPU load and VRAM are adapter-wide. Single Windows machine at $Size."
}
$result | ConvertTo-Json -Depth 8
if ($result.status -ne 'PASS') { exit 1 }
