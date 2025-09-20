"""
Unit tests for football play loader module.

Tests the PlayLoader class and its methods to ensure proper loading and parsing
of football plays from YAML files. These tests help understand everything that
happens before the snap - formation setup, pre-snap shifts, motion, assignments.
"""

import tempfile
from pathlib import Path
from unittest.mock import Mock

from football.play_loader import PlayLoader
from football.yaml_loader import FormationLoader
from football.plays import (
    FootballPlay,
    PreSnapShift,
    PlayerMotion,
    PlayerAssignment,
    PreSnapAction,
    AssignmentType,
)


def test_play_loader_initialization():
    """
    Test PlayLoader initialization - the foundation for loading football plays.

    The PlayLoader is crucial because it:
    1. Bridges YAML play files with Python objects
    2. Requires a FormationLoader for validation
    3. Caches loaded plays for performance
    4. Enables loading individual plays or entire directories

    In football terms: This is like having a "playbook reader" that can
    translate written plays into executable game plans.
    """
    # Create a mock formation loader
    formation_loader = Mock(spec=FormationLoader)

    # Initialize the play loader
    play_loader = PlayLoader(formation_loader)

    # Test basic properties
    assert (
        play_loader.formation_loader is formation_loader
    ), "PlayLoader should store the formation loader reference"
    assert hasattr(play_loader, "_plays_cache"), "PlayLoader should have a plays cache"
    assert isinstance(
        play_loader._plays_cache, dict
    ), "Plays cache should be a dictionary"
    assert len(play_loader._plays_cache) == 0, "Plays cache should start empty"

    print("✅ PlayLoader initialized correctly with formation loader")
    print("✅ Plays cache properly initialized")
    print("🏈 PlayLoader initialization test completed!")


def test_parse_pre_snap_shifts():
    """
    Test parsing pre-snap shifts - the strategic movements before the snap.

    Pre-snap shifts are crucial because they:
    1. Allow offense to create mismatches
    2. Can confuse defensive alignments
    3. Enable motion and misdirection
    4. Must be properly timed and executed

    In football terms: This is like choreographing the "setup dance" that
    happens before every play to get players in optimal positions.
    """
    formation_loader = Mock(spec=FormationLoader)
    play_loader = PlayLoader(formation_loader)

    # Test simple shift data
    shifts_data = [
        {
            "action": "shift_right",
            "player": "WR1",
            "target_lane": "right",
            "target_depth": "line",
            "target_alignment": "outside",
            "timing": 1,
        },
        {
            "action": "move_up",
            "player": "TE1",
            "target_lane": "left",
            "target_depth": "line",
            "timing": 2,
        },
    ]

    shifts = play_loader._parse_pre_snap_shifts(shifts_data)

    # Test that we get the right number of shifts
    assert len(shifts) == 2, "Should parse 2 pre-snap shifts"
    print("✅ Correct number of pre-snap shifts parsed")

    # Test first shift (WR1 shifting right)
    shift1 = shifts[0]
    assert isinstance(shift1, PreSnapShift), "Should create PreSnapShift objects"
    assert shift1.player_position == "WR1", "Should set correct player"
    assert shift1.action == PreSnapAction.SHIFT_RIGHT, "Should parse action enum"
    assert shift1.target_lane == "right", "Should set target lane"
    assert shift1.target_depth == "line", "Should set target depth"
    assert shift1.target_alignment == "outside", "Should set target alignment"
    assert shift1.timing == 1, "Should set timing"
    print("✅ WR1 shift right parsed correctly")

    # Test second shift (TE1 moving up)
    shift2 = shifts[1]
    assert shift2.player_position == "TE1", "Should set correct player"
    assert shift2.action == PreSnapAction.MOVE_UP, "Should parse action enum"
    assert shift2.target_lane == "left", "Should set target lane"
    assert shift2.target_depth == "line", "Should set target depth"
    assert shift2.target_alignment is None, "Optional alignment should be None"
    assert shift2.timing == 2, "Should set timing"
    print("✅ TE1 move up parsed correctly")

    # Test empty shifts
    empty_shifts = play_loader._parse_pre_snap_shifts([])
    assert len(empty_shifts) == 0, "Should handle empty shifts list"
    print("✅ Empty shifts list handled correctly")

    print("🏈 Pre-snap shifts parsing test completed!")


