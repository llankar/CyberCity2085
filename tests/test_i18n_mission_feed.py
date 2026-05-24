from game.i18n import t
from game.mission_generation import _build_emotional_impact_hint
from game.mission_templates import MissionTemplate
from game.ui.widgets.mission_impact_summary import impact_hint_text
from game.ui.widgets.narrative.feed_item import readable_relative_timestamp


def test_i18n_fallback_missing_key_returns_key():
    assert t("missing.key", "en") == "missing.key"


def test_mission_impact_rendering_is_consistent_for_language():
    mission = MissionTemplate(
        id="m1",
        title="Test",
        objective_text="Brief",
        target_faction="corp",
        district="Neo",
        objective_type="extract",
        risk_level=4,
        district_pressure={},
        fund_reward=10,
        duration_days=2,
        starting_enemy_count=2,
        tags=[],
        possible_complications=["a"],
    )
    hint = _build_emotional_impact_hint(mission, "en")
    rendered = impact_hint_text(hint, "en")
    assert "Expected human impact" in rendered
    assert "high" in rendered or "critical" in rendered


def test_feed_timestamp_translation():
    assert readable_relative_timestamp(0, "en") == "just now"
