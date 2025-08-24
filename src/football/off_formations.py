from .models import OffFormationFull, Placement

def off_pro_set() -> OffFormationFull:
    f = OffFormationFull([
        Placement("OL","left","line",1),
        Placement("OL","middle","line",3),
        Placement("OL","right","line",1),
        Placement("QB","middle","backfield",1),
        Placement("RB","middle","backfield",1),
        Placement("TE","right","line",1),
        Placement("WR","left","wide",1),
        Placement("WR","right","wide",2),
    ])
    errs = f.validate()
    if errs: raise ValueError(errs)
    return f

def off_i_formation() -> OffFormationFull:
    f = OffFormationFull([
        Placement("OL","left","line",1),
        Placement("OL","middle","line",3),
        Placement("OL","right","line",1),
        Placement("QB","middle","backfield",1),
        Placement("RB","middle","backfield",1),
        Placement("FB","middle","backfield",1),
        Placement("TE","right","line",1),
        Placement("WR","left","wide",1),
    ])
    errs = f.validate()
    if errs: raise ValueError(errs)
    return f

def off_strong_i() -> OffFormationFull:
    f = OffFormationFull([
        Placement("OL","left","line",1),
        Placement("OL","middle","line",3),
        Placement("OL","right","line",1),
        Placement("QB","middle","backfield",1),
        Placement("RB","middle","backfield",1),
        Placement("FB","right","backfield",1),
        Placement("TE","right","line",1),
        Placement("WR","left","wide",1),
    ])
    errs = f.validate()
    if errs: raise ValueError(errs)
    return f

def off_weak_i() -> OffFormationFull:
    f = OffFormationFull([
        Placement("OL","left","line",1),
        Placement("OL","middle","line",3),
        Placement("OL","right","line",1),
        Placement("QB","middle","backfield",1),
        Placement("RB","middle","backfield",1),
        Placement("FB","left","backfield",1),
        Placement("TE","right","line",1),
        Placement("WR","left","wide",1),
    ])
    errs = f.validate()
    if errs: raise ValueError(errs)
    return f

def singleback_11() -> OffFormationFull:
    f = OffFormationFull([
        Placement("OL","left","line",1),
        Placement("OL","middle","line",3),
        Placement("OL","right","line",1),
        Placement("QB","middle","backfield",1),
        Placement("RB","middle","backfield",1),
        Placement("TE","right","line",1),
        Placement("WR","left","wide",2),
    ])
    errs = f.validate()
    if errs: raise ValueError(errs)
    return f

def singleback_12() -> OffFormationFull:
    f = OffFormationFull([
        Placement("OL","left","line",1),
        Placement("OL","middle","line",3),
        Placement("OL","right","line",1),
        Placement("QB","middle","backfield",1),
        Placement("RB","middle","backfield",1),
        Placement("TE","right","line",1),
        Placement("TE","left","line",1),
        Placement("WR","left","wide",1),
        Placement("WR","right","wide",1),
    ])
    errs = f.validate()
    if errs: raise ValueError(errs)
    return f

def off_trips_right_11() -> OffFormationFull:
    f = OffFormationFull([
        Placement("OL","left","line",1),
        Placement("OL","middle","line",3),
        Placement("OL","right","line",1),
        Placement("QB","middle","backfield",1),
        Placement("RB","middle","backfield",1),
        Placement("TE","right","line",1),
        Placement("WR","right","wide",2),
        Placement("WR","left","wide",1),
    ])
    errs = f.validate()
    if errs: raise ValueError(errs)
    return f

def off_spread_10() -> OffFormationFull:
    f = OffFormationFull([
        Placement("OL","left","line",1),
        Placement("OL","middle","line",3),
        Placement("OL","right","line",1),
        Placement("QB","middle","backfield",1),
        Placement("RB","middle","backfield",1),
        Placement("WR","left","wide",2),
        Placement("WR","right","wide",2),
    ])
    errs = f.validate()
    if errs: raise ValueError(errs)
    return f

def off_empty_00() -> OffFormationFull:
    f = OffFormationFull([
        Placement("OL","left","line",1),
        Placement("OL","middle","line",3),
        Placement("OL","right","line",1),
        Placement("QB","middle","backfield",1),
        Placement("WR","left","wide",3),
        Placement("WR","right","wide",2),
    ])
    errs = f.validate()
    if errs: raise ValueError(errs)
    return f

