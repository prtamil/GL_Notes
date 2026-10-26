# 27. Prefix Sum and Integral Image

## Mental Model

Store the sum of every top-left rectangle. Then calculate any rectangle sum from four table cells.

## Relationship to Cognitive Verb

```text
Precompute -> cumulative table -> constant-time range query
```

## Clojure Functions and Common Idioms

|Need|Use|
|---|---|
|One-dimensional prefix|`reductions`|
|Two-dimensional prefix|inclusion and exclusion|
|Rectangle sum|bottom-right minus two sides plus overlap|
|Fast box mean|rectangle sum divided by area|
|Fast fixed window|query every legal origin|
|Fast range updates|difference array|

## Common Uses

- Answer many rectangle-sum queries.
- Count marked cells in an area.
- Calculate box blur values.
- Find a fixed-size maximum-sum block.
- Apply many offline range additions.

## Hidden Interview Problems

- Use a leading row and column of zeros.
- Keep inclusive and exclusive coordinates separate.
- Find a maximum-sum rectangle of any size.
- Use XOR instead of addition.
- Know when prefix maxima cannot work.

## Recognition Clues

Look for `many rectangle queries`, `static matrix`, `area sum`, `integral image`, or `four corners`.

## Pattern Summary

Build time is linear in the cell count. Each rectangle-sum query then takes constant time.

## Shape and Edge Behavior

- Matrix functions expect a finite rectangular matrix.
- An empty matrix creates a prefix table that contains one zero.
- Window dimensions must be positive where a window is required.
- Matrix functions reject ragged rows with `ExceptionInfo`.

## Clojure Recipe Book

