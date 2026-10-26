# 19. Rotate 270 Degrees

## Mental Model

A 270-degree clockwise turn equals a 90-degree counter-clockwise turn. Transpose, then reverse the row order.

## Relationship to Cognitive Verb

```text
Turn left -> transpose -> reverse rows
```

## Clojure Functions and Common Idioms

|Need|Use|
|---|---|
|Turn left|transpose, then reverse rows|
|Coordinate rule|`[r c] -> [cols-1-c r]`|
|Any quarter turn|repeat `rotate-90`|
|Canonical orientation|sort the four variants|

## Common Uses

- Rotate images left.
- Normalize rotated shapes.
- Generate game-piece orientations.
- Compare cyclic layouts.

## Hidden Interview Problems

- Avoid confusing left and right turns.
- Map coordinates without creating a matrix.
- Deduplicate rotated shapes.
- Normalize negative turn counts.

## Recognition Clues

Look for `turn left`, `counter-clockwise`, or `270 degrees clockwise`.

## Pattern Summary

The shape changes from `R x C` to `C x R`. This turn is the inverse of a clockwise quarter turn.

## Shape and Edge Behavior

- The functions expect a finite rectangular matrix.
- An empty or zero-width matrix rotates to `[]`.
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

(defn transpose [matrix]
  (require-rectangular matrix)
  (if (empty? matrix) [] (apply mapv vector matrix)))

(defn rotate-270 [matrix]
  (vec (reverse (transpose matrix))))

(defn rotate-90 [matrix]
  (transpose (vec (reverse matrix))))

(defn rotate-quarter-turns [matrix turns]
  (nth (iterate rotate-90 matrix) (mod turns 4)))

(defn turn-left-coordinate [columns [row column]]
  [(- (dec columns) column) row])

(defn rotated-coordinate-grid [rows columns]
  (when (or (neg? rows) (neg? columns))
    (throw (ex-info "Matrix dimensions must not be negative"
                    {:rows rows :columns columns})))
  (rotate-270
    (mapv (fn [row]
            (mapv (fn [column] [row column])
                  (range columns)))
          (range rows))))

(defn canonical-rotation [matrix]
  (first (sort-by pr-str
                  (map #(rotate-quarter-turns matrix %) (range 4)))))

(defn rotate-270-atom! [matrix-atom]
  (swap! matrix-atom rotate-270))

(def matrix [[1 2 3] [4 5 6]])

(rotate-270 matrix)
;; => [[3 6] [2 5] [1 4]]

(turn-left-coordinate 3 [0 2])
;; => [0 0]

;; Executable checks

(assert (= [[3 6] [2 5] [1 4]] (rotate-270 matrix)))
(assert (= matrix (rotate-quarter-turns matrix 4)))
```

The canonical function uses printed value order. Supply a domain-specific key when another order has meaning.

### Memory Hooks

- Transpose first.
- Reverse the new row order.
- Left turn is the inverse of right turn.
- Negative turns work with `mod`.

### Key Insight

Write the coordinate rule when direction is unclear. A coordinate grid makes the result visible.

## The Four Rotations

|Clockwise turns|Operation|
|---|---|
|0|identity|
|1|rotate 90 degrees|
|2|rotate 180 degrees|
|3|rotate 270 degrees|
