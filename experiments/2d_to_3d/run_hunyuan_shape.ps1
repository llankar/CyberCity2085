param([Parameter(Mandatory=$true)][ValidateSet('stealth_vtol','rook_unarmed','robot','rook')][string]$Subject)
$ErrorActionPreference='Stop'
$lab='E:\CyberCity2085-3d-lab'
# Git may check shell files out as CRLF on Windows. Normalize only the E: runner.
$environment=[IO.File]::ReadAllText((Join-Path $PSScriptRoot 'trellis_env.sh')).Replace("`r",'')
$scriptPath=(Join-Path $PSScriptRoot 'run_hunyuan_shape.py').Replace('\','/')
$linuxScript='/mnt/'+$scriptPath.Substring(0,1).ToLower()+$scriptPath.Substring(2)
$environment+="`nexport HF_HUB_OFFLINE=1`n"
$environment+='export LD_LIBRARY_PATH=/mnt/e/CyberCity2085-3d-lab/venvs/hunyuan-shape/lib/python3.11/site-packages/torch/lib:$LD_LIBRARY_PATH'+"`n"
$environment+="/mnt/e/CyberCity2085-3d-lab/venvs/hunyuan-shape/bin/python '$linuxScript' '$Subject'`n"
$runner=Join-Path $lab 'tmp\hunyuan_shape_runner.sh'
[IO.File]::WriteAllText($runner,$environment,[Text.UTF8Encoding]::new($false))
& wsl.exe -e bash /mnt/e/CyberCity2085-3d-lab/tmp/hunyuan_shape_runner.sh
exit $LASTEXITCODE
