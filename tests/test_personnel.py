# tests/test_personnel.py
from src.football.models import Placement, OffFormationFull
from src.football.personnel import infer_personnel


def make_base_ol_qb():
    return [
        Placement("OL", "left", "line", 1),
        Placement("OL", "middle", "line", 3),
        Placement("OL", "right", "line", 1),
        Placement("QB", "middle", "backfield", 1),
    ]


def test_personnel_11():
    # 1 RB, 1 TE, so WR should be 3
    placements = make_base_ol_qb() + [
        Placement("RB", "middle", "backfield", 1),
        Placement("TE", "right", "line", 1),
        Placement("WR", "left", "wide", 1),
        Placement("WR", "right", "wide", 2),
    ]
    form = OffFormationFull(placements)
    code, counts = infer_personnel(form)
    assert code == "11"
    assert counts == {"RB": 1, "TE": 1, "WR": 3}


def test_personnel_12():
    placements = make_base_ol_qb() + [
        Placement("RB", "middle", "backfield", 1),
        Placement("TE", "left", "line", 1),
        Placement("TE", "right", "line", 1),
        Placement("WR", "right", "wide", 2),
    ]
    form = OffFormationFull(placements)
    code, counts = infer_personnel(form)
    assert code == "12"
    assert counts == {"RB": 1, "TE": 2, "WR": 2}


def test_personnel_21_fb_counts_as_rb():
    # 2 backs (RB+FB) and 1 TE -> "21"
    placements = make_base_ol_qb() + [
        Placement("RB", "middle", "backfield", 1),
        Placement("FB", "left", "backfield", 1),
        Placement("TE", "right", "line", 1),
        Placement("WR", "right", "wide", 2),
    ]
    form = OffFormationFull(placements)
    code, counts = infer_personnel(form)
    assert code == "21"
    assert counts == {"RB": 2, "TE": 1, "WR": 2}


def test_personnel_exotic_00_all_wr():
    placements = make_base_ol_qb() + [
        Placement("WR", "left", "wide", 2),
        Placement("WR", "right", "wide", 3),
    ]
    form = OffFormationFull(placements)
    code, counts = infer_personnel(form)
    assert code == "00"
    assert counts == {"RB": 0, "TE": 0, "WR": 5}


def test_personnel_out_of_shape_recovers_wr():
    # If someone builds a bad shape (skill != 5), WR is derived as 5 - RB - TE (floored at 0)
    placements = make_base_ol_qb() + [
        Placement("RB", "middle", "backfield", 2),
        Placement("TE", "right", "line", 2),
        # WR deliberately omitted → skill=4; helper will treat WR=1
    ]
    form = OffFormationFull(placements)
    code, counts = infer_personnel(form)
    assert code == "22"
    assert counts == {"RB": 2, "TE": 2, "WR": 1}
