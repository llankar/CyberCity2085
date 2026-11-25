# One pinned publicly licensed scan; Windows certificate validation stays enabled.
$ErrorActionPreference = 'Stop'
$scanRoot = 'E:\CyberCity2085-3d-lab\sources\infinite_scan_head'
$revision = '150b6c46ebb6a011b93ed2e0fee9b612df78281b'
$baseUrl = "https://raw.githubusercontent.com/keijiro/InfiniteScan/$revision/Assets/InfiniteScan"
$files = @(
    @{Path='License.txt'; Bytes=1747},
    @{Path='Head.fbx'; Bytes=684896},
    @{Path='Textures/lambertian.jpg'; Bytes=8975275},
    @{Path='Textures/bump-lowRes.png'; Bytes=377110}
)
New-Item -ItemType Directory -Force -Path $scanRoot | Out-Null
$records = @()
foreach ($entry in $files) {
    $destination = Join-Path $scanRoot $entry.Path
    New-Item -ItemType Directory -Force -Path (Split-Path $destination) | Out-Null
    Invoke-WebRequest "$baseUrl/$($entry.Path)" -OutFile $destination -TimeoutSec 60
    if ((Get-Item -LiteralPath $destination).Length -ne $entry.Bytes) {
        throw "Pinned source size changed: $($entry.Path)"
    }
    if ($entry.Path -eq 'License.txt') {
        $notice = Get-Content -LiteralPath $destination -Raw
        if ($notice -notmatch 'Attribution 3.0' -or $notice -notmatch 'Lee Perry-Smith') {
            throw 'Grant differs from reviewed CC BY3 source; stop before model download'
        }
    }
    $records += @{Path=$entry.Path; Bytes=$entry.Bytes; SHA256=(Get-FileHash -LiteralPath $destination -Algorithm SHA256).Hash.ToLowerInvariant()}
}
@{Repository='https://github.com/keijiro/InfiniteScan'; Revision=$revision; License='CC-BY-3.0'; Files=$records; Scope='Original scan selected for anatomical review; not Rook likeness approval'} |
    ConvertTo-Json -Depth 5 | Set-Content -LiteralPath (Join-Path $scanRoot 'provenance.json') -Encoding UTF8
Write-Output "INFINITE_SCAN_ACQUIRED files=4 revision=$revision"
