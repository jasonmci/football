from typing import cast
from football.formation_model import (
    OffFormationFull,
    DefFormation,
    o,
    d,
    Lane,
    OffDepth,
    DefDepth,
    to_counts
)


class TestOffFormation:
    """Test cases for OffFormation class."""

    def test_off_formation_initialization(self):
        """Test that OffFormation initializes with correct defaults."""
        formation = OffFormationFull()

        assert to_counts(formation) == {}
        assert formation.has_qb is True

    def test_off_formation_custom_initialization(self):
        """Test OffFormation with custom values."""
        counts = {
            (cast(Lane, "left"), cast(OffDepth, "line")): 2,
            (cast(Lane, "right"), cast(OffDepth, "wide")): 1,
        }
        formation = OffFormation(counts=counts, has_qb=False)  # type: ignore

        assert formation.counts == counts
        assert formation.has_qb is False

    def test_off_formation_counts_type(self):
        """Test that counts dictionary accepts valid lane/depth combinations."""
        formation = OffFormationFull()
        formation.counts[("left", "line")] = 1
        formation.counts[("middle", "backfield")] = 2
        formation.counts[("right", "wide")] = 3

        assert formation.counts[("left", "line")] == 1
        assert formation.counts[("middle", "backfield")] == 2
        assert formation.counts[("right", "wide")] == 3


class TestDefFormation:
    """Test cases for DefFormation class."""

    def test_def_formation_initialization(self):
        """Test that DefFormation initializes with correct defaults."""
        formation = DefFormation()

        assert formation.counts == {}

    def test_def_formation_custom_initialization(self):
        """Test DefFormation with custom values."""
        counts = {
            (cast(Lane, "left"), cast(DefDepth, "line")): 3,
            (cast(Lane, "middle"), cast(DefDepth, "box")): 2,
        }
        formation = DefFormation(counts=counts)  # type: ignore

        assert formation.counts == counts

    def test_def_formation_counts_type(self):
        """Test that counts dictionary accepts valid lane/depth combinations."""
        formation = DefFormation()
        formation.counts[("left", "line")] = 4
        formation.counts[("middle", "box")] = 3
        formation.counts[("right", "deep")] = 2

        assert formation.counts[("left", "line")] == 4
        assert formation.counts[("middle", "box")] == 3
        assert formation.counts[("right", "deep")] == 2


class TestOffensiveHelper:
    """Test cases for the 'o' helper function."""

    def test_o_function_adds_single_player(self):
        """Test adding a single player to a position."""
        formation = OffFormation()
        o(formation, "left", "line")

        assert formation.counts[("left", "line")] == 1

    def test_o_function_adds_multiple_players(self):
        """Test adding multiple players to a position."""
        formation = OffFormation()
        o(formation, "middle", "backfield", 3)

        assert formation.counts[("middle", "backfield")] == 3

    def test_o_function_accumulates_players(self):
        """Test that multiple calls accumulate players."""
        formation = OffFormation()
        o(formation, "right", "wide", 2)
        o(formation, "right", "wide", 1)

        assert formation.counts[("right", "wide")] == 3

    def test_o_function_different_positions(self):
        """Test adding players to different positions."""
        formation = OffFormation()
        o(formation, "left", "line", 2)
        o(formation, "middle", "backfield", 1)
        o(formation, "right", "wide", 3)

        assert formation.counts[("left", "line")] == 2
        assert formation.counts[("middle", "backfield")] == 1
        assert formation.counts[("right", "wide")] == 3

    def test_o_function_zero_players(self):
        """Test adding zero players (edge case)."""
        formation = OffFormation()
        o(formation, "left", "line", 0)

        assert formation.counts[("left", "line")] == 0

    def test_o_function_all_lane_combinations(self):
        """Test all valid lane combinations."""
        formation = OffFormation()
        lanes: list[Lane] = ["left", "middle", "right"]
        depths: list[OffDepth] = ["line", "backfield", "wide"]

        for lane in lanes:
            for depth in depths:
                o(formation, lane, depth, 1)

        for lane in lanes:
            for depth in depths:
                assert formation.counts[(lane, depth)] == 1


