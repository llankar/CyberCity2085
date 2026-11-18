# CODEX — registre persistant

**CHANTIER GLOBAL INCOMPLET**

Source structurée : `docs/CODEX_PROGRESS.json`. Générer ce document avec la commande de [vérification globale](COMBAT_VISUAL_ACCEPTANCE.md).

Statuts : `TODO` non commencé ; `IN_PROGRESS` en cours ; `DONE` réalisé et vérifié dans la portée indiquée ; `BLOCKED` bloqué avec raison explicite.

## Tâches et preuves

### GOV-01 — DONE — Consignes permanentes et lots successifs

- Fichiers : `AGENTS.md`.
- Tests / contrôles réellement exécutés : python -m pytest -q tests/test_combat_visual_acceptance.py tests/test_environment_progress.py --junitxml=docs/reports/work_governance_tests.xml; Contrôle du maintien des règles qualité et absence de la phrase retirée.
- Preuves : `AGENTS.md`, `docs/reports/work_governance_tests.xml`.
- Travail restant dans cette portée : Aucun.

### GOV-02 — DONE — Registre structuré avec portées et preuves

- Fichiers : `docs/CODEX_PROGRESS.json`, `docs/CODEX_PROGRESS.md`.
- Tests / contrôles réellement exécutés : python -m pytest -q tests/test_combat_visual_acceptance.py tests/test_environment_progress.py --junitxml=docs/reports/work_governance_tests.xml; Contrôles DONE sans preuve, BLOCKED sans raison et statuts invalides.
- Preuves : `docs/CODEX_PROGRESS.json`, `docs/reports/work_governance_tests.xml`.
- Travail restant dans cette portée : Aucun.

### GOV-03 — DONE — Critères globaux réels et méthode reproductible

- Fichiers : `docs/COMBAT_VISUAL_ACCEPTANCE.md`.
- Tests / contrôles réellement exécutés : python -m pytest -q tests/test_combat_visual_acceptance.py tests/test_environment_progress.py --junitxml=docs/reports/work_governance_tests.xml; Contrôles distinguant chargement, art déclaré, art revu et couverture attendue.
- Preuves : `docs/COMBAT_VISUAL_ACCEPTANCE.md`, `docs/reports/work_governance_tests.xml`.
- Travail restant dans cette portée : Aucun.

### GOV-04 — DONE — Outil de vérification et rapport FAIL/NOT VERIFIED honnête

- Fichiers : `tools/check_combat_visual_acceptance.py`, `tests/test_combat_visual_acceptance.py`, `docs/reports/combat_visual_acceptance.json`.
- Tests / contrôles réellement exécutés : python -m pytest -q tests/test_combat_visual_acceptance.py tests/test_environment_progress.py --junitxml=docs/reports/work_governance_tests.xml; python -m tools.check_combat_visual_acceptance --write : code 1 attendu, CHANTIER GLOBAL INCOMPLET sur les vraies données.
- Preuves : `docs/reports/work_governance_tests.xml`, `docs/reports/combat_visual_acceptance.json`, `docs/reports/combat_visual_acceptance.md`.
- Travail restant dans cette portée : Aucun.

### GOV-05 — DONE — Bilan final, contrôle du périmètre et sauvegarde Git locale

- Fichiers : `AGENTS.md`, `docs/CODEX_PROGRESS.md`, `docs/backlog.md`, `docs/reports/work_governance_scope.json`.
- Tests / contrôles réellement exécutés : git diff --name-only 47d593b ; contrôle des chemins autorisés; git commit 2a73feb : sauvegarde locale créée; git diff --name-only 47d593b : aucune modification du gameplay.
- Preuves : `docs/reports/work_governance_scope.json`.
- Travail restant dans cette portée : Aucun.

### ART-NEXT-01 — DONE — Deux nouvelles agentes : sources dessinées et identité

- Fichiers : `assets/units/agent_diverse_01_neon_blade_512.png`, `assets/units/agent_diverse_03_magenta_pistol_512.png`.
- Tests / contrôles réellement exécutés : Inspection initiale des PNG de référence ; aucune validation native des nouveaux dessins; Six planches comparées aux PNG originaux ; empreintes vérifiées avant import.
- Preuves : `assets/combat_visual/source_sheets/import-plan.json`.
- Travail restant dans cette portée : Aucun.

