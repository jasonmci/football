#!/usr/bin/env python3
from __future__ import annotations
import argparse, sys
from pathlib import Path

try:
    from .yaml_loader import load_off_formations, load_def_formations
    from .plays_loader import load_offense_plays, load_defense_plays
except ImportError:
    from yaml_loader import load_off_formations, load_def_formations
    from plays_loader import load_offense_plays, load_defense_plays

LANES = ("left","middle","right")
OFF_DEPTHS = ("line","backfield","wide")
DEF_DEPTHS = ("line","box","deep")

def _grid(counts, lanes=LANES, depths=()):
    rows = []
    for d in depths:
        row = []
        for ln in lanes:
            row.append(counts.get((ln,d), 0))
        rows.append((d, row))
    return rows

def _render_off(off_counts):
    print("OFFENSE (Ln/Bk/W):")
    for d, row in _grid(off_counts, LANES, OFF_DEPTHS):
        print(f"  {d[:3].upper():>3} | " + "  ".join(f"{n:2d}" for n in row))

def _render_def(def_counts):
    print("DEFENSE (Ln/Box/Deep):")
    for d, row in _grid(def_counts, LANES, DEF_DEPTHS):
        print(f"  {d[:4].upper():>4} | " + "  ".join(f"{n:2d}" for n in row))

def _motion_str(motion: dict | None) -> str:
    if not motion: return "(none)"
    pts = [f"{wp['lane']}/{wp['depth']}" for wp in motion.get("path",[])]
    return f"{motion.get('player')} @ {motion.get('timing','pre_snap')}: " + " → ".join(pts)

def main(argv=None):
    ap = argparse.ArgumentParser(description="Visualize offense/defense formations & motion from YAML plays.")
    ap.add_argument("--off-form", required=True, help="off formation key")
    ap.add_argument("--def-form", required=True, help="def formation key")
    ap.add_argument("--off-play", help="off play key (to show motion/assignments)")
    ap.add_argument("--def-play", help="def play key (to show pre-snap disguise)")
    ap.add_argument("--plays-off", help="path to plays_offense.yaml")
    ap.add_argument("--plays-def", help="path to plays_defense.yaml")
    ap.add_argument("--off-forms", help="path to formations_offense.yaml")
    ap.add_argument("--def-forms", help="path to formations_defense.yaml")
    args = ap.parse_args(argv)

    here = Path(__file__).resolve().parent
    off_forms_path = Path(args.off_forms) if args.off_forms else here / "formations_offense.yaml"
    def_forms_path = Path(args.def_forms) if args.def_forms else here / "formations_defense.yaml"
    plays_off_path = Path(args.plays_off) if args.plays_off else here / "plays_offense.yaml"
    plays_def_path = Path(args.plays_def) if args.plays_def else here / "plays_defense.yaml"

    OFF_FORMS = load_off_formations(str(off_forms_path))
    DEF_FORMS = load_def_formations(str(def_forms_path))
    OFF_PLAYS = load_offense_plays(str(plays_off_path))
    DEF_PLAYS = load_defense_plays(str(plays_def_path))

    off_full = OFF_FORMS[args.off_form]
    def_base = DEF_FORMS[args.def_form]
    off_counts = off_full.to_counts()

    print(f"OFF FORM: {args.off_form} | DEF FORM: {args.def_form}")
    _render_off(off_counts)
    _render_def(def_base.counts)

    if args.off_play and args.off_play in OFF_PLAYS:
        print("\nOFF PLAY:", args.off_play)
        motion = OFF_PLAYS[args.off_play].get("motion")
        print("  motion:", _motion_str(motion))

    if args.def_play and args.def_play in DEF_PLAYS:
        print("\nDEF PLAY:", args.def_play)
        pre = DEF_PLAYS[args.def_play].get("pre_snap", [])
        if pre:
            for p in pre:
                print("  pre-snap:", p)

if __name__ == "__main__":
    sys.exit(main())
