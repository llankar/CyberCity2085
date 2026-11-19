# Unified Experience 1.0 — progression persistante

**CHANTIER GLOBAL INCOMPLET.** Python possède l’état persistant. Godot n’écrit aucune sauvegarde de campagne. Les travaux Combat Visual / SCALE sont conservés, mais ne sont pas l’objet des validations ci-dessous.

## Bilan vérifié

17 tâches DONE / 18 tâches enregistrées pour les quatre premiers lots ; UE2-04 reste BLOCKED faute de Windows graphique. Ces dix-huit tâches ne constituent pas tout le périmètre d’acceptation. **127 tests ciblés distincts PASS, 0 FAIL, 0 skipped** dans [le rapport agrégé](reports/unified_targeted_tests.xml). Les exécutions du lot 2 couvrent 65 cas, plus 19 régressions de lancement partiellement communes ; le rapport déduplique aussi le lot 1, les 57 cas du lot audio et les 104 cas du lot 4.

Un parcours natif supplémentaire valide la propriété musicale dans le lot 3 (audio muet, aucune validation auditive). Le lot 4 ajoute la reprise tactique en 720p/1080p/1440p et le renvoi d’ACK après résolution sauvegardée. Cinq scénarios graphiques du lot 2 : trois issues avec interruption et récupération en 1280×720 ; victoire et reprise du débriefing en 1920×1080 et 2560×1440. Les issues sont forcées par la fixture : cela vérifie les transitions et conséquences, pas une partie complète avec IA. Trois autres parcours natifs normaux ont aussi été rejoués en 720p.

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
| Crash pendant un tour sans résultat préparé | PASS dans la portée testée : reprise au dernier état logique écrit, PA/PV/objectifs/postures/caméra/projection préservés ; aucune promesse sur les jets futurs ni les effets en cours |
| Fenêtre Windows : focus, Alt+Tab, restauration, DPI et moniteurs | IN PROGRESS : Alt+Tab, réduction et restauration visuellement PASS ; redimensionnement et DPI multi-écrans restent NOT VERIFIED |
| Audio sans doublons et transition sans bureau visible | NOT VERIFIED auditivement et sous Windows ; lecture des bookmarks et reprise existantes conservées, audio Dummy dans les preuves |
| Préparation Godot en amont et performances de transition | DONE dans la portée mesurée : première frame/readiness froide 2,109–3,625 s ; préchauffage rejeté pour l’instant, musique Arcade continue |

## Lot 1 — retour de combat

- DONE UE1-01 : audit et contrat isolé par session.
- DONE UE1-02 : préparation, consultation puis confirmation et ACK Godot.
- DONE UE1-03 : résolution de campagne commune sur copie transactionnelle ; suppression du raccourci fonds/XP.
- DONE UE1-04 : débriefing puis promotions puis HQ ; statistiques individuelles manquantes indiquées indisponibles.
- DONE UE1-05 : 67 tests distincts et trois parcours natifs Linux ; [preuves et limites](images/unified-experience/batch1/README.md).

Points Git : lot 1 `a1fa0d9` ; lot 2 `5bb5632`.

## Lot 2 — récupération durable et cycle de vie

- DONE UE2-01 : `checkpoints.py` écrit avant lancement et avant validation finale de la transaction. Échec d’écriture après résolution : campagne en mémoire inchangée. La sauvegarde manuelle n’est pas écrasée.
- DONE UE2-02 : `return_snapshot.py` sépare présentation et résolution. CONTINUE charge le checkpoint récent ; débriefing et promotions reprennent sans attribuer de récompenses. La fermeture du dernier écran enregistre le marqueur de présentation terminée.
- DONE UE2-03 : `session_mailbox.gd` centralise les écritures atomiques ; démarrage prêt après une frame, résultat préparé/confirmé, identités contrôlées. Délai d’initialisation de 90 secondes, aucune limite de durée du combat. Résultat corrompu signalé sans mutation.
- IN PROGRESS UE2-04 : `win32_embed.py` utilise des handles de taille correcte, une fenêtre possédée plutôt que SetParent, suivi du rectangle client et réduction/restauration. Un premier parcours natif Windows est réussi ; Alt+Tab, DPI, restauration et multi-écrans restent à vérifier.
- DONE UE2-05 : tests de récupération et vrais processus Godot tués avant confirmation ; reprise depuis checkpoint après résolution ; captures vérifiées aux trois résolutions. Correction révélée par les tests : mémoriser les PV maximum à l’extraction avant une promotion.

