#!/usr/bin/env python3
"""
Test formation validation rules to make sure they catch violations.
"""

import sys
from pathlib import Path
from football2.core.players import PlayerRole
from football2.core.game_board import Lane
from football2.football.positions import ALL_POSITIONS, FootballFormation
from football2.football.yaml_loader import FormationLoader

# Add the src directory to the path so we can import football2
src_path = Path(__file__).parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))



def test_validation_rules():
    """Test that our validation rules properly catch violations."""

    print("🧪 Testing formation validation rules...\n")

    loader = FormationLoader()

    # Test 1: Too many safeties
    print("Test 1: Formation with 3 safeties (should fail)")
    try:
        roles = {
            "DL1": PlayerRole("DL1", ALL_POSITIONS["DL"], Lane.LEFT, "line"),
            "DL2": PlayerRole("DL2", ALL_POSITIONS["DL"], Lane.MIDDLE, "line"),
            "DL3": PlayerRole("DL3", ALL_POSITIONS["DL"], Lane.RIGHT, "line"),
            "DL4": PlayerRole("DL4", ALL_POSITIONS["DL"], Lane.RIGHT, "line"),
            "LB1": PlayerRole("LB1", ALL_POSITIONS["LB"], Lane.LEFT, "box"),
            "LB2": PlayerRole("LB2", ALL_POSITIONS["LB"], Lane.MIDDLE, "box"),
            "CB1": PlayerRole("CB1", ALL_POSITIONS["CB"], Lane.LEFT, "deep"),
            "CB2": PlayerRole("CB2", ALL_POSITIONS["CB"], Lane.RIGHT, "deep"),
            "S1": PlayerRole("S1", ALL_POSITIONS["S"], Lane.LEFT, "deep"),
            "S2": PlayerRole("S2", ALL_POSITIONS["S"], Lane.MIDDLE, "deep"),
            "S3": PlayerRole("S3", ALL_POSITIONS["S"], Lane.RIGHT, "deep"),  # Too many!
        }

        formation = FootballFormation("test_bad", roles)
        violations = loader.validator.validate_formation(formation)

        if violations:
            print(f"   ✅ Correctly caught violations: {violations}")
        else:
            print("   ❌ Should have caught too many safeties!")

    except Exception as e:
        print(f"   ✅ Correctly rejected formation: {e}")

    # Test 2: Formation with no QB (defensive - should pass)
    print("\nTest 2: Defensive formation with no QB (should pass)")
    try:
        roles = {
            "DL1": PlayerRole("DL1", ALL_POSITIONS["DL"], Lane.LEFT, "line"),
            "DL2": PlayerRole("DL2", ALL_POSITIONS["DL"], Lane.MIDDLE, "line"),
            "DL3": PlayerRole("DL3", ALL_POSITIONS["DL"], Lane.MIDDLE, "line"),
            "DL4": PlayerRole("DL4", ALL_POSITIONS["DL"], Lane.RIGHT, "line"),
            "LB1": PlayerRole("LB1", ALL_POSITIONS["LB"], Lane.LEFT, "box"),
            "LB2": PlayerRole("LB2", ALL_POSITIONS["LB"], Lane.MIDDLE, "box"),
            "LB3": PlayerRole("LB3", ALL_POSITIONS["LB"], Lane.RIGHT, "box"),
            "CB1": PlayerRole("CB1", ALL_POSITIONS["CB"], Lane.LEFT, "deep"),
            "CB2": PlayerRole("CB2", ALL_POSITIONS["CB"], Lane.RIGHT, "deep"),
            "S1": PlayerRole("S1", ALL_POSITIONS["S"], Lane.LEFT, "deep"),
            "S2": PlayerRole("S2", ALL_POSITIONS["S"], Lane.MIDDLE, "deep"),
        }

        formation = FootballFormation("test_defense", roles)
        violations = loader.validator.validate_formation(formation)

        if not violations:
            print("   ✅ Correctly accepted defensive formation")
        else:
            print(f"   ❌ Should have accepted defensive formation: {violations}")

    except Exception as e:
        print(f"   ❌ Unexpected error: {e}")

    # Test 3: Offensive formation with no QB (should fail)
    print("\nTest 3: Offensive formation with no QB (should fail)")
    try:
        roles = {
            "RB": PlayerRole("RB", ALL_POSITIONS["RB"], Lane.MIDDLE, "backfield"),
            "WR1": PlayerRole("WR1", ALL_POSITIONS["WR"], Lane.LEFT, "line"),
            "WR2": PlayerRole("WR2", ALL_POSITIONS["WR"], Lane.RIGHT, "line"),
            "TE": PlayerRole("TE", ALL_POSITIONS["TE"], Lane.RIGHT, "line"),
            "LT": PlayerRole("LT", ALL_POSITIONS["LT"], Lane.LEFT, "line"),
            "LG": PlayerRole("LG", ALL_POSITIONS["LG"], Lane.MIDDLE, "line"),
            "C": PlayerRole("C", ALL_POSITIONS["C"], Lane.MIDDLE, "line"),
            "RG": PlayerRole("RG", ALL_POSITIONS["RG"], Lane.MIDDLE, "line"),
            "RT": PlayerRole("RT", ALL_POSITIONS["RT"], Lane.RIGHT, "line"),
            "WR3": PlayerRole("WR3", ALL_POSITIONS["WR"], Lane.LEFT, "line"),
            "WR4": PlayerRole("WR4", ALL_POSITIONS["WR"], Lane.RIGHT, "line"),
        }

        formation = FootballFormation("test_no_qb", roles)
        violations = loader.validator.validate_formation(formation)

        if violations:
            print(f"   ✅ Correctly caught violations: {violations}")
        else:
            print("   ❌ Should have caught missing QB!")

    except Exception as e:
        print(f"   ✅ Correctly rejected formation: {e}")


if __name__ == "__main__":
    test_validation_rules()
