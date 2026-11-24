"""CyberCity 2085 — Tactical Battle HUD (Overhaul).

Full XCOM2-style battle overlay:
  • Tactical grid with movement / attack range highlights
  • Pulsing active-unit selection ring with corner brackets
  • Unit labels (HP bar + name) above every sprite
  • Bottom portrait strip — all player units, active highlighted
  • Action bar above portrait strip — contextual action buttons
  • Phase banner — large animated turn indicator
  • Unit detail panel — bottom-left, active unit stats
  • Target-lock panel — shows hit-chance when picking a target
  • Objective marker — pulsing ring on mission goal
  • Mission status bar — top chrome
  • Attack flash — screen-edge flash on hit/miss
  • Floating damage numbers — pop-up text on hit/miss
  • In-battle pause overlay — Resume / Settings / Abandon
  • Combat log side panel — Tab-toggled event history
"""

from __future__ import annotations

import math
from collections import deque
from typing import TYPE_CHECKING, Literal

import arcade

from game.ui import palette
from game.combat.tactical_identity import EnemyIntent, build_enemy_intents
from game.agent_specializations import (
    signature_for_role, Stance, PsiState,
    update_unit_stance, update_unit_psi_state, default_stance_for_unit,
)

if TYPE_CHECKING:
    from game.unit import Unit

# ── Grid constants ──────────────────────────────────────────────────────────

CELL = 32           # pixels per tile
MOVE_RANGE = 1      # tiles per action point for movement preview
ATTACK_RANGE_DEFAULT = 4
MOVE_RANGE_CELL_SCALE = 0.5

# ── Palette aliases ──────────────────────────────────────────────────────────

_GRID_COL       = (50,  100, 130,  18)
_MOVE_COL       = (60,  160, 220,  28)
_MOVE_BLOCKED_COL = (255,  90,  90,  90)  # temporary debug overlay for blocked tiles
_PATH_BLOCK_TERRAIN_COL = (255,  80,  80,  62)
_PATH_BLOCK_OCCUPIED_COL = (255, 190,  80,  72)
_ATTACK_COL     = (255, 160,  60,  28)
_ACTIVE_COL     = (120, 232, 180)
_ENEMY_COL      = (255,  88,  76)
_PHASE_PLAYER   = palette.TACTICAL_GREEN
_PHASE_ENEMY    = palette.DANGER
_PHASE_END      = palette.MUTED_TEXT

# Portrait strip layout — must sit above the existing combat action bar (18 + 112 = 130)
_COMBAT_BAR_TOP = 130   # top edge of the existing draw_combat_action_bar panel
_STRIP_H        = 80    # height of the bottom portrait strip
_STRIP_CARD_W   = 70    # width per unit card in strip
_ACTION_BAR_H   = 36    # kept for status panel offset reference (small indicator bar)

_OVERWATCH_COL  = (255, 220, 60)    # yellow — matches XCOM's overwatch tint
_FOG_COL        = (0, 0, 0, 140)    # semi-transparent black fog tiles
_OVERWATCH_TRIGGER_COL = (255, 220, 60, 75)
_OVERWATCH_COVERAGE_COL = (255, 180, 60, 95)


def battle_shortcut_banner(input_mode: str, selecting_target: bool, pending_end_turn_confirmation: bool) -> str:
    """Build a compact contextual shortcuts banner for the battle HUD."""
    if input_mode == "controller":
        base = ["LS move", "A confirm", "B cancel", "X fire", "Y psi"]
        target = ["LB/RB target", "A confirm", "B back"]
        end_turn = ["A confirm end turn", "B cancel"]
    else:
        base = ["Arrow keys move", "E objective", "F fire", "P psi", "Enter end turn"]
        target = ["Left/Right target", "Enter confirm", "Esc back"]
        end_turn = ["Enter confirm end turn", "Esc cancel"]
    hints = end_turn if pending_end_turn_confirmation else (target if selecting_target else base)
    return "Active shortcuts: " + " | ".join(hints)


