# CyberCity 2085 — Audio Overhaul 1.0

## État vérifié au 19 novembre 2026

**7 générations terminées chez ElevenLabs, 58 familles configurées ; 5 WAV envoyés par l'utilisateur, inspectés techniquement mais non écoutés, non validés et non committés.**

L'ensemble des **58 familles et 167 variantes cibles** est détaillé dans [elevenlabs_manifest.json](elevenlabs_manifest.json), qui relie maintenant chaque famille à son vrai nœud ElevenLabs (`elevenlabs_node`) et liste les ID des 7 générations achevées. Les variantes non générées portent un statut d'attente et ne sont pas des fichiers disponibles.

### Projets ElevenLabs accessibles
- [Principal : armes, interfaces, technologies et essais pilotes](https://elevenlabs.io/app/flows/3m8GvCVzF9JhOgZl3kbb)
- [Armes supplémentaires](https://elevenlabs.io/app/flows/vj5p3VgAMplpSMS6QnwY)
- [Impacts et combats](https://elevenlabs.io/app/flows/hqjK65yzArYgCCR3Ylun)
- [Déplacements](https://elevenlabs.io/app/flows/kDhE2kIk7F7y8aeom152)
- [Ambiances](https://elevenlabs.io/app/flows/OEDA8eQA1fnUUe1mqrlT)

Les tentatives automatisées ont été limitées par la saturation du service de génération gratuite. Des nœuds supplémentaires ont été configurés et peuvent être exécutés dans ElevenLabs lorsque la capacité est disponible. Chaque génération nouvelle dépense des crédits ; lancer **un seul candidat par nœud d'abord**, puis réserver les variantes aux sons fréquents.

### Générations réellement achevées
| Famille | Nombre | État local |
|---|---:|---|
| `fire_pistol` | 1 | MP3 chez ElevenLabs, WAV absent |
| `fire_assault` | 2 | MP3 chez ElevenLabs, WAV absents |
| `impact_metal` | 2 | MP3 chez ElevenLabs, WAV absents |
| `step_concrete` | 1 | MP3 chez ElevenLabs, WAV absent |
| `ui_click` | 1 | MP3 chez ElevenLabs, WAV absent |

Les vrais identifiants de génération et durées sont enregistrés dans le JSON. Une archive utilisateur séparée contient 5 WAV ; certains écarts de durées doivent être élucidés. Aucun son n'a été auditionné ou approuvé par ChatGPT. Aucun nouveau fichier audio n'a été commité dans le dépôt.

## Prochaines étapes
1. Télécharger depuis ElevenLabs les MP3 correspondant aux IDs de génération ; le connecteur fournit des médias mais l'environnement ChatGPT ne peut actuellement pas récupérer ces liens signés.
2. Convertir en WAV PCM 48 kHz, 16 bits, stéréo dans un dossier de staging, sans écraser les 19 effets historiques. Un kit d'import/QA autonome a été fourni dans la conversation.
3. Vérifier les crêtes, saturation, durée, queue sonore, qualité à l'écoute, raccords des boucles d'ambiances et licences.
4. Intégrer après validation via le [plan d'intégration Codex](integration_plan.md), avec variantes, non-répétition, anti-spam, routage Arcade/Godot, et fallback.
5. Tester les deux moteurs, la continuité des musiques et les événements de combat, avant fusion de la PR.

### Sources complémentaires
- [Inventaire des 19 WAV historiques](current_inventory.json)
- [Manifeste complet](elevenlabs_manifest.json)
- [Plan technique d'intégration](integration_plan.md)

**Interdictions :** ne pas confondre un nœud configuré, une génération terminée chez le fournisseur et un fichier réellement installé. Ne pas lancer `tools/gen_sounds.py` sur la nouvelle bibliothèque ; préserver les MP3 musicaux existants et les effets de secours jusqu'à validation.


## Réception d'une archive utilisateur et contrôle technique (19 novembre 2026)

- Source : `cybercity_sfx_staging_unreviewed.zip` reçue dans la conversation, contenant **5 WAV PCM 48 kHz 16 bits stéréo** et un rapport d'import.
- Familles présentes : `fire_pistol_01`, `fire_assault_01`, `impact_metal_01`, `step_concrete_01`, `ui_click_01`.
- `fire_assault_02` et `impact_metal_02` figurent comme fichiers manquants dans le rapport d'import ; aucun des deux n'est présent dans cette archive.
- `impact_metal_01.wav` atteint le pleine échelle numérique sur 3 échantillons. La copie de staging a été atténuée de 3 dB, **sans correction du possible écrêtage initial**.
- `fire_assault_01.wav` a été atténué de 2,84 dB afin de conserver au moins 3 dB de marge. Les trois autres fichiers ne nécessitaient pas d'atténuation.
- Le WAV du pistolet dure 1,48 s contre 0,88 s annoncé par ElevenLabs ; le WAV d'assaut 3,00 s contre 1,48 s ; le WAV métal 0,88 s contre 1,00 s. **Association à vérifier sur les originaux MP3**, pas de déclaration de conformité.
- Un pack de QA local a été créé avec les WAV originaux et les copies staging, ainsi qu'un manifeste de mesures et empreintes SHA256. Il n'est pas présent dans le dépôt GitHub.
- À ce stade, aucun fichier n'a été installé dans Arcade ou Godot. Écoute humaine, licence et tests en jeu restent obligatoires.
