# 13. Block and Tile

## Mental Model

Set the row stride to the tile height. Set the column stride to the tile width.

The result is a grid of non-overlapping tiles. Edge tiles can be smaller when dimensions do not divide evenly.

## Relationship to Cognitive Verb

```text
Partition -> divide into independent blocks
```

## Clojure Functions and Common Idioms

|Need|Use|
|---|---|
|Tile starts|stepped `range`|
|Take a tile|bounded `subvec`|
|Keep tile layout|a grid of tile grids|
|Pool each tile|`mapv` twice|
|Reassemble tiles|join matching inner rows|

## Common Uses

- Validate Sudoku boxes.
- Pool image blocks.
- Process JPEG blocks.
- Divide work across workers.
- Rearrange matrix quadrants.

## Hidden Interview Problems

- Keep or pad partial edge tiles.
- Reassemble the original matrix.
- Transpose the grid of tiles.
- Replace each tile with one pooled value.

## Recognition Clues

Look for `non-overlapping`, `blocks`, `tiles`, `chunks`, `boxes`, or `downsample`.

## Pattern Summary

Tiles are sliding windows whose stride equals their size. Every source cell belongs to one tile.

## Shape and Edge Behavior

- The functions expect a finite rectangular matrix.
- Tile dimensions must be positive.
- An empty matrix produces an empty tile grid.
- The functions reject ragged rows with `ExceptionInfo`.

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

(defn ceiling-quotient [number divisor]
  (when (or (neg? number) (not (pos? divisor)))
    (throw (ex-info "Number must be nonnegative and divisor must be positive"
                    {:number number :divisor divisor})))
  (quot (+ number divisor -1) divisor))

(defn tile-count [rows columns height width]
  (* (ceiling-quotient rows height)
     (ceiling-quotient columns width)))

(defn tile-at [matrix [row column] height width]
  (require-rectangular matrix)
  (when (or (not (pos? height)) (not (pos? width)))
    (throw (ex-info "Tile dimensions must be positive"
                    {:height height :width width})))
  (let [row-end (min (count matrix) (+ row height))
        column-count (if-let [source-row (first matrix)]
                       (count source-row)
                       0)
        column-end (min column-count (+ column width))]
    (when-not (and (<= 0 row) (< row (count matrix))
                   (<= 0 column) (< column column-count))
      (throw (ex-info "Tile origin is outside the matrix"
                      {:origin [row column]})))
    (mapv (fn [source-row]
            (subvec (vec source-row) column column-end))
          (subvec (vec matrix) row row-end))))

(defn tile-grid [matrix height width]
  (require-rectangular matrix)
  (when-not (and (pos? height) (pos? width))
    (throw (ex-info "Tile dimensions must be positive"
                    {:height height :width width})))
  (let [rows (count matrix)
        columns (if-let [row (first matrix)] (count row) 0)]
    (mapv (fn [row]
            (mapv (fn [column]
                    (tile-at matrix [row column] height width))
                  (range 0 columns width)))
          (range 0 rows height))))

(defn flatten-tile [tile]
  (into [] cat tile))

(defn pool-tiles [matrix height width summarize]
  (mapv (fn [tile-row]
          (mapv (fn [tile]
                  (summarize (flatten-tile tile)))
                tile-row))
        (tile-grid matrix height width)))

(defn untile [tiles]
  (vec
    (mapcat
      (fn [tile-row]
        (if (empty? tile-row)
          []
          (mapv (fn [inner-row]
                  (into [] cat
                        (map #(nth % inner-row) tile-row)))
                (range (count (first tile-row))))))
      tiles)))

(defn transpose-grid [grid]
  (require-rectangular grid)
  (if (empty? grid) [] (apply mapv vector grid)))

(defn transpose-tile-layout [matrix height width]
  (untile (transpose-grid (tile-grid matrix height width))))

(defn pixelate [matrix height width]
  (let [pooled (pool-tiles matrix height width
                           #(/ (reduce + %) (count %)))
        rows (count matrix)
        columns (if-let [row (first matrix)] (count row) 0)]
    (mapv (fn [row]
            (mapv (fn [column]
                    (get-in pooled [(quot row height)
                                    (quot column width)]))
                  (range columns)))
          (range rows))))

(defn tile-sequence [matrix height width]
  (for [tile-row (tile-grid matrix height width)
        tile tile-row]
    tile))

(def matrix
  [[1  2  3  4]
   [5  6  7  8]
   [9 10 11 12]
   [13 14 15 16]])

(pool-tiles matrix 2 2 #(apply max %))
;; => [[6 8] [14 16]]

(untile (tile-grid matrix 2 2))
;; => the original matrix

;; Executable checks

(assert (= [[6 8] [14 16]]
           (pool-tiles matrix 2 2 #(apply max %))))
(assert (= matrix (untile (tile-grid matrix 2 2))))
```

`tile-grid` keeps smaller edge tiles. Pad the matrix first when every tile must have the same size.

### Memory Hooks

- Window stride one means overlap.
- Tile stride equals tile size.
- Keep a grid of tiles when reassembly matters.
- Pooling returns one value for each tile.

### Key Insight

Non-overlapping tiles partition the work. This property permits independent processing and simple reassembly.

## Window vs Tile

A sliding window checks every placement. A tile grid selects disjoint placements only.
