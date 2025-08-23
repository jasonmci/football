# resolver.py
from __future__ import annotations

from typing import Dict, Literal, Optional
import random

from .play_v_play_matrix import BASE
from .models import Lane, OffDepth, DefFormation, OffFormationFull

# Optional type alias for readability
OffCountsMap = Dict[tuple[Lane, OffDepth], int]

DEEP_PASS_TABLE = {
    2: ("int",  -25, -10),
    3: ("sack",  -10,  -5),
    4: ("inc",     0,    0),
    5: ("inc",     0,    0),
    6: ("gain",   12,   18),
    7: ("gain",   15,   22),
    8: ("gain",   18,   25),
    9: ("gain",   22,   30),
    10: ("gain",  28,   38),
    11: ("gain",  33,   45),
    12: ("gain",  40,   60),
}

SHORT_PASS_TABLE = {
    2: ("int",  -15,  -5),
    3: ("sack", -10,  -4),
    4: ("inc",    0,   0),
    5: ("inc",    0,   0),
    6: ("gain",   3,   6),
    7: ("gain",   4,   8),
    8: ("gain",   6,  12),
    9: ("gain",   8,  15),
    10:("gain",  10,  18),
    11:("gain",  12,  22),
    12:("gain",  15,  30),
}

SCREEN_TABLE = {
    2: ("gain",  -6,  -2),   # blown up
    3: ("inc",    0,   0),
    4: ("gain",   0,   2),
    5: ("gain",   1,   4),
    6: ("gain",   3,   7),
    7: ("gain",   4,  10),
    8: ("gain",   6,  14),
    9: ("gain",   8,  18),
    10:("gain",  10,  22),
    11:("gain",  12,  25),
    12:("gain",  14,  28),
}

INSIDE_RUN_TABLE = {
    2: ("fumble",-8, -3),
    3: ("gain", -3,  0),
    4: ("gain", -2,  1),
    5: ("gain",  0,  2),
    6: ("gain",  2,  4),
    7: ("gain",  3,  5),
    8: ("gain",  4,  7),
    9: ("gain",  5,  9),
    10:("gain",  6, 10),
    11:("gain",  8, 12),
    12:("gain", 10, 20),
}

OUTSIDE_RUN_TABLE = {
    2: ("fumble",-8, -3),
    3: ("gain", -4,  0),
    4: ("gain", -2,  1),
    5: ("gain",  0,  3),
    6: ("gain",  2,  5),
    7: ("gain",  3,  6),
    8: ("gain",  5,  9),
    9: ("gain",  7, 12),
    10:("gain",  8, 15),
    11:("gain", 10, 18),
    12:("gain", 12, 25),
}

TABLES_BY_PLAY = {
    "deep_pass":   DEEP_PASS_TABLE,
    "short_pass":  SHORT_PASS_TABLE,
    "screen":      SCREEN_TABLE,
    "inside_run":  INSIDE_RUN_TABLE,
    "outside_run": OUTSIDE_RUN_TABLE,
}

def _sample_from_table(play: str, eff: int, rng: random.Random) -> tuple[int, Optional[str]]:
    """Pick yards/event by looking up the shifted 2d6 result."""
    table = TABLES_BY_PLAY[play]
    eff = 2 if eff < 2 else 12 if eff > 12 else eff
    kind, lo, hi = table[eff]
    if kind == "inc":
        return 0, None
    if kind == "sack":
        return rng.randint(lo, hi), "sack"
    if kind == "int":
        return rng.randint(lo, hi), "interception"
    if kind == "fumble":
        return rng.randint(lo, hi), "fumble"
    # gain
    return rng.randint(lo, hi), None

# Play spaces (used for validation / tooling; BASE comes from play_v_play_matrix)
PLAY_O: list[str] = ["inside_run", "outside_run", "short_pass", "deep_pass", "screen"]
PLAY_D: list[str] = ["base", "run_commit", "blitz", "short_shell", "deep_shell"]

# Natural caps per play type (keeps results believable)
BOUNDS: Dict[str, tuple[int, int]] = {
    "inside_run": (-3, 10),
    "outside_run": (-4, 15),
    "short_pass": (-6, 18),
    "deep_pass": (-10, 40),
    "screen": (-8, 20),
}

# ---------- lane selection & modifiers ----------

def _lane_strength(off_counts: OffCountsMap, lane: Lane) -> int:
    """Targets in a lane = wide + backfield bodies (formation heat)."""
    return off_counts.get((lane, "wide"), 0) + off_counts.get((lane, "backfield"), 0)

