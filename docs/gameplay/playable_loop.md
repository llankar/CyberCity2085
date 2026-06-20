# Playable Loop (Required)

CyberCity2085 playable loop must always follow this chain:

1. **Base management**
   - Player allocates resources, handles events, prepares economy and recovery.
2. **Squad preparation**
   - Player recruits/selects agents, equips loadouts, manages stress/recovery, assigns support assets.
3. **Mission launch**
   - Player picks an operation and reviews the mission briefing before deployment.
   - The briefing must expose objective, target faction, district, risk, expected stress band, emotional impact, complications, map preview, squad roster, selected support assets, reward preview, and DEPLOY / ABORT actions.
4. **Battle resolution**
   - Tactical outcome resolves mission objectives, casualties, and objective branches.
   - The post-battle debrief must show objective result, rewards, per-agent performance/stress/injuries/XP, triggered complications, faction/district changes, narrative consequences, and a clear return to management.
   - The compact consequence summary must expose city pressure, faction hostility/influence/legitimacy, tags gained, agent scars, rewards, unavailable missions, intel unlocks, and campaign state changes.
5. **Consequences**
   - Rewards/penalties apply (funds/resources/faction/narrative aftermath/stress).
6. **Next day**
   - Strategic day advances (calendar/events/research/recovery/income), enabling next planning cycle.

## Design decision

This loop keeps **agents as the emotional core** while preserving a compact modular structure: each stage changes persistent state and leaves readable traces in logs/UI.

## Downtime (Squad / Management)
- New downtime menu in Squad view with three activities.
- Each activity spends 1 day + strategic resource, then updates selected agents' stress, morale (loyalty proxy), and traits.
- Shortcuts: keys 7/8/9.
