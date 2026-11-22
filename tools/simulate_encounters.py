"""Run with python -m tools.simulate_encounters --output runtime/encounter_qa.json."""

import argparse
from collections import Counter
import json
from pathlib import Path
from hashlib import sha256

from game.combat.encounter_qa import simulate_action_coverage, simulate_encounter
from game.combat.tactical_identity import profile_for_theme


OBJECTIVES = ("extract", "data_theft", "sabotage", "recon_scan", "civilian_rescue", "defend", "containment", "assassination")


def evaluate_action_dominance(action_totals, *, max_share=0.70):
    """Bound the representative rifle policy without judging specialist probes."""
    total = sum(action_totals.values())
    shares = {action: count / total for action, count in action_totals.items()} if total else {}
    required = {"move", "fire", "defend", "objective"}
    missing = sorted(required - {action for action, count in action_totals.items() if count > 0})
    dominant = sorted(action for action, share in shares.items() if share > max_share)
    return {
        "status": "PASS" if total and not missing and not dominant else "FAIL",
        "max_share": max_share,
        "missing_policy_actions": missing,
        "dominant_actions": dominant,
    }


def combat_source_fingerprint():
    files = [*Path("game/combat").glob("*.py"), Path(__file__), Path("game/campaign/story_missions.py"),
             *(Path("game") / name for name in ("combat_system.py", "unit.py", "cover_system.py", "map_terrain.py",
                                                "map_geometry.py", "mission_objectives.py", "enemy_themes.py", "stats.py",
                                                "mission_generation.py", "mission_templates.py", "battle_maps.py"))]
    digest = sha256()
    for path in sorted(files):
        digest.update(path.name.encode())
        digest.update(path.read_bytes())
    return digest.hexdigest()


def story_rows(args):
    from game.campaign.story_missions import STORY_MISSIONS
    from game.mission_generation import story_mission_to_template
    from game.gamestate import GameState
    from game.battle_maps import select_battle_map_entry
    state = GameState()
    rows = []
    for story in STORY_MISSIONS:
        mission = story_mission_to_template(story, state)
        entry = select_battle_map_entry(mission)
        for seed in range(args.seeds):
            row = simulate_encounter(theme=mission.enemy_theme, level=4, risk=mission.risk_level,
                                     count=mission.starting_enemy_count, seed=seed,
                                     policy="objective_counterplay", max_turns=60,
                                     map_path=entry.path, mission_template=mission)
            row["mission_template_sha256"] = sha256(json.dumps(mission.to_dict(), sort_keys=True).encode()).hexdigest()
            rows.append(row)
        print(json.dumps({"story_checked": story.id, "runs": len(rows)}), flush=True)
    return rows


def authored_rows(args):
    from game.battle_maps import build_battle_map_catalog
    rows = []
    entries = build_battle_map_catalog()
    for index, entry in enumerate(entries):
        themes = ("corp_samurai", "corp_37_robot", "novatek_hybrid") if entry.environment == "city" else ("starver", "mutant", "raider")
        for objective in ([args.objective] if args.objective else ("eliminate", *OBJECTIVES)):
            for seed in range(args.seeds):
                try:
                    row = simulate_encounter(theme=themes[index % len(themes)], level=4, risk=5, count=6,
                                             seed=seed, policy="objective_counterplay", map_path=entry.path,
                                             objective_kind=objective, max_turns=60)
                except (AssertionError, ValueError) as error:
                    row = dict(map_file=entry.filename, objective_kind=objective, seed=seed,
                               outcome="error", error=str(error))
                rows.append(row)
        if (index + 1) % 10 == 0:
            print(json.dumps({"maps_checked": index+1, "maps_total": len(entries), "runs": len(rows)}), flush=True)
    return rows


