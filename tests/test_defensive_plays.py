"""
Unit tests for defensive football plays.

Tests the loading and validation of defensive plays from YAML files.
These tests help understand defensive concepts, coverages, blitzes, and
how defensive coordinators call plays to stop the offense.
"""

from pathlib import Path
from unittest.mock import Mock

from football.play_loader import PlayLoader
from football.yaml_loader import FormationLoader
from football.plays import AssignmentType


def test_load_basic_coverage_play():
    """
    Test loading a basic coverage defensive play (Cover 3).

    Cover 3 is a fundamental zone coverage where:
    1. Three deep defenders cover deep thirds of the field
    2. Four underneath defenders cover zones
    3. Four pass rushers pressure the quarterback

    This is the "base" defense that many teams use as their foundation.
    """
    formation_loader = Mock(spec=FormationLoader)
    play_loader = PlayLoader(formation_loader)

    # Load the 4-3 Cover 3 base defensive play
    play_file = Path("data/plays/defense/43_cover3_base.yaml")
    play = play_loader.load_play(play_file)

    print("\n🛡️  DEFENSIVE COVERAGE TEST")
    print(f"   Play: {play.label}")
    print(f"   Formation: {play.base_formation}")
    print(f"   Type: {play.play_type}")
    print(f"   Tags: {', '.join(play.tags)}")

    # Verify basic play properties
    assert play.name == "43_cover3_base", "Play name should match YAML"
    assert play.play_type == "defense", "Should be a defensive play"
    assert "cover3" in play.tags, "Should be tagged as Cover 3"
    assert "zone" in play.tags, "Should be tagged as zone coverage"

    # Analyze the coverage scheme
    coverage_assignments = [
        a for a in play.assignments if a.assignment_type == AssignmentType.COVERAGE
    ]
    rush_assignments = [
        a for a in play.assignments if a.assignment_type == AssignmentType.RUSH
    ]

    print(f"   Coverage Defenders: {len(coverage_assignments)}")
    print(f"   Pass Rushers: {len(rush_assignments)}")

    # Cover 3 should have 7 coverage defenders
    assert (
        len(coverage_assignments) == 7
    ), "Cover 3 should have 7 coverage defenders (3 deep, 4 underneath)"

    # Should have 4 pass rushers
    assert len(rush_assignments) == 4, "Should have 4 pass rushers"

    # Check for deep coverage assignments
    deep_coverage = [a for a in coverage_assignments if a.zone and "deep" in a.zone]
    assert len(deep_coverage) == 3, "Cover 3 should have 3 deep defenders"

    print("   ✅ Cover 3 structure validated")
    print(f"   ✅ Deep coverage: {len(deep_coverage)} defenders")


def test_load_blitz_play():
    """
    Test loading a blitz defensive play (Double A-Gap).

    A Double A-Gap blitz brings extra pass rushers through the A-gaps
    (between center and guards) to pressure the quarterback quickly.
    This creates 6 pass rushers vs 5 offensive linemen.
    """
    formation_loader = Mock(spec=FormationLoader)
    play_loader = PlayLoader(formation_loader)

    # Load the Nickel Double A-Gap blitz play
    play_file = Path("data/plays/defense/nickel_doubleA_cover2.yaml")
    play = play_loader.load_play(play_file)

    print("\n⚡ DEFENSIVE BLITZ TEST")
    print(f"   Play: {play.label}")
    print(f"   Formation: {play.base_formation}")
    print(f"   Tags: {', '.join(play.tags)}")

    # Verify basic blitz properties
    assert play.play_type == "defense", "Should be a defensive play"
    assert "blitz" in play.tags, "Should be tagged as blitz"
    assert "pressure" in play.tags, "Should be tagged as pressure"

    # Count different types of assignments
    rush_assignments = [
        a for a in play.assignments if a.assignment_type == AssignmentType.RUSH
    ]
    blitz_assignments = [
        a for a in play.assignments if a.assignment_type == AssignmentType.BLITZ
    ]
    coverage_assignments = [
        a for a in play.assignments if a.assignment_type == AssignmentType.COVERAGE
    ]

    print(f"   Base Rushers: {len(rush_assignments)}")
    print(f"   Blitzers: {len(blitz_assignments)}")
    print(f"   Coverage: {len(coverage_assignments)} defenders")

    # Should have both base rush and blitz
    assert len(rush_assignments) >= 4, "Should have base pass rushers"
    assert len(blitz_assignments) >= 1, "Should have additional blitzers"

    total_pressure = len(rush_assignments) + len(blitz_assignments)
    print(f"   Total Pressure: {total_pressure} defenders")

    # Blitz should bring more than 4 rushers
    assert total_pressure >= 5, "Blitz should bring extra pressure"

    # Check for pre-snap movement to disguise blitz
    assert len(play.pre_snap_shifts) > 0, "Blitz should have pre-snap movement"

    print("   ✅ Blitz pressure validated")
    print(f"   ✅ Pre-snap disguise: {len(play.pre_snap_shifts)} shifts")


