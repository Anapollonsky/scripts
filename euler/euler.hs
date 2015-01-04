{-# OPTIONS_GHC -fno-warn-missing-signatures #-}
module Main where
import qualified Data.Map as Map
import Data.List
import Data.Maybe
import Data.Char

---------------------------------------- 2
fibs = 0 : 1 : zipWith (+) fibs (tail fibs)

fibs2 = (map fib [0 ..] !!)
  where fib 0 = 0
        fib 1 = 1
        fib n = fibs2 (n-2) + fibs2 (n-1)

evenfibs = [i | i <- fibs, even i]
oddfibs = [i | i <- fibs, odd i]
num2 = sum (takeWhile (<4000000) evenfibs)

---------------------------------------- 12
trianglenums = 1 : 3 :  zipWith (+) (tail trianglenums) [3..]
intSqrRt = floor . sqrt . fromIntegral

factorize :: Int -> [Int]
factorize n = lows ++ (reverse $ map (div n) lows)
  where lows = filter ((==0) . mod n) [1 .. intSqrRt n]

num12 = fromJust $ find (\n -> length (factorize n) >= 500) trianglenums

---------------------------------------- 16
num2dig :: Integral x => x -> [x]
num2dig = reverse . num2dighelp

num2dighelp :: Integral x => x -> [x]
num2dighelp 0 = []
num2dighelp x = x `mod` 10 : num2dighelp (x `div` 10)

num16 = sum ( num2dig .  floor $ 2 ** 1000)

---------------------------------------- 25
num25 = fromJust $ findIndex (\x -> length (num2dig x) >= 1000) fibs

---------------------------------------- 29
num29 = length $ nub [a ^ b | a <- [2..100], b <- [2..100]]

---------------------------------------- 35  ot fast enough
-- generate primes
-- http://www.cs.hmc.edu/~oneill/papers/Sieve-JFP.pdf
sieve xs = sieve' xs Map.empty
  where
    sieve' [] table = []
    sieve' (x:xs) table =
      case Map.lookup x table of
        Nothing -> x : sieve' xs (Map.insert (x*x) [x] table)
        Just facts -> sieve' xs (foldl reinsert (Map.delete x table) facts)
      where
        reinsert table prime = Map.insertWith (++) (x + prime) [prime] table

primes = sieve [2..]

-- rotate a list
rotatelistright :: Int -> [a] -> [a]
rotatelistright l x = drop l x ++ take l x

-- digit list to integer
dig2num :: [Int] -> Int
dig2num [] = 0
dig2num x = last x + 10 * dig2num ( init x)

-- generate list of rotations of a list
genlistrots :: [a] -> [[a]]
genlistrots x = [rotatelistright i x | i <- [1 .. (length x) ]]

-- generate list of rotations of integer
gennumrots :: Int -> [Int]
gennumrots x = map dig2num $ genlistrots $ num2dig x

-- check if number is prime
isprime :: Int -> Bool
isprime x = last (takeWhile ( <= x) primes) == x

-- generate list of circular primes
circprimes = [x | x <- primes, notElem 5 (num2dig x), notElem 2 (num2dig x), all isprime (gennumrots x)]
-- circprimes = [x | x <- primes, all isprime (gennumrots x)]
num35 = length $ takeWhile (<10000) circprimes

---------------------------------------- 39
righttriangleperim :: Int -> Int
righttriangleperim x = length [1 | a <- [1..quot x 2], b <- [1..a], a ^ 2 + b ^ 2 == (x-a-b) ^ 2]

righttriangleperimlengths = [righttriangleperim x | x <- [1..1000]]
num39 = 1 + ( fromJust $ elemIndex (maximum righttriangleperimlengths) righttriangleperimlengths)

---------------------------------------- 48
num48 = dig2num . reverse . take 10 . reverse . num2dig $ sum [a^a|a<-[1..1000]]

---------------------------------------- 56
digsum = [sum $ num2dig (a ^ b) | a<-[1..100], b <- [1..100]]
num56 = maximum digsum

---------------------------------------- 74
factorial :: Int -> Int
factorial x = product [1..x]

digFacSum :: Int -> Int
digFacSum = sum . map factorial . num2dig

checknum74 :: Int -> [Int] -> Int
checknum74 x xs =
  if x `elem` xs
  then length xs
  else checknum74 (digFacSum x) (x:xs)

num74 = length [1 | x <- [1..1000000], checknum74 x [] == 60]

---------------------------------------- 112




pfactorize :: Int -> [Int]
pfactorize 1 = []
pfactorize x = n : (pfactorize $ quot x n)
  where
    n = fromJust (find (\k -> rem x k == 0) primes) :: Int

upfactorize = nub . pfactorize

main = print num39
