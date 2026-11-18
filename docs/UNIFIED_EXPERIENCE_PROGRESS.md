# Unified Experience 1.0 — progression persistante

**CHANTIER GLOBAL INCOMPLET.** Arcade reste propriétaire de la campagne ; Godot ne modifie aucune sauvegarde. Les travaux Combat Visual / SCALE sont conservés et passent derrière cette nouvelle priorité.

## Critères d’acceptation

- [ ] Headquarters → World Map → Briefing → Combat Godot → Results consultables → confirmation → Debrief → Promotions → Headquarters.
- [ ] Résolution commune aux deux moteurs, résultat validé avant mutation, données absentes signalées, récompenses appliquées une seule fois.
- [ ] Sessions et messages versionnés, identité de mission, ready/start/end/result/ack/error ; erreurs et déconnexions récupérables.
- [ ] Résultat préparé distinct du résultat confirmé ; aucune interruption du résultat affiché ; récupération explicite après crash.
- [ ] Sauvegarde/rechargement et anti-duplication après interruption vérifiés.
- [ ] Fenêtre Windows unifiée : bordures, focus, Alt+Tab, minimisation, restauration, redimensionnement et DPI testés graphiquement.
- [ ] Transition et audio cohérents, sans bureau visible ni doublons ; fallback Arcade explicitement choisi.
- [ ] Tests Python/Godot et parcours graphique réel ; aucune équivalence entre headless et validation des fenêtres.

## Lot 1 — priorité au retour de combat (cinq tâches)

1. DONE — Auditer les flux et définir le contrat de résultat/session.
2. DONE — Séparer préparation et confirmation du résultat dans Godot.
3. DONE — Extraire la résolution de campagne commune et valider le résultat Godot avant mutation.
4. DONE — Router le retour vers débriefing, promotions et HQ ; supprimer l’ancien raccourci d’application.
5. DONE — Tester victoire/défaite/retraite, erreurs et doublons ; sauvegarder preuves et point Git.

## Lots suivants

- Transport bidirectionnel, acquittement et journal de récupération durable, déconnexions et sessions isolées.
- Cycle de vie des processus et intégration Win32 ; lancement masqué/préchauffage lorsque réellement compatible.
- Continuité graphique/audio et tests natifs complets du parcours.

## État réel observé

`mission_results.gd` écrit immédiatement les fichiers et le signal. `GodotCombatHandoffView` les lit, tue Godot, ajoute fonds/XP dans un parcours simplifié et revient à Management. Le parcours Arcade applique ressources, conséquences, aftermath et réputation dans `BattleView.end_battle`, puis montre actuellement les promotions avant le débriefing.

## Tests et blocages

67 cas distincts réussis : validation sans mutation, rollback sur échec, statuts de session, doublons et relecture des sauvegardes, soutiens endommagés, blessure/mort, résultat préparé/confirmé et ACK. Trois parcours natifs Linux contrôlés avec captures : Headquarters → World Map → Briefing → Godot → Results → Debrief → Promotions éventuelles → Headquarters. Les issues sont forcées par la fixture, pas une validation exhaustive du combat. Environnement Linux : validation graphique Windows indisponible ; Alt+Tab/DPI Win32 ne seront pas déclarés validés par des mocks.

## Prochaine action précise

Lot 2 : écrire des checkpoints Python atomiques avant et après résolution, conserver un instantané de débriefing pour rejouer les écrans sans rejouer les récompenses, puis ajouter readiness/erreurs et tests de crash. La validation graphique Windows reste bloquée par l’environnement Linux.

## Réalisé et preuves du lot 1

- Session UUID isolée, protocole 2 et mailboxes atomiques ; session/mission/HP/déploiement validés avant traitement. Ancien raccourci fonds/XP retiré du handoff.
- Résolution campagne extraite de `BattleView.end_battle` et réutilisée par Godot, sur copie transactionnelle. Ressources, conséquences, blessures, aftermath, réputation, XP et soutiens passent par les règles existantes.
- Résultat préparé distinct de la confirmation ; Godot attend un ACK correspondant. L’interface affiche de vrais résultats, avec récompenses résolues uniquement côté campagne.
- Débriefing puis promotions puis HQ ; champs non mesurés indisponibles. Les doublons confirmés sont refusés après relecture d’une sauvegarde.
- [Captures et limites](images/unified-experience/batch1/README.md) ; [JUnit 67 cas distincts](reports/unified_batch1_tests.xml).

## Limites de cette étape

Le journal anti-duplication est sérialisé dans les sauvegardes, mais aucun checkpoint durable automatique n’est encore écrit au moment de la transaction. Un crash d’Arcade avant sauvegarde reste à traiter. La reprise d’un résultat déjà appliqué ne réaffiche pas encore automatiquement le débriefing. Le protocole n’a pas encore de readiness/heartbeat. Windows n’a pas été testé graphiquement ; ne pas confondre les captures Linux avec un test des fenêtres Win32.
