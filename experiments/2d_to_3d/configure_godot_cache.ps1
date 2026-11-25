$ErrorActionPreference = 'Stop'
$labRoot = [IO.Path]::GetFullPath('E:\CyberCity2085-3d-lab')
$appDataRoot = [IO.Path]::GetFullPath([Environment]::GetFolderPath('ApplicationData'))
$source = [IO.Path]::GetFullPath((Join-Path $appDataRoot 'Godot\app_userdata\CyberCity 2D to 3D Lab'))
$target = [IO.Path]::GetFullPath((Join-Path $labRoot 'godot-userdata'))
if (-not $source.StartsWith(($appDataRoot + '\'),[StringComparison]::OrdinalIgnoreCase) -or
    [IO.Path]::GetFileName($source) -ne 'CyberCity 2D to 3D Lab' -or
    -not $target.StartsWith(($labRoot + '\'),[StringComparison]::OrdinalIgnoreCase)) {
    throw 'Unexpected experiment user-data paths; no filesystem changes made.'
}
if (Test-Path -LiteralPath $source) {
    $existing = Get-Item -LiteralPath $source -Force
    if ($existing.LinkType) {
        $linkedTarget = [IO.Path]::GetFullPath([string]$existing.Target[0])
        if (-not $linkedTarget.StartsWith(($labRoot + '\'),[StringComparison]::OrdinalIgnoreCase)) {
            throw 'Existing experiment user-data link points outside the E: lab.'
        }
        Write-Output "GODOT_LAB_CACHE_ON_E $linkedTarget"
        return
    }
    if (@(Get-Process -Name 'Godot*' -ErrorAction SilentlyContinue).Count -gt 0) {
        throw 'Initial cache relocation requires no live Godot process; original data preserved.'
    }
    $files = @(Get-ChildItem -LiteralPath $source -Recurse -File -Force)
    if (-not (Test-Path -LiteralPath $target)) {
        Copy-Item -LiteralPath $source -Destination $target -Recurse
    }
    $targetFiles = @(Get-ChildItem -LiteralPath $target -Recurse -File -Force)
    if ($targetFiles.Count -ne $files.Count) { throw 'Cache copy count mismatch; original data preserved.' }
    foreach ($file in $files) {
        $relative = $file.FullName.Substring($source.Length + 1)
        $copied = [IO.Path]::GetFullPath((Join-Path $target $relative))
        if (-not $copied.StartsWith(($target + '\'),[StringComparison]::OrdinalIgnoreCase)) { throw 'Unexpected cache member path.' }
        if ((Get-FileHash -LiteralPath $file.FullName -Algorithm SHA256).Hash -ne
            (Get-FileHash -LiteralPath $copied -Algorithm SHA256).Hash) {
            throw 'Cache checksum mismatch; original data preserved.'
        }
    }
    # Both absolute paths checked above, exact lab directory only, copied data
    # verified before replacing this sole experiment directory with a junction.
    Remove-Item -LiteralPath $source -Recurse -Force
    $record = [ordered]@{utc=(Get-Date).ToUniversalTime().ToString('o'); source=$source; target=$target;
                         files=$files.Count; bytes=($files | Measure-Object -Property Length -Sum).Sum; sha256_verified=$true}
    $record | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $labRoot 'tmp\godot_userdata_migration.json') -Encoding UTF8
} else {
    New-Item -ItemType Directory -Force -Path $target | Out-Null
    New-Item -ItemType Directory -Force -Path ([IO.Path]::GetDirectoryName($source)) | Out-Null
}
New-Item -ItemType Junction -Path $source -Target $target | Out-Null
Write-Output "GODOT_LAB_CACHE_ON_E $target"
