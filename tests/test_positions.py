"""
Unit tests for football positions module.

Tests the FootballPosition base class and specific position implementations
to ensure proper football positioning constraints and validation.
"""

from football.positions import (
    FootballPosition,
    FootballDepth,
    # Defensive positions for testing
    DefensiveLine,
    Linebacker,
    Cornerback,
    Nickelback,
    Safety,
    DEFENSIVE_POSITIONS,
)
from core.game_board import Lane


def test_football_position_base_class():
    """
    Test the FootballPosition base class - foundation for all football positions.

    This base class is crucial because it:
    1. Provides consistent interface for all football positions
    2. Stores position name and allowed alignments
    3. Ensures all positions follow the same contract
    4. Enables position-based validation and constraints

    In football terms: This is like the "player position rules" that define
    where each type of player (QB, RB, WR, etc.) is allowed to line up.
    """
    # Test creating a custom position with specific alignments
    custom_alignments = {
        (Lane.MIDDLE, FootballDepth.BACKFIELD.value),
        (Lane.LEFT, FootballDepth.LINE.value),
        (Lane.RIGHT, FootballDepth.LINE.value),
    }

    position = FootballPosition("TEST_POS", custom_alignments)

    # Test name property
    assert position.name == "TEST_POS", "Position name should be stored correctly"
    assert isinstance(position.name, str), "Position name should be a string"
    print("✅ Position name property works correctly")

    # Test allowed_alignments property
    assert (
        position.allowed_alignments == custom_alignments
    ), "Allowed alignments should be stored correctly"
    assert isinstance(
        position.allowed_alignments, set
    ), "Allowed alignments should be a set"
    print("✅ Allowed alignments property works correctly")

    # Test that each alignment is a tuple of (Lane, str)
    for alignment in position.allowed_alignments:
        assert isinstance(alignment, tuple), "Each alignment should be a tuple"
        assert len(alignment) == 2, "Each alignment should have exactly 2 elements"
        lane, depth = alignment
        assert isinstance(lane, Lane), "First element should be a Lane enum"
        assert isinstance(depth, str), "Second element should be a depth string"
        print(f"✅ Alignment {alignment} has correct structure")

    # Test immutability - position name shouldn't be changeable
    original_name = position.name
    # Note: name is read-only property, so this tests the design
    assert position.name == original_name, "Position name should remain constant"
    print("✅ Position name is properly encapsulated")

    # Test that alignments set is returned (not a copy that could be modified)
    alignments_ref1 = position.allowed_alignments
    alignments_ref2 = position.allowed_alignments
    assert (
        alignments_ref1 is alignments_ref2
    ), "Should return same set reference for consistency"
    print("✅ Allowed alignments reference is consistent")

    # Test with empty alignments (edge case)
    empty_position = FootballPosition("EMPTY", set())
    assert empty_position.name == "EMPTY"
    assert len(empty_position.allowed_alignments) == 0
    print("✅ Empty alignments handled correctly")

    # Test with single alignment
    single_alignment = {(Lane.MIDDLE, FootballDepth.LINE.value)}
    single_position = FootballPosition("SINGLE", single_alignment)
    assert len(single_position.allowed_alignments) == 1
    assert (Lane.MIDDLE, FootballDepth.LINE.value) in single_position.allowed_alignments
    print("✅ Single alignment handled correctly")

    # Test inheritance from Position abstract base class
    from core.players import Position

    assert isinstance(
        position, Position
    ), "FootballPosition should inherit from Position"
    print("✅ Proper inheritance from Position base class")

    print("🏈 FootballPosition base class test completed - all validations working!")


