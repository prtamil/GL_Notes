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
;; (1 2 3 4 5 6 7 8 9 10 11 12)


;;--------------------------------------------------------
;; 1D -> 2D Matrix
;;--------------------------------------------------------

(partition 3 xs)

;; =>
;; ((1 2 3)
 ;; (4 5 6)
 ;; (7 8 9)
 ;; (10 11 12))


;;--------------------------------------------------------
;; Partial Final Row
;;--------------------------------------------------------

(partition-all 5 xs)

;; =>
;; ((1 2 3 4 5)
 ;; (6 7 8 9 10)
 ;; (11 12))


;;--------------------------------------------------------
;; Matrix -> Vector
;;--------------------------------------------------------

(flatten
 [[1 2 3]
  [4 5 6]])

;; =>
;; (1 2 3 4 5 6)


;;--------------------------------------------------------
;; One-Level Flatten
;;--------------------------------------------------------

(mapcat identity
        [[1 2 3]
         [4 5 6]])

;; =>
;; (1 2 3 4 5 6)


;;--------------------------------------------------------
;; Flatten Then Reshape
;;--------------------------------------------------------

(->> [[1 2]
      [3 4]
      [5 6]]
     flatten
     (partition 3))

;; =>
;; ((1 2 3)
 ;; (4 5 6))


;;--------------------------------------------------------
;; Reshape Characters
;;--------------------------------------------------------

(partition 4
           "abcdefghijkl")

;; =>
;; ((\a \b \c \d)
 ;; (\e \f \g \h)
 ;; (\i \j \k \l))


;;--------------------------------------------------------
;; Batch Processing
;;--------------------------------------------------------

(def sample-records
  (mapv (fn [id] {:id id}) (range 230)))

(map count (partition-all 100 sample-records))

;; => (100 100 30)


;;--------------------------------------------------------
;; Build a 3x4 Matrix
;;--------------------------------------------------------

(->> (range 12)
     (partition 4))

;; =>
;; ((0 1 2 3)
 ;; (4 5 6 7)
 ;; (8 9 10 11))


;;--------------------------------------------------------
;; Compare Flatten vs Reshape
;;--------------------------------------------------------

(flatten
 [[1 2]
  [3 4]])

;; =>
;; (1 2 3 4)

(partition 2
           [1 2 3 4])

;; =>
;; ((1 2)
 ;; (3 4))
```

---

### Readable Clojure Functions

```clojure
(defn require-positive-dimension [label value]
  (when-not (pos? value)
    (throw (ex-info (str label " must be positive") {label value})))
  value)

(defn reshape [rows columns collection]
  (require-positive-dimension :rows rows)
  (require-positive-dimension :columns columns)
  (let [values (vec collection)
        expected (* rows columns)]
    (when-not (= expected (count values))
      (throw (ex-info "Shape does not match element count"
                      {:shape [rows columns]
                       :expected expected
                       :actual (count values)})))
    (mapv vec (partition columns values))))

(defn partition-all-v [width values]
  (require-positive-dimension :width width)
  (mapv vec (partition-all width values)))

(defn reshape-padded [columns fill-value collection]
  (require-positive-dimension :columns columns)
  (let [values (vec collection)
        missing (mod (- columns (mod (count values) columns))
                     columns)]
    (mapv vec
          (partition columns
                     (concat values (repeat missing fill-value))))))

(defn reshape-infer-rows [columns collection]
  (require-positive-dimension :columns columns)
  (let [values (vec collection)]
    (when-not (zero? (mod (count values) columns))
      (throw (ex-info "Column count does not divide element count"
                      {:columns columns
                       :elements (count values)})))
    (reshape (quot (count values) columns)
             columns
             values)))

(defn reshape-column-major [rows columns values]
  (let [columns-first (reshape columns rows values)]
    (if (empty? columns-first)
      []
      (apply mapv vector columns-first))))

(defn grid-index [columns row column]
  (require-positive-dimension :columns columns)
  (+ (* row columns) column))

(defn grid-coordinate [columns index]
  (require-positive-dimension :columns columns)
  [(quot index columns) (mod index columns)])

(reshape 3 4 (range 12))
;; => [[0 1 2 3] [4 5 6 7] [8 9 10 11]]

(partition-all-v 5 (range 12))
;; => [[0 1 2 3 4] [5 6 7 8 9] [10 11]]

(reshape-padded 5 :missing (range 12))
;; => [[0 1 2 3 4] [5 6 7 8 9] [10 11 :missing :missing :missing]]

(reshape-column-major 3 4 (range 12))
;; => [[0 3 6 9] [1 4 7 10] [2 5 8 11]]
```

Persistent nested vectors do not provide NumPy-style zero-copy reshape. These functions construct new row vectors. Part 3 introduces typed tensor buffers where shape metadata and storage layout are separate concerns.

### Memory Hooks

|You want|You reach for|
|---|---|
|fixed-width rows, dropping an incomplete tail|`partition`|
|keep an incomplete tail|`partition-all`|
|pad an incomplete tail|append fills, then `partition`|
|exact target shape|validate element count first|
|infer row count|divide total by column count|
|column-major fill|form columns, then transpose|
|flat ↔ grid coordinates|quotient and remainder|

### Key Insight

Reshape preserves element order while changing boundaries. Decide explicitly what happens to an incomplete final group—reject it, keep it short, drop it, or pad it. Those policies are different algorithms and deserve different names.
