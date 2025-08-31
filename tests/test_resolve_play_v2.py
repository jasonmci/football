# tests/test_resolve_play_v2.py
from __future__ import annotations
from typing import Dict, Tuple
import random
import textwrap

from src.football.models import (
    Placement,
    OffFormationFull,
    DefFormation,
    Lane,
    OffDepth,
    DefDepth,
)
from src.football.resolver import ResolverConfig, resolve_play_v2

OffCounts = Dict[Tuple[Lane, OffDepth], int]

# --- Helpers -----------------------------------------------------------------


def make_off(
    left=0,
    mid=0,
    right=0,
    back_left=0,
    back_mid=0,
    back_right=0,
    wide_left=0,
    wide_right=0,
) -> OffFormationFull:
    """Build a tiny offense by placements; ensures total 11 (adds OL/QB as needed)."""
    placements = []
    # Base OL/QB to get us close to 11; we’ll pad with WRs if needed
    placements += [
        Placement("OL", "left", "line", 1),
        Placement("OL", "middle", "line", 3),
        Placement("OL", "right", "line", 1),
        Placement("QB", "middle", "backfield", 1),
    ]
    # knobs
    if left:
        placements.append(Placement("RB", "left", "backfield", left))
    if mid:
        placements.append(Placement("RB", "middle", "backfield", mid))
    if right:
        placements.append(Placement("RB", "right", "backfield", right))
    if back_left:
        placements.append(Placement("RB", "left", "backfield", back_left))
    if back_mid:
        placements.append(Placement("RB", "middle", "backfield", back_mid))
    if back_right:
        placements.append(Placement("RB", "right", "backfield", back_right))
    if wide_left:
        placements.append(Placement("WR", "left", "wide", wide_left))
    if wide_right:
        placements.append(Placement("WR", "right", "wide", wide_right))

    # pad with WRs on right if we’re short of 11
    form = OffFormationFull(placements)
    missing = 11 - form.total_players()
    if missing > 0:
        placements.append(Placement("WR", "right", "wide", missing))
        form = OffFormationFull(placements)
    return form


def make_def(**counts: int) -> DefFormation:
    """
    Build a DefFormation with keys like left_line=1, middle_box=2, right_deep=1.
    """
    keymap: Dict[str, Tuple[Lane, DefDepth]] = {
        "left_line": ("left", "line"),
        "middle_line": ("middle", "line"),
        "right_line": ("right", "line"),
        "left_box": ("left", "box"),
        "middle_box": ("middle", "box"),
        "right_box": ("right", "box"),
        "left_deep": ("left", "deep"),
        "middle_deep": ("middle", "deep"),
        "right_deep": ("right", "deep"),
    }
    d = DefFormation()
    for k, v in counts.items():
        lane, depth = keymap[k]
        d.counts[(lane, depth)] = v
    # fill up to 11 with deep bodies so totals are realistic
    while d.total() < 11:
        d.counts[("middle", "deep")] = d.counts.get(("middle", "deep"), 0) + 1
    return d


def write_min_config(tmp_path, core_expr="2d6") -> ResolverConfig:
    """
    Write a minimal but complete resolver_config.yaml and return the loaded config.
    """
    cfg_yaml = textwrap.dedent(
        f"""
    dice:
      core: "{core_expr}"
      advantage_bonus: 1
      disadvantage_penalty: 1
    weights:
      eff_min: 3
      eff_max: 12
    modifiers:
      lane_strength_cap: 2
      blitz_pass_penalty: -1
      shell_vs_short: -1
      shell_vs_deep: -1
      draw_vs_blitz: +1
    turnovers:
      pass_interception:
        base: 0.0
        eff3: 0.03
        eff4: 0.02
        eff5: 0.015
        blitz_lane_bonus: 0.01
      run_fumble:
        base: 0.0
        eff3: 0.02
    tables:
      short_pass:
        "3":  {{ kind: sack, y: [-7, -3] }}
        "4":  {{ kind: inc,  y: [0, 0] }}
        "5":  {{ kind: inc,  y: [0, 0] }}
        "6":  {{ kind: gain, y: [3, 6] }}
        "7":  {{ kind: gain, y: [4, 9] }}
        "8":  {{ kind: gain, y: [6, 12] }}
        "9":  {{ kind: gain, y: [7, 14] }}
        "10": {{ kind: gain, y: [9, 16] }}
        "11": {{ kind: gain, y: [10, 20] }}
        "12": {{ kind: gain, y: [12, 24] }}
      deep_pass:
        "3":  {{ kind: sack, y: [-9, -4] }}
        "4":  {{ kind: inc,  y: [0, 0] }}
        "5":  {{ kind: inc,  y: [0, 0] }}
        "6":  {{ kind: gain, y: [10, 16] }}
        "7":  {{ kind: gain, y: [14, 20] }}
        "8":  {{ kind: gain, y: [18, 26] }}
        "9":  {{ kind: gain, y: [22, 32] }}
        "10": {{ kind: gain, y: [28, 40] }}
        "11": {{ kind: gain, y: [34, 48] }}
        "12": {{ kind: gain, y: [40, 60] }}
      inside_run:
        "3":  {{ kind: stuff, y: [-3, 0] }}
        "4":  {{ kind: stuff, y: [-2, 1] }}
        "5":  {{ kind: gain,  y: [0, 3] }}
        "6":  {{ kind: gain,  y: [1, 4] }}
        "7":  {{ kind: gain,  y: [2, 6] }}
        "8":  {{ kind: gain,  y: [3, 8] }}
        "9":  {{ kind: gain,  y: [4, 10] }}
        "10": {{ kind: gain,  y: [5, 12] }}
        "11": {{ kind: break, y: [8, 20] }}
        "12": {{ kind: break, y: [10, 30] }}
    """
    ).strip()
    p = tmp_path / "resolver_config.yaml"
    p.write_text(cfg_yaml)
    return ResolverConfig.from_yaml(str(p))


