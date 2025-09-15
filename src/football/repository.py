from __future__ import annotations

import os
from pathlib import Path
from typing import List, Dict, Any, Literal
import yaml

from .schemas import (
    PreSnapEvent,
    RoleChange,
    Team,
    PlaySpecDTO,
    MotionSpec,
    FormationSpecDTO,
    RoleSpec,
    Waypoint,
    PlacementSpec,
)

# Point to repo root / data, not src/data
REPO_ROOT = Path(__file__).resolve().parents[2]  # .../football
DATA_DIR = Path(os.environ.get("TB_DATA_DIR", str(REPO_ROOT / "data")))
WIDE_ALIASES = {"wide", "outside"}

FormOrPlay = Literal["formations", "plays"]


def _dir_for(kind: FormOrPlay, team: Team) -> Path:
    return DATA_DIR / kind / team


def _safe_stem(name: str) -> str:
    # very simple safeguard; you can expand to stricter slug validation if needed
    return name.replace("/", "").replace("\\", "").strip()


def list_items(kind: FormOrPlay, team: Team) -> List[str]:
    root = _dir_for(kind, team)
    if not root.exists():
        return []
    return sorted(p.stem for p in root.glob("*.yaml"))


def _load_yaml(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def _norm_align_from_depth_if_needed(
    pos: str, depth: str | None, align: str | None
) -> tuple[str | None, str | None]:
    if depth is None:
        return None, align
    d = depth.lower()
    if d in WIDE_ALIASES:
        # WR/TE on LOS; backs off the ball
        return ("line" if pos in {"WR", "TE"} else "backfield"), (align or "outside")
    if d == "slot":
        return ("line" if pos in {"WR", "TE"} else "backfield"), (align or "slot")
    if d == "tight":
        return "line", (align or "tight")
    return depth, align


def load_formation(team: Team, name: str) -> FormationSpecDTO:

    path = _dir_for("formations", team) / f"{name}.yaml"
    if not path.exists():
        path = _dir_for("formations", team) / f"{name}.yml"
    if not path.exists():
        raise FileNotFoundError(f"Formation not found: {team}/{name}")

    doc = _load_yaml(path)

    aliases_raw = doc.get("aliases", {}) or {}
    if not isinstance(aliases_raw, dict):
        raise ValueError(
            f"Formation {team}/{name}: 'aliases' must be a mapping of alias->role"
        )
    aliases = {str(k): str(v) for k, v in aliases_raw.items()}

    roles_raw = doc.get("roles")
    if not isinstance(roles_raw, dict) or not roles_raw:
        raise ValueError(
            f"Formation {team}/{name}: 'roles' must be a non-empty mapping"
        )

    roles: Dict[str, RoleSpec] = {}
    for rname, r in roles_raw.items():
        roles[str(rname)] = RoleSpec(
            pos=r["pos"], lane=r["lane"], depth=r["depth"], align=r.get("align")
        )

    # NEW: optional per-role placement
    placement_raw = doc.get("placement", {})
    placement: Dict[str, PlacementSpec] = {}
    if placement_raw is not None:
        if not isinstance(placement_raw, dict):
            raise ValueError(
                f"Formation {team}/{name}: 'placement' must be a mapping of role -> { '{x?, y?, dx?, dy?}' }"
            )
        for role_name, p in placement_raw.items():
            if role_name not in roles:
                raise ValueError(
                    f"Formation {team}/{name}: placement refers to unknown role '{role_name}'"
                )
            if p is None:
                placement[role_name] = PlacementSpec()  # empty = no override
            elif isinstance(p, dict):
                placement[role_name] = PlacementSpec(
                    x=p.get("x"),
                    y=p.get("y"),
                    dx=int(p.get("dx", 0)),
                    dy=int(p.get("dy", 0)),
                )
            else:
                raise ValueError(
                    f"Formation {team}/{name}: placement for '{role_name}' must be a mapping"
                )

    return FormationSpecDTO(
        name=str(doc.get("name", name)),
        label=doc.get("label"),
        team=team,
        allowed_personnel=[str(p) for p in (doc.get("allowed_personnel") or [])],
        roles=roles,
        placement=placement,
        aliases=aliases,
    )


# -------- helpers for play parsing --------
def _parse_pre_snap(doc: Dict[str, Any]) -> List[PreSnapEvent]:
    raw = doc.get("pre_snap", [])
    # allow single mapping or list
    if isinstance(raw, dict):
        raw = [raw]
    if not isinstance(raw, list):
        raise ValueError("pre_snap must be a list (or single mapping) of events")

    out: List[PreSnapEvent] = []
    for idx, evt in enumerate(raw):
        if not isinstance(evt, dict):
            raise ValueError(f"pre_snap[{idx}] must be a mapping")
        missing = [k for k in ("player", "type", "to") if k not in evt]
        if missing:
            raise ValueError(f"pre_snap[{idx}] missing: {', '.join(missing)}")
        if str(evt["type"]).lower() != "shift":
            raise ValueError(f"pre_snap[{idx}].type must be 'shift' for now")
        to = evt["to"]
        if not isinstance(to, dict) or "lane" not in to or "depth" not in to:
            raise ValueError(f"pre_snap[{idx}].to must include lane+depth")
        out.append(
            PreSnapEvent(
                player=str(evt["player"]),
                type="shift",
                to=RoleChange(lane=to["lane"], depth=to["depth"]),
            )
        )
    return out


def _norm_align_from_depth_if_needed(
    pos: str, depth: str | None, align: str | None
) -> tuple[str | None, str | None]:
    if depth is None:
        return None, align
    d = depth.lower()
    if d in WIDE_ALIASES:
        # WR/TE on LOS; backs off the ball
        return ("line" if pos in {"WR", "TE"} else "backfield"), (align or "outside")
    if d == "slot":
        return ("line" if pos in {"WR", "TE"} else "backfield"), (align or "slot")
    if d == "tight":
        return "line", (align or "tight")
    return depth, align


def _role_change_map(raw: Any) -> Dict[str, RoleChange]:
    if raw is None:
        return {}
    if not isinstance(raw, dict):
        raise ValueError("shift team map must be a mapping of role -> {lane, depth}")
    out: Dict[str, RoleChange] = {}
    for role, v in raw.items():
        if not isinstance(v, dict) or "lane" not in v or "depth" not in v:
            raise ValueError(f"shift for '{role}' must include lane+depth")
        out[str(role)] = RoleChange(lane=v["lane"], depth=v["depth"])
    return out


def _waypoints(raw_list: Any) -> List[Waypoint]:
    if not isinstance(raw_list, list) or not raw_list:
        raise ValueError("motion.path must be a non-empty list of {lane, depth}")
    wps: List[Waypoint] = []
    for i, w in enumerate(raw_list):
        if not isinstance(w, dict) or "lane" not in w or "depth" not in w:
            raise ValueError(f"motion.path[{i}] must be an object with lane+depth")
        wps.append(Waypoint(lane=w["lane"], depth=w["depth"]))
    return wps


# --- plays (with shifts, motions, assignments) ---


def load_play(team: Team, name: str) -> PlaySpecDTO:
    path = _dir_for("plays", team) / f"{name}.yaml"
    if not path.exists():
        path = _dir_for("plays", team) / f"{name}.yml"
    if not path.exists():
        raise FileNotFoundError(f"Play not found: {team}/{name}")
    doc = _load_yaml(path)

    if "shift" in doc or "shifts" in doc:
        raise ValueError("Use 'pre_snap' (event list); 'shift(s)' is not supported.")
    if "motions" in doc:
        raise ValueError("Use single 'motion' object; 'motions' is not supported.")

    formation = doc.get("formation")
    if not formation:
        raise ValueError(f"Play {team}/{name}: 'formation' is required")

    pre_snap = _parse_pre_snap(doc)

    motion_obj = doc.get("motion")
    motion: MotionSpec | None = None
    if motion_obj is not None:
        if not isinstance(motion_obj, dict):
            raise ValueError(
                "motion must be an object with keys: player, path[, speed, delay]"
            )
        if "id" in motion_obj and "player" not in motion_obj:
            raise ValueError("motion.id is deprecated; use 'player'")
        missing = [k for k in ("player", "path") if k not in motion_obj]
        if missing:
            raise ValueError(f"motion missing required field(s): {', '.join(missing)}")
        motion = MotionSpec(
            player=str(motion_obj["player"]),
            path=_waypoints(motion_obj["path"]),
            speed=int(motion_obj.get("speed", 1)),
            delay=int(motion_obj.get("delay", 0)),
        )

    return PlaySpecDTO(
        name=str(doc.get("name", name)),
        team=team,
        formation=str(formation),
        pre_snap=pre_snap,
        motion=motion,
    )