### ART-NEXT-02 — DONE — Importer les deux atlas et contrôler les silhouettes

- Fichiers : `tools/art/import_directional_clips.py`, `assets/combat_visual/animations`.
- Tests / contrôles réellement exécutés : Import existant utilisé ; huit directions et poses uniques contrôlées par validate_atlas; Inspection des deux atlas nettoyés, marges, lames, pistolet et identités.
- Preuves : `assets/combat_visual/animations/agent_diverse_01_neon_blade.json`, `assets/combat_visual/animations/agent_diverse_03_magenta_pistol.json`.
- Travail restant dans cette portée : Aucun.

### ART-NEXT-03 — DONE — Étendre les tests aux six références sans perdre les quatre précédentes

- Fichiers : `tests/test_directional_animation.py`, `godot/combat_missions_ui/tests/directional_animation_regression.gd`.
- Tests / contrôles réellement exécutés : 55 tests ciblés réussis ; 192 sélections de frames natives sur six références.
- Preuves : `docs/reports/roster_batch2_runtime_tests.xml`.
- Travail restant dans cette portée : Aucun.

### ART-NEXT-04 — DONE — Captures et interactions natives du nouveau lot

- Fichiers : `godot/combat_missions_ui/tests/capture_directional_animation.gd`.
- Tests / contrôles réellement exécutés : Deux clics de déplacement : 4 PA dépensés par agente, destinations atteintes et retour idle; Captures réelles aux trois résolutions, orientations et mouvements inspectés.
- Preuves : `docs/images/roster-batch2/animation-report.json`, `docs/images/roster-batch2/README.md`.
- Travail restant dans cette portée : Aucun.

### ART-NEXT-05 — DONE — Actualiser couverture, preuves et prochain lot artistique

- Fichiers : `docs/combat_visual_25_status.json`, `docs/CODEX_PROGRESS.json`.
- Tests / contrôles réellement exécutés : 122 captures natives terminées, 221 placements de décor inchangés; Galeries de six références et déplacements archivés ; bilans actualisés.
- Preuves : `docs/images/roster-batch2/native-report.json`, `docs/images/roster-batch2/README.md`.
- Travail restant dans cette portée : Aucun.

### SCALE-01 — DONE — Inventorier les profils actuels, sources et variantes du catalogue

- Fichiers : `tools/audit_entity_scale.py`, `docs/reports/entity_scale_baseline.json`, `docs/reports/entity_scale_baseline.md`.
- Tests / contrôles réellement exécutés : 122 cartes / 92 illustrations ; aucune empreinte source incohérente; 33 tests ciblés du suivi et de l’inventaire réussis.
- Preuves : `docs/reports/entity_scale_baseline.json`, `docs/reports/entity_scale_baseline.md`, `docs/reports/scale_inventory_tests.xml`.
- Travail restant dans cette portée : Aucun.

### UE1-01 — DONE — Isoler les sessions et contrats

- Fichiers : `docs/UNIFIED_EXPERIENCE_PROGRESS.md`.
- Tests / contrôles réellement exécutés : 67 tests distincts réussis ; trois parcours natifs Linux contrôlés.
- Preuves : `docs/reports/unified_batch1_tests.xml`, `docs/images/unified-experience/batch1/native-report.json`, `docs/images/unified-experience/batch1/README.md`.
- Travail restant dans cette portée : Aucun.
- Problème / raison : Portée limitée au premier lot fonctionnel ; aucune validation graphique Windows.

### UE1-02 — DONE — Différer la publication jusqu’à confirmation et ACK

- Fichiers : `docs/UNIFIED_EXPERIENCE_PROGRESS.md`.
- Tests / contrôles réellement exécutés : 67 tests distincts réussis ; trois parcours natifs Linux contrôlés.
- Preuves : `docs/reports/unified_batch1_tests.xml`, `docs/images/unified-experience/batch1/native-report.json`, `docs/images/unified-experience/batch1/README.md`.
- Travail restant dans cette portée : Aucun.
- Problème / raison : Portée limitée au premier lot fonctionnel ; aucune validation graphique Windows.

