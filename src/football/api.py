from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


from .schemas import PlayDTO, PlayInfoDTO
from .engine import demo_domain_play, to_play_dto

app = FastAPI(title="Techno Bowl API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/plays", response_model=list[PlayInfoDTO])
def list_plays() -> list[PlayInfoDTO]:
    play_dto = to_play_dto(demo_domain_play())
    return [PlayInfoDTO(name=play_dto.name, frames=len(play_dto.frames))]


@app.get("/api/plays/current", response_model=PlayDTO)
def get_current_play() -> PlayDTO:
    return to_play_dto(demo_domain_play())
