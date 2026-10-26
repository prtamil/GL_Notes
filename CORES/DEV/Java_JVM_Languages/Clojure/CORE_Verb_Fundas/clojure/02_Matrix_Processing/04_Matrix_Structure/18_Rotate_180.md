# 18. Rotate 180 Degrees

## Mental Model

Reverse the row order and reverse every row. The shape stays the same.

## Relationship to Cognitive Verb

```text
Turn around -> reverse both axes
```

## Clojure Functions and Common Idioms

|Need|Use|
|---|---|
|Half turn|two `reverse` operations|
|Coordinate rule|`[r c] -> [rows-1-r cols-1-c]`|
|Use flat data|reverse once, then reshape|
|Check central symmetry|compare with the half turn|

## Common Uses

- Rotate boards and images.
- Check central symmetry.
- Reverse row-major data.
- Create orientation variants.

## Hidden Interview Problems

- Prove that two half turns restore the input.
- Handle a fixed center cell.
- Rotate through flat storage.
- Update matrix state through an atom.

## Recognition Clues

Look for `half turn`, `upside down`, `reverse both axes`, or `central symmetry`.

## Pattern Summary

This rotation preserves shape. Every cell pairs with the cell opposite the center.

## Shape and Edge Behavior

- Direct rotation accepts finite ragged rows and preserves their lengths.
- Flat rotation requires a rectangular matrix.
- An empty matrix rotates to an empty matrix.

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

(defn rotate-180 [matrix]
  (mapv (comp vec reverse) (reverse matrix)))

(defn turn-around-coordinate [rows columns [row column]]
  [(- (dec rows) row)
   (- (dec columns) column)])

(defn flatten-matrix [matrix]
  (into [] cat matrix))

(defn reshape [values columns]
  (when-not (pos? columns)
    (throw (ex-info "Column count must be positive" {:columns columns})))
  (mapv vec (partition columns values)))

(defn rotate-180-via-flat [matrix]
  (require-rectangular matrix)
  (let [columns (if-let [row (first matrix)] (count row) 0)]
    (if (zero? columns)
      []
      (reshape (reverse (flatten-matrix matrix)) columns))))

(defn centrally-symmetric? [matrix]
  (= matrix (rotate-180 matrix)))

(defn rotate-180-atom! [matrix-atom]
  (swap! matrix-atom rotate-180))

(def matrix [[1 2 3] [4 5 6]])

(rotate-180 matrix)
;; => [[6 5 4] [3 2 1]]

(= matrix (rotate-180 (rotate-180 matrix)))
;; => true

;; Executable checks

(assert (= [[6 5 4] [3 2 1]] (rotate-180 matrix)))
(assert (= matrix (rotate-180 (rotate-180 matrix))))
(assert (= (rotate-180 matrix) (rotate-180-via-flat matrix)))
```

Persistent vectors do not share mutable row state. The pure form is safe and direct.

### Memory Hooks

- Reverse the rows.
- Reverse each row.
- The shape does not change.
- Two half turns cancel.

### Key Insight

A 180-degree rotation is also a complete reversal of row-major values.

## The Rotation Family So Far

|Turns|Shape|
|---|---|
|90 degrees|axes swap|
|180 degrees|shape stays|
|360 degrees|original matrix|
