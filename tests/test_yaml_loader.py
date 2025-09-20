# create a first yaml loader test
from football.yaml_loader import FormationLoader


def test_yaml_loader():
    """Test the YAML loader for formations."""
    loader = FormationLoader()
    formation = loader.load_formation("data/formations/offense/singleback_11.yaml")
    assert formation.name == "singleback_11"
    assert len(formation.roles) == 11
    print("YAML loader test passed.")


def test_load_all_formations():
    """Test loading all formations from the directory."""
    from src.football.yaml_loader import load_all_formations

    all_formations = load_all_formations("data/formations")
    assert "offense" in all_formations
    assert "defense" in all_formations
    assert len(all_formations["offense"]) > 0
    assert len(all_formations["defense"]) > 0
    print("Load all formations test passed.")


def test_create_formation_from_data():
    """Test creating a formation from data."""
    loader = FormationLoader()
    data = {
        "name": "test_formation",
        "roles": {
            "QB": {"pos": "QB", "lane": "middle", "depth": "shotgun"},
            "RB": {"pos": "RB", "lane": "right", "depth": "backfield"},
            "TE": {"pos": "TE", "lane": "right", "depth": "line", "align": "tight"},
            "WR1": {"pos": "WR", "lane": "left", "depth": "line"},
            "WR2": {"pos": "WR", "lane": "right", "depth": "line"},
            "WR3": {"pos": "WR", "lane": "right", "depth": "line"},
            "LT": {"pos": "LT", "lane": "left", "depth": "line", "align": "tight"},
            "LG": {"pos": "LG", "lane": "middle", "depth": "line", "align": "tight"},
            "C": {"pos": "C", "lane": "middle", "depth": "line", "align": "tight"},
            "RG": {"pos": "RG", "lane": "middle", "depth": "line", "align": "tight"},
            "RT": {"pos": "RT", "lane": "right", "depth": "line", "align": "tight"},
        },
        "allowed_personnel": ["11"],
    }
    formation = loader._create_formation_from_data(data)
    assert formation.name == "test_formation"
    assert len(formation.roles) == 11
    assert formation.roles["QB"].position.name == "QB"
    assert formation.roles["RB"].position.name == "RB"


def test_get_position_method():
    """
    Test the _get_position method - validates position names from YAML data.

    This method is crucial for football formation loading because it:
    1. Validates that the position name exists in our football position system
    2. Returns the actual Position object (not just a string)
    3. Provides clear error messages for invalid positions

    In football terms: ensures QB maps to Quarterback, WR to Wide Receiver, etc.

    IMPORTANT: All offensive line positions (LT, LG, C, RG, RT) map to the same
    "OL" (Offensive Line) position type because they follow the same rules
    and constraints, even though they have different roster names.
    """
    loader = FormationLoader()

    # Test valid positions - these should work for all standard football positions
    valid_positions = [
        ("QB", "QB"),  # Quarterback
        ("RB", "RB"),  # Running Back
        ("WR", "WR"),  # Wide Receiver
        ("TE", "TE"),  # Tight End
        ("LT", "OL"),  # Left Tackle -> Offensive Line
        ("LG", "OL"),  # Left Guard -> Offensive Line
        ("C", "OL"),  # Center -> Offensive Line
        ("RG", "OL"),  # Right Guard -> Offensive Line
        ("RT", "OL"),  # Right Tackle -> Offensive Line
        ("CB", "CB"),  # Cornerback
        ("S", "S"),  # Safety
        ("LB", "LB"),  # Linebacker
        ("DL", "DL"),  # Defensive Line
    ]

    for pos_code, expected_name in valid_positions:
        role_info = {"pos": pos_code}
        position = loader._get_position(role_info)

        # Verify we get back a proper Position object with correct name
        assert (
            position.name == expected_name
        ), f"Expected {expected_name}, got {position.name}"
        assert hasattr(position, "name"), "Position should have a name attribute"

        print(f"✅ Position '{pos_code}' correctly mapped to {position.name}")

    # Test missing position - should raise clear error
    try:
        role_info = {"lane": "middle", "depth": "line"}  # Missing 'pos' key
        loader._get_position(role_info)
        assert False, "Should have raised ValueError for missing position"
    except ValueError as e:
        assert "Unknown or missing position" in str(e)
        print("✅ Missing position correctly raises error")

    # Test None position - should raise clear error
    try:
        role_info = {"pos": None}
        loader._get_position(role_info)
        assert False, "Should have raised ValueError for None position"
    except ValueError as e:
        assert "Unknown or missing position" in str(e)
        print("✅ None position correctly raises error")

    # Test invalid position - should raise clear error
    try:
        role_info = {"pos": "INVALID_POSITION"}
        loader._get_position(role_info)
        assert False, "Should have raised ValueError for invalid position"
    except ValueError as e:
        assert "Unknown or missing position" in str(e)
        assert "INVALID_POSITION" in str(e)
        print("✅ Invalid position correctly raises error with position name")

    # Test empty string position - should raise clear error
    try:
        role_info = {"pos": ""}
        loader._get_position(role_info)
        assert False, "Should have raised ValueError for empty position"
    except ValueError as e:
        assert "Unknown or missing position" in str(e)
        print("✅ Empty position correctly raises error")

    print("🏈 _get_position test completed - all position validations working!")


