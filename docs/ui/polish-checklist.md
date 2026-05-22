# UI Polish Checklist

## Motion & Transition
- [x] Les timings/easings sont centralisés dans `game/ui/theme/motion.py`.
- [x] Ouverture/fermeture room-expanded et transitions de sélection utilisent une durée harmonisée (`0.28s`).
- [x] Les micro-interactions restent légères (pulsation alpha discrète sur boutons d'action/fermeture).

## Interaction feedback
- [x] Hover/focus/click conservent une hiérarchie visuelle lisible sans surcharge (contraste + accent léger).
- [x] Feedback audio UI optionnel ajouté (toggle `M`), limité aux actions majeures (recrutement, toggles, sélection mission).

## Vérifications finale
- [ ] Vérifier la lisibilité en low-res (1280x720) et high-res.
- [ ] Vérifier la cohérence de rythme entre Corp/City/Squad.
- [ ] Vérifier qu'aucune animation ne retarde l'action (feeling immédiat).
