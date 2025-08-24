# yaml_loader.py
from __future__ import annotations
import yaml
from typing import Dict, Tuple
from .models import OffFormationFull, Placement, DefFormation, Lane, OffDepth, DefDepth

# Allowed combos to catch TE middle/wide mistakes, etc.
ALLOWED_COMBOS = {
    "QB": {("middle","backfield")},
    "RB": {("left","backfield"), ("middle","backfield"), ("right","backfield")},
    "FB": {("left","backfield"), ("middle","backfield"), ("right","backfield")},
    "WR": {("left","wide"), ("right","wide")},
    "TE": {("left","line"), ("right","line"), ("left","wide"), ("right","wide")},
    "OL": {("left","line"), ("middle","line"), ("right","line")},
}

def load_personnel(path: str) -> Dict[str, Tuple[int,int,int]]:
    with open(path, "r") as f:
        data = yaml.safe_load(f)
    out = {}
    for g in data["personnel_groups"]:
        rb, te = int(g["rb"]), int(g["te"])
        wr = 5 - rb - te
        if wr < 0: raise ValueError(f"Personnel {g['code']} exceeds 5 skill players")
        out[g["code"]] = (rb, te, wr)
    return out

def load_off_formations(path: str) -> Dict[str, OffFormationFull]:
    with open(path, "r") as f:
        data = yaml.safe_load(f)
    out = {}
    for fdef in data["formations"]:
        placements = []
        for p in fdef["placements"]:
            pos = p["pos"]; lane = p["lane"]; depth = p["depth"]; count = int(p["count"])
            if (lane, depth) not in ALLOWED_COMBOS[pos]:
                raise ValueError(f"Illegal alignment: {pos} at {lane}/{depth}")
            placements.append(Placement(pos, lane, depth, count))
        form = OffFormationFull(placements)
        errs = form.validate()
        if errs: raise ValueError({"formation": fdef["key"], "errors": errs})
        out[fdef["key"]] = form
    return out

def load_def_formations(path: str) -> Dict[str, DefFormation]:
    with open(path, "r") as f:
        data = yaml.safe_load(f)
    out = {}
    for fdef in data["formations"]:
        d = DefFormation()
        for c in fdef["counts"]:
            lane = c["lane"]; depth = c["depth"]; count = int(c["count"])
            d.counts[(lane, depth)] = d.counts.get((lane, depth), 0) + count
        out[fdef["key"]] = d
    return out
