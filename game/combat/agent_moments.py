"""Small, factual agent memories triggered by resolved tactical actions."""

from game.character import Character


def record_last_stand(state, actor, target, *, defeated):
    """Remember one clutch kill per agent per battle; never consume combat RNG."""
    character = getattr(actor, "character", None)
    if (not defeated or not isinstance(character, Character)
            or not any(actor is unit for unit in state.allied_units)
            or target is None or target.unit_type != "enemy" or target.health > 0
            or not 0 < actor.health <= max(1, character.stats.max_hp // 4)):
        return
    recorded = state.tactical_flags.setdefault("last_stand_agents", set())
    if id(character) in recorded:
        return
    recorded.add(id(character))
    line = last_stand_dialogue(character)
    moment = remember_last_stand(character, state.mission, actor.health)
    state.tactical_flags.setdefault("agent_moments", []).append(moment)
    state.logs.append(f'{character.name}: "{line}"')
    state.logs.append(f'REMEMBERED — {moment["text"]}')


def remember_last_stand(character: Character, mission, hp: int) -> dict:
    title = getattr(mission, "title", None) or "Tactical engagement"
    memory = f"{title}: held on at {hp} HP and neutralized a hostile."
    character.history.append(memory)
    return {"kind": "last_stand", "agent_name": character.name, "text": f"{character.name}: {memory}"}


def last_stand_dialogue(character: Character) -> str:
    """Select the line from campaign state for either tactical client."""
    traits = {str(trait).casefold() for trait in character.traits}
    traits.add(character.personality_primary_trait.casefold())
    traits.add(character.personality_secondary_trait.casefold())
    if character.fears:
        return "I'm scared. I'm still here."
    elif character.temporary_scars:
        return "I remember how this ends. Get me to cover."
    elif character.ambition:
        return "I've still got something to finish."
    elif traits & {"reckless", "bold", "brave"}:
        return "Still standing. Who's next?"
    elif traits & {"cautious", "careful", "pragmatic"}:
        return "One down. I need cover."
    return "Not my last shot."


def record_rescue(state, actor, target, *, before_hp, cleared_bleeding):
    helper, patient = actor.character, target.character
    if (actor is target or not isinstance(helper, Character) or not isinstance(patient, Character)
            or before_hp <= 0 or target.health <= 0
            or not (cleared_bleeding or (target.health > before_hp and before_hp <= max(1,patient.stats.max_hp//4)))):
        return
    seen = state.tactical_flags.setdefault("rescue_pairs", set())
    pair = (id(helper), id(patient))
    if pair in seen:
        return
    seen.add(pair)
    mission = getattr(state.mission, "title", None) or "Tactical engagement"
    reason = "stopped the bleeding" if cleared_bleeding else "treated critical wounds"
    helper.history.append(f"{mission}: {reason} for {patient.name} under fire.")
    patient.history.append(f"{mission}: {helper.name} {reason} for me under fire.")
    state.tactical_flags.setdefault("agent_moments", []).append(
        {"kind": "rescue", "agent_name": helper.name, "patient_name": patient.name,
         "text": f"{helper.name} {reason} for {patient.name}."})
    bond = patient.relationships.get(helper.name, 0)
    line = "I knew you wouldn't leave me." if bond > 0 else "Didn't think you'd come back for me." if bond < 0 else "You came for me. Thank you."
    state.logs.append(f'{patient.name}: "{line}"')
    state.logs.append(f"REMEMBERED — {helper.name} helped {patient.name}: {reason}.")


def record_losses(state, participants):
    """Retain loss memories even when AI has removed a fallen unit from its list."""
    seen = state.tactical_flags.setdefault("remembered_losses", set())
    for unit in participants:
        character = unit.character
        if not isinstance(character, Character) or unit.health > 0 or id(character) in seen:
            continue
        seen.add(id(character))
        mission = getattr(state.mission, "title", None) or "Tactical engagement"
        text = f"{character.name} fell during {mission}."
        character.history.append(text)
        survivors = [other for other in participants if other.health > 0 and isinstance(other.character, Character)]
        if survivors:
            survivor = max(survivors, key=lambda other: (other.character.relationships.get(character.name, 0),
                                                         -other.distance_to(unit)))
            witness = survivor.character
            bond = witness.relationships.get(character.name, 0)
            line = f"{character.name}, stay with me!" if bond > 0 else f"{character.name} is down. We need to finish this."
            witness.history.append(f"{mission}: lost a teammate when {character.name} fell.")
            state.logs.append(f'{witness.name}: "{line}"')
        state.tactical_flags.setdefault("agent_moments", []).append(
            {"kind": "downed", "agent_name": character.name, "text": text})
        state.logs.append(f"REMEMBERED — {text}")


def record_panic(state, unit):
    """Record the real lost activation before its one-turn status is cleared."""
    character = unit.character
    if not isinstance(character, Character) or unit.health <= 0 or not unit.has_status("panicked"):
        return
    seen = state.tactical_flags.setdefault("remembered_panic", set())
    if id(character) in seen:
        return
    seen.add(id(character))
    mission = getattr(state.mission, "title", None) or "Tactical engagement"
    text = f"{character.name} lost an activation to panic during {mission}."
    character.history.append(text)
    if character.trauma:
        reaction = "Not again. I need a moment."
    elif character.ambition:
        reaction = "I still have something to finish. Give me a moment."
    else:
        reaction = "I can't focus. Cover me."
    state.logs.append(f'{character.name}: "{reaction}"')
    state.tactical_flags.setdefault("agent_moments", []).append(
        {"kind": "panic", "agent_name": character.name, "text": text})
