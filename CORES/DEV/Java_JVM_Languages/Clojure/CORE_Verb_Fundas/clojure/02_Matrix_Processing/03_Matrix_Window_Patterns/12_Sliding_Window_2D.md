# 12. Sliding Window in Two Dimensions

## Mental Model

Place a fixed rectangle at every valid top-left position. Reduce or test the cells inside each placement.

## Relationship to Cognitive Verb

```text
Scan -> place window -> calculate result -> move by stride
```

## Clojure Functions and Common Idioms

|Need|Use|
|---|---|
|Legal positions|two stepped `range` values|
|Extract a window|`subvec` inside `mapv`|
|Reduce a window|reduce each row, then reduce the row results|
|Fast sum|summed-area table|
|Fast maximum|two one-dimensional deque passes|
|Find a pattern|compare each extracted window|

## Common Uses

- Find a maximum-sum block.
- Search for a small pattern.
- Calculate local sums or averages.
- Find solid regions.
- Scan terrain or image data.

## Hidden Interview Problems

- Use a rectangular window.
- Use a stride larger than one.
- Find every matching placement.
- Reuse overlap with a prefix table.
- Apply a monotonic queue for window maxima.

## Recognition Clues

Look for `every submatrix`, `fixed rectangle`, `slide`, `placement`, or `local window`.

## Pattern Summary

A valid window never crosses an edge. A large window has no valid position.

## Shape and Edge Behavior

- The functions expect a finite rectangular matrix.
- Window dimensions and stride must be positive.
- A window larger than the matrix has no positions.
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

(defn window-positions [rows columns height width stride]
  (when (or (neg? rows) (neg? columns)
            (not (pos? height)) (not (pos? width))
            (not (pos? stride)))
    (throw (ex-info "Dimensions and stride are invalid"
                    {:rows rows :columns columns
                     :height height :width width :stride stride})))
  (vec
    (for [row (range 0 (inc (- rows height)) stride)
          column (range 0 (inc (- columns width)) stride)]
      [row column])))

(defn window-at [matrix [row column] height width]
  (require-rectangular matrix)
  (let [rows (count matrix)
        columns (if-let [source-row (first matrix)] (count source-row) 0)]
    (when-not (and (pos? height) (pos? width)
                   (<= 0 row) (<= (+ row height) rows)
                   (<= 0 column) (<= (+ column width) columns))
      (throw (ex-info "Window is outside the matrix"
                      {:origin [row column]
                       :height height :width width})))
    (mapv (fn [source-row]
            (subvec (vec source-row) column (+ column width)))
          (subvec (vec matrix) row (+ row height)))))

(defn sliding-windows [matrix height width stride]
  (require-rectangular matrix)
  (let [rows (count matrix)
        columns (if-let [row (first matrix)] (count row) 0)]
    (mapv (fn [position]
            {:origin position
             :values (window-at matrix position height width)})
          (window-positions rows columns height width stride))))

