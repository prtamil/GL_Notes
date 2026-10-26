# 23. Flatten

## Mental Model

Read rows from top to bottom. Read each row from left to right and remove one grouping level.

## Relationship to Cognitive Verb

```text
Linearize -> matrix rows -> one row-major vector
```

## Clojure Functions and Common Idioms

|Need|Use|
|---|---|
|Eager vector|`into [] cat`|
|Lazy values|`mapcat identity`|
|Index conversion|`quot` and `mod`|
|Deep sequential data|recursive `sequential?` test|
|Restore rows|`partition` or reshape|

## Common Uses

- Serialize a matrix.
- Apply one-dimensional algorithms.
- Compare matrix contents in row-major order.
- Search a globally sorted matrix.

## Hidden Interview Problems

- Convert coordinates to flat indexes.
- Convert flat indexes to coordinates.
- Distinguish row-major and column-major order.
- Flatten nested sequential data.

## Recognition Clues

Look for `one sequence`, `linear index`, `serialize`, `row-major`, or `remove nesting`.

## Pattern Summary

One-level flatten preserves all values and row-major order. It removes only the row boundary.

## Shape and Edge Behavior

- Row-major flatten accepts finite ragged input.
- Column-major work and matrix search require rectangular input.
- Index conversion requires a positive column count.
- Strict unflatten rejects a short final row.

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

(defn lazy-matrix-values [matrix]
  (mapcat identity matrix))

(defn coordinate->index [[row column] columns]
  (when-not (and (pos? columns) (<= 0 row) (<= 0 column) (< column columns))
    (throw (ex-info "Coordinate or column count is invalid"
                    {:coordinate [row column] :columns columns})))
  (+ (* row columns) column))

(defn index->coordinate [index columns]
  (when-not (and (<= 0 index) (pos? columns))
    (throw (ex-info "Index or column count is invalid"
                    {:index index :columns columns})))
  [(quot index columns) (mod index columns)])

(defn column-major-values [matrix]
  (require-rectangular matrix)
  (if (empty? matrix)
    []
    (into [] cat (apply mapv vector matrix))))

(defn find-in-sorted-matrix [matrix target]
  (require-rectangular matrix)
  (let [values (flatten-matrix matrix)
        columns (if-let [row (first matrix)] (count row) 0)]
    (loop [low 0
           high (dec (count values))]
      (when (<= low high)
        (let [middle (quot (+ low high) 2)
              value (nth values middle)]
          (cond
            (= value target) (index->coordinate middle columns)
            (< value target) (recur (inc middle) high)
            :else (recur low (dec middle))))))))

(defn deep-flatten [value]
  (letfn [(walk [item]
            (lazy-seq
              (if (sequential? item)
                (mapcat walk item)
                (list item))))]
    (vec (walk value))))

(defn unflatten [values columns]
  (when-not (pos? columns)
    (throw (ex-info "Column count must be positive" {:columns columns})))
  (when-not (zero? (mod (count values) columns))
    (throw (ex-info "Element count must be divisible by columns"
                    {:elements (count values) :columns columns})))
  (mapv vec (partition columns values)))

(def matrix [[1 2 3] [4 5 6]])

(flatten-matrix matrix)
;; => [1 2 3 4 5 6]

(column-major-values matrix)
;; => [1 4 2 5 3 6]

(find-in-sorted-matrix [[1 3 5] [7 9 11]] 9)
;; => [1 1]

(deep-flatten [1 [2 [3 4]]])
;; => [1 2 3 4]

;; Executable checks

(assert (= [1 2 3 4 5 6] (flatten-matrix matrix)))
(assert (= [1 4 2 5 3 6] (column-major-values matrix)))
(assert (= [1 1]
           (find-in-sorted-matrix [[1 3 5] [7 9 11]] 9)))
(assert (= [1 2 3 4] (deep-flatten [1 [2 [3 4]]])))
```

The sorted search requires every row-major value to be globally sorted. Sorted rows alone are not sufficient.

### Memory Hooks

- Outer loop: rows.
- Inner loop: cells.
- Flat index: `row * columns + column`.
- Coordinates: `[quotient remainder]`.

### Key Insight

Flatten exposes a matrix as one sequence. Preserve the width when you need to restore coordinates or shape.

## The Structure Section Complete

Transpose, rotate, and flip move cells. Reshape changes grouping. Flatten removes the row grouping.
