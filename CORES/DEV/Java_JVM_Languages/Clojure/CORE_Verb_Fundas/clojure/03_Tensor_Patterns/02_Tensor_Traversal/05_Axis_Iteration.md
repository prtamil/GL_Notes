# 5. Axis Iteration

## Mental Model

Iteration removes one outer axis at each step.

A rank-3 tensor yields rank-2 views when you iterate axis zero.

To iterate another axis, move that axis to the front first.

## Relationship to Cognitive Verb

```text
Traverse -> move the selected axis to the front -> visit each sub-tensor
```

## Clojure Functions and Common Idioms

|Need|Use|
|---|---|
|Axis-zero slices|`tensor/slice` with `1`|
|Last-axis slices|`tensor/slice-right` with `1`|
|Another axis|`tensor/transpose`, then `tensor/slice`|
|Slice with index|`map-indexed`|
|All last-axis vectors|`tensor/slice` with `rank - 1`|
|Arithmetic over an axis|prefer a tensor operation|

## Shape and Edge Behavior

- Axis-zero iteration produces `shape[0]` slices.
- Each slice has rank one less than the input.
- Iteration over a zero-sized outer axis produces no slices.
- Each slice is a view and can share storage.
- Axis iteration is useful when the body performs input/output or branching.
- Prefer vectorized operations for numeric work.

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

(defn axis-slices [t axis]
  (let [moved (move-axis t axis 0)]
    (tensor/slice moved 1)))

(def t
  (tensor/reshape
    (dtype/make-container :jvm-heap :int64 (range 24))
    [2 3 4]))

(mapv tensor/->jvm (axis-slices t 0))
;; => [[[0 1 2 3] [4 5 6 7] [8 9 10 11]]
;;     [[12 13 14 15] [16 17 18 19] [20 21 22 23]]]

(mapv tensor/->jvm (axis-slices t 1))
;; => [[[0 1 2 3] [12 13 14 15]]
;;     [[4 5 6 7] [16 17 18 19]]
;;     [[8 9 10 11] [20 21 22 23]]]

(mapv tensor/->jvm (axis-slices t -1))
;; => [[[0 4 8] [12 16 20]]
;;     [[1 5 9] [13 17 21]]
;;     [[2 6 10] [14 18 22]]
;;     [[3 7 11] [15 19 23]]]

(assert (= 2 (count (axis-slices t 0))))
(assert (= 3 (count (axis-slices t 1))))
(assert (= 4 (count (axis-slices t -1))))
(assert (every? #(= [3 4] (vec (dtype/shape %)))
                (axis-slices t 0)))
(assert (every? #(= [2 4] (vec (dtype/shape %)))
                (axis-slices t 1)))

;; Flatten all leading axes and keep the final feature axis.
(let [feature-size (last (dtype/shape t))
      rows (tensor/reshape t
                           [(quot (dtype/ecount t) feature-size)
                            feature-size])]
  (assert (= [6 4] (vec (dtype/shape rows)))))

;; A slice is a view.
(let [source (tensor/reshape
               (dtype/make-container :jvm-heap :int64 (range 24))
               [2 3 4])
      first-slice (first (axis-slices source 0))]
  (tensor/mset! first-slice 0 0 91)
  (assert (= 91 (tensor/mget source 0 0 0))))

;; Numeric reduction does not need an explicit slice loop.
(assert (= [66 210]
           (mapv #(long (dfn/sum (dtype/->reader %)))
                 (axis-slices t 0))))
```

## Common Uses

- Process one batch item at a time.
- Pair inputs with labels.
- Save one image per slice.
- Call an external service for each sample.
- Apply different control flow to each slice.

## Recognition Clues

Look for `for each batch item`, `one channel at a time`, `save each`, or `per slice`.

## Memory Hooks

- Iteration starts on axis zero.
- Move another axis to the front first.
- One step removes one axis.
- Slice values are views.
- Use reductions for arithmetic.

## Key Insight

Axis iteration visits sub-tensors. It does not visit individual values unless the input rank is one.

