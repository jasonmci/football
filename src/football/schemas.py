from __future__ import annotations
from typing import Dict, List, Literal, Optional, Union, Annotated
from pydantic import BaseModel, Field

Team = Literal["offense", "defense"]
Lane = Literal["left", "middle", "right"]
Align = Literal["outside", "slot", "tight"]  # 'wide' → alias → 'outside'

OffenseDepth = Literal["under_center", "line", "wing", "backfield", "pistol", "shotgun"]
DefenseDepth = Literal["line", "box", "overhang", "deep"]
Depth = Union[OffenseDepth, DefenseDepth]

Position = Literal[
    "QB", "RB", "FB", "WR", "TE", "C", "RG", "LG", "RT", "LT", "DL", "LB", "CB", "S"
]  # extend if you add more later


class RoleSpec(BaseModel):
    pos: str
    lane: Lane
    depth: Depth  # OffenseDepth | DefenseDepth (as you set earlier)
    align: Optional[Align] = None


# NEW: per-role placement overrides for a formation (x/y absolute; dx/dy offsets)
class PlacementSpec(BaseModel):
    x: Optional[int] = None
    y: Optional[int] = None
    dx: int = 0
    dy: int = 0


class FormationSpecDTO(BaseModel):
    name: str
    label: Optional[str] = None
    team: Team
    allowed_personnel: List[str] = Field(default_factory=list)
    roles: Dict[str, RoleSpec] = Field(default_factory=dict)
    placement: Dict[str, PlacementSpec] = Field(default_factory=dict)
    aliases: Dict[str, str] = Field(default_factory=dict)  # optional, for RB→RB1 etc.


class RoleChange(BaseModel):
    lane: Optional[Lane] = None
    depth: Optional[Depth] = None
    align: Optional[Align] = None  # NEW


# (unchanged) If you already have PlaySpecDTO etc. keep them:
class ShiftSegment(BaseModel):
    offense: Dict[str, List[int]] = Field(default_factory=dict)
    defense: Dict[str, List[int]] = Field(default_factory=dict)


# Shifts: instantaneous “re-spotting” before motion


# NEW: event-based pre-snap
class PreSnapEvent(BaseModel):
    player: str
    type: Literal["shift"]
    to: RoleChange


# Motions: animated pre-snap movement along lane/depth waypoints
class Waypoint(BaseModel):
    lane: Lane
    depth: Depth
    align: Optional[Align] = None  # NEW (optional)


class MotionSpec(BaseModel):
    player: str  # role name
    path: List[Waypoint]  # lane/depth waypoints
    speed: int = 1  # tiles/frame (used by resolver later)
    delay: int = 0  # frames to wait before starting (optional)


# Concrete output frames
class PlayerFrame(BaseModel):
    id: str
    team: Team
    pos: str
    x: int
    y: int


class PlayFramesDTO(BaseModel):
    name: str
    frames: List[List[PlayerFrame]]


# Play spec (pre-snap only now)
class PlaySpecDTO(BaseModel):
    name: str
    team: Team
    formation: str
    pre_snap: List[PreSnapEvent] = Field(default_factory=list)
    motion: Optional[MotionSpec] = None  # single offense motion (or None for no motion)


class RouteAssignment(BaseModel):
    kind: Literal["route"]
    path: List[Waypoint]
    speed: int = 1


class BlockAssignment(BaseModel):
    kind: Literal["block"]
    technique: Optional[str] = None  # e.g., "zone", "screen", "reach"
    target: Optional[str] = None  # optional role hint (e.g., "CB_right")


class ManAssignment(BaseModel):
    kind: Literal["man"]
    target_role: str


class ZoneAssignment(BaseModel):
    kind: Literal["zone"]
    lane: Lane
    depth: Depth
    radius: int = 1  # abstract “area” size


Assignment = Annotated[
    Union[RouteAssignment, BlockAssignment, ManAssignment, ZoneAssignment],
    Field(discriminator="kind"),
]


# src/football/schemas.py
class LogicalPlayerFrame(BaseModel):
    id: str
    team: Team
    pos: str
    lane: Lane
    depth: Depth
    align: Optional[Align] = None


class PlayLogicalFramesDTO(BaseModel):
    name: str
    frames: List[List[LogicalPlayerFrame]]
