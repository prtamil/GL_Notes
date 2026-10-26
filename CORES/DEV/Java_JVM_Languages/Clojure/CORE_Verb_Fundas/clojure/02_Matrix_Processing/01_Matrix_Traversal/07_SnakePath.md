# 7. Snake Traversal

## Mental Model

A snake joins alternate rows into one continuous path. Each row ends beside the start of the next row.

## Relationship to Cognitive Verb

```text
Connect -> forward row -> reverse row -> repeat
```

## Clojure Functions and Common Idioms

|Need|Use|
|---|---|
|Alternate rows|`map-indexed` and `reverse`|
|Create one path|`into [] cat`|
|Check continuity|`partition 2 1`|
|Map index to cell|`quot` and `mod`|

## Common Uses

- Move a robot across a grid.
- Address a serpentine LED panel.
- Reduce print-head travel.
- Fill a board in path order.

## Hidden Interview Problems

- Convert a path index to a coordinate.
- Convert a coordinate to a path index.
- Prove that each step is adjacent.
- Build a column-based snake.

## Recognition Clues

Look for `continuous`, `serpentine`, `boustrophedon`, or `reverse alternate rows`.

## Pattern Summary

Snake order uses the same alternation as row zigzag. Its purpose is a continuous physical path.

## Shape and Edge Behavior

- Row snake order accepts finite ragged rows.
- Column snake order requires a rectangular matrix.
- Generation rejects negative dimensions.
- Index conversion requires a nonnegative index and positive width.

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

(defn require-nonnegative-dimensions [rows columns]
  (when (or (neg? rows) (neg? columns))
    (throw (ex-info "Matrix dimensions must not be negative"
                    {:rows rows :columns columns}))))

(defn serpentine [lines]
  (->> lines
       (map-indexed (fn [line-index line]
                      (if (even? line-index)
                        line
                        (reverse line))))
       (mapcat identity)
       vec))

(defn snake-order [matrix]
  (serpentine matrix))

(defn transpose [matrix]
  (require-rectangular matrix)
  (if (empty? matrix) [] (apply mapv vector matrix)))

(defn column-snake-order [matrix]
  (serpentine (transpose matrix)))

(defn snake-coordinates [rows columns]
  (require-nonnegative-dimensions rows columns)
  (serpentine
    (mapv (fn [row]
            (mapv (fn [column] [row column])
                  (range columns)))
          (range rows))))

(defn manhattan-distance [[row-a column-a] [row-b column-b]]
  (+ (abs (- row-a row-b))
     (abs (- column-a column-b))))

(defn continuous-path? [path]
  (every? (fn [[from to]]
            (= 1 (manhattan-distance from to)))
          (partition 2 1 path)))

(defn path-length [path]
  (reduce + 0
          (map (fn [[from to]]
                 (manhattan-distance from to))
               (partition 2 1 path))))

(defn snake-index [row column columns]
  (when-not (pos? columns)
    (throw (ex-info "Column count must be positive" {:columns columns})))
  (+ (* row columns)
     (if (even? row)
       column
       (- (dec columns) column))))

(defn snake-position [index columns]
  (when (or (neg? index) (not (pos? columns)))
    (throw (ex-info "Index must be nonnegative and columns must be positive"
                    {:index index :columns columns})))
  (let [row (quot index columns)
        offset (mod index columns)]
    [row (if (even? row)
           offset
           (- (dec columns) offset))]))

(defn snake-fill [rows columns]
  (require-nonnegative-dimensions rows columns)
  (mapv (fn [row]
          (mapv (fn [column]
                  (inc (snake-index row column columns)))
                (range columns)))
        (range rows)))

(snake-coordinates 2 4)
;; => [[0 0] [0 1] [0 2] [0 3] [1 3] [1 2] [1 1] [1 0]]

(snake-fill 3 4)
;; => [[1 2 3 4] [8 7 6 5] [9 10 11 12]]

;; Executable checks

(assert (= [[0 0] [0 1] [0 2] [0 3]
            [1 3] [1 2] [1 1] [1 0]]
           (snake-coordinates 2 4)))
(assert (continuous-path? (snake-coordinates 3 4)))
(assert (= [[1 2 3 4] [8 7 6 5] [9 10 11 12]]
           (snake-fill 3 4)))
```

The path is empty when either dimension is zero. Index conversion requires a positive column count.

### Memory Hooks

- Even row: left to right.
- Odd row: right to left.
- `quot` finds the row.
- `mod` finds the offset within the row.

### Key Insight

The alternating direction removes the long jump between rows. This property makes snake order useful for physical movement.

## Zigzag vs Snake

Zigzag is an ordering rule. Snake is that rule plus coordinate continuity.
