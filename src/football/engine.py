# src/football/engine.py
from typing import List, cast

# your real domain models:
# from .models import DomainPlay, DomainPlayer
from .schemas import Team, PlayDTO, PlayerDTO


# Example stub domain types (delete these when using real ones)
class DomainPlayer:
    def __init__(self, id: str, team: Team, role: str, x: int, y: int):
        self.id = id
        self.team = team  # "offense" | "defense"
        self.role = role
        self.x = x
        self.y = y


class DomainPlay:
    def __init__(self, name: str, frames: List[List[DomainPlayer]]):
        self.name = name
        self.frames = frames


def to_player_dto(p: DomainPlayer) -> PlayerDTO:
    return PlayerDTO(
        id=p.id,
        team=cast(Team, p.team),  # enforce Team only here
        role=p.role,
        x=p.x,
        y=p.y,
    )


def to_play_dto(play: "DomainPlay") -> PlayDTO:
    return PlayDTO(
        name=play.name,
        frames=[[to_player_dto(p) for p in frame] for frame in play.frames],
    )


# --- Demo generator (replace with your real engine output) ---
def demo_domain_play() -> DomainPlay:
    frames: List[List[DomainPlayer]] = []
    frames.append(
        [
            DomainPlayer("QB", "offense", "QB", 4, 18),
            DomainPlayer("WR1", "offense", "WR", 1, 15),
            DomainPlayer("WR2", "offense", "WR", 2, 15),
            DomainPlayer("RB", "offense", "RB", 4, 19),
            DomainPlayer("CB1", "defense", "CB", 1, 13),
            DomainPlayer("LB", "defense", "LB", 4, 13),
        ]
    )
    frames.append(
        [
            DomainPlayer("QB", "offense", "QB", 4, 18),
            DomainPlayer("WR1", "offense", "WR", 2, 16),
            DomainPlayer("WR2", "offense", "WR", 3, 15),
            DomainPlayer("RB", "offense", "RB", 4, 19),
            DomainPlayer("CB1", "defense", "CB", 1, 13),
            DomainPlayer("LB", "defense", "LB", 4, 13),
        ]
    )
    frames.append(
        [
            DomainPlayer("QB", "offense", "QB", 4, 18),
            DomainPlayer("WR1", "offense", "WR", 3, 15),
            DomainPlayer("WR2", "offense", "WR", 4, 15),
            DomainPlayer("RB", "offense", "RB", 4, 19),
            DomainPlayer("CB1", "defense", "CB", 1, 13),
            DomainPlayer("LB", "defense", "LB", 4, 13),
        ]
    )
    return DomainPlay("Trips Right (demo)", frames)
