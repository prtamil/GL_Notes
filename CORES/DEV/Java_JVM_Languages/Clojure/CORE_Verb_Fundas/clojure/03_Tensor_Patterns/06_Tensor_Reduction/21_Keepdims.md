# 21. Keep Dimensions

## Mental Model

A normal reduction deletes its axis. A keep-dimensions reduction leaves that axis with size one.

```text
[2 3 4] reduce axis 1             -> [2 4]
[2 3 4] reduce axis 1, keep slot  -> [2 1 4]
```

The size-one slot lets the statistic broadcast back over the source tensor.

## Relationship to Cognitive Verb

```text
Summarize and align -> reduce one axis -> restore it with size one
```

## Clojure Functions and Common Idioms

|Need|Use|
|---|---|
|Keep one reduced axis|reduce, insert `1`, reshape|
|Center|subtract a broadcast mean|
|Normalize|divide by a broadcast sum|
|Stable softmax|subtract max, exponentiate, divide by sum|
|Return to lower rank|squeeze the named size-one axis|

## Shape and Edge Behavior

- Rank stays unchanged.
- The reduced axis becomes size one.
- Value count matches the ordinary reduction.
- Broadcasting back restores the source shape.
- Keep dimensions when a statistic meets its source again.
- A final scalar metric does not need retained axes.

## Clojure Recipe Book

```clojure
(require '[tech.v3.datatype :as dtype]
         '[tech.v3.datatype.functional :as dfn]
         '[tech.v3.tensor :as tensor])

(defn normalize-axis [rank axis]
  (let [axis (if (neg? axis) (+ rank axis) axis)]
    (when-not (< -1 axis rank)
      (throw (ex-info "Axis is outside the tensor rank"
                      {:axis axis :rank rank})))
    axis))

(defn insert-at [values index value]
  (vec (concat (subvec (vec values) 0 index)
               [value]
               (subvec (vec values) index))))

(defn reduce-keep-dims [t reduce-fn axis]
  (let [shape (vec (dtype/shape t))
        axis (normalize-axis (count shape) axis)]
    (when (= 1 (count shape))
      (throw (ex-info "Rank-1 keep-dim reduction needs a scalar wrapper"
                      {:shape shape})))
    (let [reduced (tensor/reduce-axis t reduce-fn axis)]
      (tensor/reshape reduced
                      (insert-at (dtype/shape reduced) axis 1)))))

(defn broadcast-like [small large]
  (tensor/broadcast small (dtype/shape large)))

(defn center-axis [t axis]
  (let [means (reduce-keep-dims t dfn/mean axis)]
    (dfn/- t (broadcast-like means t))))

(defn normalize-axis-sum [t axis]
  (let [sums (reduce-keep-dims t dfn/sum axis)]
    (dfn// t (broadcast-like sums t))))

(defn softmax [t axis]
  (let [maxima (reduce-keep-dims t dfn/reduce-max axis)
        shifted (dfn/- t (broadcast-like maxima t))
        exponents (dfn/exp shifted)
        totals (reduce-keep-dims exponents dfn/sum axis)]
    (dfn// exponents (broadcast-like totals exponents))))

(def t
  (tensor/reshape
    (dtype/make-container :jvm-heap :float64 (range 24))
    [2 3 4]))

(let [sums (reduce-keep-dims t dfn/sum 1)]
  (assert (= [2 1 4] (vec (dtype/shape sums))))
  (assert (= [[[12.0 15.0 18.0 21.0]]
              [[48.0 51.0 54.0 57.0]]]
             (tensor/->jvm sums))))

;; Center each axis-1 group.
(let [centered (center-axis t 1)
      checks (tensor/reduce-axis centered dfn/sum 1)]
  (assert (every? #(< (Math/abs (double %)) 1.0e-12)
                  (dtype/->reader checks))))

;; Normalize each row of a matrix.
(let [matrix (tensor/reshape
               (dtype/make-container :jvm-heap :float64 (range 1 13))
               [3 4])
      normalized (normalize-axis-sum matrix 1)
      checks (tensor/reduce-axis normalized dfn/sum 1)]
  (assert (every? #(< (Math/abs (- 1.0 (double %))) 1.0e-12)
                  (dtype/->reader checks))))

;; Stable softmax works for large shifted values.
(let [values (tensor/->tensor [[1.0 2.0 3.0]
                               [1000.0 1001.0 1002.0]]
                              {:datatype :float64})
      probabilities (softmax values 1)
      row-sums (tensor/reduce-axis probabilities dfn/sum 1)]
  (assert (every? #(Double/isFinite (double %))
                  (dtype/->reader probabilities)))
  (assert (every? #(< (Math/abs (- 1.0 (double %))) 1.0e-12)
                  (dtype/->reader row-sums)))
  (assert (< (Math/abs (- (tensor/mget probabilities 0 2)
                           (tensor/mget probabilities 1 2)))
             1.0e-12)))
```

## Common Uses

- Center features.
- Normalize rows or channels.
- Standardize batches.
- Implement stable softmax.
- Reuse reduced statistics against source data.

## Recognition Clues

Look for `broadcast back`, `normalize`, `center`, `softmax`, `keep rank`, or `retain axis`.

## Memory Hooks

- Reduction changes the axis size to one.
- Rank stays unchanged.
- Broadcast the statistic back to the source shape.
- Stable softmax keeps both max and sum axes.
- Keep the slot when the statistic meets the source.

## Key Insight

Keeping dimensions records where a statistic came from. That record prevents later alignment errors.

