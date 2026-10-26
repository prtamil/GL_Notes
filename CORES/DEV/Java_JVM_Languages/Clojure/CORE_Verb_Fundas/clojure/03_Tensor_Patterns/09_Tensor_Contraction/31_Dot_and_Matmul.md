# 31. Dot and Matmul

## Mental Model

A dot product multiplies aligned vector items and sums the products.

Matrix multiplication applies that dot product to each output row and column pair.

```text
[m k] @ [k n] -> [m n]
```

The two inner sizes must match. The two outer sizes remain.

## Relationship to Cognitive Verb

```text
Combine -> multiply across one shared axis -> sum that axis
```

## Clojure Functions and Common Idioms

|Need|Use|
|---|---|
|Vector dot product|Multiply matching positions and sum|
|Matrix product|Compute one dot product per row and column|
|Matrix-vector product|Treat the vector as one column|
|Linear layer|Multiply by weights, then add bias|
|Gram matrix|Multiply a matrix transpose by the matrix|

## Shape and Edge Behavior

- Dot requires two rank-one tensors with equal sizes.
- Matrix multiplication requires rank-two tensors.
- The left column count must equal the right row count.
- A shared axis of size zero produces zero sums.
- Empty outer axes produce an empty result.
- The input tensors must be rectangular.

## Clojure Recipe Book

```clojure
(require '[tech.v3.datatype :as dtype]
         '[tech.v3.tensor :as tensor])

(defn dot [left right]
  (let [left-shape (vec (dtype/shape left))
        right-shape (vec (dtype/shape right))]
    (when-not (and (= 1 (count left-shape))
                   (= 1 (count right-shape))
                   (= left-shape right-shape))
      (throw (ex-info "Dot requires equal rank-one shapes"
                      {:left-shape left-shape
                       :right-shape right-shape})))
    (reduce +
            (map * (dtype/->vector left)
                   (dtype/->vector right)))))

(defn matmul-2d [left right]
  (let [left-shape (vec (dtype/shape left))
        right-shape (vec (dtype/shape right))]
    (when-not (= 2 (count left-shape) (count right-shape))
      (throw (ex-info "Matrix multiplication requires rank-two tensors"
                      {:left-shape left-shape
                       :right-shape right-shape})))
    (let [[rows shared] left-shape
          [right-shared cols] right-shape]
      (when-not (= shared right-shared)
        (throw (ex-info "Inner matrix sizes must match"
                        {:left-shape left-shape
                         :right-shape right-shape})))
      (tensor/clone
        (tensor/compute-tensor
          [rows cols]
          (fn [row col]
            (double
              (reduce +
                      (map (fn [index]
                             (* (tensor/mget left row index)
                                (tensor/mget right index col)))
                           (range shared)))))
          :float64)))))

(defn matrix-vector [matrix vector]
  (let [[size] (vec (dtype/shape vector))
        column (tensor/reshape vector [size 1])]
    (tensor/clone (tensor/select (matmul-2d matrix column) :all 0))))

(def left
  (tensor/->tensor [[1 2 3]
                    [4 5 6]]
                   {:datatype :int64}))

(def right
  (tensor/->tensor [[7 8]
                    [9 10]
                    [11 12]]
                   {:datatype :int64}))

(assert (= 32
           (dot (tensor/->tensor [1 2 3] {:datatype :int64})
                (tensor/->tensor [4 5 6] {:datatype :int64}))))

(assert (= [[58.0 64.0]
            [139.0 154.0]]
           (tensor/->jvm (matmul-2d left right))))

(assert (= [14.0 32.0]
           (dtype/->vector
             (matrix-vector
               left
               (tensor/->tensor [1 2 3] {:datatype :int64})))))

;; A Gram matrix contains all column-to-column dot products.
(let [gram (matmul-2d (tensor/transpose left [1 0]) left)]
  (assert (= [[17.0 22.0 27.0]
              [22.0 29.0 36.0]
              [27.0 36.0 45.0]]
             (tensor/->jvm gram))))

(assert (try
          (matmul-2d left left)
          false
          (catch clojure.lang.ExceptionInfo _ true)))
```

## Common Uses

- Apply a linear transform.
- Compare feature vectors.
- Compute covariance-related matrices.
- Transform coordinates.
- Combine graph or sequence features.

## Recognition Clues

Look for `dot product`, `row by column`, `linear layer`, `transform`, or `Gram matrix`.

## Memory Hooks

- Multiply aligned items.
- Sum the shared axis.
- Inner sizes disappear.
- Outer sizes remain.
- Matrix multiplication is a grid of dot products.

## Key Insight

Matrix multiplication contracts one shared axis. Its shape rule shows which dimensions disappear and which remain.

