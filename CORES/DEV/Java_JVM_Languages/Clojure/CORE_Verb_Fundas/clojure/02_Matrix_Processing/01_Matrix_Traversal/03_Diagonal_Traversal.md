# 3. Diagonal Traversal

## Mental Model

Diagonal traversal visits cells where the **row and column indices change together**. The most common diagonal is the **main diagonal**, running from the top-left to the bottom-right.

Unlike rows or columns, a diagonal represents a **relationship between coordinates**, not a contiguous row or column.

---

## Relationship to Cognitive Verb

```text
Trace
   ↓
Diagonal Traversal
```

Related verbs:

- Trace a diagonal
    
- Follow a diagonal
    
- Scan diagonally
    
- Visit matching coordinates
    
- Compare corresponding positions
    

---

## Clojure Functions & Common Idioms

|Variation|Example|Common Clojure|
|---|---|---|
|Main diagonal|`(0,0) → (n,n)`|`range`, `nth`|
|Offset diagonal|above/below main|`range` with offset|
|Collect diagonal|build sequence|`map`|
|Reduce diagonal|sum/product|`reduce`|
|Indexed traversal|explicit `(r,c)`|`map vector`|

---

## Common Uses

- Matrix trace
    
- Identity matrix checks
    
- Symmetric matrix algorithms
    
- Tic-Tac-Toe winner detection
    
- Image edge detection
    
- Dynamic programming tables
    
- Game board evaluation
    
- Computer vision
    

---

## Hidden Interview Problems

- Print the main diagonal
    
- Sum the diagonal
    
- Product of diagonal elements
    
- Check identity matrix
    
- Check symmetry
    
- Difference between diagonals
    
- Diagonal averages
    
- Traverse all diagonals
    

---

## Recognition Clues

If you hear...

- "top-left to bottom-right..."
    
- "main diagonal..."
    
- "matching row and column..."
    
- "where row equals column..."
    
- "principal diagonal..."
    

...think **Diagonal Traversal**.

---

## Pattern Summary

|Property|Value|
|---|---|
|Dimension|2D|
|Traversal Unit|Diagonal|
|Direction|Top-Left → Bottom-Right|
|Coordinate Rule|`row == col`|
|Time Complexity|O(min(rows, cols))|
|Space Complexity|O(1) extra|
|Common Domains|Linear algebra, games, graphics|

---

## Clojure Recipe Book

```clojure
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;; Basic matrix

(def m
  [[1 2 3]
   [4 5 6]
   [7 8 9]])

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;; Main diagonal

(map
 #(nth (nth m %) %)
 (range (min (count m)
             (count (first m)))))

;; => (1 5 9)

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;; Sum of main diagonal

(reduce +
        (map #(nth (nth m %) %)
             (range 3)))

;; => 15

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;; Product of main diagonal

(reduce *
        (map #(nth (nth m %) %)
             (range 3)))

;; => 45

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;; Row/Column coordinate pairs

(map vector
     (range 3)
     (range 3))

;; => ([0 0] [1 1] [2 2])

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;; Access using coordinate pairs

(map
 (fn [[r c]]
   (get-in m [r c]))
 (map vector
      (range 3)
      (range 3)))

;; => (1 5 9)

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;; Offset diagonal (one above)

(map
 #(get-in m [% (inc %)])
 (range 2))

;; => (2 6)

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;; Offset diagonal (one below)

(map
 #(get-in m [(inc %) %])
 (range 2))

;; => (4 8)

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;; Compare

;; Row traversal
(row, all columns)

;; Column traversal
(all rows, column)

;; Diagonal traversal
(row i, column i)

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;; Generic pattern

(for [i (range (min rows cols))]
  (get-in matrix [i i]))
```

---

## Key Insight

**A diagonal is defined by a coordinate relationship, not by physical storage.** The main diagonal follows the simple rule:

```text
(row, col)

(0,0)
(1,1)
(2,2)
(3,3)
...
```

Whenever the **row index and column index increase together**, you're traversing the main diagonal. This pattern appears frequently in linear algebra, board games, image processing, and dynamic programming.

---