def test_get_alignment_method():
    loader = FormationLoader()

    valid_alignments = [
        ("tight", "tight"),  # Tight alignment
        ("slot", "slot"),  # Slot alignment
        ("outside", "outside"),  # Outside alignment
        ("wingback", "wingback"),  # Wingback alignment
        ("", None),  # No alignment specified
    ]

    for align_str, expected_align in valid_alignments:
        role_info = {"align": align_str}
        alignment = loader._get_alignment(role_info)

        # Verify we get back the correct alignment string
        assert (
            alignment == expected_align
        ), f"Expected {expected_align}, got {alignment}"
        print(f"✅ Alignment '{align_str}' correctly validated as {alignment}")


def test_get_lane_depth_method():
    loader = FormationLoader()

    valid_depths = [
        ("line", "line"),  # On the line of scrimmage
        ("backfield", "backfield"),  # In the backfield (behind line)
        ("shotgun", "shotgun"),  # Shotgun depth (5-7 yards behind line)
        ("pistol", "pistol"),  # Pistol depth (3-4 yards behind line)
        ("under_center", "under_center"),  # Under center (right at line)
        ("box", "box"),  # Defensive box (5-8 yards)
        ("deep", "deep"),  # Deep (10+ yards)
    ]

    for depth_str, expected_depth in valid_depths:
        role_info = {"depth": depth_str}
        depth = loader._get_depth(role_info)

        # Verify we get back the correct depth string
        assert depth == expected_depth, f"Expected {expected_depth}, got {depth}"
        print(f"✅ Depth '{depth_str}' correctly validated as {depth}")

    # test missing depth - should raise error
    try:
        role_info = {"pos": "QB", "lane": "middle"}  # No depth specified
        loader._get_depth(role_info)
        assert False, "Should have raised ValueError for missing depth"
    except ValueError as e:
        assert "Missing depth specification" in str(e)
        print("✅ Missing depth correctly raises error")

    # test None depth - should raise error
    try:
        role_info = {"depth": None}
        loader._get_depth(role_info)
        assert False, "Should have raised ValueError for None depth"
    except ValueError as e:
        assert "Missing depth specification" in str(e)
        print("✅ None depth correctly raises error")

    # test invalid depth - should raise error
    try:
        role_info = {"depth": "INVALID_DEPTH"}
        loader._get_depth(role_info)
        assert False, "Should have raised ValueError for invalid depth"
    except ValueError as e:
        assert "Invalid depth" in str(e)
        print("✅ Invalid depth correctly raises error with depth name")

    # test empty string depth - should raise error
    try:
        role_info = {"depth": ""}
        loader._get_depth(role_info)
        assert False, "Should have raised ValueError for empty depth"
    except ValueError as e:
        assert "Missing depth specification" in str(e)
        print("✅ Empty depth correctly raises error")

    print("🏈 _get_depth test completed - all depth validations working!")