class TestDefensiveHelper:
    """Test cases for the 'd' helper function."""

    def test_d_function_adds_single_player(self):
        """Test adding a single player to a position."""
        formation = DefFormation()
        d(formation, "left", "line")

        assert formation.counts[("left", "line")] == 1

    def test_d_function_adds_multiple_players(self):
        """Test adding multiple players to a position."""
        formation = DefFormation()
        d(formation, "middle", "box", 4)

        assert formation.counts[("middle", "box")] == 4

    def test_d_function_accumulates_players(self):
        """Test that multiple calls accumulate players."""
        formation = DefFormation()
        d(formation, "right", "deep", 1)
        d(formation, "right", "deep", 2)

        assert formation.counts[("right", "deep")] == 3

    def test_d_function_different_positions(self):
        """Test adding players to different positions."""
        formation = DefFormation()
        d(formation, "left", "line", 3)
        d(formation, "middle", "box", 4)
        d(formation, "right", "deep", 2)

        assert formation.counts[("left", "line")] == 3
        assert formation.counts[("middle", "box")] == 4
        assert formation.counts[("right", "deep")] == 2

    def test_d_function_zero_players(self):
        """Test adding zero players (edge case)."""
        formation = DefFormation()
        d(formation, "left", "line", 0)

        assert formation.counts[("left", "line")] == 0

    def test_d_function_all_lane_combinations(self):
        """Test all valid lane combinations."""
        formation = DefFormation()
        lanes: list[Lane] = ["left", "middle", "right"]
        depths: list[DefDepth] = ["line", "box", "deep"]

        for lane in lanes:
            for depth in depths:
                d(formation, lane, depth, 1)

        for lane in lanes:
            for depth in depths:
                assert formation.counts[(lane, depth)] == 1


class TestFormationIntegration:
    """Integration tests combining offensive and defensive formations."""

    def test_basic_formation_setup(self):
        """Test setting up a basic offensive and defensive formation."""
        off = OffFormation()
        defn = DefFormation()

        # Set up a basic offensive formation
        o(off, "left", "line", 1)  # Left tackle
        o(off, "middle", "line", 3)  # Center and guards
        o(off, "right", "line", 1)  # Right tackle
        o(off, "middle", "backfield", 1)  # Running back
        o(off, "left", "wide", 1)  # Left receiver
        o(off, "right", "wide", 1)  # Right receiver

        # Set up a basic defensive formation
        d(defn, "left", "line", 1)  # Left end
        d(defn, "middle", "line", 2)  # Defensive tackles
        d(defn, "right", "line", 1)  # Right end
        d(defn, "left", "box", 1)  # Left linebacker
        d(defn, "middle", "box", 2)  # Middle linebackers
        d(defn, "right", "box", 1)  # Right linebacker
        d(defn, "left", "deep", 1)  # Left safety/corner
        d(defn, "middle", "deep", 1)  # Safety
        d(defn, "right", "deep", 1)  # Right safety/corner

        # Verify offensive formation (should total 8 + QB = 11 players)
        total_off_players = sum(off.counts.values())
        assert total_off_players == 8  # 8 + QB = 11
        assert off.has_qb is True

        # Verify defensive formation (should total 11 players)
        total_def_players = sum(defn.counts.values())
        assert total_def_players == 11

    def test_formation_modification(self):
        """Test modifying formations after initial setup."""
        off = OffFormation()

        # Initial setup
        o(off, "left", "wide", 1)
        assert off.counts[("left", "wide")] == 1

        # Add more players to same position
        o(off, "left", "wide", 2)
        assert off.counts[("left", "wide")] == 3

        # Add players to different position
        o(off, "right", "wide", 1)
        assert off.counts[("right", "wide")] == 1
        assert off.counts[("left", "wide")] == 3  # Should remain unchanged


class TestTypeConstraints:
    """Test type constraints and edge cases."""

    def test_lane_types(self):
        """Test that all lane types work correctly."""
        formation = OffFormation()
        lanes: list[Lane] = ["left", "middle", "right"]

        for lane in lanes:
            o(formation, lane, "line", 1)
            assert formation.counts[(lane, "line")] == 1

    def test_off_depth_types(self):
        """Test that all offensive depth types work correctly."""
        formation = OffFormation()
        depths: list[OffDepth] = ["line", "backfield", "wide"]

        for depth in depths:
            o(formation, "middle", depth, 1)
            assert formation.counts[("middle", depth)] == 1

    def test_def_depth_types(self):
        """Test that all defensive depth types work correctly."""
        formation = DefFormation()
        depths: list[DefDepth] = ["line", "box", "deep"]

        for depth in depths:
            d(formation, "middle", depth, 1)
            assert formation.counts[("middle", depth)] == 1