def test_parse_motion():
    """
    Test parsing player motion - the dynamic pre-snap movement.

    Player motion is crucial because it:
    1. Can reveal defensive coverage (man vs zone)
    2. Creates favorable matchups
    3. Adds deception and misdirection
    4. Must be timed perfectly with the snap

    In football terms: This is the "jet sweep motion" or "orbit motion" that
    gets defenses to tip their hand and creates big play opportunities.
    """
    formation_loader = Mock(spec=FormationLoader)
    play_loader = PlayLoader(formation_loader)

    # Test full motion data
    motion_data = {
        "player": "WR2",
        "type": "jet",
        "start_lane": "right",
        "start_depth": "line",
        "end_lane": "left",
        "end_depth": "backfield",
        "end_alignment": "wingback",
        "speed": "fast",
    }

    motion = play_loader._parse_motion(motion_data)

    # Test motion object creation
    assert isinstance(motion, PlayerMotion), "Should create PlayerMotion object"
    assert motion.player_position == "WR2", "Should set correct player"
    assert motion.motion_type == "jet", "Should set motion type"
    assert motion.start_lane == "right", "Should set start lane"
    assert motion.start_depth == "line", "Should set start depth"
    assert motion.end_lane == "left", "Should set end lane"
    assert motion.end_depth == "backfield", "Should set end depth"
    assert motion.end_alignment == "wingback", "Should set end alignment"
    assert motion.speed == "fast", "Should set speed"
    print("✅ Full motion data parsed correctly")

    # Test minimal motion data (with defaults)
    minimal_motion_data = {"player": "RB1", "type": "orbit"}

    minimal_motion = play_loader._parse_motion(minimal_motion_data)
    assert minimal_motion is not None, "Should create motion object for valid data"
    assert minimal_motion.player_position == "RB1", "Should set player"
    assert minimal_motion.motion_type == "orbit", "Should set motion type"
    assert minimal_motion.speed == "normal", "Should default to normal speed"
    assert minimal_motion.start_lane is None, "Optional fields should be None"
    print("✅ Minimal motion data with defaults parsed correctly")

    # Test no motion
    no_motion = play_loader._parse_motion(None)
    assert no_motion is None, "Should return None for no motion"
    print("✅ No motion case handled correctly")

    print("🏈 Player motion parsing test completed!")


def test_parse_assignments():
    """
    Test parsing player assignments - what each player does during the play.

    Player assignments are crucial because they:
    1. Define each player's specific job (block, route, handoff, etc.)
    2. Coordinate the entire offensive strategy
    3. Enable complex play designs and concepts
    4. Must work together as a cohesive unit

    In football terms: This is the "playbook assignment sheet" that tells
    every player exactly what their job is on this specific play.
    """
    formation_loader = Mock(spec=FormationLoader)
    play_loader = PlayLoader(formation_loader)

    # Test various assignment types
    assignments_data = [
        {
            "player": "QB",
            "assignment": "handoff",
            "target": "RB1",
            "details": {"fake_direction": "left"},
        },
        {
            "player": "RB1",
            "assignment": "run_block",
            "direction": "right",
            "details": {"hole": "B_gap", "vision": "inside_out"},
        },
        {
            "player": "WR1",
            "assignment": "route",
            "details": {"pattern": "slant", "depth": 6},
        },
        {
            "player": "LT",
            "assignment": "pass_block",
            "zone": "left",
            "details": {"technique": "vertical_set"},
        },
    ]

    assignments = play_loader._parse_assignments(assignments_data)

    # Test basic parsing
    assert len(assignments) == 4, "Should parse 4 assignments"
    print("✅ Correct number of assignments parsed")

    # Test QB handoff assignment
    qb_assignment = assignments[0]
    assert isinstance(qb_assignment, PlayerAssignment), "Should create PlayerAssignment"
    assert qb_assignment.player_position == "QB", "Should set player"
    assert qb_assignment.assignment_type == AssignmentType.HANDOFF, "Should parse enum"
    assert qb_assignment.target == "RB1", "Should set target player"
    assert qb_assignment.details["fake_direction"] == "left", "Should parse details"
    print("✅ QB handoff assignment parsed correctly")

    # Test RB run assignment
    rb_assignment = assignments[1]
    assert rb_assignment.player_position == "RB1", "Should set player"
    assert (
        rb_assignment.assignment_type == AssignmentType.RUN_BLOCK
    ), "Should parse enum"
    assert rb_assignment.direction == "right", "Should set direction"
    assert rb_assignment.details["hole"] == "B_gap", "Should parse hole detail"
    assert rb_assignment.details["vision"] == "inside_out", "Should parse vision"
    print("✅ RB run assignment parsed correctly")

    # Test WR route assignment
    wr_assignment = assignments[2]
    assert wr_assignment.player_position == "WR1", "Should set player"
    assert wr_assignment.assignment_type == AssignmentType.ROUTE, "Should parse enum"
    assert wr_assignment.details["pattern"] == "slant", "Should parse route pattern"
    assert wr_assignment.details["depth"] == 6, "Should parse route depth"
    print("✅ WR route assignment parsed correctly")

    # Test OL blocking assignment
    lt_assignment = assignments[3]
    assert lt_assignment.player_position == "LT", "Should set player"
    assert (
        lt_assignment.assignment_type == AssignmentType.PASS_BLOCK
    ), "Should parse enum"
    assert lt_assignment.zone == "left", "Should set zone"
    assert (
        lt_assignment.details["technique"] == "vertical_set"
    ), "Should parse technique"
    print("✅ LT pass block assignment parsed correctly")

    # Test empty assignments
    empty_assignments = play_loader._parse_assignments([])
    assert len(empty_assignments) == 0, "Should handle empty assignments"
    print("✅ Empty assignments handled correctly")

    print("🏈 Player assignments parsing test completed!")


