#!/usr/bin/env python3
# play_simulator_yaml.py
from __future__ import annotations

import argparse
import copy
import json
import random
import sys
from pathlib import Path
from typing import Dict, Optional, Tuple

# ---------- Imports ----------
try:
    from .yaml_loader import load_personnel, load_off_formations, load_def_formations
    from .models import OffFormationFull, DefFormation, Lane, OffDepth
    from .resolver import resolve_play, PLAY_O, PLAY_D, BOUNDS
    from .overlays import OVERLAY_MAP
except ImportError:
    from yaml_loader import load_personnel, load_off_formations, load_def_formations
    from models import OffFormationFull, DefFormation, Lane, OffDepth
    from resolver import resolve_play, PLAY_O, PLAY_D, BOUNDS
    from overlays import OVERLAY_MAP

OffCountsMap = Dict[tuple[Lane, OffDepth], int]

# ---------- Helpers: locate default YAMLs ----------
DEFAULT_OFF = "formations_offense.yaml"
DEFAULT_DEF = "formations_defense.yaml"
DEFAULT_PER = "personnel.yaml"

def _package_dir() -> Path:
    # Where this module lives (…/src/football)
    return Path(__file__).resolve().parent

def _search_paths(filename: str) -> list[Path]:
    cwd = Path.cwd()
    pkg = _package_dir()
    return [
        cwd / filename,
        cwd / "yaml" / filename,
        cwd / "assets" / filename,
        pkg / filename,
        pkg / "data" / filename,
    ]

