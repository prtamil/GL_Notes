# 24. Find a Cell

## Mental Model

Search coordinates in a defined order. Stop at the first match or collect every match.

## Relationship to Cognitive Verb

```text
Search -> coordinate -> cell value -> match
```

## Clojure Functions and Common Idioms

|Need|Use|
|---|---|
|First match|`some`|
|All matches|`into` with `filter`|
|Match by rule|a predicate|
|Sorted rows and columns|staircase search|
|Globally sorted values|binary search over flat indexes|

## Common Uses

- Locate a board value.
- Find image markers.
- Select cells by a predicate.
- Search sorted matrices.

## Hidden Interview Problems

- Return coordinates instead of values.
- Preserve row-major tie order.
- Search a row-and-column sorted matrix.
- Search a globally sorted matrix in logarithmic time.

## Recognition Clues

Look for `find the cell`, `return its coordinates`, `first match`, or `sorted matrix search`.

## Pattern Summary

General search reads cells. Sorted structure permits a faster search when its exact invariant is known.

## Shape and Edge Behavior

- General coordinate search accepts a finite ragged matrix.
- An empty matrix has no match.
- Optimized sorted searches require rectangular input.
- Optimized searches reject ragged rows with `ExceptionInfo`.

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

(defn coordinates [matrix]
  (for [row (range (count matrix))
        column (range (count (nth matrix row)))]
    [row column]))

(defn find-cell-by [matrix predicate]
  (some (fn [coordinate]
          (let [value (get-in matrix coordinate)]
            (when (predicate value)
              {:coordinate coordinate :value value})))
        (coordinates matrix)))

(defn find-cell [matrix target]
  (find-cell-by matrix (fn [value] (= target value))))

(defn find-all-cells [matrix predicate]
  (->> (coordinates matrix)
       (keep (fn [coordinate]
               (let [value (get-in matrix coordinate)]
                 (when (predicate value)
                   {:coordinate coordinate :value value}))))
       vec))

(defn staircase-search [matrix target]
  (require-rectangular matrix)
  (let [rows (count matrix)
        columns (if-let [row (first matrix)] (count row) 0)]
    (loop [row 0
           column (dec columns)]
      (when (and (< row rows) (<= 0 column))
        (let [value (get-in matrix [row column])]
          (cond
            (= value target) [row column]
            (> value target) (recur row (dec column))
            :else (recur (inc row) column)))))))

(defn binary-search-matrix [matrix target]
  (require-rectangular matrix)
  (let [rows (count matrix)
        columns (if-let [row (first matrix)] (count row) 0)
        size (* rows columns)]
    (when (pos? columns)
      (loop [low 0
             high (dec size)]
        (when (<= low high)
          (let [middle (quot (+ low high) 2)
                coordinate [(quot middle columns) (mod middle columns)]
                value (get-in matrix coordinate)]
            (cond
              (= value target) coordinate
              (< value target) (recur (inc middle) high)
              :else (recur low (dec middle)))))))))

(def matrix [[1 4 7] [2 5 8] [3 6 9]])

(find-cell matrix 5)
;; => {:coordinate [1 1], :value 5}

(find-all-cells matrix odd?)
;; => five coordinate and value maps

(staircase-search matrix 6)
;; => [2 1]

;; Executable checks

(assert (= {:coordinate [1 1] :value 5} (find-cell matrix 5)))
(assert (= 5 (count (find-all-cells matrix odd?))))
(assert (= [2 1] (staircase-search matrix 6)))
```

Staircase search requires sorted rows and sorted columns. Binary search requires global row-major order.

### Memory Hooks

- Return the coordinate with the value.
- `some` stops at the first truthy result.
- Staircase search starts at the top-right corner.
- Binary search treats the matrix as a virtual vector.

### Key Insight

Choose the search from the data invariant. Do not apply binary search to rows that are only individually sorted.

## The Search Section

This lesson finds independent cells. The next lessons search connected regions.
