# 5. Spiral Traversal

## Mental Model

Walk the outer ring clockwise. Move each boundary inward, then repeat.

## Relationship to Cognitive Verb

```text
Peel -> top -> right -> bottom -> left -> shrink
```

## Clojure Functions and Common Idioms

|Need|Use|
|---|---|
|Track four boundaries|`loop` and `recur`|
|Build a vector|`into`|
|Read the path only|generate coordinate pairs|
|Fill in spiral order|`reduce-kv` with `assoc-in`|

## Common Uses

- Print a matrix in spiral order.
- Fill a board by rings.
- Animate an inward scan.
- Process concentric layers.

## Hidden Interview Problems

- Handle one remaining row or column.
- Return each ring separately.
- Fill a matrix in spiral order.
- Walk an irregular board with direction vectors.

## Recognition Clues

Look for `spiral`, `rings`, `outer layer`, `clockwise`, or `shrink the bounds`.

## Pattern Summary

The state has four bounds. Guard the bottom and left edges to prevent duplicate cells.

## Shape and Edge Behavior

- Traversal expects a finite rectangular matrix.
- An empty matrix returns an empty traversal.
- Generation rejects negative dimensions.
- Traversal rejects ragged rows with `ExceptionInfo`.

## Clojure Recipe Book

```clojure
(defn rectangular? [matrix]
  (or (empty? matrix) (apply = (map count matrix))))

(defn ring-coordinates [top bottom left right]
  (cond
    (or (> top bottom) (> left right)) []
    (= top bottom)
    (mapv (fn [column] [top column])
          (range left (inc right)))
    (= left right)
    (mapv (fn [row] [row left])
          (range top (inc bottom)))
    :else
    (vec
      (concat
        (for [column (range left (inc right))]
          [top column])
        (for [row (range (inc top) (inc bottom))]
          [row right])
        (for [column (range (dec right) (dec left) -1)]
          [bottom column])
        (for [row (range (dec bottom) top -1)]
          [row left])))))

(defn spiral-rings [matrix]
  (when-not (rectangular? matrix)
    (throw (ex-info "Matrix must be rectangular" {})))
  (let [rows (count matrix)
        columns (if-let [row (first matrix)] (count row) 0)]
    (loop [top 0
           bottom (dec rows)
           left 0
           right (dec columns)
           result []]
      (if (or (> top bottom) (> left right))
        result
        (recur (inc top)
               (dec bottom)
               (inc left)
               (dec right)
               (conj result
                     (ring-coordinates top bottom left right)))))))

(defn spiral-coordinates [matrix]
  (into [] cat (spiral-rings matrix)))

(defn spiral-order [matrix]
  (mapv #(get-in matrix %) (spiral-coordinates matrix)))

(defn transpose [matrix]
  (when-not (rectangular? matrix)
    (throw (ex-info "Matrix must be rectangular"
                    {:row-lengths (mapv count matrix)})))
  (if (empty? matrix) [] (apply mapv vector matrix)))

(defn counter-clockwise-spiral [matrix]
  (spiral-order (transpose matrix)))

(defn spiral-fill [rows columns]
  (when (or (neg? rows) (neg? columns))
    (throw (ex-info "Matrix dimensions must not be negative"
                    {:rows rows :columns columns})))
  (let [blank (vec (repeat rows (vec (repeat columns nil))))
        path (spiral-coordinates blank)]
    (reduce-kv (fn [matrix index coordinate]
                 (assoc-in matrix coordinate (inc index)))
               blank
               path)))

(def matrix
  [[1  2  3  4]
   [5  6  7  8]
   [9 10 11 12]
   [13 14 15 16]])

(spiral-order matrix)
;; => [1 2 3 4 8 12 16 15 14 13 9 5 6 7 11 10]

(spiral-fill 3 3)
;; => [[1 2 3] [8 9 4] [7 6 5]]

;; Executable checks

(assert (= [1 2 3 4 8 12 16 15 14 13 9 5 6 7 11 10]
           (spiral-order matrix)))
(assert (= [[1 2 3] [8 9 4] [7 6 5]]
           (spiral-fill 3 3)))
```

The traversal returns `[]` for an empty matrix. It rejects ragged rows.

Use direction vectors when the path has holes or blocked cells. Fixed bounds suit a full rectangle.

### Memory Hooks

- Walk four edges.
- Guard thin final rings.
- Shrink all four bounds.
- Coordinates make traversal and filling reusable.

### Key Insight

Generate the path separately from the values. The same coordinate path can read, write, or animate the matrix.
