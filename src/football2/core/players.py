"""
Player positioning system for sports simulations.

Defines positions, roles, and constraints for realistic player placement
while allowing strategic flexibility in formation design.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Protocol, Set, Tuple, Dict, Optional, List
from enum import Enum
from abc import ABC, abstractmethod

from .game_board import Coordinate, Lane


class Position(ABC):
    """Abstract base class for player positions (QB, RB, etc.)."""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """The position name (e.g., 'QB', 'WR')."""
        ...
    
    @property
    @abstractmethod
    def allowed_alignments(self) -> Set[Tuple[Lane, str]]:
        """Valid (lane, depth) combinations for this position."""
        ...


@dataclass(frozen=True)
class PlayerRole:
    """
    A specific assignment/role for a player in a formation.
    
    Separates the player's position (what they are) from their role 
    (what they're doing in this formation).
    """
    name: str              # Role identifier (e.g., "QB", "WR1", "MLB")
    position: Position     # The player's position type
    lane: Lane            # Horizontal alignment
    depth: str            # Vertical alignment (sport-specific)
    alignment: Optional[str] = None  # Specific alignment within depth (tight, slot, etc.)
    coordinate: Optional[Coordinate] = None  # Exact board position
    
    def __post_init__(self):
        # Validate that this role's depth is allowed for the position
        if (self.lane, self.depth) not in self.position.allowed_alignments:
            raise ValueError(
                f"Invalid alignment for {self.position.name}: "
                f"{self.lane.value}/{self.depth}"
            )


class Formation(ABC):
    """Abstract base class for team formations."""
    
    def __init__(self, name: str, roles: Dict[str, PlayerRole]):
        self.name = name
        self.roles = roles
        self._validate_formation()
    
    @abstractmethod
    def _validate_formation(self) -> None:
        """Validate that the formation meets sport-specific rules."""
        ...
    
    @property
    @abstractmethod 
    def required_player_count(self) -> int:
        """Number of players required for this formation."""
        ...
    
    def get_role(self, role_name: str) -> PlayerRole:
        """Get a specific role from the formation."""
        if role_name not in self.roles:
            raise KeyError(f"Role '{role_name}' not found in formation '{self.name}'")
        return self.roles[role_name]
    
    def get_roles_by_position(self, position: Position) -> Dict[str, PlayerRole]:
        """Get all roles for players at a specific position."""
        return {
            name: role for name, role in self.roles.items() 
            if role.position == position
        }


class PositionConstraints:
    """
    Manages realistic positioning constraints to prevent unrealistic alignments.
    
    Examples:
    - WRs can't line up 30 yards behind QB
    - Offensive linemen must be near the line of scrimmage
    - Defensive backs shouldn't be in the backfield
    """
    
    def __init__(self):
        self.distance_constraints: Dict[Tuple[str, str], Tuple[int, int]] = {}
        self.depth_constraints: Dict[str, Tuple[int, int]] = {}
    
    def add_distance_constraint(
        self, 
        position1: str, 
        position2: str, 
        min_distance: int, 
        max_distance: int
    ) -> None:
        """Add a distance constraint between two positions."""
        key: Tuple[str, str] = tuple(sorted([position1, position2]))  # type: ignore
        self.distance_constraints[key] = (min_distance, max_distance)
    
    def add_depth_constraint(
        self, 
        position: str, 
        min_depth: int, 
        max_depth: int
    ) -> None:
        """Add a depth constraint for a position."""
        self.depth_constraints[position] = (min_depth, max_depth)
    
    def validate_formation(self, formation: Formation) -> List[str]:
        """
        Validate a formation against all constraints.
        
        Returns:
            List of constraint violations (empty if valid)
        """
        violations = []
        
        # Check distance constraints
        for (pos1, pos2), (min_dist, max_dist) in self.distance_constraints.items():
            violations.extend(
                self._check_distance_constraint(formation, pos1, pos2, min_dist, max_dist)
            )
        
        # Check depth constraints  
        for position, (min_depth, max_depth) in self.depth_constraints.items():
            violations.extend(
                self._check_depth_constraint(formation, position, min_depth, max_depth)
            )
        
        return violations
    
    def _check_distance_constraint(
        self, 
        formation: Formation, 
        pos1: str, 
        pos2: str, 
        min_dist: int, 
        max_dist: int
    ) -> List[str]:
        """Check distance constraints between positions."""
        violations = []
        
        # Get all roles for each position
        roles1 = [r for r in formation.roles.values() if r.position.name == pos1]
        roles2 = [r for r in formation.roles.values() if r.position.name == pos2]
        
        for role1 in roles1:
            for role2 in roles2:
                if role1.coordinate and role2.coordinate:
                    distance = role1.coordinate.distance_to(role2.coordinate)
                    if not (min_dist <= distance <= max_dist):
                        violations.append(
                            f"Distance between {role1.name} and {role2.name} "
                            f"({distance:.1f}) violates constraint ({min_dist}-{max_dist})"
                        )
        
        return violations
    
    def _check_depth_constraint(
        self, 
        formation: Formation, 
        position: str, 
        min_depth: int, 
        max_depth: int
    ) -> List[str]:
        """Check depth constraints for a position."""
        violations = []
        
        roles = [r for r in formation.roles.values() if r.position.name == position]
        for role in roles:
            if role.coordinate:
                if not (min_depth <= role.coordinate.y <= max_depth):
                    violations.append(
                        f"{role.name} depth ({role.coordinate.y}) "
                        f"violates constraint ({min_depth}-{max_depth})"
                    )
        
        return violations