def test_defensive_pre_snap_shifts():
    """
    Test defensive pre-snap shifts and movement.

    Defenses move players before the snap to:
    1. Disguise their coverage/blitz intentions
    2. Create better angles for pressure
    3. Confuse the offensive line protection calls
    4. Get better positioning for the called play
    """
    formation_loader = Mock(spec=FormationLoader)
    play_loader = PlayLoader(formation_loader)

    # Load a play with defensive pre-snap movement
    play_file = Path("data/plays/defense/nickel_doubleA_cover2.yaml")
    play = play_loader.load_play(play_file)

    print("\n🔄 DEFENSIVE PRE-SNAP MOVEMENT TEST")
    print(f"   Play: {play.label}")

    # Should have pre-snap shifts
    assert len(play.pre_snap_shifts) > 0, "Defense should have pre-snap movement"

    print(f"   Pre-snap Shifts: {len(play.pre_snap_shifts)}")

    for i, shift in enumerate(play.pre_snap_shifts):
        print(f"   Shift {i + 1}:")
        print(f"     Player: {shift.player_position}")
        print(f"     Action: {shift.action.value}")
        print(f"     Timing: {shift.timing}")

        # Validate shift properties
        assert shift.player_position, "Shift must specify a player"
        assert shift.action, "Shift must have an action"
        assert isinstance(
            shift.timing, (int, type(None))
        ), "Timing should be integer or None"

    print("   ✅ Pre-snap movement validated")


def test_defensive_coverage_assignments():
    """
    Test defensive coverage assignments and zones.

    Coverage assignments define how defenders cover receivers:
    1. Zone coverage - defend specific areas of the field
    2. Man coverage - follow specific receivers
    3. Combination coverages - mix of man and zone
    """
    formation_loader = Mock(spec=FormationLoader)
    play_loader = PlayLoader(formation_loader)

    # Load a zone coverage play
    play_file = Path("data/plays/defense/43_cover3_base.yaml")
    play = play_loader.load_play(play_file)

    print("\n🎯 DEFENSIVE COVERAGE ASSIGNMENTS TEST")
    print(f"   Play: {play.label}")

    # Get all coverage assignments
    coverage_assignments = [
        a for a in play.assignments if a.assignment_type == AssignmentType.COVERAGE
    ]

    print(f"   Coverage Assignments: {len(coverage_assignments)}")

    # Analyze coverage zones
    zones = {}
    for assignment in coverage_assignments:
        if assignment.zone:
            zone_type = assignment.zone
            if zone_type not in zones:
                zones[zone_type] = []
            zones[zone_type].append(assignment.player_position)

    print("   Coverage Zones:")
    for zone, players in zones.items():
        print(f"     {zone}: {', '.join(players)}")

    # Should have multiple coverage zones
    assert len(zones) >= 2, "Coverage should have multiple zones"

    # Check for deep coverage
    deep_zones = [zone for zone in zones.keys() if "deep" in zone]
    assert len(deep_zones) > 0, "Should have deep coverage zones"

    # Validate assignment details
    for assignment in coverage_assignments:
        assert assignment.player_position, "Coverage assignment must specify player"

        if assignment.details:
            print(f"   {assignment.player_position} details: {assignment.details}")

    print("   ✅ Coverage zones validated")
    print("   ✅ Deep coverage confirmed")


