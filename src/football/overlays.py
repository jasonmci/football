from typing import Tuple
from .models import DefFormation, Lane

def overlay_base(f: DefFormation, **kwargs) -> dict:
    # no changes to f
    return {"call": "base"}

def overlay_run_commit(f: DefFormation) -> dict:
    moved = 0
    for lane in ("left","right","middle"):
        if moved >= 2: break
        if f.get(lane,"deep") > 0:
            f.move(lane, "deep", "box", 1)
            moved += 1
    return {"call":"run_commit"}

def overlay_blitz(f: DefFormation, lanes: Tuple[Lane,...]=("left","middle")) -> dict:
    for ln in lanes:
        if f.get(ln,"box") > 0:
            f.move(ln, "box", "line", 1)
    return {"call":"blitz","lanes":lanes}

def overlay_short_shell(f: DefFormation) -> dict:
    total_deep = sum(f.get(ln,"deep") for ln in ("left","middle","right"))
    if total_deep > 1:
        for ln in ("middle","left","right"):
            if f.get(ln,"deep") > 0:
                f.move(ln, "deep", "box", 1)
                break
    return {"call":"short_shell"}

def overlay_deep_shell(f: DefFormation) -> dict:
    for ln in ("left","right","middle"):
        if f.get(ln,"box") > 0:
            f.move(ln, "box", "deep", 1)
            break
    return {"call":"deep_shell"}

OVERLAY_MAP = {
    "base": overlay_base,
    "run_commit": overlay_run_commit,
    "blitz": overlay_blitz,
    "short_shell": overlay_short_shell,
    "deep_shell": overlay_deep_shell,
}
