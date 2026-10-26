# 12. Reshape

## Mental Model

Reshape keeps the logical value order and changes the axis boundaries.

```text
[2 3 4] -> [4 6]

same 24 values
same row-major order
new grouping
```

The old and new shapes must have the same element count.

## Relationship to Cognitive Verb

```text
Regroup -> preserve linear order -> replace the shape
```

## Clojure Functions and Common Idioms

|Need|Use|
|---|---|
|New shape|`tensor/reshape`|
|Infer one axis|course helper with one `-1`|
|Flatten|shape `[element-count]`|
|Keep the first axis|`[first-size inferred-size]`|
|Keep the last axis|`[inferred-size last-size]`|
|Restore|save the old shape and reshape back|

## Shape and Edge Behavior

- New dimensions must be integers.
- At most one dimension can be `-1`.
- Other dimensions must not be negative.
- Inference requires exact divisibility.
- Zero-size inference is ambiguous when the known product is zero.
- Reshape preserves logical order.
- A reshape can share storage with the source.

## Clojure Recipe Book

```clojure
(require '[tech.v3.datatype :as dtype]
         '[tech.v3.tensor :as tensor])

(defn shape-size [shape]
  (reduce * 1 shape))

(defn resolve-shape [element-count requested-shape]
  (let [requested-shape (vec requested-shape)
        inferred-positions (keep-indexed
                             (fn [index size]
                               (when (= -1 size) index))
                             requested-shape)]
    (when (some #(< % -1) requested-shape)
      (throw (ex-info "Shape values must be nonnegative or -1"
                      {:shape requested-shape})))
    (when (> (count inferred-positions) 1)
      (throw (ex-info "Only one shape value can be inferred"
                      {:shape requested-shape})))
    (if-let [position (first inferred-positions)]
      (let [known-shape (assoc requested-shape position 1)
            known-size (shape-size known-shape)]
        (when (zero? known-size)
          (throw (ex-info "Cannot infer through a zero-size product"
                          {:shape requested-shape})))
        (when-not (zero? (mod element-count known-size))
          (throw (ex-info "Element count is not divisible by known axes"
                          {:element-count element-count
                           :shape requested-shape})))
        (assoc requested-shape position (quot element-count known-size)))
      (do
        (when-not (= element-count (shape-size requested-shape))
          (throw (ex-info "Reshape must preserve element count"
                          {:element-count element-count
                           :shape requested-shape})))
        requested-shape))))

(defn reshape [t requested-shape]
  (tensor/reshape t
                  (resolve-shape (dtype/ecount t) requested-shape)))

(def t
  (tensor/reshape
    (dtype/make-container :jvm-heap :int64 (range 24))
    [2 3 4]))

(tensor/->jvm (reshape t [4 6]))
;; => [[0 1 2 3 4 5]
;;     [6 7 8 9 10 11]
;;     [12 13 14 15 16 17]
;;     [18 19 20 21 22 23]]

(assert (= [2 12] (resolve-shape 24 [2 -1])))
(assert (= [6 4] (resolve-shape 24 [-1 4])))
(assert (= [2 2 3 2] (resolve-shape 24 [2 2 3 2])))
(assert (= [4 6] (vec (dtype/shape (reshape t [4 6])))))
(assert (= [2 12] (vec (dtype/shape (reshape t [2 -1])))))
(assert (= (dtype/->vector t)
           (dtype/->vector (reshape t [4 6]))))

;; Reshape and transpose can produce the same shape with different values.
(let [small (tensor/reshape
              (dtype/make-container :jvm-heap :int64 (range 8))
              [2 2 2])
      regrouped (tensor/reshape small [2 4])
      reordered (tensor/reshape (tensor/transpose small [1 0 2]) [2 4])]
  (assert (= [2 4] (vec (dtype/shape regrouped))))
  (assert (= [2 4] (vec (dtype/shape reordered))))
  (assert (not= (tensor/->jvm regrouped)
                (tensor/->jvm reordered))))

;; A reshape view shares storage.
(let [source (tensor/reshape
               (dtype/make-container :jvm-heap :int64 (range 6))
               [2 3])
      view (reshape source [3 2])]
  (tensor/mset! view 0 0 94)
  (assert (= 94 (tensor/mget source 0 0))))

;; Remembering the original shape makes reshape reversible.
(let [shape (vec (dtype/shape t))
      restored (reshape (reshape t [6 4]) shape)]
  (assert (= shape (vec (dtype/shape restored))))
  (assert (= (dtype/->vector t) (dtype/->vector restored))))

(assert (try
          (resolve-shape 24 [5 -1])
          false
          (catch clojure.lang.ExceptionInfo _ true)))
(assert (try
          (resolve-shape 24 [-1 -1])
          false
          (catch clojure.lang.ExceptionInfo _ true)))
```

## Common Uses

- Flatten features while keeping a batch axis.
- Split one axis into factors.
- Merge adjacent axes.
- Prepare data for matrix multiplication.
- Restore a saved tensor shape.

## Recognition Clues

Look for `same values`, `new dimensions`, `flatten except`, `split axis`, or `infer size`.

## Memory Hooks

- Preserve element count.
- Preserve logical order.
- Infer only one axis.
- Reshape is not transpose.
- Save the old shape for a round trip.

## Key Insight

Reshape moves boundaries in the logical value sequence. It does not relabel the axes.

