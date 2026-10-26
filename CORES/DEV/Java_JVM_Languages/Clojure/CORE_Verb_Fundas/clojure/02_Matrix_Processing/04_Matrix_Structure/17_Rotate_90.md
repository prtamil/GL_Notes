# 17. Rotate 90 Degrees

## Mental Model

A clockwise quarter turn transposes the matrix after reversing its row order.

## Relationship to Cognitive Verb

```text
Turn right -> reverse rows -> transpose
```

## Clojure Functions and Common Idioms

|Need|Use|
|---|---|
|Clockwise turn|`reverse`, then transpose|
|Coordinate rule|`[row column] -> [column rows-1-row]`|
|Several turns|normalize with `mod`|
|Compare rotations|generate four orientations|

## Common Uses

- Rotate images and boards.
- Normalize puzzle pieces.
- Change portrait data to landscape data.
- Generate orientation variants.

## Hidden Interview Problems

- Rotate a rectangular matrix.
- Map old coordinates to new coordinates.
- Test whether two matrices differ only by rotation.
- Rotate shared state safely.

## Recognition Clues

Look for `quarter turn`, `clockwise`, `turn right`, or `rotate 90 degrees`.

## Pattern Summary

The shape changes from `R x C` to `C x R`. Four turns restore the original matrix.

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

(defn rotate-90 [matrix]
  (transpose (vec (reverse matrix))))

(defn rotate-90-explicit [matrix]
  (require-rectangular matrix)
  (let [rows (count matrix)
        columns (if-let [row (first matrix)] (count row) 0)]
    (mapv (fn [column]
            (mapv (fn [row]
                    (get-in matrix [row column]))
                  (range (dec rows) -1 -1)))
          (range columns))))

(defn turn-right-coordinate [rows [row column]]
  [column (- (dec rows) row)])

(defn rotated-coordinate-grid [rows columns]
  (when (or (neg? rows) (neg? columns))
    (throw (ex-info "Matrix dimensions must not be negative"
                    {:rows rows :columns columns})))
  (rotate-90
    (mapv (fn [row]
            (mapv (fn [column] [row column])
                  (range columns)))
          (range rows))))

(defn rotate-quarter-turns [matrix turns]
  (nth (iterate rotate-90 matrix) (mod turns 4)))

(defn rotation-variants [matrix]
  (mapv #(rotate-quarter-turns matrix %) (range 4)))

(defn rotation-of? [candidate matrix]
  (boolean (some #(= candidate %) (rotation-variants matrix))))

(defn rotate-90-atom! [matrix-atom]
  (swap! matrix-atom rotate-90))

(def matrix [[1 2 3] [4 5 6]])

(rotate-90 matrix)
;; => [[4 1] [5 2] [6 3]]

(turn-right-coordinate 2 [0 2])
;; => [2 1]

;; Executable checks

(assert (= [[4 1] [5 2] [6 3]] (rotate-90 matrix)))
(assert (= matrix (rotate-quarter-turns matrix 4)))
```

The pure function supports rectangular matrices. In-place four-cell swaps only suit square mutable arrays.

### Memory Hooks

- Reverse row order.
- Transpose.
- Clockwise means turn right.
- Normalize turn counts with `mod 4`.

### Key Insight

A 90-degree rotation is a transpose plus one flip. The flip direction determines the turn direction.

## Rotate 90 Degrees vs Transpose

Transpose only swaps axes. Rotation also reverses one axis.
