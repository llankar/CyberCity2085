# Démonstration tactique 3D — priorité visuelle

Scène indépendante : `experiments/2d_to_3d/godot/demo167.tscn`.
Ressources et captures privées : `E:/CyberCity2085-3d-lab/generated/phase2/demo167_final`.

Relancer sans campagne :
```powershell
& experiments/2d_to_3d/run_godot.ps1 -Scene res://demo167.tscn -RenderingMethod gl_compatibility
```
Ajouter `-SceneArguments @('--record')` pour enregistrer les images natives sur E:.
`package_demo167.py` assemble ces images en MP4/GIF ; il ne fabrique pas de captures.

## Choix pour cette démonstration

- Rook : `sole_skin162/human.glb`, personnage cyberpunk AmJViZ déjà texturé et animé.
- Raider : `modularity166/body_1.glb`, militaire Rocketbox, silhouette et costume distincts.
- Robot : `security_opaque137/robot_actions.glb`, Security Bot articulé.
- VTOL : `vtol_finish135/vtol_actions.glb`, rotors animés.
- Caisse, générateur et façades déjà disponibles ; carte Neon Market Alley existante.

Les candidats Hunyuan restent conservés séparément. Leur géométrie sans couleur,
arme fusionnée et absence de rig rendent les personnages professionnels plus
utiles pour une démonstration complète immédiate. Cela ne valide pas leur qualité
comme personnages définitifs. Hunyuan demeure candidat pour une génération A/T
sans arme et une vraie couleur, sans généraliser tous les agents.

## Séquence visible

Prêt, marche simultanée, tir avec accessoires réutilisés, mêlée, couverture/réaction,
PSI puis soins expérimentaux et mort. Le PSI réutilise `Spell_Simple_Shoot` CC0.
Les soins adaptent `Fixing_Kneeling` avec une mallette médicale : ce n'est pas une
animation médicale finalisée ; le contact avec un patient reste à travailler.
Les deux nouveaux mouvements sont ajoutés à la scène ; le corps et les anciens
clips de Rook sont chargés depuis leur GLB précédent, sans réexport imposé.

Le zoom tactique conserve environ 62 pixels pour 1,8 m. La vue de détail est
explicitement agrandie (~180 pixels). La démonstration est une présentation
animée, sans combat simulé, IA, pathfinding ni modification des règles.

## Droits et diffusion

Vérification préalable par notices locales conservées et FAQ officielle :
AmJViZ sous Blendkit Royalty Free ; rendu/animation permis, distribution de scène
brute et extraction facile des assets non permises. Démonstration privée seulement.
[FAQ officielle](https://www.blenderkit.com/docs/licenses/licensing-faq/).
Rocketbox : MIT, notice Microsoft conservée ; Quaternius : CC0 ; Security Bot :
CC BY 4.0, attribution Blender Foundation conservée dans ses CREDITS.

Le propriétaire demande explicitement de poursuivre les essais personnels sans
consacrer le chantier aux questions de distribution. Les notices restent
conservées ; les anciens constats de licence ne bloquent pas ces essais privés.
L'étape Paint est maintenant en préparation avec son rasterizer CUDA sur E:.
Aucune distribution des modèles expérimentaux n'est effectuée.

## Limites à garder visibles

Les façades simples restent moins abouties que la carte illustrée. Les raccords
de phases, le glissement de locomotion et le geste médical nécessitent une revue
artistique à l'écran. Les couleurs IA, un candidat A/T riggé et la comparaison
complète au zoom de 21 pixels restent ouverts. Aucun test de campagne ni test
technique historique répété pour cette livraison.