### UE1-03 — DONE — Extraire et réutiliser la résolution de campagne

- Fichiers : `docs/UNIFIED_EXPERIENCE_PROGRESS.md`.
- Tests / contrôles réellement exécutés : 67 tests distincts réussis ; trois parcours natifs Linux contrôlés.
- Preuves : `docs/reports/unified_batch1_tests.xml`, `docs/images/unified-experience/batch1/native-report.json`, `docs/images/unified-experience/batch1/README.md`.
- Travail restant dans cette portée : Aucun.
- Problème / raison : Portée limitée au premier lot fonctionnel ; aucune validation graphique Windows.

### UE1-04 — DONE — Router débriefing, promotions et HQ

- Fichiers : `docs/UNIFIED_EXPERIENCE_PROGRESS.md`.
- Tests / contrôles réellement exécutés : 67 tests distincts réussis ; trois parcours natifs Linux contrôlés.
- Preuves : `docs/reports/unified_batch1_tests.xml`, `docs/images/unified-experience/batch1/native-report.json`, `docs/images/unified-experience/batch1/README.md`.
- Travail restant dans cette portée : Aucun.
- Problème / raison : Portée limitée au premier lot fonctionnel ; aucune validation graphique Windows.

### UE1-05 — DONE — Vérifier le lot fonctionnel et ses limites

- Fichiers : `docs/UNIFIED_EXPERIENCE_PROGRESS.md`.
- Tests / contrôles réellement exécutés : 67 tests distincts réussis ; trois parcours natifs Linux contrôlés.
- Preuves : `docs/reports/unified_batch1_tests.xml`, `docs/images/unified-experience/batch1/native-report.json`, `docs/images/unified-experience/batch1/README.md`.
- Travail restant dans cette portée : Aucun.
- Problème / raison : Portée limitée au premier lot fonctionnel ; aucune validation graphique Windows.

### UE2-01 — DONE — Journal Python durable avant/après résolution

- Fichiers : `game/combat/session_protocol.py`, `game/combat/godot_resolution.py`, `game/combat/checkpoints.py`.
- Tests / contrôles réellement exécutés : 65 tests ciblés Python/Godot du lot 2 ; 19 régressions de lancement; Parcours natifs Linux : crash/récupération sur trois issues en 720p ; victoire et reprise en 1080p/1440p.
- Preuves : `docs/reports/unified_batch2_tests.xml`, `docs/reports/unified_window_regression_tests.xml`, `docs/images/unified-experience/batch2/README.md`.
- Travail restant dans cette portée : Aucun.
- Problème / raison : Portée du lot : récupération après résultat préparé et reprise du débriefing, pas reprise du tour en cours.

### UE2-02 — DONE — Reprendre le débriefing après crash sans rejouer les récompenses

- Fichiers : `game/ui/screens/mission_return.py`, `game/ui/screens/godot_combat_handoff_view.py`, `game/combat/return_snapshot.py`, `game/ui/screens/combat_recovery.py`, `game/ui/screens/title_screen.py`.
- Tests / contrôles réellement exécutés : 65 tests ciblés Python/Godot du lot 2 ; 19 régressions de lancement; Parcours natifs Linux : crash/récupération sur trois issues en 720p ; victoire et reprise en 1080p/1440p.
- Preuves : `docs/reports/unified_batch2_tests.xml`, `docs/reports/unified_window_regression_tests.xml`, `docs/images/unified-experience/batch2/README.md`.
- Travail restant dans cette portée : Aucun.
- Problème / raison : Portée du lot : récupération après résultat préparé et reprise du débriefing, pas reprise du tour en cours.

### UE2-03 — DONE — Readiness, statuts et délais de communication

