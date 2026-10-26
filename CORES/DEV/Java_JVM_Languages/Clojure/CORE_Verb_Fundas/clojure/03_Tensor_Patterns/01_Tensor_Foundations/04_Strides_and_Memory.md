# 4. Strides and Memory

## Mental Model

A tensor combines a flat buffer with an index mapping.

```text
shape     [2 3 4]
strides   [12 4 1]
buffer    0 1 2 3 4 5 ... 23
```

The strides give the buffer step for each axis.

```text
flat index = i*12 + j*4 + k*1
```

`dtype-next` dimension strides use elements. NumPy array strides use bytes.

## Relationship to Cognitive Verb

```text
Locate -> multiply each index by its stride -> add the offsets
```

## Clojure Functions and Common Idioms

|Need|Use|
|---|---|
|Dimension metadata|`tensor/tensor->dimensions`|
|Element strides|`dimensions/strides`|
|Dense layout check|`dimensions/dense?`|
|Flat row-major reader|`dtype/->reader` or `dtype/->vector`|
|New shape view|`tensor/reshape`|
|Axis permutation view|`tensor/transpose`|
|Independent buffer|`tensor/clone`|

## Shape and Edge Behavior

- Row-major order gives the last axis stride 1.
- A zero-sized axis has no valid element coordinate.
- Reshape requires the same element count.
- Reshape and transpose can share the source storage.
- A transpose is usually not dense in its logical index order.
- A clone copies values into independent storage.

## Clojure Recipe Book

```clojure
(require '[tech.v3.datatype :as dtype]
         '[tech.v3.tensor :as tensor]
         '[tech.v3.tensor.dimensions :as dimensions])

(defn row-major-strides [shape]
  (if (empty? shape)
    []
    (->> (reverse (rest shape))
         (reductions * 1)
         reverse
         vec)))

(defn flat-index [coordinate strides]
  (when-not (= (count coordinate) (count strides))
    (throw (ex-info "Coordinate rank must match stride rank"
                    {:coordinate coordinate :strides strides})))
  (reduce + (map * coordinate strides)))

(defn coordinate-in-bounds? [shape coordinate]
  (and (= (count shape) (count coordinate))
       (every? true?
               (map (fn [axis-size index]
                      (< -1 index axis-size))
                    shape
                    coordinate))))

(defn checked-flat-index [shape coordinate]
  (when-not (coordinate-in-bounds? shape coordinate)
    (throw (ex-info "Coordinate is outside the tensor shape"
                    {:shape shape :coordinate coordinate})))
  (flat-index coordinate (row-major-strides shape)))

(def t
  (tensor/reshape
    (dtype/make-container :jvm-heap :int64 (range 24))
    [2 3 4]))

(def tensor-dimensions (tensor/tensor->dimensions t))

(vec (dimensions/strides tensor-dimensions))
;; => [12 4 1]

(flat-index [1 2 3] [12 4 1])
;; => 23

(nth (dtype/->vector t) 23)
;; => 23

(assert (= [12 4 1] (row-major-strides [2 3 4])))
(assert (= [12 4 1]
           (vec (dimensions/strides tensor-dimensions))))
(assert (= 23 (checked-flat-index [2 3 4] [1 2 3])))
(assert (= (tensor/mget t 1 2 3)
           (nth (dtype/->vector t)
                (checked-flat-index [2 3 4] [1 2 3]))))
(assert (dimensions/dense? tensor-dimensions))

;; Reshape changes shape and strides. It keeps the storage.
(let [source (tensor/reshape
               (dtype/make-container :jvm-heap :int64 (range 24))
               [2 3 4])
      view (tensor/reshape source [4 6])
      view-dimensions (tensor/tensor->dimensions view)]
  (assert (= [4 6] (vec (dtype/shape view))))
  (assert (= [6 1] (vec (dimensions/strides view-dimensions))))
  (tensor/mset! view 0 0 99)
  (assert (= 99 (tensor/mget source 0 0 0))))

;; Transpose permutes shape and strides without moving values.
(let [source (tensor/reshape
               (dtype/make-container :jvm-heap :int64 (range 24))
               [2 3 4])
      view (tensor/transpose source [2 1 0])
      view-dimensions (tensor/tensor->dimensions view)]
  (assert (= [4 3 2] (vec (dtype/shape view))))
  (assert (= [1 4 12] (vec (dimensions/strides view-dimensions))))
  (assert (not (dimensions/dense? view-dimensions)))
  (tensor/mset! view 0 0 0 88)
  (assert (= 88 (tensor/mget source 0 0 0))))

;; Clone breaks the storage relationship.
(let [source (tensor/reshape
               (dtype/make-container :jvm-heap :int64 (range 6))
               [2 3])
      copy (tensor/clone source)]
  (tensor/mset! copy 0 0 55)
  (assert (= 0 (tensor/mget source 0 0)))
  (assert (= 55 (tensor/mget copy 0 0))))

(assert (try
          (checked-flat-index [2 3 4] [2 0 0])
          false
          (catch clojure.lang.ExceptionInfo _ true)))
```

`dtype-next` can keep an indirect storage mapping after some view operations. Do not infer copying from shape alone.

Test aliasing through behavior. Use `tensor/clone` when the result must be independent.

## Common Uses

- Convert between flat and n-dimensional indices.
- Explain zero-copy reshape and transpose.
- Choose cache-friendly traversal order.
- Prepare buffers for native libraries.
- Diagnose unexpected shared mutation.

## Recognition Clues

Look for `contiguous`, `zero-copy`, `layout`, `row-major`, `buffer`, or `alias`.

## Memory Hooks

- Shape sets the valid coordinates.
- Strides map coordinates to storage.
- The last row-major stride is 1.
- Views can share storage.
- Clone when you need a copy.

## Key Insight

A tensor is a flat buffer plus an index mapping. Many tensor operations change the mapping, not the buffer.

