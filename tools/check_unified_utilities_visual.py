"""Native Arcade QA of utility views and narrative transitions at three resolutions."""

import argparse
import json
from pathlib import Path
from unittest.mock import patch
from types import SimpleNamespace
import arcade
from tools.check_squad_command_visual import fixture
from game.ui.screens.settings_screen import SettingsView, SettingsState
from game.ui.screens.new_game_screen import NewGameSetupView
from game.ui.screens.agent_promotion_view import AgentPromotionView, PromotionRecord
from game.ui.screens.campaign_ending_view import CampaignEndingView
from game.ui.screens.battle_debrief_view import BattleDebriefView, AgentDebriefStat
from game.ui.screens.text_mission_view import TextMissionView
from game.ui.screens.godot_combat_handoff_view import GodotCombatHandoffView
from game.text_missions.text_mission_library import all_text_missions
from game.campaign.ending import evaluate_campaign_ending
from game.ui.portraits import portrait_path_for_character
from game.ui.theme.typography import set_text_size


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="work/unified-ui")
    args = parser.parse_args()
    output = Path(args.output)
    output.mkdir(parents=True, exist_ok=True)
    window = arcade.Window(
        1280, 720, "Visual Unification · Utility QA", visible=False, antialiasing=False
    )
    gs, management = fixture()
    gs.ui_language = "fr"
    gs.campaign.ending = evaluate_campaign_ending(gs)
    stats = [
        AgentDebriefStat(
            c.name,
            c.role,
            portrait_path_for_character(c),
            damage_dealt=10 + i,
            actions_used=4,
            kills=i % 3,
            xp_gained=5,
        )
        for i, c in enumerate(gs.characters)
    ]
    with patch(
        "game.ui.screens.settings_screen.load_settings", return_value=SettingsState()
    ):
        settings = SettingsView(management)
    new = NewGameSetupView()
    promotion = AgentPromotionView(
        gs,
        [
            PromotionRecord(
                gs.characters[0], 1, 2, portrait_path_for_character(gs.characters[0])
            )
        ],
        management,
    )
    ending = CampaignEndingView(gs)
    debrief = BattleDebriefView(gs, True, gs.mission_templates[0], stats)
    narrative = TextMissionView(gs, all_text_missions()[0])
    narrative.on_show_view()

    handoff = GodotCombatHandoffView(
        gs,
        gs.mission_templates[0],
        SimpleNamespace(
            launched=False,
            message="Executable unavailable in isolated QA fixture",
            process=None,
            process_pid=None,
        ),
    )

    def show(v):
        with patch.object(v, "on_show_view", lambda: None):
            window.show_view(v)

    def draw(v, name):
        window.switch_to()
        window.default_camera.use()
        v.on_draw()
        window.ctx.finish()
        hits = (
            v._modal_hits
            if name.startswith("recruit")
            else getattr(v, "_visual_hits", v._hits)
        )
        assert all(
            0 <= h.left < h.right <= window.width
            and 0 <= h.bottom < h.top <= window.height
            for h in hits
        ), (name, window.width)
        arcade.get_image(0, 0, window.width, window.height).save(
            output / f"{name}-{window.width}x{window.height}.png"
        )

    def click(v, action, data=None, modal=False):
        window.switch_to()
        window.default_camera.use()
        v.on_draw()
        window.ctx.finish()
        hits = v._modal_hits if modal else getattr(v, "_visual_hits", v._hits)
        h = next(
            h for h in hits if h.action == action and (data is None or h.data == data)
        )
        x, y = (h.left + h.right) / 2, (h.bottom + h.top) / 2
        v.on_mouse_motion(x, y, 0, 0)
        v.on_mouse_press(x, y, arcade.MOUSE_BUTTON_LEFT, 0)

    checks = []
    for w, h in [(1280, 720), (1920, 1080), (2560, 1440)]:
        window.set_size(w, h)
        window.dispatch_events()
        window.flip()
        set_text_size("medium")
        for name, v in [
            ("settings", settings),
            ("new-game", new),
            ("promotion", promotion),
            ("ending", ending),
            ("debrief", debrief),
            ("handoff", handoff),
        ]:
            show(v)
            draw(v, name)
        show(management)
        management._open_hub_room("squad")
        management._do_recruit_prompt()
        draw(management, "recruitment")
        click(management, "recruit_preview", 1, True)
        draw(management, "recruitment-selected")
        assert management._recruitment_deck.selection["candidate"] == 1
        management.on_key_press(arcade.key.ESCAPE, 0)
        assert not management.recruit_window_open
        show(narrative)
        narrative._state = "reading"
        narrative._scene_id = narrative._mission.opening_scene_id
        draw(narrative, "narrative")
        click(narrative, "choose", 0)
        assert narrative._state == "agent_select"
        draw(narrative, "narrative-agent")
        narrative.on_key_press(arcade.key.DOWN, 0)
        assert narrative._selected_agent_idx == 1
        click(narrative, "cancel_agent")
        assert narrative._state == "reading"
        click(narrative, "choose", 0)
        click(narrative, "confirm_agent")
        assert narrative._state == "result"
        draw(narrative, "narrative-result")
        click(narrative, "continue_result")
        assert narrative._state in {"reading", "complete"}
        draw(narrative, "narrative-outcome")
        checks.append([w, h])
    show(handoff)
    draw(handoff, "handoff")
    with patch.object(handoff, "_retry_godot") as retry:
        click(handoff, "handoff_key", arcade.key.R)
        retry.assert_called_once()
    show(debrief)
    draw(debrief, "debrief")
    click(debrief, "report_agent", 1)
    draw(debrief, "debrief-agent")
    assert debrief._visual_deck.selection["report_agent"] == 1
    click(debrief, "report_mission")
    assert "report_agent" not in debrief._visual_deck.selection
    show(settings)
    draw(settings, "settings")
    settings._visual_deck.hover = ("toggle_grid", None)
    before = settings._settings.show_grid
    settings.on_key_press(arcade.key.SPACE, 0)
    assert (
        settings._settings.show_grid != before
    ), "Keyboard action must activate exactly once"
    for action, field in [
        ("toggle_grid", "show_grid"),
        ("toggle_contrast", "high_contrast"),
        ("toggle_audio", "audio_enabled"),
        ("toggle_shake", "camera_shake"),
        ("toggle_motion", "reduced_motion"),
    ]:
        before = getattr(settings._settings, field)
        click(settings, action)
        assert getattr(settings._settings, field) != before
        draw(settings, "settings")
    with patch(
        "game.ui.screens.settings_screen._browse_for_godot_executable",
        return_value="/tmp/Godot",
    ), patch("game.ui.screens.settings_screen._persist_godot_bin_path"):
        click(settings, "godot_bin_browse")
        assert settings._settings.godot_bin_path == "/tmp/Godot"
        draw(settings, "settings")
        click(settings, "godot_bin_clear")
        assert settings._settings.godot_bin_path == ""
    with patch("game.ui.screens.settings_screen.save_settings") as saved, patch(
        "game.ui.screens.settings_screen.apply_settings"
    ) as applied:
        draw(settings, "settings")
        click(settings, "save_apply")
        saved.assert_called_once()
        applied.assert_called_once()
    show(new)
    draw(new, "new-game")
    before = new._corp
    new.on_key_press(arcade.key.BACKSPACE, 0)
    assert new._corp == before[:-1]
    new.on_key_press(arcade.key.TAB, 0)
    assert new._focus == 1
    bounds = new._hit_diffs[2]
    new.on_mouse_press((bounds[0] + bounds[2]) / 2, (bounds[1] + bounds[3]) / 2, 1, 0)
    assert new._diff == 2
    with patch.object(new, "_start_game") as start:
        draw(new, "new-game")
        hit = new._hit_start
        new.on_mouse_press((hit[0] + hit[2]) / 2, (hit[1] + hit[3]) / 2, 1, 0)
        start.assert_called_once()
    # Accessibility and English with the actual same renderer, no separate fallback.
    window.set_size(1280, 720)
    window.dispatch_events()
    window.flip()
    set_text_size("large")
    gs.ui_language = "en"
    for name, v in [
        ("settings", settings),
        ("promotion", promotion),
        ("ending", ending),
        ("debrief", debrief),
        ("handoff", handoff),
        ("narrative", narrative),
    ]:
        show(v)
        draw(v, name + "-large-en")
    print(
        json.dumps(
            {
                "resolutions": checks,
                "settings_actions": True,
                "recruit_preview": True,
                "narrative_state_machine": True,
                "new_game_input": True,
                "large_text": True,
            }
        )
    )
    window.close()


if __name__ == "__main__":
    main()
