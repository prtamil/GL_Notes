# Pattern 35 — Transpose

## Mental Model

Swap **rows and columns** of a 2D sequence.

A Transpose changes the **orientation** of data without changing the values.

---

## Relationship to Cognitive Verb

```text
Structure
     ↓
Transpose
```

Transpose is a **Structure** pattern because it reorganizes the layout of data from **row-major** to **column-major** (or vice versa).

---

## Clojure Functions & Common Idioms

|Variation|Example|Common Clojure|
|---|---|---|
|Matrix Transpose|Rows ↔ Columns|`apply mapv vector`|
|Lazy Transpose|Sequence output|`apply map list`|
|Zip as Transpose|2 rows → columns|`apply map vector`|
|Transpose then Process|Column operations|`->>` + `apply mapv vector`|
|Unzip|Inverse of zip|`apply map vector`|

> **Note:** Clojure has no built-in `transpose`. Use `apply mapv vector`.

---

## Common Uses

- Matrix operations
    
- CSV processing
    
- Pivot tables
    
- Column-wise statistics
    
- Graphics transformations
    
- Machine learning datasets
    
- DataFrame operations
    
- Image processing
    

---

## Hidden Interview Problems

- Matrix transpose
    
- Rotate image
    
- Zip/unzip arrays
    
- Pivot table
    
- Column sums
    
- Spreadsheet transformations
    

---

## Recognition Clues

If you hear:

- Rows to columns
    
- Columns to rows
    
- Pivot
    
- Matrix transpose
    
- Flip across diagonal
    
- Column-wise processing
    
- Unzip
    

Think:

**→ Transpose**

---

## Pattern Summary

|Property|Value|
|---|---|
|Cognitive Verb|Structure|
|Pattern|Transpose|
|Input|2D sequence|
|Output|Rows become columns|
|Preserves Values|Yes|
|Primary Use|Matrix reorganization|

---

## Clojure Recipe Book

```clojure
;;--------------------------------------------------------
;; Matrix
;;--------------------------------------------------------

(def m
  [[1 2 3]
   [4 5 6]
   [7 8 9]])


;;--------------------------------------------------------
;; Basic Transpose
;;--------------------------------------------------------

(apply mapv vector m)

;; =>
;; [[1 4 7]
 ;; [2 5 8]
 ;; [3 6 9]]


;;--------------------------------------------------------
;; Lazy Version
;;--------------------------------------------------------

(apply map list m)

;; =>
;; ((1 4 7)
 ;; (2 5 8)
 ;; (3 6 9))


;;--------------------------------------------------------
;; Two Rows -> Columns (Zip)
;;--------------------------------------------------------

(apply mapv vector
       [[1 2 3]
        [:a :b :c]])

;; =>
;; [[1 :a]
 ;; [2 :b]
 ;; [3 :c]]


;;--------------------------------------------------------
;; Unzip
;;--------------------------------------------------------

(apply mapv vector
       [[1 :a]
        [2 :b]
        [3 :c]])

;; =>
;; [[1 2 3]
 ;; [:a :b :c]]


;;--------------------------------------------------------
;; Column Sums
;;--------------------------------------------------------

(map #(reduce + %)
     (apply mapv vector m))

;; =>
;; (12 15 18)


;;--------------------------------------------------------
;; Column Maximums
;;--------------------------------------------------------

(map #(apply max %)
     (apply mapv vector m))

;; =>
;; (7 8 9)


;;--------------------------------------------------------
;; Matrix + Transpose
;;--------------------------------------------------------

(map vector
     m
     (apply mapv vector m))

;; =>
;; ([[1 2 3] [1 4 7]]
 ;; [[4 5 6] [2 5 8]]
 ;; [[7 8 9] [3 6 9]])


;;--------------------------------------------------------
;; Transpose Characters
;;--------------------------------------------------------

(apply mapv str
       ["CAT"
        "DOG"
        "PIG"])

;; =>
;; ["CDP"
 ;; "AOI"
 ;; "TGG"]


;;--------------------------------------------------------
;; Transpose Then Flatten
;;--------------------------------------------------------

(->> m
     (apply mapv vector)
     flatten)

;; =>
;; (1 4 7 2 5 8 3 6 9)
```

---

### Readable Clojure Functions

```clojure
(defn rectangular? [matrix]
  (or (empty? matrix)
      (apply = (map count matrix))))

(defn transpose [matrix]
  (if (empty? matrix)
    []
    (apply mapv vector matrix)))

(defn transpose-strict [matrix]
  (when-not (rectangular? matrix)
    (throw (ex-info "Cannot transpose a ragged matrix"
                    {:row-lengths (mapv count matrix)})))
  (transpose matrix))

(defn column-sums [matrix]
  (mapv #(reduce + 0 %)
        (transpose-strict matrix)))

(defn records->columns [records]
  (if-let [record (first records)]
    (into {}
          (map (fn [key]
                 [key (mapv key records)]))
          (keys record))
    {}))

(defn rotate-clockwise [matrix]
  (transpose-strict (reverse matrix)))

(defn rotate-counter-clockwise [matrix]
  (mapv (comp vec reverse)
        (transpose-strict matrix)))

(transpose [[1 2 3]
            [4 5 6]])
;; => [[1 4] [2 5] [3 6]]

(column-sums [[1 2 3]
              [4 5 6]])
;; => [5 7 9]

(records->columns [{:id 1 :name "Ana"}
                   {:id 2 :name "Bo"}])
;; => {:id [1 2], :name ["Ana" "Bo"]}

(rotate-clockwise [[1 2 3]
                   [4 5 6]
                   [7 8 9]])
;; => [[7 4 1] [8 5 2] [9 6 3]]
```

`apply map vector` silently truncates to the shortest row. That is sometimes useful for zipping, but dangerous for matrices, so the reusable matrix function validates rectangularity first.

### Memory Hooks

|You want|You reach for|
|---|---|
|rows become columns|`apply mapv vector`|
|reject ragged data|compare all row counts first|
|unzip pairs|the same transpose operation|
|column summaries|transpose, then reuse row functions|
|records to columns|one vector per map key|
|90° rotation|transpose plus reversal|

### Key Insight

Transpose exchanges structural roles. It does not change values. The zip operation stops at the shortest row. A strict matrix function must reject ragged rows.
