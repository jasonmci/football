from typing import cast
from unittest.mock import patch
from football.resolver import (
    lane_for_play,
    lane_modifier,
    defensive_overlay_adjust,
    resolve_play,
    BOUNDS,
)
from football.formation_model import OffFormation, DefFormation, o, d, Lane
from football.play_v_play_matrix import BASE


class TestLaneForPlay:
    """Test cases for the lane_for_play function."""

    def test_inside_run_returns_middle(self):
        """Test that inside_run always returns middle lane."""
        assert lane_for_play("inside_run") == "middle"

    def test_outside_run_returns_left_or_right(self):
        """Test that outside_run returns left or right (not middle)."""
        with patch("random.choice") as mock_choice:
            mock_choice.return_value = "left"
            assert lane_for_play("outside_run") == "left"
            mock_choice.assert_called_once_with(["left", "right"])

    def test_short_pass_returns_middle(self):
        """Test that short_pass returns middle lane."""
        assert lane_for_play("short_pass") == "middle"

    def test_screen_returns_middle(self):
        """Test that screen returns middle lane."""
        assert lane_for_play("screen") == "middle"

    def test_deep_pass_returns_left_or_right(self):
        """Test that deep_pass returns left or right (not middle)."""
        with patch("random.choice") as mock_choice:
            mock_choice.return_value = "right"
            assert lane_for_play("deep_pass") == "right"
            mock_choice.assert_called_once_with(["left", "right"])

    def test_unknown_play_returns_middle(self):
        """Test that unknown play types default to middle."""
        assert lane_for_play("unknown_play") == "middle"
        assert lane_for_play("") == "middle"

    def test_multiple_calls_outside_run(self):
        """Test multiple calls to outside_run can return different values."""
        results = set()
        for _ in range(100):  # Run enough times to likely get both values
            result = lane_for_play("outside_run")
            results.add(result)
            if len(results) == 2:  # Got both left and right
                break
        assert "left" in results or "right" in results  # At least one should be present

    def test_multiple_calls_deep_pass(self):
        """Test multiple calls to deep_pass can return different values."""
        results = set()
        for _ in range(100):  # Run enough times to likely get both values
            result = lane_for_play("deep_pass")
            results.add(result)
            if len(results) == 2:  # Got both left and right
                break
        assert "left" in results or "right" in results  # At least one should be present


class TestLaneModifier:
    """Test cases for the lane_modifier function."""

    def test_empty_formations(self):
        """Test lane modifier with empty formations."""
        off = OffFormation()
        deff = DefFormation()
        assert lane_modifier(off, deff, "middle") == 0

    def test_offensive_advantage(self):
        """Test lane modifier when offense has more players."""
        off = OffFormation()
        deff = DefFormation()

        # Add 3 offensive players (2 wide + 1 backfield)
        o(off, "left", "wide", 2)
        o(off, "left", "backfield", 1)

        # No defensive players in left lane
        result = lane_modifier(off, deff, "left")
        assert result == 3  # Capped at max 3

    def test_defensive_advantage(self):
        """Test lane modifier when defense has more players."""
        off = OffFormation()
        deff = DefFormation()

        # Add 4 defensive players (2 line + 2 box)
        d(deff, "right", "line", 2)
        d(deff, "right", "box", 2)

        # No offensive players in right lane
        result = lane_modifier(off, deff, "right")
        assert result == -3  # Capped at min -3

    def test_balanced_formations(self):
        """Test lane modifier with balanced formations."""
        off = OffFormation()
        deff = DefFormation()

        # Equal strength: 2 off vs 2 def
        o(off, "middle", "wide", 1)
        o(off, "middle", "backfield", 1)
        d(deff, "middle", "line", 1)
        d(deff, "middle", "box", 1)

        result = lane_modifier(off, deff, "middle")
        assert result == 0

    def test_moderate_offensive_advantage(self):
        """Test moderate offensive advantage."""
        off = OffFormation()
        deff = DefFormation()

        # 3 offensive vs 1 defensive
        o(off, "left", "wide", 2)
        o(off, "left", "backfield", 1)
        d(deff, "left", "line", 1)

        result = lane_modifier(off, deff, "left")
        assert result == 2

    def test_moderate_defensive_advantage(self):
        """Test moderate defensive advantage."""
        off = OffFormation()
        deff = DefFormation()

        # 1 offensive vs 3 defensive
        o(off, "right", "wide", 1)
        d(deff, "right", "line", 2)
        d(deff, "right", "box", 1)

        result = lane_modifier(off, deff, "right")
        assert result == -2

    def test_only_line_players_count_defense(self):
        """Test that only line and box players count for defense."""
        off = OffFormation()
        deff = DefFormation()

        # Add deep defensive players (shouldn't count)
        d(deff, "middle", "deep", 5)
        o(off, "middle", "wide", 1)

        result = lane_modifier(off, deff, "middle")
        assert result == 1  # Only offensive advantage

    def test_only_wide_and_backfield_count_offense(self):
        """Test that only wide and backfield players count for offense."""
        off = OffFormation()
        deff = DefFormation()

        # Add line offensive players (shouldn't count)
        o(off, "middle", "line", 5)
        d(deff, "middle", "box", 1)

        result = lane_modifier(off, deff, "middle")
        assert result == -1  # Only defensive advantage

    def test_large_difference_capped_at_three(self):
        """Test that large differences are capped at ±3."""
        off = OffFormation()
        deff = DefFormation()

        # Extreme offensive advantage: 10 vs 0
        o(off, "left", "wide", 5)
        o(off, "left", "backfield", 5)

        result = lane_modifier(off, deff, "left")
        assert result == 3

        # Extreme defensive advantage: 0 vs 10
        off2 = OffFormation()
        deff2 = DefFormation()
        d(deff2, "right", "line", 5)
        d(deff2, "right", "box", 5)

        result2 = lane_modifier(off2, deff2, "right")
        assert result2 == -3


