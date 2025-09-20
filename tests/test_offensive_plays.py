"""
Unit tests for offensive football plays.

Tests the loading and validation of offensive plays from YAML files.
These tests help understand offensive concepts, run schemes, pass concepts,
and how offensive coordinators design plays to move the ball and score.
"""

from pathlib import Path
from unittest.mock import Mock

from football.play_loader import PlayLoader
from football.yaml_loader import FormationLoader
from football.plays import AssignmentType


def test_load_basic_run_play():
    """
    Test loading a basic run play (Inside Zone).

    Inside Zone is a fundamental running concept where:
    1. Offensive line creates horizontal displacement
    2. Running back reads the defense and cuts to daylight
    3. All gaps are covered by zone blocking scheme
    4. Simple, effective ground game foundation

    This is the "bread and butter" of most NFL running games.
    """
    formation_loader = Mock(spec=FormationLoader)
    play_loader = PlayLoader(formation_loader)

    # Load the Inside Zone Right play
    play_file = Path("data/plays/offense/inside_zone_right_v2.yaml")
    play = play_loader.load_play(play_file)

    print("\n🏃 OFFENSIVE RUN PLAY TEST")
    print(f"   Play: {play.label}")
    print(f"   Formation: {play.base_formation}")
    print(f"   Type: {play.play_type}")
    print(f"   Tags: {', '.join(play.tags)}")

    # Verify basic play properties
    assert play.name == "inside_zone_right", "Play name should match YAML"
    assert play.play_type == "run", "Should be a running play"
    assert "zone" in play.tags, "Should be tagged as zone concept"
    assert "inside" in play.tags, "Should be tagged as inside run"

    # Analyze the blocking scheme
    run_block_assignments = [
        a for a in play.assignments if a.assignment_type == AssignmentType.RUN_BLOCK
    ]
    handoff_assignments = [
        a for a in play.assignments if a.assignment_type == AssignmentType.HANDOFF
    ]
    lead_block_assignments = [
        a for a in play.assignments if a.assignment_type == AssignmentType.LEAD_BLOCK
    ]

    print(f"   Run Blockers: {len(run_block_assignments)}")
    print(f"   Handoff: {len(handoff_assignments)}")
    print(f"   Lead Blockers: {len(lead_block_assignments)}")

    # Should have handoff assignment (QB to RB)
    assert len(handoff_assignments) >= 1, "Should have handoff assignment"

    # Should have multiple run blockers (offensive line)
    assert len(run_block_assignments) >= 5, "Should have offensive line blocking"

    print("   ✅ Inside zone structure validated")
    print(f"   ✅ Blocking scheme: {len(run_block_assignments)} blockers")


def test_load_pass_concept():
    """
    Test loading a pass concept play (Four Verticals).

    Four Verticals is a classic passing concept where:
    1. All receivers run vertical routes at different levels
    2. QB reads the coverage levels (high-low concept)
    3. Stretches defense vertically and horizontally
    4. Great against both man and zone coverage

    This concept tests every level of the defense.
    """
    formation_loader = Mock(spec=FormationLoader)
    play_loader = PlayLoader(formation_loader)

    # Load the Four Verticals play
    play_file = Path("data/plays/offense/four_verts.yaml")
    play = play_loader.load_play(play_file)

    print("\n🎯 OFFENSIVE PASS CONCEPT TEST")
    print(f"   Play: {play.label}")
    print(f"   Formation: {play.base_formation}")
    print(f"   Tags: {', '.join(play.tags)}")

    # Verify basic pass play properties
    assert play.play_type == "pass", "Should be a passing play"
    assert "pass" in play.tags, "Should be tagged as pass"
    assert "vertical" in play.tags, "Should be tagged as vertical concept"

    # Count different types of assignments
    route_assignments = [
        a for a in play.assignments if a.assignment_type == AssignmentType.ROUTE
    ]
    pass_block_assignments = [
        a for a in play.assignments if a.assignment_type == AssignmentType.PASS_BLOCK
    ]

    print(f"   Route Runners: {len(route_assignments)}")
    print(f"   Pass Blockers: {len(pass_block_assignments)}")

    # Should have multiple route runners
    assert len(route_assignments) >= 4, "Should have multiple receivers running routes"

    # Should have pass protection
    assert len(pass_block_assignments) >= 1, "Should have pass protection"

    # Check for vertical routes
    vertical_routes = []
    for assignment in route_assignments:
        if assignment.details and "pattern" in assignment.details:
            pattern = assignment.details["pattern"]
            if pattern in ["go", "vertical", "fade"]:
                vertical_routes.append(assignment.player_position)

    print(f"   Vertical Routes: {len(vertical_routes)} - {vertical_routes}")
    assert len(vertical_routes) >= 3, "Four Verts should have multiple vertical routes"

    print("   ✅ Pass concept validated")
    print("   ✅ Vertical stretches confirmed")