Fichiers et tests détaillés : [registre](CODEX_PROGRESS.md). Captures : [lot 2](images/unified-experience/batch2/README.md).

## Lot 3 — continuité musicale pendant le chargement

- DONE UE3-01 : Arcade conserve sa musique jusqu’à readiness ; un message de transfert versionné porte le bookmark actualisé. Godot ne lance pas de musique avant de recevoir cette autorisation.
- DONE UE3-02 : erreur d’écriture ou fermeture restitue la propriété à Arcade ; les transitions d’interface gardent leur pause/reprise.
- DONE UE3-03 : 57 tests ciblés dont quatre nouveaux cas de propriété musicale ; parcours natif vérifiant l’absence de propriété avant transfert et sa réception, puis débriefing/promotions/HQ. [Preuves et limites](images/unified-experience/batch3/README.md).

Le préchauffage et les fondus audibles restent ouverts. Un avertissement ObjectDB persiste à la fermeture de la fixture Godot ; aucune absence générale de fuite n’est affirmée.

## Lot 4 — reprise tactique et instances interrompues

- DONE UE4-01 : contrat d’instantané runtime distinct des sauvegardes de campagne. [Format et limites](UNIFIED_TACTICAL_SNAPSHOT.md).
- DONE UE4-02 : écriture atomique différée, après retour de la logique d’action ; les écritures identiques sont évitées.
- DONE UE4-03 : validation Python et Godot avant restauration ; carte/déploiement liés par empreinte, positions/PV/PA/tours/postures/objectifs/caméra/projection/mode graphique et orientations enregistrées conservés. Les cartes, collisions et règles ne sont pas importées depuis l’instantané.
- DONE UE4-04 : bouton REPRENDRE [S], nouvel UUID, annulation identifiée de l’ancienne instance sans PID arbitraire. Une copie de l’instantané existe avant le lancement de remplacement ; échec de lancement = source toujours récupérable. Un résultat disponible exige sa confirmation et ne peut pas être contourné par S. Le nouvel hôte renvoie aussi un ACK pour un résultat déjà appliqué.
- DONE UE4-05 : **104 cas ciblés PASS**, dont 34 tests de récupération ; vrais roundtrips Godot phase joueur/ennemi, agents/robot/armure, clic viewport → grille y compris après changement de résolution, projection isométrique et mode legacy, corruption refusée sans combat neuf silencieux. Quatre scénarios de reprise tactique natifs (joueur 720p/1080p, phase ennemie avec ancien processus vivant 720p/1440p), plus interruption avant ACK en 720p. [Captures et rapports](images/unified-experience/batch4/README.md).

Problèmes rencontrés et corrigés dans la validation : les entiers du JSON Godot sont relus comme flottants, ce qui rendait une comparaison stricte de tableaux fausse ; l’oracle compare maintenant les états normalisés. Le test de phase ennemie contrôle aussi un vrai tour IA après restauration : l’instantané final est donc logiquement passé au tour joueur. Le premier rapport d’échecs est conservé (`reports/unified_tactical_roundtrip_initial_failures.xml`) ; il n’est pas compté dans les validations finales PASS. La persistance de la projection, du mode legacy et des orientations a été ajoutée après examen de l’état visuel.

## Reproduire les validations

Créer une vraie fenêtre Arcade invisible avant pytest pour les anciens tests d’aftermath qui dépendent d’un contexte graphique :

```python
import arcade, pytest
window = arcade.Window(640, 480, visible=False)
try:
    code = pytest.main(['-q', 'tests/test_unified_checkpoints.py',
        'tests/test_unified_tactical_recovery.py', 'tests/test_unified_audio_transfer.py',
        'tests/test_unified_mission_resolution.py', 'tests/test_unified_result_lifecycle.py',
        'tests/test_godot_combat_bridge.py', 'tests/test_battle_debrief_view.py',
        'tests/test_title_screen_ui.py', 'tests/test_agent_aftermath.py'])
finally:
    window.close()
raise SystemExit(code)
```

Sous Linux de validation : `DISPLAY=:107 ALSOFT_DRIVERS=null`. Commandes et dimensions des captures dans le README du lot 2. Aucun test headless ne valide les transitions de fenêtre Win32.

## Prochaine action précise

La première mission native non forcée est vérifiée sous Windows : objectif accompli par les actions normales, parcours HQ → carte → briefing → Godot → débriefing → promotions → HQ, sauvegarde/rechargement et application unique. [Preuves et limites](images/unified-experience/windows-real-mission/README.md). Le résultat prêt est observé après 5,828 s, mais cette durée inclut dix tours de combat et ne constitue pas une mesure isolée du chargement.

