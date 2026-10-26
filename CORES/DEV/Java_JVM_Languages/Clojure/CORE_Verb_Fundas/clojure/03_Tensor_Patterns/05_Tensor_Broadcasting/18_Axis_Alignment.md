# 18. Axis Alignment

## Mental Model

Broadcasting starts at the right edge. A vector therefore aligns with the final axis by default.

To target another axis, reshape the vector with size one everywhere else.

```text
tensor shape   [2 3 4]

axis 2 values      [4]
axis 1 values    [3 1]
axis 0 values  [2 1 1]
```

## Relationship to Cognitive Verb

```text
Align -> place the vector size on its target axis -> fill other slots with one
```

## Clojure Functions and Common Idioms

|Need|Use|
|---|---|
|Align with final axis|use the vector shape directly|
|Align with another axis|reshape to ones with one named size|
|Reduce and broadcast back|retain the reduced axis as size one|
|Per-channel NCHW value|shape `[1 channels 1 1]`|
|Variable axis|construct the alignment shape programmatically|

## Shape and Edge Behavior

- The vector length must equal its target axis size.
- The aligned shape has the same rank as the target.
- Non-target axes have size one.
- Named alignment prevents silent square-shape errors.
- Explicit broadcast produces the target shape.

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

(defn alignment-shape [target-shape axis vector-size]
  (let [target-shape (vec target-shape)
        axis (normalize-axis (count target-shape) axis)]
    (when-not (= vector-size (nth target-shape axis))
      (throw (ex-info "Vector size does not match its target axis"
                      {:target-shape target-shape
                       :axis axis
                       :vector-size vector-size})))
    (assoc (vec (repeat (count target-shape) 1)) axis vector-size)))

(defn align-vector [vector-tensor target-shape axis]
  (let [vector-shape (vec (dtype/shape vector-tensor))]
    (when-not (= 1 (count vector-shape))
      (throw (ex-info "Alignment input must be rank one"
                      {:shape vector-shape})))
    (tensor/reshape
      vector-tensor
      (alignment-shape target-shape axis (first vector-shape)))))

(defn add-along-axis [t vector-tensor axis]
  (let [shape (vec (dtype/shape t))
        aligned (align-vector vector-tensor shape axis)]
    (dfn/+ t (tensor/broadcast aligned shape))))

(def t
  (tensor/reshape
    (dtype/make-container :jvm-heap :int64 (range 24))
    [2 3 4]))

(assert (= [1 1 4] (alignment-shape [2 3 4] -1 4)))
(assert (= [1 3 1] (alignment-shape [2 3 4] 1 3)))
(assert (= [2 1 1] (alignment-shape [2 3 4] 0 2)))

;; Add one value per row axis.
(let [row-values (tensor/->tensor [100 200 300] {:datatype :int64})
      result (add-along-axis t row-values 1)]
  (assert (= [2 3 4] (vec (dtype/shape result))))
  (assert (= 100 (tensor/mget result 0 0 0)))
  (assert (= 311 (tensor/mget result 0 2 3))))

;; Add one value per outer block.
(let [block-values (tensor/->tensor [1000 2000] {:datatype :int64})
      result (add-along-axis t block-values 0)]
  (assert (= 1000 (tensor/mget result 0 0 0)))
  (assert (= 2023 (tensor/mget result 1 2 3))))

;; NCHW channel alignment uses shape [1 C 1 1].
(let [images (tensor/new-tensor [2 3 4 4] {:datatype :float32})
      channels (tensor/->tensor [0.1 0.2 0.3] {:datatype :float32})
      aligned (align-vector channels (dtype/shape images) 1)]
  (assert (= [1 3 1 1] (vec (dtype/shape aligned))))
  (assert (= [2 3 4 4]
             (vec (dtype/shape
                    (tensor/broadcast aligned (dtype/shape images)))))))

(assert (try
          (alignment-shape [2 3 4] 1 4)
          false
          (catch clojure.lang.ExceptionInfo _ true)))
```

An equal dimension can hide a wrong alignment. State the target axis even when the operation already runs.

## Common Uses

- Add per-channel constants.
- Normalize one feature axis.
- Apply one row or column statistic.
- Center batched image channels.
- Write rank-independent axis functions.

## Recognition Clues

Look for `per channel`, `per feature`, `broadcast back`, `wrong direction`, or `keep dimensions`.

## Memory Hooks

- The final axis aligns automatically.
- Other axes need trailing size-one slots.
- Construct the alignment shape from the target.
- Keep reduced axes before reuse.
- Equal sizes can hide an axis mistake.

## Key Insight

Broadcast compatibility does not prove semantic alignment. Name the axis that each value describes.