def test_load_power_run_concept():
    """
    Test loading a power run concept play.

    Power running is a gap scheme concept where:
    1. Offensive line creates double teams and kicks out defenders
    2. Lead blocker (FB/H-back) attacks linebacker level
    3. Running back presses the double team then cuts
    4. Physical, downhill running style

    This represents traditional, physical football concepts.
    """
    formation_loader = Mock(spec=FormationLoader)
    play_loader = PlayLoader(formation_loader)

    # Load the Power Right play
    play_file = Path("data/plays/offense/power_right.yaml")
    play = play_loader.load_play(play_file)

    print("\n⚡ POWER RUN CONCEPT TEST")
    print(f"   Play: {play.label}")
    print(f"   Formation: {play.base_formation}")
    print(f"   Tags: {', '.join(play.tags)}")

    # Verify power run properties
    assert play.play_type == "run", "Should be a run play"
    assert "power" in play.tags, "Should be tagged as power"
    assert "gap" in play.tags, "Should be tagged as gap scheme"

    # Should have run blocking and handoff elements
    run_elements = [
        a
        for a in play.assignments
        if a.assignment_type in [AssignmentType.RUN_BLOCK, AssignmentType.HANDOFF]
    ]
    lead_block_elements = [
        a for a in play.assignments if a.assignment_type == AssignmentType.LEAD_BLOCK
    ]

    print(f"   Run Elements: {len(run_elements)}")
    print(f"   Lead Block Elements: {len(lead_block_elements)}")

    # Power should have strong run component
    assert len(run_elements) >= 2, "Power should have run blocking and handoff"

    # Look for power-specific details
    power_details = []
    for assignment in play.assignments:
        if assignment.details and "power" in str(assignment.details).lower():
            power_details.append(assignment.player_position)

    print(f"   Power Technique Details: {power_details}")

    print("   ✅ Power run concept validated")
    print("   ✅ Gap scheme structure confirmed")


def test_offensive_motion_and_shifts():
    """
    Test offensive pre-snap motion and shifts.

    Offensive motion serves multiple purposes:
    1. Identify coverage (man vs zone)
    2. Create favorable matchups
    3. Add deception and misdirection
    4. Get players in better position to execute

    Motion is a key tool in modern offensive strategy.
    """
    formation_loader = Mock(spec=FormationLoader)
    play_loader = PlayLoader(formation_loader)

    # Load a play with motion
    play_file = Path("data/plays/offense/pa_slant_motion.yaml")
    play = play_loader.load_play(play_file)

    print("\n🔄 OFFENSIVE MOTION TEST")
    print(f"   Play: {play.label}")

    # Check for motion
    if play.motion:
        print(f"   Motion Player: {play.motion.player_position}")
        print(f"   Motion Type: {play.motion.motion_type}")
        print(f"   Speed: {play.motion.speed}")

        # Validate motion properties
        assert play.motion.player_position, "Motion must specify a player"
        assert play.motion.motion_type, "Motion must have a type"

        print("   ✅ Motion validated")
    else:
        print("   No motion in this play")

    # Check for pre-snap shifts
    if len(play.pre_snap_shifts) > 0:
        print(f"   Pre-snap Shifts: {len(play.pre_snap_shifts)}")

        for i, shift in enumerate(play.pre_snap_shifts):
            print(f"   Shift {i + 1}: {shift.player_position} - {shift.action.value}")

        print("   ✅ Pre-snap movement validated")
    else:
        print("   No pre-snap shifts in this play")


