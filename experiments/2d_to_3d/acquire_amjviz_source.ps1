param([switch]$IncludeBlenderSource)
$ErrorActionPreference='Stop'
# Private experiment only: royalty-free is not a raw-asset redistribution grant.
$destination='E:\CyberCity2085-3d-lab\sources\blenderkit_cyberpunk143'
New-Item -ItemType Directory -Force -Path $destination | Out-Null
$metadata=Invoke-RestMethod 'https://www.blendkit.com/api/v1/assets/3faea5ca-a58d-46c5-adc3-5ed1ef39dc44/'
if ($metadata.id -ne '3faea5ca-a58d-46c5-adc3-5ed1ef39dc44' -or -not $metadata.isFree -or $metadata.license -ne 'royalty_free') {
    throw 'Source identity/free status/license changed; review before downloading.'
}
$sceneId=[guid]::NewGuid().ToString()
$choices=@(@{kind='gltf_godot';name='source_godot.glb';size=28357000;sha='1b32cef27e37065117214bc8c670db8aeb46f64f318fe715e5d8034c76108e4d'})
if ($IncludeBlenderSource) {
    $choices+=@{kind='blend';name='source.blend';size=493590799;sha='331e5ef80c495dc11ac637c87a29d46bdf424ab7bc1cbed898151bb13489df94'}
}
foreach ($choice in $choices) {
    $target=Join-Path $destination $choice.name
    if (Test-Path -LiteralPath $target) {
        if ((Get-FileHash -LiteralPath $target -Algorithm SHA256).Hash.ToLowerInvariant() -ne $choice.sha) {
            throw "Existing source differs or is still downloading: $target. Preserved without overwrite."
        }
        Write-Output "Verified existing $($choice.name)"
        continue
    }
    $files=@($metadata.files | Where-Object fileType -eq $choice.kind)
    if ($files.Count -ne 1 -or $files[0].fileUploadSize -ne $choice.size) {throw 'Reviewed file metadata changed.'}
    $part=$target+'.part'
    if (Test-Path -LiteralPath $part) {throw "Existing partial download preserved: $part"}
    # The documented scene_uuid parameter is required even for public free files.
    $response=Invoke-RestMethod ($files[0].downloadUrl+'?scene_uuid='+$sceneId)
    if (-not $response.filePath -or ([uri]$response.filePath).Scheme -ne 'https') {throw 'No HTTPS download supplied.'}
    Invoke-WebRequest -UseBasicParsing $response.filePath -OutFile $part
    if ((Get-Item -LiteralPath $part).Length -ne $choice.size -or
        (Get-FileHash -LiteralPath $part -Algorithm SHA256).Hash.ToLowerInvariant() -ne $choice.sha) {
        throw "Downloaded source failed identity check; partial preserved: $part"
    }
    Move-Item -LiteralPath $part -Destination $target
    Write-Output "Downloaded and verified $($choice.name)"
}
$metadata | ConvertTo-Json -Depth 30 | Set-Content -Encoding UTF8 (Join-Path $destination 'metadata.json')
Write-Output 'Private royalty-free source acquired. Do not commit or publish raw files.'
