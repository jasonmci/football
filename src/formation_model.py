from dataclasses import dataclass, field
from typing import Dict, Literal

Lane = Literal["left", "middle", "right"]
OffDepth = Literal["line", "backfield", "wide"]
DefDepth = Literal["line", "box", "deep"]


@dataclass
class OffFormation:
    """
    Counts by lane/depth (OL is abstracted as 1 unit that always occupies all lanes at "line")
    """

    counts: Dict[tuple[Lane, OffDepth], int] = field(default_factory=dict)
    has_qb: bool = True


@dataclass
class DefFormation:
    counts: Dict[tuple[Lane, DefDepth], int] = field(default_factory=dict)


def o(off: OffFormation, lane: Lane, depth: OffDepth, n: int = 1) -> None:
    off.counts[(lane, depth)] = off.counts.get((lane, depth), 0) + n


def d(defn: DefFormation, lane: Lane, depth: DefDepth, n: int = 1) -> None:
    defn.counts[(lane, depth)] = defn.counts.get((lane, depth), 0) + n
