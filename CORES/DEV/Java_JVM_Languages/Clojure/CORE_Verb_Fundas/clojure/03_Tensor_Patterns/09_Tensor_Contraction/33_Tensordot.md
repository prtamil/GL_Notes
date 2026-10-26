# 33. Tensordot

## Mental Model

Tensor contraction generalizes the dot product. It multiplies along selected axis pairs and sums those axes.

The unselected left axes come first. The unselected right axes follow them.

```text
left remaining + right remaining -> result shape
```

## Relationship to Cognitive Verb

```text
Contract -> pair equal-sized axes -> multiply -> sum the paired axes
```

## Clojure Functions and Common Idioms

|Need|Use|
|---|---|
|Vector dot|Contract the only axis|
|Matrix multiplication|Contract left axis one with right axis zero|
|Several shared axes|Pass several axis pairs|
|Outer product|Pass no contraction axes|
|Full inner product|Contract all axes|

## Shape and Edge Behavior

- Each axis list must contain distinct axes.
- Both axis lists must have equal lengths.
- Paired axis sizes must match.
- Negative axes count from the end.
- A size-zero contracted axis produces zero sums.
- A full contraction returns a Clojure scalar.
- Other contractions return a tensor.

## Clojure Recipe Book

```clojure
(require '[tech.v3.datatype :as dtype]
         '[tech.v3.tensor :as tensor])

(defn normalize-axis [rank axis]
  (let [axis (if (neg? axis) (+ rank axis) axis)]
    (when-not (< -1 axis rank)
      (throw (ex-info "Axis is outside the tensor rank"
                      {:axis axis :rank rank})))
    axis))

(defn normalize-axes [rank axes]
  (let [axes (mapv #(normalize-axis rank %) axes)]
    (when-not (= (count axes) (count (distinct axes)))
      (throw (ex-info "Contraction axes must be distinct"
                      {:axes axes})))
    axes))

(defn coordinates [shape]
  (reduce
    (fn [prefixes size]
      (vec (for [prefix prefixes
                 index (range size)]
             (conj prefix index))))
    [[]]
    shape))

(defn assign-axes [coordinate axes values]
  (reduce (fn [result [axis value]]
            (assoc result axis value))
          coordinate
          (map vector axes values)))

(defn tensor-dot [left right left-axes right-axes]
  (let [left-shape (vec (dtype/shape left))
        right-shape (vec (dtype/shape right))
        left-rank (count left-shape)
        right-rank (count right-shape)
        left-axes (normalize-axes left-rank left-axes)
        right-axes (normalize-axes right-rank right-axes)]
    (when-not (= (count left-axes) (count right-axes))
      (throw (ex-info "Contraction axis counts must match"
                      {:left-axes left-axes :right-axes right-axes})))
    (let [left-contract-shape (mapv left-shape left-axes)
          right-contract-shape (mapv right-shape right-axes)]
      (when-not (= left-contract-shape right-contract-shape)
        (throw (ex-info "Paired contraction sizes must match"
                        {:left-sizes left-contract-shape
                         :right-sizes right-contract-shape})))
      (let [left-remaining (vec (remove (set left-axes) (range left-rank)))
            right-remaining (vec (remove (set right-axes) (range right-rank)))
            left-output-shape (mapv left-shape left-remaining)
            right-output-shape (mapv right-shape right-remaining)
            output-shape (into left-output-shape right-output-shape)
            split-index (count left-remaining)
            contracted-coordinates (coordinates left-contract-shape)
            compute-value
            (fn [output-coordinate]
              (let [output-coordinate (vec output-coordinate)
                    left-values (subvec output-coordinate 0 split-index)
                    right-values (subvec output-coordinate split-index)]
                (double
                  (reduce +
                          (map
                            (fn [contracted]
                              (let [left-coordinate
                                    (-> (vec (repeat left-rank 0))
                                        (assign-axes left-remaining left-values)
                                        (assign-axes left-axes contracted))
                                    right-coordinate
                                    (-> (vec (repeat right-rank 0))
                                        (assign-axes right-remaining right-values)
                                        (assign-axes right-axes contracted))]
                                (* (apply tensor/mget left left-coordinate)
                                   (apply tensor/mget right right-coordinate))))
                            contracted-coordinates)))))]
        (if (empty? output-shape)
          (compute-value [])
          (tensor/clone
            (tensor/compute-tensor
              output-shape
              (fn [& output-coordinate]
                (compute-value output-coordinate))
              :float64)))))))

(def vector-a (tensor/->tensor [1 2 3] {:datatype :int64}))
(def vector-b (tensor/->tensor [4 5 6] {:datatype :int64}))

(assert (= 32.0 (tensor-dot vector-a vector-b [0] [0])))

;; No contracted axes produce an outer product.
(assert (= [[10.0 20.0 30.0]
            [20.0 40.0 60.0]]
           (tensor/->jvm
             (tensor-dot
               (tensor/->tensor [1 2] {:datatype :int64})
               (tensor/->tensor [10 20 30] {:datatype :int64})
               []
               []))))

;; Contracting one axis reproduces matrix multiplication.
(def left
  (tensor/->tensor [[1 2 3]
                    [4 5 6]]
                   {:datatype :int64}))
(def right
  (tensor/->tensor [[7 8]
                    [9 10]
                    [11 12]]
                   {:datatype :int64}))

(assert (= [[58.0 64.0]
            [139.0 154.0]]
           (tensor/->jvm (tensor-dot left right [1] [0]))))

;; Two contracted axes disappear. The remaining axes form [2 5].
(let [left (tensor/reshape
             (tensor/->tensor (repeat 24 1) {:datatype :int64})
             [2 3 4])
      right (tensor/reshape
              (tensor/->tensor (repeat 60 1) {:datatype :int64})
              [3 4 5])
      result (tensor-dot left right [1 2] [0 1])]
  (assert (= [2 5] (vec (dtype/shape result))))
  (assert (every? #(= 12.0 %) (dtype/->vector result))))

(assert (try
          (tensor-dot left right [0] [0])
          false
          (catch clojure.lang.ExceptionInfo _ true)))
```

## Common Uses

- Contract feature and channel axes.
- Compute generalized inner products.
- Combine tensors with several shared dimensions.
- Express matrix multiplication with explicit axes.
- Build multilinear transforms.

## Recognition Clues

Look for `contract axes`, `sum shared dimensions`, `generalized dot`, or `inner product`.

## Memory Hooks

- Name the paired axes.
- Check their sizes.
- Multiply matching coordinates.
- Sum the paired axes.
- Keep every unpaired axis.

## Key Insight

Tensor contraction removes selected axis pairs. Every unselected axis remains in a predictable order.

