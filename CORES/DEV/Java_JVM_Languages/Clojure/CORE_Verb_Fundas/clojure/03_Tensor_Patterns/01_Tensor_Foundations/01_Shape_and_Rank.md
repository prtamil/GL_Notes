# 1. Shape and Rank

## Mental Model

A tensor has a rank and a shape.

- Rank is the number of axes.
- Shape gives the size of each axis.
- Element count is the product of the shape values.

```text
rank 0   scalar   5                         shape []
rank 1   vector   [1 2 3]                   shape [3]
rank 2   matrix   [[1 2 3] [4 5 6]]         shape [2 3]
rank 3   tensor   two blocks of 3 by 4      shape [2 3 4]
```

A tensor must be rectangular. All children at one depth must have the same shape.

## Relationship to Cognitive Verb

```text
Describe -> measure each axis -> state the shape
```

## Clojure Functions and Common Idioms

|Need|Use|
|---|---|
|Tensor shape|`dtype/shape`|
|Element count|`dtype/ecount`|
|Element type|`dtype/elemwise-datatype`|
|Tensor from nested data|`tensor/->tensor`|
|Typed storage|`:datatype` option|
|New shape|`tensor/reshape`|
|Nested Clojure value|`tensor/->jvm`|

## Shape and Edge Behavior

- A scalar has conceptual shape `[]` and size 1.
- An empty vector has shape `[0]` and size 0.
- An empty axis prevents inference of deeper axes.
- Ragged or mixed-depth input is invalid.
- Shape inference consumes finite input.
- `dtype-next` tensor buffers represent rank 1 and higher.
- This course uses a Clojure scalar for rank 0.

## Clojure Recipe Book

```clojure
(require '[tech.v3.datatype :as dtype]
         '[tech.v3.tensor :as tensor])

(defn nested-shape [value]
  (if (sequential? value)
    (let [items (vec value)]
      (if (empty? items)
        [0]
        (let [child-shapes (mapv nested-shape items)
              expected (first child-shapes)]
          (when-not (every? #(= expected %) child-shapes)
            (throw (ex-info "Tensor input must be rectangular"
                            {:child-shapes child-shapes})))
          (into [(count items)] expected))))
    []))

(defn rank-of [value]
  (count (nested-shape value)))

(defn shape-size [shape]
  (reduce * 1 shape))

(defn checked-tensor
  ([data] (checked-tensor data {}))
  ([data options]
   (let [shape (nested-shape data)]
     (when (empty? shape)
       (throw (ex-info "Use a Clojure scalar for rank 0"
                       {:value data})))
     (tensor/->tensor data options))))

(def values
  [[[0 1 2 3]
    [4 5 6 7]
    [8 9 10 11]]
   [[12 13 14 15]
    [16 17 18 19]
    [20 21 22 23]]])

(def t (checked-tensor values {:datatype :int64}))

(vec (dtype/shape t))
;; => [2 3 4]

(count (dtype/shape t))
;; => 3

(dtype/ecount t)
;; => 24

(dtype/elemwise-datatype t)
;; => :int64

(tensor/->jvm (tensor/reshape t [4 6]))
;; => [[0 1 2 3 4 5]
;;     [6 7 8 9 10 11]
;;     [12 13 14 15 16 17]
;;     [18 19 20 21 22 23]]

;; A scalar has one conceptual element.
(assert (= [] (nested-shape 5)))
(assert (= 1 (shape-size [])))

;; Empty tensors contain no elements.
(assert (= [0] (nested-shape [])))
(assert (= [2 0] (nested-shape [[] []])))
(assert (zero? (shape-size [2 0])))

;; The running tensor is rectangular and typed.
(assert (= [2 3 4] (nested-shape values)))
(assert (= [2 3 4] (vec (dtype/shape t))))
(assert (= 3 (rank-of values)))
(assert (= 24 (dtype/ecount t)))
(assert (= :int64 (dtype/elemwise-datatype t)))

;; Shape and element count agree.
(assert (= (dtype/ecount t)
           (shape-size (dtype/shape t))))

;; Rectangular validation rejects both failure forms.
(assert (try
          (nested-shape [[1 2 3] [4 5]])
          false
          (catch clojure.lang.ExceptionInfo _ true)))
(assert (try
          (nested-shape [[1 2] [3 [4]]])
          false
          (catch clojure.lang.ExceptionInfo _ true)))

;; Reshape changes the grouping, not the element count.
(let [reshaped (tensor/reshape t [4 6])]
  (assert (= [4 6] (vec (dtype/shape reshaped))))
  (assert (= (dtype/ecount t) (dtype/ecount reshaped))))
```

`tensor/->tensor` infers a shape from nested input. The checked constructor validates rectangularity first.

This validation is important. Raw `tensor/->tensor` can accept some ragged object data and fill or retain irregular values.

## Common Uses

- Validate model inputs.
- State image or batch layouts.
- Check reshape compatibility.
- Estimate storage needs.
- Diagnose axis errors.

## Recognition Clues

Look for `dimensions`, `rank`, `shape`, `batch`, `size`, or `ragged`.

## Memory Hooks

- Rank is the length of the shape.
- Size is the product of the shape.
- A scalar has size 1.
- A zero axis makes the size zero.
- Rectangular validation is separate from shape inference.

## Key Insight

Shape is the central tensor description. Predict each output shape before you inspect the values.

