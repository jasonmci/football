# yaml_loader.py
from __future__ import annotations

from typing import Dict, Tuple

import yaml

from .models import DefFormation, OffFormationFull, Placement

# --- Alignment guardrails for offense (prevent impossible spots like TE middle/wide) ---
ALLOWED_COMBOS = {
    "QB": {("middle", "backfield")},
    "RB": {("left", "backfield"), ("middle", "backfield"), ("right", "backfield")},
    "FB": {("left", "backfield"), ("middle", "backfield"), ("right", "backfield")},
    "WR": {("left", "wide"), ("right", "wide")},
    "TE": {("left", "line"), ("right", "line"), ("left", "wide"), ("right", "wide")},
    "OL": {("left", "line"), ("middle", "line"), ("right", "line")},
}


def load_personnel(path: str) -> Dict[str, Tuple[int, int, int]]:
    """
    Return mapping "code" -> (rb, te, wr). WR is derived as 5 - rb - te.
    Raises on invalid totals (>5 skill players).
    """
    with open(path, "r") as f:
        data = yaml.safe_load(f)
    out: Dict[str, Tuple[int, int, int]] = {}
    for g in data.get("personnel_groups", []):
        code = str(g["code"])
        rb, te = int(g["rb"]), int(g["te"])
        wr = 5 - rb - te
        if wr < 0:
            raise ValueError(
                f"personnel {code}: rb({rb}) + te({te}) exceeds 5 skill players"
            )
        out[code] = (rb, te, wr)
    return out


def load_off_formations(path: str) -> Dict[str, OffFormationFull]:
    """
    Load offensive formations from YAML and build OffFormationFull objects.
    Validates each placement against ALLOWED_COMBOS and runs OffFormationFull.validate().
    Also asserts the total headcount == 11.
    """
    with open(path, "r") as f:
        data = yaml.safe_load(f)
    out: Dict[str, OffFormationFull] = {}

    for fdef in data.get("formations", []):
        key = str(fdef["key"])
        placements = []
        total = 0

        for p in fdef.get("placements", []):
            pos = p["pos"]
            lane = p["lane"]
            depth = p["depth"]
            count = int(p["count"])

            if pos not in ALLOWED_COMBOS:
                raise ValueError(f"{key}: unknown pos '{pos}'")
            if (lane, depth) not in ALLOWED_COMBOS[pos]:
                raise ValueError(f"{key}: illegal alignment for {pos}: {lane}/{depth}")

            placements.append(Placement(pos, lane, depth, count))
            total += count

        if total != 11:
            raise ValueError(f"{key}: offensive formation totals {total}, expected 11")

        form = OffFormationFull(placements)
        errs = form.validate()
        if errs:
            raise ValueError(f"{key}: validation errors -> {errs}")

        out[key] = form

    return out


def load_def_formations(path: str) -> Dict[str, DefFormation]:
    """
    Load defensive formations from YAML into DefFormation (counts by (lane, depth)).
    Enforces that the sum of all counts == 11 (guardrail).
    """
    with open(path, "r") as f:
        data = yaml.safe_load(f)
    out: Dict[str, DefFormation] = {}

    for fdef in data.get("formations", []):
        key = str(fdef["key"])
        d = DefFormation()
        total = 0

        for c in fdef.get("counts", []):
            lane = c["lane"]
            depth = c["depth"]
            count = int(c["count"])
            if depth not in ("line", "box", "deep"):
                raise ValueError(
                    f"{key}: illegal defensive depth '{depth}' (must be line|box|deep)"
                )
            d.counts[(lane, depth)] = d.counts.get((lane, depth), 0) + count
            total += count

        if total != 11:
            raise ValueError(f"{key}: defensive formation totals {total}, expected 11")

        out[key] = d

    return out
