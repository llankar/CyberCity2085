// Offline asset conversion only. Dependencies and all outputs remain on E:.
import {createRequire} from 'node:module';
import fs from 'node:fs/promises';
import crypto from 'node:crypto';
const require=createRequire('E:/CyberCity2085-3d-lab/tools/gltf_codec/package.json');
const {NodeIO}=require('@gltf-transform/core');
const {ALL_EXTENSIONS}=require('@gltf-transform/extensions');
const {dequantize,getBounds}=require('@gltf-transform/functions');
const {MeshoptDecoder}=require('meshoptimizer');
const sharp=require('sharp');
const source='E:/CyberCity2085-3d-lab/sources/trebejo_jacket/';
const out='E:/CyberCity2085-3d-lab/generated/phase2/trebejo_jacket/';
await fs.mkdir(out,{recursive:true});
const provenance=JSON.parse(await fs.readFile(source+'provenance.json','utf8'));
const payload=await fs.readFile(source+'jacket_source.glb');
if(crypto.createHash('sha256').update(payload).digest('hex')!==provenance.sha256)throw new Error('Source hash mismatch');
await MeshoptDecoder.ready;
const io=new NodeIO().registerExtensions(ALL_EXTENSIONS).registerDependencies({'meshopt.decoder':MeshoptDecoder});
const doc=await io.readBinary(payload);
const before=getBounds(doc.getRoot().listScenes()[0]);
const images=[];
for(const texture of doc.getRoot().listTextures()){
  const input=texture.getImage();
  const original=await sharp(input).ensureAlpha().raw().toBuffer();
  const png=await sharp(input).png().toBuffer();
  const decoded=await sharp(png).ensureAlpha().raw().toBuffer();
  if(!original.equals(decoded))throw new Error('Texture decoded pixels changed');
  const info=await sharp(png).metadata();
  images.push({width:info.width,height:info.height,rgba_sha256:crypto.createHash('sha256').update(decoded).digest('hex')});
  texture.setImage(png).setMimeType('image/png');
}
await doc.transform(dequantize());
const normalized=new Set();
for(const mesh of doc.getRoot().listMeshes())for(const primitive of mesh.listPrimitives()){
  const accessor=primitive.getAttribute('NORMAL');
  if(!accessor || normalized.has(accessor))continue;
  const values=accessor.getArray();
  for(let i=0;i<values.length;i+=3){
    const length=Math.hypot(values[i],values[i+1],values[i+2]);
    if(!Number.isFinite(length)||length<1e-8)throw new Error('Invalid decoded normal');
    values[i]/=length;values[i+1]/=length;values[i+2]/=length;
  }
  accessor.setArray(values);normalized.add(accessor);
}
for(const extension of doc.getRoot().listExtensionsUsed()){
  if(['EXT_meshopt_compression','EXT_texture_webp'].includes(extension.extensionName))extension.dispose();
}
const after=getBounds(doc.getRoot().listScenes()[0]);
const error=Math.max(...before.min.map((v,i)=>Math.abs(v-after.min[i])),...before.max.map((v,i)=>Math.abs(v-after.max[i])));
if(error>1e-5)throw new Error('Decoded scene bounds changed');
doc.getRoot().getAsset().copyright=provenance.attribution;
doc.getRoot().setExtras({...doc.getRoot().getExtras(),original_author:provenance.author,
  source:provenance.source_url,license:provenance.license,license_url:provenance.license_url,
  modifications:'Meshopt decoded; quantization expanded and normals normalized; WebP converted losslessly to PNG. No fit/resize.'});
await io.write(out+'decoded_source.glb',doc);
await fs.copyFile(source+'CREDITS.txt',out+'CREDITS.txt');
await fs.writeFile(out+'decode_report.json',JSON.stringify({images,normalized_normal_accessors:normalized.size,source_bounds:before,decoded_bounds:after,max_bounds_error:error,
  extensions:doc.getRoot().listExtensionsUsed().map(x=>x.extensionName),source_sha256:provenance.sha256,
  scope:'Format compatibility only; no geometry/texture quality or rig acceptance'},null,2));
console.log('TREBEJO_STANDARD_GLTF_DECODED',images.length,error);
