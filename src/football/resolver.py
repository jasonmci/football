from __future__ import annotations

import random
import re
from dataclasses import dataclass
from typing import Any, Dict, Optional, Tuple

import yaml

from .models import DefFormation, Lane, OffDepth, OffFormationFull

# ---------- Dice engine ----------
_DICE_RE = re.compile(r"^\s*(\d+)d(\d+)([+-]\d+)?\s*$")


def roll_dice(expr: str, rng: random.Random) -> int:
    """
    Supports 'XdY+Z' (e.g., 2d6, 1d10+1).
    """
    m = _DICE_RE.match(expr)
    if not m:
        raise ValueError(f"bad dice expr: {expr}")
    n, faces, mod = int(m.group(1)), int(m.group(2)), int(m.group(3) or 0)
    if n <= 0 or faces <= 0:
        raise ValueError(f"bad dice expr: {expr}")
    total = sum(rng.randint(1, faces) for _ in range(n)) + mod
    return total


def roll_core(
    expr: str, rng: random.Random, advantage: int = 0, disadvantage: int = 0
) -> int:
    """
    Roll using dice expression 'XdY(+Z)' and offsetting advantage/disadvantage.

    Offset rule:
      net = advantage - disadvantage
      - If net > 0: roll (n + net) dice, keep the BEST n.
      - If net < 0: roll (n + |net|) dice, keep the WORST n.
      - If net == 0: roll exactly n dice.

    Examples (expr='2d6'):
      adv=1, dis=0  -> roll 3d6 keep best 2
      adv=2, dis=1  -> net=+1 -> roll 3d6 keep best 2
      adv=1, dis=2  -> net=-1 -> roll 3d6 keep worst 2
      adv=0, dis=0  -> roll 2d6
    """
    m = _DICE_RE.match(expr)
    if not m:
        # Fallback: simple XdY+Z parser
        return roll_dice(expr, rng)

    n, faces, mod = int(m.group(1)), int(m.group(2)), int(m.group(3) or 0)
    net = int(advantage) - int(disadvantage)
    extra = abs(net)

    # Base pool + offset extras
    rolls = [rng.randint(1, faces) for _ in range(n + extra)]

    if net > 0:
        kept = sorted(rolls, reverse=True)[:n]  # keep BEST n
    elif net < 0:
        kept = sorted(rolls)[:n]  # keep WORST n
    else:
        kept = rolls[:n]  # exactly n

    return sum(kept) + mod


# ---------- Config ----------
@dataclass
class ResolverConfig:
    core_expr: str
    adv_bonus: int
    dis_bonus: int
    eff_min: int
    eff_max: int
    mods: Dict[str, int]
    tables: Dict[str, Dict[int, Dict[str, Any]]]
    to_chance: Dict[str, Any]

    @staticmethod
    def from_yaml(path: str) -> "ResolverConfig":
        data = yaml.safe_load(open(path, "r"))
        core = data["dice"]["core"]
        adv = int(data["dice"].get("advantage_bonus", 1))
        dis = int(data["dice"].get("disadvantage_penalty", 1))
        eff_min = int(data["weights"].get("eff_min", 3))
        eff_max = int(data["weights"].get("eff_max", 12))
        mods = {k: int(v) for k, v in data.get("modifiers", {}).items()}
        # normalize table keys to int
        tables: Dict[str, Dict[int, Dict[str, Any]]] = {}
        for play, mapping in data.get("tables", {}).items():
            tables[play] = {int(k): v for k, v in mapping.items()}
        return ResolverConfig(
            core, adv, dis, eff_min, eff_max, mods, tables, data.get("turnovers", {})
        )


# ---------- Helpers ----------
def clamp(x: int, lo: int, hi: int) -> int:
    return lo if x < lo else hi if x > hi else x


def lane_strength(off_counts: Dict[Tuple[Lane, OffDepth], int], lane: Lane) -> int:
    return (
        off_counts.get((lane, "line"), 0)
        + off_counts.get((lane, "backfield"), 0)
        + off_counts.get((lane, "wide"), 0)
    )


def lane_modifier(
    off_counts: Dict[Tuple[Lane, OffDepth], int],
    deff: DefFormation,
    lane: Lane,
    cap: int,
) -> int:
    off_strength = lane_strength(off_counts, lane)
    def_pressure = deff.counts.get((lane, "line"), 0) + deff.counts.get(
        (lane, "box"), 0
    )
    raw = off_strength - def_pressure
    return clamp(raw, -cap, cap)


def strong_weak_to_lane(token: str, te_side: Lane) -> Lane:
    if token in ("left", "middle", "right"):
        return token  # type: ignore
    if token == "strong":
        return te_side
    if token == "weak":
        return "left" if te_side == "right" else "right"
    return "middle"


def offense_te_side(off_form: OffFormationFull) -> Lane:
    # crude: if any TE wide/line on right>0 -> right else left; fallback right
    counts = off_form.to_counts()
    right = counts.get(("right", "line"), 0) + counts.get(("right", "wide"), 0)
    left = counts.get(("left", "line"), 0) + counts.get(("left", "wide"), 0)
    return "right" if right >= left else "left"


