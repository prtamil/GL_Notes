# 15. Convolution Window

## Mental Model

Place a numeric kernel over each position. Multiply matching cells, then add the products.

## Relationship to Cognitive Verb

```text
Combine -> local patch times kernel -> one output value
```

## Clojure Functions and Common Idioms

|Need|Use|
|---|---|
|Cross-correlation|use the kernel as given|
|True convolution|reverse both kernel axes|
|Boundary behavior|zero, clamp, wrap, or reflect policy|
|Separable kernel|one row pass and one column pass|
|Batch calculation|patch rows plus dot products|

## Common Uses

- Blur an image.
- Detect edges.
- Sharpen local detail.
- Apply cellular filters.
- Compute neural network feature maps.

## Hidden Interview Problems

- Distinguish correlation from convolution.
- Calculate output dimensions.
- Normalize a blur kernel.
- Apply a separable kernel in two passes.
- Convert patches to rows before multiplication.

## Recognition Clues

Look for `kernel`, `filter`, `weighted local sum`, `convolution`, or `feature map`.

## Pattern Summary

The output mode depends on stride and padding. Kernel reversal distinguishes convolution from cross-correlation.

## Shape and Edge Behavior

- The matrix and kernel must be finite and rectangular.
- The kernel must contain at least one cell.
- Stride must be positive, and padding must not be negative.
- The functions reject ragged input with `ExceptionInfo`.

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

(defn reflect-index [index size]
  (cond
    (zero? size) nil
    (= size 1) 0
    :else
    (let [period (* 2 (dec size))
          position (mod index period)]
      (if (< position size) position (- period position)))))

(defn sample-cell [matrix [row column] mode fill]
  (let [rows (count matrix)
        columns (if-let [source-row (first matrix)] (count source-row) 0)
        valid? (and (<= 0 row) (< row rows)
                    (<= 0 column) (< column columns))]
    (if valid?
      (get-in matrix [row column])
      (case mode
        :zero fill
        :clamp (get-in matrix [(min (dec rows) (max 0 row))
                               (min (dec columns) (max 0 column))])
        :wrap (get-in matrix [(mod row rows) (mod column columns)])
        :reflect (get-in matrix [(reflect-index row rows)
                                 (reflect-index column columns)])
        (throw (ex-info "Unknown boundary mode" {:mode mode}))))))

(defn output-length [input-size kernel-size stride padding]
  (when (or (neg? input-size) (not (pos? kernel-size))
            (not (pos? stride)) (neg? padding))
    (throw (ex-info "Output dimensions are invalid"
                    {:input-size input-size :kernel-size kernel-size
                     :stride stride :padding padding})))
  (if (> kernel-size (+ input-size (* 2 padding)))
    0
    (inc (quot (- (+ input-size (* 2 padding)) kernel-size)
               stride))))

(defn kernel-product [matrix kernel origin mode]
  (reduce + 0
          (for [kernel-row (range (count kernel))
                kernel-column (range (count (first kernel)))
                :let [coordinate (mapv + origin [kernel-row kernel-column])]]
            (* (sample-cell matrix coordinate mode 0)
               (get-in kernel [kernel-row kernel-column])))))

(defn matrix-shape [matrix]
  [(count matrix)
   (if-let [row (first matrix)] (count row) 0)])

(defn require-kernel [kernel]
  (require-rectangular kernel "Kernel")
  (when (or (empty? kernel) (empty? (first kernel)))
    (throw (ex-info "Kernel must contain at least one cell" {})))
  kernel)

(defn output-origin [output-row output-column stride padding]
  [(- (* output-row stride) padding)
   (- (* output-column stride) padding)])

