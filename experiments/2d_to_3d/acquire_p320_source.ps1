# One reviewed free prop only; private experiment, not a redistributable asset pack.
$ErrorActionPreference='Stop'
$folder='E:\CyberCity2085-3d-lab\sources\blenderkit_p320153'
New-Item -ItemType Directory -Force -Path $folder | Out-Null
$meta=Invoke-RestMethod 'https://www.blendkit.com/api/v1/assets/d1510159-defc-4546-aa3c-274dbc3fb165/'
if ($meta.id -ne 'd1510159-defc-4546-aa3c-274dbc3fb165' -or $meta.assetBaseId -ne '78f8c399-3f03-4ea8-b58f-da40b42c6b7f' -or -not $meta.isFree -or $meta.license -ne 'royalty_free') {
    throw 'Reviewed source identity/free status/license changed.'
}
$choices=@(
    @{kind='blend';name='source.blend';size=5550957;sha='5d662401f1cc9eba62027e13c5f7dacd3e0bda50a13f7e0862ee502d87dd47f5'},
    @{kind='gltf_godot';name='source_godot.glb';size=347464;sha='5effeaa2790659715399d4606e6f7d9d1084a6e5d945283448908ae5e11f6e9f'})
foreach ($choice in $choices) {
    $target=Join-Path $folder $choice.name
    if (Test-Path -LiteralPath $target) {
        if ((Get-FileHash -LiteralPath $target -Algorithm SHA256).Hash.ToLowerInvariant() -ne $choice.sha) {throw 'Existing source differs; preserve for inspection.'}
        Write-Output "Verified existing $($choice.name)";continue
    }
    $file=@($meta.files|Where-Object fileType -eq $choice.kind)
    if ($file.Count -ne 1 -or $file[0].fileUploadSize -ne $choice.size) {throw 'Reviewed file size/type changed.'}
    $part=$target+'.part';if (Test-Path -LiteralPath $part) {throw 'Preserve existing partial download.'}
    $download=Invoke-RestMethod ($file[0].downloadUrl+'?scene_uuid='+[guid]::NewGuid().ToString())
    if (-not $download.filePath -or ([uri]$download.filePath).Scheme -ne 'https') {throw 'HTTPS source required.'}
    Invoke-WebRequest -UseBasicParsing $download.filePath -OutFile $part
    if ((Get-Item -LiteralPath $part).Length -ne $choice.size -or (Get-FileHash -LiteralPath $part -Algorithm SHA256).Hash.ToLowerInvariant() -ne $choice.sha) {throw 'Downloaded source identity check failed; partial preserved.'}
    Move-Item -LiteralPath $part -Destination $target
}
$meta | ConvertTo-Json -Depth 30 | Set-Content -Encoding UTF8 (Join-Path $folder 'metadata.json')
$notice=@'
P320 Handgun — Zuhaib Khoso, Blendkit.
https://www.blendkit.com/asset-gallery-detail/78f8c399-3f03-4ea8-b58f-da40b42c6b7f/
Version d1510159-defc-4546-aa3c-274dbc3fb165, free Royalty Free asset; NOT CC0.
https://www.blendkit.com/docs/licenses/
https://www.blendkit.com/docs/licenses/licensing-faq/
Higher-level works/renders and games allowed subject to the published grant;
raw asset-pack/scene redistribution is not allowed, game files must not be easily extractable.
Private experimental source/derivatives only. No source/GLB/textures push or public asset-pack publication.
Downloaded via documented free asset API with scene_uuid; no token/authentication bypass.
Original sources preserved; adaptation/hand fit/native/art validation remain separate.
'@
$notice | Set-Content -Encoding UTF8 (Join-Path $folder 'CREDITS.txt')
Write-Output 'P320_PRIVATE_SOURCE_VERIFIED'
