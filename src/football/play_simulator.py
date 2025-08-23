#!/usr/bin/env python3
# play_simulator.py
#
# A CLI play simulator that uses your existing modules:
# - play_v_play_matrix.BASE
# - models.OffFormationFull, DefFormation
# - off_formations.OFF_FORMATIONS (returns OffFormationFull presets)
# - def_formations.DEF_FORMATIONS (returns DefFormation presets)
# - overlays.OVERLAY_MAP (defensive overlays)
# - resolver.resolve_play (core logic)
#
# Examples:
#   python play_simulator.py --list
#   python play_simulator.py --off pro --def nickel --o-play short_pass --d-play blitz --blitz-lanes left,middle --trials 1000 --seed 1 --show-forms
#   python play_simulator.py --off spread_10 --def dime --o-play short_pass --o-play deep_pass --d-play deep_shell --trials 500 --seed 7
#
from __future__ import annotations

import argparse
import copy
import json
import math
from typing import Dict, Tuple, Optional
import random
import sys

# ---------- Imports (package or flat) ----------
try:
    from .off_formations import OFF_FORMATIONS
    from .def_formations import DEF_FORMATIONS
    from .overlays import OVERLAY_MAP
    from .models import OffFormationFull, DefFormation, Lane, OffDepth
    from .resolver import resolve_play, PLAY_O, PLAY_D, BOUNDS
except Exception:
    from off_formations import OFF_FORMATIONS
    from def_formations import DEF_FORMATIONS
    from overlays import OVERLAY_MAP
    from models import OffFormationFull, DefFormation, Lane, OffDepth
    from resolver import resolve_play, PLAY_O, PLAY_D, BOUNDS

OffCountsMap = Dict[tuple[Lane, OffDepth], int]

# ---------- Formatting helpers ----------
def fmt_counts_def(f: DefFormation) -> str:
    parts = []
    for lane in ("left","middle","right"):
        parts.append(
            f"{lane[0].upper()}:L{f.counts.get((lane,'line'),0)} "
            f"B{f.counts.get((lane,'box'),0)} D{f.counts.get((lane,'deep'),0)}"
        )
    return " | ".join(parts)

def fmt_counts_off(counts: OffCountsMap) -> str:
    parts = []
    for lane in ("left","middle","right"):
        parts.append(
            f"{lane[0].upper()}:Ln{counts.get((lane,'line'),0)} "
            f"Bk{counts.get((lane,'backfield'),0)} W{counts.get((lane,'wide'),0)}"
        )
    return " | ".join(parts)

def mean_sd(vals):
    if not vals: return (0.0, 0.0)
    m = sum(vals)/len(vals)
    var = sum((x-m)*(x-m) for x in vals)/len(vals)
    return (m, var ** 0.5)

# ---------- Simulation ----------
def simulate_pair(
    off_key: str,
    def_key: str,
    oplay: str,
    dplay: str,
    blitz_lanes: Optional[Tuple[Lane,...]],
    trials: int,
    seed: Optional[int],
    verbose: bool,
) -> dict:
    rng = random.Random(seed) if seed is not None else random

    # Build formations fresh per pairing
    off_full: OffFormationFull = OFF_FORMATIONS[off_key]()
    off_counts: OffCountsMap = off_full.to_counts()

    base_def: DefFormation = DEF_FORMATIONS[def_key]()
    deff = copy.deepcopy(base_def)

    # Apply overlay
    if dplay == "blitz":
        lanes = blitz_lanes if blitz_lanes else ("left","middle")
        tags = OVERLAY_MAP["blitz"](deff, lanes=lanes)
    else:
        tags = OVERLAY_MAP[dplay](deff)

    yards_list = []
    lanes_seen = {"left":0,"middle":0,"right":0}
    events = {"interception":0,"sack":0,"fumble":0,"none":0}

    for t in range(trials):
        res = resolve_play(oplay, dplay, off_counts, deff, overlay_tags=tags, player_mod=0, rng=rng)
        yards_list.append(res["yards"])
        lanes_seen[res["lane"]] += 1
        ev = res["event"]
        if ev in events and ev is not None:
            events[ev] += 1
        else:
            events["none"] += 1
        if verbose:
            core_roll = res.get("roll", res.get("roll2d6"))   # support old/new resolvers
            adv = res.get("adv", 0)
            eff = res.get("eff", None)  # table index after shifting; may be None on old resolver
            base = res.get("base", 0)
            lane_mod = res.get("lane_mod", 0)

            if eff is not None:
                print(f"  trial {t+1:>3d}: lane={res['lane']:<6} 2d6={core_roll:+2d} adv={adv:+2d} eff={eff:>2d} "
                    f"base={base:+2d} mod={lane_mod:+2d} => yards={res['yards']:+3d} event={res['event']}")
            else:
                # fallback for old resolver
                print(f"  trial {t+1:>3d}: lane={res['lane']:<6} roll={core_roll:+2d} base={base:+2d} "
                    f"lane_mod={lane_mod:+2d} => yards={res['yards']:+3d} event={res['event']}")

    avg, sd = mean_sd([float(y) for y in yards_list])
    return {
        "off": off_key,
        "def": def_key,
        "off_play": oplay,
        "def_play": dplay,
        "overlay_tags": tags,
        "avg": avg,
        "sd": sd,
        "min": min(yards_list),
        "max": max(yards_list),
        "count": trials,
        "events": events,
        "lanes": lanes_seen,
        "off_counts": off_counts,
        "def_after_overlay": deff.counts,
    }

