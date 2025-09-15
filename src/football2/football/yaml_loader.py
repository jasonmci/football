"""
YAML loader for football formations.

Loads formation definitions from YAML files and creates validated
Formation objects with realistic positioning constraints.
"""

from __future__ import annotations
from typing import Dict, Any, List
from pathlib import Path
import yaml

from ..core.players import PlayerRole
from ..core.game_board import Lane, Coordinate
from .positions import (
    FootballFormation, 
    ALL_POSITIONS,
    FootballDepth,
    FootballAlignment,
    create_football_constraints,
    FOOTBALL_FIELD
)
from .formation_validator import FootballFormationValidator


class FormationLoader:
    """Loads and validates football formations from YAML files."""
    
    def __init__(self):
        self.constraints = create_football_constraints()
        self.validator = FootballFormationValidator()
    
    def load_formation(self, file_path: str | Path) -> FootballFormation:
        """Load a single formation from a YAML file."""
        with open(file_path, 'r') as f:
            data = yaml.safe_load(f)
        
        return self._create_formation_from_data(data)
    
    def load_formations_directory(self, directory_path: str | Path) -> Dict[str, FootballFormation]:
        """Load all formations from YAML files in a directory."""
        directory = Path(directory_path)
        formations = {}
        
        for yaml_file in directory.glob("*.yaml"):
            try:
                formation = self.load_formation(yaml_file)
                formations[formation.name] = formation
            except Exception as e:
                raise ValueError(f"Error loading formation from {yaml_file}: {e}")
        
        return formations
    
    def _create_formation_from_data(self, data: Dict[str, Any]) -> FootballFormation:
        """Create a FootballFormation from parsed YAML data."""
        name = data.get("name", "Unknown")
        roles_data = data.get("roles", {})
        placement_data = data.get("placement", {})
        personnel_data = data.get("allowed_personnel", [])
        
        roles = {}
        
        for role_name, role_info in roles_data.items():
            try:
                role = self._create_player_role(
                    role_name, 
                    role_info, 
                    placement_data.get(role_name)
                )
                roles[role_name] = role
            except Exception as e:
                raise ValueError(f"Error creating role '{role_name}': {e}")
        
        formation = FootballFormation(name, roles, personnel_data)
        
        # Validate against constraints
        violations = self.constraints.validate_formation(formation)
        if violations:
            raise ValueError(f"Formation '{name}' constraint violations: {violations}")
        
        # Validate against football-specific rules
        football_violations = self.validator.validate_formation(formation)
        if football_violations:
            raise ValueError(f"Formation '{name}' football rule violations: {football_violations}")
        
        return formation
    
    def _create_player_role(
        self, 
        role_name: str, 
        role_info: Dict[str, Any],
        placement_info: Dict[str, int] | None = None
    ) -> PlayerRole:
        """Create a PlayerRole from YAML role definition."""
        
        # Get position
        pos_name = role_info.get("pos")
        if not pos_name or pos_name not in ALL_POSITIONS:
            raise ValueError(f"Unknown or missing position: {pos_name}")
        
        position = ALL_POSITIONS[pos_name]
        
        # Get lane
        lane_str = role_info.get("lane", "middle")
        try:
            lane = Lane(lane_str)
        except ValueError:
            raise ValueError(f"Invalid lane: {lane_str}")
        
        # Get depth
        depth = role_info.get("depth")
        if not depth:
            raise ValueError("Missing depth specification")
        
        # Validate depth is a known football depth
        valid_depths = [d.value for d in FootballDepth]
        if depth not in valid_depths:
            raise ValueError(f"Invalid depth '{depth}'. Valid depths: {valid_depths}")
        
        # Get alignment (optional)
        alignment = role_info.get("align")
        if alignment:
            valid_alignments = [a.value for a in FootballAlignment]
            if alignment not in valid_alignments:
                raise ValueError(f"Invalid alignment '{alignment}'. Valid alignments: {valid_alignments}")
        
        # Create coordinate if placement info provided
        coordinate = None
        if placement_info:
            x = placement_info.get("x")
            y = placement_info.get("y") 
            if x is not None and y is not None:
                coordinate = Coordinate(x, y)
                
                # Validate coordinate is on the field
                if not FOOTBALL_FIELD.is_valid_position(coordinate):
                    raise ValueError(f"Position {coordinate} is outside field bounds")
        
        return PlayerRole(
            name=role_name,
            position=position,
            lane=lane,
            depth=depth,
            alignment=alignment,
            coordinate=coordinate
        )


def load_offensive_formations(directory_path: str | Path) -> Dict[str, FootballFormation]:
    """Convenience function to load offensive formations."""
    loader = FormationLoader()
    return loader.load_formations_directory(directory_path)


def load_defensive_formations(directory_path: str | Path) -> Dict[str, FootballFormation]:
    """Convenience function to load defensive formations.""" 
    loader = FormationLoader()
    return loader.load_formations_directory(directory_path)


def load_all_formations(base_path: str | Path) -> Dict[str, Dict[str, FootballFormation]]:
    """
    Load all formations from a base directory structure.
    
    Expected structure:
    base_path/
    ├── offense/
    │   ├── formation1.yaml
    │   └── formation2.yaml
    └── defense/
        ├── formation1.yaml
        └── formation2.yaml
    
    Returns:
        Dict with 'offense' and 'defense' keys containing formation dictionaries
    """
    base = Path(base_path)
    
    formations = {}
    
    offense_dir = base / "offense"
    if offense_dir.exists():
        formations["offense"] = load_offensive_formations(offense_dir)
    
    defense_dir = base / "defense" 
    if defense_dir.exists():
        formations["defense"] = load_defensive_formations(defense_dir)
    
    return formations
