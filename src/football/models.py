from dataclasses import dataclass, field
from typing import Literal, List, Dict, Tuple

Lane = Literal["left","middle","right"]
OffDepth = Literal["line","backfield","wide"]
DefDepth = Literal["line","box","deep"]
Pos  = Literal["QB","RB","FB","WR","TE","OL"]

OffCountsMap = dict[tuple[Lane, OffDepth], int]
DefCountsMap = dict[tuple[Lane, DefDepth], int]

ALLOWED_DEPTHS: Dict[Pos, set[OffDepth]] = {
    "QB": {"backfield"},
    "RB": {"backfield"},
    "FB": {"backfield"},
    "WR": {"wide"},
    "TE": {"line","wide"},
    "OL": {"line"},
}

@dataclass
class Placement:
    pos: Pos
    lane: Lane
    depth: OffDepth
    count: int = 1

@dataclass
class OffFormationFull:
    placements: List[Placement] = field(default_factory=list)

    def validate(self) -> list[str]:
        errors: list[str] = []
        total = sum(p.count for p in self.placements)
        if total != 11:
            errors.append(f"Formation has {total} players, must be 11.")
        qbs = sum(p.count for p in self.placements if p.pos == "QB")
        if qbs != 1:
            errors.append(f"Must have exactly 1 QB (have {qbs}).")
        ol_total = sum(p.count for p in self.placements if p.pos == "OL")
        if ol_total != 5:
            errors.append(f"Must have exactly 5 OL (have {ol_total}).")
        ol_on_line = sum(p.count for p in self.placements if p.pos == "OL" and p.depth == "line")
        if ol_on_line != 5:
            errors.append(f"All 5 OL must be on the line (have {ol_on_line} on line).")
        for p in self.placements:
            if p.depth not in ALLOWED_DEPTHS[p.pos]:
                errors.append(f"{p.pos} cannot align at {p.depth} (lane={p.lane}).")
        backfield = sum(p.count for p in self.placements if p.depth == "backfield")
        if backfield > 4:
            errors.append(f"Max 4 players in backfield (have {backfield}).")
        return errors

    def to_counts(self) -> OffCountsMap:
        out: OffCountsMap = {}
        for p in self.placements:
            key = (p.lane, p.depth)
            out[key] = out.get(key, 0) + p.count
        return out

@dataclass
class DefFormation:
    counts: DefCountsMap = field(default_factory=dict)

    def add(self, lane: Lane, depth: DefDepth, n: int = 1) -> "DefFormation":
        """Increment defenders in a lane/depth bucket."""
        self.counts[(lane, depth)] = self.counts.get((lane, depth), 0) + n
        return self  # allow chaining

    def get(self, lane: Lane, depth: DefDepth) -> int:
        return self.counts.get((lane, depth), 0)

    def move(self, lane: Lane, src: DefDepth, dst: DefDepth, n: int = 1) -> "DefFormation":
        """Move up to n defenders from src to dst within a lane (no-op if none)."""
        have = self.get(lane, src)
        if have <= 0:
            return self
        k = min(have, n)
        self.counts[(lane, src)] = have - k
        self.counts[(lane, dst)] = self.get(lane, dst) + k
        return self
