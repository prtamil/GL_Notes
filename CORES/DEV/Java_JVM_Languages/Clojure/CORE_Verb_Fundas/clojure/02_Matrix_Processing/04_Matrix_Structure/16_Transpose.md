# 16. Transpose

## Mental Model

Transpose swaps rows and columns. The cell at `[row column]` moves to `[column row]`.

## Relationship to Cognitive Verb

```text
Reorient -> swap the two axes
```

## Clojure Functions and Common Idioms

|Need|Use|
|---|---|
|Transpose a rectangle|`apply mapv vector`|
|Keep vector rows|`mapv`|
|Check symmetry|compare with the transpose|
|Reflect across the other diagonal|transpose, then rotate 180 degrees|

## Common Uses

- Turn column work into row work.
- Check symmetric matrices.
- Support matrix multiplication.
- Build rotations and reflections.

## Hidden Interview Problems

- Reject ragged input.
- Explain the new shape.
- Transpose a square matrix through an atom.
- Reflect across the anti-diagonal.

## Recognition Clues

Look for `swap rows and columns`, `change axes`, or `[row column]` becoming `[column row]`.

## Pattern Summary

An `R` by `C` matrix becomes a `C` by `R` matrix. Values do not change.

## Shape and Edge Behavior

- The functions expect a finite rectangular matrix.
- An empty or zero-width matrix transposes to `[]`.
- The functions reject ragged rows with `ExceptionInfo`.

## Clojure Recipe Book

```clojure
(defn rectangular? [matrix]
  (or (empty? matrix) (apply = (map count matrix))))

(defn require-rectangular [matrix]
  (when-not (rectangular? matrix)
    (throw (ex-info "Matrix must be rectangular"
                    {:row-lengths (mapv count matrix)})))
  matrix)

(defn transpose [matrix]
  (require-rectangular matrix)
  (if (empty? matrix)
    []
    (apply mapv vector matrix)))

(defn transpose-explicit [matrix]
  (require-rectangular matrix)
  (let [columns (if-let [row (first matrix)] (count row) 0)]
    (mapv (fn [column]
            (mapv #(nth % column) matrix))
          (range columns))))

(defn symmetric? [matrix]
  (and (rectangular? matrix)
       (= (count matrix) (count (first matrix)))
       (= matrix (transpose matrix))))

(defn rotate-180 [matrix]
  (mapv (comp vec reverse) (reverse matrix)))

(defn anti-transpose [matrix]
  (rotate-180 (transpose matrix)))

(defn transpose-atom! [matrix-atom]
  (swap! matrix-atom transpose))

(def matrix [[1 2 3] [4 5 6]])

(transpose matrix)
;; => [[1 4] [2 5] [3 6]]

(anti-transpose matrix)
;; => [[6 3] [5 2] [4 1]]

;; Executable checks

(assert (= [[1 4] [2 5] [3 6]] (transpose matrix)))
(assert (= [[6 3] [5 2] [4 1]] (anti-transpose matrix)))
```

`transpose` returns `[]` for an empty matrix. It rejects ragged rows because transposition would lose or invent positions.

Persistent vectors make a pure transpose the normal choice. Use an atom only when shared identity is required.

### Memory Hooks

- Swap the axes.
- Shape changes from `R x C` to `C x R`.
- Main diagonal cells remain fixed in a square matrix.
- Columns become ordinary rows.

### Key Insight

Transpose changes positions, not values. It is the base operation for several rotations and reflections.

## The Structure Section

Structure operations move existing cells. They do not calculate new cell values.
