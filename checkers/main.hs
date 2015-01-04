module Main where
import Position_Utils
import Data.List

data Square = Blank | Empty | Piece PieceType PiecePlayer deriving Eq
data PieceType = Pawn | Queen deriving Eq
data PiecePlayer = P1 | P2 deriving Eq


type Board = [[Square]]


prettyBoard::Board -> String
prettyBoard = unlines . map ( concatMap prettySquare)

instance Show Square where
  show (Piece a f) = show a ++ show f

instance Show PieceType where
  show Pawn = "P"
  show Queen = "Q"

instance Show PiecePlayer where
  show P1 = "1"
  show P2 = "2"

prettySquare::Square->String
prettySquare Blank = "    "
prettySquare Empty = "[  ]"
prettySquare (Piece a f) = "[" ++ show a ++ show f ++ "]"

-------------------- Board Utilities
getSquare ::Board->Pos->Square
getSquare board (a, b) = board!!a!!b

iBoard::Board
iBoard = [[(Piece Queen P1), Empty, (Piece Pawn P1), Empty],
          [Empty, Empty, Empty, Blank],
          [Blank, Empty, Empty, Empty],
          [Empty, (Piece Pawn P2), Empty, (Piece Queen P2)]]

getBoardPositions :: Board -> [Pos]
getBoardPositions x = [(a,b) | a <- [0..((length (x !! 0)) - 1)], b <- [0..((length x) - 1)], (((x !! b) !! a) /= Blank)]
-------------------- Moving

-- boardRemovePiece :: Board -> Pos -> Board
-- boardRemovePiece board x = 

moves:: Square ->[Pos]
moves (Piece Queen _) = [(i,i) | i <- [-10..10]]
moves (Piece Pawn P1) = [(-1,1),(1,1)]
moves (Piece Pawn P2) = [(-1,1),(1,1)]
moves _ = []

eats:: Square ->[Pos]
eats (Piece Queen _) = [(i,i) | i <- [-10..10]]
eats (Piece Pawn _) = [(-2,2),(2,2),(-2,-2),(2,-2)]
eats _ = []

getBoardSquare:: Pos -> Square
getBoardSquare (x,y) = (iBoard !! y) !! x

getOtherPlayer :: PiecePlayer -> PiecePlayer
getOtherPlayer P1 = P2
getOtherPlayer P2 = P1

getInterPos :: Pos -> Pos -> [Pos]
getInterPos (a, b) (c, d) = [(x, y) | x <- [a..c] ++ [c..a], y <- [b..d] ++ [d..b], (abs  (y - b)) == (abs $ (x - a))]

getValidMoves :: Pos -> [Pos]
getValidMoves pos = intersect (map (addPos pos) $ moves $ getBoardSquare pos) (getBoardPositions iBoard)

  
isValidMove:: Pos -> Pos -> Bool
isValidMove x y = elem y $ getValidMoves x
  
-- movePiece :: Board -> Pos -> Pos
-- movePiece board (a, b) (c, d) = if isValidMove (a,b) (c,d) then
--                         board !! a !! b 

main :: IO ()
main = do putStrLn $ prettyBoard iBoard
          print $ moves $ getBoardSquare (2,0)
          print $ getBoardPositions iBoard
          print $ getValidMoves (2,0)
