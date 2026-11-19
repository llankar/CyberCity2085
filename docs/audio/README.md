# CyberCity 2085 — Audio Overhaul 1.0

**État du 19 novembre 2026 : la nouvelle banque est la seule banque de production. Les 19 anciens SFX et les 3 anciennes musiques WAV ont été retirés ; Arcade et Godot utilisent les WAV CC0/CC-BY/utilisateur et les 7 MP3 du nouveau soundtrack.**

## Ressources effectivement présentes

- **18 Kenney CC0** : impact, déplacement, arme laser, technologie et interface. Converties depuis des OGG originaux à un commit Git précis ; SHA Git contrôlé avant conversion.
- **5 pas métalliques Thimras CC0** : premiers extraits de l'archive 7z OpenGameArt, convertis en WAV.
- **5 effets d'explosion rubberduck CC0** : premiers extraits de l'archive ZIP OpenGameArt, conservés sans routage événement automatique tant que non auditionnés.
- **5 WAV fournis antérieurement par l'utilisateur** : pistolet, fusil d'assaut, impact métallique, pas béton et clic UI, sur cette branche (ajout initial sur main). Leur attribution précise à une génération ElevenLabs reste à confirmer.
- **Aucun ancien fallback audio** : tous les événements historiques sont conservés mais routés vers les nouveaux fichiers. Les événements sans équivalent unique réutilisent un son proche documenté dans `game/audio/overhaul_assets.py`.

Les **28 WAV CC0** sont des fichiers matériels réels dans `assets/audio/overhaul/`, documentés dans [cc_import_receipts.json](cc_import_receipts.json) et [CREDITS_CC_AUDIO.md](../../assets/audio/CREDITS_CC_AUDIO.md). Tous portent le statut `installed_unreviewed` : contrôles techniques et décodage réalisés, mais aucune validation à l'écoute.

## Quatre ressources Freesound reçues et installées

Le 19 novembre 2026, l'utilisateur a transmis les quatre **originaux authentiques** déjà sélectionnés. Ils ont été vérifiés et convertis en WAV PCM 16 bits stéréo 48 kHz :

| Ressource | Auteur / licence | WAV prêt, non committé | Contrôle technique |
|---|---|---|---|
| Seamless City Loop | qubodup / CC0 | `ambience/ambience_city_cc0_01.wav` | 30 s, -6.46 dBFS peak |
| Raining in the City | RyanKingArt / CC0 | `ambience/ambience_city_rain_cc0_01.wav` | 97.14 s, crossfade de boucle 1.5 s |
| Robot / Mech Movement | Breviceps / CC0 | `movement/move_robot_cc0_01.wav` | 0.99 s, -3.5 dBFS peak |
| Dark Sci-Fi Laboratory | TommasoMotteran / CC BY 4.0 | `ambience/ambience_laboratory_ccby_01.wav` | 47.25 s, crossfade de boucle 0.75 s |

Les quatre WAV sont installés dans `assets/audio/overhaul/` et leurs empreintes sont enregistrées dans `docs/audio/freesound_received_manifest.json`.

Arcade utilise le fond urbain de gestion ; Godot dispose des profils `city`, `city_rain`, `laboratory` et du déclencheur `move_robot` pour les unités robotiques. Les quatre WAV sont techniquement routés mais n'ont pas été écoutés/validés en partie.

Crédits : [Freesound](../../assets/audio/CREDITS_FREESOUND_AUDIO.md). Empreintes de réception : [sources CC0/CC BY](cc0_ccby_sources.json).

## Tests et reproductibilité

- [Procédure d'importation CC0 / CC BY](CC0_CC_BY_IMPORT.md) : téléchargement direct des 3 packs Kenney retenus et des 2 archives OpenGameArt ; ajout manuel des originaux Freesound obtenus avec le compte de l'utilisateur ; conversion PCM WAV 48 kHz, stéréo 16 bits.
- [GitHub Actions : Build pinned CC0 sound previews](../../.github/workflows/build-cc0-audio.yml) — **réussi**, depuis téléchargement, contrôles SHA Git, test import et routage, conversion, jusqu'au commit audio.
- **Godot 4.6 headless : réussi**. Le test charge le script réel `audio_manager.gd` et décode/déclenche des WAV réellement présents, avec `GODOT_CC_AUDIO_SMOKE_OK`.
- **Arcade : tests ciblés avec mocks**, sans périphérique audio ni partie complète. Un nouveau WAV absent rend l'événement silencieux au lieu de restaurer l'ancienne banque.
- La **suite générale de tests du jeu n'est pas verte** : des échecs UI/environnement/règles indépendants ont été constatés. Ils ne sont pas masqués par les résultats des tests audio.
- Aucune preuve d'écoute humaine ou de lecture complète Arcade/Godot en jeu ; les ressources ne sont pas considérées « approved ».
- Certains sons CC0 Kenney sont très courts et pourraient sembler artificiels ou répétitifs : filtrage à l'écoute obligatoire.

## Plan ElevenLabs préexistant

Le [manifeste ElevenLabs](elevenlabs_manifest.json) décrit **58 familles et 167 variantes visées** et les nœuds de génération correspondants. Sept générations fournisseur ont été réalisées et identifiées (5 familles) ; cela ne signifie pas que les 167 variantes aient été produites, ni que toutes les correspondances des fichiers WAV utilisateur aient été vérifiées.

Projets existants : [principal](https://elevenlabs.io/app/flows/3m8GvCVzF9JhOgZl3kbb), [armes](https://elevenlabs.io/app/flows/vj5p3VgAMplpSMS6QnwY), [combats](https://elevenlabs.io/app/flows/hqjK65yzArYgCCR3Ylun), [déplacements](https://elevenlabs.io/app/flows/kDhE2kIk7F7y8aeom152), [ambiances](https://elevenlabs.io/app/flows/OEDA8eQA1fnUUe1mqrlT).

## Conditions de validation avant fusion

1. Écouter et classer les sons réellement installés, écarter ceux à rendu arcade/clip/queue anormale ; vérifier les coutures d'ambiances et les niveaux de mixage.
2. Vérifier les interactions en jeu Arcade et combats Godot (matériau réel, arme réelle, fréquence et simultanéité). Les événements génériques `fire` et `hit` ne transmettent pas actuellement toutes les métadonnées nécessaires à un routage par arme/matériau.
3. Conserver les attributions CC0/CC-BY et les empreintes des quatre ressources Freesound désormais installées.
4. Valider artistiquement à l'écoute les réutilisations choisies pour les événements sans équivalent dédié.

**La pull request reste en brouillon : aucune fusion / publication définitive n'a été effectuée.**
