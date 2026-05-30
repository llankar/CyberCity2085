"""Agent Promotion Screen — shown between battle and debrief when agents level up.

Displays each promoted agent's portrait, old→new level, and stat gains.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import TYPE_CHECKING

import arcade

from game.ui import palette
from game.ui.panels import draw_panel

if TYPE_CHECKING:
    from game.gamestate import GameState
    from game.character import Character


@dataclass
class PromotionRecord:
    """Snapshot of one agent's level-up event."""
    character: "Character"
    old_level: int
    new_level: int
    portrait_path: str | None = None


class AgentPromotionView(arcade.View):
    """Sequenced promotion screen — shows one agent per page, CONTINUE advances."""

    def __init__(
        self,
        game_state: "GameState",
        promotions: list[PromotionRecord],
        next_view: arcade.View,
    ) -> None:
        super().__init__()
        self.game_state = game_state
        self.promotions = promotions
        self.next_view = next_view
        self._index = 0
        self._elapsed = 0.0
        self._portrait_cache: dict[str, arcade.Texture | None] = {}
        self._continue_rect: tuple[int, int, int, int] | None = None

    def on_show_view(self) -> None:
        arcade.set_background_color((4, 10, 18))
        self._load_portraits()
        from game.audio import SoundManager
        SoundManager.get().play("sfx_victory", 0.6)

    def _load_portraits(self) -> None:
        for rec in self.promotions:
            if rec.portrait_path and rec.portrait_path not in self._portrait_cache:
                try:
                    self._portrait_cache[rec.portrait_path] = arcade.load_texture(rec.portrait_path)
                except Exception:
                    self._portrait_cache[rec.portrait_path] = None

    def on_update(self, delta_time: float) -> None:
        self._elapsed += delta_time

    def on_draw(self) -> None:
        self.clear()
        if self._index >= len(self.promotions):
            self._advance()
            return
        rec = self.promotions[self._index]
        w, h = self.window.width, self.window.height
        self._draw_background(w, h)
        self._draw_promotion(rec, w, h)
        self._draw_footer(w, h)

    def _draw_background(self, w: int, h: int) -> None:
        arcade.draw_lrbt_rectangle_filled(0, w, 0, h, (4, 10, 18, 255))
        # Gold shimmer at top
        pulse = 0.6 + 0.4 * math.sin(self._elapsed * 2.5)
        arcade.draw_lrbt_rectangle_filled(0, w, h - 3, h, (255, 215, 60, int(180 * pulse)))

    def _draw_promotion(self, rec: PromotionRecord, w: int, h: int) -> None:
        cx = w // 2
        cy = h // 2

        # Panel
        pw, ph = 480, 320
        px, py = cx - pw // 2, cy - ph // 2
        draw_panel(px, py, pw, ph, "AGENT PROMOTION")

        # Gold star burst
        pulse = 0.85 + 0.15 * math.sin(self._elapsed * 3.0)
        for i in range(8):
            angle = math.radians(i * 45 + self._elapsed * 30)
            r = 55 * pulse
            ex = cx + math.cos(angle) * r
            ey = cy + 40 + math.sin(angle) * r
            arcade.draw_line(cx, cy + 40, ex, ey, (255, 215, 60, int(80 * pulse)), 2)

        # Portrait
        portrait = self._portrait_cache.get(rec.portrait_path or "")
        if portrait:
            arcade.draw_texture_rect(portrait, arcade.LBWH(cx - 48, cy - 10, 96, 120))
            arcade.draw_lrbt_rectangle_outline(cx - 48, cx + 48, cy - 10, cy + 110,
                                               (255, 215, 60, 200), 2)
        else:
            arcade.draw_lrbt_rectangle_filled(cx - 48, cx + 48, cy - 10, cy + 110,
                                              palette.ACTION_BUTTON_FILL)

        # Name
        arcade.draw_text(
            rec.character.name.upper(),
            cx, cy + 124,
            palette.HEADER, font_size=20, bold=True,
            anchor_x="center", anchor_y="center",
        )

        # Level badge
        arcade.draw_text(
            f"LVL {rec.old_level}  →  LVL {rec.new_level}",
            cx, cy - 28,
            (255, 215, 60), font_size=16, bold=True,
            anchor_x="center", anchor_y="center",
        )

        # Stat gains summary
        arcade.draw_text(
            "STAT GAINS",
            cx, cy - 54,
            palette.MUTED_TEXT, font_size=10, bold=True,
            anchor_x="center",
        )
        s = rec.character.stats
        stat_lines = [
            f"HP +10  (now {s.max_hp})",
            f"STR {s.str}  AGI {s.agi}  PSI {s.psi}",
            f"+5 skill points  +1 talent point",
        ]
        for i, line in enumerate(stat_lines):
            arcade.draw_text(
                line, cx, cy - 74 - i * 16,
                palette.TEXT, font_size=9,
                anchor_x="center",
            )

        # Progress indicator
        remaining = len(self.promotions) - self._index
        if len(self.promotions) > 1:
            arcade.draw_text(
                f"  {self._index + 1} / {len(self.promotions)}",
                px + pw - 12, py + ph - 24,
                palette.MUTED_TEXT, font_size=9,
                anchor_x="right", anchor_y="center",
            )

    def _draw_footer(self, w: int, h: int) -> None:
        fh = 68
        arcade.draw_lrbt_rectangle_filled(0, w, 0, fh, (0, 0, 0, 200))
        arcade.draw_line(0, fh, w, fh, palette.PANEL_BORDER, 2)
        bw, bh = 220, 44
        bx = (w - bw) // 2
        by = (fh - bh) // 2
        arcade.draw_lrbt_rectangle_filled(bx, bx + bw, by, by + bh, (20, 50, 28, 230))
        arcade.draw_line(bx, by + bh, bx + bw, by + bh, (255, 215, 60), 2)
        arcade.draw_text(
            "CONTINUE  [Enter]",
            bx + bw // 2, by + bh // 2,
            (255, 215, 60), font_size=13, bold=True,
            anchor_x="center", anchor_y="center",
        )
        self._continue_rect = (bx, by, bx + bw, by + bh)

    def on_key_press(self, key, modifiers) -> None:
        if key in (arcade.key.RETURN, arcade.key.ENTER, arcade.key.SPACE, arcade.key.ESCAPE):
            self._advance()

    def on_mouse_press(self, x, y, button, modifiers) -> None:
        if self._continue_rect:
            l, b, r, t = self._continue_rect
            if l <= x <= r and b <= y <= t:
                self._advance()

    def _advance(self) -> None:
        self._index += 1
        self._elapsed = 0.0
        if self._index >= len(self.promotions):
            from game.audio import SoundManager
            SoundManager.get().play("sfx_deploy", 0.5)
            self.window.show_view(self.next_view)
        else:
            from game.audio import SoundManager
            SoundManager.get().play("sfx_victory", 0.5)
