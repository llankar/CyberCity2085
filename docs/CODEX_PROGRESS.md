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

### SCALE-02 — DONE — Mesurer les repères visuels par illustration et vérifier les variantes

- Fichiers : `docs/reports/entity_scale_baseline.json`.
- Tests / contrôles réellement exécutés : Deux voitures identifiées visuellement et axes source annotés avec incertitude; Quatre cas natifs comparatifs à trois résolutions réussis ; ratio demandé/appliqué vérifié; Onze planches couvrant 122 cartes inspectées : voitures, routes, épaves, portes, lits, bureaux, sièges, machines et structures.
- Preuves : `docs/reports/entity_scale_anchor_samples.json`, `docs/images/entity-scale-diagnostics/README.md`, `docs/images/entity-scale-diagnostics/native-diagnostics.json`, `docs/reports/entity_scale_review_windows.json`, `docs/images/entity-scale-production-windows/README.md`.
- Travail restant dans cette portée : Aucun.

### SCALE-03 — DONE — Appliquer les profils visuels par carte et catégorie

- Fichiers : `godot/combat_missions_ui/scripts/map_presentation.gd`, `godot/combat_missions_ui/scripts/unit_presentation.gd`, `godot/combat_missions_ui/art/environment/map_presentation.json`.
- Tests / contrôles réellement exécutés : 122 profils appliqués : urbain/wasteland 0,015 ; intérieur/petit intérieur/industrie 0,020; 6 tests de profils/inventaire réussis ; 0 empreinte source incohérente.
- Preuves : `docs/reports/entity_scale_profile_tests.xml`, `docs/reports/entity_scale_baseline.json`.
- Travail restant dans cette portée : Aucun.

### SCALE-04 — DONE — Vérifier les 122 cartes et les interactions aux trois résolutions

- Fichiers : `godot/combat_missions_ui/tests/capture_combat_21.gd`, `godot/combat_missions_ui/tests/directional_animation_regression.gd`.
- Tests / contrôles réellement exécutés : 122 cartes rendues nativement à 720p, 1080p et 1440p sur RTX 5070 Ti; Projection, zoom, picking, aspect, ancrage, ombres et absence de mutation tactique vérifiés; 11 planches 720p inspectées ; lisibilité limitante et proportions approuvées.
- Preuves : `docs/images/entity-scale-production-windows/native-report.json`, `docs/images/entity-scale-production-windows/README.md`, `docs/reports/entity_scale_review_windows.json`.
- Travail restant dans cette portée : Aucun.

### SCALE-05 — DONE — Archiver les comparatifs et le résultat réel de la passe d’échelle

- Fichiers : `docs/CODEX_PROGRESS.json`, `docs/COMBAT_VISUAL_ACCEPTANCE.md`.
- Tests / contrôles réellement exécutés : Acceptation reproductible : MAP-LOAD 122/122 et UNIT-SCALE PASS ; MAP-ART reste 0/122.
- Preuves : `docs/reports/combat_visual_acceptance.json`, `docs/reports/entity_scale_review_windows.json`.
- Travail restant dans cette portée : Aucun.

### ENV-FINAL — DONE — Finition artistique individuelle des 122 cartes

- Fichiers : `godot/combat_missions_ui/art/environment/environment_art.json`, `docs/combat_visual_25_inventory.md`.
- Tests / contrôles réellement exécutés : Historique : captures natives des 122 cartes ; ne valide pas la finition; Revue détaillée pages 1 à 21 : 122 cartes examinées ; trois aplats gris détectés, corrigés et rerendus; Catalogue natif final 122/122 avec ressources actives, interactions, picking et zoom vérifiés.
- Preuves : `docs/images/combat-directional-animation/README.md`, `docs/images/combat-directional-animation/validation-results.txt`, `docs/images/environment-art-review-windows/README.md`, `docs/images/environment-art-review-windows/manifest.json`.
- Travail restant dans cette portée : Aucun.

### UNIT-COVERAGE — IN_PROGRESS — Identités de toutes les familles d’unités

- Fichiers : `assets/units`, `assets/combat_visual/animations`.
- Tests / contrôles réellement exécutés : Historique : audit de 251 références ; 4 atlas partiels vérifiés; Lot 2 : six atlas marche/attente, 288 frames, six références vérifiées nativement.
- Preuves : `docs/images/combat-directional-animation/README.md`, `docs/images/combat-directional-animation/validation-results.txt`.
- Travail restant dans cette portée : Couvrir les 202 autres références éligibles, dont autres agents/ennemis, robots, armures et véhicules.

### ANIM-COMPLETE — IN_PROGRESS — Actions multidirectionnelles complètes et applicabilité documentée

