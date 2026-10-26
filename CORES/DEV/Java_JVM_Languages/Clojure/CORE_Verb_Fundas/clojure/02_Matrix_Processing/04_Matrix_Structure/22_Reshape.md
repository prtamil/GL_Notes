# 22. Reshape

## Mental Model

Keep the row-major value order. Change only how those values are grouped into rows.

## Relationship to Cognitive Verb

```text
Regroup -> flatten -> partition by the new width
```

## Clojure Functions and Common Idioms

|Need|Use|
|---|---|
|Flatten one level|`into [] cat`|
|Create equal rows|`partition`|
|Allow a final short row|`partition-all`|
|Infer one dimension|divide the element count|
|Column-major reshape|map a column-major index|

## Common Uses

- Change tensor layout.
- Form batches.
- Convert a flat buffer to a grid.
- Prepare matrix data for another API.

## Hidden Interview Problems

- Reject a mismatched element count.
- Infer one missing dimension.
- Preserve row-major order.
- Distinguish reshape from transpose.

## Recognition Clues

Look for `same values`, `new dimensions`, `change shape`, or `regroup without reordering`.

## Pattern Summary

The old and new shapes must contain the same number of cells.

## Shape and Edge Behavior

- Row-major reshape accepts finite ragged input.
- Strict reshape requires an exact element count.
- Column-major reshape requires rectangular input.
- `as-grid` permits one short final row.

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

(defn flatten-matrix [matrix]
  (into [] cat matrix))

(defn reshape-values [values height width]
  (when-not (and (not (neg? height)) (pos? width))
    (throw (ex-info "Shape is invalid" {:height height :width width})))
  (when-not (= (count values) (* height width))
    (throw (ex-info "Element count does not match the shape"
                    {:elements (count values)
                     :height height
                     :width width})))
  (mapv vec (partition width values)))

(defn reshape [matrix height width]
  (reshape-values (flatten-matrix matrix) height width))

(defn reshape-auto [matrix height width]
  (let [values (flatten-matrix matrix)
        total (count values)]
    (cond
      (and (= :auto height) (= :auto width))
      (throw (ex-info "Only one dimension can be automatic" {}))

      (= :auto height)
      (do
        (when-not (and (pos? width) (zero? (mod total width)))
          (throw (ex-info "Width does not divide the element count" {})))
        (reshape-values values (quot total width) width))

      (= :auto width)
      (do
        (when-not (and (pos? height) (zero? (mod total height)))
          (throw (ex-info "Height does not divide the element count" {})))
        (reshape-values values height (quot total height)))

      :else
      (reshape-values values height width))))

(defn transpose [matrix]
  (require-rectangular matrix)
  (if (empty? matrix) [] (apply mapv vector matrix)))

(defn reshape-column-major [matrix height width]
  (require-rectangular matrix)
  (when-not (and (not (neg? height)) (pos? width))
    (throw (ex-info "Shape is invalid" {:height height :width width})))
  (let [values (into [] cat (transpose matrix))]
    (when-not (= (count values) (* height width))
      (throw (ex-info "Element count does not match the shape" {})))
    (mapv (fn [row]
            (mapv (fn [column]
                    (nth values (+ (* column height) row)))
                  (range width)))
          (range height))))

(defn as-grid [values width]
  (when-not (pos? width)
    (throw (ex-info "Width must be positive" {:width width})))
  (mapv vec (partition-all width values)))

(def matrix [[1 2 3] [4 5 6]])

(reshape matrix 3 2)
;; => [[1 2] [3 4] [5 6]]

(reshape-auto matrix :auto 2)
;; => [[1 2] [3 4] [5 6]]

(as-grid (range 7) 3)
;; => [[0 1 2] [3 4 5] [6]]

;; Executable checks

(assert (= [[1 2] [3 4] [5 6]] (reshape matrix 3 2)))
(assert (= [[1 2] [3 4] [5 6]]
           (reshape-auto matrix :auto 2)))
(assert (= [[0 1 2] [3 4 5] [6]] (as-grid (range 7) 3)))
```

`reshape` is strict. `as-grid` is the explicit choice when a short final row is valid.

### Memory Hooks

- Flatten first.
- Check the element count.
- Partition by the new width.
- Reshape groups values but does not move them.

### Key Insight

Reshape preserves linear order. Transpose changes positions and therefore changes that order.

## Reshape vs the Rest

Transforms move cells. Reshape changes grouping. Flatten removes one grouping level.
