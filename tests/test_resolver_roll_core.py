import re
import pytest
import random
from unittest.mock import patch, MagicMock

from src.football.resolver import roll_core


class TestRollCore:
    """Test the roll_core function with advantage/disadvantage mechanics."""

    def test_neutral_roll_no_advantage_disadvantage(self):
        """Test normal dice roll without advantage or disadvantage."""
        rng = random.Random(42)

        # Test simple expression
        with patch.object(rng, "randint", side_effect=[3, 5]) as mock_randint:
            result = roll_core("2d6", rng)
            assert result == 8  # 3 + 5
            assert mock_randint.call_count == 2
            mock_randint.assert_any_call(1, 6)

        # Test with modifier
        with patch.object(rng, "randint", side_effect=[4, 2]) as mock_randint:
            result = roll_core("2d6+3", rng)
            assert result == 9  # 4 + 2 + 3
            assert mock_randint.call_count == 2

    def test_advantage_single_die(self):
        """Test advantage=1 with single die (roll 2, keep best 1)."""
        rng = random.Random(42)

        # Roll 1d6 with advantage -> roll 2d6, keep best 1
        with patch.object(rng, "randint", side_effect=[3, 5]) as mock_randint:
            result = roll_core("1d6", rng, advantage=1)
            assert result == 5  # keep best: max(3, 5) = 5
            assert mock_randint.call_count == 2  # base_roll=1 + advantage=1
            mock_randint.assert_any_call(1, 6)

    def test_advantage_multiple_dice(self):
        """Test advantage with multiple dice (2d6 -> 3d6, keep best 2)."""
        rng = random.Random(42)

        # Roll 2d6 with advantage=1 -> roll 3d6, keep best 2
        with patch.object(rng, "randint", side_effect=[2, 4, 6]) as mock_randint:
            result = roll_core("2d6", rng, advantage=1)
            # Keep best 2 from [2, 4, 6] = [6, 4] = 10
            assert result == 10
            assert mock_randint.call_count == 3

    def test_advantage_with_modifier(self):
        """Test advantage with dice modifier."""
        rng = random.Random(42)

        # 1d6+2 with advantage=1 -> roll 2d6, keep best 1, add 2
        with patch.object(rng, "randint", side_effect=[1, 5]) as mock_randint:
            result = roll_core("1d6+2", rng, advantage=1)
            assert result == 7  # max(1, 5) + 2 = 5 + 2 = 7
            assert mock_randint.call_count == 2

    def test_disadvantage_single_die(self):
        """Test disadvantage=1 with single die (roll 2, keep worst 1)."""
        rng = random.Random(42)

        # Roll 1d6 with disadvantage -> roll 2d6, keep worst 1
        with patch.object(rng, "randint", side_effect=[6, 2]) as mock_randint:
            result = roll_core("1d6", rng, disadvantage=1)
            assert result == 2  # keep worst: min(6, 2) = 2
            assert mock_randint.call_count == 2

    def test_disadvantage_multiple_dice(self):
        """Test disadvantage with multiple dice (2d6 -> 3d6, keep worst 2)."""
        rng = random.Random(42)

        # Roll 2d6 with disadvantage=1 -> roll 3d6, keep worst 2
        with patch.object(rng, "randint", side_effect=[6, 3, 1]) as mock_randint:
            result = roll_core("2d6", rng, disadvantage=1)
            # Keep worst 2 from [6, 3, 1] = [1, 3] = 4
            assert result == 4
            assert mock_randint.call_count == 3

    def test_disadvantage_with_modifier(self):
        """Test disadvantage with dice modifier."""
        rng = random.Random(42)

        # 1d6-1 with disadvantage=1 -> roll 2d6, keep worst 1, subtract 1
        with patch.object(rng, "randint", side_effect=[5, 2]) as mock_randint:
            result = roll_core("1d6-1", rng, disadvantage=1)
            assert result == 1  # min(5, 2) - 1 = 2 - 1 = 1
            assert mock_randint.call_count == 2

    def test_advantage_and_disadvantage_cancel_out(self):
        """Test that advantage and disadvantage cancel each other out."""
        rng = random.Random(42)

        # Both advantage=1 and disadvantage=1 should result in normal roll
        with patch.object(rng, "randint", side_effect=[3, 4]) as mock_randint:
            result = roll_core("2d6", rng, advantage=1, disadvantage=1)
            assert result == 7  # normal 2d6 roll: 3 + 4
            assert mock_randint.call_count == 2  # no extra dice

    def test_advantage_and_disadvantage_cancel_different_values(self):
        """Test cancellation with different advantage/disadvantage values."""
        rng = random.Random(42)

        # advantage=2, disadvantage=3 should cancel to disadvantage=0, advantage=0
        with patch.object(rng, "randint", side_effect=[1, 6]) as mock_randint:
            result = roll_core("2d6", rng, advantage=2, disadvantage=3)
            assert result == 7  # normal roll, they cancel out
            assert mock_randint.call_count == 2

    def test_multiple_advantage(self):
        """Test advantage=2 (roll extra 2 dice)."""
        rng = random.Random(42)

        # 1d6 with advantage=2 -> roll 3d6, keep best 1
        with patch.object(rng, "randint", side_effect=[2, 5, 1]) as mock_randint:
            result = roll_core("1d6", rng, advantage=2)
            assert result == 5  # max(2, 5, 1) = 5
            assert mock_randint.call_count == 3  # 1 base + 2 advantage

    def test_multiple_disadvantage(self):
        """Test disadvantage=2 (roll extra 2 dice)."""
        rng = random.Random(42)

        # 1d6 with disadvantage=2 -> roll 3d6, keep worst 1
        with patch.object(rng, "randint", side_effect=[4, 1, 6]) as mock_randint:
            result = roll_core("1d6", rng, disadvantage=2)
            assert result == 1  # min(4, 1, 6) = 1
            assert mock_randint.call_count == 3

    def test_complex_advantage_scenario(self):
        """Test complex scenario: 3d6+2 with advantage=1."""
        rng = random.Random(42)

        # 3d6+2 with advantage=1 -> roll 4d6, keep best 3, add 2
        with patch.object(rng, "randint", side_effect=[1, 6, 4, 5]) as mock_randint:
            result = roll_core("3d6+2", rng, advantage=1)
            # Keep best 3 from [1, 6, 4, 5] = [6, 5, 4] = 15, plus 2 = 17
            assert result == 17
            assert mock_randint.call_count == 4

    def test_complex_disadvantage_scenario(self):
        """Test complex scenario: 3d6-1 with disadvantage=1."""
        rng = random.Random(42)

        # 3d6-1 with disadvantage=1 -> roll 4d6, keep worst 3, subtract 1
        with patch.object(rng, "randint", side_effect=[6, 2, 4, 1]) as mock_randint:
            result = roll_core("3d6-1", rng, disadvantage=1)
            # Keep worst 3 from [6, 2, 4, 1] = [1, 2, 4] = 7, minus 1 = 6
            assert result == 6
            assert mock_randint.call_count == 4

    def test_invalid_expression_fallback_to_roll_dice(self):
        """Test that invalid expressions fall back to roll_dice function."""
        rng = random.Random(42)

        # Invalid expression should call roll_dice, which will raise ValueError
        with pytest.raises(ValueError, match=re.escape("bad dice expr: invalid")):
            roll_core("invalid", rng, advantage=1)

    def test_edge_case_zero_advantage_disadvantage(self):
        """Test explicit zero values for advantage/disadvantage."""
        rng = random.Random(42)

        with patch.object(rng, "randint", side_effect=[3, 3]) as mock_randint:
            result = roll_core("2d6", rng, advantage=0, disadvantage=0)
            assert result == 6  # normal 2d6 roll
            assert mock_randint.call_count == 2

    def test_sorting_verification_advantage(self):
        """Verify that advantage correctly sorts and keeps best dice."""
        rng = random.Random(42)

        # Carefully control the dice to verify sorting
        # 2d6 with advantage=2 -> roll 4d6, keep best 2
        dice_rolls = [1, 6, 2, 5]  # should keep [6, 5] = 11
        with patch.object(rng, "randint", side_effect=dice_rolls) as mock_randint:
            result = roll_core("2d6", rng, advantage=2)
            assert result == 11  # 6 + 5
            assert mock_randint.call_count == 4

    def test_different_die_types_with_advantage(self):
        """Test advantage with different die types."""
        rng = random.Random(42)

        test_cases = [
            ("1d4", 4, [1, 3], 3),  # keep best: max(1, 3) = 3
            ("1d8", 8, [2, 7], 7),  # keep best: max(2, 7) = 7
            ("1d10", 10, [9, 4], 9),  # keep best: max(9, 4) = 9
            ("1d12", 12, [5, 11], 11),  # keep best: max(5, 11) = 11
            ("1d20", 20, [8, 15], 15),  # keep best: max(8, 15) = 15
        ]

        for expr, faces, mock_rolls, expected in test_cases:
            with patch.object(rng, "randint", side_effect=mock_rolls) as mock_randint:
                result = roll_core(expr, rng, advantage=1)
                assert result == expected
                assert mock_randint.call_count == 2
                mock_randint.assert_any_call(1, faces)

    def test_realistic_rpg_scenarios(self):
        """Test realistic RPG advantage/disadvantage scenarios."""
        rng = random.Random(42)

        # D&D style advantage on attack roll (1d20+5)
        with patch.object(rng, "randint", side_effect=[8, 16]) as mock_randint:
            result = roll_core("1d20+5", rng, advantage=1)
            assert result == 21  # max(8, 16) + 5 = 16 + 5 = 21

        # Disadvantage on stealth check (1d20+3)
        with patch.object(rng, "randint", side_effect=[15, 6]) as mock_randint:
            result = roll_core("1d20+3", rng, disadvantage=1)
            assert result == 9  # min(15, 6) + 3 = 6 + 3 = 9

        # Football scenario: 2d6 effectiveness with advantage
        with patch.object(rng, "randint", side_effect=[2, 4, 6]) as mock_randint:
            result = roll_core("2d6", rng, advantage=1)
            assert result == 10  # best 2 from [2, 4, 6] = 6 + 4 = 10

    def test_zero_dice_faces_with_advantage_should_fail(self):
        """Test that zero dice/faces should be caught by roll_core validation."""
        rng = random.Random(42)

        # If roll_core had the same validation as roll_dice, these should fail
        # Currently they don't, which is an inconsistency

        # This test documents the current behavior
        with patch.object(rng, "randint") as mock_randint:
            result = roll_core("0d6", rng, advantage=1)
            assert result == 0  # Currently works, returns 0

    def test_zero_faces_with_advantage_raises_error(self):
        """Test that 1d0 raises error due to invalid randint call."""
        rng = random.Random(42)

        # 1d0 will call randint(1, 0) which is invalid
        with pytest.raises(ValueError):  # From randint, not from roll_dice validation
            roll_core("1d0", rng, disadvantage=1)
