# ---------- Dice engine ----------
import random
import re


_DICE_RE = re.compile(r"^\s*(\d+)d(\d+)([+-]\d+)?\s*$")


def roll_dice(expr: str, rng: random.Random) -> int:
    """
    Supports 'XdY+Z' (e.g., 2d6, 1d10+1).
    """
    m = _DICE_RE.match(expr)
    if not m:
        raise ValueError(f"bad dice expr: {expr}")
    n, faces, mod = int(m.group(1)), int(m.group(2)), int(m.group(3) or 0)
    if n <= 0 or faces <= 0:
        raise ValueError(f"bad dice expr: {expr}")
    total = sum(rng.randint(1, faces) for _ in range(n)) + mod
    return total


def roll_core(
    expr: str, rng: random.Random, advantage: int = 0, disadvantage: int = 0
) -> int:
    """
    Roll using dice expression 'XdY(+Z)' and offsetting advantage/disadvantage.

    Offset rule:
      net = advantage - disadvantage
      - If net > 0: roll (n + net) dice, keep the BEST n.
      - If net < 0: roll (n + |net|) dice, keep the WORST n.
      - If net == 0: roll exactly n dice.

    Examples (expr='2d6'):
      adv=1, dis=0  -> roll 3d6 keep best 2
      adv=2, dis=1  -> net=+1 -> roll 3d6 keep best 2
      adv=1, dis=2  -> net=-1 -> roll 3d6 keep worst 2
      adv=0, dis=0  -> roll 2d6
    """
    m = _DICE_RE.match(expr)
    if not m:
        # Fallback: simple XdY+Z parser
        return roll_dice(expr, rng)

    n, faces, mod = int(m.group(1)), int(m.group(2)), int(m.group(3) or 0)
    net = int(advantage) - int(disadvantage)
    extra = abs(net)

    # Base pool + offset extras
    rolls = [rng.randint(1, faces) for _ in range(n + extra)]

    if net > 0:
        kept = sorted(rolls, reverse=True)[:n]  # keep BEST n
    elif net < 0:
        kept = sorted(rolls)[:n]  # keep WORST n
    else:
        kept = rolls[:n]  # exactly n

    return sum(kept) + mod