```clojure
(defn rectangular? [matrix]
  (or (empty? matrix)
      (apply = (map count matrix))))

(defn require-rectangular [matrix label]
  (when-not (rectangular? matrix)
    (throw (ex-info (str label " must be rectangular")
                    {:row-lengths (mapv count matrix)})))
  matrix)

;; Core prefix-sum recipes

(defn prefix-sums-1d [values]
  (vec (reductions + 0 values)))

(defn range-sum-1d [prefix start end-exclusive]
  (when-not (and (<= 0 start) (<= start end-exclusive)
                 (< end-exclusive (count prefix)))
    (throw (ex-info "Range is outside the prefix vector"
                    {:start start :end-exclusive end-exclusive})))
  (- (nth prefix end-exclusive)
     (nth prefix start)))

(defn summed-area-table [matrix]
  (require-rectangular matrix "Matrix")
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

(defn rectangle-sum [table row column height width]
  (require-rectangular table "Prefix table")
  (let [bottom (+ row height)
        right (+ column width)
        table-rows (count table)
        table-columns (if-let [source-row (first table)]
                        (count source-row)
                        0)]
    (when-not (and (<= 0 row) (<= 0 column)
                   (<= 0 height) (<= 0 width)
                   (< bottom table-rows)
                   (< right table-columns))
      (throw (ex-info "Rectangle is outside the source matrix"
                      {:row row :column column
                       :height height :width width})))
    (+ (get-in table [bottom right])
       (get-in table [row column])
       (- (get-in table [row right]))
       (- (get-in table [bottom column])))))

(defn rectangle-sum-corners [table row-1 column-1 row-2 column-2]
  (rectangle-sum table
                 row-1
                 column-1
                 (inc (- row-2 row-1))
                 (inc (- column-2 column-1))))

(defn brute-rectangle-sum [matrix row column height width]
  (require-rectangular matrix "Matrix")
  (let [rows (count matrix)
        columns (if-let [source-row (first matrix)] (count source-row) 0)]
    (when-not (and (<= 0 row) (<= 0 column)
                   (<= 0 height) (<= 0 width)
                   (<= (+ row height) rows)
                   (<= (+ column width) columns))
      (throw (ex-info "Rectangle is outside the matrix"
                      {:row row :column column
                       :height height :width width}))))
  (reduce + 0
          (for [source-row (range row (+ row height))
                source-column (range column (+ column width))]
            (get-in matrix [source-row source-column]))))

(defn row-prefix-sums [matrix]
  (mapv prefix-sums-1d matrix))

(defn box-mean [matrix table row column radius]
  (require-rectangular matrix "Matrix")
  (when (neg? radius)
    (throw (ex-info "Radius must not be negative" {:radius radius})))
  (let [rows (count matrix)
        columns (if-let [source-row (first matrix)] (count source-row) 0)
        _ (when-not (and (<= 0 row) (< row rows)
                         (<= 0 column) (< column columns))
            (throw (ex-info "Coordinate is outside the matrix"
                            {:coordinate [row column]})))
        top (max 0 (- row radius))
        left (max 0 (- column radius))
        bottom (min rows (inc (+ row radius)))
        right (min columns (inc (+ column radius)))
        height (- bottom top)
        width (- right left)]
    (/ (rectangle-sum table top left height width)
       (* height width))))

(defn maximum-fixed-window [matrix height width]
  (require-rectangular matrix "Matrix")
  (when (or (not (pos? height)) (not (pos? width)))
    (throw (ex-info "Window dimensions must be positive"
                    {:height height :width width})))
  (let [rows (count matrix)
        columns (if-let [row (first matrix)] (count row) 0)
        table (summed-area-table matrix)
        candidates
        (for [row (range (inc (- rows height)))
              column (range (inc (- columns width)))]
          {:origin [row column]
           :height height
           :width width
           :sum (rectangle-sum table row column height width)})]
    (when (seq candidates)
      (apply max-key :sum candidates))))

;; Advanced scan recipes

(defn kadane [values]
  (when (seq values)
    (loop [index 1
           current-sum (first values)
           current-start 0
           best {:sum (first values) :start 0 :end 0}]
      (if (= index (count values))
        best
        (let [value (nth values index)
              restart? (> value (+ current-sum value))
              next-sum (if restart? value (+ current-sum value))
              next-start (if restart? index current-start)
              next-best (if (> next-sum (:sum best))
                          {:sum next-sum :start next-start :end index}
                          best)]
          (recur (inc index) next-sum next-start next-best))))))

(defn maximum-sum-submatrix [matrix]
  (require-rectangular matrix "Matrix")
  (let [rows (count matrix)
        columns (if-let [row (first matrix)] (count row) 0)]
    (when (and (pos? rows) (pos? columns))
      (let [candidates
            (mapcat
              (fn [top]
                (loop [bottom top
                       column-sums (vec (repeat columns 0))
                       result []]
                  (if (= bottom rows)
                    result
                    (let [next-sums (mapv + column-sums (nth matrix bottom))
                          best-row (kadane next-sums)]
                      (recur (inc bottom)
                             next-sums
                             (conj result
                                   {:origin [top (:start best-row)]
                                    :height (inc (- bottom top))
                                    :width (inc (- (:end best-row)
                                                   (:start best-row)))
                                    :sum (:sum best-row)}))))))
              (range rows))]
        (apply max-key :sum candidates)))))

(defn prefix-max-table [matrix]
  (require-rectangular matrix "Matrix")
  (let [rows (count matrix)
        columns (if-let [row (first matrix)] (count row) 0)]
    (mapv (fn [row]
            (mapv (fn [column]
                    (apply max
                           (for [source-row (range (inc row))
                                 source-column (range (inc column))]
                             (get-in matrix [source-row source-column]))))
                  (range columns)))
          (range rows))))

(defn xor-area-table [matrix]
  (require-rectangular matrix "Matrix")
  (let [rows (count matrix)
        columns (if-let [row (first matrix)] (count row) 0)
        blank (vec (repeat (inc rows)
                           (vec (repeat (inc columns) 0))))]
    (reduce (fn [table [row column]]
              (assoc-in table
                        [(inc row) (inc column)]
                        (bit-xor (get-in matrix [row column])
                                 (get-in table [row (inc column)])
                                 (get-in table [(inc row) column])
                                 (get-in table [row column]))))
            blank
            (for [row (range rows)
                  column (range columns)]
              [row column]))))

(defn rectangle-xor [table row column height width]
  (let [bottom (+ row height)
        right (+ column width)]
    (bit-xor (get-in table [bottom right])
             (get-in table [row right])
             (get-in table [bottom column])
             (get-in table [row column]))))

;; Difference-array recipes

(defn range-add-1d [size operations]
  (when (neg? size)
    (throw (ex-info "Size must not be negative" {:size size})))
  (doseq [[start end-inclusive _] operations]
    (when-not (and (<= 0 start) (<= start end-inclusive)
                   (< end-inclusive size))
      (throw (ex-info "Range update is outside the vector"
                      {:start start :end-inclusive end-inclusive
                       :size size}))))
  (let [difference
        (reduce (fn [result [start end-inclusive amount]]
                  (-> result
                      (update start + amount)
                      (update (inc end-inclusive) - amount)))
                (vec (repeat (inc size) 0))
                operations)]
    (vec (take size (reductions + difference)))))

(defn valid-area-update? [rows columns
                          [row-1 column-1 row-2 column-2 _]]
  (and (<= 0 row-1) (<= row-1 row-2) (< row-2 rows)
       (<= 0 column-1) (<= column-1 column-2) (< column-2 columns)))

(defn add-area-update [difference
                       [row-1 column-1 row-2 column-2 amount]]
  (-> difference
      (update-in [row-1 column-1] + amount)
      (update-in [(inc row-2) column-1] - amount)
      (update-in [row-1 (inc column-2)] - amount)
      (update-in [(inc row-2) (inc column-2)] + amount)))

(defn materialize-difference-cell [result [row column]]
  (let [above (if (pos? row)
                (get-in result [(dec row) column])
                0)
        left (if (pos? column)
               (get-in result [row (dec column)])
               0)
        overlap (if (and (pos? row) (pos? column))
                  (get-in result [(dec row) (dec column)])
                  0)
        value (+ (get-in result [row column]) above left (- overlap))]
    (assoc-in result [row column] value)))

(defn take-matrix-shape [matrix rows columns]
  (mapv #(subvec % 0 columns)
        (subvec matrix 0 rows)))

(defn range-add-2d [rows columns operations]
  (when (or (neg? rows) (neg? columns))
    (throw (ex-info "Matrix dimensions must not be negative"
                    {:rows rows :columns columns})))
  (doseq [[row-1 column-1 row-2 column-2 _] operations]
    (when-not (valid-area-update?
                rows columns
                [row-1 column-1 row-2 column-2 nil])
      (throw (ex-info "Range update is outside the matrix"
                      {:from [row-1 column-1]
                       :to [row-2 column-2]
                       :shape [rows columns]}))))
  (let [blank (vec (repeat (inc rows)
                           (vec (repeat (inc columns) 0))))
        difference
        (reduce add-area-update blank operations)
        materialized
        (reduce materialize-difference-cell
                difference
                (for [row (range rows)
                      column (range columns)]
                  [row column]))]
    (take-matrix-shape materialized rows columns)))

(def matrix
  [[1  2  3  4]
   [5  6  7  8]
   [9 10 11 12]
   [13 14 15 16]])

(def table (summed-area-table matrix))

(rectangle-sum table 1 1 2 2)
;; => 34

(maximum-fixed-window matrix 2 2)
;; => {:origin [2 2], :height 2, :width 2, :sum 54}

(range-add-1d 6 [[0 2 3] [2 4 1] [5 5 10]])
;; => [3 3 4 1 1 10]

;; Executable checks

(assert (= 34 (rectangle-sum table 1 1 2 2)))
(assert (= {:origin [2 2] :height 2 :width 2 :sum 54}
           (maximum-fixed-window matrix 2 2)))
(assert (= [3 3 4 1 1 10]
           (range-add-1d 6 [[0 2 3] [2 4 1] [5 5 10]])))
```

Prefix maximum tables cannot answer arbitrary rectangle maxima. Maximum has no inverse that removes two unwanted areas.

Prefix tables suit static data. Use a Fenwick tree or segment tree when queries and updates are interleaved.

Large floating-point prefixes can lose small differences. Prefer exact integers or stable numeric methods when precision matters.

### Memory Hooks

- Add a leading zero border.
- Query with four corners.
- Use `D - B - C + A` for sums.
- Prefix tables speed queries.
- Difference tables speed offline updates.

### Key Insight

Prefix sums precompute reusable overlap. They work when the operation has an inverse, such as subtraction or XOR.

## Prefix Sum vs the Window Patterns

The prefix table is an accelerator. It turns each sum window from an area scan into four table reads.