# ---------- Outcome sampling ----------
def sample_from_table(
    play_key: str, eff: int, cfg: ResolverConfig, rng: random.Random
) -> Tuple[int, Optional[str]]:
    table = cfg.tables[play_key]
    eff = clamp(eff, cfg.eff_min, cfg.eff_max)
    band = table[eff]
    kind = band["kind"]
    lo, hi = band["y"]
    if kind in ("inc",):
        return 0, None
    if kind in ("sack", "stuff"):
        return rng.randint(lo, hi), kind
    # gain/break
    return rng.randint(lo, hi), None


def maybe_turnover(
    is_pass: bool,
    eff: int,
    blitz_on_lane: bool,
    cfg: ResolverConfig,
    rng: random.Random,
) -> Optional[str]:
    if is_pass:
        td = cfg.to_chance.get("pass_interception", {})
        p = float(td.get("base", 0.0))
        p += float(td.get(f"eff{eff}", 0.0))
        if blitz_on_lane:
            p += float(td.get("blitz_lane_bonus", 0.0))
        return "interception" if rng.random() < p else None
    else:
        td = cfg.to_chance.get("run_fumble", {})
        p = float(td.get("base", 0.0))
        if eff <= 3:
            p += float(td.get("eff3", 0.0))
        return "fumble" if rng.random() < p else None


# ---------- Main API ----------
def resolve_play_v2(
    off_form: OffFormationFull,
    def_form: DefFormation,
    off_play: dict,
    def_play: dict,
    cfg: ResolverConfig,
    rng: random.Random,
) -> Dict[str, Any]:
    # Phase 0: pre-snap (you can extend: motion shift → slight lane bias)
    te_side = offense_te_side(off_form)

    # Phase 1: choose lane (simplified: plays may specify lane; else pick weighted)
    chosen_lane: Lane = "middle"
    # try to read an assignment lane; fall back to strongest lane
    for a in off_play.get("assignments", []):
        if a.get("action") in ("run", "route", "screen") and "lane" in a:
            chosen_lane = strong_weak_to_lane(
                a["lane"], te_side
            )  # supports strong/weak later if you add it on offense
            break

    # Phase 2: compute modifiers
    off_counts = off_form.to_counts()
    lm_cap = int(cfg.mods.get("lane_strength_cap", 2))
    lane_mod = lane_modifier(off_counts, def_form, chosen_lane, lm_cap)

    # defensive assignments → overlay-style modifiers
    overlay_mod = 0
    blitz_on_lane = False
    shell_short = shell_deep = 0
    for a in def_play.get("assignments", []):
        if a["action"] == "blitz":
            ln = strong_weak_to_lane(a.get("lane", "middle"), te_side)
            if ln == chosen_lane:
                overlay_mod += int(
                    cfg.mods.get("blitz_pass_penalty", -1)
                )  # hurts passes
                blitz_on_lane = True
        elif a["action"] in ("zone", "deep_help"):
            # crude shell effect
            sh = def_play.get("shell", "")
            if sh in ("cover2", "cover3", "quarters"):
                shell_short += int(cfg.mods.get("shell_vs_short", -1))
                shell_deep += int(cfg.mods.get("shell_vs_deep", -1))

    # offense special tags (draw, play_action)
    o_tag_mod = 0
    is_pass = any(x.get("action") == "pass" for x in off_play.get("assignments", []))
    is_run = any(x.get("action") == "run" for x in off_play.get("assignments", []))
    tags = off_play.get("tags", [])
    if "play_action" in tags and def_play.get("shell") in ("cover1", "cover3"):
        # PA vs single-high shell: soften coverage a hair
        o_tag_mod += 1
    if is_run and any(
        a.get("action") == "blitz" for a in def_play.get("assignments", [])
    ):
        # Draw/counter could give a small bonus if tagged that way
        if "draw" in tags or "counter" in tags:
            o_tag_mod += int(cfg.mods.get("draw_vs_blitz", +1))

    # coverage penalty based on pass depth tag
    coverage_mod = 0
    if is_pass:
        if "deep" in tags:
            coverage_mod += shell_deep
        else:
            coverage_mod += shell_short

    # Phase 3: roll
    core = roll_core(cfg.core_expr, rng)
    eff = clamp(
        core + lane_mod + overlay_mod + o_tag_mod + coverage_mod,
        cfg.eff_min,
        cfg.eff_max,
    )

    # Phase 4: table lookup (pick play family; default from tags)
    play_family = "inside_run"
    if is_pass and "deep" in tags:
        play_family = "deep_pass"
    elif is_pass:
        play_family = "short_pass"
    elif is_run:
        play_family = "inside_run"
    yards, event = sample_from_table(play_family, eff, cfg, rng)

    # Phase 5: secondary turnover chance (if none yet)
    if event is None:
        maybe = maybe_turnover(is_pass, eff, blitz_on_lane, cfg, rng)
        if maybe:
            event = maybe
            if event == "interception":
                yards = rng.randint(-15, -6)
            elif event == "fumble":
                yards = rng.randint(-9, -3)

    return {
        "lane": chosen_lane,
        "core": core,
        "eff": eff,
        "mods": {
            "lane": lane_mod,
            "overlay": overlay_mod,
            "o_tags": o_tag_mod,
            "coverage": coverage_mod,
        },
        "play_family": play_family,
        "yards": int(yards),
        "event": event or "none",
    }
