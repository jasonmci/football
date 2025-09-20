"""
Football-specific positions and formations.

Implements the core player positioning system for American football,
including realistic constraints and validation rules.
"""

from __future__ import annotations
from typing import Set, Tuple, Dict, List
from enum import Enum

from core.players import Position, Formation, PlayerRole, PositionConstraints
from core.game_board import Lane, FieldDimensions, StandardGameBoard


class FootballDepth(Enum):
    """Football-specific depth alignments (distance from line of scrimmage)."""

    LINE = "line"  # At line of scrimmage
    BACKFIELD = "backfield"  # Behind the line (RBs, some TEs)
    SHOTGUN = "shotgun"  # QB in shotgun formation
    PISTOL = "pistol"  # QB in pistol formation
    UNDER_CENTER = "under_center"  # QB under center

    # Defensive depths
    BOX = "box"  # Linebacker level (5-8 yards)
    DEEP = "deep"  # Secondary level (10+ yards)


class FootballAlignment(Enum):
    """Football-specific alignments within a depth level."""

    TIGHT = "tight"  # Close to formation (TE tight, OL together)
    SLOT = "slot"  # Between tight and outside (slot receiver)
    OUTSIDE = "outside"  # Split wide from formation
    WINGBACK = "wingback"  # Wingback position in backfield


class FootballPosition(Position):
    """Base class for football positions."""

    def __init__(self, name: str, allowed_alignments: Set[Tuple[Lane, str]]):
        self._name = name
        self._allowed_alignments = allowed_alignments

    @property
    def name(self) -> str:
        return self._name

    @property
    def allowed_alignments(self) -> Set[Tuple[Lane, str]]:
        return self._allowed_alignments


# Offensive Positions
class Quarterback(FootballPosition):
    def __init__(self):
        super().__init__(
            "QB",
            {
                (Lane.MIDDLE, FootballDepth.BACKFIELD.value),
                (Lane.MIDDLE, FootballDepth.SHOTGUN.value),
                (Lane.MIDDLE, FootballDepth.PISTOL.value),
                (Lane.MIDDLE, FootballDepth.UNDER_CENTER.value),
            },
        )


class RunningBack(FootballPosition):
    def __init__(self):
        super().__init__(
            "RB",
            {
                (Lane.LEFT, FootballDepth.BACKFIELD.value),
                (Lane.MIDDLE, FootballDepth.BACKFIELD.value),
                (Lane.RIGHT, FootballDepth.BACKFIELD.value),
            },
        )


class Fullback(FootballPosition):
    def __init__(self):
        super().__init__(
            "FB",
            {
                (Lane.LEFT, FootballDepth.BACKFIELD.value),
                (Lane.MIDDLE, FootballDepth.BACKFIELD.value),
                (Lane.RIGHT, FootballDepth.BACKFIELD.value),
            },
        )


class WideReceiver(FootballPosition):
    def __init__(self):
        super().__init__(
            "WR",
            {
                (Lane.LEFT, FootballDepth.LINE.value),  # Can be slot, outside, etc.
                (Lane.RIGHT, FootballDepth.LINE.value),  # Can be slot, outside, etc.
                (
                    Lane.MIDDLE,
                    FootballDepth.LINE.value,
                ),  # Rare but possible (trips formation)
                (Lane.LEFT, FootballDepth.BACKFIELD.value),  # Motion or special sets
                (Lane.RIGHT, FootballDepth.BACKFIELD.value),  # Motion or special sets
            },
        )


class TightEnd(FootballPosition):
    def __init__(self):
        super().__init__(
            "TE",
            {
                (Lane.LEFT, FootballDepth.LINE.value),  # Tight or flexed
                (Lane.RIGHT, FootballDepth.LINE.value),  # Tight or flexed
                (Lane.LEFT, FootballDepth.BACKFIELD.value),  # H-back/wingback
                (Lane.RIGHT, FootballDepth.BACKFIELD.value),  # H-back/wingback
            },
        )


class OffensiveLine(FootballPosition):
    def __init__(self):
        super().__init__(
            "OL",
            {
                (Lane.LEFT, FootballDepth.LINE.value),
                (Lane.MIDDLE, FootballDepth.LINE.value),
                (Lane.RIGHT, FootballDepth.LINE.value),
            },
        )


# Defensive Positions
class DefensiveLine(FootballPosition):
    def __init__(self):
        super().__init__(
            "DL",
            {
                (Lane.LEFT, FootballDepth.LINE.value),
                (Lane.MIDDLE, FootballDepth.LINE.value),
                (Lane.RIGHT, FootballDepth.LINE.value),
            },
        )