def test_defensive_rush_assignments():
    """
    Test defensive pass rush assignments.

    Pass rush assignments define how defenders attack the quarterback:
    1. Technique - how to rush (speed, power, contain)
    2. Gap responsibility - which gap to attack
    3. Contain vs penetration - stay outside vs get inside
    """
    formation_loader = Mock(spec=FormationLoader)
    play_loader = PlayLoader(formation_loader)

    # Load a defensive play with rush assignments
    play_file = Path("data/plays/defense/43_cover3_base.yaml")
    play = play_loader.load_play(play_file)

    print("\n🔥 DEFENSIVE PASS RUSH TEST")
    print(f"   Play: {play.label}")

    # Get all rush assignments
    rush_assignments = [
        a for a in play.assignments if a.assignment_type == AssignmentType.RUSH
    ]

    print(f"   Pass Rush Assignments: {len(rush_assignments)}")

    # Analyze rush techniques
    techniques = {}
    gaps = {}

    for assignment in rush_assignments:
        player = assignment.player_position
        print(f"   {player}:")

        if assignment.details:
            technique = assignment.details.get("technique")
            gap = assignment.details.get("gap")

            if technique:
                print(f"     Technique: {technique}")
                techniques[technique] = techniques.get(technique, 0) + 1

            if gap:
                print(f"     Gap: {gap}")
                gaps[gap] = gaps.get(gap, 0) + 1

    print(f"   Rush Techniques: {list(techniques.keys())}")
    print(f"   Gap Assignments: {list(gaps.keys())}")

    # Should have rush assignments
    assert len(rush_assignments) >= 4, "Should have at least 4 pass rushers"

    # Should have technique details
    assert len(techniques) > 0, "Rush assignments should have techniques"

    print("   ✅ Pass rush validated")
    print("   ✅ Techniques assigned")


def test_defensive_play_validation():
    """
    Test validation of defensive play structure.

    Validates that defensive plays have proper structure:
    1. Correct play type
    2. Valid assignments for all positions
    3. Proper coverage vs rush balance
    4. Realistic defensive schemes
    """
    formation_loader = Mock(spec=FormationLoader)
    play_loader = PlayLoader(formation_loader)

    # Test multiple defensive plays
    defensive_plays = [
        "43_cover3_base.yaml",
        "nickel_doubleA_cover2.yaml",
        "dime_cover4_quarters.yaml",
    ]

    print("\n🔍 DEFENSIVE PLAY VALIDATION TEST")

    for play_file in defensive_plays:
        play_path = Path(f"data/plays/defense/{play_file}")
        play = play_loader.load_play(play_path)

        print(f"   Validating: {play.label}")

        # Basic validation
        assert play.play_type in [
            "defense",
            "coverage",
        ], f"{play.name} should be defensive play type"
        assert play.base_formation, f"{play.name} should have formation"
        assert len(play.assignments) > 0, f"{play.name} should have assignments"

        # Count assignment types
        assignment_counts = {}
        for assignment in play.assignments:
            assignment_type = assignment.assignment_type.value
            assignment_counts[assignment_type] = (
                assignment_counts.get(assignment_type, 0) + 1
            )

        print(f"     Assignments: {assignment_counts}")

        # Should have both rush and coverage
        assert (
            "rush" in assignment_counts or "blitz" in assignment_counts
        ), f"{play.name} should have pass rush"
        assert "coverage" in assignment_counts, f"{play.name} should have coverage"

        # Total should be 11 players
        total_assignments = sum(assignment_counts.values())
        assert total_assignments == 11, f"{play.name} should have 11 player assignments"

        print(f"     ✅ {play.name} validated")

    print("   ✅ All defensive plays validated")


