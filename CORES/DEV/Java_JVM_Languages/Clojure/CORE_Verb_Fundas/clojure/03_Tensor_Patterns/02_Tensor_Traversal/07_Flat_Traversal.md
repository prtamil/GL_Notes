# 7. Flat Traversal

## Mental Model

Flat traversal ignores tensor boundaries and visits values as one sequence.

The default logical order is row-major. The last coordinate changes fastest.

Flattening loses shape information. Keep the original shape when you need a round trip.

## Relationship to Cognitive Verb

```text
Linearize -> visit values in a chosen order -> keep or discard the shape
```

## Clojure Functions and Common Idioms

|Need|Use|
|---|---|
|Flat logical reader|`dtype/->reader`|
|Flat vector copy|`dtype/->vector`|
|Rank-1 tensor view|`tensor/reshape`|
|Independent flat tensor|`tensor/clone`|
|Column-major logical order|reverse the axes, then read|
|Restore shape|`tensor/reshape` with saved shape|

## Shape and Edge Behavior

- The flat length equals the tensor element count.
- An empty tensor produces an empty flat sequence.
- Row-major order changes the last axis fastest.
- Flattening does not retain the original shape.
- A rank-1 reshape can share source storage.
- A vector created with `dtype/->vector` is independent Clojure data.

## Clojure Recipe Book

```clojure
(require '[tech.v3.datatype :as dtype]
         '[tech.v3.tensor :as tensor])

(defn row-major-strides [shape]
  (if (empty? shape)
    []
    (->> (reverse (rest shape))
         (reductions * 1)
         reverse
         vec)))

(defn coordinate->flat [shape coordinate]
  (reduce + (map * coordinate (row-major-strides shape))))

(defn flat->coordinate [shape flat-index]
  (when-not (< -1 flat-index (reduce * 1 shape))
    (throw (ex-info "Flat index is outside the tensor"
                    {:shape shape :flat-index flat-index})))
  (loop [remaining flat-index
         strides (row-major-strides shape)
         coordinate []]
    (if-let [stride (first strides)]
      (recur (mod remaining stride)
             (next strides)
             (conj coordinate (quot remaining stride)))
      coordinate)))

(defn flat-view [t]
  (tensor/reshape t [(dtype/ecount t)]))

(defn column-major-values [t]
  (let [rank (count (dtype/shape t))
        reversed-axes (vec (reverse (range rank)))]
    (dtype/->vector (tensor/transpose t reversed-axes))))

(def t
  (tensor/reshape
    (dtype/make-container :jvm-heap :int64 (range 24))
    [2 3 4]))

(dtype/->vector t)
;; => [0 1 2 3 4 5 6 7 8 9 10 11
;;     12 13 14 15 16 17 18 19 20 21 22 23]

(column-major-values t)
;; => [0 12 4 16 8 20 1 13 5 17 9 21
;;     2 14 6 18 10 22 3 15 7 19 11 23]

(assert (= (range 24) (seq (dtype/->reader t))))
(assert (= 24 (count (dtype/->reader t))))
(assert (= [24] (vec (dtype/shape (flat-view t)))))

(assert (= 23 (coordinate->flat [2 3 4] [1 2 3])))
(assert (= [1 2 3] (flat->coordinate [2 3 4] 23)))
(assert (= [0 1 1] (flat->coordinate [2 3 4] 5)))

;; Flat view mutation reaches the source.
(let [source (tensor/reshape
               (dtype/make-container :jvm-heap :int64 (range 6))
               [2 3])
      view (flat-view source)]
  (tensor/mset! view 0 73)
  (assert (= 73 (tensor/mget source 0 0))))

;; Clone gives independent tensor storage.
(let [source (tensor/reshape
               (dtype/make-container :jvm-heap :int64 (range 6))
               [2 3])
      copy (tensor/clone (flat-view source))]
  (tensor/mset! copy 0 81)
  (assert (= 0 (tensor/mget source 0 0)))
  (assert (= 81 (tensor/mget copy 0))))

;; Save the shape before flattening to make the operation reversible.
(let [shape (vec (dtype/shape t))
      restored (tensor/reshape (flat-view t) shape)]
  (assert (= shape (vec (dtype/shape restored))))
  (assert (= (dtype/->vector t) (dtype/->vector restored))))

(assert (try
          (flat->coordinate [2 3 4] 24)
          false
          (catch clojure.lang.ExceptionInfo _ true)))
```

## Common Uses

- Apply one-dimensional algorithms.
- Serialize a tensor buffer.
- Hash values with their shape.
- Convert flat indices to coordinates.
- Restore a tensor after storage or transfer.

## Recognition Clues

Look for `flatten`, `linear order`, `buffer`, `serialize`, or `flat index`.

## Memory Hooks

- Flat length equals element count.
- Row-major order changes the last axis fastest.
- A view can share storage.
- A vector copy is independent.
- Save the shape for reconstruction.

## Key Insight

Flat traversal keeps value order but removes axis boundaries. Shape metadata makes the operation reversible.

