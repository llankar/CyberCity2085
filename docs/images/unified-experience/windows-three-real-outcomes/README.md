# Trois issues tactiques réelles — Windows

Exécuté le 18 novembre 2026 avec Godot 4.6.3, OpenGL NVIDIA GeForce RTX 5070 Ti, framebuffer observé 1920×1080.

| Issue | Condition réellement jouée | Résultat |
|---|---|---|
| Victoire | objectif `hack` accompli par pathfinding, PA, tours ennemis et interactions | PASS |
| Défaite | escouade laissée à l’IA jusqu’à 0 survivant, sans mutation directe des PV | PASS, tour 27 |
| Retraite | nouvelle commande HUD `RETRAITE [R]`, double confirmation, résultat de campagne normal | PASS, tour 1 |

Les trois cas passent ensuite par confirmation du résultat, débriefing, éventuelles promotions, retour HQ, sauvegarde/rechargement et contrôle anti-double application. Les captures résultat et débriefing ont été examinées pour chaque issue. L’audio utilise le pilote Dummy : aucune écoute réelle n’est revendiquée.

Les mesures froides observées sont de 2,109 s à 3,625 s jusqu’à première frame/readiness. La musique Arcade restant active pendant ce délai, aucun préchauffage n’est ajouté : son coût de cycle de vie n’est pas justifié par ces mesures. Cette décision devra être réévaluée si le package ou un matériel minimal dépasse durablement le seuil documenté.

Preuves : `native-report.json`, dossiers `victory/`, `defeat/` et `retreat/`.