- Fichiers : `assets/combat_visual/animations`, `tools/audit_combat_visuals.py`.
- Tests / contrôles réellement exécutés : Audit anti-doublons : 29 ensembles complets, 0 partiel; Tireuse à dreadlocks seule : 128 frames et actions applicables capturées sur refuge, usine et wasteland aux trois résolutions; 2 tests Python réussis, 1 test X11 ignoré; Godot Windows natif ciblé : 32 sélections de frames ; aucune autre unité retestée; Captures tir, mêlée et mort inspectées dans la scène tactique réelle.
- Preuves : `docs/images/combat-directional-animation/README.md`, `docs/images/combat-directional-animation/validation-results.txt`, `docs/images/neon-blade-actions/README.md`, `docs/images/neon-blade-actions/audit.json`, `docs/images/neon-blade-actions/animation-report.json`, `docs/images/magenta-pistol-actions/README.md`, `docs/images/magenta-pistol-actions/audit.json`, `docs/images/magenta-pistol-actions/animation-report.json`, `docs/images/trench-sniper-actions/README.md`, `docs/images/trench-sniper-actions/audit.json`, `docs/images/trench-sniper-actions/animation-report.json`, `docs/images/psi-doctor-actions/README.md`, `docs/images/psi-doctor-actions/audit.json`, `docs/images/psi-doctor-actions/animation-report.json`, `docs/images/street-medic-actions/README.md`, `docs/images/street-medic-actions/audit.json`, `docs/images/street-medic-actions/animation-report.json`, `docs/images/longcoat-gunner-actions/README.md`, `docs/images/longcoat-gunner-actions/audit.json`, `docs/images/longcoat-gunner-actions/animation-report.json`, `docs/images/hooded-infiltrator-actions/README.md`, `docs/images/hooded-infiltrator-actions/audit.json`, `docs/images/hooded-infiltrator-actions/animation-report.json`, `docs/images/holo-hacker-actions/README.md`, `docs/images/holo-hacker-actions/audit.json`, `docs/images/holo-hacker-actions/animation-report.json`, `docs/images/blue-mohawk-scout-actions/README.md`, `docs/images/blue-mohawk-scout-actions/audit.json`, `docs/images/blue-mohawk-scout-actions/animation-report.json`, `docs/images/ronin-duelist-actions/README.md`, `docs/images/ronin-duelist-actions/audit.json`, `docs/images/ronin-duelist-actions/animation-report.json`, `docs/images/rail-sniper-actions/README.md`, `docs/images/rail-sniper-actions/audit.json`, `docs/images/rail-sniper-actions/animation-report.json`, `docs/images/violet-fixer-actions/README.md`, `docs/images/violet-fixer-actions/audit.json`, `docs/images/violet-fixer-actions/animation-report.json`, `docs/images/silver-pistol-actions/README.md`, `docs/images/silver-pistol-actions/audit.json`, `docs/images/silver-pistol-actions/animation-report.json`, `docs/images/armored-vanguard-actions/README.md`, `docs/images/armored-vanguard-actions/audit.json`, `docs/images/armored-vanguard-actions/animation-report.json`, `docs/images/chrome-medic-actions/README.md`, `docs/images/chrome-medic-actions/audit.json`, `docs/images/chrome-medic-actions/animation-report.json`, `docs/images/heavy-breacher-actions/README.md`, `docs/images/heavy-breacher-actions/audit.json`, `docs/images/heavy-breacher-actions/animation-report.json`, `docs/images/yellow-strike-actions/README.md`, `docs/images/yellow-strike-actions/audit.json`, `docs/images/yellow-strike-actions/animation-report.json`, `docs/images/red-enforcer-actions/README.md`, `docs/images/red-enforcer-actions/audit.json`, `docs/images/red-enforcer-actions/animation-report.json`, `docs/images/drone-handler-actions/README.md`, `docs/images/drone-handler-actions/audit.json`, `docs/images/drone-handler-actions/animation-report.json`, `docs/images/cyber-doc-actions/README.md`, `docs/images/cyber-doc-actions/audit.json`, `docs/images/cyber-doc-actions/animation-report.json`, `docs/images/twin-blade-actions/README.md`, `docs/images/twin-blade-actions/audit.json`, `docs/images/twin-blade-actions/animation-report.json`, `docs/images/veteran-inquisitor-actions/README.md`, `docs/images/veteran-inquisitor-actions/audit.json`, `docs/images/veteran-inquisitor-actions/animation-report.json`, `docs/images/dreadlock-rifle-actions/README.md`, `docs/images/dreadlock-rifle-actions/audit.json`, `docs/images/dreadlock-rifle-actions/animation-report.json`.
- Travail restant dans cette portée : 29 / 231 ensembles complets ; produire et vérifier les actions applicables des 202 autres entités. Prochaine référence éligible à déterminer par l’audit ordonné.

### TACTICAL-REVIEW — TODO — Validation artistique et fonctionnelle globale aux trois résolutions

- Fichiers : `godot/combat_missions_ui/tests`, `docs/images/combat-directional-animation`.
- Tests / contrôles réellement exécutés : Historique : 34 tests ciblés, 128 sélections de frames et déplacement à 4 PA ; portée partielle.
- Preuves : `docs/images/combat-directional-animation/README.md`, `docs/images/combat-directional-animation/validation-results.txt`.
- Travail restant dans cette portée : Exécuter les interactions et revues restant ouvertes ; ne pas extrapoler depuis cinq familles.

### GPU-BENCH — DONE — Performance et mémoire sur matériel joueur

- Fichiers : `godot/combat_missions_ui/tests/capture_combat_21.gd`, `tools/run_windows_gpu_benchmark.ps1`, `tests/test_windows_gpu_benchmark.py`.
- Tests / contrôles réellement exécutés : Benchmark natif Windows 1440p : 2400 frames animées sur NVIDIA RTX 5070 Ti; 180,53 FPS moyens ; p95 8,064 ms / 124,01 FPS ; pic mémoire statique Godot 441 MiB; 33 échantillons système : CPU total moyen 5,97 %, GPU moyen 9,82 %, pic GPU 20 %, pic VRAM processus observé 2730 MiB.
- Preuves : `docs/reports/windows_gpu_benchmark_system.json`.
- Travail restant dans cette portée : Aucun.
- Problème / raison : Portée : une machine Windows RTX 5070 Ti et un combat représentatif 1440p ; ne constitue pas une validation de configuration minimale.

