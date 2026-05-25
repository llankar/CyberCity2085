"""Initiative timeline component for tactical combat HUD."""

from __future__ import annotations

from dataclasses import dataclass

from game.ui import palette


_HIGH_IMPACT_SUBTYPES = {"sniper", "elite", "commander"}


@dataclass(frozen=True)
class InitiativeTimelineEntry:
    """One projected activation in the near-future turn sequence."""

    label: str
    is_enemy: bool
    is_active: bool
    threat: str | None


def _unit_label(unit: object) -> str:
    character = getattr(unit, "character", None)
    if character:
        return character.name.split()[0].upper()[:9]
    asset = getattr(unit, "spec_ops_asset", None)
    if asset:
        return asset.name.upper()[:9]
    subtype = str(getattr(unit, "enemy_subtype", "grunt"))
    return subtype.upper()[:9]


def _initiative_value(unit: object) -> int:
    stats = getattr(unit, "stats", None)
    return int(getattr(stats, "agi", 0)) if stats else 0


def _threat_for_enemy(unit: object) -> str | None:
    subtype = str(getattr(unit, "enemy_subtype", "grunt")).lower()
    if subtype in _HIGH_IMPACT_SUBTYPES:
        return "HIGH"
    return None


def build_initiative_timeline(
    player_units: list[object],
    enemy_units: list[object],
    *,
    active_player_index: int,
    slots: int = 8,
) -> list[InitiativeTimelineEntry]:
    """Build projected near-term activations from current turn state and initiative.

    Current active player remains first, then remaining players by initiative,
    then enemy activations by initiative. Dead units are excluded.
    """
    living_players = [unit for unit in player_units if getattr(unit, "health", 0) > 0]
    living_enemies = [unit for unit in enemy_units if getattr(unit, "health", 0) > 0]
    if not living_players and not living_enemies:
        return []

    ordered_players: list[object] = []
    if 0 <= active_player_index < len(player_units):
        active_unit = player_units[active_player_index]
        if getattr(active_unit, "health", 0) > 0:
            ordered_players.append(active_unit)

    ordered_players.extend(
        sorted(
            [u for u in living_players if u not in ordered_players],
            key=_initiative_value,
            reverse=True,
        )
    )
    ordered_enemies = sorted(living_enemies, key=_initiative_value, reverse=True)

    projected = ordered_players + ordered_enemies
    timeline: list[InitiativeTimelineEntry] = []
    for idx, unit in enumerate(projected[: max(1, slots)]):
        is_enemy = unit in ordered_enemies
        timeline.append(
            InitiativeTimelineEntry(
                label=_unit_label(unit),
                is_enemy=is_enemy,
                is_active=(idx == 0),
                threat=_threat_for_enemy(unit) if is_enemy else None,
            )
        )
    return timeline


def draw_initiative_timeline(
    width: int,
    height: int,
    timeline: list[InitiativeTimelineEntry],
) -> None:
    """Render the top-right timeline for next 6-8 activations."""
    if not timeline:
        return

    import arcade

    panel_width = 320
    panel_height = 34 + 30 * len(timeline)
    left = width - panel_width - 14
    top = height - 92
    bottom = top - panel_height

    arcade.draw_lrbt_rectangle_filled(left, left + panel_width, bottom, top, (0, 0, 0, 190))
    arcade.draw_line(left, top, left + panel_width, top, palette.PANEL_BORDER, 2)
    arcade.draw_text("INITIATIVE", left + 10, top - 16, palette.TEXT, font_size=10, bold=True)

    row_top = top - 32
    for idx, entry in enumerate(timeline):
        row_y = row_top - idx * 30
        if entry.is_active:
            arcade.draw_lrbt_rectangle_filled(
                left + 8,
                left + panel_width - 8,
                row_y - 20,
                row_y + 6,
                (*palette.TACTICAL_GREEN[:3], 48),
            )

        role_col = palette.DANGER if entry.is_enemy else palette.TACTICAL_GREEN
        marker = "●" if entry.is_active else "○"
        arcade.draw_text(marker, left + 14, row_y - 6, role_col, font_size=11, bold=entry.is_active)
        arcade.draw_text(entry.label, left + 34, row_y - 6, palette.TEXT, font_size=10, bold=entry.is_active)

        if entry.threat:
            arcade.draw_text(
                "THREAT",
                left + panel_width - 66,
                row_y - 6,
                palette.WARNING,
                font_size=8,
                bold=True,
            )