def lane_for_play(play: str, off_counts: OffCountsMap) -> Lane:
    """Choose target lane for a play, using formation heat when sensible."""
    if play == "inside_run":
        return "middle"
    if play == "outside_run":
        # prefer the heavier outside; tie-break random
        l, r = _lane_strength(off_counts, "left"), _lane_strength(off_counts, "right")
        if l > r: return "left"
        if r > l: return "right"
        return random.choice(["left", "right"])
    if play == "short_pass":
        # favor most targets, bias middle on ties
        lanes = [("left", _lane_strength(off_counts, "left")),
                 ("middle", _lane_strength(off_counts, "middle")),
                 ("right", _lane_strength(off_counts, "right"))]
        lanes.sort(key=lambda x: (x[1], x[0] == "middle"), reverse=True)
        return lanes[0][0]  # type: ignore[return-value]
    if play == "deep_pass":
        # usually outside; choose heavier side or random
        l, r = _lane_strength(off_counts, "left"), _lane_strength(off_counts, "right")
        if l > r: return "left"
        if r > l: return "right"
        return random.choice(["left", "right"])
    if play == "screen":
        # pick the lane with most immediate targets; tie favors middle
        best_lane, best = "middle", -1
        for ln in ("left", "middle", "right"):
            s = _lane_strength(off_counts, ln)
            if s > best:
                best_lane, best = ln, s
        return best_lane  # type: ignore[return-value]
    return "middle"

def lane_modifier(off_counts: OffCountsMap, deff: DefFormation, lane: Lane) -> int:
    """Offense strength minus defensive pressure (clamped to [-3, 3])."""
    off_strength = _lane_strength(off_counts, lane)
    def_pressure = deff.counts.get((lane, "line"), 0) + deff.counts.get((lane, "box"), 0)
    raw = off_strength - def_pressure
    return 3 if raw > 3 else -3 if raw < -3 else raw

def defensive_overlay_adjust(off_play: str, lane: Lane, overlay_tags: dict) -> int:
    """Return OFFENSE advantage delta from overlay (negative favors defense)."""
    mod = 0
    call = overlay_tags.get("call")
    if call == "run_commit":
        if "run" in off_play: mod -= 1      # biting helps vs run
        else: mod += 0                      # base matrix already penalizes/helps
    elif call == "blitz":
        blitz_lanes = overlay_tags.get("lanes", ())
        if "pass" in off_play and lane in blitz_lanes:
            mod -= 2                        # harder to pass
        elif off_play == "outside_run" and lane not in blitz_lanes:
            mod += 1                        # vacated contain
    elif call == "short_shell":
        if off_play == "short_pass": mod -= 1
    elif call == "deep_shell":
        if off_play == "deep_pass": mod -= 2
    return mod


# ---------- main resolution ----------

def resolve_play(
    off_play: str,
    def_play: str,
    off_counts: OffCountsMap,
    deff: DefFormation,
    overlay_tags: Optional[dict] = None,
    player_mod: int = 0,
    rng: Optional[random.Random] = None,
) -> dict:
    r = rng or random

    lane = lane_for_play(off_play, off_counts)
    base = BASE[(off_play, def_play)]

    # offense advantage from formation/pressure and overlay
    lm = lane_modifier(off_counts, deff, lane)  # off_strength - def_pressure
    if overlay_tags:
        lm += defensive_overlay_adjust(off_play, lane, overlay_tags)

    adv = base + lm + player_mod                # shift to apply to 2d6
    roll2d6 = r.randint(1,6) + r.randint(1,6)   # 2..12
    eff = roll2d6 + adv                         # shift table index by advantage

    yards, event = _sample_from_table(off_play, eff, r)

    # hard caps per play, just in case
    lo, hi = BOUNDS[off_play]
    yards = max(lo, min(hi, yards))

    return {
        "lane": lane,
        "yards": int(yards),
        "event": event,
        "base": base,
        "lane_mod": lm,
        "adv": adv,
        "roll2d6": roll2d6,
        "eff": max(2, min(12, eff)),
    }

__all__ = [
    "PLAY_O", "PLAY_D", "BOUNDS",
    "lane_for_play", "lane_modifier", "defensive_overlay_adjust",
    "resolve_play",
]

# ---------- quick demo (uses your snippet) ----------
# if __name__ == "__main__":
#     # Only runs when executed directly; safe to keep for local smoke tests
#     from .off_formations import OFF_FORMATIONS
#     from .def_formations import DEF_FORMATIONS
#     from .overlays import OVERLAY_MAP

#     # offense: make full formation, validate, then counts
#     off_full: OffFormationFull = OFF_FORMATIONS["pro"]()
#     off_counts = off_full.to_counts()

#     # defense: make base formation (already counts-based)
#     def_form = DEF_FORMATIONS["nickel"]()

#     # apply overlay and get tags
#     tags = OVERLAY_MAP["blitz"](def_form, lanes=("left", "middle"))

#     # resolve a couple plays
#     for oplay in ("short_pass", "screen", "deep_pass", "inside_run", "outside_run"):
#         res = resolve_play(oplay, "blitz", off_counts, def_form, overlay_tags=tags, player_mod=0)
#         print(f"{oplay:12} -> lane={res['lane']:>6} roll={res['roll']:+2d} "
#               f"base={res['base']:+2d} mod={res['lane_mod']:+2d} yards={res['yards']:>3d} event={res['event']}")
