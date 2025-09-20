#!/usr/bin/env python3
"""
Comprehensive test script for loading all football formations.

This will test our football2 system against all existing YAML files
and help us identify any issues or improvements needed.
"""

import sys
from pathlib import Path
from football.yaml_loader import load_all_formations

# Add the src directory to the path so we can import football2
src_path = Path(__file__).parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))


def test_all_formations():
    """Test loading all formations from the formations directory."""

    formations_path = Path("data/formations")

    if not formations_path.exists():
        print(f"❌ Formations directory not found: {formations_path}")
        return

    try:
        print("🏈 Loading all football formations...\n")

        # Load all formations using our convenience function
        all_formations = load_all_formations(formations_path)

        # Report results
        total_formations = 0

        for side, formations in all_formations.items():
            print(f"📋 {side.title()} Formations ({len(formations)}):")

            for name, formation in formations.items():
                print(f"   ✅ {formation.name}")
                print(f"      Players: {len(formation.roles)}")

                # Group players by position for summary
                position_counts = {}
                for role in formation.roles.values():
                    pos_name = role.position.name
                    position_counts[pos_name] = position_counts.get(pos_name, 0) + 1

                pos_summary = ", ".join(
                    [f"{count} {pos}" for pos, count in sorted(position_counts.items())]
                )
                print(f"      Breakdown: {pos_summary}")
                print()

                total_formations += 1

        print(f"🎉 Successfully loaded {total_formations} total formations!")

        return all_formations

    except Exception as e:
        print(f"❌ Error loading formations: {e}")
        import traceback

        traceback.print_exc()
        return None


def test_formation_details(formations_dict):
    """Print detailed breakdown of a specific formation."""

    if not formations_dict:
        return

    print("\n" + "=" * 60)
    print("DETAILED FORMATION BREAKDOWN")
    print("=" * 60)

    # Let's look at one offensive and one defensive formation in detail
    test_formations = []

    if "offense" in formations_dict:
        offense_formations = list(formations_dict["offense"].items())
        if offense_formations:
            test_formations.append(("Offensive", offense_formations[0]))

    if "defense" in formations_dict:
        defense_formations = list(formations_dict["defense"].items())
        if defense_formations:
            test_formations.append(("Defensive", defense_formations[0]))

    for side, (name, formation) in test_formations:
        print(f"\n{side} Formation: {formation.name}")
        print("-" * 40)

        for role_name, role in formation.roles.items():
            coord_str = f" at {role.coordinate}" if role.coordinate else ""
            # Fix: alignment is already a string, not an enum
            align_str = (
                f" ({role.alignment})"
                if hasattr(role, "alignment") and role.alignment
                else ""
            )

            print(
                f"  {role_name:8} | {role.position.name:2} | {role.lane.value:6}/{role.depth:9}{align_str}{coord_str}"
            )


if __name__ == "__main__":
    formations = test_all_formations()
    test_formation_details(formations)
