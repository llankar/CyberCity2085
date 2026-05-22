from game.ui.components.foundation import Badge, Button, Divider, Panel, ProgressBar, Tooltip
from game.ui.theme import colors, radii, spacing


def test_semantic_color_tokens_exist() -> None:
    assert colors.surface_primary
    assert colors.text_secondary
    assert colors.accent_warning


def test_foundation_primitives_instantiable() -> None:
    panel = Panel(padding=spacing.section_gap, elevation=10)
    button = Button(corner_radius=radii.control, border_width=1)
    badge = Badge(text_size=9)
    divider = Divider(thickness=1)
    progress = ProgressBar(thickness=6)
    tooltip = Tooltip(text_size=9, padding=spacing.stack_default)
    assert panel.padding > 0
    assert button.corner_radius > 0
    assert badge.text_size > 0
    assert divider.thickness > 0
    assert progress.thickness > 0
    assert tooltip.padding > 0
