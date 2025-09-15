# src/football/mapper.py
from .schemas import (
    PlayLogicalFramesDTO,
    PlayFramesDTO,
    Team,
    PlayerFrame,
    FormationSpecDTO,
)
from .config import get_placement_maps

DEFAULT_LANE_X = {"left": 2, "middle": 5, "right": 8}
DEFAULT_DEPTH_Y_OFFENSE = {"line": 12, "backfield": 14, "wide": 12}
DEFAULT_DEPTH_Y_DEFENSE = {"line": 8, "box": 6, "deep": 4, "wide": 12, "backfield": 14}


def _base_xy(
    team: Team, pos: str, lane: str, depth: str, maps, cols: int, rows: int
) -> tuple[int, int]:
    lane_x = maps.get("lane_x") or {}
    off = maps.get("depth_offense") or {}
    deff = maps.get("depth_defense") or {}
    x = lane_x.get(lane, DEFAULT_LANE_X.get(lane, 5))
    ymap = off if team == "offense" else deff
    y = ymap.get(
        depth,
        (DEFAULT_DEPTH_Y_OFFENSE if team == "offense" else DEFAULT_DEPTH_Y_DEFENSE).get(
            depth, 10
        ),
    )
    x = max(0, min(cols - 1, x))
    y = max(0, min(rows - 1, y))
    return x, y


def _apply_placement(
    x: int, y: int, role_name: str, formation: FormationSpecDTO, cols: int, rows: int
) -> tuple[int, int]:
    p = formation.placement.get(role_name)
    if not p:
        return x, y
    if p.x is not None:
        x = p.x
    if p.y is not None:
        y = p.y
    x += p.dx
    y += p.dy
    return max(0, min(cols - 1, x)), max(0, min(rows - 1, y))


def render_frames(
    team: Team,
    formation: FormationSpecDTO,
    logical: PlayLogicalFramesDTO,
    cols: int = 20,
    rows: int = 20,
    force_reload_config: bool = False,
) -> PlayFramesDTO:
    maps = get_placement_maps(force_reload=force_reload_config)
    out_frames: list[list[PlayerFrame]] = []
    for frame in logical.frames:
        rendered: list[PlayerFrame] = []
        for p in frame:
            x, y = _base_xy(p.team, p.pos, p.lane, p.depth, maps, cols, rows)
            # apply per-formation placement for display
            x, y = _apply_placement(x, y, p.id, formation, cols, rows)
            rendered.append(PlayerFrame(id=p.id, team=p.team, pos=p.pos, x=x, y=y))
        out_frames.append(rendered)
    return PlayFramesDTO(name=logical.name, frames=out_frames)
