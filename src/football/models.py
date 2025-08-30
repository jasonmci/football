# models.py
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Literal, Iterable

# ----------------------------
# Type aliases / enums
# ----------------------------
Lane = Literal["left", "middle", "right"]
OffDepth = Literal["line", "backfield", "wide"]
DefDepth = Literal["line", "box", "deep"]

PosOff = Literal["QB", "RB", "FB", "WR", "TE", "OL"]

# Allowed offensive alignments (used by yaml_loader too)
ALLOWED_COMBOS: Dict[str, set[Tuple[Lane, OffDepth]]] = {
    "QB": {("middle", "backfield")},
    "RB": {
        ("left", "backfield"),
        ("middle", "backfield"),
        ("right", "backfield"),
    },
    "FB": {
        ("left", "backfield"),
        ("middle", "backfield"),
        ("right", "backfield"),
    },
    "WR": {
        ("left", "wide"),
        ("right", "wide"),
    },
    "TE": {
        ("left", "line"),
        ("right", "line"),
        ("left", "wide"),
        ("right", "wide"),
    },
    "OL": {
        ("left", "line"),
        ("middle", "line"),
        ("right", "line"),
    },
}


# ----------------------------
# Offensive side
# ----------------------------
@dataclass(frozen=True)
class Placement:
    """
    Offensive placement bucket.
    - pos: one of QB/RB/FB/WR/TE/OL
    - lane: left|middle|right
    - depth: line|backfield|wide  (WR/TE can be 'wide'; OL must be 'line'; QB/RB/FB must be 'backfield')
    - count: number of players in this bucket (>=1)
    """

    pos: PosOff
    lane: Lane
    depth: OffDepth
    count: int = 1

    def __post_init__(self) -> None:
        if self.count <= 0:
            raise ValueError(f"Placement count must be >=1 (got {self.count})")
        combos = ALLOWED_COMBOS.get(self.pos)
        if combos is None or (self.lane, self.depth) not in combos:
            raise ValueError(
                f"Illegal alignment for {self.pos}: {self.lane}/{self.depth}"
            )


@dataclass
class OffFormationFull:
    """
    Full offensive formation described as a list of placements.
    Provides validation guardrails and converts to lane/depth counts.
    """

    placements: List[Placement] = field(default_factory=list)

    def total_players(self) -> int:
        return sum(p.count for p in self.placements)

    def count_by_pos(self) -> Dict[str, int]:
        agg: Dict[str, int] = {}
        for p in self.placements:
            agg[p.pos] = agg.get(p.pos, 0) + p.count
        return agg

    def to_counts(self) -> Dict[Tuple[Lane, OffDepth], int]:
        """
        Collapse placements into a lane/depth -> count map the resolver uses.
        """
        out: Dict[Tuple[Lane, OffDepth], int] = {}
        for p in self.placements:
            key = (p.lane, p.depth)
            out[key] = out.get(key, 0) + p.count
        return out

    def validate(self) -> List[str]:
        """
        Non-throwing validation; returns a list of human-readable errors.
        yaml_loader also performs checks, but this provides an extra safety net.
        """
        errs: List[str] = []

        # Total headcount
        total = self.total_players()
        if total != 11:
            errs.append(f"total players = {total}, expected 11")

        # Per-position counts
        by_pos = self.count_by_pos()
        if by_pos.get("QB", 0) != 1:
            errs.append(f"QB count = {by_pos.get('QB', 0)}, expected 1")
        if by_pos.get("OL", 0) != 5:
            errs.append(f"OL count = {by_pos.get('OL', 0)}, expected 5")

        # Skill total (RB/FB/WR/TE must sum to 5)
        skill = sum(by_pos.get(k, 0) for k in ("RB", "FB", "WR", "TE"))
        if skill != 5:
            errs.append(f"skill positions total = {skill}, expected 5 (RB+FB+WR+TE)")

        # Per-placement legalities and non-negative aggregation already enforced in Placement.__post_init__
        # But we can double-check for any impossible over-aggregation (not expected)
        for (lane, depth), cnt in self.to_counts().items():
            if cnt < 0:
                errs.append(f"negative count at {lane}/{depth} (bug)")

        return errs


# ----------------------------
# Defensive side
# ----------------------------
@dataclass
class DefFormation:
    """
    Defensive formation as counts by (lane, depth).
    Example:
      counts[('left','line')] = 1
      counts[('middle','box')] = 2
      counts[('right','deep')] = 1
    """

    counts: Dict[Tuple[Lane, DefDepth], int] = field(default_factory=dict)

    def add(self, lane: Lane, depth: DefDepth, n: int = 1) -> None:
        if n == 0:
            return
        if n < 0:
            raise ValueError("Cannot add negative defenders")
        key = (lane, depth)
        self.counts[key] = self.counts.get(key, 0) + n

    def total(self) -> int:
        return sum(self.counts.values())

    def copy(self) -> "DefFormation":
        nf = DefFormation()
        nf.counts = dict(self.counts)
        return nf

    # Convenience accessors
    def get(self, lane: Lane, depth: DefDepth) -> int:
        return self.counts.get((lane, depth), 0)

    def lanes(self) -> Iterable[Lane]:
        return ("left", "middle", "right")

    def depths(self) -> Iterable[DefDepth]:
        return ("line", "box", "deep")

    def validate(self) -> List[str]:
        errs: List[str] = []
        total = self.total()
        if total != 11:
            errs.append(f"defense total = {total}, expected 11")
        # Non-negative check
        for k, v in self.counts.items():
            if v < 0:
                errs.append(f"negative defender count at {k}: {v}")
        return errs
