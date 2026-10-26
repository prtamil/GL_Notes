# 2. Axes

## Mental Model

An axis is a position in the shape vector.

```text
shape = [2 3 4]
         0 1 2   axes
```

To operate along one axis, vary that index and hold the other indices fixed.

A reduction removes the selected axis.

```text
reduce axis 0   [2 3 4] -> [3 4]
reduce axis 1   [2 3 4] -> [2 4]
reduce axis 2   [2 3 4] -> [2 3]
```

## Relationship to Cognitive Verb

```text
Orient -> select a direction -> operate along that axis
```

## Clojure Functions and Common Idioms

|Need|Use|
|---|---|
|Reduce one axis|`tensor/reduce-axis`|
|Innermost axis|`-1` after normalization|
|Complete reduction|`dfn/sum` on a tensor reader|
|Predict result shape|remove the selected shape entry|
|Move an axis|build a permutation and call `tensor/transpose`|
|Iterate outer slices|`tensor/slice`|

## Shape and Edge Behavior

- Axis zero is the outermost axis.
- Axis `-1` is the innermost axis.
- Valid axes are from `(- rank)` through `(rank - 1)`.
- Reducing an empty axis requires an identity or an explicit policy.
- `tensor/reduce-axis` must leave at least one tensor axis.
- Use a direct functional reduction when the result is a scalar.

## Clojure Recipe Book

```clojure
(require '[tech.v3.datatype :as dtype]
         '[tech.v3.datatype.functional :as dfn]
         '[tech.v3.tensor :as tensor])

(defn normalize-axis [rank axis]
  (let [normalized (if (neg? axis) (+ rank axis) axis)]
    (when-not (< -1 normalized rank)
      (throw (ex-info "Axis is outside the tensor rank"
                      {:axis axis :rank rank})))
    normalized))

(defn shape-without-axis [shape axis]
  (let [axis (normalize-axis (count shape) axis)]
    (into (subvec (vec shape) 0 axis)
          (subvec (vec shape) (inc axis)))))

(defn move-axis-permutation [rank source destination]
  (let [source (normalize-axis rank source)
        destination (normalize-axis rank destination)
        remaining (vec (remove #{source} (range rank)))]
    (vec (concat (subvec remaining 0 destination)
                 [source]
                 (subvec remaining destination)))))

(defn move-axis [t source destination]
  (tensor/transpose
    t
    (move-axis-permutation (count (dtype/shape t))
                           source
                           destination)))

(def t
  (tensor/reshape
    (dtype/make-container :jvm-heap :int64 (range 24))
    [2 3 4]))

(def sum-axis-0 (tensor/reduce-axis t dfn/sum 0))
(def sum-axis-1 (tensor/reduce-axis t dfn/sum 1))
(def sum-axis-2 (tensor/reduce-axis t dfn/sum 2))

(tensor/->jvm sum-axis-0)
;; => [[12 14 16 18]
;;     [20 22 24 26]
;;     [28 30 32 34]]

(tensor/->jvm sum-axis-1)
;; => [[12 15 18 21]
;;     [48 51 54 57]]

(tensor/->jvm sum-axis-2)
;; => [[6 22 38]
;;     [54 70 86]]

(dfn/sum (dtype/->reader t))
;; => 276.0

(assert (= 0 (normalize-axis 3 -3)))
(assert (= 2 (normalize-axis 3 -1)))
(assert (= [3 4] (shape-without-axis [2 3 4] 0)))
(assert (= [2 4] (shape-without-axis [2 3 4] 1)))
(assert (= [2 3] (shape-without-axis [2 3 4] -1)))

(assert (= [3 4] (vec (dtype/shape sum-axis-0))))
(assert (= [2 4] (vec (dtype/shape sum-axis-1))))
(assert (= [2 3] (vec (dtype/shape sum-axis-2))))

(assert (= [[12 14 16 18]
            [20 22 24 26]
            [28 30 32 34]]
           (tensor/->jvm sum-axis-0)))

(assert (= [[12 15 18 21]
            [48 51 54 57]]
           (tensor/->jvm sum-axis-1)))

(assert (= [[6 22 38]
            [54 70 86]]
           (tensor/->jvm sum-axis-2)))

(assert (= 276.0 (double (dfn/sum (dtype/->reader t)))))

;; Move axis 1 to the front. The shape follows the same permutation.
(let [moved (move-axis t 1 0)]
  (assert (= [3 2 4] (vec (dtype/shape moved)))))

;; Invalid axes fail before the library operation starts.
(assert (try
          (normalize-axis 3 3)
          false
          (catch clojure.lang.ExceptionInfo _ true)))
```

## Common Uses

- Reduce spatial axes in an image batch.
- Normalize the final feature axis.
- Move a channel axis.
- Compute statistics for each sample.
- Preserve an axis convention across functions.

## Recognition Clues

Look for `along`, `per channel`, `per sample`, `last dimension`, or `collapse`.

## Memory Hooks

- Axis means a position in the shape.
- Negative axes count from the right.
- Reduction removes the chosen shape entry.
- Axis zero is the default iteration direction.
- Move an axis by permuting the axes.

## Key Insight

An axis is not a loop. It names which index changes while all other indices stay fixed.

