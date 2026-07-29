# Part 2 — Matrix Patterns

# 1. Row Traversal

## Mental Model

A matrix is often treated as a collection of rows. Row traversal means processing one complete row at a time before moving to the next.

This is the most natural traversal order because most programming languages store 2D arrays in **row-major order**, making it cache-friendly and easy to reason about.

---

## Relationship to Cognitive Verb

```text
Visit
   ↓
Row Traversal
```

Related verbs:

- Visit each row
    
- Process row-by-row
    
- Scan rows
    
- Iterate rows
    
- Aggregate rows
    

---

## Clojure Functions & Common Idioms

|Variation|Example|Common Clojure|
|---|---|---|
|Iterate rows|process each row|`doseq`, `map`|
|Transform rows|modify every row|`map`|
|Filter rows|keep matching rows|`filter`|
|Reduce rows|summarize rows|`reduce`|
|Index rows|need row number|`map-indexed`|
|Nested traversal|visit every cell|nested `map`, nested `doseq`, `for`|

---

## Common Uses

- Spreadsheet processing
    
- CSV tables
    
- Database result sets
    
- Image scanlines
    
- Tile maps
    
- Heatmaps
    
- Neural network weight matrices
    
- Matrix printing
    
- Row statistics
    

---

## Hidden Interview Problems

- Sum each row
    
- Maximum value per row
    
- Count occurrences in each row
    
- Detect empty rows
    
- Normalize every row
    
- Find row with largest sum
    
- Validate Sudoku rows
    
- Compress rows
    

---

## Recognition Clues

If you hear...

- "for every row..."
    
- "each record..."
    
- "scan line by line..."
    
- "process one row at a time..."
    
- "calculate row totals..."
    

...think **Row Traversal**.

---

## Pattern Summary

|Property|Value|
|---|---|
|Dimension|2D|
|Traversal Unit|Row|
|Order|Left → Right, Top → Bottom|
|Cache Friendly|Yes (row-major layouts)|
|Time Complexity|O(rows × cols)|
|Space Complexity|O(1) extra (typically)|
|Common Domains|Images, tables, grids|

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
;; Visit every row

(doseq [row m]
  (println row))

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;; Transform every row

(map #(map inc %) m)

;; =>
;; ((2 3 4)
;;  (5 6 7)
;;  (8 9 10))

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;; Sum every row

(map #(reduce + %) m)

;; => (6 15 24)

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;; Maximum in each row

(map #(apply max %) m)

;; => (3 6 9)

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;; Count elements satisfying a condition

(map #(count (filter even? %)) m)

;; => (1 2 1)

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;; Access row index

(map-indexed
  (fn [i row]
    {:row i
     :sum (reduce + row)})
  m)

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;; Nested traversal (row then cell)

(doseq [row m
        cell row]
  (println cell))

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;; Same using for

(for [row m
      cell row]
  (* cell 2))

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;; Reduce across rows

(reduce
  (fn [acc row]
    (+ acc (reduce + row)))
  0
  m)

;; => 45

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;; Compare

;; Row traversal
(map f matrix)

;; Cell traversal
(mapcat identity matrix)
;; or nested map/doseq/for

;; Row reduction
(map #(reduce op %) matrix)

;; Whole matrix reduction
(reduce ...)
```

---

### Key Insight

**A row is the 2D equivalent of a sequence.** Most row-based algorithms simply apply familiar 1D sequence patterns (map, filter, reduce, partition, summarize, etc.) independently to each row before combining results if needed.
