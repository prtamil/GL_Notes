# 2. Column Traversal

## Mental Model

A column contains the value at one column index from every row. A transpose turns columns into rows.

## Relationship to Cognitive Verb

```text
Visit -> one column -> each row at that column
```

## Clojure Functions and Common Idioms

|Need|Use|
|---|---|
|Read one column|`mapv` with `nth`|
|Read all columns|transpose with `apply mapv vector`|
|Keep column indexes|`map-indexed`|
|Summarize columns|transpose, then `mapv`|

## Common Uses

- Calculate spreadsheet field totals.
- Validate Sudoku columns.
- Read vertical image lines.
- Compare feature columns.

## Hidden Interview Problems

- Find the column with the largest sum.
- Detect equal columns.
- Normalize each column.
- Handle ragged input safely.

## Recognition Clues

Look for `each column`, `vertical`, `same position in every row`, or `transpose first`.

## Pattern Summary

Column traversal fixes the column index and changes the row index.

## Shape and Edge Behavior

- The functions expect a finite rectangular matrix.
- An empty matrix returns empty column results.
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
  (if (empty? matrix)
    []
    (apply mapv vector matrix)))

(defn process-single-column [process-value matrix column-index]
  (require-rectangular matrix)
  (mapv (fn [row]
          (process-value (nth row column-index)))
        matrix))

(defn process-each-column [process-column matrix]
  (mapv process-column (transpose matrix)))

(defn column-total [column]
  (reduce + 0 column))

(defn column-sums [matrix]
  (process-each-column column-total matrix))

(defn column-maximum [column]
  (when (seq column) (apply max column)))

(defn column-maximums [matrix]
  (process-each-column column-maximum matrix))

(defn indexed-columns [matrix]
  (mapv (fn [column-index column]
          {:column column-index
           :values column})
        (range)
        (transpose matrix)))

(defn column-with-largest-sum [matrix]
  (let [columns (transpose matrix)]
    (when (seq columns)
      (apply max-key column-total columns))))

(defn unique-columns? [matrix]
  (every? #(= (count %) (count (set %)))
          (transpose matrix)))

(defn normalize-columns [matrix]
  (let [columns (transpose matrix)
        normalized
        (mapv (fn [column]
                (let [total (reduce + 0 column)]
                  (if (zero? total)
                    (mapv (constantly 0) column)
                    (mapv #(/ % total) column))))
              columns)]
    (transpose normalized)))

(def matrix [[1 2 3] [4 5 6] [7 8 9]])

(transpose matrix)
;; => [[1 4 7] [2 5 8] [3 6 9]]

(column-sums matrix)
;; => [12 15 18]

;; Executable checks

(assert (= [[1 4 7] [2 5 8] [3 6 9]]
           (transpose matrix)))
(assert (= [12 15 18] (column-sums matrix)))
```

`transpose` returns `[]` for an empty matrix. It rejects ragged rows because silent truncation loses data.

### Memory Hooks

- A column is one index across all rows.
- Transpose once when many column operations follow.
- Validate the row lengths before transposition.

### Key Insight

Transpose changes the view, not the values. After transposition, every row recipe becomes a column recipe.