(defn correlate
  ([matrix kernel] (correlate matrix kernel {}))
  ([matrix kernel {:keys [stride padding mode]
                   :or {stride 1 padding 0 mode :zero}}]
   (require-rectangular matrix "Matrix")
   (require-kernel kernel)
   (when (or (not (pos? stride)) (neg? padding))
     (throw (ex-info "Stride or padding is invalid"
                     {:stride stride :padding padding})))
   (let [[rows columns] (matrix-shape matrix)
         [kernel-rows kernel-columns] (matrix-shape kernel)
         output-rows (output-length rows kernel-rows stride padding)
         output-columns (output-length columns kernel-columns stride padding)]
     (when (and (or (zero? rows) (zero? columns))
                (not= mode :zero)
                (pos? padding))
       (throw (ex-info "This boundary mode needs a nonempty matrix"
                       {:mode mode})))
     (mapv (fn [output-row]
             (mapv (fn [output-column]
                     (kernel-product
                       matrix
                       kernel
                        (output-origin output-row output-column
                                       stride padding)
                       mode))
                   (range output-columns)))
           (range output-rows)))))

(defn flip-kernel [kernel]
  (mapv (comp vec reverse) (reverse kernel)))

(defn convolve
  ([matrix kernel] (convolve matrix kernel {}))
  ([matrix kernel options]
   (correlate matrix (flip-kernel kernel) options)))

(defn normalize-kernel [kernel]
  (require-rectangular kernel "Kernel")
  (let [total (reduce + 0 (mapcat identity kernel))]
    (when (zero? total)
      (throw (ex-info "Kernel sum must not be zero" {})))
    (mapv (fn [row]
            (mapv #(/ % total) row))
          kernel)))

(defn correlate-rows [matrix kernel]
  (require-rectangular matrix "Matrix")
  (when (empty? kernel)
    (throw (ex-info "Kernel must not be empty" {})))
  (let [radius (quot (count kernel) 2)]
    (mapv (fn [row]
            (mapv (fn [column]
                    (reduce + 0
                            (map-indexed
                              (fn [index weight]
                                (* weight
                                   (sample-cell matrix
                                                [row (+ column (- index radius))]
                                                :zero
                                                0)))
                              kernel)))
                  (range (count (first matrix)))))
          (range (count matrix)))))

(defn transpose [matrix]
  (require-rectangular matrix "Matrix")
  (if (empty? matrix) [] (apply mapv vector matrix)))

(defn separable-correlate [matrix row-kernel column-kernel]
  (-> matrix
      (correlate-rows row-kernel)
      transpose
      (correlate-rows column-kernel)
      transpose))

(defn patch-rows [matrix kernel-size stride]
  (require-rectangular matrix "Matrix")
  (when (or (not (pos? kernel-size)) (not (pos? stride)))
    (throw (ex-info "Kernel size and stride must be positive"
                    {:kernel-size kernel-size :stride stride})))
  (let [rows (count matrix)
        columns (if-let [row (first matrix)] (count row) 0)]
    (mapv (fn [[row column]]
            (vec
              (for [row-offset (range kernel-size)
                    column-offset (range kernel-size)]
                (get-in matrix [(+ row row-offset)
                                (+ column column-offset)]))))
          (for [row (range 0 (inc (- rows kernel-size)) stride)
                column (range 0 (inc (- columns kernel-size)) stride)]
            [row column]))))

(def matrix [[1 2 3] [4 5 6] [7 8 9]])
(def edge-kernel [[-1 0 1] [-1 0 1] [-1 0 1]])

(correlate matrix edge-kernel)
;; => [[6]]

(correlate matrix [[1 1] [1 1]])
;; => [[12 16] [24 28]]

;; Executable checks

(assert (= [[6]] (correlate matrix edge-kernel)))
(assert (= [[12 16] [24 28]]
           (correlate matrix [[1 1] [1 1]])))
```

Most machine learning libraries call cross-correlation `convolution`. State whether the kernel is reversed.

### Memory Hooks

- Patch and kernel must have the same shape.
- Multiply matching cells.
- Add all products.
- Reverse both kernel axes for true convolution.

### Key Insight

Convolution is a sliding window with a weighted sum. Boundary policy, stride, padding, and kernel direction define the exact operation.

## The Window Section in One Table

|Pattern|Step|Output|
|---|---|---|
|Sliding window|usually one|one reduced value per placement|
|Tile|window size|independent blocks|
|Patch extraction|configurable|stored windows|
|Convolution|configurable|weighted local sums|
