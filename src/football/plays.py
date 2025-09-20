"""
Football play system built on formation foundation.

Defines plays as dynamic modifications to base formations, including:
- Pre-snap shifts and adjustments
- Player motion (offense and defensive reactions)
- Position-specific assignments and responsibilities
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any
from core.game_board import Coordinate
from .positions import FootballFormation


class PreSnapAction(Enum):
    """Types of pre-snap actions players can take."""

    SHIFT_LEFT = "shift_left"
    SHIFT_RIGHT = "shift_right"
    MOVE_UP = "move_up"
    MOVE_BACK = "move_back"
    MOVE_WIDE = "move_wide"
    MOVE_TIGHT = "move_tight"
    FLIP_FORMATION = "flip_formation"
    STACK = "stack"  # Move behind another player
    BUNCH = "bunch"  # Move close to group of receivers


class MotionType(Enum):
    """Types of motion a player can execute."""

    ORBIT = "orbit"  # Around the formation
    JET = "jet"  # Across the formation at speed
    SHUTTLE = "shuttle"  # Short back and forth
    FADE = "fade"  # Backing out of formation
    SHIFT = "shift"  # Simple positional change


class DefensiveReaction(Enum):
    """How defense can react to offensive motion."""

    FOLLOW = "follow"  # DB follows receiver
    ROTATE = "rotate"  # Safety rotation
    BUMP = "bump"  # Bump coverage assignments
    IGNORE = "ignore"  # No reaction
    ALERT = "alert"  # Ready to react but no movement


class AssignmentType(Enum):
    """Categories of assignments for different play types."""

    # Offensive assignments
    RUN_BLOCK = "run_block"
    PASS_BLOCK = "pass_block"
    ROUTE = "route"
    HANDOFF = "handoff"
    FAKE = "fake"
    LEAD_BLOCK = "lead_block"

    # Defensive assignments
    RUSH = "rush"
    COVERAGE = "coverage"
    RUN_FIT = "run_fit"
    BLITZ = "blitz"
    SPY = "spy"  # Follow specific player


@dataclass
class PreSnapShift:
    """Defines a pre-snap movement for a player using football abstractions."""

    player_position: str  # Position name (QB, RB1, WR1, etc.)
    action: PreSnapAction
    target_lane: Optional[str] = None  # Lane.LEFT, Lane.MIDDLE, Lane.RIGHT
    target_depth: Optional[str] = None  # FootballDepth values
    target_alignment: Optional[str] = None  # FootballAlignment values
    target_player: Optional[str] = None  # For stacking/bunching
    timing: int = 1  # Order of execution (1 = first, 2 = second, etc.)


@dataclass
class PlayerMotion:
    """Defines motion for a single player using football abstractions."""

    player_position: str
    motion_type: str  # "jet", "orbit", "shift", "bunch"
    start_lane: Optional[str] = None  # Starting lane if different from formation
    start_depth: Optional[str] = None  # Starting depth if different
    end_lane: Optional[str] = None  # Ending lane
    end_depth: Optional[str] = None  # Ending depth
    end_alignment: Optional[str] = None  # Final alignment
    speed: str = "normal"  # "slow", "normal", "fast"


@dataclass
class DefensiveMotionReaction:
    """How defense reacts to offensive motion."""

    defensive_position: str
    reaction_type: DefensiveReaction
    target_player: Optional[str] = None  # Player to follow/cover
    new_position: Optional[Coordinate] = None


@dataclass
class PlayerAssignment:
    """Specific assignment for a player during the play."""

    player_position: str
    assignment_type: AssignmentType
    details: Dict[str, Any] = field(default_factory=dict)

    # Common assignment properties
    target: Optional[str] = None  # Player to block/cover/follow
    zone: Optional[str] = None  # Zone responsibility
    depth: Optional[int] = None  # Route depth, rush depth, etc.
    direction: Optional[str] = None  # left, right, inside, outside


class PositionAssignmentCatalog:
    """Defines available assignments for each position."""

    OFFENSIVE_ASSIGNMENTS = {
        "QB": [
            AssignmentType.HANDOFF,
            AssignmentType.FAKE,
            AssignmentType.ROUTE,  # For trick plays/rollouts
        ],
        "RB": [
            AssignmentType.RUN_BLOCK,  # When carrying the ball, it's still a "run play"
            AssignmentType.PASS_BLOCK,
            AssignmentType.ROUTE,
            AssignmentType.LEAD_BLOCK,
            AssignmentType.FAKE,
        ],
        "FB": [
            AssignmentType.RUN_BLOCK,
            AssignmentType.PASS_BLOCK,
            AssignmentType.LEAD_BLOCK,
            AssignmentType.ROUTE,
        ],
        "WR": [
            AssignmentType.ROUTE,
            AssignmentType.RUN_BLOCK,  # Crack blocks, stalk blocks, etc.
        ],
        "TE": [
            AssignmentType.RUN_BLOCK,
            AssignmentType.PASS_BLOCK,
            AssignmentType.ROUTE,
        ],
        "OL": [  # All offensive line positions
            AssignmentType.RUN_BLOCK,
            AssignmentType.PASS_BLOCK,
        ],
    }

    DEFENSIVE_ASSIGNMENTS = {
        "DL": [
            AssignmentType.RUSH,
            AssignmentType.RUN_FIT,
            AssignmentType.SPY,
        ],
        "LB": [
            AssignmentType.RUSH,
            AssignmentType.COVERAGE,
            AssignmentType.RUN_FIT,
            AssignmentType.BLITZ,
            AssignmentType.SPY,
        ],
        "CB": [
            AssignmentType.COVERAGE,
            AssignmentType.BLITZ,  # Corner blitz
            AssignmentType.RUN_FIT,  # Run support
        ],
        "S": [
            AssignmentType.COVERAGE,
            AssignmentType.RUN_FIT,
            AssignmentType.BLITZ,
            AssignmentType.SPY,
        ],
        "NB": [  # Nickel back
            AssignmentType.COVERAGE,
            AssignmentType.BLITZ,
            AssignmentType.RUN_FIT,
        ],
    }

    @classmethod
    def get_available_assignments(
        cls, position: str, is_offense: bool = True
    ) -> List[AssignmentType]:
        """Get available assignments for a specific position."""
        if is_offense:
            # Handle specific OL positions
            if position in ["LT", "LG", "C", "RG", "RT"]:
                return cls.OFFENSIVE_ASSIGNMENTS["OL"]
            # Handle numbered WR positions (WR1, WR2, WR3)
            elif position.startswith("WR"):
                return cls.OFFENSIVE_ASSIGNMENTS["WR"]
            # Handle numbered RB positions (RB1, RB2)
            elif position.startswith("RB"):
                return cls.OFFENSIVE_ASSIGNMENTS["RB"]
            return cls.OFFENSIVE_ASSIGNMENTS.get(position, [])
        else:
            # Handle specific DL positions
            if position in ["DE1", "DE2", "DT1", "DT2", "NT"]:
                return cls.DEFENSIVE_ASSIGNMENTS["DL"]
            # Handle numbered positions
            elif position.startswith("DE") or position.startswith("DT"):
                return cls.DEFENSIVE_ASSIGNMENTS["DL"]
            elif position.startswith("LB") or position in [
                "MLB",
                "OLB1",
                "OLB2",
                "WILL",
                "MIKE",
                "SAM",
            ]:
                return cls.DEFENSIVE_ASSIGNMENTS["LB"]
            elif position.startswith("CB"):
                return cls.DEFENSIVE_ASSIGNMENTS["CB"]
            elif position in ["FS", "SS"] or position.startswith("S"):
                return cls.DEFENSIVE_ASSIGNMENTS["S"]
            return cls.DEFENSIVE_ASSIGNMENTS.get(position, [])


@dataclass
class FootballPlay:
    """
    Complete football play definition built on formation foundation.

    A play inherits a base formation and then applies dynamic modifications:
    1. Pre-snap shifts and adjustments
    2. Motion (with defensive reactions)
    3. Assignment of specific responsibilities to each player
    """

    name: str
    label: str
    base_formation: str  # Name of formation to inherit from
    personnel: List[str]  # Expected personnel groupings (inherited from formation)

    # Play categorization
    play_type: str  # "run", "pass", "special"
    tags: List[str] = field(default_factory=list)

    # Pre-snap modifications
    pre_snap_shifts: List[PreSnapShift] = field(default_factory=list)
    motion: Optional[PlayerMotion] = None
    defensive_reactions: List[DefensiveMotionReaction] = field(default_factory=list)

    # Player assignments
    assignments: List[PlayerAssignment] = field(default_factory=list)

    # Play execution details
    snap_count: Optional[str] = None  # "on one", "on two", etc.
    audible_options: List[str] = field(default_factory=list)

    def validate_assignments(self) -> List[str]:
        """Validate that all assignments are legal for their positions."""
        violations = []

        for assignment in self.assignments:
            position = assignment.player_position
            assignment_type = assignment.assignment_type

            # Determine if this is offense or defense based on position
            offensive_positions = [
                "QB",
                "RB",
                "FB",
                "WR",
                "TE",
                "LT",
                "LG",
                "C",
                "RG",
                "RT",
            ]
            is_offense = (
                position in offensive_positions
                or any(
                    position.startswith(pos) for pos in ["QB", "RB", "FB", "WR", "TE"]
                )
                or position in ["LT", "LG", "C", "RG", "RT"]
            )

            available = PositionAssignmentCatalog.get_available_assignments(
                position, is_offense
            )
            if assignment_type not in available:
                violations.append(
                    f"{position} cannot perform {assignment_type.value} assignment"
                )

        return violations

    def get_formation_modifications(self) -> Dict[str, Dict[str, str]]:
        """
        Calculate final player positions after all pre-snap modifications.

        Returns:
            Dictionary mapping player positions to their final lane/depth/alignment
        """
        modifications = {}

        # Apply pre-snap shifts in order
        for shift in sorted(self.pre_snap_shifts, key=lambda x: x.timing):
            player_mods = self._build_player_mods(
                lane=shift.target_lane,
                depth=shift.target_depth,
                alignment=shift.target_alignment,
            )
            if player_mods:
                modifications[shift.player_position] = player_mods

        # Apply motion end position if applicable
        if self.motion:
            motion_mods = self._build_player_mods(
                lane=self.motion.end_lane,
                depth=self.motion.end_depth,
                alignment=self.motion.end_alignment,
            )
            if motion_mods:
                modifications[self.motion.player_position] = motion_mods

        return modifications

    def _build_player_mods(
        self, lane: Optional[str], depth: Optional[str], alignment: Optional[str]
    ) -> Dict[str, str]:
        """Helper to build player modifications dictionary."""
        mods = {}
        if lane:
            mods["lane"] = lane
        if depth:
            mods["depth"] = depth
        if alignment:
            mods["alignment"] = alignment
        return mods

    def requires_defensive_formation(self) -> bool:
        """Check if this play requires a specific defensive formation."""
        return bool(self.defensive_reactions)


class PlayExecutor:
    """Executes plays by applying them to formations."""

    def __init__(self):
        self.formation_loader = None  # Will be set when needed

    def execute_play(
        self,
        play: FootballPlay,
        base_formation: FootballFormation,
        defensive_formation: Optional[FootballFormation] = None,
    ) -> Dict[str, Any]:
        """
        Execute a play by applying all modifications to the base formation.

        Args:
            play: The play to execute
            base_formation: Base offensive formation
            defensive_formation: Optional defensive formation for reactions

        Returns:
            Dictionary with execution results and final player positions
        """
        execution_result = {
            "play_name": play.name,
            "base_formation": base_formation.name,
            "final_positions": {},
            "motion_path": None,
            "defensive_reactions": [],
            "violations": [],
        }

        # Validate assignments
        violations = play.validate_assignments()
        execution_result["violations"] = violations

        if violations:
            return execution_result

        # Start with base formation positions
        current_positions = {}
        for position_id, role in base_formation.roles.items():
            current_positions[position_id] = role.coordinate

        # Apply pre-snap shifts
        modifications = play.get_formation_modifications()
        current_positions.update(modifications)

        # Handle motion
        if play.motion:
            execution_result["motion_path"] = {
                "player": play.motion.player_position,
                "type": play.motion.motion_type,
                "start_lane": play.motion.start_lane,
                "start_depth": play.motion.start_depth,
                "end_lane": play.motion.end_lane,
                "end_depth": play.motion.end_depth,
                "end_alignment": play.motion.end_alignment,
                "speed": play.motion.speed,
            }

            # Apply defensive reactions to motion
            if defensive_formation:
                for reaction in play.defensive_reactions:
                    execution_result["defensive_reactions"].append(
                        {
                            "defensive_player": reaction.defensive_position,
                            "reaction": reaction.reaction_type.value,
                            "target": reaction.target_player,
                        }
                    )

        execution_result["final_positions"] = current_positions
        return execution_result


# Route patterns for receivers (common assignment details)
class RoutePattern(Enum):
    """Standard route patterns for receivers."""

    SLANT = "slant"
    HITCH = "hitch"
    OUT = "out"
    IN = "in"
    GO = "go"
    POST = "post"
    CORNER = "corner"
    COMEBACK = "comeback"
    CURL = "curl"
    DIG = "dig"
    DRAG = "drag"
    SCREEN = "screen"


# Blocking schemes for linemen
class BlockingScheme(Enum):
    """Standard blocking schemes."""

    ZONE = "zone"
    GAP = "gap"
    POWER = "power"
    REACH = "reach"
    BACK = "back"
    SLIDE = "slide"
    COMBO = "combo"
    DOUBLE = "double"
