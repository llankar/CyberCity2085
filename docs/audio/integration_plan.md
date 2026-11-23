# CyberCity 2085 — Plan d'intégration Codex des bruitages

## État et limites
Le manifeste reste majoritairement **pending_generation**, mais douze générations fournisseur sont maintenant confirmées et cinq sorties du lot du 22 novembre ont été téléchargées puis converties en staging sur `E:`. Aucune n'est intégrée : quatre attendent une écoute humaine ; l'impact métal `xv8Gzq2sccJdkTGrTECr` est rejeté techniquement comme quasi inaudible. Les conditions EEE ElevenLabs consultées le 23 novembre 2026 réservent l'usage commercial aux utilisateurs payants. Le connecteur ne prouve pas le plan actif lors des générations : les cinq sorties sont donc bloquées pour distribution jusqu'à justification du plan et des droits applicables. Ne jamais déclarer une variante prête si le WAV final approuvé n'existe pas. Préserver les MP3 du catalogue.

## Source de vérité
- L'ancien inventaire des 19 WAV a été retiré avec la banque historique.
- `docs/audio/elevenlabs_manifest.json` fournit les 58 familles, 167 variantes, prompts, déclencheurs cibles et chemins.
- Garder les clés d'événements compatibles (`sfx_fire` Arcade et `fire` Godot, etc.).
- Le générateur procédural historique a été retiré afin qu'il ne puisse pas recréer l'ancienne banque.

## Chaîne de production
1. Vérifier le solde/crédits de la formule et estimer un lot avant de lancer une grande quantité.
2. Lancer ElevenLabs Sound Effects v2 sur chaque famille; prompt clair, une seule action sonore. Ajuster `duration_seconds` (0,5–30s), `prompt_influence` et `loop` (true seulement pour les ambiances).
3. Récupérer les vrais fichiers à partir des générations terminées; nommer `assets/audio/overhaul/<category>/<family>_NN.wav`.
4. Consigner par variante : ID de génération, lien permanent si disponible, prompt effectivement lancé, modèle retourné, fichier WAV local, codec/canaux/fréquence, durée **mesurée**, statut d'écoute, licence à vérifier. Les URL signées expirent : conserver un identifiant de génération stable.
5. Auditer les fichiers : entête WAV, décodage réussi, aucun fichier vide, pas de clipping involontaire, queue naturelle sans coupure brutale, pas de voix/musique, pas de duplication exacte. Pour les boucles : auditionner explicitement la jonction et vérifier l'absence de clic.
6. N'autoriser le routage que si une variante est `ready` et si le fichier existe. Les autres continuent à utiliser le WAV historique.

## Architecture audio partagée
- Construire une table d'événements sémantiques commune (tir selon `weapon_kind`, impact selon `surface`, pas selon `floor_material`, unité selon `unit_kind`, UI, technologie, ambiance).
- L'API doit accepter `event, context, position, intensity, category`, avec valeurs par défaut et traitement des données absentes.
- Sélection déterministe ou pseudo-aléatoire reproductible parmi les variantes validées, avec **non-répétition immédiate** pour les familles fréquentes. Éviter le même échantillon à chaque projectile et à chaque pas.
- Ajouter anti-spam/cooldowns par famille, gestion de priorité/voix simultanées et limitation du niveau total des SFX, sans couper les sons critiques.
- Conserver un mix à bus distincts : `Music`, `SFX`, `UI`, `Ambience`; volume de chacun, voix prioritaires et protection contre les pics. L'ambiance ne doit pas masquer les informations tactiques; prévoir fondu d'entrée/sortie.
- Uniformiser le contexte de source entre le shell Python Arcade et les scènes Godot. Les fonctions music de `game/audio/music_catalog.py` restent inchangées.

## Correctifs nécessaires
- `game/audio/sound_manager.py` : conserver `play(name)` historique et résoudre les variantes exclusivement dans la nouvelle banque ; `play_music` reste indépendant.
- `game/gamestate.py` : résoudre explicitement `recruitment`, `selection`, `toggle`, qui correspondent à des clés SFX manquantes.
- `godot/combat_missions_ui/scripts/audio_manager.gd` : charger les nouveaux fichiers disponibles, choisir variantes selon métadonnées des événements, préserver la lecture des 18 événements actuels. Remplacer la logique de 6 lecteurs cycliques par un pool qui cherche un lecteur disponible et dégrade proprement sous forte charge.
- `game/combat/godot_bridge.py` : transférer les WAV disponibles et un manifeste compatible vers Godot (chemins relatifs, extension WAV, pas de noms en collision). Pas de lecture d'un fichier de manifeste comme s'il était un son.
- Événements de combat (`game/views.py`, `godot/combat_missions_ui/scripts/combat_mission_ui.gd`, `unit_visual.gd`, `unit_token.gd`) : transmettre type d'arme / matériau / type d'unité quand ils sont connus. Ne pas inventer de contexte.
- Ambiances : ne pas jouer de longues boucles avec l'API d'effets éphémères; gérer une piste d'ambiance dédiée avec transition entre scènes.
- Protéger les MP3 présents dans `assets/audio/music/` et les formats d'assets utilisés par le soundtrack handoff.

## Tests et critères d'acceptation
- Test JSON : exactement une entrée par famille, chemins uniques, variantes sans collision et durée entre 0,5 et 30s.
- Test SFX : les fichiers `ready` se décodent; les `pending_generation` ne sont jamais chargés.
- Test routage : `play('sfx_fire')` utilise la nouvelle banque sans fallback historique, avec impact métal distinct du béton, mouvements distincts et UI non agressive.
- Test variété : pas de répétition immédiatement consecutive lorsque >=2 variantes validées.
- Test simultanéité : rafale / impacts / clics joués ensemble n'interrompent pas les événements prioritaires.
- Test synchronisation Arcade→Godot et retour : musique inchangée et volumes cohérents.
- Test d'environnement : chaque ambiance bouclée n'a ni trou ni clic audible à la jonction.
- Validation visuelle/code + **écoute humaine** obligatoires avant de marquer `validated`; ne jamais prétendre avoir auditionné si ce n'est pas vrai.
- Ne déclarer l'overhaul finalisé que si les 58 familles, 167 variantes visées (ou révision justifiée), contrôles audio et tests des deux moteurs sont réellement validés.

## Définition de fait
`DONE` = fichiers audio réels + checks machine + écoute + routage dans les deux moteurs + tests verts + musique préservée. Toute autre étape est `PARTIAL` ou `BLOCKED`.
