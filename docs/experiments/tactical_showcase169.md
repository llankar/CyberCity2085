# Neon Alley — démonstration de combat 3D indépendante

Livrables : `E:/CyberCity2085-3d-lab/generated/phase2/combat169/index.html`.
Vidéo `encounter_1080p30.mp4`, GIF extrait, captures `clean_*.png` sans diagnostic.

## Ce qui est effectivement exécuté

Deux agents, deux raiders et un robot conservent leurs positions après chaque
déplacement. Les cercles les suivent, les modèles s'orientent selon la trajectoire
ou la cible et la vitesse des cycles suit celle du déplacement. Les personnages,
leurs textures et leurs animations précédemment fonctionnelles sont réutilisés.

La rencontre est mise en scène dans un runtime expérimental : tirs depuis
l'arme avec tracés et flashs, impacts, réactions, perte de santé, mêlée, arcs
cyberpsychiques, destruction du robot et soins avec une vraie mallette PBR.
Le premier tir du robot est arrêté par le volume réel de la caisse. Les autres
obstacles utilisent les cellules de la carte. Le soigneur rejoint son patient
sans revenir à son point de départ, et la santé remonte pendant le soin.

La caméra tourne et zoome, puis descend ; les bâtiments masquant les agents
s'effacent progressivement. Les sons proviennent des WAV existants de CyberCity.
Le Movie Maker natif enregistre l'audio en même temps que les images ; le MP4
augmente le niveau audio de9dB, sans recréer les effets ni les décaler.

## Une seule carte vitrine

Les627cellules des obstacles sont conservées. Les neuf groupes de bâtiments
reçoivent brique/béton/métal PBR, fenêtres, portes, enseignes, cheminées,
réservoirs et panneaux de toiture. Des modèles existants de tuyaux, lampadaires,
compresseurs, câbles et rideaux métalliques complètent le décor.

Sources conservées sur E: : Poly Haven (`sources/environment169`),
Kenney City Kit Industrial, acteurs et notices déjà acquis. Le sol illustré et
les sons appartiennent aux ressources actuelles du projet. Aucun asset du jeu
de production n'est remplacé ; aucune des121autres cartes n'est convertie.

## Reproduire

```powershell
python experiments/2d_to_3d/acquire_environment169.py
& experiments/2d_to_3d/run_blender.ps1 -Script blender/showcase_environment169.py
& experiments/2d_to_3d/run_movie169.ps1
python experiments/2d_to_3d/package_combat169.py
```

Pour voir la scène sans capturer :
```powershell
& experiments/2d_to_3d/run_godot.ps1 -Scene res://combat169.tscn -RenderingMethod gl_compatibility
```

## Vérifications limitées à cette livraison

Capture native1920×1080,902images à30fps, soit30,07secondes de vidéo. Rendu
hors temps réel en environ60secondes, pas une mesure de capture temps réel.
Le journal Godot mesure environ7–10msGPU/image dans cette scène ; cela ne
garantit pas les performances d'une campagne. Le fichier possède une vraie
piste audio stéréo48kHz. Le contrôle ciblé confirme1tir bloqué,143occultations
de bâtiment/image et la santé finale cohérente. Les captures tir/PSI/soins ont
été inspectées. Aucun test de campagne ni ancien test de rig relancé.

## Limites restantes

La rencontre est scénarisée, sans IA de campagne ni modification des règles
tactiques de production. L'architecture et les transitions restent celles d'un
prototype ; certains volumes et panneaux sont encore simples. Les contacts du
soin et les fragments de destruction peuvent être améliorés. Le travail Hunyuan
couleur continue séparément et ne bloque pas la démonstration existante.

## Variante de façades du26novembre

Les composants architecturaux Poly Haven sont assemblés dans une variante
séparée, `showcase170` :204panneaux, fenêtres/vitres, portes et corniches,
avec conduits de toiture. Les neuf emprises de bâtiments et627cellules sont
conservées. Un premier aperçu natif a révélé les fenêtres absentes (composants
séparés des panneaux) ; les inserts ont été ajoutés et le nouvel aperçu inspecté.
La vidéo169 demeure conservée. Native170 delivery DONE: 902 frames,1920x1080/30fps, stereo audio,30.07s. Offline rendering72s; cover blocked1shot,144building/frame occlusions. Clean0254/0750 inspected. Repeated roofs, mixed prop styles and medical contact remain open.

```powershell
& experiments/2d_to_3d/run_blender.ps1 -Script blender/showcase_environment169.py -ScriptArguments @('--authored-facades')
& experiments/2d_to_3d/run_movie169.ps1 -Architectural
python experiments/2d_to_3d/package_combat169.py --folder E:/CyberCity2085-3d-lab/generated/phase2/combat170
```

CHANTIER GLOBAL INCOMPLET : cette livraison montre le combat, sans prétendre
que la migration3D ou la qualité artistique finale sont acceptées.

## Refined stage171

The optional `--refined-stage` Blender pass writes `showcase171`, preserving
169/170. It keeps authored PBR vents and compressors, removes the mismatched
white low-detail roof kit props, and mixes dark concrete with blue metal roofs.
The source PBR images remain intact; the derived roof colour image stays on E:.
`run_movie169.ps1 -Refined` selects that environment and writes `combat171`.
The patient turns toward the medic and the real medical case appears during
treatment. Hand-to-patient anatomical contact is still not artistically accepted.

Initial171 movie had no occlusion: removing the tall props reduced the building
bounds. The packaging check rejected it. A lower final camera demonstrates actual
building occlusion; failed and overbright roof takes are retained separately.
No campaign or production runtime is involved.
