# Playable Loop (Required)

CyberCity2085 playable loop must always follow this chain:

1. **Base management**
   - Player allocates resources, handles events, prepares economy and recovery.
2. **Squad preparation**
   - Player recruits/selects agents, equips loadouts, manages stress/recovery, assigns support assets.
3. **Mission launch**
   - Player picks an operation and confirms deployment.
4. **Battle resolution**
   - Tactical outcome resolves mission objectives, casualties, and objective branches.
5. **Consequences**
   - Rewards/penalties apply (funds/resources/faction/narrative aftermath/stress).
6. **Next day**
   - Strategic day advances (calendar/events/research/recovery/income), enabling next planning cycle.

## Design decision

This loop keeps **agents as the emotional core** while preserving a compact modular structure: each stage changes persistent state and leaves readable traces in logs/UI.
