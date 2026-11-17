"""Build an honest per-map inventory from completed native captures, not load flags."""
import argparse,hashlib,json
from pathlib import Path
from PIL import Image,ImageDraw,ImageChops
ROOT=Path(__file__).resolve().parents[2]
ART=ROOT/'godot/combat_missions_ui/art/environment'

def webp(source,target):
    with Image.open(source) as original:
        image=original.convert('RGB');image.save(target,'WEBP',lossless=True,quality=0,method=0)
        assert ImageChops.difference(image,Image.open(target).convert('RGB')).getbbox() is None

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--captures',type=Path,default=ROOT/'work/art25-release-clear-catalogue')
    parser.add_argument('--families',type=Path,default=ROOT/'work/art25-release-families')
    parser.add_argument('--before',type=Path,default=ROOT/'work/art25-before-clear')
    parser.add_argument('--output',type=Path,default=ROOT/'docs/images/combat-25')
    args=parser.parse_args();out=args.output.resolve();out.mkdir(parents=True,exist_ok=True)
    image_links=out.relative_to(ROOT/'docs').as_posix()
    report=json.loads((args.captures/'native-report.json').read_text());assert len(report)==122
    assert 'COMBAT_21_CAPTURE_PASSED' in (args.captures.parent/(args.captures.name+'.log')).read_text()
    assert 'SCRIPT ERROR' not in (args.captures.parent/(args.captures.name+'.log')).read_text()
    records={x['map']:x for x in report}
    review_path=ART/'expansion_reviews.json'
    reviews=json.loads(review_path.read_text()).get('candidates',[]) if review_path.exists() else []
    source=ART/'environment_art.json';data=json.loads(source.read_text());inventory=[]
    for name,entry in sorted(data['maps'].items()):
        result=records[name];props=[p for p in entry['props'] if p['enabled']]
        assert result['rendered_sprites']==len(props),(name,result['rendered_sprites'],len(props))
        assert result['native_render'] and result['projection_and_zoom_checked']
        frame=args.captures/f'{Path(name).stem}-1280x720.png'
        with Image.open(frame) as image:
            assert image.size==(1280,720)
            screenshot_hash=hashlib.sha256(image.convert('RGB').tobytes()).hexdigest()
        entry['validation'].update(native_render='passed',picking_zoom='passed',tactical_catalogue='passed',artistically_complete=False)
        for prop in entry['props']:
            prop['detail_status']='native_render_verified_art_completion_pending' if prop['enabled'] else 'original_retained_frame_mismatch'
        decisions=[dict(object=r['source_object_id'],decision=r['decision'],reason=r['reason'],sheet='reviews/'+r['review_sheet'],cell=r['review_cell']) for r in reviews if name in r['aliases']]
        inventory.append(dict(map=name,source_sha256=entry['image_sha256'],rendered_props=[dict(object=p['source_object_id'],asset=p['asset'],yaw=p['yaw'],partial_group=p.get('partial_source_object',False)) for p in props],retained_2d=entry['remaining_2d'],source_foreground_layers=entry['source_foreground_layers'],issues=entry['issues'],review_decisions=decisions,validation=entry['validation'],native=result,screenshot_rgb_sha256=screenshot_hash))
    source.write_text(json.dumps(data,indent=2)+'\n')
    # Catalog contact sheets are reduced real captures, never invented artwork.
    for page in range((len(inventory)+11)//12):
        sheet=Image.new('RGB',(1440,1160),(8,14,18));draw=ImageDraw.Draw(sheet)
        for i,entry in enumerate(inventory[page*12:page*12+12]):
            x=(i%3)*480;y=(i//3)*290
            frame=args.captures/f'{Path(entry["map"]).stem}-1280x720.png'
            with Image.open(frame) as image:sheet.paste(image.convert('RGB').resize((480,270),Image.Resampling.LANCZOS),(x,y+20))
            draw.text((x+5,y+4),entry['map'],fill=(150,240,245))
            entry['contact_sheet']=f'catalogue-{page+1:02}.jpg';entry['contact_cell']=i+1
        sheet.save(out/f'catalogue-{page+1:02}.jpg',quality=92)
    names=['cybercity_inner_02_safehouse','city_industrial_factory_floor','city_exterior_neon_market_alley','city_interior_blacksite_lab','wasteland_outdoor_01_dust_road_ambush']
    for name in names:
        webp(args.before/f'{name}-1920x1080.png',out/f'before-{name}-1920x1080.webp')
        for size in ['1280x720','1920x1080','2560x1440']:
            webp(args.families/f'{name}-{size}.png',out/f'after-{name}-{size}.webp')
    (out/'inventory.json').write_text(json.dumps(inventory,indent=2)+'\n')
    (out/'native-report.json').write_text(json.dumps(report,indent=2)+'\n')
    header=['# Inventaire artistique Combat Visual 2.5','','Statut : travail artistique **partiel**. Les validations natives ne signifient pas qu’une carte est artistiquement terminée. Les nombres de rendu source désignent des entrées de relevé ; une entrée peut regrouper plusieurs objets.','','| Carte | Remplacements actifs | Ressources | Entrées encore en art source | Contrôle natif | Capture |','|---|---|---|---|---|---|']
    for i in inventory:
        models=', '.join(f"{p['object']} → {p['asset']}@{p['yaw']}°" for p in i['rendered_props']) or 'Source conservée'
        header.append(f"| {i['map']} | {len(i['rendered_props'])} | {models} | {len(i['retained_2d'])} | Rendu / picking / zoom vérifiés ; art incomplet | [Planche, case {i['contact_cell']}]({image_links}/{i['contact_sheet']}) |")
    header+=['','Les listes complètes des objets améliorés, ressources, éléments 2D, problèmes et résultats sont dans [inventory.json]('+image_links+'/inventory.json). Les sources et annotations restent indépendantes des collisions.']
    (ROOT/'docs/combat_visual_25_inventory.md').write_text('\n'.join(header)+'\n')
    readme=['# Captures réelles Combat Visual 2.5','','Les 11 planches sont des réductions des 122 captures natives en 1280×720. Les vues détaillées conservent exactement les pixels des captures PNG grâce à WebP sans perte. Les empreintes RGB originales et résultats natifs sont dans le manifeste.','','| Environnement | Avant 1080p | Après 720p | Après 1080p | Après 1440p |','|---|---|---|---|---|']
    for name in names:
        readme.append(f'| {name} | [Voir](before-{name}-1920x1080.webp) | [Voir](after-{name}-1280x720.webp) | [Voir](after-{name}-1920x1080.webp) | [Voir](after-{name}-2560x1440.webp) |')
    readme+=['','## Catalogue complet','']+[f'- [Planche {p+1}](catalogue-{p+1:02}.jpg)' for p in range(11)]
    readme+=['','[Inventaire détaillé](../../combat_visual_25_inventory.md) · [Données et empreintes des captures](inventory.json) · [Mesures natives](native-report.json)','','Le matériel de validation utilise OpenGL llvmpipe. Les mesures incluent les fixtures et captures et ne constituent pas un benchmark GPU joueur.']
    (out/'README.md').write_text('\n'.join(readme)+'\n')
    print('ENVIRONMENT_INVENTORY_BUILT',len(inventory),'maps',sum(len(i['rendered_props']) for i in inventory),'sprite placements')
if __name__=='__main__':main()
