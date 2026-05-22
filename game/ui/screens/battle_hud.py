"""CyberCity 2085 — Tactical Battle HUD.

Provides all overlay drawing for the BattleView: tactical grid,
unit status panel, turn/phase indicator, movement & attack range
highlights, and improved unit labels.

Keeping all draw logic here makes BattleView.on_draw clean and lets
this module be tested / swapped independently of game logic.
"""

from __future__ import annotations

import math
from typing import TYPE_CHECKING

import arcade

from game.ui import palette

if TYPE_CHECKING:
    from game.unit import Unit

# ── Grid constants ──────────────────────────────────────────────────────────

CELL = 32           # pixels per tile — matches unit.distance_to() math
MOVE_RANGE = 3      # default AP moves for highlighting
ATTACK_RANGE_DEFAULT = 4


# ── Palette aliases ─────────────────────────────────────────────────────────

_GRID_COL       = (50,  100, 130,  18)
_MOVE_COL       = (60,  160, 220,  28)
_ATTACK_COL     = (255, 160,  60,  28)
_ACTIVE_COL     = (120, 232, 180)
_ENEMY_COL      = (255,  88,  76)
_PHASE_PLAYER   = palette.TACTICAL_GREEN
_PHASE_ENEMY    = palette.DANGER
_PHASE_END      = palette.MUTED_TEXT


# ══════════════════════════════════════════════════════════════════════════════
# Public API
# ══════════════════════════════════════════════════════════════════════════════

def draw_tactical_grid(width: int, height: int) -> None:
    """Draw a faint isometric-style grid over the whole map."""
    for x in range(0, width + CELL, CELL):
        arcade.draw_line(x, 0, x, height, _GRID_COL, 1)
    for y in range(0, height + CELL, CELL):
        arcade.draw_line(0, y, width, y, _GRID_COL, 1)


def draw_movement_range(unit: Unit, width: int, height: int) -> None:
    """Highlight cells the active unit can reach (Manhattan ≤ MOVE_RANGE)."""
    if not unit or not unit.position:
        return
    ux, uy = unit.position
    moves = max(1, getattr(unit, "action_points", 1)) * MOVE_RANGE
    for dx in range(-moves, moves + 1):
        for dy in range(-moves, moves + 1):
            if abs(dx) + abs(dy) <= moves:
                cx = ux + dx * CELL
                cy = uy + dy * CELL
                if 0 <= cx < width and 0 <= cy < height:
                    arcade.draw_lrbt_rectangle_filled(
                        cx, cx + CELL, cy, cy + CELL, _MOVE_COL
                    )


def draw_attack_range(
    unit: Unit, width: int, height: int, *, highlight: bool = False
) -> None:
    """Highlight cells within the unit's attack range (orange tint)."""
    if not unit or not unit.position:
        return
    ux, uy = unit.position
    r = getattr(unit, "attack_range", ATTACK_RANGE_DEFAULT) * CELL
    for dx in range(-int(r / CELL) - 1, int(r / CELL) + 2):
        for dy in range(-int(r / CELL) - 1, int(r / CELL) + 2):
            cx = ux + dx * CELL
            cy = uy + dy * CELL
            dist = math.sqrt(dx * dx + dy * dy) * CELL
            if dist <= r and 0 <= cx < width and 0 <= cy < height:
                col = (*_ATTACK_COL[:3], 44) if highlight else _ATTACK_COL
                arcade.draw_lrbt_rectangle_filled(cx, cx + CELL, cy, cy + CELL, col)


