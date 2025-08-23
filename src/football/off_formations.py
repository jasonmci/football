from .models import OffFormationFull, Placement

def off_pro() -> OffFormationFull:
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

OFF_FORMATIONS = {
    "pro": off_pro,
    "trips_right_11": off_trips_right_11,
    "spread_10": off_spread_10,
}