# ---------- CLI ----------
def main(argv=None):
    p = argparse.ArgumentParser(description="Play simulator using your formations, overlays, and resolver.")
    p.add_argument("--off", required=True, choices=sorted(OFF_FORMATIONS.keys()), help="Offensive formation key.")
    p.add_argument("--def", dest="defn", required=True, choices=sorted(DEF_FORMATIONS.keys()), help="Defensive formation key.")
    p.add_argument("--o-play", dest="o_plays", action="append", choices=PLAY_O, required=True, help="Offensive play (repeatable).")
    p.add_argument("--d-play", dest="d_plays", action="append", choices=PLAY_D, required=True, help="Defensive play/overlay (repeatable).")
    p.add_argument("--blitz-lanes", type=str, default=None, help="Comma-separated lanes when using d-play blitz, e.g., left,middle")
    p.add_argument("--trials", type=int, default=100, help="Trials per pairing (Monte Carlo).")
    p.add_argument("--seed", type=int, default=None, help="Random seed for reproducibility.")
    p.add_argument("--verbose", action="store_true", help="Print each trial.")
    p.add_argument("--show-forms", action="store_true", help="Print formations before/after overlays.")
    p.add_argument("--json", dest="json_out", action="store_true", help="Emit JSON summary to stdout.")
    p.add_argument("--list", action="store_true", help="List available keys and plays then exit.")
    args = p.parse_args(argv)

    if args.list:
        print("Offensive formations:", ", ".join(sorted(OFF_FORMATIONS.keys())))
        print("Defensive formations:", ", ".join(sorted(DEF_FORMATIONS.keys())))
        print("Offensive plays:", ", ".join(PLAY_O))
        print("Defensive plays:", ", ".join(PLAY_D))
        return 0

    blitz_lanes: Optional[Tuple[Lane,...]] = None
    if args.blitz_lanes:
        lanes = tuple(x.strip() for x in args.blitz_lanes.split(","))
        for ln in lanes:
            if ln not in ("left","middle","right"):
                raise SystemExit(f"Invalid lane in --blitz-lanes: {ln}")
        blitz_lanes = lanes  # type: ignore

    # Header
    print(f"OFF: {args.off} | DEF: {args.defn}")
    if args.show_forms:
        off_counts = OFF_FORMATIONS[args.off]().to_counts()
        deff = DEF_FORMATIONS[args.defn]()
        print("  Off counts:", fmt_counts_off(off_counts))
        print("  Def (pre-overlay):", fmt_counts_def(deff))

    results = []
    for oplay in args.o_plays:
        for dplay in args.d_plays:
            res = simulate_pair(args.off, args.defn, oplay, dplay, blitz_lanes, args.trials, args.seed, args.verbose)
            results.append(res)

    if args.json_out:
        # Ensure floats are rounded for readability
        def roundfloats(o):
            if isinstance(o, float): return round(o, 4)
            if isinstance(o, dict): return {k: roundfloats(v) for k, v in o.items()}
            if isinstance(o, list): return [roundfloats(x) for x in o]
            return o
        print(json.dumps(roundfloats(results), indent=2, sort_keys=False))
    else:
        # Pretty table
        print(f"{'OFF_PLAY':<12} {'DEF_PLAY':<12} {'AVG':>6} {'SD':>6} {'MIN':>5} {'MAX':>5} {'N':>4}   Events [int/sack/fum]   Lanes [L/M/R]")
        for r in results:
            ev = r["events"]; ln = r["lanes"]
            print(f"{r['off_play']:<12} {r['def_play']:<12} {r['avg']:>6.2f} {r['sd']:>6.2f} "
                  f"{r['min']:>5d} {r['max']:>5d} {r['count']:>4d}   "
                  f"[{ev['interception']:>2d}/{ev['sack']:>2d}/{ev['fumble']:>2d}]   "
                  f"[{ln['left']:>2d}/{ln['middle']:>2d}/{ln['right']:>2d}]")

    if args.show_forms and results:
        # Show defense after overlay for the last pairing
        last = results[-1]
        # Reconstruct a DefFormation-like print for after-overlay
        class _D:
            def __init__(self, counts): self.counts = counts
        print("-"*72)
        print("Def (after last overlay):", fmt_counts_def(_D(last["def_after_overlay"]))) # type: ignore
        if last["overlay_tags"].get("call") == "blitz":
            lanes = last["overlay_tags"].get("lanes", ())
            print("  Blitz lanes:", ",".join(lanes))

    print("-"*72)
    print("Tip: use --trials 1000 --seed 1 for stable averages; add --json for machine-readable output.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
