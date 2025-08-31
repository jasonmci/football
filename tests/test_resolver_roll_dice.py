import re
import pytest
import random
from unittest.mock import patch, MagicMock

from src.football.resolver import roll_dice


class TestRollDice:
    """Test the roll_dice function."""

    def test_simple_dice_expression(self):
        """Test basic dice expressions like '1d6'."""
        rng = random.Random(42)  # Fixed seed for reproducible tests

        # Mock the randint to return predictable values
        with patch.object(rng, "randint", return_value=4) as mock_randint:
            result = roll_dice("1d6", rng)
            assert result == 4
            mock_randint.assert_called_once_with(1, 6)

    def test_multiple_dice(self):
        """Test expressions with multiple dice like '2d6'."""
        rng = random.Random(42)

        # Mock randint to return [3, 5] for two dice rolls
        with patch.object(rng, "randint", side_effect=[3, 5]) as mock_randint:
            result = roll_dice("2d6", rng)
            assert result == 8  # 3 + 5
            assert mock_randint.call_count == 2
            mock_randint.assert_any_call(1, 6)

    def test_dice_with_positive_modifier(self):
        """Test dice expressions with positive modifiers like '1d10+3'."""
        rng = random.Random(42)

        with patch.object(rng, "randint", return_value=7) as mock_randint:
            result = roll_dice("1d10+3", rng)
            assert result == 10  # 7 + 3
            mock_randint.assert_called_once_with(1, 10)

    def test_dice_with_negative_modifier(self):
        """Test dice expressions with negative modifiers like '2d6-2'."""
        rng = random.Random(42)

        with patch.object(rng, "randint", side_effect=[4, 3]) as mock_randint:
            result = roll_dice("2d6-2", rng)
            assert result == 5  # 4 + 3 - 2
            assert mock_randint.call_count == 2

    def test_different_die_types(self):
        """Test different die types (d4, d8, d10, d12, d20)."""
        rng = random.Random(42)

        test_cases = [
            ("1d4", 4, 2, 2),
            ("1d8", 8, 6, 6),
            ("1d10", 10, 8, 8),
            ("1d12", 12, 9, 9),
            ("1d20", 20, 15, 15),
        ]

        for expr, faces, mock_roll, expected in test_cases:
            with patch.object(rng, "randint", return_value=mock_roll) as mock_randint:
                result = roll_dice(expr, rng)
                assert result == expected
                mock_randint.assert_called_with(1, faces)

    def test_large_number_of_dice(self):
        """Test expressions with many dice like '10d6'."""
        rng = random.Random(42)

        # Mock 10 dice rolls all returning 3
        with patch.object(rng, "randint", return_value=3) as mock_randint:
            result = roll_dice("10d6", rng)
            assert result == 30  # 10 * 3
            assert mock_randint.call_count == 10

    def test_complex_expression(self):
        """Test complex expressions like '3d8+5'."""
        rng = random.Random(42)

        with patch.object(rng, "randint", side_effect=[2, 7, 4]) as mock_randint:
            result = roll_dice("3d8+5", rng)
            assert result == 18  # 2 + 7 + 4 + 5
            assert mock_randint.call_count == 3
            mock_randint.assert_any_call(1, 8)

    def test_whitespace_handling(self):
        """Test that whitespace in expressions is handled correctly."""
        rng = random.Random(42)

        test_cases = [
            " 1d6 ",
            "  2d8+1  ",
            "\t1d10-2\t",
            " 3d4 + 2 ",  # Note: this should fail with current regex
        ]

        # Valid cases (no spaces around operators)
        with patch.object(rng, "randint", return_value=5):
            assert roll_dice(" 1d6 ", rng) == 5

        with patch.object(rng, "randint", side_effect=[3, 4]):
            assert roll_dice("  2d8+1  ", rng) == 8  # 3 + 4 + 1

        with patch.object(rng, "randint", return_value=6):
            assert roll_dice("\t1d10-2\t", rng) == 4  # 6 - 2

    def test_invalid_dice_expressions(self):
        """Test that invalid dice expressions raise ValueError."""
        rng = random.Random(42)

        invalid_expressions = [
            "not_a_dice",
            "1d",
            "d6",
            "1x6",
            "1d6+",
            "-1d6",
            "1d0",
            "0d6",
            "1.5d6",
            "1d6.5",
            "1d6++1",
            "1d6--1",
            "1 d 6",  # spaces around 'd'
            "1d6 + 1",  # spaces around '+'
        ]

        for expr in invalid_expressions:
            with pytest.raises(ValueError, match=re.escape(f"bad dice expr: {expr}")):
                roll_dice(expr, rng)

    def test_edge_cases(self):
        """Test edge cases for dice expressions."""
        rng = random.Random(42)

        # Minimum possible roll (1d1+0 = 1)
        with patch.object(rng, "randint", return_value=1) as mock_randint:
            result = roll_dice("1d1", rng)
            assert result == 1
            mock_randint.assert_called_with(1, 1)

        # Zero modifier
        with patch.object(rng, "randint", return_value=4):
            result = roll_dice("1d6+0", rng)
            assert result == 4

        # Large modifier
        with patch.object(rng, "randint", return_value=1):
            result = roll_dice("1d6+100", rng)
            assert result == 101

        # Large negative modifier
        with patch.object(rng, "randint", return_value=6):
            result = roll_dice("1d6-10", rng)
            assert result == -4

    def test_regex_pattern_matching(self):
        """Test the regex pattern matching more thoroughly."""
        rng = random.Random(42)

        # Valid patterns
        valid_patterns = [
            "1d6",
            "12d10",
            "100d100",
            "1d6+1",
            "1d6-1",
            "1d6+999",
            "1d6-999",
        ]

        for pattern in valid_patterns:
            with patch.object(rng, "randint", return_value=1):
                # Should not raise an exception
                roll_dice(pattern, rng)

        # Invalid patterns that might look valid
        invalid_patterns = [
            "1d6+1+1",  # multiple operators
            "1d6-+1",  # conflicting operators
            "1d6+-1",  # conflicting operators
            "+1d6",  # leading operator
            "1d6x2",  # wrong operator
        ]

        for pattern in invalid_patterns:
            with pytest.raises(ValueError):
                roll_dice(pattern, rng)

    def test_realistic_gaming_scenarios(self):
        """Test realistic gaming dice scenarios."""
        rng = random.Random(42)

        # Common RPG dice
        with patch.object(rng, "randint", side_effect=[4, 4]):
            result = roll_dice("2d6", rng)  # Common for many games
            assert result == 8

        # D&D style damage roll
        with patch.object(rng, "randint", side_effect=[6, 3]):
            result = roll_dice("2d6+2", rng)  # Sword damage
            assert result == 11

        # Percentile roll
        with patch.object(rng, "randint", return_value=50):
            result = roll_dice("1d100", rng)
            assert result == 50

    def test_random_state_independence(self):
        """Test that the function doesn't modify the RNG state unexpectedly."""
        rng = random.Random(42)
        initial_state = rng.getstate()

        # Call roll_dice
        roll_dice("1d6", rng)

        # The state should have changed (one randint call)
        new_state = rng.getstate()
        assert initial_state != new_state

        # But calling it again should give different results
        result1 = roll_dice("1d6", rng)
        result2 = roll_dice("1d6", rng)
        # They might be the same by chance, but the RNG state changed
        final_state = rng.getstate()
        assert new_state != final_state
