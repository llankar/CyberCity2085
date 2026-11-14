"""Release architecture contracts for small domain and UI boundaries."""

from pathlib import Path

from game.campaign.service import record_story_mission_complete, tick_campaign
from game.missions.flow import (
    ensure_mission_templates,
    launch_selected_mission,
    resolve_mission_outcome,
)


ROOT = Path(__file__).resolve().parents[1]


def test_campaign_service_exposes_progression_without_moving_save_state() -> None:
    assert callable(tick_campaign)
    assert callable(record_story_mission_complete)


def test_mission_flow_exposes_board_launch_and_resolution() -> None:
    assert callable(ensure_mission_templates)
    assert callable(launch_selected_mission)
    assert callable(resolve_mission_outcome)


def test_release_path_views_live_in_ui_screens() -> None:
    screens = ROOT / "game" / "ui" / "screens"
    required = {
        "management_screen.py",
        "world_map_view.py",
        "mission_briefing_view.py",
        "battle_debrief_view.py",
        "campaign_ending_view.py",
    }
    assert required <= {path.name for path in screens.glob("*.py")}

    # The remaining legacy BattleView is an explicit compatibility shell; new
    # release screens must not be added to the root views module.
    legacy_source = (ROOT / "game" / "views.py").read_text(encoding="utf-8")
    for class_name in (
        "ManagementView",
        "MissionWorldMapView",
        "MissionBriefingView",
        "BattleDebriefView",
        "CampaignEndingView",
    ):
        assert f"class {class_name}" not in legacy_source
