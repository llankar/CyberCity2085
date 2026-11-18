# Unified Experience — preuves du lot 1

**CHANTIER GLOBAL INCOMPLET.** Ces captures proviennent d’Arcade et Godot réellement exécutés avec OpenGL sous Linux/llvmpipe. Elles ne valident pas l’intégration des fenêtres Windows.

| Phase | Victoire | Défaite | Retraite |
|---|---|---|---|
| Headquarters | [Voir](victory-01-headquarters.webp) | [Voir](defeat-01-headquarters.webp) | [Voir](retreat-01-headquarters.webp) |
| World Map | [Voir](victory-02-world-map.webp) | [Voir](defeat-02-world-map.webp) | [Voir](retreat-02-world-map.webp) |
| Briefing | [Voir](victory-03-briefing.webp) | [Voir](defeat-03-briefing.webp) | [Voir](retreat-03-briefing.webp) |
| Résultat Godot consultable | [Voir](victory-godot-results.webp) | [Voir](defeat-godot-results.webp) | [Voir](retreat-godot-results.webp) |
| Débriefing Arcade | [Voir](victory-05-debrief.webp) | [Voir](defeat-05-debrief.webp) | [Voir](retreat-05-debrief.webp) |
| Retour HQ | [Voir](victory-07-headquarters-return.webp) | [Voir](defeat-07-headquarters-return.webp) | [Voir](retreat-07-headquarters-return.webp) |

[Promotion réelle après le débriefing de victoire](victory-06-promotions.webp).

## Portée exacte

La fixture effectue un vrai déplacement dans le combat, puis force une issue pour tester le retour. Les résultats JSON sont écrits par le véritable composant Godot, jamais fabriqués par le test Python. Les trois scénarios ne constituent pas une validation exhaustive du combat/IA ni des conditions de victoire.

Avant confirmation, le processus reste vivant, le fichier final reste absent et les fonds de campagne restent inchangés. La confirmation déclenche la validation et la résolution commune. Les contrôles vérifient le débriefing avant les promotions, le retour HQ, la sauvegarde/relecture et le refus de payer deux fois. Les champs individuels non mesurés s’affichent « — ».

Le défaut de taille nulle du panneau de résultats a été corrigé et vérifié sur les captures. Les fonds et ressources affichés au débriefing viennent de la résolution de campagne ; aucune récompense inventée n’est ajoutée par Godot.

[Rapport natif](native-report.json) · [67 cas de tests distincts](../../../reports/unified_batch1_tests.xml) · [Suivi du chantier](../../../UNIFIED_EXPERIENCE_PROGRESS.md).

## Reproduire

```sh
DISPLAY=:107 ALSOFT_DRIVERS=null python -m tools.check_unified_return --output work/unified-experience-proof
```

La session X11 doit être disponible. Les tests de protocole peuvent être exécutés headless ; ils ne prouvent ni le focus ni les transitions de fenêtres. Aucun parcours Windows, DPI, Alt+Tab ou minimisation/restauration Windows n’est déclaré validé.

## Encore ouvert

Journal durable avant/après avec reprise après crash d’Arcade ; reprise du débriefing après un redémarrage ; readiness/heartbeat et délais ; intégration Win32 et tests sur Windows ; synchronisation audio perceptuelle et chargement sans flashs.
