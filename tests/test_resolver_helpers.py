from typing import Dict, Tuple
from src.football.resolver import clamp, lane_strength, lane_modifier
from src.football.models import Lane, OffDepth, DefDepth
from src.football.models import Placement, OffFormationFull, DefFormation

OffCounts = Dict[Tuple[Lane, OffDepth], int]


def make_def(**counts: int) -> DefFormation:
    keymap: Dict[str, Tuple[Lane, DefDepth]] = {
        "left_line": ("left", "line"),
        "middle_line": ("middle", "line"),
        "right_line": ("right", "line"),
        "left_box": ("left", "box"),
        "middle_box": ("middle", "box"),
        "right_box": ("right", "box"),
        "left_deep": ("left", "deep"),
        "middle_deep": ("middle", "deep"),
        "right_deep": ("right", "deep"),
    }
    d = DefFormation()
    for k, v in counts.items():
        lane: Lane
        depth: DefDepth
        lane, depth = keymap[k]  # now typed as Literals, not plain str
        d.counts[(lane, depth)] = v
    return d


class TestLaneModifier:
    """Test the lane_modifier function."""

    def test_neutral_equal_strengths_returns_zero(self):
        off: OffCounts = {
            ("left", "line"): 2,
            ("left", "backfield"): 1,
        }  # total 3 on left
        deff = make_def(left_line=2, left_box=1)  # pressure 3 on left
        assert lane_strength(off, "left") == 3
        cap = 2
        assert lane_modifier(off, deff, "left", cap) == 0

    def test_positive_delta_respects_cap(self):
        # Offense 6 vs defense pressure 2 -> raw +4, cap at +2
        off: OffCounts = {
            ("left", "line"): 2,
            ("left", "backfield"): 2,
            ("left", "wide"): 2,
        }
        deff = make_def(left_line=1, left_box=1)
        assert lane_modifier(off, deff, "left", cap=2) == 2

    def test_negative_delta_respects_cap(self):
        # Offense 1 vs defense pressure 5 -> raw -4, cap at -2
        off: OffCounts = {("middle", "line"): 1}
        deff = make_def(middle_line=3, middle_box=2)
        assert lane_modifier(off, deff, "middle", cap=2) == -2

    def test_missing_buckets_default_to_zero(self):
        # No entries for right lane on offense or defense -> strengths 0 -> mod 0
        off: OffCounts = {("left", "line"): 1}
        deff = make_def(left_line=1)
        assert lane_modifier(off, deff, "right", cap=2) == 0

    def test_offense_strength_sums_all_depths(self):
        # Verify lane_strength uses line+backfield+wide
        off: OffCounts = {
            ("left", "line"): 1,
            ("left", "backfield"): 2,
            ("left", "wide"): 3,
        }
        assert lane_strength(off, "left") == 6

    def test_defense_pressure_sums_line_and_box_only(self):
        # deep defenders should not contribute to trench pressure
        off: OffCounts = {("right", "line"): 2}
        deff = make_def(
            right_line=1, right_box=1, right_deep=9
        )  # deep shouldn't matter
        # raw = off(2) - def(line+box=2) = 0
        assert lane_modifier(off, deff, "right", cap=2) == 0

    def test_integration_with_placements(self):
        # Build offense via model to ensure to_counts() works with lane_modifier
        form = OffFormationFull(
            [
                Placement("OL", "left", "line", 1),
                Placement("RB", "left", "backfield", 1),
                Placement("WR", "left", "wide", 2),
            ]
        )  # left total = 3
        off_counts = form.to_counts()
        deff = make_def(left_line=1, left_box=1)  # pressure = 2
        assert lane_modifier(off_counts, deff, "left", cap=2) == 2  # 3 - 2 = +1


class TestClamp:
    """Test the clamp function."""

    def test_within_bounds(self):
        """Value within bounds should remain unchanged."""
        assert clamp(5, 1, 10) == 5
        assert clamp(1, 1, 10) == 1
        assert clamp(10, 1, 10) == 10

    def test_below_lower_bound(self):
        """Value below lower bound should be set to lower bound."""
        assert clamp(0, 1, 10) == 1
        assert clamp(-5, -3, 3) == -3

    def test_above_upper_bound(self):
        """Value above upper bound should be set to upper bound."""
        assert clamp(11, 1, 10) == 10
        assert clamp(5, -3, 3) == 3

    def test_equal_bounds(self):
        """When lower and upper bounds are equal, value should be set to that bound."""
        assert clamp(5, 5, 5) == 5
        assert clamp(0, 0, 0) == 0
        assert clamp(-1, -1, -1) == -1

    def test_negative_bounds(self):
        """Test with negative bounds."""
        assert clamp(-2, -5, -1) == -2
        assert clamp(-6, -5, -1) == -5
        assert clamp(0, -5, -1) == -1


class TestLaneStrength:
    """Test the lane_strength function."""

    def test_empty_counts_dictionary(self):
        """Test with empty offensive counts dictionary."""

        off_counts = {}
        assert lane_strength(off_counts, "left") == 0
        assert lane_strength(off_counts, "middle") == 0
        assert lane_strength(off_counts, "right") == 0

    def test_single_depth_in_lane(self):
        """Test with players at only one depth in the target lane."""
        counts: OffCounts = {("left", "line"): 1}

        assert lane_strength(counts, "left") == 1
        assert lane_strength(counts, "middle") == 0
        assert lane_strength(counts, "right") == 0

    def test_sum_across_depths(self):
        # left lane has players at multiple depths; should sum to 1+2+3 = 6
        counts: OffCounts = {
            ("left", "line"): 1,
            ("left", "backfield"): 2,
            ("left", "wide"): 3,
        }
        assert lane_strength(counts, "left") == 6

    def test_missing_keys_default_to_zero(self):
        counts: OffCounts = {("middle", "line"): 5}
        # left has no entries → 0
        assert lane_strength(counts, "left") == 0
        # middle should be 5 (no backfield/wide)
        assert lane_strength(counts, "middle") == 5

    def test_with_placements(self):
        form = OffFormationFull(
            [
                Placement("OL", "left", "line", 1),
                Placement("RB", "left", "backfield", 2),
                Placement("WR", "left", "wide", 3),
            ]
        )
        counts = form.to_counts()
        assert lane_strength(counts, "left") == 6
