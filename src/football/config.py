from __future__ import annotations
from pathlib import Path
from typing import Any, Dict, Tuple
import os, yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = Path(os.environ.get("TB_DATA_DIR", str(REPO_ROOT / "data")))
_PL_PATH = DATA_DIR / "config" / "placement.yaml"

_cache: Dict[str, Any] = {"mtime": None, "maps": None}

def get_placement_maps(force_reload: bool = False) -> Dict[str, Any]:
    """
    Returns a dict with:
      lane_x, depth_offense, depth_defense, by_role, by_pos
    Hot-reloads when the YAML mtime changes, or when force_reload=True.
    """

    combos_off: Dict[str, Any] = {}
    combos_def: Dict[str, Any] = {}

    mtime = _PL_PATH.stat().st_mtime if _PL_PATH.exists() else None
    if not force_reload and _cache["maps"] is not None and _cache["mtime"] == mtime:
        return _cache["maps"]

    lane_x: Dict[str, int] = {}
    depth_offense: Dict[str, int] = {}
    depth_defense: Dict[str, int] = {}
    by_role: Dict[str, Dict[str, int]] = {}
    by_pos: Dict[str, Any] = {}

    if _PL_PATH.exists():
        with _PL_PATH.open("r", encoding="utf-8") as f:
            doc = yaml.safe_load(f) or {}
        lane_x = dict(doc.get("lanes") or {})
        depths = doc.get("depths") or {}
        depth_offense = dict(depths.get("offense") or {})
        depth_defense = dict(depths.get("defense") or {})
        overrides = doc.get("overrides") or {}
        by_role = dict(overrides.get("by_role") or {})
        by_pos = dict(overrides.get("by_pos") or {})
        combos = doc.get("combos") or {}
        combos_off = dict(combos.get("offense") or {})
        combos_def = dict(combos.get("defense") or {})

    _cache["mtime"] = mtime
    _cache["maps"] = {
        "lane_x": lane_x,
        "depth_offense": depth_offense,
        "depth_defense": depth_defense,
        "by_role": by_role,
        "by_pos": by_pos,
        "combos_offense": combos_off,
        "combos_defense": combos_def,
    }
    return _cache["maps"]