def test_football_position_realistic_alignments():
    """
    Test that FootballPosition handles realistic football alignments correctly.

    This tests the football-specific depth and lane combinations that make
    sense in real football formations.
    """
    # Test with all FootballDepth values
    all_depths = [depth.value for depth in FootballDepth]
    all_lanes = [Lane.LEFT, Lane.MIDDLE, Lane.RIGHT]

    # Create position with all possible combinations
    all_combinations = {(lane, depth) for lane in all_lanes for depth in all_depths}
    versatile_position = FootballPosition("VERSATILE", all_combinations)

    expected_count = len(all_lanes) * len(all_depths)
    assert len(versatile_position.allowed_alignments) == expected_count
    alignment_count = len(versatile_position.allowed_alignments)
    print(f"✅ Position supports {alignment_count} alignments")

    # Test specific football-realistic combinations
    qb_like_alignments = {
        (Lane.MIDDLE, FootballDepth.UNDER_CENTER.value),
        (Lane.MIDDLE, FootballDepth.SHOTGUN.value),
        (Lane.MIDDLE, FootballDepth.PISTOL.value),
    }

    qb_position = FootballPosition("QB_TEST", qb_like_alignments)

    # Verify QB-like position only allows middle lane
    for lane, depth in qb_position.allowed_alignments:
        assert lane == Lane.MIDDLE, "QB should only be in middle lane"
        assert depth in [
            "under_center",
            "shotgun",
            "pistol",
        ], f"Unexpected QB depth: {depth}"

    print("✅ QB-like alignments are realistic")

    # Test receiver-like alignments
    wr_like_alignments = {
        (Lane.LEFT, FootballDepth.LINE.value),
        (Lane.RIGHT, FootballDepth.LINE.value),
        (Lane.LEFT, FootballDepth.BACKFIELD.value),  # Motion
        (Lane.RIGHT, FootballDepth.BACKFIELD.value),  # Motion
    }

    wr_position = FootballPosition("WR_TEST", wr_like_alignments)

    # Verify WR-like position allows left/right but not middle line
    for lane, depth in wr_position.allowed_alignments:
        if depth == FootballDepth.LINE.value:
            assert lane in [Lane.LEFT, Lane.RIGHT], "WR on line should be left or right"

    print("✅ WR-like alignments are realistic")

    print("🏈 Realistic alignments test completed!")


def test_defensive_line_position():
    """
    Test the DefensiveLine position - the foundation of football defense.

    Defensive linemen are crucial because they:
    1. Rush the quarterback to pressure passing plays
    2. Stop running plays at the line of scrimmage
    3. Can line up across all three lanes on the line
    4. Form the first level of defense

    In football terms: These are your DEs (Defensive Ends) and DTs (Defensive Tackles)
    who line up right at the line of scrimmage to disrupt offensive plays.
    """
    dl = DefensiveLine()

    # Test basic properties
    assert dl.name == "DL", "DefensiveLine should have name 'DL'"
    print("✅ DefensiveLine name is correct")

    # Test that DL can line up in all three lanes on the line
    expected_alignments = {
        (Lane.LEFT, FootballDepth.LINE.value),  # Left DE
        (Lane.MIDDLE, FootballDepth.LINE.value),  # DT/NT (Nose Tackle)
        (Lane.RIGHT, FootballDepth.LINE.value),  # Right DE
    }

    assert (
        dl.allowed_alignments == expected_alignments
    ), "DefensiveLine should allow all three lanes on the line"
    print("✅ DefensiveLine allows correct lane/depth combinations")

    # Verify DL is restricted to line of scrimmage only
    for lane, depth in dl.allowed_alignments:
        assert (
            depth == FootballDepth.LINE.value
        ), f"DefensiveLine should only be on line, found depth: {depth}"
        assert lane in [
            Lane.LEFT,
            Lane.MIDDLE,
            Lane.RIGHT,
        ], f"DefensiveLine should be in valid lane, found: {lane}"

    print("✅ DefensiveLine properly restricted to line of scrimmage")
    print("🏈 DefensiveLine position test completed!")


def test_linebacker_position():
    """
    Test the Linebacker position - the versatile middle level of defense.

    Linebackers are crucial because they:
    1. Cover the "box" area 5-8 yards from line of scrimmage
    2. Can rush the quarterback, cover receivers, or stop runs
    3. Provide the flexible second level of defense
    4. Can line up in all three lanes in the box

    In football terms: These are your MLB (Middle), OLB (Outside), and
    specialized LBs who handle both run support and pass coverage.
    """
    lb = Linebacker()

    # Test basic properties
    assert lb.name == "LB", "Linebacker should have name 'LB'"
    print("✅ Linebacker name is correct")

    # Test that LB can line up in all three lanes in the box
    expected_alignments = {
        (Lane.LEFT, FootballDepth.BOX.value),  # LOLB (Left Outside LB)
        (Lane.MIDDLE, FootballDepth.BOX.value),  # MLB (Middle LB)
        (Lane.RIGHT, FootballDepth.BOX.value),  # ROLB (Right Outside LB)
    }

    assert (
        lb.allowed_alignments == expected_alignments
    ), "Linebacker should allow all three lanes in the box"
    print("✅ Linebacker allows correct lane/depth combinations")

    # Verify LB is restricted to box level only
    for lane, depth in lb.allowed_alignments:
        assert (
            depth == FootballDepth.BOX.value
        ), f"Linebacker should only be in box, found depth: {depth}"
        assert lane in [
            Lane.LEFT,
            Lane.MIDDLE,
            Lane.RIGHT,
        ], f"Linebacker should be in valid lane, found: {lane}"

    print("✅ Linebacker properly positioned in the box")
    print("🏈 Linebacker position test completed!")


