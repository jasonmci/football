from typing import Literal

Lane = Literal["left","middle","right"]
OffDepth = Literal["line","backfield","wide"]
DefDepth = Literal["line","box","deep"]
OffPos  = Literal["QB","RB","FB","WR","TE","OL"]

# Offense counts map (what the resolver wants)
OffCountsMap = dict[tuple[Lane, OffDepth], int]

# Defense counts map (what overlays & resolver use now)
DefCountsMap = dict[tuple[Lane, DefDepth], int]