Les trois issues réelles sont maintenant vérifiées sous Windows avec [captures et rapports](images/unified-experience/windows-three-real-outcomes/README.md). Alt+Tab, réduction et restauration sont visuellement vérifiés ; redimensionnement et DPI multi-écrans restent ouverts. Le chargement froid mesuré ne justifie pas un préchauffage tant que la musique Arcade assure la continuité.

Prochaine action : valider redimensionnement/DPI multi-écrans et écoute audio réelle, puis fermer les autres chantiers globaux sans extrapoler depuis cette intégration.

## Points encore ouverts

Redimensionnement, DPI et moniteurs Windows ; écoute/fondus audio ; ancienne API bloquante hors parcours campagne ; avertissement ObjectDB à la fermeture. Les futurs jets du RNG global et les effets en cours ne sont pas sérialisés. Une interruption revient au dernier état logique complet, pas à une instruction arbitraire de la boucle IA. Ne pas transformer ces limites en PASS.

## Lot 5 en cours — moteur résident dès l’ouverture du jeu

Instruction utilisateur prioritaire : aucun lancement de Godot à l’entrée en mission, même la première. `GameWindow` initialise le runtime avant le menu titre ; les missions sont des scènes chargées dans ce processus déjà vivant. Le résultat confirmé parque la scène au lieu de quitter le moteur. Fermeture de l’application : arrêt du processus possédé. Une panne nécessite une réparation explicite, pas un lancement tardif silencieux.

Preuve Linux native : `docs/images/unified-experience/batch5/report.json`, un seul lancement, PID identique pour deux missions naturelles (`data_theft_d1_s2`, puis `road_relay_d2_s0`), débriefing/QG entre les deux. Préchargement de la scène et des sprites communs, cache de textures borné à 128 Mio ; les données propres aux cartes continuent de charger. Une victoire et une défaite naturelles ont aussi été vérifiées séparément. La victoire Godot par élimination peut survenir sans terminal piraté : cette règle existante est conservée, aucun objectif accompli n’est inventé.

84 tests ciblés réussis, un test de routage graphique désélectionné après timeout sous charge ; 6 tests supplémentaires réussis. Le refactoring final vers la véritable classe `GameWindow` a une nouvelle preuve native en cours (`/tmp/persistent-app-window.log`). Ne pas déclarer le lot terminé avant examen de cette preuve et régression isolée du routage. Windows/Alt+Tab/DPI et écoute audio restent NON VÉRIFIÉS. Les mesures Linux sous rendu logiciel et forte charge ne constituent pas une promesse de temps de chargement.

Prochaine action : examiner `work/persistent-runtime-app-window/report.json`, tester la fermeture réelle de `GameWindow`, puis finaliser les tests et le bilan. CHANTIER GLOBAL INCOMPLET.

Le retour de retraite conserve le nom de campagne transmis au déploiement. La récupération accepte également les anciens noms d’affichage non ambigus, y compris après normalisation du nom au rechargement du checkpoint. La validation du déploiement et la protection contre les doublons restent actives. Suites de résolution et de checkpoints : 40 tests réussis.

Le débriefing s’ouvre automatiquement dès qu’un résultat valide est disponible. Après une interruption ou un rechargement, le jeu récupère une fois le résultat enregistré. Un combat en cours laisse le joueur consulter ses résultats dans Godot avant de confirmer le retour. Sans résultat exploitable, les commandes de secours restent disponibles. Vérification ciblée : 46 tests réussis, dont reprise automatique d’une retraite préparée et confirmée.

Le débriefing présente le résultat de l’objectif en tête, puis les gains, le district, les factions et la progression dans des rubriques distinctes. Les renseignements portent leur titre et les identifiants de missions sont remplacés par un libellé lisible. Les pages du rapport, des agents, des promotions et de la fin de campagne utilisent des libellés anglais. Capture : [débriefing Linux](images/unified-experience/debrief-polish/debrief.webp). Vérification de mise en page en 720p, 1080p et 1440p.

Au démarrage, le projet Godot désactive le logo de lancement. Sous Windows, le moteur résident démarre avec une fenêtre initiale de 1 × 1 pixel, masquée et hors écran. Le chargement d’une mission applique les dimensions de jeu. La réutilisation du processus est testée sous Linux. L’élimination du flash reste à vérifier sur Windows.
