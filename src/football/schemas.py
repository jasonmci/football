# src/football/schemas.py
from pydantic import BaseModel, Field
from typing import Literal, List

Team = Literal["offense", "defense"]


class PlayerDTO(BaseModel):
    id: str
    team: Team
    role: str
    x: int
    y: int


class PlayDTO(BaseModel):
    name: str
    frames: List[List[PlayerDTO]] = Field(default_factory=list)


class PlayInfoDTO(BaseModel):
    name: str
    frames: int