### SCALE-CATALOGUE — DONE — Recalibrer PJ, PNJ, robots, armures et véhicules sur les décors des 122 cartes

- Fichiers : `godot/combat_missions_ui/scripts/unit_presentation.gd`, `godot/combat_missions_ui/scripts/visual_battlefield.gd`, `godot/combat_missions_ui/scripts/combat_mission_ui.gd`, `godot/combat_missions_ui/scripts/unit_visual.gd`, `assets/maps/*.walls.json`.
- Tests / contrôles réellement exécutés : Revue visuelle des 122 cartes et cinq profils d’environnement; Trois résolutions natives avec agents, ennemis, robots, power armors et véhicules ; clics et zoom vérifiés.
- Preuves : `docs/images/entity-scale-production-windows/README.md`, `docs/reports/entity_scale_review_windows.json`, `docs/reports/entity_scale_windows_tests.xml`.
- Travail restant dans cette portée : Aucun.

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

### UE5-03 — IN_PROGRESS — Démarrer Godot avec le jeu et réutiliser le même processus dès la première mission

- Fichiers : `game/combat/persistent_runtime.py`, `game/ui/application_window.py`, `main.py`, `godot/combat_missions_ui/scripts/persistent_runtime.gd`.
- Tests / contrôles réellement exécutés : Deux missions naturelles de campagne dans le même PID, initialisé avant la première mission (Linux natif); 84 tests ciblés PASS, 1 test natif désélectionné après un timeout sous charge ; 6 tests de cycle de vie/entrées PASS.
- Preuves : `docs/images/unified-experience/batch5/report.json`, `docs/reports/unified_persistent_runtime_tests.xml`, `docs/reports/unified_runtime_lifecycle_tests.xml`.
- Travail restant dans cette portée : Finaliser validation après extraction de GameWindow, réexécuter le test natif de routage isolément ; Windows et audio non vérifiés.

### UE5-04 — IN_PROGRESS — Conserver la transition visible jusqu’à la readiness native Windows

- Fichiers : `game/ui/screens/godot_combat_handoff_view.py`, `game/combat/win32_embed.py`.
- Tests / contrôles réellement exécutés : Deux missions naturelles de campagne dans le même PID, initialisé avant la première mission (Linux natif); 84 tests ciblés PASS, 1 test natif désélectionné après un timeout sous charge ; 6 tests de cycle de vie/entrées PASS.
- Preuves : `docs/images/unified-experience/batch5/report.json`, `docs/reports/unified_persistent_runtime_tests.xml`, `docs/reports/unified_runtime_lifecycle_tests.xml`.
- Travail restant dans cette portée : Finaliser validation après extraction de GameWindow, réexécuter le test natif de routage isolément ; Windows et audio non vérifiés.

### UE5-05 — IN_PROGRESS — Archiver les preuves natives, régressions et critères encore ouverts

- Fichiers : `docs/UNIFIED_EXPERIENCE_PROGRESS.md`.
- Tests / contrôles réellement exécutés : Deux missions naturelles de campagne dans le même PID, initialisé avant la première mission (Linux natif); 84 tests ciblés PASS, 1 test natif désélectionné après un timeout sous charge ; 6 tests de cycle de vie/entrées PASS.
- Preuves : `docs/images/unified-experience/batch5/report.json`, `docs/reports/unified_persistent_runtime_tests.xml`, `docs/reports/unified_runtime_lifecycle_tests.xml`.
- Travail restant dans cette portée : Finaliser validation après extraction de GameWindow, réexécuter le test natif de routage isolément ; Windows et audio non vérifiés.

### AUDIO-REPLACE-01 — DONE — Remplacer intégralement les anciens sons et musiques

- Fichiers : `assets/audio/sfx`, `assets/audio/music`, `game/audio`, `godot/combat_missions_ui/audio`, `godot/combat_missions_ui/scripts/audio_manager.gd`, `docs/audio/README.md`, `docs/gameplay/soundtrack.md`.
- Tests / contrôles réellement exécutés : python -m pytest -q tests/test_cc0_audio_routing.py tests/test_cc0_audio_import.py tests/test_music_catalog.py tests/test_music_continuity.py tests/test_unified_audio_transfer.py --junitxml=docs/reports/audio_replacement_tests.xml : 36 passed, 1 skipped, 4 subtests passed; Inventaire : 0 ancien fichier, 37 nouveaux WAV et 7 nouveaux MP3 dans assets/audio et dans le miroir Godot.
- Preuves : `tests/test_cc0_audio_routing.py`, `tests/test_music_catalog.py`.
- Travail restant dans cette portée : Aucun.
- Problème / raison : Portée technique validée ; écoute artistique humaine et partie complète non exécutées.

### AUDIO-NOBEEP-01 — DONE — Retirer les bips de substitution du combat

