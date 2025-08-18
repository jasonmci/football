import random
from .formation_model import Lane, OffFormation, DefFormation
from .play_v_play_matrix import BASE


def lane_for_play(play: str) -> Lane:
    if play == "inside_run":
        return "middle"
    if play == "outside_run":
        return random.choice(["left", "right"])
    if play in ("short_pass", "screen"):
        # choose lane with most offensive “targets” (wide/backfield)
        # in a tie, prefer middle for short_pass, random for screen
        return "middle"
    if play == "deep_pass":
        return random.choice(["left", "right"])
    return "middle"


def lane_modifier(off: OffFormation, deff: DefFormation, lane: Lane) -> int:
    off_strength = off.counts.get((lane, "wide"), 0) + off.counts.get(
        (lane, "backfield"), 0
    )
    def_pressure = deff.counts.get((lane, "line"), 0) + deff.counts.get(
        (lane, "box"), 0
    )
    return max(-3, min(3, off_strength - def_pressure))


BOUNDS = {
    "inside_run": (-3, 10),
    "outside_run": (-4, 15),
    "short_pass": (-6, 18),
    "deep_pass": (-10, 40),
    "screen": (-8, 20),
}


def resolve_play(
    off_play: str, def_play: str, off: OffFormation, deff: DefFormation, player_mod=0
):
    lane = lane_for_play(off_play)
    base = BASE[(off_play, def_play)]
    lm = lane_modifier(off, deff, lane)
    roll = random.randint(1, 6) + random.randint(1, 6) - 7  # centered at 0
    yards = roll + base + lm + player_mod
    lo, hi = BOUNDS[off_play]
    yards = max(lo, min(hi, yards))
    # rare events
    rare = random.randint(1, 36)  # 1..36
    event = None
    if off_play in ("deep_pass", "short_pass") and rare == 1:
        event = "interception"
        yards = -random.randint(5, 25)
    elif off_play.startswith("inside") and rare == 1:
        event = "fumble"
        yards = -random.randint(3, 15)
    elif def_play == "blitz" and rare <= 3 and yards < 0:
        event = "sack"
        yards -= random.randint(2, 7)
    return {
        "lane": lane,
        "yards": yards,
        "event": event,
        "base": base,
        "lane_mod": lm,
        "roll": roll,
    }