- Fichiers : `game/combat/session_protocol.py`, `godot/combat_missions_ui/scripts/session_mailbox.gd`, `game/ui/screens/godot_combat_handoff_view.py`.
- Tests / contrôles réellement exécutés : 65 tests ciblés Python/Godot du lot 2 ; 19 régressions de lancement; Parcours natifs Linux : crash/récupération sur trois issues en 720p ; victoire et reprise en 1080p/1440p.
- Preuves : `docs/reports/unified_batch2_tests.xml`, `docs/reports/unified_window_regression_tests.xml`, `docs/images/unified-experience/batch2/README.md`.
- Travail restant dans cette portée : Aucun.
- Problème / raison : Portée du lot : récupération après résultat préparé et reprise du débriefing, pas reprise du tour en cours.

### UE2-04 — IN_PROGRESS — Cycle de vie Win32 et continuité de fenêtre

- Fichiers : `game/combat/win32_embed.py`, `game/ui/screens/godot_combat_handoff_view.py`.
- Tests / contrôles réellement exécutés : 65 tests ciblés Python/Godot du lot 2 ; 19 régressions de lancement; Parcours natifs Linux : crash/récupération sur trois issues en 720p ; victoire et reprise en 1080p/1440p.
- Preuves : `docs/reports/unified_batch2_tests.xml`, `docs/reports/unified_window_regression_tests.xml`, `docs/images/unified-experience/batch2/README.md`.
- Travail restant dans cette portée : Validation graphique Windows restante : redimensionnement et DPI multi-écrans.
- Problème / raison : Alt+Tab, réduction et restauration visuellement vérifiés ; bord de redimensionnement intercepté par la fenêtre Godot possédée.

### UE2-05 — DONE — Scénarios de crash, récupération et bilan du lot

- Fichiers : `tests/test_unified_mission_resolution.py`, `docs/UNIFIED_EXPERIENCE_PROGRESS.md`.
- Tests / contrôles réellement exécutés : 65 tests ciblés Python/Godot du lot 2 ; 19 régressions de lancement; Parcours natifs Linux : crash/récupération sur trois issues en 720p ; victoire et reprise en 1080p/1440p.
- Preuves : `docs/reports/unified_batch2_tests.xml`, `docs/reports/unified_window_regression_tests.xml`, `docs/images/unified-experience/batch2/README.md`.
- Travail restant dans cette portée : Aucun.
- Problème / raison : Portée du lot : récupération après résultat préparé et reprise du débriefing, pas reprise du tour en cours.

### SCALE-02 — IN_PROGRESS — Mesurer les repères visuels par illustration et vérifier les variantes

- Fichiers : `docs/reports/entity_scale_baseline.json`.
- Tests / contrôles réellement exécutés : Deux voitures identifiées visuellement et axes source annotés avec incertitude; Quatre cas natifs comparatifs à trois résolutions réussis ; ratio demandé/appliqué vérifié ; tous marqués NOT VERIFIED.
- Preuves : `docs/reports/entity_scale_anchor_samples.json`, `docs/images/entity-scale-diagnostics/README.md`, `docs/images/entity-scale-diagnostics/native-diagnostics.json`.
- Travail restant dans cette portée : Deux illustrations urbaines ont un repère automobile proposé, mais aucune carte n’est approuvée. Ajouter plusieurs repères, examiner appartement/industrie/laboratoire/wasteland, puis toutes les illustrations et variantes. Comparer toutes les catégories et la lisibilité avant application..

### SCALE-03 — TODO — Appliquer les profils visuels par carte et catégorie

- Fichiers : `godot/combat_missions_ui/scripts/map_presentation.gd`, `godot/combat_missions_ui/scripts/unit_presentation.gd`, `godot/combat_missions_ui/art/environment/map_presentation.json`.
- Tests / contrôles réellement exécutés : Aucun — non exécutés.
- Preuves : Aucune.
- Travail restant dans cette portée : Après mesures : adapter les PJ/PNJ/robots/armures/véhicules, préserver proportions, ancrage et données tactiques ; conserver fallback lorsque l’échelle est incertaine.

### SCALE-04 — TODO — Vérifier les 122 cartes et les interactions aux trois résolutions

