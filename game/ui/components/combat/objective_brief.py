"""Objective instructions derived from the actual interaction/win model."""


def objective_brief_lines(objective, *, turn_number=1, defend_turns_required=4, enemy_count=None):
    if getattr(objective, "failed", False):
        return "FAILED", getattr(objective,"failure_message","") or "Objective failed."
    if getattr(objective,"completed",False):
        until=getattr(objective,"hold_until_turn",None)
        if until is not None and turn_number<until:
            return f"Counterpush: hold until turn {until}", "Survive the counterpush; no interaction required."
        return "Objective complete", "Objective secured."
    kind=getattr(objective,"kind","")
    if kind=="defend":
        return f"Hold: turn {min(turn_number,defend_turns_required)}/{defend_turns_required}", "Keep hostiles out of the marked zone."
    if kind=="containment":
        progress=f"Hostiles remaining: {enemy_count}" if enemy_count is not None else "Contain the threat"
        return progress, "Keep hostiles above the line; eliminate them."
    if kind=="assassination":
        return "Priority target active", "Eliminate the marked high-value target."
    return getattr(objective,"progress_text",""), "E: 1 AP, once per squad turn; clear nearby hostiles."
