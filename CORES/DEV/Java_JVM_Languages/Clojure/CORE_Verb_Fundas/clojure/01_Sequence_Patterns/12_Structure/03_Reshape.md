# Pattern 36 — Reshape

## Mental Model

Change the **shape** of data without changing the values.

Unlike **Flatten**, which removes structure, **Reshape** reorganizes a linear sequence into a different structural layout.

---

## Relationship to Cognitive Verb

```text
Structure
     ↓
Reshape
```

Reshape is a **Structure** pattern because it changes **how data is organized**, not the data itself.

---

## Clojure Functions & Common Idioms

|Variation|Example|Common Clojure|
|---|---|---|
|1D → 2D|`[1 2 3 4] → [[1 2] [3 4]]`|`partition`|
|Fixed-size Rows|Chunks of N|`partition`|
|Partial Final Row|Keep remainder|`partition-all`|
|Flatten then Reshape|Change dimensions|`flatten` + `partition`|
|Matrix → Vector|2D → 1D|`flatten` / `mapcat identity`|
|Custom Reshape|Arbitrary layouts|`partition`, `split-at`, `reduce`|

> **Note:** Clojure has no general-purpose `reshape` like NumPy. The idiomatic approach is to combine `partition`, `partition-all`, `flatten`, and `mapcat`.

---

## Common Uses

- Matrix construction
    
- Image pixels
    
- CSV parsing
    
- Batch processing
    
- Neural network tensors
    
- Packet parsing
    
- Data chunking
    
- Grid generation
    

---

## Hidden Interview Problems

- Convert array to matrix
    
- Spiral matrix
    
- Chunk data
    
- Reshape image pixels
    
- Batch processing
    
- Grid generation
    

---

## Recognition Clues

If you hear:

- Reshape
    
- Matrix
    
- Rows and columns
    
- Chunk into groups
    
- Convert to grid
    
- Batch size
    
- Change dimensions
    

Think:

**→ Reshape**

---

## Pattern Summary

|Property|Value|
|---|---|
|Cognitive Verb|Structure|
|Pattern|Reshape|
|Input|Linear or nested sequence|
|Output|Different structural layout|
|Preserves Values|Yes|
|Primary Use|Change organization|

---

## Clojure Recipe Book

```clojure
;;--------------------------------------------------------
;; Input
;;--------------------------------------------------------

(def xs (range 1 13))

;; =>
(1 2 3 4 5 6 7 8 9 10 11 12)


;;--------------------------------------------------------
;; 1D -> 2D Matrix
;;--------------------------------------------------------

(partition 3 xs)

;; =>
((1 2 3)
 (4 5 6)
 (7 8 9)
 (10 11 12))


;;--------------------------------------------------------
;; Partial Final Row
;;--------------------------------------------------------

(partition-all 5 xs)

;; =>
((1 2 3 4 5)
 (6 7 8 9 10)
 (11 12))


;;--------------------------------------------------------
;; Matrix -> Vector
;;--------------------------------------------------------

(flatten
 [[1 2 3]
  [4 5 6]])

;; =>
(1 2 3 4 5 6)


;;--------------------------------------------------------
;; One-Level Flatten
;;--------------------------------------------------------

(mapcat identity
        [[1 2 3]
         [4 5 6]])

;; =>
(1 2 3 4 5 6)


;;--------------------------------------------------------
;; Flatten Then Reshape
;;--------------------------------------------------------

(->> [[1 2]
      [3 4]
      [5 6]]
     flatten
     (partition 3))

;; =>
((1 2 3)
 (4 5 6))


;;--------------------------------------------------------
;; Reshape Characters
;;--------------------------------------------------------

(partition 4
           "abcdefghijkl")

;; =>
((\a \b \c \d)
 (\e \f \g \h)
 (\i \j \k \l))


;;--------------------------------------------------------
;; Batch Processing
;;--------------------------------------------------------

(partition-all 100 records)

;; =>
;; ((100 records)
;;  (100 records)
;;  (remaining records))


;;--------------------------------------------------------
;; Build a 3x4 Matrix
;;--------------------------------------------------------

(->> (range 12)
     (partition 4))

;; =>
((0 1 2 3)
 (4 5 6 7)
 (8 9 10 11))


;;--------------------------------------------------------
;; Compare Flatten vs Reshape
;;--------------------------------------------------------

(flatten
 [[1 2]
  [3 4]])

;; =>
(1 2 3 4)

(partition 2
           [1 2 3 4])

;; =>
((1 2)
 (3 4))
```