- Fichiers : `godot/combat_missions_ui/tests/capture_combat_21.gd`, `godot/combat_missions_ui/tests/directional_animation_regression.gd`.
- Tests / contrôles réellement exécutés : Aucun — non exécutés.
- Preuves : Aucune.
- Travail restant dans cette portée : Comparer les tailles au décor, contrôler occultation, zoom, clics et déplacements ; ne pas confondre chargement et échelle visuellement validée.

### SCALE-05 — TODO — Archiver les comparatifs et le résultat réel de la passe d’échelle

- Fichiers : `docs/CODEX_PROGRESS.json`, `docs/COMBAT_VISUAL_ACCEPTANCE.md`.
- Tests / contrôles réellement exécutés : Aucun — non exécutés.
- Preuves : Aucune.
- Travail restant dans cette portée : Renseigner uniquement les cartes effectivement calibrées et revues ; conserver NOT VERIFIED pour les autres, sauvegarder puis identifier le lot suivant.

### ENV-FINAL — IN_PROGRESS — Finition artistique individuelle des 122 cartes

- Fichiers : `godot/combat_missions_ui/art/environment/environment_art.json`, `docs/combat_visual_25_inventory.md`.
- Tests / contrôles réellement exécutés : Historique : captures natives des 122 cartes ; ne valide pas la finition.
- Preuves : `docs/images/combat-directional-animation/README.md`, `docs/images/combat-directional-animation/validation-results.txt`.
- Travail restant dans cette portée : 0 / 122 finalisées artistiquement ; poursuivre murs, objets, raccords et revues détaillées.

### UNIT-COVERAGE — IN_PROGRESS — Identités de toutes les familles d’unités

- Fichiers : `assets/units`, `assets/combat_visual/animations`.
- Tests / contrôles réellement exécutés : Historique : audit de 251 références ; 4 atlas partiels vérifiés; Lot 2 : six atlas marche/attente, 288 frames, six références vérifiées nativement.
- Preuves : `docs/images/combat-directional-animation/README.md`, `docs/images/combat-directional-animation/validation-results.txt`.
- Travail restant dans cette portée : Couvrir les 225 autres références éligibles, dont autres agents/ennemis, robots, armures et véhicules.

### ANIM-COMPLETE — TODO — Actions multidirectionnelles complètes et applicabilité documentée

- Fichiers : `assets/combat_visual/animations`, `tools/audit_combat_visuals.py`.
- Tests / contrôles réellement exécutés : Aucun — non exécutés.
- Preuves : `docs/images/combat-directional-animation/README.md`, `docs/images/combat-directional-animation/validation-results.txt`.
- Travail restant dans cette portée : 0 / 231 ensembles complets ; documenter les actions applicables puis produire les clips manquants.

### TACTICAL-REVIEW — TODO — Validation artistique et fonctionnelle globale aux trois résolutions

- Fichiers : `godot/combat_missions_ui/tests`, `docs/images/combat-directional-animation`.
- Tests / contrôles réellement exécutés : Historique : 34 tests ciblés, 128 sélections de frames et déplacement à 4 PA ; portée partielle.
- Preuves : `docs/images/combat-directional-animation/README.md`, `docs/images/combat-directional-animation/validation-results.txt`.
- Travail restant dans cette portée : Exécuter les interactions et revues restant ouvertes ; ne pas extrapoler depuis cinq familles.

### GPU-BENCH — DONE — Performance et mémoire sur matériel joueur

- Fichiers : `godot/combat_missions_ui/tests/capture_combat_21.gd`, `tools/run_windows_gpu_benchmark.ps1`, `tests/test_windows_gpu_benchmark.py`.
- Tests / contrôles réellement exécutés : Benchmark natif Windows 1440p : 2400 frames animées sur NVIDIA RTX 5070 Ti; 185,15 FPS moyens ; p95 7,876 ms / 126,97 FPS ; pic mémoire statique Godot 441 MiB; 35 échantillons système : CPU total moyen 5,51 %, GPU moyen 16,31 %, pic GPU 20 %, pic VRAM processus observé 2721 MiB.
- Preuves : `docs/reports/windows_gpu_benchmark_system.json`.
- Travail restant dans cette portée : Aucun.
- Problème / raison : Portée : une machine Windows RTX 5070 Ti et un combat représentatif 1440p ; ne constitue pas une validation de configuration minimale.

