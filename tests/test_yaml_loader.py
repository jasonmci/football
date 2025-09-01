import os
import tempfile
from unittest.mock import patch, MagicMock

import pytest

from src.football.models import DefFormation, OffFormationFull
from src.football.yaml_loader import (
    ALLOWED_COMBOS,
    load_def_formations,
    load_off_formations,
)


class TestLoadOffFormations:
    """Test the load_off_formations function."""

    def test_valid_offensive_formation(self):
        """Test loading a valid offensive formation."""
        yaml_content = """
formations:
  - key: "i_formation"
    placements:
      - pos: "QB"
        lane: "middle"
        depth: "backfield"
        count: 1
      - pos: "RB"
        lane: "middle"
        depth: "backfield"
        count: 1
      - pos: "FB"
        lane: "middle"
        depth: "backfield"
        count: 1
      - pos: "WR"
        lane: "left"
        depth: "wide"
        count: 1
      - pos: "WR"
        lane: "right"
        depth: "wide"
        count: 1
      - pos: "TE"
        lane: "right"
        depth: "line"
        count: 1
      - pos: "OL"
        lane: "left"
        depth: "line"
        count: 1
      - pos: "OL"
        lane: "middle"
        depth: "line"
        count: 3
      - pos: "OL"
        lane: "right"
        depth: "line"
        count: 1
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write(yaml_content)
            f.flush()

            result = load_off_formations(f.name)

            assert "i_formation" in result
            assert isinstance(result["i_formation"], OffFormationFull)
            assert len(result["i_formation"].placements) == 9

        os.unlink(f.name)

    def test_unknown_position(self):
        """Test error for unknown position."""
        yaml_content = """
formations:
  - key: "bad_formation"
    placements:
      - pos: "INVALID_POS"
        lane: "middle"
        depth: "backfield"
        count: 1
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write(yaml_content)
            f.flush()

            with pytest.raises(ValueError, match="unknown pos 'INVALID_POS'"):
                load_off_formations(f.name)

        os.unlink(f.name)

    def test_illegal_alignment(self):
        """Test error for illegal position alignment."""
        yaml_content = """
formations:
  - key: "bad_formation"
    placements:
      - pos: "TE"
        lane: "middle"
        depth: "wide"
        count: 1
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write(yaml_content)
            f.flush()

            with pytest.raises(
                ValueError, match="illegal alignment for TE: middle/wide"
            ):
                load_off_formations(f.name)

        os.unlink(f.name)

    def test_wrong_player_count(self):
        """Test error when total players != 11."""
        yaml_content = """
formations:
  - key: "bad_formation"
    placements:
      - pos: "QB"
        lane: "middle"
        depth: "backfield"
        count: 1
      - pos: "OL"
        lane: "middle"
        depth: "line"
        count: 5
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write(yaml_content)
            f.flush()

            with pytest.raises(
                ValueError, match="offensive formation totals 6, expected 11"
            ):
                load_off_formations(f.name)

        os.unlink(f.name)

    @patch.object(OffFormationFull, "validate")
    def test_formation_validation_error(self, mock_validate: MagicMock):
        """Test error when formation validation fails."""
        mock_validate.return_value = ["Some validation error"]

        yaml_content = """
formations:
  - key: "bad_formation"
    placements:
      - pos: "QB"
        lane: "middle"
        depth: "backfield"
        count: 1
      - pos: "OL"
        lane: "left"
        depth: "line"
        count: 5
      - pos: "OL"
        lane: "middle"
        depth: "line"
        count: 3
      - pos: "OL"
        lane: "right"
        depth: "line"
        count: 2
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write(yaml_content)
            f.flush()

            with pytest.raises(ValueError, match="validation errors"):
                load_off_formations(f.name)

        os.unlink(f.name)


class TestLoadDefFormations:
    """Test the load_def_formations function."""

    def test_valid_defensive_formation(self):
        """Test loading a valid defensive formation."""
        yaml_content = """
