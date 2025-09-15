"""
Football-specific formation validation rules.

Enforces realistic constraints beyond basic position alignment rules.
"""

from typing import List, Dict
from ..core.players import Formation
from .positions import FootballFormation


class FootballFormationValidator:
    """Validates football formations against realistic constraints."""
    
    def __init__(self):
        self.max_positions = {
            "QB": 1,    # Only one quarterback
            "S": 2,     # Maximum 2 safeties 
            "CB": 2,    # Maximum 2 cornerbacks
        }
        
        self.min_positions = {
            "QB": 1,    # Must have exactly one quarterback (offense only)
        }
    
    def validate_formation(self, formation: Formation) -> List[str]:
        """
        Validate a formation against football-specific rules.
        
        Returns:
            List of validation errors (empty if valid)
        """
        violations = []
        
        # Count positions
        position_counts = self._count_positions(formation)
        
        # Check maximum limits
        for pos, max_count in self.max_positions.items():
            actual_count = position_counts.get(pos, 0)
            if actual_count > max_count:
                violations.append(
                    f"Too many {pos} players: {actual_count} (max {max_count})"
                )
        
        # Check minimum requirements for offensive formations
        # If it has offensive players (WR, RB, TE, OL) but no QB, that's a problem
        if self._has_offensive_players(formation) and not self._has_quarterback(formation):
            violations.append("Offensive formation must have exactly 1 QB")
        
        # If it has a QB, enforce other offensive rules
        if self._has_quarterback(formation):
            for pos, min_count in self.min_positions.items():
                actual_count = position_counts.get(pos, 0)
                if actual_count < min_count:
                    violations.append(
                        f"Too few {pos} players: {actual_count} (min {min_count})"
                    )
        
        # Check total defensive backs
        if self._is_defensive_formation(formation):
            db_count = (position_counts.get("CB", 0) + 
                       position_counts.get("S", 0) + 
                       position_counts.get("NB", 0))
            if db_count > 6:
                violations.append(
                    f"Too many defensive backs: {db_count} (max 6)"
                )
        
        # Validate personnel groupings for offensive formations
        if self._has_quarterback(formation):
            personnel_violations = self._validate_personnel_grouping(formation)
            violations.extend(personnel_violations)
        
        return violations
    
    def _count_positions(self, formation: Formation) -> Dict[str, int]:
        """Count how many players at each position."""
        counts = {}
        for role in formation.roles.values():
            pos_name = role.position.name
            counts[pos_name] = counts.get(pos_name, 0) + 1
        return counts
    
    def _is_offensive_formation(self, formation: Formation) -> bool:
        """Check if this is an offensive formation (has QB)."""
        return any(role.position.name == "QB" for role in formation.roles.values())
    
    def _is_defensive_formation(self, formation: Formation) -> bool:
        """Check if this is a defensive formation (has DL/LB/DB)."""
        defensive_positions = {"DL", "LB", "CB", "S", "NB"}
        return any(
            role.position.name in defensive_positions 
            for role in formation.roles.values()
        )
    
    def _has_quarterback(self, formation: Formation) -> bool:
        """Check if formation has a quarterback."""
        return any(role.position.name == "QB" for role in formation.roles.values())
    
    def _has_offensive_players(self, formation: Formation) -> bool:
        """Check if formation has typical offensive players."""
        offensive_positions = {"QB", "RB", "FB", "WR", "TE", "OL", "LT", "LG", "C", "RG", "RT"}
        return any(
            role.position.name in offensive_positions 
            for role in formation.roles.values()
        )
    
    def _validate_personnel_grouping(self, formation: Formation) -> List[str]:
        """Validate that the formation matches its declared personnel grouping."""
        violations = []
        
        # Only validate personnel for FootballFormation instances
        if not isinstance(formation, FootballFormation) or not formation.personnel:
            return violations  # Skip validation if not a FootballFormation or no personnel declared
        
        # Count actual skill position players
        position_counts = self._count_positions(formation)
        actual_rb = position_counts.get("RB", 0) + position_counts.get("FB", 0)
        actual_te = position_counts.get("TE", 0)
        actual_wr = position_counts.get("WR", 0)
        
        # Parse personnel notation (e.g., "11" = 1 RB, 1 TE)
        for personnel in formation.personnel:
            if len(personnel) == 2 and personnel.isdigit():
                expected_rb = int(personnel[0])
                expected_te = int(personnel[1])
                expected_wr = 5 - expected_rb - expected_te  # Remaining skill players are WRs
                
                if actual_rb == expected_rb and actual_te == expected_te and actual_wr == expected_wr:
                    return violations  # Found a matching personnel grouping
        
        # If we get here, no personnel grouping matched
        violations.append(
            f"Personnel mismatch: formation has {actual_rb}RB/{actual_te}TE/{actual_wr}WR "
            f"but declares {formation.personnel}"
        )
        
        return violations
