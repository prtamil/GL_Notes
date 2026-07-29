# Pattern 8 — Cartesian Product

## Mental Model

Generate **every possible combination** by pairing each element of one sequence with **every** element of another sequence.

---

## Relationship to Cognitive Verb

```text
Pair
   ↓
Cartesian Product
```

Cartesian Product is a **Pair** pattern that creates **all possible pairs**, not just corresponding or alternating ones.

---

## Clojure Functions & Common Idioms

|Variation|Example|Common Clojure|
|---|---|---|
|Cartesian Product (2 sequences)|`(1 a) (1 b) (2 a) (2 b)`|`for`|
|Cartesian Product (3 sequences)|`(1 a x) (1 a y) ...`|`for`|
|Pair then Transform|`(x y) → f(x,y)`|`for` + expression|
|Cartesian with Filter|Valid combinations only|`for :when`|
|Nested Iteration|Every outer × inner|`for` / nested `mapcat`|

---

## Common Uses

- Grid generation
    
- Chess board coordinates
    
- Game state generation
    
- Test case generation
    
- Password combinations
    
- Hyperparameter search
    
- SQL CROSS JOIN
    
- All pair comparisons
    
- Ray/object intersection tests
    

---

## Hidden Interview Problems

- Generate all pairs
    
- Generate all combinations of two arrays
    
- Sudoku coordinate generation
    
- Matrix coordinate traversal
    
- Compare every item with every other item
    
- Brute-force search
    
- CROSS JOIN implementation
    

---

## Recognition Clues

If you hear:

- Every possible combination
    
- All pairs
    
- Every X with every Y
    
- Cross join
    
- Nested loops
    
- Exhaustive search
    
- Grid coordinates
    
- Combinations of two lists
    

Think:

**→ Cartesian Product**

---

## Pattern Summary

| Property        | Value                          |
| --------------- | ------------------------------ |
| Cognitive Verb  | Pair                           |
| Pattern         | Cartesian Product              |
| Input           | Two or more sequences          |
| Output          | Every possible combination     |
| Pairing Rule    | Every element with every other |
| Complexity      | O(n × m)                       |
| Preserves Order | Yes (nested iteration order)   |
## Examples
```clojure
;; 1. Cartesian Product of Two Sequences

(for [x [1 2 3]
      y [:a :b]]
  [x y])

;; =>
([1 :a]
 [1 :b]
 [2 :a]
 [2 :b]
 [3 :a]
 [3 :b])


;; 2. Cartesian Product of Three Sequences

(for [x [1 2]
      y [:a :b]
      z [:x :y]]
  [x y z])

;; =>
([1 :a :x]
 [1 :a :y]
 [1 :b :x]
 [1 :b :y]
 [2 :a :x]
 [2 :a :y]
 [2 :b :x]
 [2 :b :y])


;; 3. Transform While Pairing

(for [x [1 2 3]
      y [10 20]]
  (+ x y))

;; =>
(11 21 12 22 13 23)


;; 4. Cartesian Product with Filtering

(for [x (range 5)
      y (range 5)
      :when (< x y)]
  [x y])

;; =>
([0 1]
 [0 2]
 [0 3]
 [0 4]
 [1 2]
 [1 3]
 [1 4]
 [2 3]
 [2 4]
 [3 4])


;; 5. Matrix Coordinates

(for [row (range 3)
      col (range 4)]
  [row col])

;; =>
([0 0] [0 1] [0 2] [0 3]
 [1 0] [1 1] [1 2] [1 3]
 [2 0] [2 1] [2 2] [2 3])


;; 6. Chess Board Coordinates

(for [file [:a :b :c]
      rank [1 2 3]]
  [file rank])

;; =>
([:a 1] [:a 2] [:a 3]
 [:b 1] [:b 2] [:b 3]
 [:c 1] [:c 2] [:c 3])
```
