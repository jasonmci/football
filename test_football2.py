#!/usr/bin/env python3
"""
Test script for the new football2 YAML loader.

This will help us validate that our new system works with existing formation files.
"""

import sys
from pathlib import Path

# Add the src directory to the path so we can import football2
src_path = Path(__file__).parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from football2.football.yaml_loader import FormationLoader

def test_formation_loading():
    """Test loading formations from the existing YAML files."""

    # Test with both offensive and defensive formations
    formations_to_test = [
        ("data/formations/offense/singleback_11.yaml", "Offensive"),
        ("data/formations/defense/bear46.yaml", "Defensive")
    ]

    for formation_file, formation_type in formations_to_test:
        formation_path = Path(formation_file)

        if not formation_path.exists():
            print(f"Formation file not found: {formation_path}")
            continue

        try:
            loader = FormationLoader()
            formation = loader.load_formation(formation_path)

            print(f"\n✅ Successfully loaded {formation_type.lower()} formation: {formation.name}")
            print(f"   Players: {len(formation.roles)}")

            # Print each role
            for role_name, role in formation.roles.items():
                coord_str = f" at {role.coordinate}" if role.coordinate else ""
                align_str = f" ({role.alignment})" if role.alignment else ""
                print(f"   {role_name}: {role.position.name} {role.lane.value}/{role.depth}{align_str}{coord_str}")

        except Exception as e:
            print(f"❌ Error loading {formation_type.lower()} formation: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    test_formation_loading()
