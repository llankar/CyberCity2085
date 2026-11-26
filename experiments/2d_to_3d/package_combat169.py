"""Encode the native Full HD movie and its recorded game sounds for review."""
from pathlib import Path
import json,subprocess,shutil,argparse

OUT=Path('E:/CyberCity2085-3d-lab/generated/phase2/combat169')
TOOLS=Path('C:/Users/llank/AppData/Local/Microsoft/WinGet/Packages/Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe/ffmpeg-9.1-full_build/bin')

def run(*args):subprocess.run([str(TOOLS/'ffmpeg.exe'),'-y','-loglevel','error',*map(str,args)],check=True)

def main():
    global OUT
    parser=argparse.ArgumentParser();parser.add_argument('--folder',default=str(OUT))
    OUT=Path(parser.parse_args().folder).resolve()
    assert OUT.is_relative_to(Path('E:/CyberCity2085-3d-lab').resolve())
    state=json.loads((OUT/'encounter.json').read_text())
    if OUT.name in ('contact204','facade206','cyber207','district208','medic209','finish210','tempo212','recovery213','clinic214','industry216'):
        contact=json.loads((OUT/'melee_contact.json').read_text())
        assert contact['wrist_to_chest_m']<=.35,contact
        assert contact['forward_hand_speed_m_s']>.12,contact
        assert state['health'][1]==0,state
    assert state['blocked_shots']>=1,'Cover has not stopped a shot'
    assert state.get('occlusion_frames',0)>0,'Camera occlusion not demonstrated'
    native_input=OUT/'encounter.avi'
    retained_video=OUT/'encounter_1080p30.mp4'
    input_video=native_input if native_input.is_file() else retained_video
    assert input_video.is_file(), 'Render or retained MP4 required'
    probe=json.loads(subprocess.check_output([str(TOOLS/'ffprobe.exe'),'-v','error','-show_streams','-of','json',str(input_video)]))
    video=next(s for s in probe['streams'] if s['codec_type']=='video')
    assert (video['width'],video['height'],video['avg_frame_rate'])==(1920,1080,'30/1')
    assert any(s['codec_type']=='audio' for s in probe['streams'])
    assert int(video['nb_frames'])==state['frames']
    if native_input.is_file():
        run('-i',native_input,'-c:v','libx264','-crf','18','-pix_fmt','yuv420p',
            '-af','volume=9dB','-c:a','aac','-b:a','160k','-movflags','+faststart',retained_video)
    run('-ss','7','-t','15','-i',OUT/'encounter_1080p30.mp4','-filter_complex',
        'fps=10,scale=960:-1:flags=lanczos,split[a][b];[a]palettegen[p];[b][p]paletteuse',
        '-loop','0',OUT/'combat_excerpt.gif')
    (OUT/'index.html').write_text('''<!doctype html><html lang="fr"><meta charset="utf-8"><title>CyberCity — combat 3D</title>
<style>body{background:#081117;color:#dceef1;font:18px system-ui;margin:32px;max-width:1500px}h1{color:#21dce9}video,img{width:100%;border:1px solid #1f505b;margin:12px 0}p{line-height:1.5;color:#a8bdc4}</style>
<h1>CYBERCITY 2085 // NEON ALLEY</h1><video controls src="encounter_1080p30.mp4"></video>
<p>Full HD, 30 images/s, sons du jeu. Deux agents, deux raiders et un robot. Déplacements continus, tir arrêté par une couverture, échanges de tirs, mêlée, arcs PSI, destruction et soins. Caméra animée avec fondu des bâtiments masquant les agents.</p>
<p>Rencontre mise en scène dans le laboratoire indépendant : aucune campagne ni IA de production exécutée. La vidéo est rendue hors temps réel. Le style architectural et les contacts de soins restent perfectibles.</p>
<img src="clean_0254.png"><img src="clean_0590.png"><img src="clean_0750.png">
<p>Modèles humains et robot conservés. Matériaux PBR et accessoires Poly Haven, composants de toiture Kenney, sol et sons CyberCity existants. Ressources privées locales, aucune publication.</p></html>''',encoding='utf8')
    if OUT.name in ('industry216','lighting218','counter219','aircraft221','aircraft222','services223','roof226','library227'):
        # The selected gallery survives pruning historical experiment workspaces.
        recovery=json.loads((OUT/'recovery.json').read_text())
        assert recovery['health']==100 and not recovery['contact_active']
        page='<!doctype html><meta charset="utf-8"><title>CyberCity2085 ? current 3D showcase</title>\n<style>body{max-width:1400px;margin:32px auto;background:#07141a;color:#e9f4f7;font:18px system-ui}a{color:#39dce7}video,img{width:100%;margin:12px 0}p{line-height:1.6}</style>\n<h1>CYBERCITY 2085 // CURRENT SHOWCASE</h1><video controls src="encounter_1080p30.mp4"></video>\n<p>Full HD30. One staged encounter,1.7pace, retained character rigs/motions and actual game audio. Experimental scene; production runtime unchanged.</p>\n<h2>Repair / salvage / rooftops</h2><img src="clean_0030.png"><p>Acquired PBR compressor, valves and pipe elbows replace repeated stock rows. Foreground duct corners use restrained existing soft-smoke rendering.</p>\n<h2>Combat and treatment</h2><img src="clean_0590.png"><img src="clean_0750.png">\n<h2>Editable environment</h2><p><a href="../showcase216/environment.blend">Packed Blender</a> / <a href="../showcase216/environment.glb">Environment GLB</a></p>\n<h2>Selected models</h2><p><a href="../robot210/robot_actions.glb">Robot</a> / <a href="../sole_skin162/human.glb">Rook</a> / <a href="../armored203/armored_actions.glb">Armored Raider</a> / <a href="../rig177/human.glb">Textured AI human</a> / <a href="../vtol178/vtol_actions.glb">VTOL</a></p>\n<h2>Retained standalone checkpoint</h2><p><a href="../../../deliveries/tactical_demo215/index.html">Demo215 and sources</a></p><img src="../../../deliveries/tactical_demo215/media/comparison_native.png"><p>Nominal combat-scale sprite/model reference; poses/views differ and helmet addition is later. Global artistic work remains incomplete.</p>'
        if OUT.name in ('lighting218','counter219','aircraft221','aircraft222','services223','roof226','library227'):
            page+='<h2>Local shop lighting</h2><p>Seven practical lights follow the actual emissive valances and their cutaway alpha. Restrained neutral key/fill preserves tactical readability.</p>'
        if OUT.name in ('counter219','aircraft221','aircraft222','services223','roof226','library227'):
            page=page.replace('../showcase216/','../showcase219/')
            page+='<h2>Worn counter cladding</h2><p>Seven existing counter bodies use metric worn PBR cladding in three muted finishes. Original silhouettes and obstacle cells are unchanged.</p>'
        if OUT.name=='aircraft221':
            page+='<h2>Static VTOL candidate</h2><p>Hunyuan mesh and color generated from the actual stealth dropship combat illustration, matched to the previous vehicle width and center. Fan/gear animation is not yet transferred. Existing animated VTOL178 is retained.</p><p><a href="../paint220/stealth_vtol/review/model.blend">Textured Blender source</a> / <a href="../paint220/stealth_vtol/mesh.glb">Textured GLB</a></p>'
        if OUT.name in ('aircraft222','services223','roof226','library227'):
            page+='<h2>Articulated generated VTOL</h2><p>Two actual inner fan meshes extracted from the generated aircraft rotate inside stationary rings. Retained UV/albedo, metallic response adjusted. Landing gear is not transferred; this is a hover art trial.</p><p><a href="../vtol222/vtol_actions.blend">Animated Blender</a> / <a href="../vtol222/vtol_actions.glb">Animated GLB</a></p>'
        if OUT.name=='services223':
            page=page.replace('../showcase219/','../showcase223/')
            page+='<h2>Industrial service access</h2><p>Two facade bays use acquired maintenance decks, safety rails, access ladders, power boxes and ventilation. Existing map geometry and paths retained.</p>'
        if OUT.name=='roof226':
            page+='<h2>Original-map roof machine</h2><p>Manual masked source reference; Blender mechanical reconstruction, one authentic view. Hidden geometry inferred. Registered source placement, no tactical cell changes.</p><img src="../../../environment-library/assets/roof_twin_fan/reference.png"><img src="../../../environment-library/assets/roof_twin_fan/neutral.png"><p><a href="../../../environment-library/assets/roof_twin_fan/source.blend">Blender source</a> / <a href="../../../environment-library/assets/roof_twin_fan/optimized.glb">GLB</a></p>'
        if OUT.name=='library227':
            bindings=json.loads((OUT/'placements.json').read_text())
            environment=bindings.get('environment_relative','showcase219/environment.glb').split('/')[0]
            page=page.replace('../showcase219/','../'+environment+'/')
            page=page.replace('../vtol178/vtol_actions.glb','../vtol222/vtol_actions.glb')
            page+='<h2>Original-derived library placements</h2><p>Roof fan and purple paneled pair loaded from the same compiled library associations. Original map context, manual masks, Blender reconstructions; hidden sides inferred. No new Hunyuan inference.</p><p><a href="../../../environment-library/index.html">Source library and model links</a></p><img src="../../../environment-library/assets/purple_paneled_pair/reference.png"><img src="../../../environment-library/assets/purple_paneled_pair/neutral.png">'
        if OUT.name=='library227' and environment=='showcase229':
            page+='<h2>Original-derived segmented roofs</h2><p>Original contexts govern dark segmented plates and service hatch. Invented photovoltaic assemblies and roof sign removed; wall clinic signage retained. Reconstruction is interpretive, not recovered hidden geometry.</p><img src="../../../environment-library/references/city_exterior_neon_market_alley__south_building_w.png"><img src="original_roofs_detail.png">'
        if OUT.name=='library227' and environment in ('showcase230','showcase232','showcase233','showcase234','showcase235','showcase236','showcase237','showcase239','showcase240','showcase241','showcase243','showcase245'):
            run('-i',OUT/'clean_0030.png','-vf',('crop=280:290:180:565' if environment in ('showcase239','showcase240','showcase241','showcase243','showcase245') else 'crop=380:350:80:550'),'-frames:v','1',OUT/'service_facade_detail.png')
            page+='<h2>Interpreted industrial facade</h2><p>Original roof identity retained; unseen wall construction interpreted with cut-corner panels, service doors, glazing, reinforcement and supply conduits. Not an authentic recovered facade view.</p><img src="service_facade_detail.png">'
            if environment in ('showcase233','showcase234','showcase235','showcase236','showcase237','showcase239','showcase240','showcase241','showcase243','showcase245'):
                run('-i',OUT/'clean_0030.png','-vf',('crop=330:220:530:220' if environment in ('showcase239','showcase240','showcase241','showcase243','showcase245') else 'crop=420:260:470:190'),'-frames:v','1',OUT/'source_canopy_detail.png')
                page+='<h2>Original market cloth</h2><p>The green canopy uses an unmodified RGB crop of the original market illustration on a draped mesh with thickness. One authentic view; hidden shape inferred. Existing supports and machinery retained, cap vent removed. Source lighting is baked into the cloth and remains an artistic limitation.</p><img src="../../../environment-library/assets/market_green_canopy/source_cloth.png"><img src="source_canopy_detail.png">'
                if environment in ('showcase234','showcase235','showcase236','showcase237','showcase239','showcase240','showcase241','showcase243','showcase245'):
                    page+='<p>Current variant: three separate sage, green and plum cloth panels, cropped from the same original context. Complete shop exported as a reusable library GLB and actually loaded through its placement association; inferred counter/machinery retained.</p><p><a href="../../../environment-library/assets/market_three_canopies/shop.glb">Standalone shop GLB</a></p>'
            if environment in ('showcase235','showcase236','showcase237','showcase239','showcase240','showcase241','showcase243','showcase245'):
                page+='<h2>Original southeast display counter</h2><p>Four real recessed trays and a blue cloth cover use original RGB crops; interpreted sides and lower counter remain. Current video includes this shop loaded from its standalone library model.</p><p><a href="../../../environment-library/assets/market_southeast_display/shop.glb">Display counter GLB</a></p>'
            if environment in ('showcase236','showcase237','showcase239','showcase240','showcase241','showcase243','showcase245'):
                run('-i',OUT/'clean_0030.png','-vf',('crop=480:260:1290:300' if environment in ('showcase239','showcase240','showcase241','showcase243','showcase245') else 'crop=520:315:1390:245'),'-frames:v','1',OUT/'roof_layout_detail.png')
                page+='<h2>Original-layout industrial roof</h2><p>Northeast roof: two unequal extractors reuse existing swept blades, a raised stepped hatch and acquired pipe runs follow the original single-view layout. Hidden depths and connections interpreted. Same tactical footprint.</p><img src="../../../environment-library/references/city_exterior_neon_market_alley__ne_building.png"><img src="roof_layout_detail.png">'
                if environment in ('showcase237','showcase239','showcase240','showcase241','showcase243','showcase245'):
                    run('-i',OUT/'clean_0030.png','-vf',('crop=480:390:1290:300' if environment in ('showcase239','showcase240','showcase241','showcase243','showcase245') else 'crop=520:450:1390:245'),'-frames:v','1',OUT/'depot_facade_detail.png')
                    page+='<h2>Interpreted maintenance depot facade</h2><p>Acquired factory garage/service doors and industrial windows replace brick bays. Worn metal PBR cladding and source-inspired magenta accent. Vertical walls are inferred, not authentic recovered views. Saved-model comparison preserves98 roof/base meshes.</p><img src="depot_facade_detail.png">'
            baseline=OUT.parent/'roof226/clean_0030.png'
            if baseline.is_file():
                run('-i',baseline,'-vf','crop=380:350:80:550','-frames:v','1',OUT/'service_building_before.png')
                page+='<p>Before the source roof and facade passes:</p><img src="service_building_before.png">'
        if OUT.name=='library227' and environment in ('showcase239','showcase240','showcase241','showcase243','showcase245'):
            page+='<h2>Original-layout northern roof</h2><p>Reused extractor blades and acquired pipe mesh; left-side machinery cluster and broad right service panel follow the original roof context. Old generic compressor removed. Equipment depth interpreted. Opening camera24.5m then returns to existing action framing. Door palette uses verified glTF factors with unchanged texture pixels.</p><img src="../../../environment-library/references/city_exterior_neon_market_alley__north_building.png"><img src="../showcase239/north_neutral.png">'
        if OUT.name=='library227' and environment in ('showcase240','showcase241','showcase243','showcase245'):
            run('-i',OUT/'clean_0030.png','-vf','crop=400:340:270:0','-frames:v','1',OUT/'west_utility_detail.png')
            page+='<h2>Western utility frontage</h2><p>Acquired tall window and glazed service-door modules on dark PBR cladding; interpreted vertical frontage, genuine segmented roof/conduit layout. Old generic garage bays, compressor and walkway removed. Original tactical body vertices/faces unchanged.</p><img src="../../../environment-library/references/city_exterior_neon_market_alley__west_building.png"><img src="west_utility_detail.png">'
        if OUT.name=='library227' and environment in ('showcase241','showcase243','showcase245'):
            run('-i',OUT/'clean_0030.png','-vf','crop=410:465:1510:480','-frames:v','1',OUT/'east_cover_detail.png')
            page+='<h2>Original blue covered service roof</h2><p>Genuine blue cloth crop on a768quad draped mesh with thickness, posts and rails; reused service extractor and source-context segmented roof. Solid tactical body preserved, not a new walkable courtyard. Original baked highlights remain a limitation.</p><img src="../../../environment-library/references/city_exterior_neon_market_alley__east_building.png"><img src="east_cover_detail.png">'
        if OUT.name=='library227' and environment in ('showcase243','showcase245'):
            page+='<h2>Northwest service plant</h2><p>Original central service row and right extractor layout; acquired grilles, factory door and worn concrete PBR. Night-adjusted albedo, source pixels retained. Vertical facade and equipment depths interpreted. Current scene loads the blue covering as a standalone library assembly, replacing its seven embedded parts.</p><img src="../../../environment-library/references/city_exterior_neon_market_alley__nw_building.png"><img src="../showcase243/north_neutral.png">'
        if OUT.name=='library227' and environment=='showcase245':
            page+='<h2>Southwest framed service housing</h2><p>Genuine blue housing inset, real framed case, two curved service runs and reused extractor stations follow the original roof context. Acquired door/grilles, structural ribs and concrete service face. Exact function/hidden connections are unknown and interpreted; tactical body retained.</p><img src="../../../environment-library/references/city_exterior_neon_market_alley__sw_building.png"><img src="../showcase245/north_neutral.png">'
        if OUT.name=='library227' and bindings.get('floor_support'):
            floor=OUT.parent/'floor244'
            shutil.copyfile(OUT/'clean_0254.png',floor/'after_cutaway.png')
            for label in ('before','after'):
                run('-i',floor/(label+'_cutaway.png'),'-vf','crop=570:400:130:320','-frames:v','1',floor/(label+'_detail.png'))
            page+='<h2>Inferred floors beneath occupied volumes</h2><p>Original map artwork remains unchanged on route surfaces. A single PBR support surface covers only the627existing occupied cells, hiding flat roof/canopy drawings when the corresponding3D objects fade. These unseen floors are inferred, not recovered source views. No grid, LOS or collision changes.</p><div style="display:grid;grid-template-columns:1fr 1fr;gap:15px"><div>Before<img src="../floor244/before_detail.png"></div><div>After<img src="../floor244/after_detail.png"></div></div>'
        (OUT/'index.html').write_text(page,encoding='utf8')
        (OUT/'delivery.json').write_text(json.dumps({'native_video':video,'encounter':state,'scope':'Selected native scene; historical scratch workspaces pruned'},indent=2))
        print('CURRENT_SHOWCASE_DELIVERED',state)
        return
    if len(state['health'])==6:
        page=(OUT/'index.html').read_text(encoding='utf8')
        page=page.replace('Deux agents, deux raiders et un robot.', 'Trois agents, deux raiders et un robot, avec le candidat Hunyuan armé.')
        page=page.replace('Modèles humains et robot conservés.', 'Cast conservé et candidat Hunyuan ajouté pour comparaison.')
        (OUT/'index.html').write_text(page,encoding='utf8')
    if OUT.name=='vehicle178':
        page=(OUT/'index.html').read_text(encoding='utf8')
        page=page.replace('</html>','''<h2>VTOL — finition mécanique</h2>
<p>Coque PBR, verrière ajustée, turbines et détails de maintenance.
Les pivots existants sont conservés. La rotation des rotors boucle dans cette scène.
L'atterrissage et la qualité artistique finale restent à vérifier.</p>
<p><a href="../vtol178/vtol_actions.glb">GLB animé</a> ·
<a href="../vtol178/vtol_actions.blend">Source Blender</a></p>
<img src="../vtol178/neutral.png"><img src="../vtol178/rear.png"></html>''')
        (OUT/'index.html').write_text(page,encoding='utf8')
    if OUT.name in ('fall181','presentation182','district183','assemblies184','visible185','materials186','painted192','cannon193','gait194','market195','treatment196','storefront197','art198','roof199','cast200','medic201','armored203','contact204','facade206','cyber207','district208','medic209','finish210','tempo212','recovery213','clinic214','industry216'):
        page=(OUT/'index.html').read_text(encoding='utf8')
        page=page.replace('</html>','''<h2>Robot : impact et chute</h2>
<p>Impulsion PSI, chute continue hors du masque de la caisse, fumée et fragments.
La rencontre reste une séquence mise en scène indépendante.</p>
<img src="impact_0603.png"><img src="clean_0630.png">
<p><a href="../rig177/human.glb">Humain GLB</a> ·
<a href="../security_opaque137/robot_actions.glb">Robot GLB</a> ·
<a href="../vtol178/vtol_actions.glb">VTOL GLB</a></p></html>''')
        (OUT/'index.html').write_text(page,encoding='utf8')
    if OUT.name in ('presentation182','district183','assemblies184','visible185','materials186','painted192','cannon193','gait194','market195','treatment196','storefront197','art198','roof199','cast200','medic201','armored203','contact204','facade206','cyber207','district208','medic209','finish210','tempo212','recovery213','clinic214','industry216'):
        page=(OUT/'index.html').read_text(encoding='utf8')
        page=page.replace('</html>','''<h2>Cadrages d’action</h2>
<p>Vue tactique, échanges de tirs, approche et mêlée, PSI puis soins.
La caméra se rapproche progressivement ; les bâtiments utilisent la caméra
réelle pour leur fondu. Aucun changement des règles ou positions de combat.</p>
<img src="clean_0460.png"><img src="clean_0750.png"></html>''')
        (OUT/'index.html').write_text(page,encoding='utf8')
    if OUT.name=='district183':
        page=(OUT/'index.html').read_text(encoding='utf8')
        page=page.replace('</html>','''<h2>Matériaux du quartier</h2>
<p>Trois palettes dérivées des textures locales, surfaces plus sobres et valves
réduites. La géométrie tactique et les animations restent celles de la scène précédente.</p>
<p><a href="../showcase183/environment.glb">Décor GLB</a> ·
<a href="../showcase183/environment.blend">Source Blender</a></p></html>''')
        (OUT/'index.html').write_text(page,encoding='utf8')
    if OUT.name in ('assemblies184','visible185','materials186','painted192','cannon193','gait194','market195','treatment196','storefront197','art198','roof199','cast200','medic201','armored203','contact204','facade206','cyber207','district208','medic209','finish210','tempo212','recovery213','clinic214','industry216'):
        page=(OUT/'index.html').read_text(encoding='utf8')
        page=page.replace('</html>','''<h2>Assemblages architecturaux</h2>
<p>Trois baies de garage et plateformes de toiture provenant des kits locaux.
Les volumes tactiques et les animations de la rencontre sont conservés.</p>
<p><a href="../showcase184/environment.glb">Décor GLB</a> ·
<a href="../showcase184/environment.blend">Source Blender</a></p>
<img src="clean_0030.png"></html>''')
        (OUT/'index.html').write_text(page,encoding='utf8')
    if OUT.name in ('visible185','materials186','painted192','cannon193','gait194','market195','treatment196','storefront197','art198','roof199','cast200','medic201','armored203','contact204','facade206','cyber207','district208','medic209','finish210','tempo212','recovery213','clinic214','industry216'):
        page=(OUT/'index.html').read_text(encoding='utf8')
        page=page.replace('../showcase184/','../showcase185/')
        page=page.replace('</html>','''<p>Baies choisies selon leur orientation
vers la caméra principale. Portes et encadrements conservent leurs décalages
relatifs et leur échelle commune issus du kit source.</p></html>''')
        (OUT/'index.html').write_text(page,encoding='utf8')
    if OUT.name in ('materials186','painted192','cannon193','gait194','market195','treatment196','storefront197','art198','roof199','cast200','medic201','armored203','contact204','facade206','cyber207','district208','medic209','finish210','tempo212','recovery213','clinic214','industry216'):
        page=(OUT/'index.html').read_text(encoding='utf8')
        page=page.replace('</html>','''<h2>Harmonisation dans Godot</h2>
<p>Portes charbon, toitures moins métalliques et murs plus sobres. Textures,
normal maps et néons conservés. Cette direction de matériaux est appliquée
dans le GLB et le fichier Blender186, chargés directement par cette scène.</p><p><a href="../showcase186/environment.glb">Décor harmonisé GLB</a> · <a href="../showcase186/environment.blend">Source Blender harmonisée</a></p><h2>Comparaison au même cadrage</h2><div style="display:grid;grid-template-columns:1fr 1fr;gap:16px"><div>Avant<img src="../visible185/clean_0030.png"></div><div>Après<img src="clean_0030.png"></div></div></html>''')
        (OUT/'index.html').write_text(page,encoding='utf8')
    if OUT.name in ('painted192','cannon193','gait194','market195','treatment196','storefront197','art198','roof199','cast200','medic201','armored203','contact204','facade206','cyber207','district208','medic209','finish210','tempo212','recovery213','clinic214','industry216'):
        page=(OUT/'index.html').read_text(encoding='utf8').replace('../security_opaque137/robot_actions.glb','../robot191/robot_actions.glb')
        page=page.replace('</html>','''<h2>Robot Hunyuan articulé</h2>
<p>Variante indépendante utilisant le robot couleur déjà généré, une articulation
corrigée par connectivité et les effets/sons existants. L’ancienne scène est conservée.</p>
<p><a href="../robot191/robot_actions.glb">Robot GLB</a> ·
<a href="../robot191/robot_actions.blend">Source Blender</a> ·
<a href="../robot191/index.html">Étude des cinq actions</a></p></html>''')
        (OUT/'index.html').write_text(page,encoding='utf8')
    if OUT.name in ('cannon193','gait194','market195','treatment196','storefront197','art198','roof199','cast200','medic201','armored203','contact204','facade206','cyber207','district208','medic209','finish210','tempo212','recovery213','clinic214','industry216'):
        page=(OUT/'index.html').read_text(encoding='utf8').replace('../robot191/robot_actions.glb','../robot193/robot_actions.glb').replace('../robot191/robot_actions.blend','../robot193/robot_actions.blend')
        page=page.replace('</html>','''<h2>Canon : point de départ et visée</h2>
<p>Le tir part de l’embouchure attachée au canon. L’arme s’oriente vers la cible,
puis le rayon rencontre la couverture réelle. Le robot précédent et sa scène restent conservés.</p>
<img src="cannon_0146.png"></html>''')
        (OUT/'index.html').write_text(page,encoding='utf8')
    if OUT.name=='gait194':
        run('-ss','8.2','-i',OUT/'encounter_1080p30.mp4','-vf','fps=8,crop=640:640:850:150,scale=480:480,tile=4x2','-frames:v','1',OUT/'walk_sequence.png')
        page=(OUT/'index.html').read_text(encoding='utf8')
        page=page.replace('</html>','''<h2>Cadence du robot</h2>
<p>Le cycle utilise le pas animé de0,28m, sa phase d’appui et sa durée réelle.
Le trajet garde la même vitesse ; le cycle tourne à1,44 au lieu de0,66.
Cette correction ne constitue pas une validation complète des contacts de pieds.</p>
<img src="walk_sequence.png"><details><summary>Comparer la marche précédente</summary>
<video controls src="../cannon193/encounter_1080p30.mp4#t=8,13"></video></details></html>''')
        (OUT/'index.html').write_text(page,encoding='utf8')
    if OUT.name in ('market195','treatment196','storefront197','art198','roof199','cast200','medic201','armored203','contact204','facade206','cyber207','district208','medic209','finish210','tempo212','recovery213','clinic214','industry216'):
        page=(OUT/'index.html').read_text(encoding='utf8').replace('../showcase186/','../showcase195/')
        page=page.replace('</html>','''<h2>Market and clinic</h2><p>Sept comptoirs existants recoivent des auvents textiles, des cadres metalliques et un eclairage de bordure. La clinique porte une croix lumineuse. Volumes tactiques conserves ; decors supplementaires cosmetiques.</p><p><a href="../showcase195/environment.blend">Source Blender du decor</a> ? <a href="../showcase195/environment.glb">Decor GLB</a></p><img src="clean_0750.png"></html>''')
        (OUT/'index.html').write_text(page,encoding='utf8')
    if OUT.name in ('treatment196','storefront197','art198','roof199','cast200','medic201','armored203','contact204','facade206','cyber207','district208','medic209','finish210','tempo212','recovery213','clinic214','industry216'):
        run('-ss',str(21/1.7 if OUT.name in ('tempo212','recovery213','clinic214','industry216') else 21),'-i',input_video,'-vf','fps=1,scale=640:360,tile=3x2','-frames:v','1',OUT/'treatment_sequence.png')
        page=(OUT/'index.html').read_text(encoding='utf8').replace('</html>','''<h2>Lateral treatment</h2><img src="treatment_sequence.png"><p>Approche continue jusqu'au cote du patient, orientation distincte et mallette rapprochee. L'animation et le ciblage de la main restent ceux de la scene precedente.</p><p>Comparaison : <a href="../market195/clean_0750.png">ancien placement</a></p></html>''')
        (OUT/'index.html').write_text(page,encoding='utf8')
    if OUT.name in ('storefront197','art198','roof199','cast200','medic201','armored203','contact204','facade206','cyber207','district208','medic209','finish210','tempo212','recovery213','clinic214','industry216'):
        page=(OUT/'index.html').read_text(encoding='utf8').replace('../showcase195/','../showcase197/')
        page=page.replace('</html>','''<h2>Furnished market stalls</h2><p>Seven existing counters gain folded metal worktops, local medical cases or sealed component crates, small terminals and geometric emissive signs. The map keeps its tactical footprint. Original source assets are reused, with no new downloads.</p><p><a href="../showcase197/environment.blend">Blender source</a> / <a href="../showcase197/environment.glb">Environment GLB</a></p><details><summary>Previous empty stalls</summary><img src="../market195/clean_0030.png"></details></html>''')
        (OUT/'index.html').write_text(page,encoding='utf8')
    if OUT.name in ('art198','roof199','cast200','medic201','armored203','contact204','facade206','cyber207','district208','medic209','finish210','tempo212','recovery213','clinic214','industry216'):
        run('-ss',str(29.5/1.7 if OUT.name in ('tempo212','recovery213','clinic214','industry216') else 29.5),'-i',OUT/'encounter_1080p30.mp4','-frames:v','1',OUT/'orbit_final.png')
        run('-i',OUT/'encounter_1080p30.mp4','-vf','fps=2/5,scale=480:270,tile=4x3','-frames:v','1',OUT/'encounter_storyboard.png')
        page=(OUT/'index.html').read_text(encoding='utf8').replace('../showcase197/','../showcase198/')
        page=page.replace('</html>','''<h2>Whole encounter review</h2><p>The end orbit stays above the finite map to avoid framing the void below the floor.</p><img src="orbit_final.png"><p>Local PBR metal normals/roughness, less rigid merchandise placement, and removal of the two conflicting decorative valves. Tactical footprints remain unchanged. This contact sheet samples the whole sequence; it does not replace full-motion artistic acceptance.</p><img src="encounter_storyboard.png"><p><a href="../showcase198/environment.blend">Current Blender source</a> / <a href="../showcase198/environment.glb">Current environment GLB</a></p></html>''')
        (OUT/'index.html').write_text(page,encoding='utf8')
    if OUT.name in ('roof199','cast200','medic201','armored203','contact204','facade206','cyber207','district208','medic209','finish210','tempo212','recovery213','clinic214','industry216'):
        page=(OUT/'index.html').read_text(encoding='utf8').replace('../showcase198/','../showcase199/')
        page=page.replace('</html>','''<h2>Distinct rooftop identities</h2><img src="../roof199/roof_overview.png"><p>Utility reservoir with steel mounts and bands, tilted photovoltaic array on the repair shop, and a supported clinic sign. All are independent hard-surface meshes within the existing building footprints. Functional tactical volumes and the retained encounter stay unchanged.</p><p><a href="../showcase199/environment.blend">Blender source</a> / <a href="../showcase199/environment.glb">Environment GLB</a></p><details><summary>Previous roof composition</summary><img src="../art198/clean_0030.png"></details></html>''')
        (OUT/'index.html').write_text(page,encoding='utf8')
    if OUT.name in ('cast200','medic201','armored203','contact204','facade206','cyber207','district208','medic209','finish210','tempo212','recovery213','clinic214','industry216'):
        run('-ss',str(11.72/1.7 if OUT.name in ('tempo212','recovery213','clinic214','industry216') else 11.72),'-i',OUT/'encounter_1080p30.mp4','-vf','fps=6,crop=1024:768:600:280,scale=640:480,tile=2x2','-frames:v','1',OUT/'retaliation_sequence.png')
        retaliation=json.loads((OUT/'retaliation.json').read_text())
        assert retaliation['health_before']-retaliation['health_after']==12,retaliation
        assert retaliation['teammate_clearance_m']>.35,retaliation
        run('-ss',str(11.733333/1.7 if OUT.name in ('tempo212','recovery213','clinic214','industry216') else 11.733333),'-i',OUT/'encounter_1080p30.mp4','-frames:v','1',OUT/'reinforcement_fire.png')
        page=(OUT/'index.html').read_text(encoding='utf8').replace('</html>','''<h2>Distinct enemy reinforcement</h2><img src="retaliation_sequence.png"><p>The second hostile uses the existing alternate authored body and rigged helmet instead of duplicating the first. Shared walk/fire animations remain in use. The reinforcement now returns fire once; treatment starts from actual remaining health.</p><img src="reinforcement_fire.png"><p><a href="../modularity166/body_0_helmet_restfixed.glb">Alternate body GLB</a> / <a href="../modularity166/helmet_transfer_restfixed.blend">Existing Blender source</a></p></html>''')
        (OUT/'index.html').write_text(page,encoding='utf8')
    if OUT.name in ('medic201','armored203','contact204','facade206','cyber207','district208','medic209','finish210','tempo212','recovery213','clinic214','industry216'):
        page=(OUT/'index.html').read_text(encoding='utf8').replace('</html>','''<h2>Medical equipment module</h2><p>The existing PBR medical hard case is adapted as detachable equipment on the medic's upper spine. Original human geometry, textures and motions are retained. This is equipment distinction, not a redesigned human wardrobe.</p><p><a href="medical_pack.blend">Medical module Blender source</a> / <a href="medical_pack.glb">Medical module GLB</a></p><img src="clean_0750.png"><details><summary>Previous medic silhouette</summary><img src="../cast200/clean_0750.png"></details></html>''')
        (OUT/'index.html').write_text(page,encoding='utf8')
    if OUT.name in ('medic201','armored203','contact204','facade206','cyber207','district208','medic209','finish210','tempo212','recovery213','clinic214','industry216'):
        page=(OUT/'index.html').read_text(encoding='utf8').replace('</html>','<h2>Sprites / current models at combat scale</h2><p>Native comparison at nominal human heights of 41 and 62 pixels. Robot uses the existing 1.65 sprite multiplier. The first actual idle atlas tile is shown; pose and orientation are not identical to the 3D idle view. This is an artistic reference, not final acceptance.</p><a href="../scale202/comparison_native.png"><img src="../scale202/comparison_native.png"></a></html>')
        (OUT/'index.html').write_text(page,encoding='utf8')
    if OUT.name in ('armored203','contact204','facade206','cyber207','district208','medic209','finish210','tempo212','recovery213','clinic214','industry216'):
        page=(OUT/'index.html').read_text(encoding='utf8')
        page=page.replace('The second hostile uses the existing alternate authored body and rigged helmet instead of duplicating the first.','The second hostile uses an existing authored yellow/black armored body with its bound pistol instead of the civilian-shirt candidate.')
        page=page.replace('../modularity166/body_0_helmet_restfixed.glb','armored_actions.glb').replace('../modularity166/helmet_transfer_restfixed.blend','armored_actions.blend')
        page=page.replace('../scale202/comparison_native.png','comparison_native.png')
        page=page.replace('href="medical_pack.blend"','href="../medic201/medical_pack.blend"').replace('href="medical_pack.glb"','href="../medic201/medical_pack.glb"')
        page=page.replace('</html>','''<h2>Armored Raider candidate</h2><p>Retained Unvanquished body, detailed original textures, source motions and bound pistol assembled into one portable model. Existing forward-axis audit reused. No new humanoid generation or repaint.</p><p><a href="armored_actions.blend">Complete Blender source</a> / <a href="armored_actions.glb">Complete animated GLB</a></p><details><summary>Previous civilian candidate</summary><img src="../medic201/clean_0750.png"></details></html>''')
        (OUT/'index.html').write_text(page,encoding='utf8')
    if OUT.name in ('contact204','facade206','cyber207','district208','medic209','finish210','tempo212','recovery213','clinic214','industry216'):
        contact=json.loads((OUT/'melee_contact.json').read_text())
        run('-ss',str(max(0,contact.get('video_time',contact['time'])-.08)),'-i',OUT/'encounter_1080p30.mp4','-vf','fps=5,crop=640:640:700:200,tile=3x1','-frames:v','1',OUT/'melee_sequence.png')
        run('-ss',str(8.4/1.7 if OUT.name in ('tempo212','recovery213','clinic214','industry216') else 8.4),'-i',OUT/'encounter_1080p30.mp4','-vf','fps=5,crop=640:640:700:200,tile=3x1','-frames:v','1',OUT/'hit_sequence.png')
        page=(OUT/'index.html').read_text(encoding='utf8').replace('href="armored_actions.glb"','href="../armored203/armored_actions.glb"').replace('href="armored_actions.blend"','href="../armored203/armored_actions.blend"').replace('href="comparison_native.png"','href="../armored203/comparison_native.png"').replace('src="comparison_native.png"','src="../armored203/comparison_native.png"')
        page=page.replace('</html>','''<h2>Combat contacts</h2><p>Nonlethal hits use short torso recoil instead of a death-clip squat. The staged melee resolves when an advancing fist reaches an approximate torso volume, not at a fixed timestamp. The robot no longer swings out of reach. Existing clips and final encounter remain in use.</p><img src="hit_sequence.png"><img src="melee_sequence.png"><p>One staged contact volume, not a new production collision system or exhaustive motion acceptance.</p></html>''')
        (OUT/'index.html').write_text(page,encoding='utf8')
    if OUT.name=='facade206':
        run('-i',OUT.parent/'contact204/clean_0030.png','-i',OUT/'clean_0030.png','-filter_complex','[0:v]crop=420:430:0:450[a];[1:v]crop=420:430:0:450[b];[a][b]hstack','-frames:v','1',OUT/'facade_comparison.png')
        page=(OUT/'index.html').read_text(encoding='utf8').replace('../showcase199/','../showcase206/')
        page=page.replace('</html>','''<h2>Urban facade variant</h2><p>Before / after, same framing</p><img src="facade_comparison.png"><p>Eight bays on two buildings reuse the retained urban kit, with shallower window frames and distinct material palettes. Existing tactical map volumes/paths are retained. The verified local Delivery205 remains unchanged while this artistic variant is reviewed.</p><p><a href="../showcase206/environment.blend">Blender environment source</a> / <a href="../showcase206/environment.glb">Environment GLB</a></p><details><summary>Previous facade composition</summary><img src="../contact204/clean_0030.png"></details></html>''')
        (OUT/'index.html').write_text(page,encoding='utf8')
    if OUT.name=='cyber207':
        page=(OUT/'index.html').read_text(encoding='utf8').replace('../showcase199/','../showcase207/')
        page=page.replace('</html>','''<h2>Cyberpunk technical kiosks</h2><p>Seven cloth canopies replaced by weathered metal kiosks: cyberclinic holograms, power stations and neural terminals. Existing urban facade kit, authored ventilation and pipes, exposed cables and network advertising. Transparent displays keep the building occlusion fade. Same tactical encounter and retained character animation.</p><p><a href="../showcase207/environment.blend">Packed Blender source</a> / <a href="../showcase207/environment.glb">Environment GLB</a></p><h3>Before</h3><img src="../facade206/clean_0030.png"><h3>After</h3><img src="clean_0030.png"></html>''')
        (OUT/'index.html').write_text(page,encoding='utf8')
    if OUT.name=='district208':
        page=(OUT/'index.html').read_text(encoding='utf8').replace('../showcase199/','../showcase208/')
        page=page.replace('</html>','<h2>Industrial district finish</h2><p>Three existing buildings use worn metal cladding and illustrated clinic advertising within fitted facade bays. Same map volumes and combat, existing cyberpunk kiosks and cutaway preserved. This is an art variant; final visual acceptance remains open.</p><p><a href="../showcase208/environment.blend">Packed Blender source</a> / <a href="../showcase208/environment.glb">Environment GLB</a></p><h3>Before</h3><img src="../cyber207/clean_0030.png"><h3>After</h3><img src="clean_0030.png"></html>')
        (OUT/'index.html').write_text(page,encoding='utf8')
    if OUT.name in ('medic209','finish210','tempo212','recovery213','clinic214','industry216'):
        run('-i',OUT.parent/'district208/clean_0750.png','-i',OUT/'clean_0750.png','-filter_complex','[0:v]crop=480:420:760:360[a];[1:v]crop=480:420:760:360[b];[a][b]hstack','-frames:v','1',OUT/'medic_comparison.png')
        page=(OUT/'index.html').read_text(encoding='utf8').replace('../showcase199/','../showcase208/')
        page=page.replace('</html>','<h2>Medic silhouette / existing authored equipment</h2><p>Retained authored military helmet, attached to the existing head bone. Original body, skeleton, treatment and movement clips preserved. Existing spine-mounted medical case stays in use.</p><p><a href="helmet.blend">Helmet Blender source</a> / <a href="helmet.glb">Detachable GLB</a></p><h3>Before / after, native medical pose</h3><img src="medic_comparison.png"><p>One accessory fit in this encounter, not a complete class wardrobe or general modular equipment system.</p></html>')
        (OUT/'index.html').write_text(page,encoding='utf8')
    if OUT.name in ('finish210','tempo212','recovery213','clinic214','industry216'):
        run('-i',OUT.parent/'district208/clean_0030.png','-i',OUT/'clean_0030.png','-filter_complex','[0:v]crop=400:350:950:270[a];[1:v]crop=400:350:950:270[b];[a][b]hstack','-frames:v','1',OUT/'robot_comparison.png')
        page=(OUT/'index.html').read_text(encoding='utf8').replace('href="helmet.blend"','href="../medic209/helmet.blend"').replace('href="helmet.glb"','href="../medic209/helmet.glb"')
        page=page.replace('</html>','<h2>Heavy robot finish</h2><p>Existing broad silhouette, painted albedo, 14-bone rig, five actions and cannon sockets retained. Metal response and emission on the existing red sensor pixels. Sensors shut down during destruction.</p><img src="robot_comparison.png"><p><a href="../robot210/robot_actions.blend">Robot Blender source</a> / <a href="../robot210/robot_actions.glb">Robot GLB</a></p></html>')
        (OUT/'index.html').write_text(page,encoding='utf8')
    if OUT.name in ('tempo212','recovery213','clinic214','industry216'):
        assert 17<int(video['nb_frames'])/30<19,video
        run('-ss',str(int(video['nb_frames'])/30-.7),'-i',OUT/'encounter_1080p30.mp4','-frames:v','1',OUT/'end_orbit.png')
        contact=json.loads((OUT/'melee_contact.json').read_text())
        assert abs(contact['video_time']-contact['time']/1.7)<.001,contact
        page=(OUT/'index.html').read_text(encoding='utf8').replace('../showcase208/','../showcase211/')
        page=page.replace('</html>','<h2>Faster scene rhythm and street architecture</h2><img src="end_orbit.png"><p>Scene simulation runs at1.7 pace: positions, animation advancement, effects and camera remain on the same clock. Actual audio clips keep their pitch; no post-encoding speed filter. Gallery image names identify simulation phases. Two old lamps replaced by angular lit fixtures; one repetitive window bay becomes a retained authored industrial vent assembly.</p><p><a href="../showcase211/environment.blend">Environment Blender</a> / <a href="../showcase211/environment.glb">Environment GLB</a></p><details><summary>Previous30-second rhythm</summary><video controls src="../finish210/encounter_1080p30.mp4"></video></details></html>')
        (OUT/'index.html').write_text(page,encoding='utf8')
    if OUT.name in ('recovery213','clinic214','industry216'):
        recovery=json.loads((OUT/'recovery.json').read_text())
        run('-ss',str(int(video['nb_frames'])/30-.2),'-i',OUT/'encounter_1080p30.mp4','-vf','crop=600:500:600:250','-frames:v','1',OUT/'recovery_final_detail.png')
        assert recovery['health']==100 and not recovery['contact_active'] and recovery['idle_rest_channels_reset'],recovery
        assert recovery['medic_clip']=='Hard stand' and recovery['patient_clip']=='Hard stand',recovery
        run('-ss','16.1','-i',OUT/'encounter_1080p30.mp4','-vf','fps=3,scale=640:360,tile=3x2','-frames:v','1',OUT/'recovery_sequence.png')
        page=(OUT/'index.html').read_text(encoding='utf8').replace('</html>','<h2>Medical completion and recovery</h2><p>Existing source kneeling pose held until actual100HP. Arm contact releases at completion; both characters use their existing recovery/standing motions. No new rig or healing amount.</p><img src="recovery_sequence.png"><img src="recovery_final_detail.png"><p><a href="recovery.json">Native completion state</a></p></html>')
        (OUT/'index.html').write_text(page,encoding='utf8')
    if OUT.name in ('clinic214','industry216'):
        run('-i',OUT.parent/'recovery213/clean_0030.png','-i',OUT/'clean_0030.png','-filter_complex','[0:v]crop=500:330:280:750[a];[1:v]crop=500:330:280:750[b];[a][b]hstack','-frames:v','1',OUT/'clinic_comparison.png')
        page=(OUT/'index.html').read_text(encoding='utf8').replace('../showcase211/','../showcase214/')
        page=page.replace('</html>','<h2>Clinic service facade</h2><p>Camera-facing bay with retained authored ventilation, external coolant conduits, illustrated scanner and dispenser drawer. Same tactical map geometry.</p><img src="clinic_comparison.png"><p><a href="../showcase214/environment.blend">Packed Blender environment</a> / <a href="../showcase214/environment.glb">Environment GLB</a></p></html>')
        (OUT/'index.html').write_text(page,encoding='utf8')
    if OUT.name=='industry216':
        page=(OUT/'index.html').read_text(encoding='utf8').replace('../showcase214/','../showcase216/')
        page=page.replace('</html>','<h2>Repair/salvage and rooftop services</h2><p>Two counters now use acquired PBR compressor, valves and pipe elbows instead of repeated crate rows. Two foreground roofs use authored duct corners, with restrained vapor from the existing soft smoke renderer. Same map/cast/tempo and lamp cutaway.</p><img src="clean_0030.png"><p><a href="../showcase216/environment.blend">Blender environment</a> / <a href="../showcase216/environment.glb">Environment GLB</a></p></html>')
        (OUT/'index.html').write_text(page,encoding='utf8')
    (OUT/'delivery.json').write_text(json.dumps({'native_video':video,'encounter':state,
        'scope':'Native rendered visual sequence, not campaign or production AI acceptance'},indent=2))
    print('COMBAT169_DELIVERED',state)

if __name__=='__main__':main()
