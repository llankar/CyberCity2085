# CyberCity 2085 — Audio Overhaul 1.0

**État vérifié au 19 novembre 2026 : génération ElevenLabs non démarrée, accès à l'estimation confirmé, fournisseur temporairement saturé.**

- [Inventaire actuel](current_inventory.json) : 19 bruitages WAV de synthèse, leur durée, événements Godot et sites d'appel Arcade.
- [Manifeste de production](elevenlabs_manifest.json) : 58 familles, 167 variantes à produire, prompts anglais, déclencheurs, chemins cibles, provenance à compléter, règles de validation et estimation de crédits.
- [Plan d'intégration Codex](integration_plan.md) : gestion multi-variantes, routage Arcade/Godot, conditions de validation et tests.

## ElevenLabs réellement invoqué
Un flow nommé `CyberCity 2085 — Audio Overhaul 1.0 | SFX` a été créé dans ElevenLabs : https://elevenlabs.io/app/flows/3m8GvCVzF9JhOgZl3kbb

Quatre nœuds SFX ont été préparés : `fire_assault`, `impact_metal`, `step_concrete`, `ui_click`, avec 3 candidats prévus chacun.

Le fournisseur a estimé le lot de 12 candidats à **234 crédits (0,0234 USD)**. À l'exécution, il a répondu « Free generations are busy right now », avec **aucune génération démarrée et aucun crédit débité**. Aucun WAV nouveau n'a été produit, téléchargé ou écouté.

Les durées cibles inférieures au minimum de 0,5 seconde du modèle SFX v2 ont été corrigées dans le manifeste. Son estimation complète est **extrapolée** du petit lot, pas vérifiée par une estimation globale. Ni le solde de crédits du compte ni la licence applicable à sa formule ne sont confirmés.

## Préservation
Ne pas écraser les 19 WAV anciens tant que les nouveaux ne sont pas validés. Ne pas remplacer les musiques MP3 existantes. Ne pas exécuter `tools/gen_sounds.py` sur les ressources finales : il réécrit les WAV synthétiques.

## Vérifications obligatoires
Chaque variante n'est utilisable que lorsque le fichier audio existe réellement et que ses propriétés (format, durée, niveau, absence de saturation et caractère sonore) ont été contrôlées. Les ambiances demandent en plus un test de boucle. Aucune génération n'est déclarée approuvée à ce stade.