### SCALE-CATALOGUE — IN_PROGRESS — Recalibrer PJ, PNJ, robots, armures et véhicules sur les décors des 122 cartes

- Fichiers : `godot/combat_missions_ui/scripts/unit_presentation.gd`, `godot/combat_missions_ui/scripts/visual_battlefield.gd`, `godot/combat_missions_ui/scripts/combat_mission_ui.gd`, `godot/combat_missions_ui/scripts/unit_visual.gd`, `assets/maps/*.walls.json`.
- Tests / contrôles réellement exécutés : Aucun — non exécutés.
- Preuves : Aucune.
- Travail restant dans cette portée : Après le lot animé en cours : relever sur chaque carte des repères vérifiables (portes, voitures du décor, mobilier, largeur des rues) ; définir des profils visuels par carte/famille et catégorie d’entité ; contrôler les 122 cartes avec comparatifs, trois résolutions et clics. Aucune validation d’échelle déduite d’un simple chargement ou de token_terrain_scale existant..
- Problème / raison : La capture utilisateur montre des voitures du décor trop petites face aux personnages et au véhicule déployé ; les cartes n’ont pas toutes la même échelle artistique..

### UE3-01 — DONE — Transférer la musique après readiness sans silence de chargement

- Fichiers : `game/combat/audio_transfer.py`, `game/combat/session_protocol.py`, `godot/combat_missions_ui/scripts/audio_manager.gd`.
- Tests / contrôles réellement exécutés : 57 cas ciblés Python/Godot réussis; Parcours natif Linux avec propriété Godot absente avant release puis accordée après readiness ; débriefing/promotions/HQ et replay vérifiés.
- Preuves : `docs/reports/unified_audio_tests.xml`, `docs/images/unified-experience/batch3/README.md`, `docs/images/unified-experience/batch3/audio-native-report.json`.
- Travail restant dans cette portée : Aucun.
- Problème / raison : Audio Dummy : validation auditive non disponible.

### UE3-02 — DONE — Restituer la lecture après erreur ou retour de Godot

- Fichiers : `game/audio/sound_manager.py`, `game/ui/screens/godot_combat_handoff_view.py`.
- Tests / contrôles réellement exécutés : 57 cas ciblés Python/Godot réussis; Parcours natif Linux avec propriété Godot absente avant release puis accordée après readiness ; débriefing/promotions/HQ et replay vérifiés.
- Preuves : `docs/reports/unified_audio_tests.xml`, `docs/images/unified-experience/batch3/README.md`, `docs/images/unified-experience/batch3/audio-native-report.json`.
- Travail restant dans cette portée : Aucun.
- Problème / raison : Audio Dummy : validation auditive non disponible.

### UE3-03 — DONE — Vérifier propriété audio et parcours natif sans prétendre valider le son

- Fichiers : `tests/test_unified_audio_transfer.py`, `godot/combat_missions_ui/tests/unified_return_flow.gd`.
- Tests / contrôles réellement exécutés : 57 cas ciblés Python/Godot réussis; Parcours natif Linux avec propriété Godot absente avant release puis accordée après readiness ; débriefing/promotions/HQ et replay vérifiés.
- Preuves : `docs/reports/unified_audio_tests.xml`, `docs/images/unified-experience/batch3/README.md`, `docs/images/unified-experience/batch3/audio-native-report.json`.
- Travail restant dans cette portée : Aucun.
- Problème / raison : Audio Dummy : validation auditive non disponible.

### UE4-01 — DONE — Inventorier les états tactiques et définir le contrat de reprise

