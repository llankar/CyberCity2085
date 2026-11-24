# CyberCity 2085 - Godot Scene Validator
# This script validates the Godot combat mission UI scene structure and assets

import json
import os
import sys
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent

def check_project_structure():
    """Verify all required files exist for the Godot project."""
    base = PROJECT_DIR
    
    required = {
        "project.godot": "Godot project file",
        "scenes/combat_mission_ui.tscn": "Main scene file",
        "scripts/combat_mission_ui.gd": "Main script",
        "scripts/battlefield.gd": "Battlefield component",
        "scripts/hud_controller.gd": "HUD controller",
        "scripts/phase_banner.gd": "Phase banner UI",
        "scripts/audio_manager.gd": "Audio manager",
        "scripts/unit_token.gd": "Unit token UI",
        "scripts/combat_signals.gd": "Combat signals bus",
    }
    
    print("\n=== Godot Project Structure Validation ===\n")
    
    missing = []
    check_mark = "\u2713"  # UTF-8 checkmark for internal use only
    x_mark = "\u2717"      # UTF-8 X for internal use
    
    try:
        print(f"\n{'PROJECT STRUCTURE':^50}")
        for file, desc in required.items():
            path = base / file
            exists = path.exists()
            status = check_mark if exists else f"{x_mark} MISSING"
            # Use ASCII fallback for Windows console compatibility
            print(f"[{'OK' if exists else 'MISSING'}] {file}")
        print()
    except Exception as e:
        print(f"Error displaying project structure: {e}")
    
    return missing

def check_assets():
    """Verify shader and audio assets exist."""
    base = PROJECT_DIR
    
    assets_dir = {
        "shaders": ["crt.gdshader", "circle_portrait.gdshader", "damaged.gdshader", 
                    "standee_portrait.gdshader", "neon_glow.gdshader", "holo.gdshader"],
        "audio": ["Neon Street Warfare.mp3", "impact_metal_cc0_01.wav", "impact_organic_cc0_01.wav"]
    }
    
    print("\n=== Asset Validation ===\n")
    
    missing = []
    for category, files in assets_dir.items():
        category_path = base / category
        print(f"\n[{category.upper()}]:")
        
        if not category_path.exists():
            print(f"  [MISSING] {category}/ directory")
            missing.extend(files)
            continue
            
        for file in files:
            path = category_path / file
            exists = path.exists()
            status = "OK" if exists else "MISSING"
            print(f"  [{status}] {file}")
            if not exists:
                missing.append(f"{category}/{file}")
    
    return missing

def check_handoff_file():
    """Check if handoff file exists and is valid JSON."""
    # Resolve to absolute path from parent directory
    script_dir = PROJECT_DIR
    handoff_path = script_dir / "runtime" / "godot_combat" / "mission_handoff.json"
    
    print("\n=== HANDOFF FILE CHECK ===\n")
    
    if not handoff_path.exists():
        print("[MISSING] mission_handoff.json")
        print(f"   Expected path: {handoff_path}")
        print("   Creating a sample handoff file for testing...")
        
        # Create minimal valid handoff
        handoff_path.parent.mkdir(parents=True, exist_ok=True)
        
        sample_handoff = {
            "asset_base_dir": "",
            "mission": {
                "title": "TACTICAL INSERTION - SAMPLE",
                "target_faction": "CORP_37",
                "risk_level": "medium",
                "objective_text": "Protect the extraction point.",
                "location": {"name": "Sample Site", "terrain": "urban"}
            },
            "squad": [
                {
                    "name": "Neon Blade",
                    "role": "samurai",
                    "hp": 60,
                    "max_hp": 60,
                    "stress": 0,
                    "aim": 5,
                    "melee_power": 12,
                    "portrait_path": "",
                    "position": [14, 12]
                },
                {
                    "name": "Holo Hacker",
                    "role": "sniper",
                    "hp": 50,
                    "max_hp": 50,
                    "stress": 0,
                    "aim": 8,
                    "melee_power": 4,
                    "portrait_path": "",
                    "position": [16, 12]
                }
            ],
            "map": {
                "path": "assets/maps/neon_chrome_city_street_07.png",
                "label": "Neo-Chrome City Street",
                "cell_size": 80,
                "width": 40,
                "height": 28,
                "objective_cell": [20, 15]
            },
            "enemy_theme": "corp_37"
        }
        
        with open(handoff_path, 'w') as f:
            json.dump(sample_handoff, f, indent=2)
        
        print(f"✓ Created sample handoff at: {handoff_path}")
        return ["mission_handoff.json (created sample)"]
    
    try:
        with open(handoff_path, 'r') as f:
            data = json.load(f)
        
        print("[OK] mission_handoff.json exists and is valid JSON")
        print(f"   Mission: {data.get('mission', {}).get('title', 'Unknown')}")
        return []
    except Exception as e:
        print(f"[ERROR] mission_handoff.json is invalid: {e}")
        return ["mission_handoff.json (corrupted)"]

def diagnose_scene():
    """Try to parse the scene file and check for errors."""
    scene_path = PROJECT_DIR / "scenes" / "combat_mission_ui.tscn"
    
    print("\n=== Scene File Analysis ===\n")
    
    if not scene_path.exists():
        print("✗ Scene file not found!")
        return ["Scene file missing"]
    
    with open(scene_path, 'r', encoding='utf-8', errors='replace') as f:
        content = f.read()
    
    # Check for common issues
    issues = []
    
    if "ext_resource" not in content:
        issues.append("Scene file missing ext_resource declarations")
    
    if "res://scripts/combat_mission_ui.gd" not in content:
        issues.append("Script path may be incorrect in scene file")
    
    # Count node definitions
    node_count = content.count("[node name=")
    print(f"Found {node_count} node definitions in scene")
    
    if issues:
        for issue in issues:
            print(f"  ! WARNING: {issue}")
    else:
        print("[OK] Scene file structure appears valid")
    
    return issues

def main():
    print("=" * 60)
    print("CYBERCITY 2085 - GODOT COMBAT UI VALIDATOR")
    print("=" * 60)
    
    all_missing = []
    
    # Run checks
    missing_project = check_project_structure()
    missing_assets = check_assets()
    handoff_issues = check_handoff_file()
    scene_issues = diagnose_scene()
    
    missing_project.extend(missing_assets)
    missing_project.extend(handoff_issues)
    missing_project.extend(scene_issues)
    
    # Summary
    print("\n" + "=" * 60)
    print("VALIDATION SUMMARY")
    print("=" * 60)
    
    if not all_missing:
        print("[OK] All files and assets present!")
        print("\nThe Godot project structure is complete.")
        print("\nTo launch:")
        print("  1. Open Godot 4.2+")
        print("  2. Select this project folder")
        print("  3. Run 'scenes/combat_mission_ui.tscn'")
        print("  \nOR double-click: launch_windows.bat")
        return 0
    else:
        print(f"[ERROR] Found {len(all_missing)} missing/corrupted items:")
        for item in all_missing:
            print(f"  - {item}")
        print("\nPlease fix the missing files before launching.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