def test_cornerback_position():
    """
    Test the Cornerback position - the primary pass coverage defenders.

    Cornerbacks are crucial because they:
    1. Cover wide receivers in man-to-man or zone coverage
    2. Can play at different depths based on coverage type
    3. Usually line up on the left or right sides (not middle)
    4. Provide the primary defense against passing plays

    In football terms: These are your CBs who shadow receivers and
    defend against passing attacks at multiple depth levels.
    """
    cb = Cornerback()

    # Test basic properties
    assert cb.name == "CB", "Cornerback should have name 'CB'"
    print("✅ Cornerback name is correct")

    # Test that CB can line up at multiple depths but not in middle lane
    expected_alignments = {
        (Lane.LEFT, FootballDepth.LINE.value),  # Press coverage left
        (Lane.RIGHT, FootballDepth.LINE.value),  # Press coverage right
        (Lane.LEFT, FootballDepth.BOX.value),  # Off coverage left
        (Lane.RIGHT, FootballDepth.BOX.value),  # Off coverage right
        (Lane.LEFT, FootballDepth.DEEP.value),  # Deep coverage left
        (Lane.RIGHT, FootballDepth.DEEP.value),  # Deep coverage right
    }

    assert (
        cb.allowed_alignments == expected_alignments
    ), "Cornerback should allow left/right lanes at multiple depths"
    print("✅ Cornerback allows correct lane/depth combinations")

    # Verify CB never lines up in middle lane
    for lane, depth in cb.allowed_alignments:
        assert lane != Lane.MIDDLE, "Cornerback should not line up in middle lane"
        assert lane in [
            Lane.LEFT,
            Lane.RIGHT,
        ], f"Cornerback should only be left/right, found: {lane}"
        assert depth in [
            FootballDepth.LINE.value,
            FootballDepth.BOX.value,
            FootballDepth.DEEP.value,
        ], f"Cornerback depth should be line/box/deep, found: {depth}"

    print("✅ Cornerback properly restricted to left/right lanes")
    print("🏈 Cornerback position test completed!")


def test_nickelback_position():
    """
    Test the Nickelback position - the slot coverage specialist.

    Nickelbacks are crucial because they:
    1. Cover slot receivers and tight ends in the middle
    2. Provide additional pass coverage in nickel packages
    3. Can play at box or deep levels based on coverage
    4. Specialize in middle-of-field coverage

    In football terms: These are your NB/Slot CBs who come in on
    passing downs to provide extra coverage, especially in the slot.
    """
    nb = Nickelback()

    # Test basic properties
    assert nb.name == "NB", "Nickelback should have name 'NB'"
    print("✅ Nickelback name is correct")

    # Test that NB focuses on middle coverage with some flexibility
    expected_alignments = {
        (Lane.MIDDLE, FootballDepth.BOX.value),  # Slot coverage
        (Lane.MIDDLE, FootballDepth.DEEP.value),  # Deep middle coverage
        (Lane.LEFT, FootballDepth.BOX.value),  # Left slot coverage
        (Lane.RIGHT, FootballDepth.BOX.value),  # Right slot coverage
    }

    assert (
        nb.allowed_alignments == expected_alignments
    ), "Nickelback should focus on middle with some slot flexibility"
    print("✅ Nickelback allows correct lane/depth combinations")

    # Verify NB has middle focus but can play slots
    middle_positions = [
        (lane, depth) for lane, depth in nb.allowed_alignments if lane == Lane.MIDDLE
    ]
    assert len(middle_positions) == 2, "Nickelback should have 2 middle lane positions"

    # Verify NB doesn't play at line level (no press coverage)
    for lane, depth in nb.allowed_alignments:
        assert (
            depth != FootballDepth.LINE.value
        ), "Nickelback should not play press coverage at line"
        assert depth in [
            FootballDepth.BOX.value,
            FootballDepth.DEEP.value,
        ], f"Nickelback should be at box/deep level, found: {depth}"

    print("✅ Nickelback properly positioned for slot coverage")
    print("🏈 Nickelback position test completed!")


