# Unified Experience — preuves du lot 2

Captures réelles Arcade et Godot sous Linux/Xorg/Mesa, exportées en WebP sans perte. Aucun montage. Les issues sont forcées par la fixture pour vérifier le retour de combat ; ce ne sont pas des parties complètes ni des tests Win32.

- `victory/defeat/retreat-04-crash-recovery` : Godot tué avant confirmation ; récupération proposée explicitement.
- `*-05-recovered-debrief` : état rechargé depuis le checkpoint après résolution, sans nouvelle récompense.
- `*-06-promotions` : promotions après le débriefing, lorsque les règles existantes en produisent.
- `1080-*`, `1440-*` : véritables dimensions Godot respectivement 1920×1080 et 2560×1440 ; le script vérifie les pixels du fichier capturé. Les premières tentatives avaient une fixture forçant 720p et ne constituent pas ces preuves.
- Rapports natifs JSON joints ; les trois issues sont vérifiées en 720p, la victoire avec reprise du débriefing aux deux résolutions supérieures.

Commandes :

```sh
DISPLAY=:107 ALSOFT_DRIVERS=null python -m tools.check_unified_return --crash-recovery --resume-debrief --output work/unified-recovery-proof
DISPLAY=:107 ALSOFT_DRIVERS=null python -m tools.check_unified_return --width 1920 --height 1080 --outcomes victory --resume-debrief --output work/unified-1080-verified
DISPLAY=:107 ALSOFT_DRIVERS=null python -m tools.check_unified_return --width 2560 --height 1440 --outcomes victory --resume-debrief --output work/unified-1440-verified
```

Examen effectué : écran de récupération sans chevauchement, débriefing récupéré lisible, résultats Godot centrés en 1440p. L’audio est neutralisé pour le test : aucune validation auditive. Aucun Alt+Tab, DPI ou changement de moniteur Windows n’est validé par ces captures.