def test_get_lane_method():
    """
    Test the _get_lane method - validates lane names from YAML data.

    This method is crucial for football formation loading because it:
    1. Validates that the lane name is a valid football field lane
    2. Returns the actual Lane enum object (not just a string)
    3. Provides default "middle" lane if none specified
    4. Provides clear error messages for invalid lanes

    In football terms: lanes represent horizontal positioning on the field:
    - "left": Left side of the formation (offense looking downfield)
    - "middle": Center of the formation (where QB and center typically are)
    - "right": Right side of the formation (offense looking downfield)
    """
    from core.game_board import Lane

    loader = FormationLoader()

    # Test valid lanes - these are the three basic football field lanes
    valid_lanes = [
        ("left", Lane.LEFT),  # Left side of formation
        ("middle", Lane.MIDDLE),  # Center of formation
        ("right", Lane.RIGHT),  # Right side of formation
    ]

    for lane_str, expected_lane in valid_lanes:
        role_info = {"lane": lane_str}
        lane = loader._get_lane(role_info)

        # Verify we get back a proper Lane enum object
        assert lane == expected_lane, f"Expected {expected_lane}, got {lane}"
        assert isinstance(lane, Lane), "Should return a Lane enum object"

        print(f"✅ Lane '{lane_str}' correctly mapped to {lane}")

    # Test missing lane - should default to "middle"
    role_info = {"pos": "QB", "depth": "shotgun"}  # No lane specified
    lane = loader._get_lane(role_info)
    assert lane == Lane.MIDDLE, "Missing lane should default to MIDDLE"
    print("✅ Missing lane correctly defaults to MIDDLE")

    # Test None lane - should raise error (current implementation behavior)
    # NOTE: This reveals that dict.get("lane", "middle") returns None when
    # the key exists but has None value, rather than using the default!
    try:
        role_info = {"lane": None}
        loader._get_lane(role_info)
        assert False, "Should have raised ValueError for None lane"
    except ValueError as e:
        assert "Invalid lane: None" in str(e)
        print(
            "✅ None lane correctly raises error "
            + "(educational: shows dict.get behavior)"
        )

    # Test invalid lane - should raise clear error
    try:
        role_info = {"lane": "invalid_lane"}
        loader._get_lane(role_info)
        assert False, "Should have raised ValueError for invalid lane"
    except ValueError as e:
        assert "Invalid lane" in str(e)
        assert "invalid_lane" in str(e)
        print("✅ Invalid lane correctly raises error with lane name")

    # Test empty string lane - should raise clear error
    try:
        role_info = {"lane": ""}
        loader._get_lane(role_info)
        assert False, "Should have raised ValueError for empty lane"
    except ValueError as e:
        assert "Invalid lane" in str(e)
        print("✅ Empty lane correctly raises error")

    # Test lane with wrong case - should raise clear error
    try:
        role_info = {"lane": "LEFT"}  # Should be lowercase "left"
        loader._get_lane(role_info)
        assert False, "Should have raised ValueError for wrong case"
    except ValueError as e:
        assert "Invalid lane" in str(e)
        print("✅ Wrong case lane correctly raises error")

    print("🏈 _get_lane test completed - all lane validations working!")


