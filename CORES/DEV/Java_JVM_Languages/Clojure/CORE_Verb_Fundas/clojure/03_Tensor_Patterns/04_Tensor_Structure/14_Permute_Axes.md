# 14. Permute Axes

## Mental Model

A permutation states which old axis becomes each new axis.

```text
shape        [2 3 4]
permutation  [2 0 1]
result       [4 2 3]
```

New axis zero is old axis two. New axis one is old axis zero.

## Relationship to Cognitive Verb

```text
Reorder -> name every source axis once -> create an axis view
```

## Clojure Functions and Common Idioms

|Need|Use|
|---|---|
|Arbitrary permutation|`tensor/transpose`|
|Predict shape|select shape entries by the permutation|
|Reverse all axes|reverse `(range rank)`|
|Transpose final two axes|swap their permutation entries|
|Undo|apply the inverse permutation|
|Compose|select the first permutation with the second|

## Shape and Edge Behavior

- A permutation must contain every axis exactly once.
- The output rank equals the input rank.
- Shape entries follow the permutation.
- Logical flat order usually changes.
- The result is a view.
- Rank zero has one empty permutation conceptually.

## Clojure Recipe Book

```clojure
(require '[tech.v3.datatype :as dtype]
         '[tech.v3.tensor :as tensor])

(defn valid-permutation? [rank permutation]
  (= (vec (range rank)) (vec (sort permutation))))

(defn require-permutation [rank permutation]
  (let [permutation (vec permutation)]
    (when-not (valid-permutation? rank permutation)
      (throw (ex-info "Axes must form a permutation"
                      {:rank rank :permutation permutation})))
    permutation))

(defn permuted-shape [shape permutation]
  (let [shape (vec shape)
        permutation (require-permutation (count shape) permutation)]
    (mapv shape permutation)))

(defn inverse-permutation [permutation]
  (let [permutation (require-permutation (count permutation) permutation)]
    (mapv (fn [axis]
            (first (keep-indexed
                     (fn [index value]
                       (when (= axis value) index))
                     permutation)))
          (range (count permutation)))))

(defn compose-permutations [first-permutation second-permutation]
  (let [rank (count first-permutation)
        first-permutation (require-permutation rank first-permutation)
        second-permutation (require-permutation rank second-permutation)]
    (mapv first-permutation second-permutation)))

(defn permute [t permutation]
  (tensor/transpose
    t
    (require-permutation (count (dtype/shape t)) permutation)))

(def t
  (tensor/reshape
    (dtype/make-container :jvm-heap :int64 (range 24))
    [2 3 4]))

(def permutation [2 0 1])
(def transposed (permute t permutation))

(assert (= [4 2 3] (permuted-shape [2 3 4] permutation)))
(assert (= [4 2 3] (vec (dtype/shape transposed))))

;; Coordinates follow the same relabeling.
(assert (= (tensor/mget t 1 2 3)
           (tensor/mget transposed 3 1 2)))

;; The inverse restores shape and values.
(let [inverse (inverse-permutation permutation)
      restored (permute transposed inverse)]
  (assert (= [1 2 0] inverse))
  (assert (= [2 3 4] (vec (dtype/shape restored))))
  (assert (= (dtype/->vector t) (dtype/->vector restored))))

;; Composition matches two successive permutations.
(let [p [2 0 1]
      q [1 2 0]
      twice (permute (permute t p) q)
      once (permute t (compose-permutations p q))]
  (assert (= (vec (dtype/shape twice))
             (vec (dtype/shape once))))
  (assert (= (dtype/->vector twice) (dtype/->vector once))))

;; NCHW to NHWC layout conversion.
(let [images (tensor/new-tensor [8 3 32 32] {:datatype :float32})
      channels-last (permute images [0 2 3 1])]
  (assert (= [8 32 32 3] (vec (dtype/shape channels-last)))))

;; A permutation view shares storage.
(let [source (tensor/reshape
               (dtype/make-container :jvm-heap :int64 (range 24))
               [2 3 4])
      view (permute source [2 0 1])]
  (tensor/mset! view 0 0 0 67)
  (assert (= 67 (tensor/mget source 0 0 0))))

(assert (try
          (permute t [0 0 1])
          false
          (catch clojure.lang.ExceptionInfo _ true)))
```

## Common Uses

- Convert image layouts.
- Transpose each matrix in a batch.
- Place a feature axis where a function expects it.
- Bring non-adjacent axes together.
- Undo an earlier layout change.

## Recognition Clues

Look for `axis order`, `layout`, `channels first`, `channels last`, `permutation`, or `transpose`.

## Memory Hooks

- New axis `i` comes from old axis `permutation[i]`.
- Every source axis appears once.
- The shape uses the same permutation.
- Use the inverse to restore the layout.
- Permutation changes logical order, unlike reshape.

## Key Insight

Axis permutation relabels every dimension. It changes logical traversal order without moving the source values.

