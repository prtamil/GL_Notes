# 20. Flip Horizontal

## Mental Model

Mirror the matrix across its vertical axis. Reverse each row and keep the row order.

## Relationship to Cognitive Verb

```text
Mirror left to right -> reverse each row
```

## Clojure Functions and Common Idioms

|Need|Use|
|---|---|
|Horizontal flip|`mapv` with `reverse`|
|Coordinate rule|`[r c] -> [r cols-1-c]`|
|Check mirror symmetry|compare with the flip|
|Flip binary values too|reverse, then complement|

## Common Uses

- Mirror images.
- Compare reflected patterns.
- Convert camera orientation.
- Solve binary image tasks.

## Hidden Interview Problems

- Test if two matrices are mirrors.
- Find fixed cells on the center column.
- Flip and invert binary rows.
- Generate all reflection variants.

## Recognition Clues

Look for `left-right mirror`, `reverse each row`, or `vertical mirror axis`.

## Pattern Summary

The row index stays fixed. Only the column index changes.

## Shape and Edge Behavior

- The functions accept finite ragged rows.
- Each row keeps its original length.
- An empty matrix returns an empty matrix.

## Clojure Recipe Book

```clojure
(defn flip-horizontal [matrix]
  (mapv (comp vec reverse) matrix))

(defn mirror-coordinate [columns [row column]]
  [row (- (dec columns) column)])

(defn mirror-symmetric? [matrix]
  (= matrix (flip-horizontal matrix)))

(defn horizontal-mirror-of? [candidate matrix]
  (= candidate (flip-horizontal matrix)))

(defn flip-horizontal-atom! [matrix-atom]
  (swap! matrix-atom flip-horizontal))

(defn flip-and-invert [binary-matrix]
  (mapv (fn [row]
          (mapv #(- 1 %) (reverse row)))
        binary-matrix))

(def matrix [[1 2 3] [4 5 6]])

(flip-horizontal matrix)
;; => [[3 2 1] [6 5 4]]

(mirror-coordinate 3 [1 0])
;; => [1 2]

(flip-and-invert [[1 1 0] [1 0 1]])
;; => [[1 0 0] [0 1 0]]

;; Executable checks

(assert (= [[3 2 1] [6 5 4]] (flip-horizontal matrix)))
(assert (= [[1 0 0] [0 1 0]]
           (flip-and-invert [[1 1 0] [1 0 1]])))
```

`Horizontal flip` can be ambiguous. This course follows the Python reference and means a left-right mirror.

### Memory Hooks

- Keep row order.
- Reverse each row.
- The mirror axis is vertical.
- A center column stays fixed.

### Key Insight

Name the axis and show the coordinate rule. This practice prevents direction mistakes.

## The Four Mirrors

The main mirrors are horizontal, vertical, main diagonal, and anti-diagonal.