- Fichiers : `game/audio/overhaul_assets.py`, `godot/combat_missions_ui/scripts/audio_manager.gd`, `godot/combat_missions_ui/scripts/hud_controller.gd`, `godot/combat_missions_ui/scripts/combat_mission_ui.gd`, `tests/test_cc0_audio_routing.py`, `docs/backlog.md`.
- Tests / contrôles réellement exécutés : python -m pytest -q tests/test_cc0_audio_routing.py tests/test_music_catalog.py tests/test_music_continuity.py tests/test_unified_audio_transfer.py : 35 passed; Contrat HUD : NEXT, END TURN et RETREAT ne déclenchent plus ui_click; Contrat combat : l'auto-sélection à 0 AP ne déclenche plus ui_click.
- Preuves : `tests/test_cc0_audio_routing.py`.
- Travail restant dans cette portée : Aucun.
- Problème / raison : Validation d'écoute en partie à confirmer par l'utilisateur.

### PLAYER-UI-01 — DONE — Masquer les détails internes et les portées impossibles

- Fichiers : `game/ui/screens/godot_combat_handoff_view.py`, `game/ui/components/utilities/handoff.py`, `godot/combat_missions_ui/scripts/combat_mission_ui.gd`, `tests/test_godot_launch_routing.py`, `tests/test_godot_move_highlights.py`, `docs/backlog.md`.
- Tests / contrôles réellement exécutés : python -m pytest ciblé sur lancement, surbrillances, checkpoints et reprise : 47 passed, 9 skipped; aucun nom de moteur/runtime dans la copie joueur; AP=0 efface les surbrillances au lieu de forcer un budget minimal de 1; aucun bouton, raccourci ou chemin de mode de secours.
- Preuves : `tests/test_godot_launch_routing.py`, `tests/test_godot_move_highlights.py`.
- Travail restant dans cette portée : Aucun.
- Problème / raison : Tests natifs nécessitant un environnement graphique ignorés.

### PSI-OFFENSE-01 — DONE — Restaurer les attaques psi offensives

- Fichiers : `game/management/equipment.py`, `godot/combat_missions_ui/scripts/combat_mission_ui.gd`, `godot/combat_missions_ui/scripts/visual_hud.gd`, `godot/combat_missions_ui/tests/weapon_balance_regression.gd`, `tests/test_agent_equipment.py`, `tests/test_psi_combat_routing.py`, `docs/backlog.md`.
- Tests / contrôles réellement exécutés : 26 tests Python ciblés réussis; contrat natif weapon_balance ignoré car Godot indisponible; Mind Spike vérifié comme attaque PSI ciblée et Psi Focus comme soutien distinct.
- Preuves : `tests/test_agent_equipment.py`, `tests/test_psi_combat_routing.py`.
- Travail restant dans cette portée : Aucun.
- Problème / raison : Contrat natif Godot non exécuté car l'exécutable est indisponible.

### ENGLISH-UI-01 — DONE — Uniformiser toute la copie joueur en anglais

- Fichiers : `game/i18n/__init__.py`, `game/gamestate.py`, `game/mission_generation.py`, `game/missions/objective_branches.py`, `game/ui`, `godot/combat_missions_ui/scripts/combat_mission_ui.gd`, `godot/combat_missions_ui/scripts/visual_hud.gd`, `tests/test_english_player_ui.py`.
- Tests / contrôles réellement exécutés : suite ciblée Arcade/Godot, langue, missions, objectifs, lancement et psi : 44 réussis, 1 ignoré, 5 sous-tests réussis.
- Preuves : `tests/test_english_player_ui.py` ; anglais forcé pour les nouvelles campagnes et les anciennes sauvegardes ; contrats régionaux, objectifs, carte du monde, récupération, liaison tactique et HUD Godot traduits ; détails de moteur retirés des réglages joueur.
- Travail restant dans cette portée : validation visuelle humaine de tous les écrans non exécutée.
- Problème / raison : un test natif nécessitant un environnement graphique a été ignoré.

### GODOT-UI-FOCUS-01 — DONE — Traduire le HUD tactique résiduel et afficher le combat sans clic

- Fichiers : `godot/combat_missions_ui/scripts/visual_hud.gd`, `godot/combat_missions_ui/scripts/visual_battlefield.gd`, `game/combat/win32_embed.py`, `game/ui/screens/godot_combat_handoff_view.py`, `tests/test_english_player_ui.py`, `tests/test_godot_launch_routing.py`.
- Tests / contrôles réellement exécutés : 13 réussis, 1 ignoré ; scan de toutes les chaînes des scripts Godot ; contrat d'activation Windows.
- Preuves : les libellés visibles sont désormais `TURN`, `PLAYER PHASE`, `RETREAT`, `NEXT`, `END TURN`, `HP` et `AP` ; la fenêtre prête est montrée, remontée, activée et passée au premier plan sans dépendre d'un clic Arcade.
- Travail restant dans cette portée : validation native Windows du focus automatique en lançant une mission réelle.
- Problème / raison : le test cross-process natif est ignoré hors environnement graphique compatible.

### GODOT-ENGLISH-02 — DONE — Auditer toutes les chaînes Godot et retirer les dernières fuites françaises