def retest_limited_rows(path):
    baseline = json.loads(path.read_text(encoding="utf-8"))
    rows = []
    for old in baseline["runs"]:
        if old["outcome"] != "turn_limit":
            continue
        if old.get("mission_id", "encounter_qa") != "encounter_qa":
            raise ValueError("Story template replays require the story scenario; generic limited replay cannot preserve their rules")
        if not old.get("map_file") or Path(old["map_file"]).name != old["map_file"]:
            raise ValueError("Limited-case replay requires an authored map filename")
        arguments = {key: old[key] for key in ("theme", "level", "risk", "count", "seed", "policy", "layout", "objective_kind")}
        rows.append(simulate_encounter(**arguments, map_path=Path("assets/maps") / old["map_file"], max_turns=old["turns"]))
        if len(rows) % 5 == 0:
            print(json.dumps({"limited_cases_checked": len(rows)}), flush=True)
    return rows, baseline["combat_sources_sha256"]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--seeds", type=int, default=3)
    parser.add_argument("--scenario", choices=("elimination", "objectives", "authored", "story"), default="elimination")
    parser.add_argument("--objective", choices=("eliminate", *OBJECTIVES))
    parser.add_argument("--retest-limits", type=Path, help="Replay only limited authored cases with their original turn caps")
    args = parser.parse_args()
    if args.scenario == "story" and (args.objective or args.retest_limits):
        parser.error("story scenario uses its authored objectives and cannot use generic limited replay")
    if not 1 <= args.seeds <= 100:
        parser.error("--seeds must be 1..100")
    fingerprint = combat_source_fingerprint()
    objectives = ([args.objective] if args.objective else OBJECTIVES) if args.scenario == "objectives" else (args.objective or "eliminate",)
    policies = ("objective", "objective_counterplay") if args.scenario == "objectives" else ("focus", "counterplay")
    baseline_fingerprint = None
    if args.retest_limits:
        rows, baseline_fingerprint = retest_limited_rows(args.retest_limits)
    elif args.scenario == "story":
        rows = story_rows(args)
    elif args.scenario == "authored":
        rows = authored_rows(args)
    else:
        rows = [simulate_encounter(theme=theme, level=level, risk=risk, count=count,
                                   seed=seed, policy=policy, layout=layout, objective_kind=objective)
                for objective in objectives
                for theme in ("starver", "mutant", "raider", "corp_samurai", "corp_37_robot", "novatek_hybrid")
                for level, risk, count in ((1, 2, 3), (4, 5, 6), (7, 8, 8))
                for seed in range(args.seeds) for policy in policies
                for layout in ("open", "cover")]
    themes = sorted({row.get("theme") for row in rows if row.get("theme")})
    action_totals = Counter()
    for row in rows:
        action_totals.update(row.get("player_actions", {}))
    total_decisions = sum(action_totals.values())
    action_distribution = {
        action: {
            "count": count,
            "share": round(count / total_decisions, 6) if total_decisions else 0.0,
        }
        for action, count in sorted(action_totals.items())
    }
    coverage = {
        "objectives": sorted({row.get("objective_kind") for row in rows if row.get("objective_kind")}),
        "themes": themes,
        "doctrines": sorted({profile_for_theme(theme).key for theme in themes}),
        "enemy_roles": sorted({role for row in rows for role in row.get("roles", {})}),
        "player_actions": list(simulate_action_coverage()),
    }
    dominance_check = (
        evaluate_action_dominance(action_totals)
        if args.scenario == "objectives" and not args.retest_limits
        else {"status": "NOT_APPLICABLE"}
    )
    report = {"scope": "Fixed four-rifle balance squad plus isolated real-action probes; not campaign or human balance proof", "scenario": args.scenario,
              "combat_sources_sha256": fingerprint,
              "baseline_sources_sha256": baseline_fingerprint,
              "limited_retest_only": args.retest_limits is not None,
              "coverage": coverage,
              "action_distribution": action_distribution,
              "dominance_check": dominance_check,
              "summary": dict(Counter(row["outcome"] for row in rows)), "runs": rows}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"runs": len(rows), **report["summary"]}))
    return int(bool(report["summary"].get("error")) or dominance_check["status"] == "FAIL")


if __name__ == "__main__":
    raise SystemExit(main())
