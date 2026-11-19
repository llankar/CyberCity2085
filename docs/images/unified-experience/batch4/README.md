# Reprise tactique — preuves du lot 4

Captures réelles Arcade/Godot sous Linux/Xorg/Mesa, exportées en WebP sans perte. Les images `before-interruption` et `after-resume` proviennent de deux processus Godot distincts ; le deuxième restaure l’instantané, et ne refait pas le déplacement.

- **720p** : déplacement réel (1 PA), arrêt brutal de Godot, rechargement du checkpoint Python, bouton REPRENDRE, nouveau UUID, état tactique restauré, résultats confirmés, débriefing, promotions et HQ.
- **1080p** : même reprise en phase joueur ; dimensions réelles contrôlées par le script.
- **1440p** : phase ennemie, ancien processus laissé vivant après simulation du redémarrage d’Arcade. La nouvelle session lui envoie une annulation portant son UUID ; sa sortie normale est vérifiée. La phase ennemie, les PA et la caméra sont restaurés.
- **ACK après résolution** : interruption simulée entre checkpoint de campagne et accusé de réception. Le nouvel hôte relit l’état appliqué, renvoie l’ACK, montre le débriefing ; le Godot d’origine se ferme normalement, sans nouvelle récompense.

Les fixtures effectuent des mouvements par les méthodes réelles, mais **forcent ensuite la victoire pour tester le retour**. Elles ne valident pas une mission de campagne jouée intégralement ni Windows. L’IA n’est pas jouée dans les captures figées de reprise : le test Godot de roundtrip exécute séparément un vrai tour ennemi après restauration. Le clic viewport → grille après restauration est également testé dans cette fixture.

```sh
DISPLAY=:107 ALSOFT_DRIVERS=null python -m tools.check_unified_return --outcomes victory --interrupt-phase player --resume-debrief --output work/unified-tactical-player-proof
DISPLAY=:107 ALSOFT_DRIVERS=null python -m tools.check_unified_return --width 1920 --height 1080 --outcomes victory --interrupt-phase player --resume-debrief --output work/unified-tactical-1080-proof
DISPLAY=:107 ALSOFT_DRIVERS=null python -m tools.check_unified_return --width 2560 --height 1440 --outcomes victory --interrupt-phase enemy --keep-source-alive --resume-debrief --output work/unified-tactical-1440-proof
DISPLAY=:107 ALSOFT_DRIVERS=null python -m tools.check_unified_return --outcomes victory --interrupt-after-resolution --resume-debrief --output work/unified-return-ack-proof
```

Examen effectué : bouton de reprise lisible, absence de chevauchement, position/PA/caméra conservés, phase ennemie bien identifiée. L’audio Dummy empêche toute validation auditive. L’avertissement ObjectDB à la fermeture de la fixture persiste ; le renderer headless émet aussi des diagnostics de shaders dans certains tests de logique. Ces tests ne prouvent ni l’absence de fuite ni la qualité graphique Windows.
