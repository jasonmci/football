from typing import TypeVar, Sequence, cast
from .schemas import (
    Team, FormationSpecDTO, PlaySpecDTO,
    LogicalPlayerFrame, RoleSpec, Lane, Align,
    PlayLogicalFramesDTO, OffenseDepth, DefenseDepth
)

# Typed orders
LANE_ORDER: Sequence[Lane] = ("left", "middle", "right")
OFF_DEPTH_ORDER: Sequence[OffenseDepth] = ("under_center", "line", "wing", "backfield", "pistol", "shotgun")
DEF_DEPTH_ORDER: Sequence[DefenseDepth] = ("line", "box", "overhang", "deep")

# Generic stepper that preserves the literal type T
T = TypeVar("T", bound=str)
def _next_toward(current: T, target: T, order: Sequence[T]) -> T:
    if current == target:
        return current
    ci, ti = order.index(current), order.index(target)
    step = 1 if ti > ci else -1
    return order[ci + step]

def _resolve_role_name(name: str, formation: FormationSpecDTO) -> str | None:
    if name in formation.roles: return name
    if name in formation.aliases and formation.aliases[name] in formation.roles:
        return formation.aliases[name]
    lname = name.lower()
    for k in formation.roles.keys():
        if k.lower() == lname: return k
    for a, canon in formation.aliases.items():
        if a.lower() == lname and canon in formation.roles: return canon
    return None

def build_logical_presnap_frames( team: Team, formation: FormationSpecDTO, play: PlaySpecDTO) -> PlayLogicalFramesDTO:
    # mutable copy of role specs (lane/depth/align mutate over time)
    roles: dict[str, RoleSpec] = {
        r: RoleSpec(**spec.model_dump()) for r, spec in formation.roles.items()
    }

    def snap() -> list[LogicalPlayerFrame]:
        return [
            LogicalPlayerFrame(
                id=r,
                team=team,
                pos=spec.pos,
                lane=spec.lane,
                depth=spec.depth,
                align=spec.align,
            )
            for r, spec in roles.items()
        ]

    frames: list[list[LogicalPlayerFrame]] = [snap()]

    # ---- pre-snap events (apply → snapshot) ----
    unknown: list[str] = []
    for evt in play.pre_snap:
        rname = _resolve_role_name(evt.player, formation)
        if rname is None:
            unknown.append(evt.player)
            frames.append(snap())
            continue

        rs = roles[rname]
        if evt.to.lane is not None:
            rs.lane = evt.to.lane
        if evt.to.depth is not None:
            # depth is a Union; narrow to the correct side
            if team == "offense":
                rs.depth = cast(OffenseDepth, evt.to.depth)
            else:
                rs.depth = cast(DefenseDepth, evt.to.depth)
        if evt.to.align is not None:
            rs.align = evt.to.align

        frames.append(snap())

    if unknown:
        avail = ", ".join(sorted(formation.roles.keys()))
        raise ValueError(
            f"pre_snap references unknown role(s): {', '.join(unknown)}; available: {avail}"
        )

    # ---- motion (offense only) ----
    if team == "offense" and play.motion:
        mover_name = _resolve_role_name(play.motion.player, formation)
        if mover_name and mover_name in roles:
            # delay ticks (snapshot to reflect time passing)
            for _ in range(max(0, play.motion.delay)):
                frames.append(snap())

            for wp in play.motion.path:
                ticks = 0
                while ticks < 2000:  # safety cap
                    ticks += 1
                    rs = roles[mover_name]
                    moved = False

                    # lane step (Lane -> Lane, preserves literal type)
                    if rs.lane != wp.lane:
                        rs.lane = _next_toward(rs.lane, wp.lane, LANE_ORDER)
                        moved = True

                    # depth step (narrow union before stepping)
                    if not moved and rs.depth != wp.depth:
                        if team == "offense":
                            cur = cast(OffenseDepth, rs.depth)
                            tgt = cast(OffenseDepth, wp.depth)
                            rs.depth = _next_toward(cur, tgt, OFF_DEPTH_ORDER)
                        else:
                            cur = cast(DefenseDepth, rs.depth)
                            tgt = cast(DefenseDepth, wp.depth)
                            rs.depth = _next_toward(cur, tgt, DEF_DEPTH_ORDER)
                        moved = True

                    # align snaps to target if provided (no intermediate steps)
                    if wp.align is not None:
                        rs.align = wp.align

                    frames.append(snap())

                    if not moved and rs.lane == wp.lane and rs.depth == wp.depth:
                        break

    return PlayLogicalFramesDTO(name=play.name, frames=frames)