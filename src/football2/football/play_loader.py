"""
YAML loader for football plays using the new play system.

Loads plays that inherit from formations and include dynamic modifications.
"""

import yaml
from typing import Dict, List, Optional, Any
from pathlib import Path
from ..core.game_board import Coordinate
from .plays import (
    FootballPlay, PreSnapShift, PlayerMotion, DefensiveMotionReaction,
    PlayerAssignment, PreSnapAction, DefensiveReaction,
    AssignmentType, PlayExecutor
)
from .yaml_loader import FormationLoader


class PlayLoader:
    """Loads football plays from YAML files."""
    
    def __init__(self, formation_loader: FormationLoader):
        self.formation_loader = formation_loader
        self._plays_cache = {}
    
    def load_play(self, play_file: Path) -> FootballPlay:
        """Load a single play from a YAML file."""
        if play_file in self._plays_cache:
            return self._plays_cache[play_file]
        
        with open(play_file, 'r') as f:
            data = yaml.safe_load(f)
        
        play = self._create_play_from_data(data)
        self._plays_cache[play_file] = play
        return play
    
    def load_plays_from_directory(self, directory: Path) -> Dict[str, FootballPlay]:
        """Load all plays from a directory."""
        plays = {}
        
        if not directory.exists():
            return plays
        
        for play_file in directory.glob("*.yaml"):
            try:
                play = self.load_play(play_file)
                plays[play.name] = play
            except Exception as e:
                print(f"Warning: Failed to load play {play_file}: {e}")
        
        return plays
    
    def _create_play_from_data(self, data: Dict[str, Any]) -> FootballPlay:
        """Create a FootballPlay from YAML data."""
        # Basic play information
        name = data["name"]
        label = data.get("label", name)
        base_formation = data["formation"]
        personnel = data.get("personnel", [])
        if isinstance(personnel, str):
            personnel = [personnel]
        
        play_type = data.get("play_type", "run")
        tags = data.get("tags", [])
        
        # Pre-snap modifications
        pre_snap_shifts = self._parse_pre_snap_shifts(data.get("pre_snap_shifts", []))
        motion = self._parse_motion(data.get("motion"))
        defensive_reactions = self._parse_defensive_reactions(data.get("defensive_reactions", []))
        
        # Player assignments
        assignments = self._parse_assignments(data.get("assignments", []))
        
        # Additional details
        snap_count = data.get("snap_count")
        audible_options = data.get("audible_options", [])
        
        return FootballPlay(
            name=name,
            label=label,
            base_formation=base_formation,
            personnel=personnel,
            play_type=play_type,
            tags=tags,
            pre_snap_shifts=pre_snap_shifts,
            motion=motion,
            defensive_reactions=defensive_reactions,
            assignments=assignments,
            snap_count=snap_count,
            audible_options=audible_options
        )
    
    def _parse_pre_snap_shifts(self, shifts_data: List[Dict]) -> List[PreSnapShift]:
        """Parse pre-snap shift data using football abstractions."""
        shifts = []
        
        for shift_data in shifts_data:
            action = PreSnapAction(shift_data["action"])
            player_position = shift_data["player"]
            
            target_lane = shift_data.get("target_lane")
            target_depth = shift_data.get("target_depth")
            target_alignment = shift_data.get("target_alignment")
            target_player = shift_data.get("target_player")
            timing = shift_data.get("timing", 1)
            
            shifts.append(PreSnapShift(
                player_position=player_position,
                action=action,
                target_lane=target_lane,
                target_depth=target_depth,
                target_alignment=target_alignment,
                target_player=target_player,
                timing=timing
            ))
        
        return shifts
    
    def _parse_motion(self, motion_data: Optional[Dict]) -> Optional[PlayerMotion]:
        """Parse motion data using football abstractions."""
        if not motion_data:
            return None
        
        player_position = motion_data["player"]
        motion_type = motion_data["type"]  # Now just a string, not enum
        
        start_lane = motion_data.get("start_lane")
        start_depth = motion_data.get("start_depth")
        end_lane = motion_data.get("end_lane")
        end_depth = motion_data.get("end_depth")
        end_alignment = motion_data.get("end_alignment")
        speed = motion_data.get("speed", "normal")
        
        return PlayerMotion(
            player_position=player_position,
            motion_type=motion_type,
            start_lane=start_lane,
            start_depth=start_depth,
            end_lane=end_lane,
            end_depth=end_depth,
            end_alignment=end_alignment,
            speed=speed
        )
    
    def _parse_defensive_reactions(self, reactions_data: List[Dict]) -> List[DefensiveMotionReaction]:
        """Parse defensive reaction data."""
        reactions = []
        
        for reaction_data in reactions_data:
            defensive_position = reaction_data["player"]
            reaction_type = DefensiveReaction(reaction_data["reaction"])
            target_player = reaction_data.get("target")
            
            new_position = None
            if "new_position" in reaction_data:
                pos_data = reaction_data["new_position"]
                new_position = Coordinate(pos_data["x"], pos_data["y"])
            
            reactions.append(DefensiveMotionReaction(
                defensive_position=defensive_position,
                reaction_type=reaction_type,
                target_player=target_player,
                new_position=new_position
            ))
        
        return reactions
    
    def _parse_assignments(self, assignments_data: List[Dict]) -> List[PlayerAssignment]:
        """Parse player assignment data."""
        assignments = []
        
        for assignment_data in assignments_data:
            player_position = assignment_data["player"]
            assignment_type = AssignmentType(assignment_data["assignment"])
            
            details = assignment_data.get("details", {})
            target = assignment_data.get("target")
            zone = assignment_data.get("zone")
            depth = assignment_data.get("depth")
            direction = assignment_data.get("direction")
            
            assignments.append(PlayerAssignment(
                player_position=player_position,
                assignment_type=assignment_type,
                details=details,
                target=target,
                zone=zone,
                depth=depth,
                direction=direction
            ))
        
        return assignments
    
    def validate_play_against_formation(self, play: FootballPlay) -> List[str]:
        """Validate that a play is compatible with its base formation."""
        violations = []
        
        try:
            # Load formations to find the base formation
            all_formations = self.formation_loader.load_formations_directory(
                Path("data/formations/offense")  # Assuming this is the path
            )
            
            formation = all_formations.get(play.base_formation)
            if not formation:
                violations.append(f"Base formation '{play.base_formation}' not found")
                return violations
            
            # Check that all players in assignments exist in formation
            formation_players = set(formation.roles.keys())
            play_players = set(assignment.player_position for assignment in play.assignments)
            
            missing_players = play_players - formation_players
            if missing_players:
                violations.append(f"Play references players not in formation: {missing_players}")
            
            # Check personnel grouping compatibility
            if play.personnel and formation.personnel:
                if not any(p in formation.personnel for p in play.personnel):
                    violations.append(f"Play personnel {play.personnel} doesn't match formation {formation.personnel}")
            
        except Exception as e:
            violations.append(f"Cannot validate against formation {play.base_formation}: {e}")
        
        return violations
