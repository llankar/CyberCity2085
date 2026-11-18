# Unified Experience 1.0 — progression persistante

**CHANTIER GLOBAL INCOMPLET.** Python possède l’état persistant. Godot n’écrit aucune sauvegarde de campagne. Les travaux Combat Visual / SCALE sont conservés, mais ne sont pas l’objet des validations ci-dessous.

## Bilan vérifié

9 tâches DONE / 10 tâches enregistrées pour les deux premiers lots ; UE2-04 reste BLOCKED faute de Windows graphique. Ces dix tâches ne constituent pas tout le périmètre d’acceptation. **85 tests ciblés distincts PASS, 0 FAIL, 0 skipped** dans [le rapport agrégé](reports/unified_targeted_tests.xml). Les exécutions du lot 2 couvrent 65 cas, plus 19 régressions de lancement partiellement communes ; le rapport déduplique aussi le lot 1.

Cinq scénarios graphiques du lot 2 : trois issues avec interruption et récupération en 1280×720 ; victoire et reprise du débriefing en 1920×1080 et 2560×1440. Les issues sont forcées par la fixture : cela vérifie les transitions et conséquences, pas une partie complète avec IA. Trois autres parcours natifs normaux ont aussi été rejoués en 720p.

Cartes artistiquement finalisées / animations complètes : aucune validation supplémentaire dans ce chantier. Les anciens décomptes restent dans CODEX_PROGRESS et COMBAT_VISUAL_ACCEPTANCE ; charger la scène de test ne finalise aucune carte.

## Critères d’acceptation et limites

| Critère | État réel et preuve |
|---|---|
| HQ → World Map → Briefing → Godot → Results consultables → confirmation → Debrief → Promotions → HQ | PASS sur fixtures natives Linux, NOT VERIFIED sur missions intégralement jouées et Windows |
| Résolveur campagne commun, validation avant mutation, absence de double récompense | PASS dans les tests ciblés : ressources, aftermath, blessure/mort, soutiens, XP et sauvegarde/rechargement |
| Résultat préparé séparé de confirmé ; ACK avant sortie | PASS tests Godot et parcours natifs ; Godot ne ferme plus dès l’affichage des résultats |
| Checkpoint avant/après et reprise du débriefing sans réapplication | PASS tests disque plein, rechargement, corruption, doublons et captures réelles |
| Session UUID et protocole versionné ; readiness, début, résultat et ACK | PASS sur le flux normal de campagne ; l’ancienne API bloquante reste à harmoniser |
| Crash avant confirmation | PASS récupération explicite du résultat préparé ; aucun résultat préparé appliqué automatiquement |
| Crash pendant un tour sans résultat préparé | INCOMPLET : checkpoint avant combat disponible, relance explicite ; le tour courant n’est pas sauvegardé |
| Fenêtre Windows : focus, Alt+Tab, restauration, DPI et moniteurs | BLOCKED / NOT VERIFIED : Linux uniquement ; code d’ownership, géométrie client et lancement sans bordures ajouté |
| Audio sans doublons et transition sans bureau visible | NOT VERIFIED auditivement et sous Windows ; lecture des bookmarks et reprise existantes conservées, audio Dummy dans les preuves |
| Préparation Godot en amont et performances de transition | TODO : pas de processus préchauffé |

## Lot 1 — retour de combat

- DONE UE1-01 : audit et contrat isolé par session.
- DONE UE1-02 : préparation, consultation puis confirmation et ACK Godot.
- DONE UE1-03 : résolution de campagne commune sur copie transactionnelle ; suppression du raccourci fonds/XP.
- DONE UE1-04 : débriefing puis promotions puis HQ ; statistiques individuelles manquantes indiquées indisponibles.
- DONE UE1-05 : 67 tests distincts et trois parcours natifs Linux ; [preuves et limites](images/unified-experience/batch1/README.md).

Point Git : `a1fa0d9`.

## Lot 2 — récupération durable et cycle de vie

- DONE UE2-01 : `checkpoints.py` écrit avant lancement et avant validation finale de la transaction. Échec d’écriture après résolution : campagne en mémoire inchangée. La sauvegarde manuelle n’est pas écrasée.
- DONE UE2-02 : `return_snapshot.py` sépare présentation et résolution. CONTINUE charge le checkpoint récent ; débriefing et promotions reprennent sans attribuer de récompenses. La fermeture du dernier écran enregistre le marqueur de présentation terminée.
- DONE UE2-03 : `session_mailbox.gd` centralise les écritures atomiques ; démarrage prêt après une frame, résultat préparé/confirmé, identités contrôlées. Délai d’initialisation de 90 secondes, aucune limite de durée du combat. Résultat corrompu signalé sans mutation.
- BLOCKED UE2-04 : `win32_embed.py` utilise des handles de taille correcte, une fenêtre possédée plutôt que SetParent, suivi du rectangle client et réduction/restauration. Lancement avec position/résolution et sans bordures avant apparition de la fenêtre. **Implémenté, pas validé sous Windows.**
- DONE UE2-05 : tests de récupération et vrais processus Godot tués avant confirmation ; reprise depuis checkpoint après résolution ; captures vérifiées aux trois résolutions. Correction révélée par les tests : mémoriser les PV maximum à l’extraction avant une promotion.

Fichiers et tests détaillés : [registre](CODEX_PROGRESS.md). Captures : [lot 2](images/unified-experience/batch2/README.md).

## Reproduire les validations

Créer une vraie fenêtre Arcade invisible avant pytest pour les anciens tests d’aftermath qui dépendent d’un contexte graphique :

```python
import arcade, pytest
window = arcade.Window(640, 480, visible=False)
try:
    code = pytest.main(['-q', 'tests/test_unified_checkpoints.py',
        'tests/test_unified_mission_resolution.py', 'tests/test_unified_result_lifecycle.py',
        'tests/test_godot_combat_bridge.py', 'tests/test_battle_debrief_view.py',
        'tests/test_title_screen_ui.py', 'tests/test_agent_aftermath.py'])
finally:
    window.close()
raise SystemExit(code)
```

Sous Linux de validation : `DISPLAY=:107 ALSOFT_DRIVERS=null`. Commandes et dimensions des captures dans le README du lot 2. Aucun test headless ne valide les transitions de fenêtre Win32.

## Prochaine action précise

Préparer un instantané tactique versionné du combat en cours, lié à la session, permettant de reprendre avant l’existence d’un résultat préparé. Examiner les états réellement nécessaires (unités, tours/PA, objectifs, IA et événements) avant toute sérialisation, sans changer les règles. Ensuite vérifier la continuité audio et harmoniser l’ancienne API bloquante. Le contrôle graphique Windows reste bloqué par l’environnement disponible.

## Points encore ouverts

Reprise exacte d’un tour interrompu, sessions récupérées alors qu’un ancien processus Godot vit encore, audio réellement écouté, préchauffage, parcours d’une mission jouée jusqu’à sa vraie condition de fin, commande de retraite réelle (la fixture seule produit ce résultat), tests Windows complets. Ne pas transformer ces absences de preuves en PASS.