class TestDefensiveOverlayAdjust:
    """Test cases for the defensive_overlay_adjust function."""

    def test_no_overlay_tags(self):
        """Test with empty overlay tags."""
        result = defensive_overlay_adjust("inside_run", "middle", {})
        assert result == 0

    def test_run_commit_with_run_play(self):
        """Test run_commit overlay with run play."""
        overlay_tags = {"call": "run_commit"}
        result = defensive_overlay_adjust("inside_run", "middle", overlay_tags)
        assert result == 1

    def test_run_commit_with_pass_play(self):
        """Test run_commit overlay with pass play."""
        overlay_tags = {"call": "run_commit"}
        result = defensive_overlay_adjust("short_pass", "middle", overlay_tags)
        assert result == -1

    def test_blitz_with_pass_in_blitz_lane(self):
        """Test blitz overlay with pass play in blitzed lane."""
        overlay_tags = {"call": "blitz", "lanes": ("left", "middle")}
        result = defensive_overlay_adjust("short_pass", "left", overlay_tags)
        assert result == 2

    def test_blitz_with_pass_not_in_blitz_lane(self):
        """Test blitz overlay with pass play not in blitzed lane."""
        overlay_tags = {"call": "blitz", "lanes": ("left", "middle")}
        result = defensive_overlay_adjust("short_pass", "right", overlay_tags)
        assert result == 0

    def test_blitz_with_outside_run_not_in_blitz_lane(self):
        """Test blitz overlay with outside run not in blitzed lane."""
        overlay_tags = {"call": "blitz", "lanes": ("left",)}
        result = defensive_overlay_adjust("outside_run", "right", overlay_tags)
        assert result == -1

    def test_blitz_with_outside_run_in_blitz_lane(self):
        """Test blitz overlay with outside run in blitzed lane."""
        overlay_tags = {"call": "blitz", "lanes": ("left",)}
        result = defensive_overlay_adjust("outside_run", "left", overlay_tags)
        assert result == 0

    def test_blitz_with_inside_run(self):
        """Test blitz overlay with inside run (should have no special effect)."""
        overlay_tags = {"call": "blitz", "lanes": ("left", "right")}
        result = defensive_overlay_adjust("inside_run", "middle", overlay_tags)
        assert result == 0

    def test_short_shell_with_short_pass(self):
        """Test short_shell overlay with short pass."""
        overlay_tags = {"call": "short_shell"}
        result = defensive_overlay_adjust("short_pass", "middle", overlay_tags)
        assert result == 1

    def test_short_shell_with_other_play(self):
        """Test short_shell overlay with other play."""
        overlay_tags = {"call": "short_shell"}
        result = defensive_overlay_adjust("deep_pass", "middle", overlay_tags)
        assert result == 0

    def test_deep_shell_with_deep_pass(self):
        """Test deep_shell overlay with deep pass."""
        overlay_tags = {"call": "deep_shell"}
        result = defensive_overlay_adjust("deep_pass", "left", overlay_tags)
        assert result == 2

    def test_deep_shell_with_other_play(self):
        """Test deep_shell overlay with other play."""
        overlay_tags = {"call": "deep_shell"}
        result = defensive_overlay_adjust("short_pass", "left", overlay_tags)
        assert result == 0

    def test_unknown_call(self):
        """Test with unknown overlay call."""
        overlay_tags = {"call": "unknown_call"}
        result = defensive_overlay_adjust("inside_run", "middle", overlay_tags)
        assert result == 0


