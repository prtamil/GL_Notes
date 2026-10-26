# 17. Broadcasting Rules

## Mental Model

Broadcasting aligns shapes from the right. Two aligned sizes are compatible when they are equal or one size is one.

Missing leading axes act like size-one axes.

```text
  [2 1 3]
    [4 3] -> [1 4 3]
  -------
  [2 4 3]
```

## Relationship to Cognitive Verb

```text
Expand -> right-align shapes -> stretch only size-one axes
```

## Clojure Functions and Common Idioms

|Need|Use|
|---|---|
|Predict a common shape|compare aligned axes from the right|
|Add leading axes|reshape with leading ones|
|Create an expanded view|`tensor/broadcast` after strict validation|
|Element-wise math|functions in `tech.v3.datatype.functional`|
|Control alignment|insert size-one axes first|

## Shape and Edge Behavior

- Equal sizes stay unchanged.
- Size one expands to the other aligned size.
- Missing leading axes act as size one.
- A zero axis is compatible with size one and remains zero.
- Other unequal sizes are incompatible.
- Broadcasting changes the view shape, not the source shape.
- This course validates NumPy rules before it calls `tensor/broadcast`.

## Clojure Recipe Book

```clojure
(require '[tech.v3.datatype :as dtype]
         '[tech.v3.datatype.functional :as dfn]
         '[tech.v3.tensor :as tensor])

(defn pad-shape [shape rank]
  (let [shape (vec shape)]
    (when (> (count shape) rank)
      (throw (ex-info "Shape rank exceeds the target rank"
                      {:shape shape :rank rank})))
    (vec (concat (repeat (- rank (count shape)) 1) shape))))

(defn combine-axis-sizes [sizes]
  (reduce
    (fn [result size]
      (cond
        (= result size) result
        (= result 1) size
        (= size 1) result
        :else (throw (ex-info "Shapes are not broadcast-compatible"
                              {:axis-sizes sizes}))))
    1
    sizes))

(defn broadcast-shape [& shapes]
  (if (empty? shapes)
    []
    (let [rank (apply max (map count shapes))
          padded (mapv #(pad-shape % rank) shapes)]
      (apply mapv (fn [& sizes]
                    (combine-axis-sizes sizes))
             padded))))

(defn broadcast-to [t target-shape]
  (let [source-shape (vec (dtype/shape t))
        target-shape (vec target-shape)
        padded-source (pad-shape source-shape (count target-shape))]
    (when-not (= target-shape
                 (broadcast-shape source-shape target-shape))
      (throw (ex-info "Tensor cannot broadcast to the target shape"
                      {:source-shape source-shape
                       :target-shape target-shape})))
    (tensor/broadcast (tensor/reshape t padded-source) target-shape)))

(defn broadcast-map [op left right]
  (let [shape (broadcast-shape (dtype/shape left)
                               (dtype/shape right))]
    (op (broadcast-to left shape)
        (broadcast-to right shape))))

(assert (= [2 4 3] (broadcast-shape [2 1 3] [4 3])))
(assert (= [3 4] (broadcast-shape [3 4] [4])))
(assert (= [3 4] (broadcast-shape [3 1] [1 4])))
(assert (= [0 4] (broadcast-shape [0 4] [1 4])))

(def matrix
  (tensor/reshape
    (dtype/make-container :jvm-heap :int64 (range 12))
    [3 4]))

(def bias (tensor/->tensor [10 20 30 40] {:datatype :int64}))

(tensor/->jvm (broadcast-map dfn/+ matrix bias))
;; => [[10 21 32 43]
;;     [14 25 36 47]
;;     [18 29 40 51]]

(assert (= [3 4]
           (vec (dtype/shape (broadcast-to bias [3 4])))))
(assert (= [[10 21 32 43]
            [14 25 36 47]
            [18 29 40 51]]
           (tensor/->jvm (broadcast-map dfn/+ matrix bias))))

;; Two perpendicular vectors produce a grid.
(let [column (tensor/->tensor [[1] [2] [3]] {:datatype :int64})
      row (tensor/->tensor [[10 20 30 40]] {:datatype :int64})
      result (broadcast-map dfn/+ column row)]
  (assert (= [3 4] (vec (dtype/shape result))))
  (assert (= [[11 21 31 41]
              [12 22 32 42]
              [13 23 33 43]]
             (tensor/->jvm result))))

;; A scalar already works with dtype-next element-wise operations.
(assert (= [5 6 7 8]
           (dtype/->vector
             (dfn/+ (tensor/->tensor [0 1 2 3] {:datatype :int64}) 5))))

(assert (try
          (broadcast-shape [3] [4])
          false
          (catch clojure.lang.ExceptionInfo _ true)))
(assert (try
          (broadcast-shape [2 3 4] [2 4])
          false
          (catch clojure.lang.ExceptionInfo _ true)))
```

Raw `tensor/broadcast` can repeat dimensions that NumPy would reject. The wrapper applies the stricter course rule.

## Common Uses

- Add one bias per feature.
- Apply one scale per channel.
- Normalize with retained dimensions.
- Form outer operations.
- Compare every item with every category.

## Recognition Clues

Look for `different shapes`, `per feature`, `stretch`, `align`, `bias`, or `singleton axis`.

## Memory Hooks

- Align shapes from the right.
- Equal sizes are compatible.
- Size one can stretch.
- Missing leading axes act as one.
- Predict the result shape first.

## Key Insight

Broadcasting replaces many explicit loops with one mechanical shape rule.

