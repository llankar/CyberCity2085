"""Live agents pane for Squad Command; dispatches existing management actions."""

import arcade
from game.character import is_deployable
from game.ui.layouts.world_map_beacons import Rect
from game.ui.layouts.squad_command import visible_roster_range
from game.ui.portraits import portrait_path_for_character
from game.ui.theme.typography import get_text_size, scale_font_size
from .squad_style import CYAN, GOLD, MINT, RED, TEXT, MUTED

ROSTER_PANEL_FILL_ALPHA = 150
ROSTER_CARD_FILL_ALPHA = 182


def draw_agents(self, r):
    gs = self.gs
    u = self.u
    self.panel(
        r,
        self.tr(
            "squad", selected=len(gs.selected_agent_names), total=len(gs.characters)
        ),
        "squad",
        fill_alpha=ROSTER_PANEL_FILL_ALPHA,
    )
    top = r.top - 59 * u
    bottom = r.bottom + 65 * u
    capacity = 4 if get_text_size() == "large" and self.layout.height < 900 else 5
    self.roster_capacity = capacity
    self.roster_first = max(
        0, min(self.roster_first, max(0, len(gs.characters) - capacity))
    )
    indices = visible_roster_range(
        len(gs.characters), self.view.deployment_cursor, self.roster_first, capacity
    )
    card_h = (top - bottom - (capacity - 1) * 9 * u) / capacity
    self.regions["roster"] = Rect(r.left, bottom, r.right, top)
    stress_reserve = (160 if get_text_size() == "large" else 140) * u
    for row, index in enumerate(indices):
        char = gs.characters[index]
        t = top - row * (card_h + 9 * u)
        b = t - card_h
        rect = Rect(r.left + 11 * u, b, r.right - 11 * u, t)
        active = index == self.view.deployment_cursor
        selected = char.name in gs.selected_agent_names
        color = GOLD if active else CYAN
        hot = self.hover == ("agent_card", index)
        if active:
            self.paint.glow(
                *rect.center, rect.width * 1.03, rect.height * 1.4, GOLD, 55
            )
        self.paint.panel(
            rect,
            color,
            selected=active or hot,
            fill_alpha=ROSTER_CARD_FILL_ALPHA if not (active or hot) else 198,
        )
        ps = min(card_h - 8 * u, 96 * u)
        portrait = Rect(rect.left + 4 * u, b + 4 * u, rect.left + 4 * u + ps, t - 4 * u)
        self.image(portrait_path_for_character(char), portrait)
        arcade.draw_line(
            portrait.right, b + 4 * u, portrait.right, t - 4 * u, (*color, 180), 1
        )
        tx = portrait.right + 10 * u
        right = rect.right - 10 * u
        name_h = scale_font_size(max(13, 22 * u)) * 1.2
        small_h = scale_font_size(max(13, 12 * u)) * 1.2
        name_y = t - 5 * u - name_h / 2
        role_y = name_y - name_h / 2 - 3 * u - small_h / 2
        self.label(
            char.name.upper(),
            tx,
            name_y,
            22,
            bold=True,
            width=right - tx - (70 if char.pending_points else 15) * u,
        )
        if selected:
            self.icon("select", right - 2 * u, t - 15 * u, 15, MINT)
        role = (
            self.tr("role." + char.role)
            if char.role in ("samurai", "sniper", "psi", "robot", "power_armor")
            else char.role.upper()
        )
        self.label(role, tx, role_y, 12, CYAN, width=right - tx)
        health_label_y = role_y - small_h - 2 * u
        health_y = health_label_y - small_h / 2 - 4 * u
        self.label(
            self.tr("hp") + f"  {char.stats.hp}/{char.stats.max_hp}",
            tx,
            health_label_y,
            11,
            TEXT,
            width=right - tx,
        )
        self.meter(
            Rect(tx, health_y - 1 * u, right, health_y + 5 * u),
            char.stats.hp / max(1, char.stats.max_hp),
            CYAN,
        )
        self.label(
            f"STRESS {char.stress}%",
            tx,
            b + 11 * u,
            10.5,
            GOLD,
            width=stress_reserve - 5 * u,
        )
        self.meter(
            Rect(tx + stress_reserve, b + 6 * u, right, b + 13 * u),
            char.stress / 100,
            GOLD,
        )
        state = (
            self.tr("ready")
            if is_deployable(char)
            else self.tr("recovering", days=char.recovery_turns)
        )
        arcade.draw_lrbt_rectangle_filled(
            portrait.left,
            portrait.right,
            portrait.bottom,
            portrait.bottom + 16 * u,
            (1, 10, 15, 225),
        )
        self.label(
            state,
            portrait.center[0],
            portrait.bottom + 8 * u,
            10.5,
            MINT if is_deployable(char) else RED,
            width=portrait.width - 5 * u,
            anchor_x="center",
            bold=True,
        )
        self.hit(
            rect,
            "agent_card",
            index,
            f"{char.name} · {role} · {state} · " + self.tr("double_click"),
        )
        if char.pending_points:
            point_rect = Rect(
                rect.right - 59 * u, t - 29 * u, rect.right - 17 * u, t - 7 * u
            )
            self.paint.panel(point_rect, GOLD)
            self.label(
                f"+{char.pending_points}",
                *point_rect.center,
                11,
                GOLD,
                bold=True,
                width=point_rect.width - 6 * u,
                anchor_x="center",
            )
            self.hit(point_rect, "squad_sheet", index, self.tr("upgrade"))

    self.button(
        Rect(r.left + 14 * u, r.bottom + 13 * u, r.right - 14 * u, r.bottom + 52 * u),
        self.tr("recruit_window"),
        "recruit_prompt",
        icon="recruit",
        color=MINT,
    )
    if len(gs.characters) > capacity:
        self.label(
            f"{self.roster_first+1}–{min(len(gs.characters),self.roster_first+capacity)}/{len(gs.characters)}",
            r.right - 15 * u,
            r.top - 23 * u,
            10,
            MUTED,
            anchor_x="right",
        )
        rail = Rect(r.right - 6 * u, bottom, r.right - 3 * u, top)
        thumb_height = rail.height * capacity / len(gs.characters)
        thumb_top = rail.top - self.roster_first / max(
            1, len(gs.characters) - capacity
        ) * (rail.height - thumb_height)
        arcade.draw_lrbt_rectangle_filled(
            rail.left, rail.right, rail.bottom, rail.top, (16, 49, 61, 255)
        )
        arcade.draw_lrbt_rectangle_filled(
            rail.left, rail.right, thumb_top - thumb_height, thumb_top, CYAN
        )
    if not gs.characters:
        self.label(
            self.tr("empty_roster"),
            *self.regions["roster"].center,
            16,
            MUTED,
            anchor_x="center",
            width=r.width - 30 * u,
        )