class TestBounds:
    """Test cases for the BOUNDS constant."""

    def test_bounds_structure(self):
        """Test that BOUNDS has the expected structure."""
        expected_plays = {
            "inside_run",
            "outside_run",
            "short_pass",
            "deep_pass",
            "screen",
        }
        assert set(BOUNDS.keys()) == expected_plays

    def test_bounds_values(self):
        """Test specific bound values."""
        assert BOUNDS["inside_run"] == (-3, 10)
        assert BOUNDS["outside_run"] == (-4, 15)
        assert BOUNDS["short_pass"] == (-6, 18)
        assert BOUNDS["deep_pass"] == (-10, 40)
        assert BOUNDS["screen"] == (-8, 20)

    def test_bounds_all_tuples(self):
        """Test that all bounds are tuples with min and max."""
        for play, bounds in BOUNDS.items():
            assert isinstance(bounds, tuple)
            assert len(bounds) == 2
            min_val, max_val = bounds
            assert min_val < max_val


class TestResolvePlay:
    """Test cases for the resolve_play function."""

    def test_basic_play_resolution(self):
        """Test basic play resolution without special events."""
        off = OffFormation()
        deff = DefFormation()

        with patch("random.randint") as mock_randint:
            # Mock dice roll to return 0 (6+6-7=5, 1+1-7=-5, avg=0)
            # Mock rare event to not trigger (>1)
            mock_randint.side_effect = [3, 4, 2]  # 3+4-7=0, rare=2

            result = resolve_play("inside_run", "base", off, deff)

            assert isinstance(result, dict)
            assert "lane" in result
            assert "yards" in result
            assert "event" in result
            assert "base" in result
            assert "lane_mod" in result
            assert "roll" in result

    def test_play_with_player_modifier(self):
        """Test play resolution with player modifier."""
        off = OffFormation()
        deff = DefFormation()

        with patch("random.randint") as mock_randint:
            mock_randint.side_effect = [3, 4, 10]  # roll=0, rare=10

            result = resolve_play("inside_run", "base", off, deff, player_mod=5)

            # Should include the player modifier in final yards
            base_yards = BASE[("inside_run", "base")]
            expected_yards = (
                0 + base_yards + 0 + 5
            )  # roll + base + lane_mod + player_mod
            lo, hi = BOUNDS["inside_run"]
            expected_yards = max(lo, min(hi, expected_yards))

            assert result["yards"] == expected_yards

    def test_yards_bounded_by_play_type(self):
        """Test that yards are properly bounded by play type."""
        off = OffFormation()
        deff = DefFormation()

        # Test with a play that might exceed bounds
        with patch("random.randint") as mock_randint:
            # High roll that would exceed upper bound
            mock_randint.side_effect = [6, 6, 10]  # roll=5, rare=10

            result = resolve_play("inside_run", "base", off, deff, player_mod=20)

            # Should be capped at upper bound
            lo, hi = BOUNDS["inside_run"]
            assert result["yards"] <= hi
            assert result["yards"] >= lo

    def test_interception_event(self):
        """Test interception event on passing plays."""
        off = OffFormation()
        deff = DefFormation()

        with patch("random.randint") as mock_randint:
            # rare=1 triggers interception, then negative yards
            mock_randint.side_effect = [3, 4, 1, 15]  # roll=0, rare=1, int_yards=15

            result = resolve_play("short_pass", "base", off, deff)

            assert result["event"] == "interception"
            assert result["yards"] == -15

    def test_interception_deep_pass(self):
        """Test interception on deep pass."""
        off = OffFormation()
        deff = DefFormation()

        with patch("random.randint") as mock_randint:
            mock_randint.side_effect = [3, 4, 1, 10]  # roll=0, rare=1, int_yards=10

            result = resolve_play("deep_pass", "deep_shell", off, deff)

            assert result["event"] == "interception"
            assert result["yards"] == -10

    def test_fumble_event(self):
        """Test that fumble events are no longer implemented in the current version."""
        off = OffFormation()
        deff = DefFormation()
        
        with patch("random.randint") as mock_randint:
            mock_randint.side_effect = [3, 4, 1]  # roll=0, rare=1
            
            result = resolve_play("inside_run", "base", off, deff)
            
            # Fumbles are no longer implemented in the current version
            assert result["event"] is None

    def test_sack_event(self):
        """Test sack event on blitz with negative yards."""
        off = OffFormation()
        deff = DefFormation()

        with patch("random.randint") as mock_randint:
            # Force negative yards initially, then rare<=3, then sack penalty
            mock_randint.side_effect = [1, 1, 2, 5]  # roll=-5, rare=2, sack_penalty=5

            # Need overlay_tags with blitz call for sack to trigger
            overlay_tags = {"call": "blitz"}
            result = resolve_play("short_pass", "base", off, deff, overlay_tags)

            # Should have sack event and additional negative yards
            assert result["event"] == "sack"
            # Yards should be initial negative result minus additional sack penalty
            assert result["yards"] < 0

    def test_no_sack_on_positive_yards(self):
        """Test that sack doesn't occur with positive yards."""
        off = OffFormation()
        deff = DefFormation()

        with patch("random.randint") as mock_randint:
            # Force positive yards, rare<=3 for blitz
            mock_randint.side_effect = [6, 6, 2]  # roll=5, rare=2

            result = resolve_play("short_pass", "blitz", off, deff)

            # Should not have sack event since yards are positive
            assert result["event"] is None

    def test_no_special_events_on_high_rare_roll(self):
        """Test that no special events occur with high rare roll."""
        off = OffFormation()
        deff = DefFormation()

        with patch("random.randint") as mock_randint:
            mock_randint.side_effect = [3, 4, 36]  # roll=0, rare=36 (high)

            result = resolve_play("deep_pass", "blitz", off, deff)

            assert result["event"] is None

    def test_lane_assignment_consistency(self):
        """Test that lane assignment is consistent with lane_for_play."""
        off = OffFormation()
        deff = DefFormation()

        with patch("random.randint") as mock_randint:
            mock_randint.side_effect = [3, 4, 10]  # Normal resolution

            result = resolve_play("inside_run", "base", off, deff)

            assert result["lane"] == "middle"  # inside_run always uses middle

    def test_all_play_types(self):
        """Test resolution for all play types."""
        off = OffFormation()
        deff = DefFormation()

        play_types = ["inside_run", "outside_run", "short_pass", "deep_pass", "screen"]

        for play_type in play_types:
            with patch("random.randint") as mock_randint:
                mock_randint.side_effect = [3, 4, 10]  # Normal resolution

                result = resolve_play(play_type, "base", off, deff)

                assert isinstance(result, dict)
                assert result["yards"] is not None
                assert result["lane"] in ["left", "middle", "right"]

                # Check bounds
                lo, hi = BOUNDS[play_type]
                assert lo <= result["yards"] <= hi

    def test_formation_impact_on_resolution(self):
        """Test that formations impact play resolution."""
        # Strong offensive formation
        strong_off = OffFormation()
        o(strong_off, "middle", "wide", 3)
        o(strong_off, "middle", "backfield", 2)

        # Weak defensive formation
        weak_def = DefFormation()

        # Weak offensive formation
        weak_off = OffFormation()

        # Strong defensive formation
        strong_def = DefFormation()
        d(strong_def, "middle", "line", 3)
        d(strong_def, "middle", "box", 2)

        with patch("random.randint") as mock_randint:
            mock_randint.side_effect = [3, 4, 10] * 2  # Same roll for both

            # Strong offense vs weak defense
            result1 = resolve_play("inside_run", "base", strong_off, weak_def)

            # Reset mock for second call
            mock_randint.side_effect = [3, 4, 10]

            # Weak offense vs strong defense
            result2 = resolve_play("inside_run", "base", weak_off, strong_def)

            # Strong offense should generally do better
            assert result1["lane_mod"] > result2["lane_mod"]

    def test_return_value_structure(self):
        """Test the structure of the returned dictionary."""
        off = OffFormation()
        deff = DefFormation()

        with patch("random.randint") as mock_randint:
            mock_randint.side_effect = [3, 4, 10]

            result = resolve_play("inside_run", "base", off, deff)

            # Check all required keys are present
            required_keys = {"lane", "yards", "event", "base", "lane_mod", "roll"}
            assert set(result.keys()) == required_keys

            # Check types
            assert isinstance(result["lane"], str)
            assert isinstance(result["yards"], int)
            assert result["event"] is None or isinstance(result["event"], str)
            assert isinstance(result["base"], int)
            assert isinstance(result["lane_mod"], int)
            assert isinstance(result["roll"], int)

    def test_edge_case_play_names(self):
        """Test edge cases with play names."""
        off = OffFormation()
        deff = DefFormation()
        
        # Test that interceptions can happen on any play containing "pass"
        with patch("random.randint") as mock_randint:
            mock_randint.side_effect = [3, 4, 1, 5]  # interception conditions
            
            result = resolve_play("short_pass", "base", off, deff)
            assert result["event"] == "interception"
            
            # Test that runs don't trigger interceptions with same rare roll
            mock_randint.side_effect = [3, 4, 1]
            result2 = resolve_play("outside_run", "base", off, deff)
            assert result2["event"] is None  # runs don't contain "pass"
