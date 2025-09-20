"""
Core game board concepts for sports simulations.

Provides a coordinate system and positioning framework that can be used
across different sports while maintaining realistic constraints.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Protocol
from enum import Enum


@dataclass(frozen=True)
class Coordinate:
    """A position on the game board using x,y coordinates."""

    x: int
    y: int

    def distance_to(self, other: Coordinate) -> float:
        """Calculate distance between two coordinates."""
        return ((self.x - other.x) ** 2 + (self.y - other.y) ** 2) ** 0.5


class Lane(Enum):
    """Horizontal positioning on the field."""

    LEFT = "left"
    MIDDLE = "middle"
    RIGHT = "right"


class GameBoard(Protocol):
    """Protocol defining the interface for a game board."""

    @property
    def width(self) -> int:
        """Width of the playing field."""
        ...

    @property
    def height(self) -> int:
        """Height of the playing field."""
        ...

    def is_valid_position(self, coord: Coordinate) -> bool:
        """Check if a coordinate is within the valid playing area."""
        ...

    def get_lane_center(self, lane: Lane, y_position: int) -> Coordinate:
        """Get the center coordinate for a given lane at a y-position."""
        ...


@dataclass
class FieldDimensions:
    """Defines the dimensions and key positions of a playing field."""

    width: int
    height: int
    line_of_scrimmage: int  # Y coordinate where play starts

    def __post_init__(self):
        if self.line_of_scrimmage >= self.height:
            raise ValueError("Line of scrimmage must be within field bounds")


class StandardGameBoard:
    """A standard rectangular game board implementation."""

    def __init__(self, dimensions: FieldDimensions):
        self.dimensions = dimensions

    @property
    def width(self) -> int:
        return self.dimensions.width

    @property
    def height(self) -> int:
        return self.dimensions.height

    def is_valid_position(self, coord: Coordinate) -> bool:
        """Check if coordinate is within field bounds."""
        return 0 <= coord.x < self.width and 0 <= coord.y < self.height

    def get_lane_center(self, lane: Lane, y_position: int) -> Coordinate:
        """Get center coordinate for a lane at given y-position."""
        lane_positions = {
            Lane.LEFT: self.width // 4,
            Lane.MIDDLE: self.width // 2,
            Lane.RIGHT: (3 * self.width) // 4,
        }
        return Coordinate(lane_positions[lane], y_position)
