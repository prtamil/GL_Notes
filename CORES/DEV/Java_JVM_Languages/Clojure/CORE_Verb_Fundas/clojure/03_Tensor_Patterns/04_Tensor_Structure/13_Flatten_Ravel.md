# 13. Flatten and Ravel

## Mental Model

Flattening merges adjacent axes.

Full flattening merges all axes into one axis. Partial flattening keeps selected outer or inner boundaries.

## Relationship to Cognitive Verb

```text
Flatten -> multiply adjacent axis sizes -> reshape without changing order
```

## Clojure Functions and Common Idioms

|Need|Use|
|---|---|
|Flat view|reshape to `[element-count]`|
|Flat copy|clone the flat view|
|Keep batch axis|`[shape[0] product(rest shape)]`|
|Keep feature axis|`[product(butlast shape) last(shape)]`|
|Merge adjacent range|replace it with its product|
|Split back|restore the saved shape|

## Shape and Edge Behavior

- Full flatten always produces rank 1.
- The result length equals the element count.
- Flatten preserves logical row-major order.
- A view can share storage.
- A clone has independent storage.
- Non-adjacent axes must be moved together before a meaningful merge.

## Clojure Recipe Book

```clojure
(require '[tech.v3.datatype :as dtype]
         '[tech.v3.tensor :as tensor])

(defn shape-size [shape]
  (reduce * 1 shape))

(defn flatten-view [t]
  (tensor/reshape t [(dtype/ecount t)]))

(defn flatten-copy [t]
  (tensor/clone (flatten-view t)))

(defn flatten-after-first [t]
  (let [shape (vec (dtype/shape t))]
    (when (< (count shape) 2)
      (throw (ex-info "Input must have at least two axes"
                      {:shape shape})))
    (tensor/reshape t [(first shape) (shape-size (rest shape))])))

(defn flatten-before-last [t]
  (let [shape (vec (dtype/shape t))]
    (when (< (count shape) 2)
      (throw (ex-info "Input must have at least two axes"
                      {:shape shape})))
    (tensor/reshape t [(shape-size (butlast shape)) (last shape)])))

(defn merged-shape [shape start end]
  (let [shape (vec shape)
        rank (count shape)]
    (when-not (<= 0 start end rank)
      (throw (ex-info "Merge range is outside the shape"
                      {:shape shape :start start :end end})))
    (when (= start end)
      (throw (ex-info "Merge range must contain an axis" {})))
    (vec (concat (subvec shape 0 start)
                 [(shape-size (subvec shape start end))]
                 (subvec shape end)))))

(defn flatten-axes [t start end]
  (tensor/reshape t (merged-shape (dtype/shape t) start end)))

(def t
  (tensor/reshape
    (dtype/make-container :jvm-heap :int64 (range 24))
    [2 3 4]))

(assert (= [24] (vec (dtype/shape (flatten-view t)))))
(assert (= [2 12] (vec (dtype/shape (flatten-after-first t)))))
(assert (= [6 4] (vec (dtype/shape (flatten-before-last t)))))
(assert (= [6 4] (merged-shape [2 3 4] 0 2)))
(assert (= [2 12] (merged-shape [2 3 4] 1 3)))
(assert (= (range 24) (seq (dtype/->reader (flatten-view t)))))

;; The flat view aliases its source.
(let [source (tensor/reshape
               (dtype/make-container :jvm-heap :int64 (range 6))
               [2 3])
      view (flatten-view source)]
  (tensor/mset! view 0 65)
  (assert (= 65 (tensor/mget source 0 0))))

;; The flat copy is independent.
(let [source (tensor/reshape
               (dtype/make-container :jvm-heap :int64 (range 6))
               [2 3])
      copy (flatten-copy source)]
  (tensor/mset! copy 0 66)
  (assert (= 0 (tensor/mget source 0 0)))
  (assert (= 66 (tensor/mget copy 0))))

;; Merge and restore form a round trip.
(let [shape (vec (dtype/shape t))
      merged (flatten-axes t 0 2)
      restored (tensor/reshape merged shape)]
  (assert (= [6 4] (vec (dtype/shape merged))))
  (assert (= (dtype/->vector t) (dtype/->vector restored))))
```

## Common Uses

- Form one feature row per sample.
- Form one feature row per position.
- Apply one-dimensional tools to all values.
- Serialize tensor data.
- Merge axes before a contraction.

## Recognition Clues

Look for `flatten`, `ravel`, `merge dimensions`, `one row per sample`, or `linear buffer`.

## Memory Hooks

- Flatten means merge adjacent axes.
- Full flatten gives one axis.
- View for shared storage.
- Clone for independent storage.
- Save shape before merging.

## Key Insight

Flattening is a specific reshape. It replaces adjacent shape entries with their product.

