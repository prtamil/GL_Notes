# 22. Multi-Axis Reduction

## Mental Model

A multi-axis reduction removes every listed axis.

```text
[2 3 4] reduce axes [1 2] -> [2]
```

Reduce axes from highest to lowest when the library accepts one axis at a time. This order prevents axis renumbering.

## Relationship to Cognitive Verb

```text
Summarize regions -> name all reduced axes -> remove them as one logical operation
```

## Clojure Functions and Common Idioms

|Need|Use|
|---|---|
|Normalize axes|convert negatives and reject duplicates|
|Avoid renumbering|reduce axes in descending order|
|Keep slots|reshape reduced output with ones|
|All axes but one|remove the retained axis from `(range rank)`|
|Global pooling|reduce spatial axes|
|Full reduction|reduce the flat reader to a scalar|

## Shape and Edge Behavior

- Each distinct reduced axis lowers rank by one.
- Axis order does not change the result.
- Duplicate axes are invalid.
- Negative axes count from the right.
- Reducing every axis returns a scalar.
- Retained mode changes each reduced axis size to one.

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

(defn normalize-axes [rank axes]
  (let [axes (mapv #(normalize-axis rank %) axes)]
    (when-not (= (count axes) (count (distinct axes)))
      (throw (ex-info "Reduction axes must be distinct"
                      {:axes axes})))
    (vec (sort axes))))

(defn reduced-shape [shape axes]
  (let [shape (vec shape)
        axes (set (normalize-axes (count shape) axes))]
    (into []
          (keep-indexed (fn [axis size]
                          (when-not (axes axis) size)))
          shape)))

(defn reduce-axes [t reduce-fn axes]
  (let [rank (count (dtype/shape t))
        axes (normalize-axes rank axes)]
    (cond
      (empty? axes) t
      (= rank (count axes)) (reduce-fn (dtype/->reader t))
      :else (reduce (fn [current axis]
                      (tensor/reduce-axis current reduce-fn axis))
                    t
                    (reverse axes)))))

(defn reduce-axes-keep-dims [t reduce-fn axes]
  (let [shape (vec (dtype/shape t))
        axes (normalize-axes (count shape) axes)
        axis-set (set axes)
        target-shape (mapv (fn [axis size]
                             (if (axis-set axis) 1 size))
                           (range (count shape))
                           shape)
        reduced (reduce-axes t reduce-fn axes)]
    (if (number? reduced)
      (tensor/reshape
        (tensor/->tensor [reduced]
                         {:datatype (dtype/elemwise-datatype t)})
        target-shape)
      (tensor/reshape reduced target-shape))))

(defn all-axes-but [rank retained-axis]
  (let [retained-axis (normalize-axis rank retained-axis)]
    (vec (remove #{retained-axis} (range rank)))))

(def t
  (tensor/reshape
    (dtype/make-container :jvm-heap :int64 (range 24))
    [2 3 4]))

(assert (= [2] (reduced-shape [2 3 4] [1 2])))
(assert (= [4] (reduced-shape [2 3 4] [0 1])))
(assert (= [0 2] (all-axes-but 3 1)))

(let [totals (reduce-axes t dfn/sum [1 2])]
  (assert (= [2] (vec (dtype/shape totals))))
  (assert (= [66 210] (dtype/->vector totals))))

;; Axis order does not change an associative reduction.
(assert (= (dtype/->vector (reduce-axes t dfn/sum [0 2]))
           (dtype/->vector (reduce-axes t dfn/sum [2 0]))))

;; Keep every reduced slot for later broadcasting.
(let [totals (reduce-axes-keep-dims t dfn/sum [1 2])]
  (assert (= [2 1 1] (vec (dtype/shape totals))))
  (assert (= [66 210] (dtype/->vector totals))))

;; Reducing all axes returns a scalar.
(assert (= 276.0 (double (reduce-axes t dfn/sum [0 1 2]))))

;; Global average pooling keeps batch and channel axes.
(let [images (tensor/reshape
               (dtype/make-container :jvm-heap :float64 (range 48))
               [2 3 2 4])
      pooled (reduce-axes images dfn/mean [2 3])]
  (assert (= [2 3] (vec (dtype/shape pooled)))))

(assert (try
          (normalize-axes 3 [1 -2])
          false
          (catch clojure.lang.ExceptionInfo _ true)))
```

Sum, maximum, minimum, any, and all compose across axes. Mean composes only across equal-size groups. Standard deviation does not compose this way.

## Common Uses

- Global average pooling.
- Dataset channel statistics.
- Reduce every axis except features.
- Sum spatial volumes.
- Create per-sample summaries.

## Recognition Clues

Look for `height and width`, `all but channel`, `several dimensions`, `global pool`, or `collapse spatial axes`.

## Memory Hooks

- Normalize all axis names first.
- Reject duplicates.
- Reduce from right to left.
- Keep slots with size one when broadcasting follows.
- Full reduction returns a scalar.

## Key Insight

Multi-axis reduction names the original axes once. Descending execution preserves those names during sequential library calls.

