# Character Sheet Visual 2.0 and medical downtime

The operative dossier now uses a full-screen, three-column holographic layout in
Python Arcade. Existing portraits, equipped items, progression and talent trees
supply every value. Cyan frames, orange available upgrades, violet PSI cards,
hover details and short upgrade flashes share Squad Command's cached painter.

## Components and behavior

`game/ui/layouts/character_sheet.py` handles responsive geometry and independent
row paging. `character_sheet_model.py` projects domain calculations without
mutating agents. Separate identity, attributes, skills and talent components
render the dossier through `CharacterSheetRenderer`; management retains its
existing point-spending, unlock, save and close handlers.

All twelve skills are accessible. At 1280×720, or with large accessibility text,
wheel scrolling, header arrows and Page Up/Down reveal remaining rows without
shrinking text or clipping interactive cards. Hovering a talent shows its full
description and requirements in the footer. Robot/power-armor agents truthfully
show no specialization tree when the game provides none.

The real XP threshold is 100 × level², rather than the illustrative reference
value. Stress retains the existing derived stress-cap calculation. Talent tiers
are labels: unlocks use actual prerequisites and talent points, without adding
level gates. Skill ranks retain their existing cap and spending rules. Existing
authored mission/item/talent text is preserved; interface labels follow the
configured French or English language.

## Rest and Hospital

Two activities join the three existing downtime actions. They treat the currently
displayed agent, including an agent recovering from injuries:

| Activity | Duration | Cost | Healing |
| --- | --- | --- | --- |
| Rest [R] | 1 day | Free | 25% of maximum HP, rounded upward |
| Hospital [H] | 1 day | 8 strategic credits | Full HP |

Healing is capped at maximum HP. Full-health, dead, transformed or missing
patients incur no day or resource cost. Insufficient funds leave HP and calendar
unchanged. Existing calendar recovery/stress ticks still occur; treatment does
not independently clear remaining recovery days. The other three activities keep
their original targets, costs and effects.

## Actual Arcade captures

These are captures of the running interface, not generated mockups:

- [1280×720](images/character-sheet-2/dossier-1280x720.png)
- [1920×1080](images/character-sheet-2/dossier-1920x1080.png)
- [2560×1440](images/character-sheet-2/dossier-2560x1440.png)
- [720p with large text](images/character-sheet-2/dossier-large-text.png)
- [PSI agent](images/character-sheet-2/dossier-psi.png)
- [English interface](images/character-sheet-2/dossier-english.png)
- [Medical downtime](images/character-sheet-2/downtime-treatments.png)
- [Downtime with large text](images/character-sheet-2/downtime-large-text.png)

Native interaction verification exercises point costs, rank caps, prerequisites,
read-only owned talents, all twelve skills, role changes, paging, language
changes, treatment, save/load and close. Pure tests additionally verify invalid
patients, insufficient credits, capped healing and parity with domain values.

Validation: the broader regression suite passed 85 tests and five subtests.
After the final accessibility-spacing changes, both native capture/interaction
checks passed; the final focused pure suite passed 40 tests and five subtests.

Reproduce captures with:

```sh
DISPLAY=:103 ALSOFT_DRIVERS=null python -m tools.check_character_sheet_visual
```

Implementation remains local until publication is authorized.
