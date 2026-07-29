# 2. Column Traversal

## Mental Model

Column traversal processes one complete column at a time before moving to the next column.

Unlike row traversal, columns are **not stored contiguously** in a typical row-major matrix, so accessing a column usually means visiting the same column index across all rows.

---

## Relationship to Cognitive Verb

```text
Visit
   ↓
Column Traversal
```

Related verbs:

- Visit each column
    
- Scan vertically
    
- Process column-by-column
    
- Aggregate columns
    
- Analyze vertical slices
    

---

## Clojure Functions & Common Idioms

|Variation|Example|Common Clojure|
|---|---|---|
|Iterate columns|process each column|`range`, `map`, `nth`|
|Transform columns|modify every column|`apply map`, `mapv`|
|Reduce columns|summarize columns|`reduce`|
|Index columns|need column number|`range`, `map-indexed`|
|Extract column|get one column|`map #(nth % c)`|
|Transpose first|convert columns to rows|`apply map vector`|

---

## Common Uses

- Spreadsheet column totals
    
- Database field analysis
    
- Image vertical scans
    
- Sudoku column validation
    
- Feature extraction in machine learning
    
- Histogram computation
    
- Sensor readings over time
    
- Vertical projections
    

---

## Hidden Interview Problems

- Sum every column
    
- Maximum per column
    
- Find empty columns
    
- Validate Sudoku columns
    
- Detect identical columns
    
- Normalize each column
    
- Count values per column
    
- Compute column averages
    

---

## Recognition Clues

If you hear...

- "for every column..."
    
- "scan vertically..."
    
- "column totals..."
    
- "analyze each field..."
    
- "process top to bottom..."
    

...think **Column Traversal**.

---

## Pattern Summary

|Property|Value|
|---|---|
|Dimension|2D|
|Traversal Unit|Column|
|Order|Top → Bottom, Left → Right|
|Cache Friendly|Usually No (row-major layouts)|
|Time Complexity|O(rows × cols)|
|Space Complexity|O(1) extra (streaming)|
|Common Domains|Tables, images, spreadsheets|

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
;; Visit every column

(doseq [c (range (count (first m)))]
  (println (map #(nth % c) m)))

;; =>
;; (1 4 7)
;; (2 5 8)
;; (3 6 9)

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;; Extract a single column

(map #(nth % 1) m)

;; => (2 5 8)

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;; Sum every column

(for [c (range (count (first m)))]
  (reduce + (map #(nth % c) m)))

;; => (12 15 18)

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;; Maximum in each column

(for [c (range (count (first m)))]
  (apply max (map #(nth % c) m)))

;; => (7 8 9)

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;; Average of each column

(for [c (range (count (first m)))]
  (let [col (map #(nth % c) m)]
    (/ (reduce + col)
       (count col))))

;; => (4 5 6)

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;; Access column index

(map
 (fn [c]
   {:column c
    :values (map #(nth % c) m)})
 (range (count (first m))))

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;; Transpose (columns become rows)

(apply map vector m)

;; =>
;; ((1 4 7)
;;  (2 5 8)
;;  (3 6 9))

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;; After transpose, process columns like rows

(map #(reduce + %) (apply map vector m))

;; => (12 15 18)

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;; Compare

;; Row traversal
(map f matrix)

;; Column traversal
(for [c (range cols)]
  (map #(nth % c) matrix))

;; Treat columns as rows
(apply map vector matrix)
```

---

## Key Insight

**A column is simply a vertical sequence.** Since Clojure matrices are typically represented as sequences of rows, column traversal is often implemented by **extracting the same index from every row**. If you need to perform many column-based operations, **transposing the matrix first** (`apply map vector`) lets you reuse all the familiar row-processing patterns from the previous lesson.

---