def test_create_play_from_data():
    """
    Test creating a complete FootballPlay from YAML data.

    This is the core functionality that transforms raw YAML into a complete
    play object with all pre-snap elements properly configured.

    In football terms: This is like taking a written play from the playbook
    and turning it into a complete, executable game plan with all the details.
    """
    formation_loader = Mock(spec=FormationLoader)
    play_loader = PlayLoader(formation_loader)

    # Complete play data
    play_data = {
        "name": "inside_zone_right",
        "label": "Inside Zone Right",
        "formation": "singleback_11",
        "personnel": ["11"],
        "play_type": "run",
        "tags": ["run", "zone", "inside"],
        "snap_count": "hut_hut",
        "pre_snap_shifts": [
            {"action": "shift_left", "player": "WR2", "target_lane": "left"}
        ],
        "motion": {"player": "WR3", "type": "jet"},
        "assignments": [
            {"player": "QB", "assignment": "handoff", "target": "RB1"},
            {"player": "RB1", "assignment": "run_block", "direction": "right"},
        ],
    }

    play = play_loader._create_play_from_data(play_data)

    # Test basic play properties
    assert isinstance(play, FootballPlay), "Should create FootballPlay object"
    assert play.name == "inside_zone_right", "Should set play name"
    assert play.label == "Inside Zone Right", "Should set play label"
    assert play.base_formation == "singleback_11", "Should set formation"
    assert play.personnel == ["11"], "Should set personnel"
    assert play.play_type == "run", "Should set play type"
    assert "run" in play.tags, "Should include tags"
    assert "zone" in play.tags, "Should include all tags"
    assert play.snap_count == "hut_hut", "Should set snap count"
    print("✅ Basic play properties set correctly")

    # Test pre-snap shifts
    assert len(play.pre_snap_shifts) == 1, "Should have 1 pre-snap shift"
    shift = play.pre_snap_shifts[0]
    assert shift.player_position == "WR2", "Should parse shift player"
    assert shift.action == PreSnapAction.SHIFT_LEFT, "Should parse shift action"
    print("✅ Pre-snap shifts parsed and included")

    # Test motion
    assert play.motion is not None, "Should have motion"
    assert play.motion.player_position == "WR3", "Should parse motion player"
    assert play.motion.motion_type == "jet", "Should parse motion type"
    print("✅ Motion parsed and included")

    # Test assignments
    assert len(play.assignments) == 2, "Should have 2 assignments"
    qb_assignment = play.assignments[0]
    assert qb_assignment.player_position == "QB", "Should parse QB assignment"
    assert (
        qb_assignment.assignment_type == AssignmentType.HANDOFF
    ), "Should parse assignment type"
    print("✅ Assignments parsed and included")

    # Test defaults for optional fields
    minimal_play_data = {"name": "minimal_play", "formation": "i_form"}

    minimal_play = play_loader._create_play_from_data(minimal_play_data)
    assert minimal_play.label == "minimal_play", "Should default label to name"
    assert minimal_play.play_type == "run", "Should default to run play"
    assert len(minimal_play.pre_snap_shifts) == 0, "Should default to no shifts"
    assert minimal_play.motion is None, "Should default to no motion"
    assert len(minimal_play.assignments) == 0, "Should default to no assignments"
    print("✅ Default values handled correctly")

    print("🏈 Play creation from data test completed!")


def test_play_loader_with_real_file():
    """
    Test loading a play from an actual YAML file to ensure real-world functionality.

    This tests the complete flow from file to FootballPlay object,
    validating that the system can handle real play configurations.
    """
    formation_loader = Mock(spec=FormationLoader)
    play_loader = PlayLoader(formation_loader)

    # Create a temporary play file
    play_yaml = """
name: test_slant
label: "Quick Slant"
formation: trips_right
personnel: ["11"]
play_type: pass
tags: [pass, quick, slant]
snap_count: "hut"

pre_snap_shifts: []

motion: null

assignments:
  - player: QB
    assignment: route
    details:
      drop: 3_step
      read: hot_route

  - player: WR1
    assignment: route
    details:
      pattern: slant
      depth: 6

  - player: LT
    assignment: pass_block
    details:
      technique: vertical_set
"""

    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        f.write(play_yaml)
        temp_path = Path(f.name)

    try:
        # Load the play
        play = play_loader.load_play(temp_path)

        # Verify the loaded play
        assert play.name == "test_slant", "Should load play name correctly"
        assert play.label == "Quick Slant", "Should load play label"
        assert play.base_formation == "trips_right", "Should load formation"
        assert play.play_type == "pass", "Should load play type"
        assert "pass" in play.tags, "Should load tags"
        assert len(play.assignments) == 3, "Should load all assignments"

        # Test caching
        play2 = play_loader.load_play(temp_path)
        assert play is play2, "Should return cached play object"

        print("✅ Real YAML file loaded successfully")
        print("✅ Play caching works correctly")
        print("🏈 Real file loading test completed!")

    finally:
        # Clean up
        temp_path.unlink()