- Fichiers : `godot/combat_missions_ui/scripts/visual_hud.gd`, `godot/combat_missions_ui/scripts/combat_mission_ui.gd`, contrats Godot natifs et `tests/test_english_player_ui.py`.
- Tests / contrôles réellement exécutés : 17 réussis, 1 ignoré ; scan des littéraux `.gd`, `.tscn`, `.tres`, `.cfg`, `.json` et `.txt` dans tout `godot`.
- Preuves : `COMBAT LOG`, `Combat log [L]` et `F9: classic interface` remplacent les dernières chaînes françaises visibles ; le pré-déploiement ne cite plus le moteur ; le diagnostic `WALL TEST` n'est plus affiché au joueur.
- Travail restant dans cette portée : validation visuelle humaine de tous les écrans non exécutée.
- Problème / raison : le parsing et le runtime natifs ont été validés ensuite dans GODOT-PARSE-01.

### GODOT-PARSE-01 — DONE — Réparer le blocage de chargement après traduction du HUD

- Fichiers : `godot/combat_missions_ui/scripts/visual_hud.gd`, `tests/test_english_player_ui.py`, `tests/test_persistent_combat_runtime.py`.
- Cause vérifiée : deux affectations de style avaient perdu leur indentation dans `_style_btn`, produisant `Parse Error: Could not preload resource script visual_hud.gd`; les sessions restaient en état `loading` sans statut combat.
- Tests / contrôles réellement exécutés : parseur natif Godot 4.6.3 sans erreur ; 16 tests réussis, 1 ignoré ; vrai runtime persistant démarré et réutilisé sur deux missions successives.
- Preuves : journal natif `runtime/godot_runtime/b5d660bd3ff2486da0d6b700fd16230e/godot.log`, `tests/test_persistent_combat_runtime.py`, `tests/test_english_player_ui.py`.
- Travail restant dans cette portée : relancer ou réparer la session déjà interrompue dans l'interface ouverte.
- Problème / raison : la session déjà en erreur exige une nouvelle tentative car son processus est arrêté.

## Problèmes et ressources en attente

- Le modèle procédural rejeté reste hors production.
- Résolu : SCALE-CATALOGUE validé sur 122 cartes, trois résolutions et cinq catégories d’environnement ; cette validation ne vaut pas finition artistique des décors.
- Résolu : X11 absent après reprise ; quatre tests natifs ont échoué faute d’affichage. Session Xorg rétablie, puis 55 tests ciblés réussis. Échec initial conservé dans work/roster-batch2/tests-display-failure.log.
- Après redémarrage X11 absent : quatre échecs initiaux d’environnement ; serveur rétabli et suite complète repassée (55 réussis).
- Résolu : profils d’échelle de production appliqués à 122 cartes — 0,015 urbain/wasteland, 0,020 intérieur/industrie — sources, collisions et règles inchangées.
- Passe SCALE-CATALOGUE demandée : proportions des unités et véhicules à revoir sur les 122 cartes ; 0 carte vérifiée pour ce nouveau critère.
- Inventaire SCALE : 122 cartes, 92 illustrations, cinq ratios génériques, 30 groupes partageant un PNG et aucune contradiction de ratio entre alias. Les références automobiles de deux intersections suggèrent des réductions, à confirmer ; la borne actuelle .015 limite les essais plus petits. Aucune taille de production modifiée.

## Prochaine action précise

- ANIM-TARGET-AUDIT — DONE. Le contrôle d’atlas accepte `--asset` pour vérifier uniquement l’unité en cours sans parcourir les cartes. La commande confirme que `enemy_commander` n’a pas encore de manifeste. Prochaine étape : produire ses planches, les importer et valider cette seule unité sur une carte.

- WINDOWS-PERFORMANCE — DONE pour les deux mesures ciblées. RTX 5070 Ti, 600 images par scène : Dust Road à 1440p, 185,5 FPS moyens (125,5 min), CPU global 5,14 %, GPU global 6,5 % et VRAM globale 2 925 Mio en pointe. Safehouse à 1080p, 252,3 FPS moyens. Le script affiche le résultat et conserve ses sorties temporaires dans work. Configuration minimale non mesurée.

- UNIFIED-NATIVE-AUDIO — IN_PROGRESS. Une victoire a été rejouée avec `--native-audio --godot-verbose`. Godot a ouvert la sortie WASAPI stéréo à 48 kHz (tampon annoncé de 10 ms). Le transfert Arcade → Godot, le débriefing et la fermeture ont réussi. Qualité audible et fondus encore à écouter.

- PERSISTENT-AUDIO-DISPOSAL — DONE. Godot arrête les flux lorsqu’une mission persistante est mise en veille ou remplacée, puis attend sa libération avant de publier le nouvel état. Seize tests audio et runtime passent. Écoute sur périphérique réel encore ouverte.

- UNIFIED-AUDIO-LIFETIME — DONE. Le journal détaillé du retour de victoire identifiait quatre objets de lecture WAV/MP3 encore actifs. Godot libère les flux après l’ACK avant de quitter ou de rendre la main au runtime. La victoire rejouée à 720p n’affiche plus la fuite. Seize tests audio et runtime passent. L’écoute réelle reste ouverte.

- UNIFIED-INTERNAL-RESIZE — DONE. Le pilote interne a réduit la fenêtre Godot de 1280 × 720 à 1120 × 630 puis rétabli sa taille. Surface rendue, dimensions de scène et état tactique préservé vérifiés, puis victoire et retour au QG. Alt+Tab, changement de DPI et focus système restent ouverts. Avertissement ObjectDB à la fermeture toujours présent.

