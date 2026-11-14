"""Render battle frames without input injection or visible/activated windows."""

import argparse
from pathlib import Path
import sys
import random


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("runtime/tactical-qa"))
    parser.add_argument("--backend", choices=("egl", "hidden"), default="egl",
                        help="EGL headless context or explicit invisible native GL context")
    args = parser.parse_args()
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    import pyglet
    pyglet.options["headless"] = args.backend == "egl"
    pyglet.options["audio"] = ("silent",)
    try:
        import arcade
    except ImportError as error:
        raise SystemExit(f"Requested rendering backend unavailable; no fallback: {error}") from error
    from game.gamestate import GameState
    from game.recruitment import recruit_agent
    from game.mission_templates import create_mission_templates
    from game.views import BattleView

    state = GameState()
    random.seed(2085)
    agent = recruit_agent(state.characters, "sniper", "Echo QA")
    state.selected_agent_names = [agent.name]
    mission = next(m for m in create_mission_templates() if m.id == "extraction")
    window = arcade.Window(1280, 720, "Off-screen tactical QA", visible=False)
    try:
        view = BattleView(state)
        window.show_view(view)
        view.setup(mission)
        args.output.mkdir(parents=True, exist_ok=True)
        for name, deploying in (("deployment", True), ("combat", False)):
            view._deploying = deploying
            view._intro_active = False
            if not deploying:
                view.combat_engine.start_player_turn()
                view._sync_view_from_combat_state()
                view.message = "Reach the witness. Clear nearby hostiles before interaction."
            view.on_draw()
            arcade.get_image(0, 0, 1280, 720).save(args.output / f"{name}.png")
        print(f"Production tactical frames rendered to {args.output}")
    finally:
        window.close()


if __name__ == "__main__":
    main()