- Fichiers : `godot/combat_missions_ui/scripts/tactical_checkpoint.gd`, `docs/UNIFIED_TACTICAL_SNAPSHOT.md`.
- Tests / contrôles réellement exécutés : 104 tests ciblés Python/Godot PASS ; roundtrips phase joueur/ennemi, agents/robot/armure, projections top-down/isométrique et mode legacy ; changement de résolution et clics après recadrage; Parcours natifs : reprise joueur 720p/1080p, ancien processus encore vivant en phase ennemie 720p/1440p, ACK après résolution sauvegardée.
- Preuves : `docs/reports/unified_batch4_tests.xml`, `docs/images/unified-experience/batch4/README.md`, `docs/UNIFIED_TACTICAL_SNAPSHOT.md`.
- Travail restant dans cette portée : Aucun.
- Problème / raison : Reprise au dernier état logique enregistré ; effets en cours et RNG futur non sérialisés ; Windows toujours non validé.

### UE4-02 — DONE — Écrire un instantané atomique après les actions résolues

- Fichiers : `godot/combat_missions_ui/scripts/combat_mission_ui.gd`.
- Tests / contrôles réellement exécutés : 104 tests ciblés Python/Godot PASS ; roundtrips phase joueur/ennemi, agents/robot/armure, projections top-down/isométrique et mode legacy ; changement de résolution et clics après recadrage; Parcours natifs : reprise joueur 720p/1080p, ancien processus encore vivant en phase ennemie 720p/1440p, ACK après résolution sauvegardée.
- Preuves : `docs/reports/unified_batch4_tests.xml`, `docs/images/unified-experience/batch4/README.md`, `docs/UNIFIED_TACTICAL_SNAPSHOT.md`.
- Travail restant dans cette portée : Aucun.
- Problème / raison : Reprise au dernier état logique enregistré ; effets en cours et RNG futur non sérialisés ; Windows toujours non validé.

### UE4-03 — DONE — Valider et restaurer sans modifier les règles ni la campagne

- Fichiers : `game/combat/tactical_recovery.py`.
- Tests / contrôles réellement exécutés : 104 tests ciblés Python/Godot PASS ; roundtrips phase joueur/ennemi, agents/robot/armure, projections top-down/isométrique et mode legacy ; changement de résolution et clics après recadrage; Parcours natifs : reprise joueur 720p/1080p, ancien processus encore vivant en phase ennemie 720p/1440p, ACK après résolution sauvegardée.
- Preuves : `docs/reports/unified_batch4_tests.xml`, `docs/images/unified-experience/batch4/README.md`, `docs/UNIFIED_TACTICAL_SNAPSHOT.md`.
- Travail restant dans cette portée : Aucun.
- Problème / raison : Reprise au dernier état logique enregistré ; effets en cours et RNG futur non sérialisés ; Windows toujours non validé.

### UE4-04 — DONE — Proposer une reprise explicite et isoler les anciennes sessions

- Fichiers : `game/ui/screens/godot_combat_handoff_view.py`.
- Tests / contrôles réellement exécutés : 104 tests ciblés Python/Godot PASS ; roundtrips phase joueur/ennemi, agents/robot/armure, projections top-down/isométrique et mode legacy ; changement de résolution et clics après recadrage; Parcours natifs : reprise joueur 720p/1080p, ancien processus encore vivant en phase ennemie 720p/1440p, ACK après résolution sauvegardée.
- Preuves : `docs/reports/unified_batch4_tests.xml`, `docs/images/unified-experience/batch4/README.md`, `docs/UNIFIED_TACTICAL_SNAPSHOT.md`.
- Travail restant dans cette portée : Aucun.
- Problème / raison : Reprise au dernier état logique enregistré ; effets en cours et RNG futur non sérialisés ; Windows toujours non validé.

### UE4-05 — DONE — Tester interruption, reprise et conséquences avec preuves natives

- Fichiers : `tests/test_unified_tactical_recovery.py`, `docs/UNIFIED_EXPERIENCE_PROGRESS.md`.
- Tests / contrôles réellement exécutés : 104 tests ciblés Python/Godot PASS ; roundtrips phase joueur/ennemi, agents/robot/armure, projections top-down/isométrique et mode legacy ; changement de résolution et clics après recadrage; Parcours natifs : reprise joueur 720p/1080p, ancien processus encore vivant en phase ennemie 720p/1440p, ACK après résolution sauvegardée.
- Preuves : `docs/reports/unified_batch4_tests.xml`, `docs/images/unified-experience/batch4/README.md`, `docs/UNIFIED_TACTICAL_SNAPSHOT.md`.
- Travail restant dans cette portée : Aucun.
- Problème / raison : Reprise au dernier état logique enregistré ; effets en cours et RNG futur non sérialisés ; Windows toujours non validé.