def _resolve_yaml(filename: str, override: Optional[str]) -> Path:
    if override:
        p = Path(override).expanduser().resolve()
        if not p.exists():
            raise SystemExit(f"YAML not found: {p}")
        return p
    for candidate in _search_paths(filename):
        if candidate.exists():
            return candidate.resolve()
    raise SystemExit(
        f"Could not find '{filename}'. Looked in:\n  " +
        "\n  ".join(str(p) for p in _search_paths(filename))
    )

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
    off_full: OffFormationFull,
    def_base: DefFormation,
    oplay: str,
    dplay: str,
    blitz_lanes: Optional[Tuple[Lane,...]],
    trials: int,
    seed: Optional[int],
    verbose: bool,
) -> dict:
    rng = random.Random(seed) if seed is not None else random

    off_counts: OffCountsMap = off_full.to_counts()
    deff = copy.deepcopy(def_base)

    # Apply overlay
    if dplay == "blitz":
        lanes = blitz_lanes if blitz_lanes else ("left","middle")
        tags = OVERLAY_MAP.get("blitz", lambda f, **kw: {"call":"blitz","lanes":lanes})(deff, lanes=lanes)
    elif dplay == "base":
        tags = {"call":"base"}
    else:
        tags = OVERLAY_MAP[dplay](deff)

    yards_list = []
    lanes_seen = {"left":0,"middle":0,"right":0}
    events = {"interception":0,"sack":0,"fumble":0,"none":0}

    for t in range(trials):
        res = resolve_play(oplay, dplay, off_counts, deff, overlay_tags=tags, player_mod=0, rng=rng) # type: ignore
        yards_list.append(res["yards"])
        lanes_seen[res["lane"]] += 1
        ev = res["event"]
        if ev in ("interception","sack","fumble"):
            events[ev] += 1
        else:
            events["none"] += 1
        if verbose:
            core_roll = res.get("roll", res.get("roll2d6"))
            adv = res.get("adv", 0)
            eff = res.get("eff", None)
            base = res.get("base", 0)
            lane_mod = res.get("lane_mod", 0)
            if eff is not None:
                print(f"  trial {t+1:>3d}: lane={res['lane']:<6} 2d6={core_roll:+2d} adv={adv:+2d} eff={eff:>2d} "
                      f"base={base:+2d} mod={lane_mod:+2d} => yards={res['yards']:+3d} event={res['event']}")
            else:
                print(f"  trial {t+1:>3d}: lane={res['lane']:<6} roll={core_roll:+2d} base={base:+2d} "
                      f"lane_mod={lane_mod:+2d} => yards={res['yards']:+3d} event={res['event']}")

    avg, sd = mean_sd([float(y) for y in yards_list])
    return {
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
    p = argparse.ArgumentParser(description="YAML-based play simulator (auto-loads YAMLs; flags override if provided).")

    # Optional overrides for YAML paths (defaults will be auto-resolved)
    p.add_argument("--off-forms", help=f"Path to {DEFAULT_OFF} (optional; defaults to auto-discovery)")
    p.add_argument("--def-forms", help=f"Path to {DEFAULT_DEF} (optional; defaults to auto-discovery)")
    p.add_argument("--personnel", help=f"Path to {DEFAULT_PER} (optional; defaults to auto-discovery)")

    # Optional, only enforced if not --list
    p.add_argument("--off", help="Offensive formation key (from YAML).")
    p.add_argument("--def", dest="defn", help="Defensive formation key (from YAML).")
    p.add_argument("--o-play", dest="o_plays", action="append", choices=PLAY_O,
                   help="Offensive play (repeatable).")
    p.add_argument("--d-play", dest="d_plays", action="append", choices=PLAY_D,
                   help="Defensive play/overlay (repeatable).")

    p.add_argument("--blitz-lanes", type=str, default=None, help="Comma-separated lanes for blitz (e.g., left,middle)")
    p.add_argument("--trials", type=int, default=100, help="Trials per pairing.")
    p.add_argument("--seed", type=int, default=None, help="Random seed.")
    p.add_argument("--verbose", action="store_true", help="Print each trial details.")
    p.add_argument("--show-forms", action="store_true", help="Print formations before/after overlays.")
    p.add_argument("--json", dest="json_out", action="store_true", help="Emit JSON summary to stdout.")
    p.add_argument("--list", action="store_true", help="List formation keys from YAML then exit.")
    args = p.parse_args(argv)

    # Resolve YAMLs (auto-discover unless overridden)
    off_forms_path = _resolve_yaml(DEFAULT_OFF, args.off_forms)
    def_forms_path = _resolve_yaml(DEFAULT_DEF, args.def_forms)
    personnel_path = _resolve_yaml(DEFAULT_PER, args.personnel)

    # Load YAMLs
    off_forms = load_off_formations(str(off_forms_path))
    def_forms = load_def_formations(str(def_forms_path))
    personnel = load_personnel(str(personnel_path))

    # If --list, just print and exit
    if args.list:
        print("Loaded YAMLs:")
        print(f"  offense:   {off_forms_path}")
        print(f"  defense:   {def_forms_path}")
        print(f"  personnel: {personnel_path}")
        print("Offensive formation keys:", ", ".join(sorted(off_forms.keys())))
        print("Defensive formation keys:", ", ".join(sorted(def_forms.keys())))
        print("Personnel groups:", ", ".join(sorted(personnel.keys())))
        return 0

    # Enforce required args if not listing
    if not args.off or not args.defn or not args.o_plays or not args.d_plays:
        p.error("--off, --def, --o-play, and --d-play are required unless using --list")

    off_full = off_forms[args.off]
    def_base = def_forms[args.defn]

    # Header
    print(f"OFF: {args.off} | DEF: {args.defn}")
    print("Using YAMLs:")
    print(f"  offense:   {off_forms_path}")
    print(f"  defense:   {def_forms_path}")
    print(f"  personnel: {personnel_path}")

    if args.show_forms:
        print("  Off counts:", fmt_counts_off(off_full.to_counts()))
        print("  Def (pre-overlay):", fmt_counts_def(def_base))

    results = []
    blitz_lanes: Optional[Tuple[Lane,...]] = None
    if args.blitz_lanes:
        lanes = tuple(x.strip() for x in args.blitz_lanes.split(","))
        for ln in lanes:
            if ln not in ("left","middle","right"):
                raise SystemExit(f"Invalid lane in --blitz-lanes: {ln}")
        blitz_lanes = lanes  # type: ignore

    for oplay in args.o_plays:
        for dplay in args.d_plays:
            res = simulate_pair(off_full, def_base, oplay, dplay, blitz_lanes,
                                args.trials, args.seed, args.verbose)
            results.append(res)

    if args.json_out:
        def roundfloats(o):
            if isinstance(o, float): return round(o, 4)
            if isinstance(o, dict): return {k: roundfloats(v) for k, v in o.items()}
            if isinstance(o, list): return [roundfloats(x) for x in o]
            return o
        print(json.dumps(roundfloats(results), indent=2, sort_keys=False))
    else:
        print(f"{'OFF_PLAY':<12} {'DEF_PLAY':<12} {'AVG':>6} {'SD':>6} "
              f"{'MIN':>5} {'MAX':>5} {'N':>4}   Events [int/sack/fum]   Lanes [L/M/R]")
        for r in results:
            ev = r["events"]; ln = r["lanes"]
            print(f"{r['off_play']:<12} {r['def_play']:<12} {r['avg']:>6.2f} {r['sd']:>6.2f} "
                  f"{r['min']:>5d} {r['max']:>5d} {r['count']:>4d}   "
                  f"[{ev['interception']:>2d}/{ev['sack']:>2d}/{ev['fumble']:>2d}]   "
                  f"[{ln['left']:>2d}/{ln['middle']:>2d}/{ln['right']:>2d}]")

    if args.show_forms and results:
        last = results[-1]
        class _D:
            def __init__(self, counts): self.counts = counts
        print("-"*72)
        print("Def (after last overlay):", fmt_counts_def(_D(last["def_after_overlay"]))) # type: ignore
        if last["overlay_tags"].get("call") == "blitz":
            lanes = last["overlay_tags"].get("lanes", ())
            print("  Blitz lanes:", ",".join(lanes))

    print("-"*72)
    print("Tip: you can override YAML paths if needed, e.g., --off-forms path/to/fo.yaml")
    return 0

if __name__ == "__main__":
    sys.exit(main())
