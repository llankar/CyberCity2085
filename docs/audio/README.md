# CyberCity 2085 — Audio Overhaul 1.0

**BLOQUÉ — accès ElevenLabs indisponible dans cette session.** Aucun bruitage n’a été généré ni écouté. Les ressources actuelles restent utilisables.

- [Inventaire actuel](current_inventory.json) : 19 WAV, formats et durées mesurés, routage Godot, sites d’appel Arcade/Godot et dispatch dynamique.
- [Manifeste ElevenLabs](elevenlabs_manifest.json) : 58 familles et 167 candidats, avec prompts anglais, durées demandées, déclencheurs envisagés et chemins de livraison. Les champs source, modèle et durée de sortie sont à renseigner à partir des générations réelles. Les durées demandées permettent de calculer le coût dès que le barème du compte est disponible. Aucun montant en crédits n’est vérifié.

Les tirs, impacts et déplacements sont les sons les plus exposés à la répétition. Aujourd’hui les variantes d’armes, de matériaux et de surfaces convergent vers quelques WAV génériques. Les tours et le clic d’interface reviennent régulièrement. Les signaux de déploiement, de fin de mission et de campagne sont ponctuels. Les références de code sont des sites d’appel, pas des mesures de fréquence en partie.

Arcade charge une liste fixe de WAV. Les retours UI `recruitment`, `selection` et `toggle` construisent un nom absent de cette liste. Godot associe un WAV à chaque événement et recycle six lecteurs. Le pont copie les WAV par nom vers le projet Godot. Garder des noms de fichiers uniques et effectuer la sélection de variantes dans les deux lecteurs au moment de l’intégration. L’ajout de nouveaux fichiers ne crée pas de déclencheur par lui-même. Les musiques relèvent du catalogue existant.

Première génération à réaliser dès que l’accès est disponible : un petit lot pilote pour tir de fusil, impact métal, pas béton et clic. Vérifier le coût annoncé par le fournisseur, comparer les candidats à l’écoute, contrôler les crêtes et les queues, puis valider le format PCM. Pour les ambiances, contrôler séparément les raccords de boucle. Consigner provenance, modèle effectivement utilisé et conditions de licence avant intégration et diffusion.
