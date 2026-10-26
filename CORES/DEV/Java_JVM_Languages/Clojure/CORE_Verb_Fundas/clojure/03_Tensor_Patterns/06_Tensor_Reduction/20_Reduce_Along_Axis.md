# 20. Reduce Along an Axis

## Mental Model

A reduction replaces all values along one axis with one summary value.

The reduced axis disappears from the result shape.

```text
[2 3 4] reduce axis 1 -> [2 4]
```

## Relationship to Cognitive Verb

```text
Summarize -> select an axis -> combine its values for every fixed coordinate
```

## Clojure Functions and Common Idioms

|Need|Use|
|---|---|
|Sum|`tensor/reduce-axis` with `dfn/sum`|
|Mean|`tensor/reduce-axis` with `dfn/mean`|
|Maximum|`tensor/reduce-axis` with `dfn/reduce-max`|
|Minimum|`tensor/reduce-axis` with `dfn/reduce-min`|
|Product|`tensor/reduce-axis` with `dfn/reduce-*`|
|Whole tensor|apply a reduction to `dtype/->reader`|

## Shape and Edge Behavior

- A one-axis reduction lowers rank by one.
- Negative axes count from the right.
- Full reduction returns a Clojure scalar.
- Empty sum returns the additive identity when supported.
- Maximum and minimum require at least one value.
- A running scan is not a reduction because it keeps the axis.

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

(defn reduced-shape [shape axis]
  (let [shape (vec shape)
        axis (normalize-axis (count shape) axis)]
    (into (subvec shape 0 axis)
          (subvec shape (inc axis)))))

(defn reduce-axis [t reduce-fn axis]
  (let [shape (vec (dtype/shape t))
        axis (normalize-axis (count shape) axis)]
    (when (= 1 (count shape))
      (throw (ex-info "Use a reader reduction for a scalar result"
                      {:shape shape :axis axis})))
    (tensor/reduce-axis t reduce-fn axis)))

(defn range-axis [t axis]
  (dfn/- (reduce-axis t dfn/reduce-max axis)
         (reduce-axis t dfn/reduce-min axis)))

(def t
  (tensor/reshape
    (dtype/make-container :jvm-heap :int64 (range 24))
    [2 3 4]))

(def sums (reduce-axis t dfn/sum 1))
(def means (tensor/reduce-axis t dfn/mean 1 :float64))

(tensor/->jvm sums)
;; => [[12 15 18 21]
;;     [48 51 54 57]]

(tensor/->jvm means)
;; => [[4.0 5.0 6.0 7.0]
;;     [16.0 17.0 18.0 19.0]]

(assert (= [2 4] (reduced-shape [2 3 4] 1)))
(assert (= [2 3] (reduced-shape [2 3 4] -1)))
(assert (= [2 4] (vec (dtype/shape sums))))
(assert (= [[12 15 18 21] [48 51 54 57]]
           (tensor/->jvm sums)))
(assert (= [[4.0 5.0 6.0 7.0]
            [16.0 17.0 18.0 19.0]]
           (tensor/->jvm means)))

(assert (= [[8 8 8 8] [8 8 8 8]]
           (tensor/->jvm (range-axis t 1))))

;; Full reduction produces a scalar.
(assert (= 276.0 (double (dfn/sum (dtype/->reader t)))))
(assert (= 11.5 (double (dfn/mean (dtype/->reader t)))))
(assert (= 23.0 (double (dfn/reduce-max (dtype/->reader t)))))

;; A scan keeps the shape. This is not a reduction.
(let [flat-scan (dfn/cumsum (dtype/->reader t))]
  (assert (= 24 (count flat-scan)))
  (assert (== 276 (last flat-scan))))

;; Maximum on an empty tensor has no useful identity.
(let [empty-tensor (tensor/->tensor [] {:datatype :int64})]
  (assert (try
            (when (zero? (dtype/ecount empty-tensor))
              (throw (ex-info "Maximum requires a value" {})))
            false
            (catch clojure.lang.ExceptionInfo _ true))))
```

## Common Uses

- Sum losses over samples.
- Average spatial dimensions.
- Find one maximum per feature.
- Count Boolean matches.
- Compute one statistic for each retained coordinate.

## Recognition Clues

Look for `sum along`, `mean per`, `collapse`, `maximum for each`, or `aggregate`.

## Memory Hooks

- Reduction removes its axis.
- Write the axis explicitly.
- Use `-1` for the innermost axis.
- Full reduction gives a scalar.
- Scans keep partial results and preserve shape.

## Key Insight

All one-axis reductions share the same shape rule. Only the summary function changes.

