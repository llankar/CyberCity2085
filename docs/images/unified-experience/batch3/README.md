# Propriété musicale Arcade ↔ Godot

Parcours natif Linux 1280×720, issue forcée victoire, débriefing récupéré puis promotion et HQ. La fixture vérifie que Godot ne possède pas la musique avant le message Python et obtient cette propriété après readiness. Le pilote audio est Dummy : aucun son n’a été écouté. Le rapport ne valide ni un fondu audible, ni Windows.

Commande : `DISPLAY=:107 ALSOFT_DRIVERS=null python -m tools.check_unified_return --outcomes victory --resume-debrief --output work/unified-audio-proof`.

Le journal Godot émet encore un avertissement ObjectDB à la fermeture de la fixture ; ce test n’établit pas l’absence de toute fuite de ressources. Les captures sont conservées dans `work/unified-audio-proof` ; l’interface est inchangée par ce lot audio.