def draw_active_unit_ring(unit: Unit, elapsed: float) -> None:
    """Draw a pulsing selection ring around the active player unit."""
    if not unit or not unit.sprite:
        return
    cx = unit.sprite.center_x
    cy = unit.sprite.center_y
    r  = max(20, unit.sprite.width // 2 + 6)
    pulse = 0.7 + 0.3 * math.sin(elapsed * 3.0)
    alpha = int(220 * pulse)
    col   = (*_ACTIVE_COL, alpha)
    # Outer ring
    for angle_deg in range(0, 360, 6):
        a = math.radians(angle_deg)
        b = math.radians(angle_deg + 6)
        arcade.draw_line(
            cx + r * math.cos(a), cy + r * math.sin(a),
            cx + r * math.cos(b), cy + r * math.sin(b),
            col, 2,
        )
    # Corner brackets (XCOM style)
    bracket = 10
    corners = [(-r, -r), (r, -r), (r, r), (-r, r)]
    segs = [
        [(0, bracket), (0, 0), (bracket, 0)],
        [(-bracket, 0), (0, 0), (0, bracket)],
        [(0, -bracket), (0, 0), (-bracket, 0)],
        [(bracket, 0), (0, 0), (0, -bracket)],
    ]
    for (ox, oy), pts in zip(corners, segs):
        for i in range(len(pts) - 1):
            ax, ay = pts[i]
            bx, by = pts[i + 1]
            arcade.draw_line(
                cx + ox + ax, cy + oy + ay,
                cx + ox + bx, cy + oy + by,
                (*palette.HEADER, 200), 2,
            )


def draw_unit_labels(
    player_units: list[Unit],
    enemy_units:  list[Unit],
    active_index:  int,
) -> None:
    """Draw HP bars and role labels above every unit."""
    for i, unit in enumerate(player_units):
        if not unit.sprite or not unit.stats:
            continue
        _draw_unit_bar(unit, active=(i == active_index), is_enemy=False)

    for unit in enemy_units:
        if not unit.sprite or not unit.stats:
            continue
        _draw_unit_bar(unit, active=False, is_enemy=True)


def _draw_unit_bar(unit: Unit, *, active: bool, is_enemy: bool) -> None:
    cx   = unit.sprite.center_x
    top  = unit.sprite.center_y + unit.sprite.height // 2 + 4
    bw   = max(40, unit.sprite.width + 12)
    bh   = 6
    lx   = cx - bw // 2
    rx   = cx + bw // 2
    # HP bar background
    arcade.draw_lrbt_rectangle_filled(lx, rx, top, top + bh, palette.PANEL_FILL_DARK)
    # HP fill
    hp_frac  = max(0, min(1, unit.health / max(1, unit.stats.max_hp)))
    hp_col   = _ENEMY_COL if is_enemy else _ACTIVE_COL
    fill_w   = int(bw * hp_frac)
    arcade.draw_lrbt_rectangle_filled(lx, lx + fill_w, top, top + bh, hp_col)
    # Border
    arcade.draw_line(lx, top,     rx, top,     palette.PANEL_BORDER_MUTED, 1)
    arcade.draw_line(lx, top + bh, rx, top + bh, palette.PANEL_BORDER_MUTED, 1)

    # Name label above HP bar
    name = ""
    if unit.character:
        name = unit.character.name.split()[0].upper()
    elif unit.spec_ops_asset:
        name = unit.spec_ops_asset.name[:8].upper()
    else:
        name = unit.unit_type.upper()[:6]
    name_col = palette.HEADER if active else (
        palette.DANGER if is_enemy else palette.MUTED_TEXT
    )
    arcade.draw_text(name, cx, top + bh + 3, name_col, font_size=8, anchor_x="center")


def draw_phase_banner(
    width: int, height: int, turn: str, turn_number: int, elapsed: float
) -> None:
    """Draw a prominent turn/phase indicator in the top-right corner."""
    if turn == "player":
        label  = "PLAYER TURN"
        color  = _PHASE_PLAYER
        pulse  = 0.9 + 0.1 * math.sin(elapsed * 2.0)
    elif turn == "enemy":
        label  = "ENEMY TURN"
        color  = _PHASE_ENEMY
        pulse  = 0.8 + 0.2 * math.sin(elapsed * 3.0)
    else:
        label  = "MISSION END"
        color  = _PHASE_END
        pulse  = 1.0

    # Turn number dots (left of label)
    dot_x = width - 320
    dot_y = height - 34
    for i in range(min(turn_number, 12)):
        dot_col = (*color[:3], int(200 * pulse)) if i < turn_number else (*color[:3], 50)
        arcade.draw_lrbt_rectangle_filled(
            dot_x + i * 18, dot_x + i * 18 + 12, dot_y, dot_y + 12, dot_col
        )

    # Phase label
    arcade.draw_text(
        label,
        width - 20, height - 26,
        (*color[:3], int(230 * pulse)),
        font_size=13,
        bold=True,
        anchor_x="right", anchor_y="center",
    )


def draw_unit_status_panel(
    width: int, height: int, unit: Unit | None, turn: str
) -> None:
    """Draw the bottom-left status panel for the active player unit."""
    pw = 320
    ph = 82
    px = 12
    py = 54  # above the action bar

    # Background panel
    arcade.draw_lrbt_rectangle_filled(px, px + pw, py, py + ph, palette.PANEL_FILL_DARK)
    arcade.draw_line(px, py + ph, px + pw, py + ph, palette.PANEL_BORDER, 2)
    arcade.draw_line(px, py,     px + pw, py,     palette.PANEL_BORDER_MUTED, 1)
    arcade.draw_line(px, py,     px,      py + ph, palette.PANEL_BORDER_MUTED, 1)
    arcade.draw_line(px + pw, py, px + pw, py + ph, palette.PANEL_BORDER_MUTED, 1)

    if unit is None:
        arcade.draw_text(
            "NO ACTIVE UNIT",
            px + 12, py + ph // 2,
            palette.MUTED_TEXT, font_size=11, anchor_y="center",
        )
        return

    # Role color
    role = ""
    if unit.character:
        role = unit.character.role
    role_col = {
        "sniper": palette.ROLE_SNIPER,
        "psi":    palette.ROLE_PSI,
    }.get(role, palette.ROLE_SAMURAI)

    # Portrait area
    pp = 56
    arcade.draw_lrbt_rectangle_filled(px + 8, px + 8 + pp, py + 13, py + 13 + pp, palette.AGENT_PORTRAIT_FILL)
    arcade.draw_line(px + 8, py + 13 + pp, px + 8 + pp, py + 13 + pp, role_col, 2)

    # Name + role
    name = (
        unit.character.name if unit.character
        else unit.spec_ops_asset.name if unit.spec_ops_asset
        else unit.unit_type
    )
    arcade.draw_text(name.upper(), px + 76, py + ph - 18, palette.TEXT, font_size=12, bold=True)
    arcade.draw_text(role.upper() or unit.unit_type.upper(), px + 76, py + ph - 32, role_col, font_size=9)

    # HP bar
    bw = pw - 88
    max_hp = max(1, unit.stats.max_hp) if unit.stats else 1
    hp_frac = max(0, min(1, unit.health / max_hp))
    arcade.draw_text("HP", px + 76, py + 42, palette.MUTED_TEXT, font_size=8)
    arcade.draw_lrbt_rectangle_filled(px + 96, px + 96 + bw, py + 38, py + 48, palette.PANEL_FILL)
    arcade.draw_lrbt_rectangle_filled(px + 96, px + 96 + int(bw * hp_frac), py + 38, py + 48, palette.TACTICAL_GREEN)
    arcade.draw_text(f"{unit.health}/{max_hp}", px + 96 + bw + 4, py + 38, palette.TACTICAL_GREEN, font_size=8)

    # AP dots
    max_ap = max(1, getattr(unit, "action_points", 1) + 1)
    ap_now = max(0, getattr(unit, "action_points", 0))
    arcade.draw_text("AP", px + 76, py + 22, palette.MUTED_TEXT, font_size=8)
    for i in range(max_ap):
        col = palette.ACCENT if i < ap_now else palette.PANEL_FILL
        arcade.draw_lrbt_rectangle_filled(px + 96 + i * 18, px + 110 + i * 18, py + 20, py + 30, col)
        arcade.draw_line(px + 96 + i * 18, py + 20, px + 110 + i * 18, py + 20, palette.PANEL_BORDER_MUTED, 1)

    # Stress (if character)
    if unit.character:
        stress = unit.character.stress
        arcade.draw_text(f"STRESS {stress}", px + 76, py + 6, palette.WARNING if stress >= 60 else palette.MUTED_TEXT, font_size=8)


def draw_target_lock_panel(
    width: int,
    target: Unit | None,
    attack_key: str,
    player: Unit | None,
) -> None:
    """Draw a target-lock info panel when the player is picking a target."""
    if target is None or player is None:
        return

    pw, ph = 260, 70
    px = width - pw - 14
    py = 54

    arcade.draw_lrbt_rectangle_filled(px, px + pw, py, py + ph, palette.PANEL_FILL_DARK)
    arcade.draw_line(px, py + ph, px + pw, py + ph, palette.DANGER, 2)

    target_name = (
        target.character.name if target.character
        else target.spec_ops_asset.name if target.spec_ops_asset
        else target.unit_type
    )
    arcade.draw_text("TARGET LOCK", px + 10, py + ph - 14, palette.DANGER, font_size=9, bold=True)
    arcade.draw_text(target_name.upper(), px + 10, py + ph - 28, palette.TEXT, font_size=11, bold=True)

    # Hit chance
    stat_map = {"melee": "str", "shoot": "agi", "psi": "psi"}
    sname = stat_map.get(attack_key, "str")
    atk   = getattr(player.stats, sname, 1) if player.stats else 1
    defense = target.stats.defense if target.stats else 1
    chance  = atk / (atk + max(1, defense))
    chance_pct = int(chance * 100)
    chance_col = (
        palette.TACTICAL_GREEN if chance_pct >= 70
        else palette.WARNING    if chance_pct >= 40
        else palette.DANGER
    )
    arcade.draw_text(f"HIT CHANCE  {chance_pct}%", px + 10, py + ph - 46, chance_col, font_size=11, bold=True)
    # Chance bar
    bw = pw - 20
    arcade.draw_lrbt_rectangle_filled(px + 10, px + 10 + bw, py + 10, py + 20, palette.PANEL_FILL)
    arcade.draw_lrbt_rectangle_filled(px + 10, px + 10 + int(bw * chance), py + 10, py + 20, chance_col)

    # Target HP
    target_hp  = target.health
    target_max = target.stats.max_hp if target.stats else 1
    arcade.draw_text(f"HP {target_hp}/{target_max}", px + bw - 30, py + 6, palette.DANGER, font_size=8)


def draw_objective_marker(objective, elapsed: float) -> None:
    """Draw an animated objective marker with status label."""
    if objective is None:
        return
    ox, oy = objective.position
    completed = getattr(objective, "completed", False)
    pulse = 0.7 + 0.3 * math.sin(elapsed * 2.2)

    col = palette.TACTICAL_GREEN if completed else palette.WARNING
    pcol = (*col[:3], int(180 * pulse))

    # Pulsing outer ring
    r = 24 + int(6 * pulse)
    for deg in range(0, 360, 10):
        a = math.radians(deg)
        b = math.radians(deg + 10)
        arcade.draw_line(
            ox + r * math.cos(a), oy + r * math.sin(a),
            ox + r * math.cos(b), oy + r * math.sin(b),
            pcol, 2,
        )

    # Inner fill
    arcade.draw_lrbt_rectangle_filled(ox - 12, ox + 12, oy - 12, oy + 12, (*col[:3], 80))
    arcade.draw_rect_outline(arcade.LBWH(ox - 16, oy - 16, 32, 32), col, border_width=2)

    # Label
    label = "OBJECTIVE COMPLETE" if completed else "OBJECTIVE"
    arcade.draw_text(
        label, ox, oy + 32, col,
        font_size=9, bold=True, anchor_x="center",
    )


def draw_mission_status_bar(
    width: int, height: int,
    mission_title: str,
    player_count: int,
    enemy_count: int,
    turn_number: int,
) -> None:
    """Compact status bar at the very top of the battle screen."""
    bh = 36
    arcade.draw_lrbt_rectangle_filled(0, width, height - bh, height, palette.PANEL_FILL_DARK)
    arcade.draw_line(0, height - bh, width, height - bh, palette.PANEL_BORDER, 2)

    cx = width // 2
    arcade.draw_text(
        mission_title.upper(), cx, height - bh // 2,
        palette.HEADER, font_size=12, bold=True,
        anchor_x="center", anchor_y="center",
    )
    arcade.draw_text(
        f"SQUAD {player_count}",
        cx - 240, height - bh // 2,
        palette.TACTICAL_GREEN, font_size=11,
        anchor_y="center",
    )
    arcade.draw_text(
        f"ENEMIES {enemy_count}",
        cx + 160, height - bh // 2,
        palette.DANGER, font_size=11,
        anchor_y="center",
    )
    arcade.draw_text(
        f"TURN {turn_number}",
        width - 80, height - bh // 2,
        palette.MUTED_TEXT, font_size=11,
        anchor_x="right", anchor_y="center",
    )