def test_get_coordinate_method():
    """
    Test the _get_coordinate method - validates coordinate placement from YAML data.

    This method is crucial for football formation loading because it:
    1. Allows precise positioning of players using x,y coordinates
    2. Validates that coordinates are within the football field bounds
    3. Returns None when no placement info is provided (uses lane/depth instead)
    4. Provides clear error messages for out-of-bounds positions

    In football terms: coordinates provide exact field positioning when the
    standard lane/depth system isn't precise enough for special formations.
    """
    from core.game_board import Coordinate

    loader = FormationLoader()

    # Test valid coordinates - these should be within football field bounds
    valid_coordinates = [
        ({"x": 10, "y": 15}, Coordinate(10, 15)),  # Center field
        ({"x": 0, "y": 0}, Coordinate(0, 0)),  # Corner of field
        ({"x": 19, "y": 29}, Coordinate(19, 29)),  # Near opposite corner
        ({"x": 10, "y": 5}, Coordinate(10, 5)),  # Common position
    ]

    for placement_dict, expected_coord in valid_coordinates:
        coordinate = loader._get_coordinate(placement_dict)

        # Verify we get back a proper Coordinate object
        assert (
            coordinate == expected_coord
        ), f"Expected {expected_coord}, got {coordinate}"
        assert isinstance(coordinate, Coordinate), "Should return a Coordinate object"

        print(f"✅ Coordinate {placement_dict} correctly mapped to {coordinate}")

    # Test missing placement info - should return None
    coordinate = loader._get_coordinate(None)
    assert coordinate is None, "Missing placement info should return None"
    print("✅ Missing placement info correctly returns None")

    # Test empty placement dict - should return None
    coordinate = loader._get_coordinate({})
    assert coordinate is None, "Empty placement dict should return None"
    print("✅ Empty placement dict correctly returns None")

    # Test partial coordinates - should return None if either x or y missing
    coordinate = loader._get_coordinate({"x": 10})  # Missing y
    assert coordinate is None, "Missing y coordinate should return None"
    print("✅ Missing y coordinate correctly returns None")

    coordinate = loader._get_coordinate({"y": 15})  # Missing x
    assert coordinate is None, "Missing x coordinate should return None"
    print("✅ Missing x coordinate correctly returns None")

    # Test out-of-bounds coordinates - should raise clear error
    try:
        loader._get_coordinate({"x": -1, "y": 15})  # Negative x
        assert False, "Should have raised ValueError for out-of-bounds coordinate"
    except ValueError as e:
        assert "outside field bounds" in str(e)
        print("✅ Out-of-bounds coordinate correctly raises error")

    try:
        loader._get_coordinate({"x": 25, "y": 15})  # x too large
        assert False, "Should have raised ValueError for out-of-bounds coordinate"
    except ValueError as e:
        assert "outside field bounds" in str(e)
        print("✅ Out-of-bounds coordinate (x too large) correctly raises error")

    try:
        loader._get_coordinate({"x": 10, "y": 35})  # y too large
        assert False, "Should have raised ValueError for out-of-bounds coordinate"
    except ValueError as e:
        assert "outside field bounds" in str(e)
        print("✅ Out-of-bounds coordinate (y too large) correctly raises error")

    print("🏈 _get_coordinate test completed - all coordinate validations working!")


def test_create_player_role():
    """Test creating a player role from YAML role definition."""
    from core.game_board import Lane, Coordinate
    from football.positions import ALL_POSITIONS

    loader = FormationLoader()

    # Test basic role creation
    role_info = {"pos": "QB", "lane": "middle", "depth": "shotgun"}
    role = loader._create_player_role("QB1", role_info)

    assert role.name == "QB1"
    assert role.position == ALL_POSITIONS["QB"]
    assert role.lane == Lane.MIDDLE
    assert role.depth == "shotgun"
    assert role.alignment is None
    assert role.coordinate is None

    # Test role with alignment
    role_info_with_align = {
        "pos": "TE",
        "lane": "right",
        "depth": "line",
        "align": "tight",
    }
    role = loader._create_player_role("TE1", role_info_with_align)

    assert role.name == "TE1"
    assert role.position == ALL_POSITIONS["TE"]
    assert role.lane == Lane.RIGHT
    assert role.depth == "line"
    assert role.alignment == "tight"
    assert role.coordinate is None

    # Test role with placement info
    role_info_basic = {"pos": "WR", "lane": "left", "depth": "line"}
    placement_info = {"x": 10, "y": 5}
    role = loader._create_player_role("WR1", role_info_basic, placement_info)

    assert role.name == "WR1"
    assert role.position == ALL_POSITIONS["WR"]
    assert role.lane == Lane.LEFT
    assert role.depth == "line"
    assert role.coordinate == Coordinate(10, 5)

    print("Create player role test passed.")