class Linebacker(FootballPosition):
    def __init__(self):
        super().__init__(
            "LB",
            {
                (Lane.LEFT, FootballDepth.BOX.value),
                (Lane.MIDDLE, FootballDepth.BOX.value),
                (Lane.RIGHT, FootballDepth.BOX.value),
            },
        )


class Cornerback(FootballPosition):
    def __init__(self):
        super().__init__(
            "CB",
            {
                (Lane.LEFT, FootballDepth.LINE.value),  # Press coverage
                (Lane.RIGHT, FootballDepth.LINE.value),  # Press coverage
                (Lane.LEFT, FootballDepth.BOX.value),  # Off coverage
                (Lane.RIGHT, FootballDepth.BOX.value),  # Off coverage
                (Lane.LEFT, FootballDepth.DEEP.value),  # Deep coverage
                (Lane.RIGHT, FootballDepth.DEEP.value),  # Deep coverage
            },
        )


class Nickelback(FootballPosition):
    def __init__(self):
        super().__init__(
            "NB",
            {
                # Nickelbacks are slot/middle coverage specialists
                (Lane.MIDDLE, FootballDepth.BOX.value),  # Slot coverage
                (Lane.MIDDLE, FootballDepth.DEEP.value),  # Deep middle
                (Lane.LEFT, FootballDepth.BOX.value),  # Left slot
                (Lane.RIGHT, FootballDepth.BOX.value),  # Right slot
            },
        )


class Safety(FootballPosition):
    def __init__(self):
        super().__init__(
            "S",
            {
                # Safeties can play deep (traditional FS/SS coverage)
                (Lane.LEFT, FootballDepth.DEEP.value),
                (Lane.MIDDLE, FootballDepth.DEEP.value),
                (Lane.RIGHT, FootballDepth.DEEP.value),
                # Safeties can also play in the box (strong safety, rover)
                (Lane.LEFT, FootballDepth.BOX.value),
                (Lane.MIDDLE, FootballDepth.BOX.value),
                (Lane.RIGHT, FootballDepth.BOX.value),
            },
        )


# Position Registry with common aliases
OFFENSIVE_POSITIONS = {
    "QB": Quarterback(),
    "RB": RunningBack(),
    "FB": Fullback(),
    "WR": WideReceiver(),
    "TE": TightEnd(),
    "OL": OffensiveLine(),
    # Specific offensive line positions (all use OL rules)
    "LT": OffensiveLine(),  # Left Tackle
    "LG": OffensiveLine(),  # Left Guard
    "C": OffensiveLine(),  # Center
    "RG": OffensiveLine(),  # Right Guard
    "RT": OffensiveLine(),  # Right Tackle
}

DEFENSIVE_POSITIONS = {
    "DL": DefensiveLine(),
    "LB": Linebacker(),
    "CB": Cornerback(),
    "NB": Nickelback(),
    "S": Safety(),
}

ALL_POSITIONS = {**OFFENSIVE_POSITIONS, **DEFENSIVE_POSITIONS}


class FootballFormation(Formation):
    """Football-specific formation with 11-player validation and personnel groupings."""

    def __init__(
        self,
        name: str,
        roles: Dict[str, PlayerRole],
        personnel: List[str] | None = None,
    ):
        self.personnel = personnel or []
        super().__init__(name, roles)

    @property
    def required_player_count(self) -> int:
        return 11

    def _validate_formation(self) -> None:
        """Validate football-specific formation rules."""
        if len(self.roles) != self.required_player_count:
            raise ValueError(
                f"Football formation '{self.name}' has {len(self.roles)} players, "
                f"expected {self.required_player_count}"
            )


def create_football_constraints() -> PositionConstraints:
    """Create realistic constraints for football formations."""
    constraints = PositionConstraints()

    # For now, let's keep constraints minimal to get the loader working
    # We can add more sophisticated constraints later

    # QBs shouldn't be too far from the formation
    # constraints.add_distance_constraint("QB", "OL", 1, 10)

    # We'll add more constraints as we refine the system

    return constraints


# Standard Football Field
FOOTBALL_FIELD = StandardGameBoard(
    FieldDimensions(
        width=20,  # Adjust based on your coordinate system
        height=30,  # Adjust based on your coordinate system
        line_of_scrimmage=15,  # Middle of field
    )
)