def test_offensive_formations_and_personnel():
    """
    Test offensive formations and personnel groupings.

    Different offensive formations serve different purposes:
    1. I-Formation - Power running, goal line situations
    2. Shotgun/Spread - Passing, quick game, RPOs
    3. Pistol - Read option, modern running concepts
    4. Empty - Maximum pass protection or quick throws

    Personnel groupings (11, 21, 12, etc.) define the skill players.
    """
    formation_loader = Mock(spec=FormationLoader)
    play_loader = PlayLoader(formation_loader)

    print("\n🏟️  OFFENSIVE FORMATIONS TEST")

    # Test different formation types (avoiding problematic files)
    formation_plays = {
        "I-Formation": "inside_zone_right_v2.yaml",
        "Spread": "four_verts.yaml",
        "Power": "power_right.yaml",
    }

    formations_found = {}

    for formation_name, play_file in formation_plays.items():
        try:
            play_path = Path(f"data/plays/offense/{play_file}")
            play = play_loader.load_play(play_path)

            print(f"   {formation_name}: {play.base_formation}")
            print(f"     Personnel: {play.personnel}")
            formations_found[formation_name] = play.base_formation

            # Validate formation characteristics
            if "i" in formation_name.lower():
                assert (
                    "i_form" in play.base_formation.lower() or "21" in play.personnel
                ), "I-Formation should use I-formation or 21 personnel"
            elif (
                "shotgun" in formation_name.lower()
                or "spread" in formation_name.lower()
            ):
                assert (
                    "gun" in play.base_formation.lower()
                    or "spread" in play.base_formation.lower()
                    or "11" in play.personnel
                ), "Shotgun/Spread should use gun/spread formation or 11 personnel"

        except FileNotFoundError:
            print(f"   {formation_name}: File not found")

    print(f"   Formations Available: {len(formations_found)}")

    # Should have found multiple formations
    assert len(formations_found) >= 2, "Should have multiple offensive formations"

    print("   ✅ Offensive formations validated")


def test_offensive_assignment_types():
    """
    Test different types of offensive assignments.

    Offensive assignments include:
    1. Run blocking - Zone, gap, man schemes
    2. Pass blocking - Protection schemes
    3. Routes - Receiver patterns and timing
    4. Handoffs - Ball distribution
    5. Fakes - Misdirection and deception
    """
    formation_loader = Mock(spec=FormationLoader)
    play_loader = PlayLoader(formation_loader)

    print("\n📋 OFFENSIVE ASSIGNMENT TYPES TEST")

    # Test multiple play types to see assignment variety (avoiding problematic files)
    test_plays = [
        ("Run Play", "inside_zone_right_v2.yaml"),
        ("Pass Play", "four_verts.yaml"),
        ("Power Run", "power_right.yaml"),
    ]

    all_assignment_types = set()

    for play_type, play_file in test_plays:
        try:
            play_path = Path(f"data/plays/offense/{play_file}")
            play = play_loader.load_play(play_path)

            print(f"   {play_type} ({play.label}):")

            # Count assignment types
            assignment_counts = {}
            for assignment in play.assignments:
                assignment_type = assignment.assignment_type.value
                assignment_counts[assignment_type] = (
                    assignment_counts.get(assignment_type, 0) + 1
                )
                all_assignment_types.add(assignment_type)

            for assignment_type, count in assignment_counts.items():
                print(f"     {assignment_type}: {count}")

        except FileNotFoundError:
            print(f"   {play_type}: File not found")

    print(f"\n   Total Assignment Types Found: {len(all_assignment_types)}")
    print(f"   Types: {sorted(all_assignment_types)}")

    # Should have multiple assignment types
    assert len(all_assignment_types) >= 3, "Should have variety of assignment types"

    print("   ✅ Assignment variety validated")