def test_create_player_role_missing_position():
    """Test error for missing position."""
    loader = FormationLoader()
    role_info = {"lane": "middle", "depth": "shotgun"}
    try:
        loader._create_player_role("QB1", role_info)
        assert False, "Should have raised ValueError for missing position"
    except ValueError as e:
        assert "Unknown or missing position" in str(e)


def test_create_player_role_invalid_position():
    """Test error for invalid position."""
    loader = FormationLoader()
    role_info = {"pos": "INVALID", "lane": "middle", "depth": "shotgun"}
    try:
        loader._create_player_role("QB1", role_info)
        assert False, "Should have raised ValueError for invalid position"
    except ValueError as e:
        assert "Unknown or missing position" in str(e)


def test_create_player_role_invalid_lane():
    """Test error for invalid lane."""
    loader = FormationLoader()
    role_info = {"pos": "QB", "lane": "invalid_lane", "depth": "shotgun"}
    try:
        loader._create_player_role("QB1", role_info)
        assert False, "Should have raised ValueError for invalid lane"
    except ValueError as e:
        assert "Invalid lane" in str(e)


def test_create_player_role_missing_depth():
    """Test error for missing depth."""
    loader = FormationLoader()
    role_info = {"pos": "QB", "lane": "middle"}
    try:
        loader._create_player_role("QB1", role_info)
        assert False, "Should have raised ValueError for missing depth"
    except ValueError as e:
        assert "Missing depth specification" in str(e)


def test_create_player_role_invalid_depth():
    """Test error for invalid depth."""
    loader = FormationLoader()
    role_info = {"pos": "QB", "lane": "middle", "depth": "invalid_depth"}
    try:
        loader._create_player_role("QB1", role_info)
        assert False, "Should have raised ValueError for invalid depth"
    except ValueError as e:
        assert "Invalid depth" in str(e)


def test_create_player_role_invalid_alignment():
    """Test error for invalid alignment."""
    loader = FormationLoader()
    role_info = {
        "pos": "TE",
        "lane": "right",
        "depth": "line",
        "align": "invalid_align",
    }
    try:
        loader._create_player_role("TE1", role_info)
        assert False, "Should have raised ValueError for invalid alignment"
    except ValueError as e:
        assert "Invalid alignment" in str(e)


def test_create_player_role_invalid_coordinate():
    """Test error for invalid coordinate (outside field bounds)."""
    loader = FormationLoader()
    role_info = {"pos": "WR", "lane": "left", "depth": "line"}
    placement_info = {"x": 1000, "y": 1000}  # Way outside field bounds
    try:
        loader._create_player_role("WR1", role_info, placement_info)
        assert False, "Should have raised ValueError for invalid coordinate"
    except ValueError as e:
        assert "outside field bounds" in str(e)


def test_load_offensive_formations():
    """Test loading offensive formations from directory."""
    from football.yaml_loader import load_offensive_formations

    formations = load_offensive_formations("data/formations/offense")
    assert len(formations) > 0
    assert "spread_10" in formations
    print("Load offensive formations test passed.")


def test_load_defensive_formations():
    """Test loading defensive formations from directory."""
    from football.yaml_loader import load_defensive_formations

    formations = load_defensive_formations("data/formations/defense")
    assert len(formations) > 0
    assert "bear46" in formations
    print("Load defensive formations test passed.")
