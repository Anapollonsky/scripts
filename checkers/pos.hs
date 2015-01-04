module Position_Utils where

type Pos = (Int, Int)

addPos:: Pos -> Pos -> Pos
addPos (a,b) (c,d) = (a+c, b+d)

subPos:: Pos -> Pos -> Pos
subPos a (c,d) = addPos a ((-c), (-d))
