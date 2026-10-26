# 29. Coordinate Grid

## Mental Model

Call one function for every `[row column]` pair. Store its result at that coordinate.

## Relationship to Cognitive Verb

```text
Generate -> coordinate -> value rule
```

## Clojure Functions and Common Idioms

|Need|Use|
|---|---|
|Generate a matrix|nested `mapv`|
|Keep coordinates|return `[row column]`|
|Create row and column fields|return one coordinate|
|Create a mask|convert a predicate to `1` or `0`|
|Probe a transform|transform a coordinate grid|

## Common Uses

- Build test matrices.
- Create geometric masks.
- Generate distance fields.
- Debug rotations and flips.
- Create gradients and index maps.

## Hidden Interview Problems

- Preserve row-major loop order.
- Convert a distance rule to a mask.
- Divide a gradient by the span.
- Trace where a transform moves each source cell.

## Recognition Clues

Look for `value from position`, `coordinate field`, `mesh grid`, `mask`, or `procedural grid`.

## Pattern Summary

One generator captures the complete pattern. Identity and checkerboard matrices are special coordinate rules.

## Shape and Edge Behavior

- Grid dimensions must be finite nonnegative integers.
- A zero dimension produces no cells.
- Rotation requires a rectangular matrix.
- `grid-from-values` expects a finite value collection.

## Clojure Recipe Book

```clojure
(defn rectangular? [matrix]
  (or (empty? matrix)
      (apply = (map count matrix))))

(defn require-rectangular [matrix]
  (when-not (rectangular? matrix)
    (throw (ex-info "Matrix must be rectangular"
                    {:row-lengths (mapv count matrix)})))
  matrix)

(defn generate-grid [rows columns value-at]
  (when-not (and (not (neg? rows)) (not (neg? columns)))
    (throw (ex-info "Grid dimensions must not be negative" {})))
  (mapv (fn [row]
          (mapv (fn [column]
                  (value-at row column))
                (range columns)))
        (range rows)))

(defn coordinate-grid [rows columns]
  (generate-grid rows columns vector))

(defn row-grid [rows columns]
  (generate-grid rows columns (fn [row _] row)))

(defn column-grid [rows columns]
  (generate-grid rows columns (fn [_ column] column)))

(defn index-grid [rows columns]
  (generate-grid rows columns
                 (fn [row column]
                   (+ (* row columns) column))))

(defn distance-grid [rows columns center metric]
  (generate-grid
    rows
    columns
    (fn [row column]
      (let [row-change (- row (first center))
            column-change (- column (second center))]
        (case metric
          :manhattan (+ (abs row-change) (abs column-change))
          :chebyshev (max (abs row-change) (abs column-change))
          :euclidean (Math/sqrt
                       (double (+ (* row-change row-change)
                                  (* column-change column-change))))
          (throw (ex-info "Unknown distance metric" {:metric metric})))))))

(defn predicate-mask [rows columns predicate]
  (generate-grid rows columns
                 (fn [row column]
                   (if (predicate row column) 1 0))))

(defn border-mask [rows columns]
  (predicate-mask
    rows
    columns
    (fn [row column]
      (or (zero? row)
          (zero? column)
          (= row (dec rows))
          (= column (dec columns))))))

(defn x-mask [size]
  (predicate-mask size size
                  (fn [row column]
                    (or (= row column)
                        (= (+ row column) (dec size))))))

(defn horizontal-gradient [rows columns]
  (let [span (max 1 (dec columns))]
    (generate-grid rows columns
                   (fn [_ column]
                     (/ (double column) span)))))

(defn rotate-90 [matrix]
  (require-rectangular matrix)
  (if (empty? matrix)
    []
    (apply mapv vector (reverse matrix))))

(defn flip-horizontal [matrix]
  (mapv (comp vec reverse) matrix))

(defn grid-from-values [values width]
  (when-not (pos? width)
    (throw (ex-info "Width must be positive" {:width width})))
  (mapv vec (partition-all width values)))

(coordinate-grid 2 3)
;; => [[[0 0] [0 1] [0 2]] [[1 0] [1 1] [1 2]]]

(index-grid 3 4)
;; => [[0 1 2 3] [4 5 6 7] [8 9 10 11]]

(rotate-90 (coordinate-grid 2 3))
;; => [[[1 0] [0 0]] [[1 1] [0 1]] [[1 2] [0 2]]]

;; Executable checks

(assert (= [[[0 0] [0 1] [0 2]]
            [[1 0] [1 1] [1 2]]]
           (coordinate-grid 2 3)))
(assert (= [[0 1 2 3] [4 5 6 7] [8 9 10 11]]
           (index-grid 3 4)))
```

The row loop stays outside the column loop. Reversing those loops transposes the generated result.

### Memory Hooks

- One function defines every cell.
- Row varies slowly.
- Column varies quickly.
- Coordinate grids expose movement rules.

### Key Insight

Generate from coordinates instead of filling and mutating cells. This form is short, pure, and easy to test.

## Coordinate Grid vs the Rest

Identity, masks, gradients, distance fields, and checkerboards all use the same generator with different value rules.
