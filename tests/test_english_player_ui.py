from pathlib import Path
import re

from game.gamestate import GameState
from game.i18n import DEFAULT_LANGUAGE, normalize_language, t
from game.ui.components.departments.copy import word
from game.ui.components.squad_copy import localized_squad_copy


ROOT = Path(__file__).resolve().parents[1]
PLAYER_COPY_FILES = (
    "game/mission_generation.py",
    "game/missions/objective_branches.py",
    "game/ui/screens/combat_recovery.py",
    "game/ui/screens/godot_combat_handoff_view.py",
    "game/ui/screens/research_lab.py",
    "game/ui/screens/world_map_view.py",
    "game/ui/widgets/critical_choice_highlight.py",
    "godot/combat_missions_ui/scripts/combat_mission_ui.gd",
    "godot/combat_missions_ui/scripts/visual_hud.gd",
)
FORBIDDEN_PLAYER_COPY = (
    "aucune mission",
    "campagne inchangée",
    "cible hors de portée",
    "cliquez une cible",
    "déploiement tactique",
    "escouade déployée",
    "jouera au retour",
    "rapport de combat",
    "réessayer",
    "réglages",
    "résultat appliqué",
    "sélectionné",
    "témoin est",
)


def test_english_is_the_only_runtime_language_even_for_legacy_saves():
    assert DEFAULT_LANGUAGE == "en"
    assert normalize_language(None) == "en"
    assert normalize_language("fr") == "en"
    assert GameState(ui_language="fr").ui_language == "en"
    assert t("hq.title", "fr") == t("hq.title", "en")


def test_legacy_arcade_copy_helpers_always_return_english():
    assert word("settings", "fr") == "SETTINGS"
    assert localized_squad_copy("ATTRIBUTES", "fr") == "ATTRIBUTES"
    assert localized_squad_copy("ATTRIBUTES", normalize_language("fr")) == "ATTRIBUTES"


def test_arcade_and_godot_player_copy_has_no_known_french_leaks():
    combined = "\n".join(
        (ROOT / relative).read_text(encoding="utf-8").lower()
        for relative in PLAYER_COPY_FILES
    )
    for phrase in FORBIDDEN_PLAYER_COPY:
        assert phrase not in combined, phrase


def test_settings_do_not_expose_engine_internals_to_players():
    source = (ROOT / "game/ui/components/utilities/settings.py").read_text(
        encoding="utf-8"
    )
    assert "GODOT EXECUTABLE" not in source
    assert "godot_bin_path" not in source
    assert "godot_bin_browse" not in source


def test_every_godot_script_literal_rejects_french_hud_copy():
    scripts = ROOT / "godot/combat_missions_ui/scripts"
    literals = []
    for path in scripts.rglob("*.gd"):
        source = path.read_text(encoding="utf-8")
        literals.extend(re.findall(r'"(?:\\.|[^"\\])*"', source))
    combined = "\n".join(literals).lower()
    forbidden = (
        "fin du tour",
        "phase ennemie",
        "phase joueur",
        "retraite [r]",
        "suivant [tab]",
        "tour %",
        "hors de portée",
        "vue bloquée",
    )
    for phrase in forbidden:
        assert phrase not in combined, phrase
    assert not re.search(r'"(?:pv|pa)(?:\s|%)', combined)

