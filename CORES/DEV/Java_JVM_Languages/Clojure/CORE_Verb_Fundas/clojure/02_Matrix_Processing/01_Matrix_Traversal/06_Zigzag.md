# 6. Zigzag Traversal

## Mental Model

Reverse every second line. A line can be a row, column, tree level, or anti-diagonal.

## Relationship to Cognitive Verb

```text
Alternate -> forward line -> reverse line -> repeat
```

## Clojure Functions and Common Idioms

|Need|Use|
|---|---|
|Alternate lines|`map-indexed` and `reverse`|
|Flatten lines|`into [] cat`|
|Zigzag columns|transpose first|
|JPEG scan|group by `row + column`|

## Common Uses

- Serialize a matrix.
- Scan image coefficients.
- Alternate tree levels.
- Sweep a grid in both directions.

## Hidden Interview Problems

- Restore a row-zigzag sequence.
- Traverse columns in alternating directions.
- Produce the JPEG diagonal order.
- Apply the pattern to tree levels.

## Recognition Clues

Look for `alternate direction`, `every second line`, `zigzag`, or `level order with reversal`.

## Pattern Summary

The line number controls direction. The line content does not control direction.

## Shape and Edge Behavior

- Row zigzag accepts finite ragged rows.
- Column and diagonal zigzag require a rectangular matrix.
- An empty matrix returns an empty result.

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

(defn alternate-lines [lines]
  (mapv (fn [line-index line]
          (if (even? line-index)
            (vec line)
            (vec (reverse line))))
        (range)
        lines))

(defn row-zigzag [matrix]
  (alternate-lines matrix))

(defn row-zigzag-order [matrix]
  (vec (mapcat identity (row-zigzag matrix))))

(defn transpose [matrix]
  (require-rectangular matrix)
  (if (empty? matrix) [] (apply mapv vector matrix)))

(defn column-zigzag [matrix]
  (alternate-lines (transpose matrix)))

(defn anti-diagonal-lines [matrix]
  (require-rectangular matrix)
  (let [rows (count matrix)
        columns (if-let [row (first matrix)] (count row) 0)]
    (mapv (fn [coordinate-sum]
            (mapv (fn [row]
                    (get-in matrix [row (- coordinate-sum row)]))
                  (range (max 0 (- coordinate-sum (dec columns)))
                         (min rows (inc coordinate-sum)))))
          (range (max 0 (dec (+ rows columns)))))))

(defn diagonal-zigzag [matrix]
  (->> (anti-diagonal-lines matrix)
       (map-indexed
         (fn [coordinate-sum diagonal]
           (if (even? coordinate-sum)
             (reverse diagonal)
             diagonal)))
       (mapcat identity)
       vec))

(defn restore-row-zigzag [values columns]
  (when-not (pos? columns)
    (throw (ex-info "Column count must be positive" {:columns columns})))
  (alternate-lines (partition-all columns values)))

(defn zigzag-levels [root children]
  (loop [level-number 0
         level [root]
         result []]
    (if (empty? level)
      result
      (let [shown (if (even? level-number)
                    level
                    (vec (reverse level)))
            next-level (into [] (mapcat children) level)]
        (recur (inc level-number)
               next-level
               (conj result shown))))))

(def matrix [[1 2 3] [4 5 6] [7 8 9]])

(row-zigzag-order matrix)
;; => [1 2 3 6 5 4 7 8 9]

(diagonal-zigzag matrix)
;; => [1 2 4 7 5 3 6 8 9]

;; Executable checks

(assert (= [1 2 3 6 5 4 7 8 9]
           (row-zigzag-order matrix)))
(assert (= [1 2 4 7 5 3 6 8 9]
           (diagonal-zigzag matrix)))
```

Row zigzag is its own inverse when each row length is known.

### Memory Hooks

- Even line: keep direction.
- Odd line: reverse direction.
- Transpose changes row zigzag into column zigzag.
- Anti-diagonal buckets produce JPEG order.

### Key Insight

Zigzag is a general line pattern. Separate line creation from direction changes.

### Zigzag vs Snake

Zigzag describes alternating line order. Snake adds a requirement: consecutive coordinates must remain adjacent.