- PACKAGE-UNIFIED-QA — DONE. L’exécutable Windows QA a joué les trois issues avec Godot embarqué à 1280 × 720 : victoire, défaite et retraite. Chaque parcours revient au QG après le débriefing, recharge sa sauvegarde et rejette une seconde application du résultat. Le pilote est réservé au build QA. DPI, focus, redimensionnement et écoute audio restent à valider.

- PACKAGE-TACTICAL-SMOKE — DONE. Exécutable reconstruit dans `work/windows-tactical-smoke/CyberCity2085`. Son smoke confirme le démarrage headless de la scène Godot embarquée et le rechargement. Suite : parcours graphique packagé via un pilote interne et validation des fenêtres.

- PACKAGE-TACTICAL-BOOT — DONE. Le smoke du package lance désormais sa scène Godot en headless et exige le marqueur de disponibilité. Huit tests de packaging réussis et démarrage vérifié avec les fichiers et le binaire du package local. Reconstruire pour intégrer ce contrôle à l’exécutable. Le parcours graphique complet reste ouvert.

- RELEASE-SUITE — DONE. Suite Windows en ordre normal : 1 144 réussis, 35 ignorés, 12 sous-tests réussis. Package reconstruit dans `work/windows-release-regression/CyberCity2085`. Le smoke de l’exécutable confirme Godot 4.6.3 embarqué et l’aller-retour de sauvegarde. Le parcours graphique depuis ce package reste à vérifier via un pilote du jeu.

- RELEASE-SUITE — IN_PROGRESS. La relance normale s’est arrêtée au premier échec après 830 réussites : les paramètres récupéraient une fixture Arcade d’un autre module. Fixture isolée pendant le test. Lot menu, paramètres et QG : 35 réussis, 1 ignoré, 5 sous-tests réussis dans l’ordre inversé. Relancer la suite normale.

- RELEASE-COMBAT-REGRESSION — DONE. Les tests utilisent un fichier de résultat présent, vérifient les familles de cartes et le rapport d’échelle, et construisent le tableau avant de bloquer une mission. 47 réussis. Relancer la suite de release pour identifier les écarts d’intégration restants.

- RELEASE-CONTRACT — DONE. Plafond historique retiré du plan. Le test de release vérifie la checklist sans exiger la fermeture des travaux encore ouverts. Les tests de choix narratifs vérifient les libellés anglais et les marqueurs.

- MAP-ART-INVENTORY — DONE. Le test compare désormais les déclarations du catalogue au manifeste de la revue Windows déjà archivée (122 cartes, 21 planches). Cinq tests réussis, deux contrôles natifs ignorés. Aucun nouveau rendu effectué. Poursuivre le tri des régressions de release.

- MAP-8K-INTEGRITY — DONE. Git matérialise les relevés JSON en CRLF sous Windows. Le contrôle normalise les fins de ligne avant le SHA du relevé. Deux tests réussis, dont les 122 entrées du manifeste. PNG, empreintes et géométrie conservés. Prochaine action : examiner le contrat de l’inventaire artistique.

- RELEASE-LAUNCH-REGRESSION — DONE. Les tests vérifient le message de déploiement et l’absence du raccourci Arcade hérité. Le test de parcours statique vérifie l’intitulé de la section des gains. Onze tests réussis. Prochain lot : comparer les empreintes de cartes aux sources et au manifeste.

- RELEASE-UI-REGRESSION — IN_PROGRESS. Fixtures Arcade du QG isolées pendant les tests. Le test Continue exclut les checkpoints externes et utilise des dates distinctes sous Windows. Les paramètres vérifient l’absence des réglages moteur. Lot ciblé : 35 tests réussis, 1 ignoré, 5 sous-tests réussis. Revoir ensuite les échecs de lancement de mission et l’inventaire des cartes.

- RELEASE-REGRESSION — IN_PROGRESS. Suite complète Windows : 1117 réussis, 32 échecs, 35 ignorés. Corrigé les attentes périmées sur l’anglais et les séparateurs de chemins dans trois suites (28 réussis, 1 ignoré). Prochain lot : fixtures Arcade du QG, puis tri des écarts de carte et de lancement avant de reconstruire le package.

- CAMPAIGN-FINALE — DONE. Seven Minutes to Dawn gagnée sous Windows à 720p avec le Titan et le K-9 achetés puis affectés via l’Asset Bay. L’écran de fin s’est ouvert et le rechargement confirme 15 missions d’histoire sur cinq actes, fin Dawn Without Masters (jour 80). Sauvegarde : `work/campaign-story-finale-dual-support/victory/campaign.json`. Le parcours depuis l’exécutable packagé reste à vérifier.

- FINALE-PREPARATION — IN_PROGRESS. Deux essais de Seven Minutes to Dawn avec la priorité cible se terminent au tour 25, même après cinq jours de permission payée et soins. Le stress baisse mais six ennemis seulement sont neutralisés et aucun soutien n’est déployé. Reprendre la sauvegarde Pharmacorp et préparer un soutien via l’Asset Bay avant le prochain essai.

- ASSASSINATION — IN_PROGRESS. Godot choisit désormais la cible par priorité de rôle comme Arcade et valide l’objectif à sa neutralisation. Le test Godot headless vérifie qu’un garde peut survivre, contrairement à kill_all. La finale avec priorité de tir seule est restée une défaite. Rejouer avec le pilote qui se rapproche aussi de la cible et vérifier l’épilogue.

