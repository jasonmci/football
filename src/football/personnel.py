# personnel.py
from __future__ import annotations
from typing import Dict, Tuple

from .models import OffFormationFull


def infer_personnel(off_form: OffFormationFull) -> Tuple[str, Dict[str, int]]:
    """
    Return (code, counts) where:
      code  -> e.g. "11", "12", "21", "00", "32"
      counts -> {"RB": rb_total, "TE": te_total, "WR": wr_total}

    Convention:
      - RB includes RB + FB
      - TE is TE
      - WR is WR
      - OL=5 and QB=1 are assumed/validated elsewhere (OffFormationFull.validate()).
      - Skill total must be 5; if not, WR is derived as max(0, 5 - RB - TE).
    """
    by_pos = off_form.count_by_pos()
    rb = by_pos.get("RB", 0) + by_pos.get("FB", 0)
    te = by_pos.get("TE", 0)
    wr = by_pos.get("WR", 0)

    # In a valid formation skill should be 5. Derive WR if someone builds odd inputs.
    skill = rb + te + wr
    if skill != 5:
        wr = max(0, 5 - rb - te)

    code = f"{rb}{te}"
    return code, {"RB": rb, "TE": te, "WR": wr}
