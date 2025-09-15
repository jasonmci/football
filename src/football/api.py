from __future__ import annotations

from typing import Literal, List
from fastapi import FastAPI, HTTPException, Path
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse

from src.football.resolver import build_logical_presnap_frames

from .schemas import FormationSpecDTO, PlayFramesDTO, PlayLogicalFramesDTO, PlaySpecDTO
from .repository import list_items, load_formation, load_play

from .resolver import build_logical_presnap_frames
from .mapper import render_frames

TeamParam = Literal["offense", "defense"]

app = FastAPI(title="Techno Bowl API", version="0.2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


# ---------- lists ----------


@app.get("/api/{team}/formations", response_model=List[str])
def get_formations(team: TeamParam = Path(...)) -> List[str]:
    return list_items("formations", team)  # list of names (file stems)


@app.get("/api/{team}/plays", response_model=List[str])
def get_plays(team: TeamParam = Path(...)) -> List[str]:
    return list_items("plays", team)


# ---------- items ----------


# details (your new paths)
@app.get("/api/{team}/formations/{name}", response_model=FormationSpecDTO)
def get_formation(team: TeamParam, name: str) -> FormationSpecDTO:
    try:
        return load_formation(team, name)
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e)) from e


@app.get("/api/{team}/plays/{name}", response_model=PlaySpecDTO)
def get_play(team: TeamParam, name: str) -> PlaySpecDTO:
    try:
        return load_play(team, name)
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e)) from e


@app.get("/api/{team}/plays/{name}/frames.logical", response_model=PlayLogicalFramesDTO)
def get_frames_logical(team: TeamParam, name: str):
    try:
        play = get_play(team, name)
        formation = get_formation(team, play.formation)
        return build_logical_presnap_frames(team, formation, play)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))


@app.get("/api/{team}/plays/{name}/frames", response_model=PlayFramesDTO)
def get_frames(
    team: TeamParam, name: str, cols: int = 20, rows: int = 20, reload: bool = False
):
    try:
        play = get_play(team, name)
        formation = get_formation(team, play.formation)
        logical = build_logical_presnap_frames(team, formation, play)
        return render_frames(
            team, formation, logical, cols=cols, rows=rows, force_reload_config=reload
        )
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))


# add frames.txt
@app.get("/api/{team}/plays/{name}/frames.txt", response_class=PlainTextResponse)
def get_frames_text(
    team: TeamParam, name: str, cols: int = 20, rows: int = 20, reload: bool = False
):
    try:
        play = get_play(team, name)
        formation = get_formation(team, play.formation)
        logical = build_logical_presnap_frames(team, formation, play)
        frames_dto = render_frames(
            team, formation, logical, cols=cols, rows=rows, force_reload_config=reload
        )

        lines: List[str] = []
        for fnum, frame in enumerate(frames_dto.frames):
            lines.append(f"Frame {fnum}:")
            grid = [["." for _ in range(cols)] for _ in range(rows)]
            for p in frame:
                grid[p.y][p.x] = p.id[0].upper()  # first letter of role
            for row in grid:
                lines.append("".join(row))
            lines.append("")  # blank line between frames
        return "\n".join(lines)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
