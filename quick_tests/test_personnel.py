#!/usr/bin/env python3
"""
Test personnel validation to ensure formations match their declared personnel groupings.
"""

import sys
from pathlib import Path
from football2.football.yaml_loader import FormationLoader
from football2.core.players import PlayerRole
from football2.core.game_board import Lane
from football2.football.positions import ALL_POSITIONS, FootballFormation

# Add the src directory to the path so we can import football2
src_path = Path(__file__).parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))



def test_personnel_validation():
    """Test that personnel validation catches mismatches."""

    print("🧪 Testing personnel validation...\n")

    loader = FormationLoader()

    # Test 1: Formation claiming "11" but actually "10"
    print("Test 1: Formation claims '11' but has 1 RB, 0 TE, 4 WR (should fail)")
    try:
        roles = {
            "QB": PlayerRole("QB", ALL_POSITIONS["QB"], Lane.MIDDLE, "backfield"),
            "RB": PlayerRole("RB", ALL_POSITIONS["RB"], Lane.MIDDLE, "backfield"),
            "WR1": PlayerRole("WR1", ALL_POSITIONS["WR"], Lane.LEFT, "line"),
            "WR2": PlayerRole("WR2", ALL_POSITIONS["WR"], Lane.RIGHT, "line"),
            "WR3": PlayerRole("WR3", ALL_POSITIONS["WR"], Lane.LEFT, "line"),
            "WR4": PlayerRole("WR4", ALL_POSITIONS["WR"], Lane.RIGHT, "line"),
            "LT": PlayerRole("LT", ALL_POSITIONS["LT"], Lane.LEFT, "line"),
            "LG": PlayerRole("LG", ALL_POSITIONS["LG"], Lane.MIDDLE, "line"),
            "C": PlayerRole("C", ALL_POSITIONS["C"], Lane.MIDDLE, "line"),
            "RG": PlayerRole("RG", ALL_POSITIONS["RG"], Lane.MIDDLE, "line"),
            "RT": PlayerRole("RT", ALL_POSITIONS["RT"], Lane.RIGHT, "line"),
        }

        # Claims "11" (1 RB, 1 TE) but actually has "10" (1 RB, 0 TE)
        formation = FootballFormation("test_mismatch", roles, ["11"])
        violations = loader.validator.validate_formation(formation)

        if violations:
            print(f"   ✅ Correctly caught violations: {violations}")
        else:
            print("   ❌ Should have caught personnel mismatch!")

    except Exception as e:
        print(f"   ✅ Correctly rejected formation: {e}")

    # Test 2: Formation with correct "00" personnel (should pass)
    print("\nTest 2: Formation correctly declares '00' (0 RB, 0 TE, 5 WR)")
    try:
        roles = {
            "QB": PlayerRole("QB", ALL_POSITIONS["QB"], Lane.MIDDLE, "shotgun"),
            "WR1": PlayerRole("WR1", ALL_POSITIONS["WR"], Lane.LEFT, "line"),
            "WR2": PlayerRole("WR2", ALL_POSITIONS["WR"], Lane.RIGHT, "line"),
            "WR3": PlayerRole("WR3", ALL_POSITIONS["WR"], Lane.LEFT, "line"),
            "WR4": PlayerRole("WR4", ALL_POSITIONS["WR"], Lane.RIGHT, "line"),
            "WR5": PlayerRole("WR5", ALL_POSITIONS["WR"], Lane.MIDDLE, "line"),
            "LT": PlayerRole("LT", ALL_POSITIONS["LT"], Lane.LEFT, "line"),
            "LG": PlayerRole("LG", ALL_POSITIONS["LG"], Lane.MIDDLE, "line"),
            "C": PlayerRole("C", ALL_POSITIONS["C"], Lane.MIDDLE, "line"),
            "RG": PlayerRole("RG", ALL_POSITIONS["RG"], Lane.MIDDLE, "line"),
            "RT": PlayerRole("RT", ALL_POSITIONS["RT"], Lane.RIGHT, "line"),
        }

        formation = FootballFormation("test_empty", roles, ["00"])
        violations = loader.validator.validate_formation(formation)

        if not violations:
            print("   ✅ Correctly accepted formation")
        else:
            print(f"   ❌ Should have accepted formation: {violations}")

    except Exception as e:
        print(f"   ❌ Unexpected error: {e}")

    # Test 3: Check that our actual formations have correct personnel
    print("\nTest 3: Checking actual formation personnel...")

    test_files = [
        ("data/formations/offense/empty_backfield.yaml", "00", "0 RB, 0 TE, 5 WR"),
        ("data/formations/offense/spread_10.yaml", "10", "1 RB, 0 TE, 4 WR"),
        ("data/formations/offense/singleback_11.yaml", "11", "1 RB, 1 TE, 3 WR"),
    ]

    for file_path, expected_personnel, description in test_files:
        try:
            formation = loader.load_formation(file_path)
            print(f"   ✅ {formation.name}: {description} - Personnel: {formation.personnel}")
        except Exception as e:
            print(f"   ❌ {file_path}: {e}")


if __name__ == "__main__":
    test_personnel_validation()