- CAMPAIGN-FINALE — IN_PROGRESS. Warsaw Citadel Raid et The Pharmacorp File gagnées sous Windows à 720p. Seven Minutes to Dawn a produit deux défaites au tour 25, avec sept ennemis sur onze abattus. Le générateur Godot traite actuellement assassination comme kill_all, alors qu’Arcade désigne une cible. Prochaine action : rétablir la parité sur cet objectif, puis repartir de `work/campaign-story-act5-expose/victory/campaign.json`.

- CAMPAIGN-ACT4 — DONE. The Names Below puis les trois missions de l’acte 4 gagnées sous Windows à 720p sur la même campagne. Douze missions d’histoire terminées, acte 5 débloqué. Reprendre `work/campaign-story-act4-voices/victory/campaign.json` pour Warsaw Citadel Raid (`sm_act5_citadel`).

- CAMPAIGN-ACT3 — IN_PROGRESS. Memory Subject Alpha et New Delhi Grid 12 gagnées sous Windows à 720p. New Delhi a nécessité un nouvel essai avec recrutement payé au QG après la défaite de l’escouade à trois. Reprendre `work/campaign-story-act3-delhi-recruit/victory/campaign.json` pour The Names Below (`sm_act3_names_below`).

- CAMPAIGN-ACT2 — DONE. Tide Estimates et Breakwater Nine gagnées à 720p sous Windows avec la sauvegarde de Drone 7-Whiskey et le système de soins. Six missions d’histoire terminées, acte 3 débloqué. Reprendre `work/campaign-story-act2-breakwater/victory/campaign.json` pour `sm_act3_perf` (Memory Subject Alpha).

- CAMPAIGN-ACT2 — IN_PROGRESS. The Vistula Witnesses a débloqué l’acte 2. Recover Drone 7-Whiskey a d’abord éliminé l’escouade sous stress, puis a été gagnée après trois séances de thérapie de groupe et un passage à l’hôpital via le système de campagne. Reprendre `work/campaign-story-act2-drone-recovered/victory/campaign.json`.

- GRID-7 — DONE. Le pilote confirme l’alerte de stress par l’action normale de la carte pour la mission sélectionnée. Badlands Survey gagnée sur la même campagne, à 720p sous Windows. Reprendre `work/campaign-story-grid7/victory/campaign.json` pour The Vistula Witnesses.

- IVORY-STATIC — DONE. Depuis le checkpoint du jour 7, l’hôpital de campagne a soigné quatre agents pour huit crédits et un jour. Le déploiement a ensuite utilisé les agents éligibles et remporté Ivory Static sous Windows à 720p. Promotions, retour au QG et rechargement vérifiés. Reprendre `work/campaign-story-ivory-hospital/victory/campaign.json` et sélectionner la prochaine mission d’histoire.

- IVORY-STATIC — IN_PROGRESS. L’essai qui privilégie le déplacement vers l’objectif a perdu au tour 10 sans interaction. Le banc permet de comparer cette stratégie avec `--objective-first`. Reprendre le checkpoint du jour 7 et vérifier la composition du déploiement, les achats disponibles et l’accès à l’objectif. Trois tests du pilote passent.

- CAMPAIGN-STORY — IN_PROGRESS. Deux victoires supplémentaires dans la même sauvegarde : Starver Depot puis Irradiated Signal. Depuis le checkpoint `work/campaign-day4-native/victory/campaign.json` (jour 7), Ivory Static a éliminé l’escouade au tour 15 après quatre ennemis abattus et sans progrès d’objectif. Repartir de ce checkpoint, revoir le déploiement et la priorité d’objectif du pilote, puis rejouer la mission d’histoire.

- CAMPAIGN-CONTINUATION — IN_PROGRESS. `--campaign-save` recharge la campagne précédente. `samurai_archive_d2_s3` gagnée sous Windows à 720p depuis la sauvegarde du jour 1, avec retour au QG et rechargement. Le banc vérifie les promotions d’après les niveaux réellement gagnés et accepte l’écran de finale. Reprendre `work/campaign-continuation-native-720/victory/campaign.json` pour le prochain acte.

- CAMPAIGN-NATIVE — IN_PROGRESS. Banc de campagne corrigé pour Windows (liens de répertoire, nettoyage et taille de fenêtre). Première mission du tableau réel `data_theft_d1_s2` jouée jusqu’à la victoire, avec parcours QG → carte → briefing → Godot → débriefing → QG et rechargement à 720p. 19 tests ciblés réussis. Reste à enchaîner les actes jusqu’à la finale avec le même état de campagne.

- UNIFIED-RESULT-POLL — DONE. Régression déterministe : un résultat publié pendant le contrôle de fin de processus est lu au cycle suivant. Suite ciblée : 29 réussis.

- UNIFIED-REAL-RECOVERY — DONE. Victoire jouée après reprise en phase joueur puis en phase ennemie sous Windows à 720p. Le second scénario a révélé une course entre la publication du résultat et sa lecture. Le correctif a passé le scénario et les tests ciblés (54 réussis, 8 ignorés). Suite : vérifier le parcours depuis le package Arcade et les transitions de fenêtre sans contrôle du bureau.

- UNIFIED-RECOVERY — IN_PROGRESS. Sous Windows, à 1280 × 720, les scénarios de reprise tactique restaurent les phases joueur et ennemi et remplacent l’ancien processus. Sur une victoire jouée, l’arrêt de Godot au retour puis la reprise du débriefing ont préservé la promotion et bloqué la double attribution. La perte d’accusé de réception a également été testée séparément. Reste à interrompre une mission réelle pendant un tour.

