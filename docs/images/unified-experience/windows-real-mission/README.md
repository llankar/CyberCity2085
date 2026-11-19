# Mission réelle unifiée — Windows

Validation native exécutée le 18 novembre 2026 avec Godot 4.6.3 sur Windows, rendu OpenGL NVIDIA GeForce RTX 5070 Ti.

- Parcours : HQ → carte des missions → briefing → Godot → débriefing → promotions → HQ.
- Condition de fin : objectif `hack` accompli par déplacements pathfindés, dépenses de PA, dix tours ennemis et interactions normales. Aucun appel direct à `_end_combat`, `_complete_mission` ou écriture de `objective_completed`.
- Résultat : victoire après 27 actions, tour 11 ; trois agents à terre et une survivante à 2 PV.
- Publication : résultat préparé invisible à la campagne jusqu’à confirmation, puis appliqué une seule fois ; sauvegarde/rechargement et refus du rejeu vérifiés.
- Transition mesurée : 5,828 s entre le lancement instrumenté et le résultat prêt. Cette mesure inclut le combat automatisé ; elle ne mesure donc pas seulement le démarrage et ne justifie pas encore un préchauffage.
- Affichage demandé : 1280×720. Framebuffer observé : 1920×1080, cohérent avec le plein écran Windows actif.
- Audio : transfert de propriété logique vérifié avec pilote Dummy ; aucune validation auditive.
- Limite : ce passage natif ne valide pas encore Alt+Tab, restauration, DPI multi-écrans ni absence de fenêtre secondaire.

Preuves : `native-report.json`, `victory/godot.log`, `victory/godot-real-results.png`, `victory/05-debrief.png`, `victory/06-promotions.png`, `victory/07-headquarters-return.png`.

