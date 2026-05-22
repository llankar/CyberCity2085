"""Contract tests for mandatory four-zone screen layouts."""

from game.ui.layouts import (
    DecisionLayout,
    OverviewLayout,
    RosterLayout,
    TacticalLayout,
    required_zones,
)


def test_layout_templates_expose_required_zone_fields() -> None:
    for template in (OverviewLayout, DecisionLayout, RosterLayout, TacticalLayout):
        for field_name in required_zones():
            value = getattr(template, field_name)
            assert value.startswith("Zone")


def test_layout_templates_share_visual_grammar() -> None:
    baseline = (
        OverviewLayout.zone_1_global_state,
        OverviewLayout.zone_2_selected_element,
        OverviewLayout.zone_3_available_actions,
        OverviewLayout.zone_4_predicted_consequences,
    )
    for template in (DecisionLayout, RosterLayout, TacticalLayout):
        assert (
            template.zone_1_global_state,
            template.zone_2_selected_element,
            template.zone_3_available_actions,
            template.zone_4_predicted_consequences,
        ) == baseline
