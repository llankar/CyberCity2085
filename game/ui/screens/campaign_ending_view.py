"""Final campaign epilogue presentation."""

from __future__ import annotations

import arcade

from game.ui.theme.colors import colors


def build_ending_summary(game_state) -> dict:
    """Return a render-independent ending payload for tests and other clients."""

    ending = game_state.campaign.ending
    if ending is None:
        return {}
    return {
        "outcome_id": ending.outcome_id,
        "title": ending.title,
        "summary": ending.summary,
        "world_lines": list(ending.world_lines),
        "agent_epilogues": list(ending.agent_epilogues),
        "resolved_day": ending.resolved_day,
        "continue_action": "TitleView",
    }


class CampaignEndingView(arcade.View):
    """A restrained finale focused on consequences and remembered agents."""

    def __init__(self, game_state) -> None:
        super().__init__()
        self.game_state = game_state
        self.summary = build_ending_summary(game_state)
        self._elapsed = 0.0

    def on_show_view(self) -> None:
        arcade.set_background_color(colors.surface_elevated)

    def on_update(self, delta_time: float) -> None:
        self._elapsed += delta_time

    def on_draw(self) -> None:
        self.clear()
        width, height = self.window.width, self.window.height
        arcade.draw_text(
            "CYBERCITY 2085 // CAMPAIGN COMPLETE",
            width / 2,
            height - 72,
            colors.text_secondary,
            12,
            anchor_x="center",
        )
        arcade.draw_text(
            self.summary.get("title", "THE CITY REMEMBERS"),
            width / 2,
            height - 125,
            colors.accent_primary,
            28,
            bold=True,
            anchor_x="center",
        )
        arcade.draw_text(
            self.summary.get("summary", ""),
            width / 2,
            height - 180,
            colors.text_primary,
            13,
            width=min(820, width - 120),
            multiline=True,
            align="center",
            anchor_x="center",
        )

        left = max(60, width * 0.12)
        y = height - 275
        arcade.draw_text("THE WORLD", left, y, colors.accent_warning, 12, bold=True)
        y -= 28
        for line in self.summary.get("world_lines", []):
            arcade.draw_text(line, left, y, colors.text_secondary, 11)
            y -= 22

        right = width * 0.54
        y = height - 275
        arcade.draw_text("THE AGENTS", right, y, colors.accent_success, 12, bold=True)
        y -= 28
        for line in self.summary.get("agent_epilogues", [])[:8]:
            arcade.draw_text(
                line,
                right,
                y,
                colors.text_primary,
                10,
                width=max(280, width * 0.38),
                multiline=True,
            )
            y -= 38

        arcade.draw_text(
            "ENTER  RETURN TO TITLE",
            width / 2,
            42,
            colors.accent_primary,
            11,
            bold=True,
            anchor_x="center",
        )

    def on_key_press(self, key, modifiers) -> None:
        if key in (arcade.key.RETURN, arcade.key.ENTER, arcade.key.SPACE, arcade.key.ESCAPE):
            self._return_to_title()

    def _return_to_title(self) -> None:
        from game.ui.screens.title_screen import TitleView

        self.window.show_view(TitleView())
