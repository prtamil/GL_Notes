# 30. Checkerboard

## Mental Model

Use the parity of `row + column`. An orthogonal step changes that parity and therefore changes the cell class.

## Relationship to Cognitive Verb

```text
Alternate -> coordinate sum -> parity class
```

## Clojure Functions and Common Idioms

|Need|Use|
|---|---|
|Two colors|`mod (+ row column) 2`|
|Opposite phase|add one before `mod`|
|Horizontal stripes|row parity only|
|Vertical stripes|column parity only|
|Large squares|divide coordinates before parity|

## Common Uses

- Render board backgrounds.
- Prove grid bipartite properties.
- Build image-editor transparency grids.
- Create parity masks.
- Reject impossible tilings.

## Hidden Interview Problems

- Count both color classes.
- Validate either checkerboard phase.
- Explain why orthogonal neighbors differ.
- Show why diagonal neighbors can match.
- Apply the mutilated chessboard proof.

## Recognition Clues

Look for `alternating cells`, `two colors`, `parity`, `chessboard`, or `bipartite grid`.

## Pattern Summary

The expression `(row + column) mod 2` partitions the grid into two classes.

## Shape and Edge Behavior

- Generation uses finite nonnegative dimensions.
- A zero dimension produces no cells.
- Validation accepts finite ragged rows.
- An empty matrix is a valid checkerboard.

## Clojure Recipe Book

```clojure
(defn generate-grid [rows columns value-at]
  (when (or (neg? rows) (neg? columns))
    (throw (ex-info "Grid dimensions must not be negative"
                    {:rows rows :columns columns})))
  (mapv (fn [row]
          (mapv (fn [column]
                  (value-at row column))
                (range columns)))
        (range rows)))

(defn checkerboard
  ([rows columns] (checkerboard rows columns [0 1] 0))
  ([rows columns [first-value second-value] phase]
   (generate-grid
     rows
     columns
     (fn [row column]
       (if (zero? (mod (+ row column phase) 2))
         first-value
         second-value)))))

(defn render-grid [matrix palette]
  (mapv (fn [row]
          (apply str (map (fn [color-index]
                            (nth palette color-index))
                          row)))
        matrix))

(defn horizontal-stripes [rows columns]
  (generate-grid rows columns (fn [row _] (mod row 2))))

(defn vertical-stripes [rows columns]
  (generate-grid rows columns (fn [_ column] (mod column 2))))

(defn block-checkerboard [rows columns block-size]
  (when-not (pos? block-size)
    (throw (ex-info "Block size must be positive"
                    {:block-size block-size})))
  (generate-grid
    rows
    columns
    (fn [row column]
      (mod (+ (quot row block-size)
              (quot column block-size))
           2))))

(defn diagonal-color-bands [rows columns color-count]
  (when-not (pos? color-count)
    (throw (ex-info "Color count must be positive" {})))
  (generate-grid rows columns
                 (fn [row column]
                   (mod (+ row column) color-count))))

(defn phase-classes [rows columns]
  (generate-grid rows columns
                 (fn [row column]
                   (+ (* 2 (mod row 2))
                      (mod column 2)))))

(defn class-counts [matrix]
  (frequencies (mapcat identity matrix)))

(defn values-at [matrix coordinates]
  (set (map (fn [coordinate] (get-in matrix coordinate))
            coordinates)))

(defn single-valued? [values]
  (<= (count values) 1))

(defn checkerboard? [matrix]
  (let [coordinates
        (for [row (range (count matrix))
              column (range (count (nth matrix row)))]
          [row column])]
    (if (empty? coordinates)
      true
      (let [classes (group-by (fn [[row column]]
                                (mod (+ row column) 2))
                              coordinates)
            class-values
            (mapv (fn [class]
                    (values-at matrix (get classes class)))
                  [0 1])]
        (and (every? single-valued? class-values)
             (or (some empty? class-values)
                 (not= (first class-values) (second class-values))))))))

(def four-directions [[-1 0] [0 1] [1 0] [0 -1]])

(defn in-bounds? [matrix [row column]]
  (and (<= 0 row) (< row (count matrix))
       (<= 0 column) (< column (count (nth matrix row)))))

(defn orthogonal-neighbors-differ? [matrix]
  (every?
    (fn [[row column :as coordinate]]
      (every?
        (fn [[row-change column-change]]
          (let [next-coordinate [(+ row row-change)
                                 (+ column column-change)]]
            (or (not (in-bounds? matrix next-coordinate))
                (not= (get-in matrix coordinate)
                      (get-in matrix next-coordinate)))))
        four-directions))
    (for [row (range (count matrix))
          column (range (count (nth matrix row)))]
      [row column])))

(checkerboard 3 4)
;; => [[0 1 0 1] [1 0 1 0] [0 1 0 1]]

(render-grid (checkerboard 3 4) ["." "#"])
;; => [".#.#" "#.#." ".#.#"]

(class-counts (checkerboard 3 3))
;; => {0 5, 1 4}

;; Executable checks

(assert (= [[0 1 0 1] [1 0 1 0] [0 1 0 1]]
           (checkerboard 3 4)))
(assert (= [".#.#" "#.#." ".#.#"]
           (render-grid (checkerboard 3 4) ["." "#"])))
(assert (= {0 5 1 4} (class-counts (checkerboard 3 3))))
(assert (checkerboard? [[0 1 0] [1 0] [0 1 0]]))
```

A four-neighbor move changes the coordinate sum by one. It always changes parity.

A diagonal move changes the sum by zero or two. It preserves parity.

This fact proves that two removed same-color corners prevent a full domino tiling of a chessboard.

Knight moves also change parity because their coordinate sum changes by an odd number.

### Memory Hooks

- Add row and column.
- Take parity with `mod 2`.
- Orthogonal steps flip parity.
- Diagonal steps preserve parity.

### Key Insight

Checkerboard coloring turns many path and tiling questions into a count or parity proof.

## The Course in One Table

|Rule|Pattern|
|---|---|
|`row = column`|identity diagonal|
|`row + column` constant|anti-diagonal|
|`(row + column) mod 2`|checkerboard|
|distance from a center|radius field|
