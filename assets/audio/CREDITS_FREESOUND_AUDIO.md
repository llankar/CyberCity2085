# CyberCity 2085 — Crédits Freesound (ressources reçues, en attente de commit audio)

Les quatre enregistrements ci-dessous ont été transmis par l'utilisateur le 19 novembre 2026, puis convertis en PCM WAV 48 kHz, 16 bits, deux canaux. Les quatre fichiers WAV correspondants sont préparés dans une archive de cette conversation, **mais pas encore présents sur GitHub**. Ils ne sont donc pas déclarés installés.

Le code du jeu est sous AGPL-3.0. Les ressources audio gardent leurs licences propres, sans changement de licence.

| WAV cible | Titre et auteur | Licence | Source | Transformation |
|---|---|---|---|---|
| `assets/audio/overhaul/ambience/ambience_city_cc0_01.wav` | Seamless City Loop — **qubodup** | CC0 1.0 | https://freesound.org/people/qubodup/sounds/223093/ | FLAC vers WAV, gain -6.445 dB |
| `assets/audio/overhaul/ambience/ambience_city_rain_cc0_01.wav` | Raining in the City Ambience — **RyanKingArt** | CC0 1.0 | https://freesound.org/people/RyanKingArt/sounds/607228/ | M4A mono vers WAV deux canaux, +10.961 dB, recouvrement de boucle 1.5 s |
| `assets/audio/overhaul/movement/move_robot_cc0_01.wav` | Robot / Mech movement — **Breviceps** | CC0 1.0 | https://freesound.org/people/Breviceps/sounds/505670/ | WAV vers WAV 48 kHz, -3.732 dB |
| `assets/audio/overhaul/ambience/ambience_laboratory_ccby_01.wav` | Dark Sci-Fi Laboratory Atmosphere – Spaceship Interior Ambience Loop — **TommasoMotteran** | **CC BY 4.0** | https://freesound.org/people/TommasoMotteran/sounds/864658/ | WAV 24 bits vers PCM16 48 kHz, +11.907 dB, recouvrement de boucle 0.75 s |

- **CC0 1.0** : https://creativecommons.org/publicdomain/zero/1.0/
- **CC BY 4.0** : https://creativecommons.org/licenses/by/4.0/
- **Attribution obligatoire pour la ressource TommasoMotteran** : conserver nom de l'auteur, titre du bruitage, URL de la source, licence et modifications lors de la diffusion du jeu.
- Empreintes SHA-256 exactes des fichiers source et des WAV préparés : `docs/audio/cc0_ccby_sources.json`, champs `received_original_sha256` et `prepared_output_sha256`.
- Validation technique (format/niveaux/durée) effectuée sur les quatre sorties. **Validation à l'écoute et test en partie non effectués.**

Les WAV ne doivent être considérés comme livrés sous Git qu'une fois les fichiers binaires copiés et leur commit vérifié.