def test_safety_position():
    """
    Test the Safety position - the deep defenders and run support.

    Safeties are crucial because they:
    1. Provide deep pass coverage as the last line of defense
    2. Can come down to support run defense (strong safety)
    3. Have the most flexibility in positioning
    4. Serve as both deep coverage and run support

    In football terms: These are your FS (Free Safety) and SS (Strong Safety)
    who can play deep coverage or come down for run support.
    """
    safety = Safety()

    # Test basic properties
    assert safety.name == "S", "Safety should have name 'S'"
    print("✅ Safety name is correct")

    # Test that Safety has maximum flexibility in positioning
    expected_alignments = {
        # Deep coverage (traditional safety positions)
        (Lane.LEFT, FootballDepth.DEEP.value),
        (Lane.MIDDLE, FootballDepth.DEEP.value),
        (Lane.RIGHT, FootballDepth.DEEP.value),
        # Box support (strong safety, rover roles)
        (Lane.LEFT, FootballDepth.BOX.value),
        (Lane.MIDDLE, FootballDepth.BOX.value),
        (Lane.RIGHT, FootballDepth.BOX.value),
    }

    assert (
        safety.allowed_alignments == expected_alignments
    ), "Safety should allow all lanes at both box and deep levels"
    print("✅ Safety allows correct lane/depth combinations")

    # Verify Safety can play at both box and deep levels
    deep_positions = [
        (lane, depth)
        for lane, depth in safety.allowed_alignments
        if depth == FootballDepth.DEEP.value
    ]
    box_positions = [
        (lane, depth)
        for lane, depth in safety.allowed_alignments
        if depth == FootballDepth.BOX.value
    ]

    assert len(deep_positions) == 3, "Safety should have 3 deep positions"
    assert len(box_positions) == 3, "Safety should have 3 box positions"

    # Verify Safety doesn't play at line level
    for lane, depth in safety.allowed_alignments:
        assert (
            depth != FootballDepth.LINE.value
        ), "Safety should not play at line of scrimmage"
        assert depth in [
            FootballDepth.BOX.value,
            FootballDepth.DEEP.value,
        ], f"Safety should be at box/deep level, found: {depth}"

    print("✅ Safety has proper flexibility for deep coverage and run support")
    print("🏈 Safety position test completed!")


def test_defensive_positions_registry():
    """
    Test the DEFENSIVE_POSITIONS registry - the collection of all defensive positions.

    This registry is crucial because it:
    1. Provides a central mapping of position codes to position objects
    2. Enables the YAML loader to validate defensive positions
    3. Ensures consistent position naming across the system
    4. Supports formation validation and constraint checking

    In football terms: This is like the "defensive playbook" that defines
    all the valid defensive positions that can be used in formations.
    """
    # Test that all expected defensive positions are present
    expected_positions = {"DL", "LB", "CB", "NB", "S"}
    actual_positions = set(DEFENSIVE_POSITIONS.keys())

    assert (
        actual_positions == expected_positions
    ), f"Expected {expected_positions}, found {actual_positions}"
    print("✅ All defensive positions present in registry")

    # Test that each position has correct type and name
    position_tests = [
        ("DL", DefensiveLine, "DL"),
        ("LB", Linebacker, "LB"),
        ("CB", Cornerback, "CB"),
        ("NB", Nickelback, "NB"),
        ("S", Safety, "S"),
    ]

    for code, expected_class, expected_name in position_tests:
        position = DEFENSIVE_POSITIONS[code]
        assert isinstance(
            position, expected_class
        ), f"{code} should be instance of {expected_class.__name__}"
        assert (
            position.name == expected_name
        ), f"{code} should have name '{expected_name}', got '{position.name}'"
        print(f"✅ {code} position correctly configured")

    # Test that positions have realistic alignment counts
    alignment_counts = {
        code: len(pos.allowed_alignments) for code, pos in DEFENSIVE_POSITIONS.items()
    }

    expected_counts = {
        "DL": 3,  # Left, Middle, Right on line
        "LB": 3,  # Left, Middle, Right in box
        "CB": 6,  # Left/Right at line, box, deep levels
        "NB": 4,  # Middle at box/deep, Left/Right at box
        "S": 6,  # All lanes at box and deep levels
    }

    for code, expected_count in expected_counts.items():
        actual_count = alignment_counts[code]
        assert (
            actual_count == expected_count
        ), f"{code} should have {expected_count} alignments, got {actual_count}"
        print(f"✅ {code} has correct alignment count: {actual_count}")

    print("🏈 Defensive positions registry test completed!")
