# One reviewed free hair-card source only; private experiment, not a redistributable asset pack.
$ErrorActionPreference='Stop'
$folder='E:\CyberCity2085-3d-lab\sources\blenderkit_hair157'
New-Item -ItemType Directory -Force -Path $folder | Out-Null
$meta=Invoke-RestMethod 'https://www.blendkit.com/api/v1/assets/0a91297d-d3c1-43a6-9d38-d1f00c352f00/'
if ($meta.id -ne '0a91297d-d3c1-43a6-9d38-d1f00c352f00' -or $meta.assetBaseId -ne '4793aff4-5e46-4902-a329-314731ebde09' -or -not $meta.isFree -or $meta.license -ne 'royalty_free') {
    throw 'Reviewed source identity/free status/license changed.'
}
$choices=@(
    @{kind='blend';name='source.blend';size=1852981;sha='679054e71464c47084e389aef1818caca0e6b686059f1833085c38243b6b0e94'},
    @{kind='gltf_godot';name='source_godot.glb';size=1068488;sha='0d758f3f7abdf396877f2bee0f1bc301219ea81937548d9d530d964843f07c9c'})
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
Short hair card — Salman Ramezani, Blendkit.
https://www.blendkit.com/asset-gallery-detail/4793aff4-5e46-4902-a329-314731ebde09/
Version 0a91297d-d3c1-43a6-9d38-d1f00c352f00, free Royalty Free asset; NOT CC0.
https://www.blendkit.com/docs/licenses/
https://www.blendkit.com/docs/licenses/licensing-faq/
Higher-level works/renders and games allowed subject to the published grant;
raw asset-pack/scene redistribution is not allowed, game files must not be easily extractable.
Private experimental source/derivatives only. No source/GLB/textures push or public asset-pack publication.
Downloaded via documented free asset API with scene_uuid; no token/authentication bypass.
Original sources preserved; adaptation/scalp fit/native/art validation remain separate.
'@
$notice | Set-Content -Encoding UTF8 (Join-Path $folder 'CREDITS.txt')
Write-Output 'HAIR157_PRIVATE_SOURCE_VERIFIED'
