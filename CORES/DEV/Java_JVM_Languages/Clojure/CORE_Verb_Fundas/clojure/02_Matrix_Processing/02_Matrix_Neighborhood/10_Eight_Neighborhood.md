# 10. Eight-Neighborhood

## Mental Model

An eight-neighborhood contains every adjacent cell around a center. It includes orthogonal and diagonal steps.

## Relationship to Cognitive Verb

```text
Expand -> one step in any direction
```

## Clojure Functions and Common Idioms

|Need|Use|
|---|---|
|Create directions|nested `for`|
|Remove the center|`:when`|
|Read a 3 by 3 area|neighbor coordinates plus center|
|Wrap edges|`mod`|

## Common Uses

- Build Minesweeper counts.
- Update Conway's Game of Life.
- Detect peaks.
- Blur local image areas.
- Find eight-connected regions.

## Hidden Interview Problems

- Compare four-connected and eight-connected regions.
- Apply wraparound board rules.
- Count diagonal contacts.
- Find a local maximum.

## Recognition Clues

Look for `surrounding cells`, `including diagonals`, `3 by 3`, `Moore`, or `Chebyshev`.

## Pattern Summary

Every direction change uses `-1`, `0`, or `1`. Remove `[0 0]` because it is the center.

## Shape and Edge Behavior

- Matrix functions expect a finite rectangular matrix.
- An empty matrix has no neighbors.
- Matrix functions reject ragged rows with `ExceptionInfo`.
- Coordinate readers require an in-bounds coordinate.

## Clojure Recipe Book

```clojure
(def eight-directions
  (vec
    (for [row-change [-1 0 1]
          column-change [-1 0 1]
          :when (not= [0 0] [row-change column-change])]
      [row-change column-change])))

(defn rectangular? [matrix]
  (or (empty? matrix)
      (apply = (map count matrix))))

(defn require-rectangular [matrix]
  (when-not (rectangular? matrix)
    (throw (ex-info "Matrix must be rectangular"
                    {:row-lengths (mapv count matrix)})))
  matrix)

(defn in-bounds? [rows columns [row column]]
  (and (<= 0 row) (< row rows)
       (<= 0 column) (< column columns)))

(defn eight-neighbors [rows columns [row column]]
  (when (or (neg? rows) (neg? columns))
    (throw (ex-info "Matrix dimensions must not be negative"
                    {:rows rows :columns columns})))
  (vec
    (for [[row-change column-change] eight-directions
          :let [neighbor [(+ row row-change)
                          (+ column column-change)]]
          :when (in-bounds? rows columns neighbor)]
      neighbor)))

(defn block-around [matrix coordinate]
  (require-rectangular matrix)
  (let [rows (count matrix)
        columns (if-let [row (first matrix)] (count row) 0)
        coordinates (conj (eight-neighbors rows columns coordinate)
                          coordinate)]
    (when-not (in-bounds? rows columns coordinate)
      (throw (ex-info "Coordinate is outside the matrix"
                      {:coordinate coordinate})))
    (mapv (fn [position]
            {:coordinate position
             :value (get-in matrix position)})
          (sort coordinates))))

(defn count-eight-neighbors [matrix coordinate value]
  (require-rectangular matrix)
  (let [rows (count matrix)
        columns (if-let [row (first matrix)] (count row) 0)]
    (when-not (in-bounds? rows columns coordinate)
      (throw (ex-info "Coordinate is outside the matrix"
                      {:coordinate coordinate})))
    (count
      (filter (fn [neighbor]
                (= value (get-in matrix neighbor)))
              (eight-neighbors rows columns coordinate)))))

(defn mine-counts [mines]
  (require-rectangular mines)
  (let [rows (count mines)
        columns (if-let [row (first mines)] (count row) 0)]
    (mapv (fn [row]
            (mapv (fn [column]
                    (count-eight-neighbors mines [row column] 1))
                  (range columns)))
          (range rows))))

(defn life-step [grid]
  (require-rectangular grid)
  (let [rows (count grid)
        columns (if-let [row (first grid)] (count row) 0)]
    (mapv (fn [row]
            (mapv (fn [column]
                    (let [alive? (= 1 (get-in grid [row column]))
                          neighbors (count-eight-neighbors grid [row column] 1)]
                      (if (or (= neighbors 3)
                              (and alive? (= neighbors 2)))
                        1
                        0)))
                  (range columns)))
          (range rows))))

(defn blur-eight [matrix]
  (require-rectangular matrix)
  (let [rows (count matrix)
        columns (if-let [row (first matrix)] (count row) 0)]
    (mapv (fn [row]
            (mapv (fn [column]
                    (let [coordinate [row column]
                          neighbors (eight-neighbors rows columns coordinate)
                           values (map (fn [position]
                                         (get-in matrix position))
                                       (conj neighbors coordinate))]
                      (/ (reduce + values) (count values))))
                  (range columns)))
          (range rows))))

(defn local-peak? [matrix coordinate]
  (require-rectangular matrix)
  (let [rows (count matrix)
        columns (if-let [row (first matrix)] (count row) 0)
        value (get-in matrix coordinate)]
    (when-not (in-bounds? rows columns coordinate)
      (throw (ex-info "Coordinate is outside the matrix"
                      {:coordinate coordinate})))
    (every? (fn [neighbor]
              (< (get-in matrix neighbor) value))
            (eight-neighbors rows columns coordinate))))

(defn chebyshev-distance [[row-a column-a] [row-b column-b]]
  (max (abs (- row-a row-b))
       (abs (- column-a column-b))))

(defn wrapped-eight-neighbors [rows columns [row column]]
  (when (or (neg? rows) (neg? columns))
    (throw (ex-info "Matrix dimensions must not be negative"
                    {:rows rows :columns columns})))
  (if (or (zero? rows) (zero? columns))
    []
    (->> eight-directions
         (map (fn [[row-change column-change]]
                [(mod (+ row row-change) rows)
                 (mod (+ column column-change) columns)]))
         distinct
         vec)))

(eight-neighbors 3 3 [1 1])
;; => eight coordinates

(chebyshev-distance [1 1] [4 3])
;; => 3

;; Executable checks

(assert (= 8 (count (eight-neighbors 3 3 [1 1]))))
(assert (= 3 (chebyshev-distance [1 1] [4 3])))
```

Small wrapped grids can map two moves to one cell. `distinct` removes these duplicates.

### Memory Hooks

- Build nine offsets.
- Remove the zero offset.
- Chebyshev distance matches eight-direction movement.
- The boundary policy changes the result.

### Key Insight

The neighborhood definition controls connectivity. Pick four or eight directions before you count regions or shortest paths.

## Von Neumann vs Moore

Von Neumann uses four orthogonal neighbors. Moore uses all eight surrounding neighbors.
