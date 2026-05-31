# UI Polish Checklist

## Motion & Transition
- [x] Timings/easings are centralized in `game/ui/theme/motion.py`.
- [x] Room-expanded open/close and selection transitions use a harmonized duration (`0.28s`).
- [x] Micro-interactions stay light (subtle alpha pulse on action/close buttons).

## Interaction feedback
- [x] Hover/focus/click preserve a readable visual hierarchy without overload (contrast + light accent).
- [x] Optional UI audio feedback added (toggle `M`), limited to major actions (recruitment, toggles, mission selection).

## Final checks
- [ ] Verify readability in low-res (1280x720) and high-res.
- [ ] Verify rhythm consistency across Corp/City/Squad.
- [ ] Verify that no animation delays the action (immediate feel).