def _draw_footer_banner(width, text, color):
    arcade.draw_lrbt_rectangle_filled(0,width,0,18,(4,12,18,255))
    arcade.draw_line(0,18,width,18,palette.PANEL_BORDER_MUTED,1)
    arcade.draw_text(text,width//2,9,color,font_size=12,anchor_x="center",anchor_y="center")


def draw_battle_shortcut_banner(width: int, height: int, text: str) -> None:
    """Contextual controls in the reserved footer, away from header panels."""
    _draw_footer_banner(width,text,palette.TEXT)


def draw_action_aftermath_line(width: int, height: int, text: str | None) -> None:
    """Transient causal feedback replaces footer hints while active."""
    if text:
        _draw_footer_banner(width,text,palette.TACTICAL_GREEN)


def draw_enemy_intents(
    enemy_units: list["Unit"],
    player_units: list["Unit"],
    objective: object | None,
    elapsed: float,
    *,
    reserved_intents: list[EnemyIntent] | None = None,
    label_boxes=None,
    label_bounds=None,
) -> list[EnemyIntent]:
    """Draw reliable next-action telegraphs above visible enemies."""

    intents = reserved_intents if reserved_intents is not None else build_enemy_intents(enemy_units, player_units, objective=objective)
    pulse = 0.78 + 0.22 * math.sin(elapsed * 4.0)
    from game.ui.components.combat.world_labels import place_caption
    label_boxes = [] if label_boxes is None else label_boxes
    for intent in intents:
        if not getattr(intent.enemy, "visible", True) or intent.enemy.health <= 0:
            continue
        x, y = intent.enemy.position
        color = (*intent.color, int(230 * pulse))
        if intent.target is not None:
            tx, ty = intent.target.position
            arcade.draw_line(x, y, tx, ty, (*intent.color, 70), 1)
        if intent.coordinator is not None and getattr(intent.coordinator, "visible", True):
            cx, cy = intent.coordinator.position
            arcade.draw_line(x, y, cx, cy, (80, 190, 255, 100), 1)
        if intent.destination is not None:
            dx, dy = intent.destination
            arcade.draw_line(x, y, dx, dy, (*intent.color, 100), 1)
            arcade.draw_circle_outline(dx, dy, 6, (*intent.color, 180), 1)
        interrupted = "! " if intent.rationale.startswith("INTERRUPTED") else ""
        link = " [LINK]" if intent.coordinator is not None else ""
        target_name = intent.target_name.upper()
        if len(target_name) > 18:
            target_name = target_name[:15]+"..."
        label = f"{interrupted}{intent.action}  {target_name}{link}"
        hint = "2 AP / 30% CRIT - MOVE OR CUT SIGHT" if intent.action == "LOCK" else ""
        width = max(88, 16+len(label)*7, 16+len(hint)*6)
        box = place_caption(x, y+34, width, label_boxes,
                            height=40 if hint else 22, bounds=label_bounds)
        if box is None:
            continue
        left,bottom,right,top = box
        cx = (left+right)/2
        arcade.draw_line(x,y+16,cx,bottom,(*intent.color,160),1)
        arcade.draw_lrbt_rectangle_filled(left,right,bottom,top,(4,10,14,235))
        arcade.draw_lrbt_rectangle_outline(left,right,bottom,top,color,1)
        arcade.draw_text(label,cx,top-11,color,font_size=8,bold=True,
                         anchor_x="center",anchor_y="center")
        if hint:
            arcade.draw_text(hint,cx,bottom+6,color,font_size=7,anchor_x="center")
    return intents

# ══════════════════════════════════════════════════════════════════════════════
# Grid & range overlays
# ══════════════════════════════════════════════════════════════════════════════

def draw_tactical_grid(width: int, height: int, *, hud_height: int = 0) -> None:
    """Draw a faint cross-hatch grid over the whole map."""
    if hud_height > 0:
        # Limiter le dessin au-dessus du HUD pour éviter tout chevauchement
        height = height - hud_height
    for x in range(0, width + CELL, CELL):
        arcade.draw_line(x, 0, x, max(0, height), _GRID_COL, 1)
    for y in range(0, max(0, height) + CELL, CELL):
        arcade.draw_line(0, y, width, y, _GRID_COL, 1)


def _movement_reachable_cells(
    unit: "Unit",
    width: int,
    height: int,
    *,
    can_enter=None,
) -> set[tuple[int, int]]:
    """Return the tiles reachable with the remaining movement budget."""
    if not unit or not unit.position:
        return set()
    moves = max(0, getattr(unit, "action_points", 0)) * MOVE_RANGE
    start = unit.position
    reachable: set[tuple[int, int]] = {start}
    if moves <= 0:
        return reachable

    seen: set[tuple[int, int]] = {start}
    queue = deque([(start[0], start[1], 0)])
    while queue:
        x, y, steps = queue.popleft()
        if steps >= moves:
            continue
        for next_x, next_y in (
            (x + CELL, y),
            (x - CELL, y),
            (x, y + CELL),
            (x, y - CELL),
        ):
            if not (0 <= next_x < width and 0 <= next_y < height):
                continue
            if (next_x, next_y) in seen:
                continue
            if can_enter is not None and not can_enter(next_x, next_y):
                continue
            seen.add((next_x, next_y))
            reachable.add((next_x, next_y))
            queue.append((next_x, next_y, steps + 1))
    return reachable


def draw_movement_range(
    unit: "Unit",
    width: int,
    height: int,
    *,
    can_enter=None,
) -> None:
    """Highlight cells the active unit can reach with the remaining AP budget."""
    if not unit or not unit.position:
        return
    ux, uy = unit.position
    moves = max(0, getattr(unit, "action_points", 0)) * MOVE_RANGE
    reachable = _movement_reachable_cells(unit, width, height, can_enter=can_enter)
    for dx in range(-moves, moves + 1):
        for dy in range(-moves, moves + 1):
            if abs(dx) + abs(dy) <= moves:
                cx = ux + dx * CELL
                cy = uy + dy * CELL
                if 0 <= cx < width and 0 <= cy < height:
                    col = _MOVE_COL if (cx, cy) in reachable else _MOVE_BLOCKED_COL
                    inset = CELL * (1.0 - MOVE_RANGE_CELL_SCALE) * 0.5
                    arcade.draw_lrbt_rectangle_filled(
                        cx + inset,
                        cx + CELL - inset,
                        cy + inset,
                        cy + CELL - inset,
                        col,
                    )


def draw_path_blocking_overlay(
    terrain_profile,
    player_units: list["Unit"],
    enemy_units: list["Unit"],
    width: int,
    height: int,
) -> None:
    """Draw a whole-map overlay for blocked movement tiles."""
    if terrain_profile is None:
        return

    occupied: set[tuple[int, int]] = {
        unit.position
        for unit in [*player_units, *enemy_units]
        if unit and getattr(unit, "health", 0) > 0 and getattr(unit, "position", None)
    }
    for x in range(0, width + CELL, CELL):
        for y in range(0, height + CELL, CELL):
            cell = (x, y)
            if cell in occupied:
                arcade.draw_lrbt_rectangle_filled(
                    x, x + CELL, y, y + CELL, _PATH_BLOCK_OCCUPIED_COL
                )
            elif not terrain_profile.is_walkable(x, y):
                arcade.draw_lrbt_rectangle_filled(
                    x, x + CELL, y, y + CELL, _PATH_BLOCK_TERRAIN_COL
                )


def draw_attack_range(
    unit: "Unit", width: int, height: int, *, highlight: bool = False
) -> None:
    """Highlight cells within the unit's attack range (orange tint)."""
    if not unit or not unit.position:
        return
    ux, uy = unit.position
    r = getattr(unit, "attack_range", ATTACK_RANGE_DEFAULT) * CELL
    cells = int(r / CELL) + 1
    for dx in range(-cells, cells + 1):
        for dy in range(-cells, cells + 1):
            cx = ux + dx * CELL
            cy = uy + dy * CELL
            dist = math.sqrt(dx * dx + dy * dy) * CELL
            if dist <= r and 0 <= cx < width and 0 <= cy < height:
                col = (*_ATTACK_COL[:3], 44) if highlight else _ATTACK_COL
                arcade.draw_lrbt_rectangle_filled(cx, cx + CELL, cy, cy + CELL, col)


def overwatch_preview_cells(
    unit: "Unit",
    direction: tuple[int, int],
    width: int,
    height: int,
    *,
    reach_cells: int | None = None,
) -> tuple[list[tuple[int, int]], list[tuple[int, int]]]:
    """Return trigger and coverage cells for an overwatch orientation preview."""
    if not unit or not unit.position or direction == (0, 0):
        return ([], [])
    ux, uy = unit.position
    dx, dy = direction
    reach = reach_cells if reach_cells is not None else max(2, getattr(unit, "attack_range", ATTACK_RANGE_DEFAULT))
    trigger_cells: list[tuple[int, int]] = []
    coverage_cells: list[tuple[int, int]] = []
    for step in range(1, reach + 1):
        line_x = ux + dx * step * CELL
        line_y = uy + dy * step * CELL
        if not (0 <= line_x < width and 0 <= line_y < height):
            break
        trigger_cells.append((line_x, line_y))
        for offset in range(-step, step + 1):
            cone_x = line_x + (-dy) * offset * CELL
            cone_y = line_y + dx * offset * CELL
            if 0 <= cone_x < width and 0 <= cone_y < height:
                coverage_cells.append((cone_x, cone_y))
    return trigger_cells, coverage_cells


def draw_overwatch_preview(
    unit: "Unit",
    direction: tuple[int, int],
    width: int,
    height: int,
) -> None:
    """Render line/cone reaction coverage and trigger tiles for overwatch setup."""
    trigger_cells, coverage_cells = overwatch_preview_cells(unit, direction, width, height)
    for cx, cy in coverage_cells:
        arcade.draw_lrbt_rectangle_filled(cx, cx + CELL, cy, cy + CELL, _OVERWATCH_COVERAGE_COL)
    for cx, cy in trigger_cells:
        arcade.draw_lrbt_rectangle_filled(cx, cx + CELL, cy, cy + CELL, _OVERWATCH_TRIGGER_COL)
        arcade.draw_line(cx, cy, cx + CELL, cy, _OVERWATCH_COL, 1)
        arcade.draw_line(cx, cy + CELL, cx + CELL, cy + CELL, _OVERWATCH_COL, 1)
        arcade.draw_line(cx, cy, cx, cy + CELL, _OVERWATCH_COL, 1)
        arcade.draw_line(cx + CELL, cy, cx + CELL, cy + CELL, _OVERWATCH_COL, 1)

# ══════════════════════════════════════════════════════════════════════════════
# Cover nodes overlay
# ══════════════════════════════════════════════════════════════════════════════

def draw_access_lanes(cells) -> None:
    """Mark procedural traversable lanes where image inference was uncertain."""
    for x, y in cells:
        arcade.draw_lrbt_rectangle_filled(x - 10, x + 10, y - 10, y + 10, (75, 185, 205, 40))
        arcade.draw_line(x - 8, y - 8, x + 8, y - 8, (75, 185, 205, 130), 1)


def _draw_world_caption(text, x, y, color, occupied, bounds=None) -> None:
    from game.ui.components.combat.world_labels import place_caption
    width = max(100, len(text)*7+16)
    box = place_caption(x, y, width, occupied, bounds=bounds)
    if box is None:
        return
    left, bottom, right, top = box
    arcade.draw_line(x, y-4, (left+right)/2, bottom, (*color[:3], 170), 1)
    arcade.draw_lrbt_rectangle_filled(left, right, bottom, top, (4, 12, 18, 235))
    arcade.draw_line(left, bottom, right, bottom, color, 1)
    arcade.draw_text(text, (left+right)/2, bottom+6, color, font_size=8,
                     bold=True, anchor_x="center")


def draw_hazard_zones(zones, *, label_boxes=None, label_bounds=None) -> None:
    """Readable patterned zones with named consequences before commitment."""
    colors = {"fire": (255, 110, 45), "contamination": (150, 220, 65), "blackout": (175, 125, 255), "sludge": (140, 225, 65)}
    labels = {"fire": "FIRE -2 HP", "contamination": "TOXIC -1 HP", "blackout": "BLACKOUT -1 AP", "sludge": "SLUDGE -1 HP / -1 AP"}
    label_boxes = [] if label_boxes is None else label_boxes
    for zone in zones:
        x, y = zone.position
        radius = max(8, zone.radius_cells * CELL)
        col = colors[zone.kind]
        arcade.draw_circle_filled(x, y, radius, (*col, 35))
        arcade.draw_circle_outline(x, y, radius, (*col, 180), 2)
        arcade.draw_line(x - 8, y - 8, x + 8, y + 8, col, 2)
        arcade.draw_line(x - 8, y + 8, x + 8, y - 8, col, 2)
        _draw_world_caption(labels[zone.kind], x, y+radius+4, col, label_boxes, label_bounds)


def draw_cover_nodes(cover_nodes: list) -> None:
    """Draw low/high cover tiles on the battlefield grid.

    *cover_nodes* is a list of ``CoverNode`` from ``game.cover_system``.
    Colours come from ``game.cover_system.COVER_LOW_COL / COVER_HIGH_COL``.
    """
    if not cover_nodes:
        return
    from game.cover_system import COVER_LOW_COL, COVER_HIGH_COL
    blocked = {(node.grid_x, node.grid_y) for node in cover_nodes if not node.passable}
    for node in cover_nodes:
        col = COVER_HIGH_COL if node.cover_type == "high" else COVER_LOW_COL
        wx, wy = node.world_x, node.world_y
        if not node.passable:
            # Map geometry needs a quiet contour, not hundreds of filled tiles
            # concealing the background. Match the sampled cell centre.
            half = CELL / 2
            gx, gy = node.grid_x, node.grid_y
            border = (105, 180, 190, 75)
            if (gx - 1, gy) not in blocked:
                arcade.draw_line(wx-half, wy-half, wx-half, wy+half, border, 1)
            if (gx + 1, gy) not in blocked:
                arcade.draw_line(wx+half, wy-half, wx+half, wy+half, border, 1)
            if (gx, gy - 1) not in blocked:
                arcade.draw_line(wx-half, wy-half, wx+half, wy-half, border, 1)
            if (gx, gy + 1) not in blocked:
                arcade.draw_line(wx-half, wy+half, wx+half, wy+half, border, 1)
            continue
        arcade.draw_lrbt_rectangle_filled(wx, wx + CELL, wy, wy + CELL, col)
        # Outline via two line pairs (compatible with all arcade stubs)
        border = (*col[:3], min(255, col[3] + 80))
        arcade.draw_line(wx, wy, wx + CELL, wy, border, 1)
        arcade.draw_line(wx, wy + CELL, wx + CELL, wy + CELL, border, 1)
        arcade.draw_line(wx, wy, wx, wy + CELL, border, 1)
        arcade.draw_line(wx + CELL, wy, wx + CELL, wy + CELL, border, 1)
        # Small label for cover height
        label = "▮" if node.cover_type == "high" else "▯"
        arcade.draw_text(
            label,
            wx + CELL // 2, wy + CELL // 2,
            (*col[:3], 220),
            font_size=8,
            anchor_x="center", anchor_y="center",
            bold=True,
        )


# ══════════════════════════════════════════════════════════════════════════════
# Fog of war
# ══════════════════════════════════════════════════════════════════════════════

_FOG_SIGHT_RADIUS = 5   # cells a player unit can see


def draw_fog_of_war(
    player_units: list["Unit"],
    width: int,
    height: int,
) -> None:
    """Darken tiles outside any player unit's sight radius (simple radius fog).

    Enemy units inherit ``visible=False`` when outside this range; the caller
    is responsible for hiding their sprites from the draw list.
    """
    if not player_units:
        return
    cols = width  // CELL + 1
    rows = height // CELL + 1

    # Pre-compute which cells are visible (any player within _FOG_SIGHT_RADIUS)
    visible: set[tuple[int, int]] = set()
    for u in player_units:
        ux = u.position[0] // CELL
        uy = u.position[1] // CELL
        for dx in range(-_FOG_SIGHT_RADIUS, _FOG_SIGHT_RADIUS + 1):
            for dy in range(-_FOG_SIGHT_RADIUS, _FOG_SIGHT_RADIUS + 1):
                if dx * dx + dy * dy <= _FOG_SIGHT_RADIUS * _FOG_SIGHT_RADIUS:
                    visible.add((ux + dx, uy + dy))

    for col in range(cols):
        for row in range(rows):
            if (col, row) not in visible:
                arcade.draw_lrbt_rectangle_filled(
                    col * CELL, col * CELL + CELL,
                    row * CELL, row * CELL + CELL,
                    _FOG_COL,
                )


def update_enemy_visibility(
    player_units: list["Unit"],
    enemy_units: list["Unit"],
) -> None:
    """Mark each enemy unit visible/hidden based on player line-of-sight range."""
    for enemy in enemy_units:
        ex = enemy.position[0] // CELL
        ey = enemy.position[1] // CELL
        enemy.visible = any(
            (px // CELL - ex) ** 2 + (py // CELL - ey) ** 2 <= _FOG_SIGHT_RADIUS ** 2
            for u in player_units
            for px, py in [u.position]
        )


# ══════════════════════════════════════════════════════════════════════════════
# Active-unit ring
# ══════════════════════════════════════════════════════════════════════════════

def draw_active_unit_ring(unit: "Unit", elapsed: float) -> None:
    """Draw a pulsing XCOM-style selection ring around the active player unit."""
    if not unit or not unit.sprite:
        return
    cx = unit.sprite.center_x
    cy = unit.sprite.center_y
    r  = max(20, unit.sprite.width // 2 + 6)
    pulse = 0.7 + 0.3 * math.sin(elapsed * 3.0)
    alpha = int(220 * pulse)
    col   = (*_ACTIVE_COL, alpha)

    # Outer dashed ring
    for angle_deg in range(0, 360, 6):
        a = math.radians(angle_deg)
        b = math.radians(angle_deg + 4)   # leave 2° gap for dashes
        arcade.draw_line(
            cx + r * math.cos(a), cy + r * math.sin(a),
            cx + r * math.cos(b), cy + r * math.sin(b),
            col, 2,
        )

    # Corner brackets (XCOM style)
    bracket = 12
    corners = [(-r, -r), (r, -r), (r, r), (-r, r)]
    segs = [
        [(0, bracket), (0, 0), (bracket, 0)],
        [(-bracket, 0), (0, 0), (0, bracket)],
        [(0, -bracket), (0, 0), (-bracket, 0)],
        [(bracket, 0), (0, 0), (0, -bracket)],
    ]
    bracket_col = (*palette.HEADER[:3], 200)
    for (ox, oy), pts in zip(corners, segs):
        for i in range(len(pts) - 1):
            ax, ay = pts[i]
            bx, by = pts[i + 1]
            arcade.draw_line(
                cx + ox + ax, cy + oy + ay,
                cx + ox + bx, cy + oy + by,
                bracket_col, 2,
            )


# ══════════════════════════════════════════════════════════════════════════════
# Unit labels (HP bar + name above sprite)
# ══════════════════════════════════════════════════════════════════════════════

def draw_unit_labels(
    player_units: list["Unit"],
    enemy_units:  list["Unit"],
    active_index: int,
    *, label_boxes=None, label_bounds=None,
) -> None:
    """Draw HP bars and role labels above every unit sprite."""
    label_boxes = [] if label_boxes is None else label_boxes
    ordered = sorted(enumerate(player_units), key=lambda item: item[0] != active_index)
    for i, unit in ordered:
        if not unit.sprite or not unit.stats:
            continue
        _draw_unit_bar(unit, active=(i == active_index), is_enemy=False, label_boxes=label_boxes, label_bounds=label_bounds)
    for unit in enemy_units:
        if not unit.sprite or not unit.stats:
            continue
        _draw_unit_bar(unit, active=False, is_enemy=True, label_boxes=label_boxes, label_bounds=label_bounds)


def _draw_unit_bar(unit: "Unit", *, active: bool, is_enemy: bool, label_boxes=None, label_bounds=None) -> None:
    # Never draw labels/HP bar for enemies hidden in fog of war
    if is_enemy and not getattr(unit, "visible", True):
        return
    anchor_x = unit.sprite.center_x
    anchor_y = unit.sprite.center_y + unit.sprite.height // 2 + 4
    name = (unit.character.name.split()[0] if unit.character else
            unit.spec_ops_asset.name if unit.spec_ops_asset else unit.unit_type).upper()
    if len(name) > 18:
        name = name[:15]+"..."
    if getattr(unit, "on_overwatch", False):
        name += " / OW"
    statuses = getattr(unit, "status_effects", [])
    subtype = getattr(unit, "enemy_subtype", "") if is_enemy else ""
    subtype_height = 12 if subtype and subtype != "grunt" else 0
    bw = max(64, min(100, unit.sprite.width+12), len(name)*7+8, len(statuses)*24+8)
    from game.ui.components.combat.world_labels import place_caption
    boxes = [] if label_boxes is None else label_boxes
    box = place_caption(
        anchor_x, anchor_y-subtype_height-3, bw, boxes,
        height=30+subtype_height+(14 if statuses else 0), bounds=label_bounds)
    if box is None:
        return
    left, bottom, right, plate_top = box
    cx = (left+right)/2
    top = bottom+subtype_height+3
    arcade.draw_line(anchor_x, anchor_y, cx, bottom, palette.PANEL_BORDER_MUTED, 1)
    arcade.draw_lrbt_rectangle_filled(left, right, bottom, plate_top, (4, 12, 18, 225))
    bh   = 6
    lx   = cx - bw // 2
    rx   = cx + bw // 2

    hp_frac = max(0, min(1, unit.health / max(1, unit.stats.max_hp)))
    hp_col  = _ENEMY_COL if is_enemy else _ACTIVE_COL

    # HP bar
    arcade.draw_lrbt_rectangle_filled(lx, rx, top, top + bh, palette.PANEL_FILL_DARK)
    arcade.draw_lrbt_rectangle_filled(lx, lx + int(bw * hp_frac), top, top + bh, hp_col)
    arcade.draw_line(lx, top,      rx, top,      palette.PANEL_BORDER_MUTED, 1)
    arcade.draw_line(lx, top + bh, rx, top + bh, palette.PANEL_BORDER_MUTED, 1)

    # Name
    name_col = palette.HEADER if active else (
        palette.DANGER if is_enemy else palette.MUTED_TEXT
    )
    arcade.draw_text(name, cx, top+bh+3, name_col, font_size=8, bold=active, anchor_x="center")

    # Enemy subtype label (grunt / heavy / elite / commander) — shown below HP bar
    if is_enemy:
        subtype = getattr(unit, "enemy_subtype", "")
        if subtype and subtype != "grunt":
            arcade.draw_text(
                subtype.upper(),
                cx, bottom+2,
                (*palette.DANGER[:3], 180),
                font_size=7, anchor_x="center",
            )

    # Status effect badges (suppressed / bleeding / stunned / burning / contaminated / panicked)
    status_effects = getattr(unit, "status_effects", [])
    _STATUS_BADGES = {
        "suppressed": ("SUP", (255, 200, 50)),
        "bleeding":   ("BLD", (220, 60, 60)),
        "stunned":    ("STN", (160, 120, 255)),
        "burning":    ("BRN", (255, 110, 40)),
        "contaminated": ("CON", (90, 220, 120)),
        "panicked":   ("PAN", (255, 120, 220)),
    }
    badge_x = cx - 12 * (len(status_effects) - 1)
    for effect in status_effects:
        badge_label, badge_col = _STATUS_BADGES.get(effect, (effect[:3].upper(), palette.WARNING))
        arcade.draw_text(
            badge_label,
            badge_x, top + bh + 18,
            (*badge_col, 230),
            font_size=7, bold=True, anchor_x="center",
        )
        badge_x += 24


# ══════════════════════════════════════════════════════════════════════════════
# Portrait strip — bottom edge, shows all player units
# ══════════════════════════════════════════════════════════════════════════════

def unit_status_panel_visible(width, unit_count):
    total = unit_count*_STRIP_CARD_W + max(0,unit_count-1)*4
    return total <= width-340


def draw_unit_portrait_strip(
    player_units: list["Unit"],
    active_index: int,
    width: int,
    elapsed: float,
) -> None:
    """Bottom strip: one card per player unit with portrait, HP, AP dots, name.
    
    Positioned above the combat action bar (combat_action_bar_rect).
    The action bar goes from bottom=18 to bottom+112=Y=130.
    This strip goes from Y=130 to Y=130+80=Y=210, fitting within the HUD area.
    """
    if not player_units:
        return

    strip_y = _COMBAT_BAR_TOP  # Aligned with action bar top edge (Y=130)
    n       = len(player_units)
    total_w = n * _STRIP_CARD_W + (n - 1) * 4
    start_x = (width - total_w) // 2
    if unit_status_panel_visible(width,n):
        start_x = max(324,start_x)

    # Strip background
    arcade.draw_lrbt_rectangle_filled(
        start_x - 8, start_x + total_w + 8,
        strip_y, strip_y + _STRIP_H,
        (0, 0, 0, 190),
    )
    arcade.draw_line(
        start_x - 8, strip_y + _STRIP_H,
        start_x + total_w + 8, strip_y + _STRIP_H,
        palette.PANEL_BORDER, 2,
    )

    for i, unit in enumerate(player_units):
        cx  = start_x + i * (_STRIP_CARD_W + 4)
        active = (i == active_index)
        pulse  = 0.8 + 0.2 * math.sin(elapsed * 4.0) if active else 1.0

        # Role colour
        role = unit.character.role if unit.character else ""
        role_col = {
            "sniper": palette.ROLE_SNIPER,
            "psi":    palette.ROLE_PSI,
        }.get(role, palette.ROLE_SAMURAI)

        # Card fill
        fill = (32, 75, 98, 230) if active else (8, 18, 24, 210)
        arcade.draw_lrbt_rectangle_filled(cx, cx + _STRIP_CARD_W, strip_y + 2, strip_y + _STRIP_H - 2, fill)
        # Active top border
        border_col = (*role_col[:3], int(220 * pulse)) if active else palette.PANEL_BORDER_MUTED
        arcade.draw_line(cx, strip_y + _STRIP_H - 2, cx + _STRIP_CARD_W, strip_y + _STRIP_H - 2, border_col, 2)

        # Portrait area
        pp = 36
        px, py = cx + 4, strip_y + _STRIP_H - 6 - pp
        arcade.draw_lrbt_rectangle_filled(px, px + pp, py, py + pp, palette.AGENT_PORTRAIT_FILL)
        arcade.draw_line(px, py + pp, px + pp, py + pp, role_col, 2)

        # Try to load portrait texture
        if unit.character:
            from game.ui.portraits import portrait_path_for_character
            from game.ui.panels import _load_texture_once
            ppath = portrait_path_for_character(unit.character)
            tex   = _load_texture_once(ppath) if ppath else None
            if tex:
                arcade.draw_texture_rect(tex, arcade.LBWH(px, py, pp, pp))

        # HP bar (below portrait)
        hp_frac = max(0.0, min(1.0, unit.health / max(1, unit.stats.max_hp if unit.stats else 1)))
        bw = _STRIP_CARD_W - 8
        bar_y = strip_y + 20
        arcade.draw_lrbt_rectangle_filled(cx + 4, cx + 4 + bw, bar_y, bar_y + 6, palette.PANEL_FILL_DARK)
        hp_col = palette.TACTICAL_GREEN if hp_frac > 0.5 else (palette.WARNING if hp_frac > 0.25 else palette.DANGER)
        arcade.draw_lrbt_rectangle_filled(cx + 4, cx + 4 + int(bw * hp_frac), bar_y, bar_y + 6, hp_col)

        # AP dots
        max_ap = max(1, getattr(unit, "action_points", 1) + 1)
        ap_now = max(0, getattr(unit, "action_points", 0))
        dot_y  = strip_y + 10
        dot_w  = min(10, (bw - 2) // max(1, max_ap))
        for d in range(max_ap):
            col = palette.ACCENT if d < ap_now else (18, 36, 48)
            arcade.draw_lrbt_rectangle_filled(
                cx + 4 + d * (dot_w + 2), cx + 4 + d * (dot_w + 2) + dot_w,
                dot_y, dot_y + 7, col,
            )

        # Name (right of portrait)
        tx = cx + 4
        name = ""
        if unit.character:
            name = unit.character.name.split()[0].upper()[:9]
        elif unit.spec_ops_asset:
            name = unit.spec_ops_asset.name[:9].upper()
        else:
            name = unit.unit_type.upper()[:5]
        arcade.draw_text(
            name, tx, strip_y + 28,
            palette.TEXT if active else palette.MUTED_TEXT,
            font_size=8, bold=active,
        )
        # Dead / recovering indicator
        if unit.health <= 0:
            arcade.draw_lrbt_rectangle_filled(cx, cx + _STRIP_CARD_W, strip_y + 2, strip_y + _STRIP_H - 2, (180, 0, 0, 80))
            arcade.draw_text("KIA", cx + _STRIP_CARD_W // 2, strip_y + _STRIP_H // 2, palette.DANGER, font_size=9, bold=True, anchor_x="center", anchor_y="center")
        
        # Role signature indicator — drawn after portrait/name for all roles
        draw_role_signature_indicator(unit, cx, strip_y, elapsed)


# ─═══════════════════════════════════════════════════════════════════════════
# Role signature indicators — Visual identity for each role tree
# ════════════════════════════════════════════════════════════════════════════

def draw_role_signature_indicator(
    unit: "Unit",
    cx: int,
    strip_y: int,
    elapsed: float,
) -> None:
    """Draw role-specific visual signature above the portrait card."""
    sig = signature_for_role(unit.character.role if unit.character else "")
    if not sig:
        return
    
    # Get current stance/state for mode-based visuals
    active_stance = (
        getattr(unit, "stance", None) or update_unit_stance(unit)
    )
    active_psi = (
        getattr(unit, "psi_state", None) or update_unit_psi_state(unit)
    )
    
    # Portrait center for drawing indicators
    portrait_center_x = cx + _STRIP_CARD_W - 12
    portrait_center_y = strip_y + 15
    num_points = 8
    
    # ─────────────────────────────────────────────────────────────────────────
    # SAMURAI: Breach/Guard stance indicator
    # ─────────────────────────────────────────────────────────────────────────
    if sig.key == "samurai":
        # Stance ring above portrait
        stance_color = sig.mode_colors.get(
            getattr(active_stance, "value", str(active_stance)),
            (200, 200, 200)
        )
        
        # Outer glow ring with pulse
        pulse = 1.0 + 0.15 * math.sin(elapsed * 8.0)
        ring_radius = int(8 / pulse) + 1
        
        # Draw circle as line segments (arcade doesn't have native circles)
        num_points = 8
        
        for i in range(num_points):
            angle = math.pi * 2 * i / num_points
            next_i = (i + 1) % num_points
            px = int(portrait_center_x + ring_radius * math.cos(angle))
            py = int(portrait_center_y + ring_radius * math.sin(angle))
            nx = int(portrait_center_x + ring_radius * math.cos(math.pi * 2 * next_i / num_points))
            ny = int(portrait_center_y + ring_radius * math.sin(math.pi * 2 * next_i / num_points))
            arcade.draw_line(px, py, nx, ny, stance_color, 1.5)
        
        # Mode label above portrait
        mode_label = getattr(active_stance, "value", str(active_stance)).upper()
        arcade.draw_text(
            mode_label,
            cx + _STRIP_CARD_W - 4,
            strip_y + _STRIP_H - 16,
            stance_color,
            font_size=6,
            bold=True,
            anchor_x="right",
        )
    
    # ─────────────────────────────────────────────────────────────────────────
    # PSY: Control/Risk state indicator  
    # ─────────────────────────────────────────────────────────────────────────
    elif sig.key == "psi":
        psi_color = sig.mode_colors.get(
            getattr(active_psi, "value", str(active_psi)),
            (200, 200, 200)
        )
        
        # Pulsing ring indicating psychic activity
        pulse = 1.0 + 0.1 * math.sin(elapsed * 10.0) if active_psi == PsiState.RISK else 1.0
        
        # Draw outer pulsing ring
        ring_radius = int(8 / pulse) + 1
        
        for i in range(num_points):
            angle = math.pi * 2 * i / num_points
            next_i = (i + 1) % num_points
            px = int(portrait_center_x + ring_radius * math.cos(angle))
            py = int(portrait_center_y + ring_radius * math.sin(angle))
            nx = int(portrait_center_x + ring_radius * math.cos(math.pi * 2 * next_i / num_points))
            ny = int(portrait_center_y + ring_radius * math.sin(math.pi * 2 * next_i / num_points))
            arcade.draw_line(px, py, nx, ny, psi_color, 1.5)
        
        # Inner core with psi symbol hint (concentric circle)
        inner_radius = 3
        
        for i in range(num_points):
            angle = math.pi * 2 * i / num_points
            next_i = (i + 1) % num_points
            px = int(portrait_center_x + inner_radius * math.cos(angle))
            py = int(portrait_center_y + inner_radius * math.sin(angle))
            nx = int(portrait_center_x + inner_radius * math.cos(math.pi * 2 * next_i / num_points))
            ny = int(portrait_center_y + inner_radius * math.sin(math.pi * 2 * next_i / num_points))
            arcade.draw_line(px, py, nx, ny, sig.secondary_color, 1)
        
        # State indicator below name area
        state_label = "CONTROL" if active_psi == PsiState.CONTROL else "RISK"
        stress_color = psi_color if active_psi == PsiState.CONTROL else (255, 50, 50)
        arcade.draw_text(
            state_label,
            cx + _STRIP_CARD_W - 4,
            strip_y + _STRIP_H - 16,
            stress_color,
            font_size=5,
            anchor_x="right",
        )
    
    # ─────────────────────────────────────────────────────────────────────────
    # SNIPER: Scope/Overwatch indicator
    # ─────────────────────────────────────────────────────────────────────────
    elif sig.key == "sniper":
        overwatch_active = getattr(unit, "overwatching", False) or bool(getattr(unit, "_pending_overwatch", []))
        
        scope_color = (150, 230, 80) if overwatch_active else sig.accent_color
        
        # Crosshair-style indicator centered on portrait
        # Draw crosshair as lines through portrait center
        arcade.draw_line(
            portrait_center_x - 6, portrait_center_y, portrait_center_x + 6, portrait_center_y,
            scope_color, 2
        )
        arcade.draw_line(
            portrait_center_x, portrait_center_y - 5, portrait_center_x, portrait_center_y + 5,
            (int(c) for c in scope_color), 1.5
        )
        
        # Overwatch status indicator below
        if overwatch_active:
            arcade.draw_lrbt_rectangle_filled(
                portrait_center_x - 6, portrait_center_x + 4,
                strip_y + _STRIP_H - 10,
                strip_y + _STRIP_H - 3,
                (50, 180, 50)  # green active status
            )
            arcade.draw_text(
                "OW",
                portrait_center_x,
                strip_y + _STRIP_H - 6,
                (50, 180, 50),
                font_size=6,
                anchor_x="right",
            )
    
    # ─────────────────────────────────────────────────────────────────────────
    # MEDIC: Stabilization indicator
    # ─────────────────────────────────────────────────────────────────────────
    elif sig.key == "medic":
        is_stabilizing = getattr(unit, "stabilizing", False)
        
        med_color = (200, 180, 80) if is_stabilizing else (60, 200, 100)
        
        # Cross symbol for medic at portrait center
        arcade.draw_line(
            portrait_center_x - 4, portrait_center_y, portrait_center_x + 4, portrait_center_y,
            med_color, 2
        )
        arcade.draw_line(
            portrait_center_x, portrait_center_y - 3, portrait_center_x, portrait_center_y + 3,
            (int(c) for c in med_color), 1.5
        )
    
    # ─────────────────────────────────────────────────────────────────────────
    # ROBOT: Heat/Asset status
    # ─────────────────────────────────────────────────────────────────────────
    elif sig.key == "robot":
        heat = getattr(unit, "heat", 0)
        heat_pct = min(1.0, heat / max(1, getattr(unit.stats, "max_heat", 100)))
        
        # Thermal gradient ring
        temp_color = (255, 100, 80) if heat_pct > 0.7 else (255, 200, 80) if heat_pct > 0.4 else (180, 220, 60)
        
        ring_w = int(36 * heat_pct) + 2
        
        # Draw thermal ring at portrait center
        for i in range(num_points):
            angle = math.pi * 2 * i / num_points
            px = int(portrait_center_x + ring_w * math.cos(angle))
            py = int(portrait_center_y + ring_w * math.sin(angle))
            nx = int(portrait_center_x + ring_w * math.cos(math.pi * 2 * next_i / num_points))
            ny = int(portrait_center_y + ring_w * math.sin(math.pi * 2 * next_i / num_points))
            arcade.draw_line(px, py, nx, ny, temp_color, 1.5)


# ════════════════════════════════════════════════════════════════════════════
# Combat actions — movement, attack, abilities
# ════════════════════════════════════════════════════════════════════════════

def arc_draw_lrbt_circle_filled(center_x: int, center_y: int, radius: int, color: tuple[int, int, int]) -> None:
    """Helper to draw a filled circle using arcade's LRBTR rectangle (arcade doesn't have built-in circle fill)."""
    # Approximate circle with polygon - 8 points for smooth look
    num_points = 8
    x_center = center_x
    y_center = center_y
    
    for i in range(num_points):
        angle = math.pi * 2 * i / num_points
        px = int(x_center + radius * math.cos(angle))
        py = int(y_center + radius * math.sin(angle))
        next_i = (i + 1) % num_points
        nx = int(x_center + radius * math.cos(math.pi * 2 * next_i / num_points))
        ny = int(y_center + radius * math.sin(math.pi * 2 * next_i / num_points))
        
        # Draw line segments approximating the circle
        arcade.draw_line(px, py, nx, ny, color, 1)


# ══════════════════════════════════════════════════════════════════════════════
# Action bar — contextual buttons above the portrait strip
# ══════════════════════════════════════════════════════════════════════════════

def draw_action_bar(
    width: int,
    actions: list[str],
    active_action: str,
    elapsed: float,
) -> None:
    """Draw clickable action buttons above the portrait strip."""
    if not actions:
        return

    # Thin active-action indicator strip — sits at the very bottom, below the combat bar
    bar_y = 0
    arcade.draw_lrbt_rectangle_filled(0, width, bar_y, bar_y + _ACTION_BAR_H, (0, 0, 0, 160))
    arcade.draw_line(0, bar_y + _ACTION_BAR_H, width, bar_y + _ACTION_BAR_H, palette.PANEL_BORDER_MUTED, 1)

    btn_w = min(176, width // max(1, len(actions)))
    total = btn_w * len(actions) + (len(actions) - 1) * 4
    bx    = (width - total) // 2

    for act in actions:
        active = act == active_action
        pulse  = 0.85 + 0.15 * math.sin(elapsed * 3.5) if active else 1.0
        fill   = (22, 58, 28, 230) if active else (8, 20, 28, 200)
        col    = (*palette.TACTICAL_GREEN[:3], int(230 * pulse)) if active else palette.ACCENT
        arcade.draw_lrbt_rectangle_filled(bx, bx + btn_w, bar_y + 4, bar_y + _ACTION_BAR_H - 4, fill)
        arcade.draw_line(bx, bar_y + _ACTION_BAR_H - 4, bx + btn_w, bar_y + _ACTION_BAR_H - 4, col, 2 if active else 1)
        arcade.draw_text(
            act.upper(), bx + btn_w // 2, bar_y + _ACTION_BAR_H // 2,
            col, font_size=11, bold=active,
            anchor_x="center", anchor_y="center",
        )
        bx += btn_w + 4


# ══════════════════════════════════════════════════════════════════════════════
# Attack flash — screen edge bleed on hit or miss
# ══════════════════════════════════════════════════════════════════════════════

def draw_attack_flash(
    width: int, height: int,
    hit: bool,
    flash_alpha: int,
) -> None:
    """Draw a restrained red edge cue for incoming damage.

    *flash_alpha* should be driven externally and fade over ~0.4 s.
    Call with flash_alpha=0 to skip drawing entirely.
    """
    if flash_alpha <= 0 or hit:
        return
    col = (*palette.DANGER[:3], min(60, flash_alpha))
    edge = 8
    arcade.draw_lrbt_rectangle_filled(0,         edge,    0, height, col)
    arcade.draw_lrbt_rectangle_filled(width-edge, width,  0, height, col)
    arcade.draw_lrbt_rectangle_filled(0,  width, 0,          edge,   col)
    arcade.draw_lrbt_rectangle_filled(0,  width, height-edge, height, col)


# ══════════════════════════════════════════════════════════════════════════════
# Phase banner
# ══════════════════════════════════════════════════════════════════════════════

def draw_phase_banner(
    width: int, height: int, turn: str, turn_number: int, elapsed: float
) -> None:
    """Draw a prominent turn/phase indicator — top-right corner with dot track."""
    if turn == "player":
        label = "PLAYER TURN"
        color = _PHASE_PLAYER
        pulse = 0.9 + 0.1 * math.sin(elapsed * 2.0)
    elif turn == "enemy":
        label = "ENEMY TURN"
        color = _PHASE_ENEMY
        pulse = 0.8 + 0.2 * math.sin(elapsed * 3.0)
    else:
        label = "MISSION END"
        color = _PHASE_END
        pulse = 1.0

    # Background pill
    pill_w, pill_h = 230, 32
    px = width - pill_w - 12
    py = height - 84
    arcade.draw_lrbt_rectangle_filled(px, px + pill_w, py, py + pill_h, (0, 0, 0, 190))
    arcade.draw_line(px, py + pill_h, px + pill_w, py + pill_h, (*color[:3], int(200 * pulse)), 2)
    arcade.draw_line(px, py, px + 24, py, color, 1)

    # XCOM notch top-left
    arcade.draw_line(px, py + pill_h, px + 18, py + pill_h - 18, color, 2)

    # Phase label
    arcade.draw_text(
        label,
        px + pill_w - 12, py + pill_h // 2,
        (*color[:3], int(230 * pulse)),
        font_size=13, bold=True,
        anchor_x="right", anchor_y="center",
    )

    arcade.draw_lrbt_rectangle_filled(px+14,px+22,py+12,py+20,(*color[:3],int(220*pulse)))


def draw_unit_status_panel(
    _width: int, _height: int, unit: "Unit | None", turn: str
) -> None:
    """Active stats in the upper lower-HUD row, beside the squad portrait strip."""
    pw = 300
    ph = 80
    px = 12
    py = _COMBAT_BAR_TOP

    # Top border colour indicates whose turn it is
    turn_col = _PHASE_PLAYER if turn == "player" else (_PHASE_ENEMY if turn == "enemy" else _PHASE_END)

    # Background
    arcade.draw_lrbt_rectangle_filled(px, px + pw, py, py + ph, (0, 0, 0, 200))
    arcade.draw_line(px, py + ph, px + pw, py + ph, turn_col, 2)
    arcade.draw_line(px, py, px + pw, py, palette.PANEL_BORDER_MUTED, 1)
    arcade.draw_line(px, py, px, py + ph, palette.PANEL_BORDER_MUTED, 1)
    arcade.draw_line(px + pw, py, px + pw, py + ph, palette.PANEL_BORDER_MUTED, 1)
    # Corner notch
    notch = 14
    arcade.draw_line(px + pw, py + ph, px + pw - notch, py + ph - notch, turn_col, 2)

    if unit is None:
        arcade.draw_text(
            "NO ACTIVE UNIT",
            px + pw // 2, py + ph // 2,
            palette.MUTED_TEXT, font_size=12,
            anchor_x="center", anchor_y="center",
        )
        return

    role = unit.character.role if unit.character else ""
    role_col = {
        "sniper": palette.ROLE_SNIPER,
        "psi":    palette.ROLE_PSI,
    }.get(role, palette.ROLE_SAMURAI)

    # Portrait
    pp = 54
    arcade.draw_lrbt_rectangle_filled(px + 8, px + 8 + pp, py + 12, py + 12 + pp, palette.AGENT_PORTRAIT_FILL)
    arcade.draw_line(px + 8, py + 12 + pp, px + 8 + pp, py + 12 + pp, role_col, 2)

    # Load portrait texture
    if unit.character:
        from game.ui.portraits import portrait_path_for_character
        from game.ui.panels import _load_texture_once
        ppath = portrait_path_for_character(unit.character)
        tex   = _load_texture_once(ppath) if ppath else None
        if tex:
            arcade.draw_texture_rect(tex, arcade.LBWH(px + 8, py + 12, pp, pp))

    # Name + role
    name = (
        unit.character.name if unit.character
        else unit.spec_ops_asset.name if unit.spec_ops_asset
        else unit.unit_type
    )
    arcade.draw_text(name.upper()[:20], px + pp + 18, py + ph - 16, palette.TEXT, font_size=13, bold=True)
    arcade.draw_text(role.upper() or unit.unit_type.upper(), px + pp + 18, py + ph - 30, role_col, font_size=10)

    # HP bar
    bw = pw - pp - 84
    max_hp   = max(1, unit.stats.max_hp) if unit.stats else 1
    hp_frac  = max(0.0, min(1.0, unit.health / max_hp))
    hp_col   = palette.TACTICAL_GREEN if hp_frac > 0.5 else (palette.WARNING if hp_frac > 0.25 else palette.DANGER)
    arcade.draw_text("HP", px + pp + 18, py + 36, palette.MUTED_TEXT, font_size=9)
    arcade.draw_lrbt_rectangle_filled(px + pp + 32, px + pp + 32 + bw, py + 34, py + 42, palette.PANEL_FILL)
    arcade.draw_lrbt_rectangle_filled(px + pp + 32, px + pp + 32 + int(bw * hp_frac), py + 34, py + 42, hp_col)
    arcade.draw_text(f"{unit.health}/{max_hp}", px + pp + 34 + bw, py + 34, hp_col, font_size=9)

    # AP pips
    max_ap = max(1, getattr(unit, "action_points", 1) + 1)
    ap_now  = max(0, getattr(unit, "action_points", 0))
    arcade.draw_text("AP", px + pp + 18, py + 20, palette.MUTED_TEXT, font_size=9)
    for i in range(max_ap):
        col = palette.ACCENT if i < ap_now else (18, 36, 48, 200)
        arcade.draw_lrbt_rectangle_filled(
            px + pp + 32 + i * 20, px + pp + 48 + i * 20, py + 18, py + 29, col
        )
        arcade.draw_line(px + pp + 32 + i * 20, py + 18, px + pp + 48 + i * 20, py + 18, palette.PANEL_BORDER_MUTED, 1)

    # Stress & defense
    if unit.character:
        stress     = unit.character.stress
        stress_col = palette.DANGER if stress >= 70 else (palette.WARNING if stress >= 40 else palette.MUTED_TEXT)
        arcade.draw_text(f"STRESS {stress:>3}%", px + pp + 18, py + 4, stress_col, font_size=9)
    if unit.stats:
        arcade.draw_text(f"DEF {unit.stats.defense}", px + pw - 60, py + 4, palette.MUTED_TEXT, font_size=9)


# ══════════════════════════════════════════════════════════════════════════════
# Target-lock panel
# ══════════════════════════════════════════════════════════════════════════════

def target_lock_bounds(width):
    left, bottom = width-290-14, _COMBAT_BAR_TOP+_STRIP_H+12
    return left, bottom, left+290, bottom+96


def combat_log_bounds(width, height, max_lines=8):
    left, bottom = width-260-8, (height-(max_lines*18+44))//2
    return left, bottom, left+260, bottom+max_lines*18+44


def battlefield_hud_regions(width, height, *, target_lock=False, show_log=False,
                            objective_visible=False, timeline_slots=0):
    """Actual opaque HUD regions shared by pointer and caption layout."""
    regions = [(0,0,width,_COMBAT_BAR_TOP+_STRIP_H), (0,height-38,width,height),
               (14,height-92,min(width-14,534),height-46),
               (width-242,height-84,width-12,height-52)]
    if objective_visible:
        regions.append((14,height-188,364,height-112))
    if timeline_slots and not show_log and not target_lock:
        regions.append((width-334,height-92-34-30*timeline_slots,width-14,height-92))
    if target_lock:
        regions.append(target_lock_bounds(width))
    if show_log and not target_lock:
        regions.append(combat_log_bounds(width,height))
    return regions


def hud_blocks_battlefield_pointer(width, height, x, y, **context):
    regions = battlefield_hud_regions(width, height, **context)
    return any(left<=x<=right and bottom<=y<=top for left,bottom,right,top in regions)


def draw_target_lock_panel(
    width: int,
    target: "Unit | None",
    attack_key: str,
    player: "Unit | None",
    *,
    preview=None,
) -> None:
    """Draw a target-lock info panel when the player is picking a target."""
    if target is None or player is None:
        return

    px, py, right, top = target_lock_bounds(width)
    pw, ph = right-px, top-py

    arcade.draw_lrbt_rectangle_filled(px, px + pw, py, py + ph, (0, 0, 0, 200))
    arcade.draw_line(px, py + ph, px + pw, py + ph, palette.DANGER, 2)
    arcade.draw_line(px + pw, py, px + pw, py + ph, palette.DANGER, 1)

    target_name = (
        target.character.name if target.character
        else target.spec_ops_asset.name if target.spec_ops_asset
        else target.unit_type
    )

    arcade.draw_text("◉  TARGET LOCK", px + 10, py + ph - 14, palette.DANGER, font_size=10, bold=True)
    portrait_size = 40
    portrait_x = px + pw - portrait_size - 10
    portrait_y = py + ph - portrait_size - 10
    arcade.draw_text(
        target_name.upper() if len(target_name) <= 22 else target_name[:19].upper()+"...",
        px + 10,
        py + ph - 30,
        palette.TEXT,
        font_size=13,
        bold=True,
        width=max(10, pw - portrait_size - 24),
        align="left",
    )

    if target.unit_type == "enemy":
        try:
            from game.ui.portraits import portrait_path_for_enemy
            from game.ui.panels import _load_texture_once

            portrait_path = portrait_path_for_enemy(
                str(id(target)),
                getattr(target, "enemy_theme", "generic"),
                getattr(target, "enemy_subtype", "grunt"),
            )
            portrait = _load_texture_once(portrait_path) if portrait_path else None
        except Exception:
            portrait = None
        if portrait:
            arcade.draw_lrbt_rectangle_filled(
                portrait_x, portrait_x + portrait_size,
                portrait_y, portrait_y + portrait_size,
                palette.PANEL_FILL_DARK,
            )
            arcade.draw_lrbt_rectangle_outline(
                portrait_x, portrait_x + portrait_size,
                portrait_y, portrait_y + portrait_size,
                palette.DANGER,
                1,
            )
            arcade.draw_texture_rect(
                portrait,
                arcade.LBWH(portrait_x, portrait_y, portrait_size, portrait_size),
            )

    # Authoritative calculation shared with execution.
    if preview is None:
        from game.combat_preview import estimate_attack_preview

        preview = estimate_attack_preview(player, target, attack_key)
    defense = target.stats.defense if target.stats else 1
    chance = preview.hit_chance
    pct     = int(chance * 100)
    chance_col = (
        palette.TACTICAL_GREEN if pct >= 70
        else palette.WARNING    if pct >= 40
        else palette.DANGER
    )
    arcade.draw_text(f"HIT  {pct}%", px + 10, py + ph - 48, chance_col, font_size=13, bold=True)
    tactical = "FLANK · COVER 0" if preview.flanking else f"COVER +{preview.cover_bonus}"
    arcade.draw_text(
        f"DMG {preview.min_damage}-{preview.max_damage} · {tactical}",
        px + 10,
        py + ph - 64,
        palette.WARNING if preview.flanking else palette.MUTED_TEXT,
        font_size=9,
    )
    cost = f"AP {preview.ap_cost}"
    if preview.resource_cost:
        cost += f" · MISSILE {preview.resource_cost}"
    arcade.draw_text(cost, px + 10, py + 5, palette.MUTED_TEXT, font_size=9)

    bw = pw - 20
    arcade.draw_lrbt_rectangle_filled(px + 10, px + 10 + bw, py + 16, py + 26, palette.PANEL_FILL)
    arcade.draw_lrbt_rectangle_filled(px + 10, px + 10 + int(bw * chance), py + 16, py + 26, chance_col)

    # Target HP
    t_hp  = target.health
    t_max = target.stats.max_hp if target.stats else 1
    arcade.draw_text(f"HP {t_hp}/{t_max}", right-10, py+5, palette.DANGER,
                     font_size=9, anchor_x="right")


def draw_resource_summary(
    width: int,
    height: int,
    resources: dict[str, int],
    available_funds: int | None = None,
) -> None:
    """Draw a compact battle-side resource overview."""
    left = 14
    top = height - 46
    bottom = top - (46 if available_funds is not None else 30)
    right = min(width - 14, left + (520 if available_funds is not None else 460))

    arcade.draw_lrbt_rectangle_filled(left, right, bottom, top, (0, 0, 0, 185))
    arcade.draw_line(left, top, right, top, palette.PANEL_BORDER, 1)
    arcade.draw_text("RESOURCES", left + 10, top - 14, palette.TEXT, font_size=10, bold=True)

    if available_funds is not None:
        arcade.draw_text(
            f"FUNDS  ₦ {available_funds:,}",
            left + 10,
            top - 28,
            palette.RESOURCE,
            font_size=12,
            bold=True,
        )

    resource_line = (
        f"CREDITS {resources.get('credits', 0)}  |  "
        f"INTEL {resources.get('intel', 0)}  |  "
        f"SALVAGE {resources.get('salvage', 0)}  |  "
        f"INFLUENCE {resources.get('influence', 0)}"
    )
    arcade.draw_text(
        resource_line,
        left + 10,
        top - (38 if available_funds is not None else 18),
        palette.TEXT,
        font_size=11,
        width=max(140, right - left - 20),
        align="left",
    )


# ══════════════════════════════════════════════════════════════════════════════
# Objective marker
# ══════════════════════════════════════════════════════════════════════════════

def draw_objective_marker(objective: object, elapsed: float, *, battlefield_width: int = 1280,
                          compact=False, label_boxes=None, label_bounds=None, **context) -> None:
    """Draw an animated pulsing ring on the mission objective."""
    if objective is None:
        return
    ox, oy    = objective.position  # type: ignore[attr-defined]
    completed = getattr(objective, "completed", False)
    pulse     = 0.7 + 0.3 * math.sin(elapsed * 2.2)
    col       = palette.TACTICAL_GREEN if completed else palette.WARNING
    pcol      = (*col[:3], int(180 * pulse))

    if getattr(objective, "kind", "") == "containment" and not completed:
        breach_y = getattr(objective, "breach_y", None)
        if breach_y is not None:
            # The <= predicate includes centres on the threshold. Outline the
            # upper tile edge, not the centre of the last forbidden row.
            edge = (breach_y // CELL + 0.5) * CELL
            danger = (255, 95, 90, 210)
            half_width = max(CELL, int(getattr(objective, "breach_half_width", CELL * 3)))
            left = max(0, ox - half_width - CELL / 2)
            right = min(battlefield_width, ox + half_width + CELL / 2)
            arcade.draw_lrbt_rectangle_filled(left, right, max(0, edge-CELL), edge,
                                               (*danger[:3], 36))
            arcade.draw_line(left, edge, right, edge, danger, 3)
            for x in range(int(left) + 16, int(right), 64):
                arcade.draw_line(x, edge-6, x+12, edge-18, danger, 2)
                arcade.draw_line(x+12, edge-18, x+24, edge-6, danger, 2)
            arcade.draw_text("BREACH ZONE - KEEP HOSTILES OUT", (left+right)/2, edge+8,
                             danger, font_size=10, bold=True, anchor_x="center")

    if getattr(objective, "kind", "") == "defend" and not completed:
        # Nine grid-cell centres can breach the defense; show their full tiles.
        half = CELL * 1.5
        arcade.draw_lrbt_rectangle_filled(ox-half, ox+half, oy-half, oy+half, (*col[:3], 24))
        arcade.draw_lrbt_rectangle_outline(ox-half, ox+half, oy-half, oy+half, pcol, 2)
        if not compact:
            arcade.draw_text("KEEP HOSTILES OUT", ox, oy+half+8, col,
                             font_size=8, bold=True, anchor_x="center")

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

    # Inner diamond
    arcade.draw_lrbt_rectangle_filled(ox - 12, ox + 12, oy - 12, oy + 12, (*col[:3], 80))
    arcade.draw_rect_outline(arcade.LBWH(ox - 16, oy - 16, 32, 32), col, border_width=2)

    # Label, prompt, and progress
    objective_label = getattr(objective, "label", "OBJECTIVE")
    objective_phase = getattr(objective, "phase_text", objective_label)
    label = "OBJECTIVE COMPLETE" if completed else f"OBJECTIVE: {objective_phase}"
    if compact:
        kind = getattr(objective, "kind", "")
        label = ("OBJECTIVE COMPLETE" if completed else "OBJECTIVE FAILED" if getattr(objective, "failed", False)
                 else "HOLD / KEEP HOSTILES OUT" if kind == "defend" else f"OBJECTIVE: {objective_phase}")
        if len(label) > 32:
            label = label[:29]+"..."
        _draw_world_caption(label, ox, oy+(CELL*1.5+8 if kind == "defend" else 36), col,
                            [] if label_boxes is None else label_boxes, label_bounds)
        return
    arcade.draw_text(
        label, ox, oy + 34, col,
        font_size=9, bold=True, anchor_x="center",
    )
    if not completed:
        prompt = getattr(objective, "interaction_prompt", "Press E near marker.")
        progress = getattr(objective, "progress_text", "")
        if getattr(objective,"kind","") in {"defend","containment","assassination"} or getattr(objective,"failed",False):
            from game.ui.components.combat.objective_brief import objective_brief_lines
            progress, prompt = objective_brief_lines(objective, **context)
        arcade.draw_text(
            prompt,
            ox,
            oy - 38,
            palette.TEXT,
            font_size=8,
            anchor_x="center",
            width=220,
            align="center",
        )
        if progress:
            arcade.draw_text(
                progress,
                ox,
                oy - 52,
                palette.MUTED_TEXT,
                font_size=8,
                anchor_x="center",
            )


def draw_objective_brief(height: int, objective: object, **context) -> None:
    """Keep objective phase readable even when its marker is behind the HUD."""
    if objective is None:
        return
    from game.ui.components.combat.objective_brief import objective_brief_lines
    progress, instruction = objective_brief_lines(objective, **context)
    left, top = 14, height - 112
    arcade.draw_lrbt_rectangle_filled(left, left + 350, top - 76, top, (4, 12, 18, 225))
    arcade.draw_line(left, top, left + 350, top, palette.WARNING, 2)
    arcade.draw_text(
        f"OBJECTIVE / {objective.phase_text}", left + 10, top - 21,
        palette.WARNING, font_size=11, bold=True,
    )
    arcade.draw_text(
        progress, left + 10, top - 43,
        palette.TEXT, font_size=10,
    )
    arcade.draw_text(
        instruction, left + 10, top - 62,
        palette.MUTED_TEXT, font_size=9,
    )


# ══════════════════════════════════════════════════════════════════════════════
# Mission status bar — top chrome
# ══════════════════════════════════════════════════════════════════════════════

def draw_mission_status_bar(
    width: int,
    height: int,
    mission_title: str,
    player_count: int,
    enemy_count: int,
    turn_number: int,
) -> None:
    """Top chrome bar showing mission title, squad / enemy count, and turn."""
    bh = 38
    arcade.draw_lrbt_rectangle_filled(0, width, height - bh, height, (0, 0, 0, 200))
    arcade.draw_line(0, height - bh, width, height - bh, palette.PANEL_BORDER, 2)

    # XCOM notch left
    notch = 18
    arcade.draw_line(0, height, notch, height - notch, palette.PANEL_BORDER, 2)

    cx = width // 2

    # Title
    arcade.draw_text(
        (mission_title.upper() if len(mission_title)<=max(12,(width-460)//14) else mission_title.upper()[:max(12,(width-460)//14)-3]+"..."),
        20,
        height - bh // 2,
        palette.HEADER,
        font_size=13,
        bold=True,
        anchor_x="left",
        anchor_y="center",
        width=max(140, int(width * 0.40)),
        align="left",
    )
    # Squad count
    arcade.draw_text(
        f"◉ SQUAD  {player_count}",
        width - 390, height - bh // 2,
        palette.TACTICAL_GREEN, font_size=12,
        anchor_y="center",
    )

    # Enemy count
    arcade.draw_text(
        f"◉ ENEMIES  {enemy_count}",
        width - 260, height - bh // 2,
        palette.DANGER, font_size=12,
        anchor_y="center",
    )

    # Turn counter
    arcade.draw_text(
        f"TURN {turn_number:02d}",
        width - 18, height - bh // 2,
        palette.MUTED_TEXT, font_size=12,
        bold=True, anchor_x="right", anchor_y="center",
    )


# ══════════════════════════════════════════════════════════════════════════════
# Floating damage numbers (P02)
# ══════════════════════════════════════════════════════════════════════════════

def draw_damage_popups(popups: list[dict], *, label_boxes=None, label_bounds=None) -> None:
    """Draw floating damage/miss text above hit units (world-space).

    Each popup dict: {x, y, text, color: (r,g,b), age: float, max_age: float}
    """
    from game.ui.components.combat.world_labels import place_caption
    label_boxes = [] if label_boxes is None else label_boxes
    for popup in popups:
        progress = popup["age"] / max(0.001, popup["max_age"])
        alpha = max(0, int(255 * (1.0 - progress)))
        if alpha == 0:
            continue
        offset_y = int(40 * progress)
        r, g, b = popup["color"][:3]
        width = max(40, len(popup["text"])*11+16)
        box = place_caption(popup["x"], popup["y"]+offset_y-14, width, label_boxes,
                            height=28, bounds=label_bounds)
        if box is None:
            continue
        left,bottom,right,top = box
        arcade.draw_text(
            popup["text"],
            (left+right)/2,
            (bottom+top)/2,
            (r, g, b, alpha),
            font_size=14,
            bold=True,
            anchor_x="center",
            anchor_y="center",
        )


# ══════════════════════════════════════════════════════════════════════════════
# In-battle pause overlay (P04)
# ══════════════════════════════════════════════════════════════════════════════

# Button keys returned by draw_pause_overlay
PAUSE_RESUME   = "resume"
PAUSE_SETTINGS = "settings"
PAUSE_ABANDON  = "abandon"


def draw_pause_overlay(width: int, height: int) -> list[tuple[str, tuple[int, int, int, int]]]:
    """Draw the in-battle pause overlay.

    Returns a list of (action_key, (left, bottom, right, top)) button rects.
    """
    # Dim the battlefield
    arcade.draw_lrbt_rectangle_filled(0, width, 0, height, (0, 0, 0, 170))

    # Central panel
    pw, ph = 300, 240
    px, py = (width - pw) // 2, (height - ph) // 2
    arcade.draw_lrbt_rectangle_filled(px, px + pw, py, py + ph, (8, 20, 30, 240))
    arcade.draw_lrbt_rectangle_outline(px, px + pw, py, py + ph, palette.PANEL_BORDER, 2)
    arcade.draw_line(px, py + ph - 44, px + pw, py + ph - 44, palette.PANEL_BORDER_MUTED, 1)
    arcade.draw_text(
        "PAUSED",
        px + pw // 2,
        py + ph - 22,
        palette.TACTICAL_GREEN,
        font_size=16,
        bold=True,
        anchor_x="center",
        anchor_y="center",
    )

    # Buttons: Resume / Settings / Abandon
    bw, bh = 220, 42
    bx = px + (pw - bw) // 2
    button_defs = [
        (PAUSE_RESUME,   "RESUME",   palette.TACTICAL_GREEN, py + ph - 102),
        (PAUSE_SETTINGS, "SETTINGS", palette.ACCENT,         py + ph - 154),
        (PAUSE_ABANDON,  "ABANDON",  palette.DANGER,         py + ph - 206),
    ]
    rects: list[tuple[str, tuple[int, int, int, int]]] = []
    for key, label, col, by in button_defs:
        arcade.draw_lrbt_rectangle_filled(bx, bx + bw, by, by + bh, (18, 36, 48, 220))
        arcade.draw_line(bx, by + bh, bx + bw, by + bh, col, 2)
        arcade.draw_text(
            label,
            bx + bw // 2,
            by + bh // 2,
            col,
            font_size=13,
            bold=True,
            anchor_x="center",
            anchor_y="center",
        )
        rects.append((key, (bx, by, bx + bw, by + bh)))
    return rects


# ══════════════════════════════════════════════════════════════════════════════
# Combat log side panel (P05)
# ══════════════════════════════════════════════════════════════════════════════

def draw_combat_log_side_panel(
    width: int,
    height: int,
    events: list[str],
    max_lines: int = 8,
) -> None:
    """Draw a compact side-panel on the right edge showing recent combat events.

    *events* is a plain list of recent message strings (newest last).
    """
    px, py, right, top = combat_log_bounds(width,height,max_lines)
    panel_w, panel_h = right-px, top-py

    arcade.draw_lrbt_rectangle_filled(px, px + panel_w, py, py + panel_h, (8, 18, 28, 220))
    arcade.draw_lrbt_rectangle_outline(px, px + panel_w, py, py + panel_h, palette.PANEL_BORDER, 1)
    arcade.draw_text(
        "COMBAT LOG  [Tab]",
        px + panel_w // 2,
        py + panel_h - 16,
        palette.MUTED_TEXT,
        font_size=10,
        bold=True,
        anchor_x="center",
        anchor_y="center",
    )
    arcade.draw_line(px, py + panel_h - 28, px + panel_w, py + panel_h - 28, palette.PANEL_BORDER_MUTED, 1)

    visible = list(reversed(events))[:max_lines]
    for i, line in enumerate(visible):
        row_y = py + panel_h - 44 - i * 18
        col = palette.TEXT if i == 0 else palette.MUTED_TEXT
        arcade.draw_text(
            line[:34],
            px + 8,
            row_y,
            col,
            font_size=9,
            anchor_y="top",
        )


# ══════════════════════════════════════════════════════════════════════════════
# Pre-battle deployment phase overlay (A02)
# ══════════════════════════════════════════════════════════════════════════════

_DEPLOY_ZONE_ROWS = 4
_DEPLOY_ZONE_H = _DEPLOY_ZONE_ROWS * CELL  # 128 px


def draw_deployment_overlay(
    width: int,
    height: int,
    player_units: list,
    deploy_cursor: int,
    elapsed: float,
    *, deployment_cells=None, camera_offset=(0,0),
) -> None:
    """Draw the pre-battle deployment overlay (GUI/screen space).

    Highlights the deployment zone at the map bottom, shows active-unit
    selector, and renders controls hint.
    """
    # Deployment zone tint (bottom of the map)
    offset_x,offset_y=camera_offset
    if deployment_cells is None:
        arcade.draw_lrbt_rectangle_filled(-offset_x,width-offset_x,-offset_y,_DEPLOY_ZONE_H-offset_y,(60,200,120,30))
        arcade.draw_line(-offset_x,_DEPLOY_ZONE_H-offset_y,width-offset_x,_DEPLOY_ZONE_H-offset_y,(60,200,120,120),2)
    else:
        for x, y in deployment_cells:
            arcade.draw_lrbt_rectangle_filled(x-offset_x-12,x-offset_x+12,y-offset_y-12,y-offset_y+12,(60,200,120,40))

    # "DEPLOYMENT" phase banner — same position as regular phase banner
    pulse = 0.85 + 0.15 * math.sin(elapsed * 2.5)
    col = (*_ACTIVE_COL, int(230 * pulse))
    pill_w, pill_h = 260, 32
    px = width - pill_w - 12
    py = height - 48
    arcade.draw_lrbt_rectangle_filled(px, px + pill_w, py, py + pill_h, (0, 0, 0, 200))
    arcade.draw_line(px, py + pill_h, px + pill_w, py + pill_h, col, 2)
    arcade.draw_line(px, py + pill_h, px + 18, py + pill_h - 18, col, 2)
    arcade.draw_text(
        "DEPLOYMENT PHASE",
        px + pill_w - 12, py + pill_h // 2,
        col, font_size=13, bold=True,
        anchor_x="right", anchor_y="center",
    )

    # Active unit highlight ring
    if player_units and 0 <= deploy_cursor < len(player_units):
        unit = player_units[deploy_cursor]
        ux, uy = unit.position
        ux,uy=ux-offset_x,uy-offset_y
        ring_r = 22 + 3 * math.sin(elapsed * 4)
        arcade.draw_circle_outline(ux, uy, ring_r, _ACTIVE_COL, 3)
        name = (
            unit.character.name if getattr(unit, "character", None)
            else getattr(getattr(unit, "spec_ops_asset", None), "name", unit.unit_type)
        )
        arcade.draw_text(
            f"▶ {name}",
            ux, uy + ring_r + 6,
            _ACTIVE_COL, font_size=9, bold=True,
            anchor_x="center",
        )

    # Bottom controls bar
    bar_h = 40
    arcade.draw_lrbt_rectangle_filled(0, width, 0, bar_h, (0, 0, 0, 200))
    arcade.draw_line(0, bar_h, width, bar_h, palette.PANEL_BORDER, 1)
    arcade.draw_text(
        "Tab = next unit   Arrows = reposition   Enter = begin battle",
        width // 2, bar_h // 2,
        palette.MUTED_TEXT, font_size=10,
        anchor_x="center", anchor_y="center",
    )


# ══════════════════════════════════════════════════════════════════════════════
# Wave 5-B: Battle Spectacle
# ══════════════════════════════════════════════════════════════════════════════

def draw_mission_intro(
    width: int,
    height: int,
    mission_title: str,
    district: str,
    progress: float,
) -> None:
    """Draw the 2-second mission-start intro overlay (GUI/screen space).

    *progress* goes 0.0 → 1.0 over the intro duration; everything fades out
    and the scanning line completes its sweep by progress=1.0.
    """
    fade = max(0.0, 1.0 - progress)

    # Dark background — fades out
    arcade.draw_lrbt_rectangle_filled(0, width, 0, height, (0, 0, 0, int(210 * fade)))

    cx = width // 2
    cy = height // 2

    # ── Scan line: sweeps left → right ──────────────────────────────────────
    scan_x = int(progress * width)
    alpha_scan = int(180 * fade)
    arcade.draw_line(scan_x, 0, scan_x, height, (60, 220, 180, alpha_scan), 2)
    # Trailing glow
    trail = max(0, scan_x - 40)
    for i in range(3):
        ax = trail + i * 13
        arcade.draw_line(ax, 0, ax, height, (60, 220, 180, max(0, int(40 * fade * (1 - i * 0.3)))), 1)

    # ── Horizontal rule ──────────────────────────────────────────────────────
    col_line = (*_ACTIVE_COL, int(200 * fade))
    arcade.draw_line(cx - 260, cy + 46, cx + 260, cy + 46, col_line, 1)
    arcade.draw_line(cx - 260, cy - 46, cx + 260, cy - 46, col_line, 1)

    # ── "TACTICAL INSERTION" label ───────────────────────────────────────────
    arcade.draw_text(
        "TACTICAL INSERTION",
        cx, cy + 60,
        (*palette.MUTED_TEXT[:3], int(200 * fade)),
        font_size=10, bold=True,
        anchor_x="center", anchor_y="center",
    )

    # ── Mission title ────────────────────────────────────────────────────────
    arcade.draw_text(
        mission_title.upper(),
        cx, cy,
        (*palette.HEADER[:3], int(240 * fade)),
        font_size=28, bold=True,
        anchor_x="center", anchor_y="center",
    )

    # ── District label ────────────────────────────────────────────────────────
    arcade.draw_text(
        district.upper(),
        cx, cy - 58,
        (*_ACTIVE_COL, int(180 * fade)),
        font_size=12,
        anchor_x="center", anchor_y="center",
    )


def draw_ambient_overlay(
    width: int,
    height: int,
    elapsed: float,
    map_path: str,
    particles: list[dict],
) -> None:
    """Draw ambient atmosphere effects over the HUD (screen space).

    *particles* is the BattleView particles list — rain drops are appended here.
    """
    import random as _r, math as _m

    # ── Scanlines: subtle CRT effect ────────────────────────────────────────
    for y in range(0, height, 3):
        arcade.draw_lrbt_rectangle_filled(0, width, y, y + 1, (0, 0, 0, 14))

    # ── Neon edge glow ────────────────────────────────────────────────────────
    edge = 22
    pulse = 0.85 + 0.15 * _m.sin(elapsed * 1.8)
    alpha_edge = int(28 * pulse)
    # Top + bottom cyan strips
    arcade.draw_lrbt_rectangle_filled(0, width, height - edge, height, (40, 200, 220, alpha_edge))
    arcade.draw_lrbt_rectangle_filled(0, width, 0, edge, (40, 200, 220, alpha_edge))
    # Left + right red strips
    arcade.draw_lrbt_rectangle_filled(0, edge, 0, height, (220, 40, 80, alpha_edge))
    arcade.draw_lrbt_rectangle_filled(width - edge, width, 0, height, (220, 40, 80, alpha_edge))

    # ── Map-keyed atmosphere ─────────────────────────────────────────────────
    mp = (map_path or "").lower()
    if any(kw in mp for kw in ("rain", "fog", "neon_rain")):
        # Spawn 2 rain-drop particles per frame
        for _ in range(2):
            particles.append({
                "x": _r.uniform(0, width),
                "y": height,
                "vx": _r.uniform(-20, -10),
                "vy": _r.uniform(-280, -180),
                "color": (180, 210, 255),
                "life": _r.uniform(0.4, 0.7),
                "size": _r.uniform(0.8, 1.6),
            })
    if any(kw in mp for kw in ("blackout", "dark")):
        arcade.draw_lrbt_rectangle_filled(0, width, 0, height, (0, 0, 0, 38))
    if "neon" in mp and _r.random() < 0.005:
        # Random neon flicker on one edge
        side = _r.randint(0, 3)
        cols = [(0, width, height - edge, height), (0, width, 0, edge),
                (0, edge, 0, height), (width - edge, width, 0, height)]
        l, r, b, t = cols[side]
        arcade.draw_lrbt_rectangle_filled(l, r, b, t, (60, 255, 220, 90))


def draw_assassination_marker(unit: "Unit", elapsed: float) -> None:
    """Draw a pulsing red crosshair above the assassination target (world space)."""
    if not unit.sprite:
        return
    cx, cy = unit.sprite.center_x, unit.sprite.center_y
    top = cy + unit.sprite.height // 2 + 20
    pulse = 0.7 + 0.3 * math.sin(elapsed * 4.0)
    alpha = int(220 * pulse)
    r_col = (255, 30, 30, alpha)
    # Diamond shape
    sz = 10
    arcade.draw_line(cx - sz, top,      cx,      top + sz, r_col, 2)
    arcade.draw_line(cx,      top + sz, cx + sz, top,      r_col, 2)
    arcade.draw_line(cx + sz, top,      cx,      top - sz, r_col, 2)
    arcade.draw_line(cx,      top - sz, cx - sz, top,      r_col, 2)
    # Label
    arcade.draw_text("TARGET", cx, top + sz + 8, r_col, font_size=8,
                     bold=True, anchor_x="center")


# ══════════════════════════════════════════════════════════════════════════════
# Advanced Visual Effects (Phase 4)
# ══════════════════════════════════════════════════════════════════════════════

# ── C2 — Spark particles ──────────────────────────────────────────────────────

def draw_particles(particles: list[dict]) -> None:
    """Draw spark particles in world space.

    Each particle dict: {x, y, vx, vy, color:(r,g,b), life:0-1, size:float}
    """
    for p in particles:
        alpha = max(0, int(255 * p["life"]))
        r, g, b = p["color"][:3]
        size = max(0.5, p["size"] * p["life"])
        arcade.draw_circle_filled(p["x"], p["y"], size, (r, g, b, alpha))


# ── C3 — Unit hit flash ───────────────────────────────────────────────────────

def draw_hit_flashes(
    all_units: list,
    flashes: dict,
) -> None:
    """Draw a coloured overlay on units that were recently hit.

    *flashes* maps id(unit) → {timer: float, color: (r,g,b), max_timer: float}
    """
    for unit in all_units:
        flash = flashes.get(id(unit))
        if not flash or not getattr(unit, "sprite", None):
            continue
        progress = flash["timer"] / max(0.001, flash.get("max_timer", 0.15))
        alpha = max(0, int(180 * progress))
        r, g, b = flash["color"][:3]
        s = unit.sprite
        cx, cy = s.center_x, s.center_y
        hw, hh = s.width // 2 + 2, s.height // 2 + 2
        arcade.draw_lrbt_rectangle_filled(cx - hw, cx + hw, cy - hh, cy + hh, (r, g, b, alpha))


# ── C4 — Death ring ───────────────────────────────────────────────────────────

def draw_death_rings(rings: list[dict]) -> None:
    """Draw expanding circle rings on unit deaths (world space).

    Each ring dict: {x, y, radius:float, life:0-1, color:(r,g,b)}
    """
    for ring in rings:
        alpha = max(0, int(220 * ring["life"]))
        r, g, b = ring["color"][:3]
        arcade.draw_circle_outline(ring["x"], ring["y"], ring["radius"], (r, g, b, alpha), 3)
        # Inner smaller ring
        if ring["radius"] > 12:
            arcade.draw_circle_outline(
                ring["x"], ring["y"], ring["radius"] * 0.55,
                (r, g, b, alpha // 2), 1,
            )


# ── C5 — Muzzle flash ─────────────────────────────────────────────────────────

def draw_muzzle_flashes(flashes: list[dict]) -> None:
    """Draw a bright burst at the attacker's position (world space).

    Each flash dict: {x, y, timer:float, max_timer:float}
    """
    for flash in flashes:
        progress = flash["timer"] / max(0.001, flash.get("max_timer", 0.08))
        size = 22 * progress
        alpha_out = max(0, int(200 * progress))
        alpha_in  = max(0, int(240 * progress))
        arcade.draw_circle_filled(flash["x"], flash["y"], size,       (255, 230, 100, alpha_out))
        arcade.draw_circle_filled(flash["x"], flash["y"], size * 0.45, (255, 255, 255, alpha_in))
        # Four small flare lines
        for angle in (0, 90, 180, 270):
            rad = math.radians(angle)
            ex = flash["x"] + math.cos(rad) * size * 1.6
            ey = flash["y"] + math.sin(rad) * size * 1.6
            arcade.draw_line(flash["x"], flash["y"], ex, ey, (255, 240, 150, alpha_out // 2), 2)


# ── C6 — Psi wave rings ───────────────────────────────────────────────────────

def draw_psi_waves(waves: list[dict]) -> None:
    """Draw concentric expanding rings for psi attacks (world space).

    Each wave dict: {x, y, radius:float, life:0-1, delay:float, active:bool}
    """
    for wave in waves:
        if not wave.get("active", True):
            continue
        alpha = max(0, int(200 * wave["life"]))
        arcade.draw_circle_outline(wave["x"], wave["y"], wave["radius"], (90, 160, 255, alpha), 2)
        # Soft inner glow
        if wave["radius"] > 5:
            arcade.draw_circle_outline(
                wave["x"], wave["y"], wave["radius"] * 0.7,
                (140, 100, 255, alpha // 2), 1,
            )
