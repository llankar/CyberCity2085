from pathlib import Path
import os
import re
import subprocess

from game.gamestate import GameState
from game.i18n import DEFAULT_LANGUAGE, normalize_language, t
from game.narrative.mission_briefing_conventions import (
    MAX_EMOTIONAL_IMPACT_CHARS,
    build_short_emotional_impact,
    translate_legacy_briefing_text,
)
from game.ui.components.departments.copy import word
from game.ui.components.squad_copy import localized_squad_copy


ROOT = Path(__file__).resolve().parents[1]
PLAYER_COPY_FILES = (
    "game/mission_generation.py",
    "game/missions/objective_branches.py",
    "game/ui/components/briefing_content.py",
    "game/ui/screens/battle_debrief_view.py",
    "game/ui/screens/campaign_ending_view.py",
    "game/ui/screens/combat_recovery.py",
    "game/ui/screens/godot_combat_handoff_view.py",
    "game/ui/screens/mission_briefing_view.py",
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
    "risque ",
    "ennemi //",
    "rapport de combat",
    "réessayer",
    "réglages",
    "résultat appliqué",
    "sélectionné",
    "témoin est",
)


def test_embedded_legacy_briefing_translates_the_complete_emotional_hint():
    legacy = (
        "After-action note: Risque de séquelles émotionnelles durables pour l'escouade "
        "(séquelles émotionnelles probables)."
    )
    assert translate_legacy_briefing_text(legacy) == (
        "After-action note: Risk of lasting emotional scars for the squad (likely emotional scars)."
    )
    assert translate_legacy_briefing_text(
        "Risque de séquelles émotionnelles durables pour l'escouade"
    ) == "Risk of lasting emotional scars for the squad (likely emotional scars)"


def test_long_briefing_impact_keeps_whole_words_within_the_display_limit():
    intro = "Uncertain support from local contacts might leave the squad exposed after the operation"
    summary = build_short_emotional_impact("high", f"{intro} ends unexpectedly.")
    assert summary == f"{intro} ends..."
    assert len(summary) <= MAX_EMOTIONAL_IMPACT_CHARS


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
    world_map = (ROOT / "game/ui/screens/world_map_view.py").read_text(encoding="utf-8")
    assert 'f"RISK {mission.risk_level}' in world_map
    assert "{mission.duration_days} DAYS" in world_map
    assert 'paragraph("HOSTILES // "' in world_map


def test_settings_do_not_expose_engine_internals_to_players():
    source = (ROOT / "game/ui/components/utilities/settings.py").read_text(
        encoding="utf-8"
    )
    assert "GODOT EXECUTABLE" not in source
    assert "godot_bin_path" not in source
    assert "godot_bin_browse" not in source
    assert "F4 then B   Hangar missions" in source
    assert "B   Mission / N   Recruitment" not in source


def test_every_godot_literal_rejects_french_player_copy():
    godot_root = ROOT / "godot"
    literals = []
    source_extensions = {".gd", ".tscn", ".tres", ".cfg", ".json", ".txt"}
    for path in godot_root.rglob("*"):
        if (
            not path.is_file()
            or path.suffix.lower() not in source_extensions
            or ".godot" in path.parts
        ):
            continue
        source = path.read_text(encoding="utf-8")
        literals.extend(re.findall(r'"(?:\\.|[^"\\])*"', source))
    combined = "\n".join(literals).lower()
    forbidden = (
        "fin du tour",
        "interface classique",
        "journal de combat",
        '"journal [l]"',
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


def test_godot_player_copy_does_not_expose_debug_or_engine_labels():
    source = (
        ROOT / "godot/combat_missions_ui/scripts/combat_mission_ui.gd"
    ).read_text(encoding="utf-8")
    visible_handoff = source.split("func _draw_handoff_scene", 1)[1].split(
        "# ─── Input", 1
    )[0]
    assert "GODOT COMBAT UI" not in visible_handoff
    assert "No agents in handoff" not in visible_handoff
    assert 'status_line += " | WALL TEST' not in source
    assert '_log_event("WALL TEST' not in source


def test_godot_project_scripts_parse_when_native_editor_is_available(tmp_path):
    from game.combat.godot_bridge import find_godot_executable

    executable = find_godot_executable()
    if not executable:
        import pytest

        pytest.skip("Godot executable unavailable")
    editor_env = os.environ.copy()
    if os.name == "nt":
        editor_env["APPDATA"] = str(tmp_path)
    result = subprocess.run(
        [
            executable,
            "--headless",
            "--path",
            str(ROOT / "godot/combat_missions_ui"),
            "--editor",
            "--quit",
        ],
        capture_output=True,
        env=editor_env,
        text=True,
        timeout=30,
    )
    output = result.stdout + result.stderr
    assert result.returncode == 0, output
    assert "SCRIPT ERROR" not in output, output
    assert "Parse Error" not in output, output

