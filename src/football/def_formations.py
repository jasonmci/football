from .models import DefFormation

def def_43() -> DefFormation:
    f = DefFormation()
    f.add("left","line",1).add("middle","line",2).add("right","line",1)
    f.add("left","box",1).add("middle","box",1).add("right","box",1)
    f.add("left","deep",1).add("right","deep",1)
    return f

def def_nickel() -> DefFormation:
    f = DefFormation()
    f.add("left","line",1).add("middle","line",2).add("right","line",1)
    f.add("middle","box",2)
    f.add("left","box",1).add("right","box",1).add("middle","box",1)
    f.add("left","deep",1).add("right","deep",1)
    return f

def def_bear46() -> DefFormation:
    f = DefFormation()
    f.add("left","line",2).add("middle","line",2).add("right","line",2)
    f.add("middle","box",2).add("left","box",1).add("right","box",1)
    f.add("middle","deep",1)
    return f

DEF_FORMATIONS = {
    "43": def_43,
    "nickel": def_nickel,
    "bear46": def_bear46,
}