- UNIFIED-RESOLUTION — DONE. Le banc écrasait son propre 720p avec une seconde option héritée d’Arcade. Une seule option est désormais transmise et la taille de capture est vérifiée sur Windows. Victoire réelle rejouée : 1280 × 720 demandé et observé. DPI, focus et redimensionnement restent ouverts.

- UNIFIED-EXPERIENCE — IN_PROGRESS. Le banc source `python -m tools.check_unified_return --real-mission` a joué victoire, défaite et retraite sous Windows avec le binaire Godot du package. Débriefing, rechargement et protection contre la double attribution vérifiés sur les trois cas. Fenêtre demandée en 720p, observée en 1080p. Parcours depuis l'exécutable Arcade packagé et vérifications DPI/focus encore ouverts. Utiliser les pilotes de test du jeu sans contrôle Windows.

- PACKAGE-WINDOWS — IN_PROGRESS. Package reconstruit dans `work/windows-godot-smoke/CyberCity2085`. Smoke Windows réussi avec Godot 4.6.3 embarqué et aller-retour de sauvegarde. La fenêtre native CyberCity 2085 s’ouvre depuis le package. Jouer ensuite le parcours Arcade → Godot → débriefing sur une campagne isolée.

ANIM-COMPLETE — IN_PROGRESS. Samurai livré : 112 images, 32 sélections natives et capture Windows ciblée sur Safehouse. 55 / 233 ensembles complets. Enemy Commander DONE: 128 frames, seven applicable actions, clean focused audit, 32 native movement frame selections and all seven poses inspected on Safehouse. Enemy sniper DONE: 128 frames, clean focused audit, 32 native movement selections and seven actions inspected on Safehouse. Enemy heavy DONE: 128 frames, clean focused audit, 32 native movement selections and seven actions inspected on Safehouse. Enemy elite DONE: 128 frames, clean focused audit, 32 native movement selections and seven actions inspected on Safehouse. Enemy psi DONE: 144 frames, clean focused audit, 32 native movement selections and eight actions inspected on Safehouse. Corp 37 grunt DONE: 128 frames, clean focused audit, 32 native movement selections and seven actions inspected on Safehouse via faction routing. Corp 37 robot grunt DONE: 128 frames, clean focused audit, 32 native movement selections and seven actions inspected on Safehouse via faction routing. Corp 37 robot heavy DONE: 128 frames, clean focused audit, 32 native movement selections and seven actions inspected on Safehouse via faction routing. Corp 37 robot elite DONE: 128 frames, clean focused audit, 32 native movement selections and seven actions inspected on Safehouse via faction routing. Corp 37 robot commander DONE: 128 frames, clean focused audit, 32 native movement selections and seven actions inspected on Safehouse via faction routing. Corp 37 power-armored heavy DONE: 128 frames, clean focused audit, 32 native movement selections and seven actions inspected on Safehouse via faction routing. Corp 37 power-armored elite DONE: 128 frames, clean focused audit, 32 native movement selections and seven actions inspected on Safehouse via faction routing. Corp 37 power-armored commander DONE: 128 frames, clean focused audit, 32 native movement selections and seven actions inspected on Safehouse via faction routing. Corp 37 human heavy DONE: 128 frames, clean focused audit, 32 native movement selections and seven actions inspected on Safehouse via faction routing. Corp 37 human elite DONE: 128 frames, clean focused audit, 32 native movement selections and seven actions inspected on Safehouse via faction routing. Corp 37 human commander DONE: 128 frames, clean focused audit, 32 native movement selections and seven actions inspected on Safehouse via faction routing. Corp Samurai grunt DONE: 128 frames, clean focused audit, 32 native movement selections and seven actions inspected on Safehouse via faction routing. Corp Samurai heavy DONE: 128 frames, clean focused audit, 32 native movement selections and seven actions inspected on Safehouse via faction routing. Corp Samurai elite DONE: 128 frames, clean focused audit, 32 native movement selections and seven actions inspected on Safehouse via faction routing. Corp Samurai commander DONE: 128 frames, clean focused audit, 32 native movement selections and seven actions inspected on Safehouse via faction routing. Corp Samurai robot grunt DONE: 128 frames, focused audit, 32 native movement selections and seven actions inspected on Safehouse via faction routing. Captures in temporary storage. Corp Samurai robot heavy DONE: 128 frames, focused audit, 32 native movement selections and seven actions inspected on Safehouse. Corp Samurai robot elite DONE: 128 frames, focused audit, 32 native movement selections and seven actions inspected on Safehouse. Corp Samurai robot commander DONE: 128 frames, rear gait corrected, focused audit, 32 native movement selections and seven actions inspected on Safehouse. Corp Samurai power-armored grunt DONE: 128 frames, clean focused audit, 32 native movement selections and seven actions inspected on Safehouse. Corp Samurai power-armored heavy IN_PROGRESS: 32 idle and fire frames including separate corrected SW and NE fire. Native Godot Windows target capture passed on Safehouse. Next: walk, cover, melee, hit and death.

Le nombre de tâches DONE et les critères ouverts sont calculés dans [le bilan global](reports/combat_visual_acceptance.md). Un lot validé ne termine pas le chantier.