### UE5-01 — DONE — Jouer une mission réelle et vérifier le retour complet sous Windows

- Fichiers : `godot/combat_missions_ui/tests/unified_real_mission_flow.gd`, `tools/check_unified_return.py`, `tests/test_unified_mission_resolution.py`, `docs/UNIFIED_EXPERIENCE_PROGRESS.md`.
- Tests / contrôles réellement exécutés : 25 tests ciblés PASS dans tests/test_unified_mission_resolution.py; Parcours natif Windows : objectif réel accompli en 27 actions et 10 tours ennemis ; HQ → carte → briefing → Godot → débriefing → promotions → HQ ; sauvegarde/rechargement et application unique.
- Preuves : `docs/reports/unified_windows_real_mission_tests.xml`, `docs/images/unified-experience/windows-real-mission/native-report.json`, `docs/images/unified-experience/windows-real-mission/README.md`.
- Travail restant dans cette portée : Aucun.
- Problème / raison : Validation native Windows 1920×1080 ; audio Dummy, aucune écoute réelle.

### UE5-02 — DONE — Vérifier trois issues réelles, fenêtres Windows et décision de préchauffage

- Fichiers : `godot/combat_missions_ui/scripts/combat_mission_ui.gd`, `godot/combat_missions_ui/scripts/hud_controller.gd`, `godot/combat_missions_ui/scripts/visual_hud.gd`, `godot/combat_missions_ui/tests/unified_real_mission_flow.gd`, `tools/check_unified_return.py`.
- Tests / contrôles réellement exécutés : Trois parcours natifs Windows PASS : victoire par objectif, défaite par élimination IA, retraite par commande doublement confirmée; Inspection Windows visible : Alt+Tab, réduction et restauration PASS ; redimensionnement et DPI NOT VERIFIED; Première frame/readiness froide mesurée entre 2,109 s et 3,625 s ; aucun préchauffage ajouté.
- Preuves : `docs/images/unified-experience/windows-three-real-outcomes/native-report.json`, `docs/images/unified-experience/windows-three-real-outcomes/README.md`, `docs/reports/windows_lifecycle_visual.json`.
- Travail restant dans cette portée : Aucun.
- Problème / raison : Audio Dummy ; redimensionnement et DPI multi-écrans hors portée validée.

## Problèmes et ressources en attente

- Le modèle procédural rejeté reste hors production.
- Passe SCALE-CATALOGUE demandée : proportions des unités et véhicules à revoir sur les 122 cartes ; 0 carte vérifiée pour ce nouveau critère.
- Résolu : X11 absent après reprise ; quatre tests natifs ont échoué faute d’affichage. Session Xorg rétablie, puis 55 tests ciblés réussis. Échec initial conservé dans work/roster-batch2/tests-display-failure.log.
- Après redémarrage X11 absent : quatre échecs initiaux d’environnement ; serveur rétabli et suite complète repassée (55 réussis).
- Inventaire SCALE : 122 cartes, 92 illustrations, cinq ratios génériques, 30 groupes partageant un PNG et aucune contradiction de ratio entre alias. Les références automobiles de deux intersections suggèrent des réductions, à confirmer ; la borne actuelle .015 limite les essais plus petits. Aucune taille de production modifiée.

## Prochaine action précise

UNIFIED : valider redimensionnement et DPI multi-écrans ainsi que l’écoute audio réelle si les surfaces restent accessibles. Puis reprendre le premier chantier global non vérifié : SCALE-02 et finition artistique individuelle des cartes, sans assimiler chargement natif et revue artistique.

Le nombre de tâches DONE et les critères ouverts sont calculés dans [le bilan global](reports/combat_visual_acceptance.md). Un lot validé ne termine pas le chantier.