def off_empty_01() -> OffFormationFull:
    f = OffFormationFull([
        Placement("OL","left","line",1),
        Placement("OL","middle","line",3),
        Placement("OL","right","line",1),
        Placement("QB","middle","backfield",1),
        Placement("WR","left","wide",2),
        Placement("WR","right","wide",2),
        Placement("TE","left","wide",1),
    ])
    errs = f.validate()
    if errs: raise ValueError(errs)
    return f

def off_empty_02() -> OffFormationFull:
    f = OffFormationFull([
        Placement("OL","left","line",1),
        Placement("OL","middle","line",3),
        Placement("OL","right","line",1),
        Placement("QB","middle","backfield",1),
        Placement("WR","left","wide",2),
        Placement("WR","right","wide",2),
        Placement("WR","left","wide",1),
        Placement("TE","left","wide",1),
        Placement("TE","right","wide",1),
    ])
    errs = f.validate()
    if errs: raise ValueError(errs)
    return f

def off_empty_11() -> OffFormationFull:
    f = OffFormationFull([
        Placement("OL","left","line",1),
        Placement("OL","middle","line",3),
        Placement("OL","right","line",1),
        Placement("QB","middle","backfield",1),
        Placement("RB","middle","backfield",1),
        Placement("WR","left","wide",2),
        Placement("WR","right","wide",2),
        Placement("TE","left","line",1),
    ])
    errs = f.validate()
    if errs: raise ValueError(errs)
    return f

def off_wishbone() -> OffFormationFull:
    f = OffFormationFull([
        Placement("OL","left","line",1),
        Placement("OL","middle","line",3),
        Placement("OL","right","line",1),
        Placement("QB","middle","backfield",1),
        Placement("RB","left","backfield",1),
        Placement("RB","right","backfield",1),
        Placement("FB","middle","backfield",1),
        Placement("TE","right","line",1),
    ])
    errs = f.validate()
    if errs: raise ValueError(errs)
    return f

def off_trips_left_10() -> OffFormationFull:
    f = OffFormationFull([
        Placement("OL","left","line",1),
        Placement("OL","middle","line",3),
        Placement("OL","right","line",1),
        Placement("QB","middle","backfield",1),
        Placement("RB","middle","backfield",1),
        Placement("TE","right","line",1),
        Placement("WR","left","wide",1),
        Placement("WR","right","wide",2),
    ])
    errs = f.validate()
    if errs: raise ValueError(errs)
    return f

def off_jumbo_22() -> OffFormationFull:
    f = OffFormationFull([
        Placement("OL","left","line",1),
        Placement("OL","middle","line",3),
        Placement("OL","right","line",1),
        Placement("QB","middle","backfield",1),
        Placement("RB","middle","backfield",1),
        Placement("FB","middle","backfield",1),
        Placement("TE","right","line",1),
        Placement("TE","left","line",1),
        Placement("WR","left","wide",1),
    ])
    errs = f.validate()
    if errs: raise ValueError(errs)
    return f

def off_jumbo_32() -> OffFormationFull:
    f = OffFormationFull([
        Placement("OL","left","line",1),
        Placement("OL","middle","line",3),
        Placement("OL","right","line",1),
        Placement("QB","middle","backfield",1),
        Placement("RB","middle","backfield",2),
        Placement("FB","middle","backfield",1),
        Placement("TE","right","line",1),
        Placement("TE","left","line",1),
    ])
    errs = f.validate()
    if errs: raise ValueError(errs)
    return f

def off_jumbo_23() -> OffFormationFull:
    f = OffFormationFull([
        Placement("OL","left","line",1),
        Placement("OL","middle","line",3),
        Placement("OL","right","line",1),
        Placement("QB","middle","backfield",1),
        Placement("RB","middle","backfield",1),
        Placement("FB","middle","backfield",1),
        Placement("TE","right","line",1),
        Placement("TE","left","line",1),
        Placement("WR","left","wide",1),
        Placement("WR","right","wide",1),
    ])
    errs = f.validate()
    if errs: raise ValueError(errs)
    return f

OFF_FORMATIONS = {
    "pro_set": off_pro_set,
    "power_i": off_i_formation,
    "strong_i": off_strong_i,
    "weak_i": off_weak_i,
    "empty_00": off_empty_00,
    "empty_01": off_empty_01,
    "empty_02": off_empty_02,
    "empty_11": off_empty_11,
    "trips_right": off_trips_right_11,
    "trips_left": off_trips_left_10,
    "singleback_11": singleback_11,
    "singleback_12": singleback_12,
    "spread": off_spread_10,
    "jumbo_22": off_jumbo_22,
    "jumbo_32": off_jumbo_32,
    "jumbo_23": off_jumbo_23,
    "wishbone": off_wishbone,
}
