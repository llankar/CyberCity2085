# Strategic economy scale

The economy uses one ordinary successful mission as its reference unit:
approximately **1,500 funds**, plus passive income earned during elapsed days.

## Funds bands

| System | Current band | Intended cadence |
|---|---:|---|
| Weekly directive | 500–700 | meaningful but affordable operational choice |
| Equipment | 100–4,340 | starter consumable to exceptional weapon |
| Recruit | 1,300–2,000 typical | roughly one successful mission |
| Research | 600–6,500 | entry project to late prototype |
| Cyberware | 500–11,000 | basic implant to action-point augmentation |
| Heavy asset | 4,500–10,000 | three to seven ordinary missions |
| Asset deployment | 150–400 | mission-level tactical trade-off |
| Base/vehicle upgrade | 9,000–25,000 | medium-term infrastructure goal |
| Hangar expansion | 20,000 / 60,000 / 180,000 | campaign milestones |

Mission allocation categories are reporting envelopes. They do not remove the
same reward a second time; actual purchases, deployments, directives and
service cycles create ledger expenses.

The command forecast combines seven days of passive income with the corporate
weekly payment. Asset maintenance is shown as a **service cycle**, matching the
actual manual service mechanic rather than claiming a daily automatic charge.

## Compatibility

Legacy saves are migrated on load:

- double-digit mission rewards are raised to the current risk floor;
- old weekly stipend/debt values are multiplied to the current scale;
- legacy asset deployment, repair and upkeep values are converted while
  retaining identity, damage, cooldown and pilot state.

## Reproducible balance check

Run:

```text
python -m tools.simulate_strategic_economy
python -m pytest -q tests/test_economy_scale.py tests/test_economy_simulation.py
```

The baseline ordinary reward median is 1,500 funds. With no discretionary
spending, the first 20,000-fund Hangar expansion is reachable after 13 ordinary
missions, inside the requested 10–15 mission window.
