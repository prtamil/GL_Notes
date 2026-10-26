# 9. Four-Neighborhood

## Mental Model

A cell has up to four orthogonal neighbors. These neighbors are above, right, below, and left.

## Relationship to Cognitive Verb

```text
Expand -> one orthogonal step
```

## Clojure Functions and Common Idioms

|Need|Use|
|---|---|
|Store moves|a vector of `[row-change column-change]`|
|Check a position|`in-bounds?`|
|Create neighbors|`keep` or `filter`|
|Search outward|a persistent queue|

## Common Uses

- Search mazes.
- Fill connected areas.
- Count islands.
- Model grid graphs.
- Calculate local values.

## Hidden Interview Problems

- Use wraparound edges.
- Pad the matrix before local work.
- Count matching neighbors.
- Perform breadth-first search.

## Recognition Clues

Look for `up, down, left, right`, `orthogonal`, `Manhattan`, or `four-connected`.

## Pattern Summary

Four-neighborhood excludes diagonal cells. A corner has two neighbors, and an inner cell has four.

## Shape and Edge Behavior

- Matrix functions expect a finite rectangular matrix.
- An empty matrix has no neighbors.
- Matrix functions reject ragged rows with `ExceptionInfo`.
- Coordinate readers require an in-bounds coordinate.

## Clojure Recipe Book

```clojure
(def four-directions
  [[-1 0] [0 1] [1 0] [0 -1]])

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

(defn move [[row column] [row-change column-change]]
  [(+ row row-change) (+ column column-change)])

(defn four-neighbors [rows columns coordinate]
  (when (or (neg? rows) (neg? columns))
    (throw (ex-info "Matrix dimensions must not be negative"
                    {:rows rows :columns columns})))
  (vec
    (for [direction four-directions
          :let [neighbor (move coordinate direction)]
          :when (in-bounds? rows columns neighbor)]
      neighbor)))

(defn neighbor-values [matrix coordinate]
  (require-rectangular matrix)
  (let [rows (count matrix)
        columns (if-let [row (first matrix)] (count row) 0)]
    (when-not (in-bounds? rows columns coordinate)
      (throw (ex-info "Coordinate is outside the matrix"
                      {:coordinate coordinate})))
    (mapv #(get-in matrix %)
          (four-neighbors rows columns coordinate))))

(defn neighbors-in-map [grid coordinate]
  (into {}
        (keep (fn [direction]
                (let [next-coordinate (move coordinate direction)]
                  (when (contains? grid next-coordinate)
                    [next-coordinate (grid next-coordinate)]))))
        four-directions))

(defn pad-matrix [matrix fill]
  (require-rectangular matrix)
  (let [columns (if-let [row (first matrix)] (count row) 0)
        padded-row (vec (repeat (+ columns 2) fill))]
    (vec
      (concat
        [padded-row]
        (map (fn [row] (vec (concat [fill] row [fill]))) matrix)
        [padded-row]))))

(defn wrapped-four-neighbors [rows columns [row column]]
  (when (or (neg? rows) (neg? columns))
    (throw (ex-info "Matrix dimensions must not be negative"
                    {:rows rows :columns columns})))
  (if (or (zero? rows) (zero? columns))
    []
    (mapv (fn [[row-change column-change]]
            [(mod (+ row row-change) rows)
             (mod (+ column column-change) columns)])
          four-directions)))

(defn count-four-neighbors [matrix coordinate value]
  (count (filter #(= value %)
                 (neighbor-values matrix coordinate))))

(defn local-minimum? [matrix coordinate]
  (let [value (get-in matrix coordinate)]
    (every? #(< value %)
            (neighbor-values matrix coordinate))))

(defn smooth-four [matrix]
  (require-rectangular matrix)
  (let [rows (count matrix)
        columns (if-let [row (first matrix)] (count row) 0)]
    (mapv (fn [row]
            (mapv (fn [column]
                    (let [coordinate [row column]
                          values (conj (neighbor-values matrix coordinate)
                                       (get-in matrix coordinate))]
                      (/ (reduce + values) (count values))))
                  (range columns)))
          (range rows))))

(defn breadth-first-coordinates [matrix start passable?]
  (require-rectangular matrix)
  (let [rows (count matrix)
        columns (if-let [row (first matrix)] (count row) 0)]
    (if-not (and (in-bounds? rows columns start)
                 (passable? (get-in matrix start)))
      []
      (loop [queue (conj clojure.lang.PersistentQueue/EMPTY start)
             seen #{start}
             result []]
        (if (empty? queue)
          result
          (let [coordinate (peek queue)
                candidates
                (filter (fn [next-coordinate]
                          (and (not (contains? seen next-coordinate))
                               (passable? (get-in matrix next-coordinate))))
                        (four-neighbors rows columns coordinate))]
            (recur (into (pop queue) candidates)
                   (into seen candidates)
                   (conj result coordinate))))))))

(defn manhattan-distance [[row-a column-a] [row-b column-b]]
  (+ (abs (- row-a row-b))
     (abs (- column-a column-b))))

(four-neighbors 3 4 [0 0])
;; => [[0 1] [1 0]]

(manhattan-distance [1 2] [4 6])
;; => 7

;; Executable checks

(assert (= [[0 1] [1 0]] (four-neighbors 3 4 [0 0])))
(assert (= 7 (manhattan-distance [1 2] [4 6])))
```

The order is up, right, down, then left. Change the direction vector order when tie order matters.

### Memory Hooks

- Four moves change one coordinate.
- Filter positions after you create them.
- A matrix is also a graph.
- Manhattan distance matches four-direction movement.

### Key Insight

Keep movement rules in data. The same search code can then use another neighborhood without structural changes.

## Von Neumann vs Moore

Four-neighborhood is also called the Von Neumann neighborhood. Moore neighborhood adds the four diagonal moves.