(defn window-sum [window]
  (reduce + 0 (map #(reduce + 0 %) window)))

(defn window-sums [matrix height width stride]
  (mapv (fn [{:keys [origin values]}]
          {:origin origin
           :sum (window-sum values)})
        (sliding-windows matrix height width stride)))

(defn summed-area-table [matrix]
  (require-rectangular matrix)
  (let [rows (count matrix)
        columns (if-let [row (first matrix)] (count row) 0)
        blank (vec (repeat (inc rows)
                           (vec (repeat (inc columns) 0))))]
    (reduce (fn [table [row column]]
              (assoc-in table
                        [(inc row) (inc column)]
                        (+ (get-in matrix [row column])
                           (get-in table [row (inc column)])
                           (get-in table [(inc row) column])
                           (- (get-in table [row column])))))
            blank
            (for [row (range rows)
                  column (range columns)]
              [row column]))))

(defn rectangle-sum [table [row column] height width]
  (let [bottom (+ row height)
        right (+ column width)]
    (+ (get-in table [bottom right])
       (get-in table [row column])
       (- (get-in table [row right]))
       (- (get-in table [bottom column])))))

(defn fast-window-sums [matrix height width stride]
  (require-rectangular matrix)
  (let [rows (count matrix)
        columns (if-let [row (first matrix)] (count row) 0)
        table (summed-area-table matrix)]
    (mapv (fn [position]
            {:origin position
             :sum (rectangle-sum table position height width)})
          (window-positions rows columns height width stride))))

(defn maximum-sum-window [matrix height width]
  (when-let [windows (seq (fast-window-sums matrix height width 1))]
    (apply max-key :sum windows)))

(defn all-ones-window-origins [matrix size]
  (->> (fast-window-sums matrix size size 1)
       (filter #(= (* size size) (:sum %)))
       (mapv :origin)))

(defn find-pattern [matrix pattern]
  (require-rectangular matrix)
  (require-rectangular pattern)
  (let [height (count pattern)
        width (if-let [row (first pattern)] (count row) 0)]
    (when (or (zero? height) (zero? width))
      (throw (ex-info "Pattern must contain at least one cell" {})))
    (->> (sliding-windows matrix height width 1)
         (filter #(= pattern (:values %)))
         (mapv :origin))))

;; This advanced recipe uses a monotonic deque.

(defn sliding-maximums-1d [values size]
  (when-not (pos? size)
    (throw (ex-info "Window size must be positive" {:size size})))
  (let [values (vec values)]
    (if (> size (count values))
      []
      (let [candidate-indexes (java.util.ArrayDeque.)
            maximums (java.util.ArrayList.)]
        (dotimes [index (count values)]
          (while (and (not (.isEmpty candidate-indexes))
                      (<= (.peekFirst candidate-indexes) (- index size)))
            (.removeFirst candidate-indexes))
          (while (and (not (.isEmpty candidate-indexes))
                      (<= (nth values (.peekLast candidate-indexes))
                          (nth values index)))
            (.removeLast candidate-indexes))
          (.addLast candidate-indexes index)
          (when (>= index (dec size))
            (.add maximums
                  (nth values (.peekFirst candidate-indexes)))))
        (vec maximums)))))

(defn maximums-in-each-row [matrix width]
  (mapv #(sliding-maximums-1d % width) matrix))

(defn transpose [matrix]
  (require-rectangular matrix)
  (if (empty? matrix) [] (apply mapv vector matrix)))

(defn sliding-maximums-2d [matrix height width]
  (require-rectangular matrix)
  (when (or (not (pos? height)) (not (pos? width)))
    (throw (ex-info "Window dimensions must be positive"
                    {:height height :width width})))
  (let [row-maximums (maximums-in-each-row matrix width)]
    (if (or (empty? row-maximums) (empty? (first row-maximums)))
      []
      (transpose
        (maximums-in-each-row (transpose row-maximums) height)))))

(def matrix
  [[1  2  3  4]
   [5  6  7  8]
   [9 10 11 12]
   [13 14 15 16]])

(window-at matrix [1 1] 2 2)
;; => [[6 7] [10 11]]

(maximum-sum-window matrix 2 2)
;; => {:origin [2 2], :sum 54}

(sliding-maximums-2d matrix 2 2)
;; => [[6 7 8] [10 11 12] [14 15 16]]

;; Executable checks

(assert (= [[6 7] [10 11]] (window-at matrix [1 1] 2 2)))
(assert (= {:origin [2 2] :sum 54}
           (maximum-sum-window matrix 2 2)))
(assert (= [[6 7 8] [10 11 12] [14 15 16]]
           (sliding-maximums-2d matrix 2 2)))
```

Naive reduction reads every cell in each window. A summed-area table gives each sum with four table reads.

`sliding-maximums-2d` uses one horizontal pass and one vertical pass.

### Memory Hooks

- Position means the top-left corner.
- Size controls the window.
- Stride controls the jump.
- The reduction controls the answer.

### Key Insight

Overlapping windows repeat work. Use a reusable summary when the reduction supports one.

## Sliding Window vs Neighborhood

A window starts at a top-left coordinate. A neighborhood is centered on a cell and needs an edge policy.
