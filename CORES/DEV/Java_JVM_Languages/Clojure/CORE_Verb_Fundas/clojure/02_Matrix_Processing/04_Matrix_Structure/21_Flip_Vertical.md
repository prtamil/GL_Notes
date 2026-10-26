# 21. Flip Vertical

## Mental Model

Mirror the matrix across its horizontal axis. Reverse the row order and keep each row unchanged.

## Relationship to Cognitive Verb

```text
Mirror top to bottom -> reverse row order
```

## Clojure Functions and Common Idioms

|Need|Use|
|---|---|
|Vertical flip|`vec` with `reverse`|
|Coordinate rule|`[r c] -> [rows-1-r c]`|
|Convert vertical origins|reverse the row coordinate|
|Check symmetry|compare with the flip|

## Common Uses

- Convert screen and Cartesian row directions.
- Mirror images top to bottom.
- Check horizontal-axis symmetry.
- Build rotation operations.

## Hidden Interview Problems

- Explain row sharing in mutable languages.
- Convert bottom-origin coordinates.
- Find a fixed center row.
- Prove that two flips cancel.

## Recognition Clues

Look for `top-bottom mirror`, `reverse the rows`, or `horizontal mirror axis`.

## Pattern Summary

The column index stays fixed. Only the row index changes.

## Shape and Edge Behavior

- The functions accept a finite ragged matrix.
- Rows keep their values and lengths.
- An empty matrix returns an empty matrix.

## Clojure Recipe Book

```clojure
(defn flip-vertical [matrix]
  (vec (reverse matrix)))

(defn vertical-mirror-coordinate [rows [row column]]
  [(- (dec rows) row) column])

(defn to-screen-row [cartesian-row rows]
  (- (dec rows) cartesian-row))

(defn vertical-symmetric? [matrix]
  (= matrix (flip-vertical matrix)))

(defn flip-vertical-atom! [matrix-atom]
  (swap! matrix-atom flip-vertical))

(def matrix [[1 2 3] [4 5 6]])

(flip-vertical matrix)
;; => [[4 5 6] [1 2 3]]

(vertical-mirror-coordinate 2 [0 2])
;; => [1 2]

(= matrix (flip-vertical (flip-vertical matrix)))
;; => true

;; Executable checks

(assert (= [[4 5 6] [1 2 3]] (flip-vertical matrix)))
(assert (= matrix (flip-vertical (flip-vertical matrix))))
```

Clojure rows are normally persistent values. Reversing the outer vector does not create mutable aliasing problems.

### Memory Hooks

- Reverse row order.
- Keep each row unchanged.
- The mirror axis is horizontal.
- A center row stays fixed.

### Key Insight

A vertical flip converts between top-origin and bottom-origin row coordinates.

## The Eight Symmetries of a Square

A square has four rotations and four reflections. These transformations form the dihedral group `D4`.
