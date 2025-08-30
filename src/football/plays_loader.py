# plays_loader.py
from __future__ import annotations
import yaml
from typing import Dict, Any, Optional

LANES = {"left", "middle", "right"}
LANES_EXT = {"left", "middle", "right", "strong", "weak"}  # NEW

OFF_DEPTHS = {"line", "backfield", "wide"}
DEF_DEPTHS = {"line", "box", "deep"}

# Offense routes we recognize (ok to extend freely)
ROUTE_SET = {
    "slant",
    "hitch",
    "out",
    "in",
    "drag",
    "post",
    "corner",
    "go",
    "screen_bubble",
}

# Offensive actions:
# - OL actions expanded to include 'combo' and 'block_down' (useful for TEs inline too)
OL_ACTIONS = {
    "pull",
    "trap",
    "double",
    "reach",
    "down",
    "climb",
    "pass_protect",
    "combo",
    "block_down",
    "backside_cutoff",  # occasionally tagged on OL/TE
}
# - Skill actions expanded to cover common blocking/utility verbs used in the sample plays
SKILL_ACTIONS = {
    "route",
    "run",
    "screen",
    "chip_release",
    "pass_protect",
    "stalk",
    "crack",
    "clear",
    "swing",
    "lead",
    "seal",
    "block_down",
    "backside_cutoff",
}
QB_ACTIONS = {"pass", "handoff", "keep", "boot"}

# Defense shell tags
SHELLS = {"cover0", "cover1", "cover2", "cover3", "quarters", "match"}

# Front / rush actions
FRONT_ACTIONS = {"blitz", "stunt", "edge_set", "spy", "contain", "rush_3"}

# Coverage actions (+ 'deep_help' alias treated as deep middle)
COV_ACTIONS = {"man", "zone", "deep_help"}

STUNT_PATHS = {"loop_inside", "crash_inside", "loop_outside"}
ZONES = {"flat", "curl", "hook", "seam", "deep_half", "deep_third", "quarter"}


class PlayLoadError(ValueError):
    pass


def _req(obj: dict, key: str) -> Any:
    if key not in obj:
        raise PlayLoadError(f"Missing required field: {key}")
    return obj[key]


def _is_ol_role(name: str) -> bool:
    return name in {"LT", "LG", "C", "RG", "RT"} or name.startswith("OL")


def load_offense_plays(path: str) -> Dict[str, dict]:
    data = yaml.safe_load(open(path, "r"))
    out: Dict[str, dict] = {}
    for p in data.get("plays", []):
        key = str(_req(p, "key"))

        # motion (optional, <=1)
        motion = p.get("motion")
        if motion:
            if "player" not in motion or "path" not in motion:
                raise PlayLoadError(f"{key}: motion requires player+path")
            for wp in motion["path"]:
                lane = wp.get("lane")
                depth = wp.get("depth")
                if lane not in LANES or depth not in OFF_DEPTHS:
                    raise PlayLoadError(f"{key}: bad motion waypoint {wp}")

        # assignments
        for a in p.get("assignments", []):
            player = a.get("player", "")
            act = _req(a, "action")

            if player == "QB":
                if act not in QB_ACTIONS:
                    raise PlayLoadError(f"{key}: QB action '{act}' invalid")
            elif _is_ol_role(player) or player in {"TE", "TE_left", "TE_right"}:
                # TE inline may use many OL-ish verbs (block_down, backside_cutoff)
                if act not in OL_ACTIONS and act not in SKILL_ACTIONS:
                    raise PlayLoadError(f"{key}: OL/TE action '{act}' invalid")
            else:
                # Skill group: allow wide variety of verbs used in sample plays
                if act not in SKILL_ACTIONS and act != "route":
                    # not strictly invalid, but warn-ready; allow unknown verbs pass-through
                    pass

            # Route details if present
            if act == "route":
                rt = a.get("route")
                if rt and rt not in ROUTE_SET:
                    # allow unknown routes but you may want to log a warning in the future
                    pass
                # optional: depth_yards, side

            # Lane fields sanity
            if "lane" in a and a["lane"] not in LANES:
                raise PlayLoadError(f"{key}: lane '{a['lane']}' invalid")

        out[key] = p
    return out


def load_defense_plays(path: str) -> Dict[str, dict]:
    data = yaml.safe_load(open(path, "r"))
    out: Dict[str, dict] = {}
    for p in data.get("plays", []):
        key = str(_req(p, "key"))
        # shell optional but if present must be valid
        sh = p.get("shell")
        if sh and sh not in SHELLS:
            raise PlayLoadError(f"{key}: shell '{sh}' invalid")

        # pre-snap checks
        for pre in p.get("pre_snap", []):
            t = pre.get("type")
            if t == "shift_front":
                if pre.get("direction") not in {"left", "right", "pinch", "wide"}:
                    raise PlayLoadError(
                        f"{key}: front shift '{pre.get('direction')}' invalid"
                    )
            elif t == "safety_roll":
                if pre.get("to_depth") not in {"box", "deep"}:
                    raise PlayLoadError(
                        f"{key}: safety_roll to_depth '{pre.get('to_depth')}' invalid"
                    )
            # pre-snap: show_blitz lane validation
            elif t == "show_blitz":
                if pre.get("lane") and pre["lane"] not in LANES_EXT:  # was LANES
                    raise PlayLoadError(
                        f"{key}: show_blitz lane '{pre['lane']}' invalid"
                    )
            else:
                # allow unknown pre-snap tags; they’re hints for your resolver/UI
                pass

        # assignments (front + coverage)
        for a in p.get("assignments", []):
            act = _req(a, "action")

            if act in FRONT_ACTIONS:
                # validate stunt specifics
                if act == "stunt":
                    if a.get("path") and a["path"] not in STUNT_PATHS:
                        raise PlayLoadError(
                            f"{key}: stunt path '{a.get('path')}' invalid"
                        )
                # lane optional, but if present must be valid
            if "lane" in a and a["lane"] not in LANES_EXT:  # was LANES
                raise PlayLoadError(f"{key}: lane '{a['lane']}' invalid")
            elif act in COV_ACTIONS:
                if act == "zone":
                    z = a.get("zone")
                    if z and z not in ZONES:
                        raise PlayLoadError(f"{key}: zone '{z}' invalid")
                elif act == "deep_help":
                    # treat like deep middle helper (you’ll translate this in the resolver)
                    pass
                # man coverage can specify "target"
            else:
                # unknown action — allow pass-through so you can experiment
                pass

        out[key] = p
    return out
