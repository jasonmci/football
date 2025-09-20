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
    from football.yaml_loader import load_all_formations

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