def test_load_all_defensive_plays():
    """
    Test loading all defensive plays from the directory.

    This test ensures:
    1. All defensive play files can be loaded
    2. Each play has valid structure
    3. Defensive concepts are properly represented
    4. No parsing errors occur
    """
    formation_loader = Mock(spec=FormationLoader)
    play_loader = PlayLoader(formation_loader)

    # Load all defensive plays
    defense_plays_dir = Path("data/plays/defense")

    print("\n📚 ALL DEFENSIVE PLAYS TEST")
    print(f"   Loading from: {defense_plays_dir}")

    try:
        plays = play_loader.load_plays_from_directory(defense_plays_dir)

        print(f"   Total Plays Loaded: {len(plays)}")

        # Categorize plays by type
        coverage_plays = []
        blitz_plays = []
        pressure_plays = []

        for play_name, play in plays.items():
            print(f"   📋 {play.label}")
            print(f"     Formation: {play.base_formation}")
            print(f"     Tags: {', '.join(play.tags)}")

            # Categorize by tags
            if "cover" in " ".join(play.tags).lower():
                coverage_plays.append(play_name)
            if "blitz" in play.tags:
                blitz_plays.append(play_name)
            if "pressure" in play.tags:
                pressure_plays.append(play_name)

        print("\n   📊 DEFENSIVE PLAY BREAKDOWN:")
        print(f"     Coverage Plays: {len(coverage_plays)}")
        print(f"     Blitz Plays: {len(blitz_plays)}")
        print(f"     Pressure Plays: {len(pressure_plays)}")

        # Should have loaded multiple plays
        assert len(plays) >= 10, "Should have loaded multiple defensive plays"

        # Should have variety of play types
        assert len(coverage_plays) > 0, "Should have coverage plays"
        assert len(blitz_plays) > 0, "Should have blitz plays"

        print("   ✅ All defensive plays loaded successfully")

    except Exception as e:
        print(f"   ❌ Error loading defensive plays: {e}")
        raise


def test_defensive_formations_and_personnel():
    """
    Test defensive formations and personnel groupings.

    Different defensive formations are used for different situations:
    1. Base defense (4-3, 3-4) - standard down and distance
    2. Nickel - 5 DBs for passing situations
    3. Dime - 6 DBs for obvious passing downs
    4. Goal line - heavy formation near the goal line
    """
    formation_loader = Mock(spec=FormationLoader)
    play_loader = PlayLoader(formation_loader)

    print("\n🏟️  DEFENSIVE FORMATIONS TEST")

    # Test different formation types
    formation_plays = {
        "Base 4-3": "43_cover3_base.yaml",
        "Nickel": "nickel_doubleA_cover2.yaml",
        "Dime": "dime_cover4_quarters.yaml",
    }

    formations_found = {}

    for formation_name, play_file in formation_plays.items():
        try:
            play_path = Path(f"data/plays/defense/{play_file}")
            play = play_loader.load_play(play_path)

            print(f"   {formation_name}: {play.base_formation}")
            formations_found[formation_name] = play.base_formation

            # Validate formation makes sense for play
            if "nickel" in formation_name.lower():
                assert (
                    "nickel" in play.base_formation.lower()
                ), "Nickel play should use nickel formation"
            elif "dime" in formation_name.lower():
                assert (
                    "dime" in play.base_formation.lower()
                ), "Dime play should use dime formation"

        except FileNotFoundError:
            print(f"   {formation_name}: File not found")

    print(f"   Formations Available: {len(formations_found)}")

    # Should have found multiple formations
    assert len(formations_found) >= 2, "Should have multiple defensive formations"

    print("   ✅ Defensive formations validated")


if __name__ == "__main__":
    # Run all tests with detailed output
    test_load_basic_coverage_play()
    test_load_blitz_play()
    test_defensive_pre_snap_shifts()
    test_defensive_coverage_assignments()
    test_defensive_rush_assignments()
    test_defensive_play_validation()
    test_load_all_defensive_plays()
    test_defensive_formations_and_personnel()

    print("\n🏆 ALL DEFENSIVE PLAY TESTS COMPLETED!")
    print("   ✅ Coverage concepts validated")
    print("   ✅ Blitz schemes tested")
    print("   ✅ Pre-snap movement verified")
    print("   ✅ All defensive plays loaded")