formations:
  - key: "4_3_base"
    counts:
      - lane: "left"
        depth: "line"
        count: 1
      - lane: "middle"
        depth: "line"
        count: 2
      - lane: "right"
        depth: "line"
        count: 1
      - lane: "left"
        depth: "box"
        count: 1
      - lane: "middle"
        depth: "box"
        count: 1
      - lane: "right"
        depth: "box"
        count: 1
      - lane: "left"
        depth: "deep"
        count: 1
      - lane: "middle"
        depth: "deep"
        count: 1
      - lane: "right"
        depth: "deep"
        count: 2
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write(yaml_content)
            f.flush()

            result = load_def_formations(f.name)

            assert "4_3_base" in result
            assert isinstance(result["4_3_base"], DefFormation)

            # Check some specific counts
            formation = result["4_3_base"]
            assert formation.counts[("middle", "line")] == 2
            assert formation.counts[("right", "deep")] == 2

        os.unlink(f.name)

    def test_illegal_defensive_depth(self):
        """Test error for illegal defensive depth."""
        yaml_content = """
formations:
  - key: "bad_formation"
    counts:
      - lane: "middle"
        depth: "invalid_depth"
        count: 1
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write(yaml_content)
            f.flush()

            with pytest.raises(
                ValueError, match="illegal defensive depth 'invalid_depth'"
            ):
                load_def_formations(f.name)

        os.unlink(f.name)

    def test_wrong_defensive_player_count(self):
        """Test error when total defensive players != 11."""
        yaml_content = """
formations:
  - key: "bad_formation"
    counts:
      - lane: "middle"
        depth: "line"
        count: 5
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write(yaml_content)
            f.flush()

            with pytest.raises(
                ValueError, match="defensive formation totals 5, expected 11"
            ):
                load_def_formations(f.name)

        os.unlink(f.name)

    def test_accumulating_counts(self):
        """Test that multiple entries for same lane/depth accumulate."""
        yaml_content = """
formations:
  - key: "accumulate_test"
    counts:
      - lane: "middle"
        depth: "line"
        count: 2
      - lane: "middle"
        depth: "line"
        count: 1
      - lane: "left"
        depth: "box"
        count: 3
      - lane: "right"
        depth: "box"
        count: 3
      - lane: "middle"
        depth: "deep"
        count: 2
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write(yaml_content)
            f.flush()

            result = load_def_formations(f.name)

            formation = result["accumulate_test"]
            assert formation.counts[("middle", "line")] == 3  # 2 + 1
            assert formation.counts[("left", "box")] == 3
            assert formation.counts[("right", "box")] == 3
            assert formation.counts[("middle", "deep")] == 2

        os.unlink(f.name)

    def test_empty_formations_file(self):
        """Test loading empty formations file."""
        yaml_content = """
formations: []
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write(yaml_content)
            f.flush()

            result = load_def_formations(f.name)
            assert result == {}

        os.unlink(f.name)


class TestAllowedCombos:
    """Test the ALLOWED_COMBOS constant."""

    def test_allowed_combos_structure(self):
        """Test that ALLOWED_COMBOS has expected structure."""
        expected_positions = {"QB", "RB", "FB", "WR", "TE", "OL"}
        assert set(ALLOWED_COMBOS.keys()) == expected_positions

        # Test QB can only be in middle/backfield
        assert ALLOWED_COMBOS["QB"] == {("middle", "backfield")}

        # Test WR can only be on wide receivers positions
        assert ALLOWED_COMBOS["WR"] == {("left", "wide"), ("right", "wide")}

        # Test TE flexibility
        expected_te = {
            ("left", "line"),
            ("right", "line"),
            ("left", "wide"),
            ("right", "wide"),
        }
        assert ALLOWED_COMBOS["TE"] == expected_te

    def test_all_positions_have_valid_lanes(self):
        """Test that all positions have valid lane assignments."""
        valid_lanes = {"left", "middle", "right"}
        valid_off_depths = {"line", "backfield", "wide"}

        for pos, combos in ALLOWED_COMBOS.items():
            for lane, depth in combos:
                assert lane in valid_lanes, f"{pos} has invalid lane: {lane}"
                assert depth in valid_off_depths, f"{pos} has invalid depth: {depth}"
