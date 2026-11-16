"""CyberCity 2085 — game entry point."""

import argparse
import json
from pathlib import Path
import sys
from game.runtime import configure_runtime_directory


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="CyberCity 2085")
    parser.add_argument("--smoke-test", action="store_true", help="Validate packaged data/combat without a game window")
    parser.add_argument("--smoke-report", type=Path, help="Write smoke results as JSON")
    args = parser.parse_args(argv)
    if args.smoke_report and not args.smoke_test:
        parser.error("--smoke-report requires --smoke-test")
    report_path = args.smoke_report.resolve() if args.smoke_report else None
    configure_runtime_directory()
    if args.smoke_test:
        try:
            from game.release_smoke import run_smoke
            report = run_smoke()
        except Exception as error:
            report = {"status": "error", "error": f"{type(error).__name__}: {error}"}
        if report_path:
            report_path.parent.mkdir(parents=True, exist_ok=True)
            report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        if sys.stdout is not None:
            print(json.dumps(report))
        return 0 if report["status"] == "ok" else 1

    import warnings
    import arcade
    from arcade.exceptions import PerformanceWarning
    from game.ui.screens.settings_screen import load_settings
    from game.ui.screens.title_screen import TitleView

    warnings.filterwarnings("ignore", category=PerformanceWarning, module="arcade")
    window = arcade.Window(1920, 1000, "CyberCity 2085")
    load_settings()
    window.show_view(TitleView())
    arcade.run()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
