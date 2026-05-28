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
"""

from __future__ import annotations

import math
from typing import TYPE_CHECKING

import arcade

from game.ui import palette

if TYPE_CHECKING:
    from game.unit import Unit

# ── Grid constants ──────────────────────────────────────────────────────────

CELL = 32           # pixels per tile
MOVE_RANGE = 3      # default AP moves for highlighting
ATTACK_RANGE_DEFAULT = 4

# ── Palette aliases ──────────────────────────────────────────────────────────

_GRID_COL       = (50,  100, 130,  18)
_MOVE_COL       = (60,  160, 220,  28)
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
        base = ["LS déplacer", "A confirmer", "B annuler", "X tir", "Y psi"]
        target = ["LB/RB cible", "A valider", "B retour"]
        end_turn = ["A confirmer fin de tour", "B annuler"]
    else:
        base = ["Flèches déplacer", "E objectif", "F tir", "P psi", "Entrée fin tour"]
        target = ["←/→ cible", "Entrée valider", "Esc retour"]
        end_turn = ["Entrée confirmer fin de tour", "Esc annuler"]
    hints = end_turn if pending_end_turn_confirmation else (target if selecting_target else base)
    return "Raccourcis actifs: " + " | ".join(hints)


def _draw_top_centered_banner(
    width: int,
    height: int,
    text: str,
    *,
    bottom_offset: int,
    banner_ratio: float,
    min_width: int,
    max_width: int | None = None,
    text_color=palette.TEXT,
    font_size: int = 10,
) -> None:
    banner_cap = width - 24
    if max_width is not None:
        banner_cap = min(banner_cap, max_width)
    banner_w = min(banner_cap, max(min_width, int(width * banner_ratio)))
    left = (width - banner_w) // 2
    right = left + banner_w
    bottom = max(0, height - bottom_offset)
    top = bottom + 24
    arcade.draw_lrbt_rectangle_filled(left, right, bottom, top, (0, 0, 0, 175))
    arcade.draw_line(left, top, right, top, palette.PANEL_BORDER_MUTED, 1)
    arcade.draw_text(
        text,
        width // 2,
        bottom + 12,
        text_color,
        font_size,
        anchor_x="center",
        anchor_y="center",
    )


def draw_battle_shortcut_banner(width: int, height: int, text: str) -> None:
    """Draw a thin contextual shortcut banner at the top-center of the screen."""
    _draw_top_centered_banner(
        width,
        height,
        text,
        bottom_offset=60,
        banner_ratio=0.62,
        min_width=620,
        font_size=12,
    )


def draw_action_aftermath_line(width: int, height: int, text: str | None) -> None:
    """Draw a fixed HUD slot for temporary action-causality feedback."""
    if not text:
        return
    _draw_top_centered_banner(
        width,
        height,
        text,
        bottom_offset=88,
        banner_ratio=0.42,
        min_width=320,
        max_width=680,
        text_color=palette.TACTICAL_GREEN,
        font_size=12,
    )

# ══════════════════════════════════════════════════════════════════════════════
# Grid & range overlays
# ══════════════════════════════════════════════════════════════════════════════

def draw_tactical_grid(width: int, height: int) -> None:
    """Draw a faint cross-hatch grid over the whole map."""
    for x in range(0, width + CELL, CELL):
        arcade.draw_line(x, 0, x, height, _GRID_COL, 1)
    for y in range(0, height + CELL, CELL):
        arcade.draw_line(0, y, width, y, _GRID_COL, 1)


def draw_movement_range(
    unit: "Unit",
    width: int,
    height: int,
    *,
    can_enter=None,
) -> None:
    """Highlight cells the active unit can reach (Manhattan ≤ AP × MOVE_RANGE)."""
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
                    if can_enter is not None and not can_enter(cx, cy):
                        continue
                    arcade.draw_lrbt_rectangle_filled(
                        cx, cx + CELL, cy, cy + CELL, _MOVE_COL
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

def draw_cover_nodes(cover_nodes: list) -> None:
    """Draw low/high cover tiles on the battlefield grid.

    *cover_nodes* is a list of ``CoverNode`` from ``game.cover_system``.
    Colours come from ``game.cover_system.COVER_LOW_COL / COVER_HIGH_COL``.
    """
    if not cover_nodes:
        return
    from game.cover_system import COVER_LOW_COL, COVER_HIGH_COL
    for node in cover_nodes:
        col = COVER_HIGH_COL if node.cover_type == "high" else COVER_LOW_COL
        wx, wy = node.world_x, node.world_y
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
) -> None:
    """Draw HP bars and role labels above every unit sprite."""
    for i, unit in enumerate(player_units):
        if not unit.sprite or not unit.stats:
            continue
        _draw_unit_bar(unit, active=(i == active_index), is_enemy=False)
    for unit in enemy_units:
        if not unit.sprite or not unit.stats:
            continue
        _draw_unit_bar(unit, active=False, is_enemy=True)


def _draw_unit_bar(unit: "Unit", *, active: bool, is_enemy: bool) -> None:
    # Never draw labels/HP bar for enemies hidden in fog of war
    if is_enemy and not getattr(unit, "visible", True):
        return
    cx   = unit.sprite.center_x
    top  = unit.sprite.center_y + unit.sprite.height // 2 + 4
    bw   = max(40, unit.sprite.width + 12)
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
    # Overwatch indicator — yellow ◈ prefix
    if getattr(unit, "on_overwatch", False):
        arcade.draw_text(
            "◈ OW",
            cx, top + bh + 3,
            _OVERWATCH_COL,
            font_size=8, bold=True, anchor_x="center",
        )
    else:
        arcade.draw_text(name, cx, top + bh + 3, name_col, font_size=9, anchor_x="center")

    # Enemy subtype label (grunt / heavy / elite / commander) — shown below HP bar
    if is_enemy:
        subtype = getattr(unit, "enemy_subtype", "")
        if subtype and subtype != "grunt":
            arcade.draw_text(
                subtype.upper(),
                cx, top - 2,
                (*palette.DANGER[:3], 180),
                font_size=7, anchor_x="center",
            )


# ══════════════════════════════════════════════════════════════════════════════
# Portrait strip — bottom edge, shows all player units
# ══════════════════════════════════════════════════════════════════════════════

def draw_unit_portrait_strip(
    player_units: list["Unit"],
    active_index: int,
    width: int,
    elapsed: float,
) -> None:
    """Bottom strip: one card per player unit with portrait, HP, AP dots, name."""
    if not player_units:
        return

    strip_y = _COMBAT_BAR_TOP + 4  # bottom of strip — sits above the combat action bar
    n       = len(player_units)
    total_w = n * _STRIP_CARD_W + (n - 1) * 4
    start_x = (width - total_w) // 2

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
        tx = px + pp + 4
        name = ""
        if unit.character:
            name = unit.character.name.split()[0].upper()[:6]
        elif unit.spec_ops_asset:
            name = unit.spec_ops_asset.name[:6].upper()
        else:
            name = unit.unit_type.upper()[:5]
        arcade.draw_text(
            name, tx, strip_y + _STRIP_H - 16,
            palette.TEXT if active else palette.MUTED_TEXT,
            font_size=8, bold=active,
        )
        # Dead / recovering indicator
        if unit.health <= 0:
            arcade.draw_lrbt_rectangle_filled(cx, cx + _STRIP_CARD_W, strip_y + 2, strip_y + _STRIP_H - 2, (180, 0, 0, 80))
            arcade.draw_text("KIA", cx + _STRIP_CARD_W // 2, strip_y + _STRIP_H // 2, palette.DANGER, font_size=9, bold=True, anchor_x="center", anchor_y="center")


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
    """Draw a red (miss) or green (hit) screen-edge flash.

    *flash_alpha* should be driven externally and fade over ~0.4 s.
    Call with flash_alpha=0 to skip drawing entirely.
    """
    if flash_alpha <= 0:
        return
    col = (*palette.TACTICAL_GREEN[:3], flash_alpha) if hit else (*palette.DANGER[:3], flash_alpha)
    edge = max(30, int(width * 0.06))
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
    py = height - 48
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

    # Turn-number dot track
    dot_x = px + 14
    dot_y  = py + 10
    for i in range(min(turn_number, 10)):
        alpha = int(200 * pulse) if i < turn_number else 50
        arcade.draw_lrbt_rectangle_filled(
            dot_x + i * 16, dot_x + i * 16 + 10,
            dot_y, dot_y + 10,
            (*color[:3], alpha),
        )


# ══════════════════════════════════════════════════════════════════════════════
# Unit detail panel — bottom-left, active unit stats
# ══════════════════════════════════════════════════════════════════════════════

def draw_unit_status_panel(
    _width: int, _height: int, unit: "Unit | None", turn: str
) -> None:
    """Detailed stats panel for the active player unit — bottom-left corner."""
    pw = 320
    ph = 90
    px = 12
    py = 12  # dock to the bottom-left edge instead of floating above the strip

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
    pp = 68
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
    arcade.draw_text(name.upper(), px + pp + 18, py + ph - 16, palette.TEXT, font_size=13, bold=True)
    arcade.draw_text(role.upper() or unit.unit_type.upper(), px + pp + 18, py + ph - 30, role_col, font_size=10)

    # HP bar
    bw = pw - pp - 32
    max_hp   = max(1, unit.stats.max_hp) if unit.stats else 1
    hp_frac  = max(0.0, min(1.0, unit.health / max_hp))
    hp_col   = palette.TACTICAL_GREEN if hp_frac > 0.5 else (palette.WARNING if hp_frac > 0.25 else palette.DANGER)
    arcade.draw_text("HP", px + pp + 18, py + 50, palette.MUTED_TEXT, font_size=9)
    arcade.draw_lrbt_rectangle_filled(px + pp + 32, px + pp + 32 + bw, py + 48, py + 58, palette.PANEL_FILL)
    arcade.draw_lrbt_rectangle_filled(px + pp + 32, px + pp + 32 + int(bw * hp_frac), py + 48, py + 58, hp_col)
    arcade.draw_text(f"{unit.health}/{max_hp}", px + pp + 34 + bw, py + 48, hp_col, font_size=9)

    # AP pips
    max_ap = max(1, getattr(unit, "action_points", 1) + 1)
    ap_now  = max(0, getattr(unit, "action_points", 0))
    arcade.draw_text("AP", px + pp + 18, py + 34, palette.MUTED_TEXT, font_size=9)
    for i in range(max_ap):
        col = palette.ACCENT if i < ap_now else (18, 36, 48, 200)
        arcade.draw_lrbt_rectangle_filled(
            px + pp + 32 + i * 20, px + pp + 48 + i * 20, py + 32, py + 43, col
        )
        arcade.draw_line(px + pp + 32 + i * 20, py + 32, px + pp + 48 + i * 20, py + 32, palette.PANEL_BORDER_MUTED, 1)

    # Stress & defense
    if unit.character:
        stress     = unit.character.stress
        stress_col = palette.DANGER if stress >= 70 else (palette.WARNING if stress >= 40 else palette.MUTED_TEXT)
        arcade.draw_text(f"STRESS {stress:>3}%", px + pp + 18, py + 16, stress_col, font_size=9)
    if unit.stats:
        arcade.draw_text(f"DEF {unit.stats.defense}", px + pp + 18, py + 6, palette.MUTED_TEXT, font_size=9)


# ══════════════════════════════════════════════════════════════════════════════
# Target-lock panel
# ══════════════════════════════════════════════════════════════════════════════

def draw_target_lock_panel(
    width: int,
    target: "Unit | None",
    attack_key: str,
    player: "Unit | None",
) -> None:
    """Draw a target-lock info panel when the player is picking a target."""
    if target is None or player is None:
        return

    pw, ph = 270, 80
    px = width - pw - 14
    py = _COMBAT_BAR_TOP + _STRIP_H + 12

    arcade.draw_lrbt_rectangle_filled(px, px + pw, py, py + ph, (0, 0, 0, 200))
    arcade.draw_line(px, py + ph, px + pw, py + ph, palette.DANGER, 2)
    arcade.draw_line(px + pw, py, px + pw, py + ph, palette.DANGER, 1)

    target_name = (
        target.character.name if target.character
        else target.spec_ops_asset.name if target.spec_ops_asset
        else target.unit_type
    )

    arcade.draw_text("◉  TARGET LOCK", px + 10, py + ph - 14, palette.DANGER, font_size=10, bold=True)
    arcade.draw_text(
        target_name.upper(),
        px + 10,
        py + ph - 30,
        palette.TEXT,
        font_size=13,
        bold=True,
        width=max(10, pw - 20),
        align="left",
    )

    # Hit chance calculation
    stat_map = {"melee": "str", "shoot": "agi", "psi": "psi"}
    sname   = stat_map.get(attack_key, "str")
    atk     = getattr(player.stats, sname, 1) if player.stats else 1
    defense = target.stats.defense if target.stats else 1
    chance  = atk / (atk + max(1, defense))
    pct     = int(chance * 100)
    chance_col = (
        palette.TACTICAL_GREEN if pct >= 70
        else palette.WARNING    if pct >= 40
        else palette.DANGER
    )
    arcade.draw_text(f"HIT  {pct}%", px + 10, py + ph - 48, chance_col, font_size=13, bold=True)
    arcade.draw_text(f"DEF  {defense}", px + 10, py + ph - 62, palette.MUTED_TEXT, font_size=9)

    bw = pw - 20
    arcade.draw_lrbt_rectangle_filled(px + 10, px + 10 + bw, py + 16, py + 26, palette.PANEL_FILL)
    arcade.draw_lrbt_rectangle_filled(px + 10, px + 10 + int(bw * chance), py + 16, py + 26, chance_col)

    # Target HP
    t_hp  = target.health
    t_max = target.stats.max_hp if target.stats else 1
    arcade.draw_text(f"HP {t_hp}/{t_max}", px + bw - 20, py + 6, palette.DANGER, font_size=9)


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
            f"FUNDS  ¥ {available_funds:,}",
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

def draw_objective_marker(objective: object, elapsed: float) -> None:
    """Draw an animated pulsing ring on the mission objective."""
    if objective is None:
        return
    ox, oy    = objective.position  # type: ignore[attr-defined]
    completed = getattr(objective, "completed", False)
    pulse     = 0.7 + 0.3 * math.sin(elapsed * 2.2)
    col       = palette.TACTICAL_GREEN if completed else palette.WARNING
    pcol      = (*col[:3], int(180 * pulse))

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

    # Label
    label = "OBJECTIVE COMPLETE" if completed else "OBJECTIVE"
    arcade.draw_text(
        label, ox, oy + 34, col,
        font_size=9, bold=True, anchor_x="center",
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
        mission_title.upper(),
        cx,
        height - bh // 2,
        palette.HEADER,
        font_size=13,
        bold=True,
        anchor_x="center",
        anchor_y="center",
        width=max(140, width - 240),
        align="center",
    )
    # Decorative flanking lines
    arcade.draw_line(cx - 200, height - bh // 2, cx - 140, height - bh // 2, palette.PANEL_BORDER_MUTED, 1)
    arcade.draw_line(cx + 140, height - bh // 2, cx + 200, height - bh // 2, palette.PANEL_BORDER_MUTED, 1)

    # Squad count
    arcade.draw_text(
        f"◉ SQUAD  {player_count}",
        cx - 280, height - bh // 2,
        palette.TACTICAL_GREEN, font_size=12,
        anchor_y="center",
    )

    # Enemy count
    arcade.draw_text(
        f"◉ ENEMIES  {enemy_count}",
        cx + 170, height - bh // 2,
        palette.DANGER, font_size=12,
        anchor_y="center",
    )

    # Turn counter
    arcade.draw_text(
        f"TURN {turn_number:02d}",
        width - 14, height - bh // 2,
        palette.MUTED_TEXT, font_size=12,
        bold=True, anchor_x="right", anchor_y="center",
    )