# --- Tests -------------------------------------------------------------------


def test_short_pass_vs_lane_blitz_mods(tmp_path):
    rng = random.Random(1)
    cfg = write_min_config(tmp_path, core_expr="2d6")

    # Offense: more bodies right to bias lane selection to right
    off_form = make_off()
    # We'll explicitly pick lane via assignment below.

    # Defense: nickel w/ blitz on RIGHT lane
    def_form = make_def(right_line=1, right_box=1, middle_line=2, left_line=1)

    off_play = {
        "tags": ["pass"],  # short pass family
        "assignments": [
            {"player": "QB", "action": "pass"},
            {
                "player": "WR_right_wide",
                "action": "route",
                "route": "slant",
                "lane": "right",
            },
        ],
    }
    def_play = {
        "shell": "cover1",
        "assignments": [
            {"player": "MLB", "action": "blitz", "lane": "right"},
        ],
    }

    res = resolve_play_v2(off_form, def_form, off_play, def_play, cfg, rng)

    # Assertions: chosen lane right, overlay negative due to blitz-on-lane, family short_pass
    assert res["lane"] == "right"
    assert res["play_family"] == "short_pass"
    assert res["mods"]["overlay"] <= 0
    assert cfg.eff_min <= res["eff"] <= cfg.eff_max
    assert cfg.eff_min <= res["eff"] <= cfg.eff_max


def test_play_action_softens_single_high(tmp_path):
    rng = random.Random(2)
    cfg = write_min_config(tmp_path, core_expr="2d6")

    off_form = make_off()  # plain singleback-ish
    def_form = make_def(middle_line=2, left_line=1, right_line=1, middle_box=1)

    off_play_plain = {
        "tags": ["pass"],
        "assignments": [
            {"player": "QB", "action": "pass"},
            {
                "player": "WR_left_wide",
                "action": "route",
                "route": "slant",
                "lane": "left",
            },
        ],
    }
    off_play_pa = {
        "tags": ["pass", "play_action"],
        "assignments": off_play_plain["assignments"],
    }
    def_play = {
        "shell": "cover3",
        "assignments": [],  # no blitz; shell should still add some penalty for short
    }

    res_plain = resolve_play_v2(off_form, def_form, off_play_plain, def_play, cfg, rng)
    rng = random.Random(2)  # reset seed so core roll is identical
    res_pa = resolve_play_v2(off_form, def_form, off_play_pa, def_play, cfg, rng)

    # PA should give a small positive o_tags modifier vs single-high
    assert res_pa["mods"]["o_tags"] >= res_plain["mods"]["o_tags"]
    # And typically raise eff (same core, so delta comes from modifiers)
    assert res_pa["eff"] >= res_plain["eff"]


def test_deep_pass_vs_two_high_shell(tmp_path):
    rng = random.Random(3)
    cfg = write_min_config(tmp_path, core_expr="2d6")

    off_form = make_off()
    def_form = make_def(
        middle_line=2, left_line=1, right_line=1, left_deep=1, right_deep=1
    )

    off_play_deep = {
        "tags": ["pass", "deep"],
        "assignments": [
            {"player": "QB", "action": "pass"},
            {
                "player": "WR_right_wide",
                "action": "route",
                "route": "go",
                "lane": "right",
            },
        ],
    }
    def_play_cover2 = {
        "shell": "cover2",
        "assignments": [],
    }

    res = resolve_play_v2(off_form, def_form, off_play_deep, def_play_cover2, cfg, rng)

    # Should classify as deep_pass family and apply some coverage penalty
    assert res["play_family"] == "deep_pass"
    assert res["mods"]["coverage"] <= 0
    assert cfg.eff_min <= res["eff"] <= cfg.eff_max


def test_inside_run_not_affected_by_deep_shell(tmp_path):
    rng = random.Random(4)
    cfg = write_min_config(tmp_path, core_expr="2d6")

    # Strong run look on left; defense light in box on left
    off_form = make_off(wide_left=1, back_mid=1)
    def_form = make_def(left_line=1, left_box=0, middle_line=2, middle_box=1)

    off_play_run = {
        "tags": ["run"],
        "assignments": [
            {"player": "QB", "action": "handoff"},
            {"player": "RB1", "action": "run", "lane": "left"},
        ],
    }
    def_play_cover2 = {
        "shell": "cover2",
        "assignments": [],  # no blitz; shell shouldn't matter for inside run coverage
    }

    res = resolve_play_v2(off_form, def_form, off_play_run, def_play_cover2, cfg, rng)

    assert res["play_family"] == "inside_run"
    # Coverage mod should be zero for runs
    assert res["mods"]["coverage"] == 0


def test_eff_is_clamped_and_returns_event_field(tmp_path):
    rng = random.Random(5)
    cfg = write_min_config(
        tmp_path, core_expr="3d6"
    )  # wider possible core values, then clamp

    # create an extreme mismatch to try to push eff
    off_form = make_off(wide_right=3, back_mid=2)
    def_form = make_def(right_line=0, right_box=0, middle_line=1)

    off_play = {
        "tags": ["pass"],
        "assignments": [
            {"player": "QB", "action": "pass"},
            {
                "player": "WR_right_wide",
                "action": "route",
                "route": "slant",
                "lane": "right",
            },
        ],
    }
    def_play = {"shell": "cover0", "assignments": []}

    res = resolve_play_v2(off_form, def_form, off_play, def_play, cfg, rng)

    assert cfg.eff_min <= res["eff"] <= cfg.eff_max
    assert "event" in res
    assert res["event"] in {"none", "sack", "stuff", "interception", "fumble"}
