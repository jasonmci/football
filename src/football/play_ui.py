#!/usr/bin/env python3
from __future__ import annotations
import argparse
import logging
import random
from pathlib import Path
from typing import Dict, Tuple, List, Optional

# fallback for direct execution if package-relative import fails
from .yaml_loader import load_off_formations, load_def_formations
from .plays_loader import load_offense_plays, load_defense_plays
from .resolver import ResolverConfig, ResolveResult, resolve_play_v2
from .models import OffFormationFull, DefFormation
from .personnel import infer_personnel


def discover_default_paths(here: Path) -> Tuple[Path, Path, Path, Path, Path]:
    """Find YAML defaults in the package directory."""
    off_forms = here / "formations_offense.yaml"
    def_forms = here / "formations_defense.yaml"
    plays_off = here / "plays_offense.yaml"
    plays_def = here / "plays_defense.yaml"
    cfg_path = here / "resolver_config.yaml"
    return off_forms, def_forms, plays_off, plays_def, cfg_path


def choose_from_list(title: str, keys: List[str], default: Optional[str] = None) -> str:
    """Prompt the user to choose an item by number (or accept default)."""
    print(f"\n== {title} ==")
    for i, k in enumerate(keys, 1):
        marker = " (default)" if default and k == default else ""
        print(f"  {i:2d}. {k}{marker}")
    while True:
        raw = input(f"Select [1-{len(keys)}]{' or Enter' if default else ''}: ").strip()
        if not raw and default:
            return default
        if raw.isdigit():
            idx = int(raw)
            if 1 <= idx <= len(keys):
                return keys[idx - 1]
        print("Invalid selection, try again.")


def summarize_result(res: ResolveResult) -> str:
    """Compact one-line summary for a single trial."""

    m = res["mods"]

    return (
        f"lane={res['lane']} core={res['core']:+d} "
        f"mods(lane={m['lane']:+d},ov={m['overlay']:+d},"
        f"tag={m['o_tags']:+d},cov={m['coverage']:+d}) "
        f"eff={res['eff']:2d} => yards={res['yards']:+d} event={res['event']}"
    )


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(
        description="Interactive play simulator UI (YAML-driven plays & formations)."
    )
    ap.add_argument(
        "--seed", type=int, default=None, help="RNG seed for reproducibility"
    )
    ap.add_argument(
        "--trials", type=int, default=1, help="Number of repetitions per run"
    )
    ap.add_argument(
        "--log-file", type=str, help="Optional path to write a detailed log"
    )
    ap.add_argument(
        "--config", type=str, help="Path to resolver_config.yaml (defaults to package)"
    )
    ap.add_argument(
        "--auto",
        action="store_true",
        help="Run once non-interactively using first options (for CI)",
    )
    args = ap.parse_args(argv)

    # Logging setup
    log_handlers: List[logging.Handler] = [logging.StreamHandler()]
    if args.log_file:
        log_handlers.append(
            logging.FileHandler(args.log_file, mode="a", encoding="utf-8")
        )
    logging.basicConfig(
        level=logging.INFO,
        format="%(message)s",
        handlers=log_handlers,
    )
    log = logging.getLogger("play_ui")

    rng = random.Random(args.seed)

    # Resolve default YAML paths next to this file
    here = Path(__file__).resolve().parent
    off_forms_path, def_forms_path, plays_off_path, plays_def_path, cfg_default = (
        discover_default_paths(here)
    )
    cfg_path = Path(args.config) if args.config else cfg_default

    # Load data
    OFF_FORMS = load_off_formations(str(off_forms_path))
    DEF_FORMS = load_def_formations(str(def_forms_path))
    OFF_PLAYS = load_offense_plays(str(plays_off_path))
    DEF_PLAYS = load_defense_plays(str(plays_def_path))
    CFG = ResolverConfig.from_yaml(str(cfg_path))

    # Selections (interactive or automatic)
    off_form_keys = sorted(OFF_FORMS.keys())
    def_form_keys = sorted(str(k) for k in DEF_FORMS.keys())
    off_play_keys = sorted(OFF_PLAYS.keys())
    def_play_keys = sorted(DEF_PLAYS.keys())

    if args.auto:
        off_form_key = off_form_keys[0]
        def_form_key = def_form_keys[0]
        off_play_key = off_play_keys[0]
        def_play_key = def_play_keys[0]
    else:
        print("\nWelcome to the Football YAML Play Simulator 👋")
        print(
            "Pick formations and plays; we’ll run the resolver and log the details.\n"
        )
        off_form_key = choose_from_list("Offensive formation", off_form_keys)
        def_form_key = choose_from_list("Defensive formation", def_form_keys)
        off_play_key = choose_from_list("Offensive play", off_play_keys)
        def_play_key = choose_from_list("Defensive play", def_play_keys)

    off_form: OffFormationFull = OFF_FORMS[off_form_key]
    def_form: DefFormation = DEF_FORMS[def_form_key]
    pers_code, pers_counts = infer_personnel(off_form)
    off_play = OFF_PLAYS[off_play_key]
    def_play = DEF_PLAYS[def_play_key]

    print("\n---------------------------------------------")
    print(
        f"OFF: {off_form_key} | PLAY: {off_play_key} | PERSONNEL: {pers_code} "
        f"(RB={pers_counts['RB']}, TE={pers_counts['TE']}, WR={pers_counts['WR']})"
    )
    print(f"DEF: {def_form_key} | PLAY: {def_play_key}")
    print(f"Trials: {args.trials} | Dice: {CFG.core_expr}\n")

    total_yards = 0
    events: Dict[str, int] = {}
    for t in range(1, args.trials + 1):
        res = resolve_play_v2(off_form, def_form, off_play, def_play, CFG, rng)
        total_yards += int(res["yards"])
        events[res["event"]] = events.get(res["event"], 0) + 1

        line = f"trial {t:3d}: {summarize_result(res)}"
        log.info(line)

    avg = total_yards / max(1, args.trials)
    print("\n=== SUMMARY ===")
    print(f"Total yards: {total_yards:+d} | Avg/play: {avg:+.2f}")
    if events:
        ev_str = ", ".join(f"{k}:{v}" for k, v in sorted(events.items()))
        print(f"Events: {ev_str}")
    print("---------------------------------------------\n")

    # Simple loop for another run
    if not args.auto:
        while True:
            again = input("Run again with new selections? [y/N]: ").strip().lower()
            if again == "y":
                return main(
                    ["--trials", str(args.trials)]
                    + ([] if args.seed is None else ["--seed", str(args.seed)])
                    + ([] if not args.log_file else ["--log-file", args.log_file])
                )
            break

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
