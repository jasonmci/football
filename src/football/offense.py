from dataclasses import dataclass, field
from typing import List, Dict
from .football_types import Lane, OffDepth, OffPos, OffCountsMap

# OL is the only position that can occupy the "line" depth
ALLOWED_DEPTHS: Dict[OffPos, set[OffDepth]] = {
    "QB": {"line", "backfield", "wide"},
    "RB": {"line", "backfield", "wide"},
    "FB": {"line", "backfield", "wide"},
    "WR": {"line", "backfield", "wide"},
    "TE": {"line", "backfield", "wide"},
    "OL": {"line"},
}

@dataclass
class Placement:
    pos: OffPos
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