# 4. Anti-Diagonal Traversal

## Mental Model

Anti-diagonal traversal visits cells where the **row index increases while the column index decreases**. It follows the diagonal from the **top-right corner** to the **bottom-left corner**.

Like the main diagonal, this is defined by a **coordinate relationship**, not by how the matrix is stored.

---

## Relationship to Cognitive Verb

```text
Trace
   ↓
Anti-Diagonal Traversal
```

Related verbs:

- Trace the opposite diagonal
    
- Follow the reverse diagonal
    
- Scan diagonally
    
- Visit mirrored coordinates
    
- Compare opposite corners
    

---

## Clojure Functions & Common Idioms

|Variation|Example|Common Clojure|
|---|---|---|
|Main anti-diagonal|`(0,n-1) → (n-1,0)`|`range`, `get-in`|
|Offset anti-diagonal|adjacent diagonals|`range` with offset|
|Collect anti-diagonal|build sequence|`map`|
|Reduce anti-diagonal|sum/product|`reduce`|
|Indexed traversal|explicit `(r,c)`|`map vector`|

---

## Common Uses

- Tic-Tac-Toe winner detection
    
- Matrix symmetry checks
    
- Image processing
    
- Dynamic programming
    
- Chess and board games
    
- Computer vision
    
- Heatmap analysis
    
- Matrix puzzles
    

---

## Hidden Interview Problems

- Print the anti-diagonal
    
- Sum the anti-diagonal
    
- Compare both diagonals
    
- Check X-patterns
    
- Difference of diagonal sums
    
- Find diagonal maximum
    
- Detect anti-diagonal symmetry
    
- Traverse all anti-diagonals
    

---

## Recognition Clues

If you hear...

- "top-right to bottom-left..."
    
- "secondary diagonal..."
    
- "opposite diagonal..."
    
- "reverse diagonal..."
    
- "mirror diagonal..."
    

...think **Anti-Diagonal Traversal**.

---

## Pattern Summary

|Property|Value|
|---|---|
|Dimension|2D|
|Traversal Unit|Anti-Diagonal|
|Direction|Top-Right → Bottom-Left|
|Coordinate Rule|`row + col == n - 1` (square matrix)|
|Time Complexity|O(min(rows, cols))|
|Space Complexity|O(1) extra|
|Common Domains|Games, graphics, linear algebra|

---

## Clojure Recipe Book

```clojure
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;; Basic matrix

(def m
  [[1 2 3]
   [4 5 6]
   [7 8 9]])

(def n (count m))

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;; Main anti-diagonal

(map
 #(get-in m [% (- n 1 %)])
 (range n))

;; => (3 5 7)

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;; Sum of anti-diagonal

(reduce +
        (map #(get-in m [% (- n 1 %)])
             (range n)))

;; => 15

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;; Product of anti-diagonal

(reduce *
        (map #(get-in m [% (- n 1 %)])
             (range n)))

;; => 105

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;; Coordinate pairs

(map vector
     (range n)
     (reverse (range n)))

;; => ([0 2] [1 1] [2 0])

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;; Access using coordinate pairs

(map
 (fn [[r c]]
   (get-in m [r c]))
 (map vector
      (range n)
      (reverse (range n))))

;; => (3 5 7)

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;; Offset anti-diagonal (one inward)

(map
 #(get-in m [% (- n 2 %)])
 (range (dec n)))

;; => (2 4)

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;; Compare

;; Main diagonal
(get-in matrix [i i])

;; Anti-diagonal
(get-in matrix [i (- n 1 i)])

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;; Generic pattern

(for [i (range (min rows cols))]
  (get-in matrix [i (- cols 1 i)]))
```

---

## Key Insight

An anti-diagonal follows the simple coordinate rule:

```text
(row, col)

(0, n-1)
(1, n-2)
(2, n-3)
...
(n-1, 0)
```

Equivalently, in a square matrix:

```text
row + col = n - 1
```

Notice the contrast with the main diagonal:

|Traversal|Coordinate Rule|
|---|---|
|Main Diagonal|`row == col`|
|Anti-Diagonal|`row + col == n - 1`|

The anti-diagonal is essentially the **mirror image** of the main diagonal. Whenever one index increases while the other decreases, you're traversing an anti-diagonal.
