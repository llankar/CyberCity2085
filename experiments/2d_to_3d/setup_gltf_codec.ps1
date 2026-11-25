$ErrorActionPreference='Stop'
$codecRoot='E:/CyberCity2085-3d-lab/tools/gltf_codec'
New-Item -ItemType Directory -Force -Path $codecRoot | Out-Null
foreach($codecFolder in @('E:/CyberCity2085-3d-lab/tmp','E:/CyberCity2085-3d-lab/cache/npm')) {
    New-Item -ItemType Directory -Force -Path $codecFolder | Out-Null
}
$env:TEMP='E:/CyberCity2085-3d-lab/tmp'
$env:TMP=$env:TEMP
$env:npm_config_cache='E:/CyberCity2085-3d-lab/cache/npm'
& npm.cmd install --prefix $codecRoot --ignore-scripts --no-audit --no-fund '@gltf-transform/core@4.5.1' '@gltf-transform/extensions@4.5.1' '@gltf-transform/functions@4.5.1' 'meshoptimizer@1.3.0' 'sharp@0.35.5'
exit $LASTEXITCODE
