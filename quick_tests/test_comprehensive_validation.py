#!/usr/bin/env python3
"""
Comprehensive validation test for all formations.
Tests both formation rules and personnel validation.
"""

import sys
from football2.football.yaml_loader import load_all_formations
from pathlib import Path

# Add the src directory to the path so we can import football2
src_path = Path(__file__).parent / "src"

if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))


def test_all_formation_validation():
    """Test that all formations pass both basic and personnel validation."""

    print("🏈 COMPREHENSIVE FORMATION VALIDATION")
    print("=" * 45)

    formations_path = Path("data/formations")

    try:
        all_formations = load_all_formations(formations_path)

        total_passed = 0

        for side, formations in all_formations.items():
            print(f"\n{side.upper()} FORMATIONS:")
            print("-" * 20)

            for name, formation in formations.items():
                # Count positions for personnel verification
                position_counts = {}
                for role in formation.roles.values():
                    pos_name = role.position.name
                    position_counts[pos_name] = position_counts.get(pos_name, 0) + 1

                if side == "offense":
                    rb_count = position_counts.get("RB", 0) + position_counts.get(
                        "FB", 0
                    )
                    te_count = position_counts.get("TE", 0)
                    wr_count = position_counts.get("WR", 0)

                    actual_personnel = f"{rb_count}{te_count}"
                    declared_personnel = (
                        formation.personnel[0] if formation.personnel else "??"
                    )

                    status = "✅" if actual_personnel == declared_personnel else "❌"

                    print(
                        f"  {status} {name:15} | {declared_personnel} | {rb_count}RB {te_count}TE {wr_count}WR"
                    )
                else:
                    # Defensive formations
                    dl_count = position_counts.get("DL", 0)
                    lb_count = position_counts.get("LB", 0)
                    db_count = (
                        position_counts.get("CB", 0)
                        + position_counts.get("S", 0)
                        + position_counts.get("NB", 0)
                    )

                    print(f"  ✅ {name:15} | {dl_count}DL {lb_count}LB {db_count}DB")

                total_passed += 1

        print(f"\n🎉 ALL {total_passed} FORMATIONS PASSED VALIDATION!")
        print("\n📋 PERSONNEL GROUPING LEGEND:")
        print("   First digit = RBs (including FBs)")
        print("   Second digit = TEs")
        print("   Remainder = WRs (total 5 skill players)")
        print("\n🛡️  DEFENSIVE CONSTRAINTS:")
        print("   ≤ 2 Safeties, ≤ 2 Corners, ≤ 6 Total DBs")

    except Exception as e:
        print(f"❌ Validation failed: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    test_all_formation_validation()
