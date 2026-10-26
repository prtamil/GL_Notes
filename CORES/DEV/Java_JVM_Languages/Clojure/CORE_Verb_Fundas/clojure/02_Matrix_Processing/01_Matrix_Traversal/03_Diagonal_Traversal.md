# 3. Diagonal Traversal

## Mental Model

Cells share a descending diagonal when `column - row` is constant. The main diagonal uses zero.

## Relationship to Cognitive Verb

```text
Trace -> keep column - row constant
```

## Clojure Functions and Common Idioms

|Need|Use|
|---|---|
|Main diagonal|same row and column index|
|Offset diagonal|constant `column - row`|
|Trace|`reduce +` over the main diagonal|
|All diagonals|map every valid offset|

## Common Uses

- Calculate a matrix trace.
- Check identity and symmetric matrices.
- Read diagonal board lines.
- Group cells by diagonal.

## Hidden Interview Problems

- Read an offset diagonal.
- Compare both main diagonals.
- Check identity structure.
- Traverse every diagonal.

## Recognition Clues

Look for `top-left to bottom-right`, `same indexes`, `trace`, or a constant coordinate difference.

## Pattern Summary

The offset `k` defines `column = row + k`. Positive offsets are above the main diagonal.

## Shape and Edge Behavior

- The functions expect a finite rectangular matrix.
- A matrix with no cells returns empty diagonal results.
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

(defn matrix-shape [matrix]
  (require-rectangular matrix)
  [(count matrix) (if-let [row (first matrix)] (count row) 0)])

(defn diagonal-coordinates
  ([matrix] (diagonal-coordinates matrix 0))
  ([matrix offset]
   (let [[rows columns] (matrix-shape matrix)
         first-row (max 0 (- offset))
         end-row (min rows (- columns offset))]
     (mapv (fn [row] [row (+ row offset)])
           (range first-row end-row)))))

(defn diagonal
  ([matrix] (diagonal matrix 0))
  ([matrix offset]
   (mapv #(get-in matrix %)
         (diagonal-coordinates matrix offset))))

(defn trace [matrix]
  (reduce + 0 (diagonal matrix)))

(defn all-diagonals [matrix]
  (let [[rows columns] (matrix-shape matrix)]
    (if (or (zero? rows) (zero? columns))
      []
      (mapv #(diagonal matrix %)
            (range (- (dec rows)) columns)))))

(defn transpose [matrix]
  (require-rectangular matrix)
  (if (empty? matrix) [] (apply mapv vector matrix)))

(defn identity-matrix? [matrix]
  (let [[rows columns] (matrix-shape matrix)]
    (and (rectangular? matrix)
         (= rows columns)
         (every? (fn [[row column]]
                   (= (get-in matrix [row column])
                      (if (= row column) 1 0)))
                 (for [row (range rows)
                       column (range columns)]
                   [row column])))))

(defn symmetric? [matrix]
  (and (rectangular? matrix)
       (= (count matrix) (count (first matrix)))
       (= matrix (transpose matrix))))

(def matrix [[1 2 3] [4 5 6] [7 8 9]])

(diagonal matrix)
;; => [1 5 9]

(diagonal matrix 1)
;; => [2 6]

(all-diagonals matrix)
;; => [[7] [4 8] [1 5 9] [2 6] [3]]

;; Executable checks

(assert (= [1 5 9] (diagonal matrix)))
(assert (= [2 6] (diagonal matrix 1)))
(assert (= [[7] [4 8] [1 5 9] [2 6] [3]]
           (all-diagonals matrix)))
```

The coordinate formula works for rectangular matrices. An offset outside the matrix produces `[]`.

### Memory Hooks

- Main diagonal: `row = column`.
- Any descending diagonal: `column - row` is constant.
- Positive offset means above the main diagonal.

### Key Insight

A diagonal is a coordinate rule. Write the rule first, then read values with `get-in`.