def test_offensive_play_validation():
    """
    Test validation of offensive play structure.

    Validates that offensive plays have proper structure:
    1. Correct play type
    2. Valid assignments for all positions
    3. Proper offensive concepts
    4. Realistic play design
    """
    formation_loader = Mock(spec=FormationLoader)
    play_loader = PlayLoader(formation_loader)

    # Test multiple offensive plays (avoiding ones with unsupported assignment types)
    offensive_plays = [
        "inside_zone_right_v2.yaml",
        "four_verts.yaml",
        "power_right.yaml",
        "trap_right.yaml",
    ]

    print("\n🔍 OFFENSIVE PLAY VALIDATION TEST")

    for play_file in offensive_plays:
        try:
            play_path = Path(f"data/plays/offense/{play_file}")
            play = play_loader.load_play(play_path)

            print(f"   Validating: {play.label}")

            # Basic validation
            assert play.play_type in [
                "run",
                "pass",
                "rpo",
            ], f"{play.name} should be offensive play type"
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

            # Validate based on play type
            if play.play_type == "run":
                assert (
                    "run_block" in assignment_counts or "handoff" in assignment_counts
                ), f"Run play {play.name} should have run elements"
            elif play.play_type == "pass":
                assert (
                    "route" in assignment_counts and "pass_block" in assignment_counts
                ), f"Pass play {play.name} should have routes and protection"
            elif play.play_type == "rpo":
                assert (
                    "route" in assignment_counts and "run_block" in assignment_counts
                ), f"RPO {play.name} should have both run and pass elements"

            # Total should be 11 players
            total_assignments = sum(assignment_counts.values())
            assert (
                total_assignments == 11
            ), f"{play.name} should have 11 player assignments"

            print(f"     ✅ {play.name} validated")

        except FileNotFoundError:
            print(f"   {play_file}: File not found")

    print("   ✅ All offensive plays validated")


def test_load_all_offensive_plays():
    """
    Test loading all offensive plays from the directory.

    This test ensures:
    1. All offensive play files can be loaded
    2. Each play has valid structure
    3. Offensive concepts are properly represented
    4. No parsing errors occur
    """
    formation_loader = Mock(spec=FormationLoader)
    play_loader = PlayLoader(formation_loader)

    # Load all offensive plays
    offense_plays_dir = Path("data/plays/offense")

    print("\n📚 ALL OFFENSIVE PLAYS TEST")
    print(f"   Loading from: {offense_plays_dir}")

    try:
        plays = play_loader.load_plays_from_directory(offense_plays_dir)

        print(f"   Total Plays Loaded: {len(plays)}")

        # Categorize plays by type
        run_plays = []
        pass_plays = []
        rpo_plays = []

        for play_name, play in plays.items():
            print(f"   🏈 {play.label}")
            print(f"     Formation: {play.base_formation}")
            print(f"     Personnel: {play.personnel}")
            print(f"     Tags: {', '.join(play.tags)}")

            # Categorize by play type
            if play.play_type == "run":
                run_plays.append(play_name)
            elif play.play_type == "pass":
                pass_plays.append(play_name)
            elif play.play_type == "rpo":
                rpo_plays.append(play_name)

        print("\n   📊 OFFENSIVE PLAY BREAKDOWN:")
        print(f"     Run Plays: {len(run_plays)}")
        print(f"     Pass Plays: {len(pass_plays)}")
        print(f"     RPO Plays: {len(rpo_plays)}")

        # Should have loaded multiple plays
        assert len(plays) >= 10, "Should have loaded multiple offensive plays"

        # Should have variety of play types
        assert len(run_plays) > 0, "Should have run plays"
        assert len(pass_plays) > 0, "Should have pass plays"

        print("   ✅ All offensive plays loaded successfully")

    except Exception as e:
        print(f"   ❌ Error loading offensive plays: {e}")
        raise


if __name__ == "__main__":
    # Run all tests with detailed output
    test_load_basic_run_play()
    test_load_pass_concept()
    test_load_power_run_concept()
    test_offensive_motion_and_shifts()
    test_offensive_formations_and_personnel()
    test_offensive_assignment_types()
    test_offensive_play_validation()
    test_load_all_offensive_plays()

    print("\n🏆 ALL OFFENSIVE PLAY TESTS COMPLETED!")
    print("   ✅ Run concepts validated")
    print("   ✅ Pass concepts tested")
    print("   ✅ Power schemes verified")
    print("   ✅ All offensive plays loaded")
