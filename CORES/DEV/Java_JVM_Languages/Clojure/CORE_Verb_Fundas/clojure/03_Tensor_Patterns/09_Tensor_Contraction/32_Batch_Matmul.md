# 32. Batch Matmul

## Mental Model

Batch matrix multiplication treats the last two axes as matrices. All earlier axes identify batches.

```text
[batch... m k] @ [batch... k n] -> [broadcast-batch... m n]
```

The batch axes use the same right-aligned broadcasting rule as element-wise operations.

## Relationship to Cognitive Verb

```text
Apply -> broadcast batch coordinates -> multiply each matrix pair
```

## Clojure Functions and Common Idioms

|Need|Use|
|---|---|
|One matrix for all samples|Use a rank-two right tensor|
|One transform per sample|Use matching batch axes|
|Broadcast batch grids|Use size-one batch axes|
|Sequence linear layer|Keep sample and token axes as batch axes|
|No batch axes|Use ordinary matrix multiplication|

## Shape and Edge Behavior

- Both operands must have rank two or more.
- The inner matrix sizes must match.
- Batch axes align from the right.
- Equal batch sizes remain unchanged.
- A batch size of one can expand.
- Other unequal batch sizes cause an error.
- Empty batch or matrix axes produce empty output where applicable.

## Clojure Recipe Book

```clojure
(require '[tech.v3.datatype :as dtype]
         '[tech.v3.tensor :as tensor])

(defn pad-left [shape rank]
  (vec (concat (repeat (- rank (count shape)) 1) shape)))

(defn combine-axis-size [left right]
  (cond
    (= left right) left
    (= left 1) right
    (= right 1) left
    :else (throw (ex-info "Batch axes are not broadcast-compatible"
                          {:left left :right right}))))

(defn broadcast-shape [left right]
  (let [rank (max (count left) (count right))
        left (pad-left (vec left) rank)
        right (pad-left (vec right) rank)]
    (mapv combine-axis-size left right)))

(defn source-batch-coordinate [output-coordinate source-shape]
  (let [output-rank (count output-coordinate)
        source-rank (count source-shape)
        padded-shape (pad-left source-shape output-rank)
        padded-coordinate
        (mapv (fn [index size]
                (if (= size 1) 0 index))
              output-coordinate
              padded-shape)]
    (subvec padded-coordinate (- output-rank source-rank))))

(defn batch-matmul [left right]
  (let [left-shape (vec (dtype/shape left))
        right-shape (vec (dtype/shape right))
        left-rank (count left-shape)
        right-rank (count right-shape)]
    (when (or (< left-rank 2) (< right-rank 2))
      (throw (ex-info "Batch matmul requires rank two or more"
                      {:left-shape left-shape
                       :right-shape right-shape})))
    (let [left-batch (subvec left-shape 0 (- left-rank 2))
          right-batch (subvec right-shape 0 (- right-rank 2))
          [rows shared] (subvec left-shape (- left-rank 2))
          [right-shared cols] (subvec right-shape (- right-rank 2))
          output-batch (broadcast-shape left-batch right-batch)
          batch-rank (count output-batch)]
      (when-not (= shared right-shared)
        (throw (ex-info "Inner matrix sizes must match"
                        {:left-shape left-shape
                         :right-shape right-shape})))
      (tensor/clone
        (tensor/compute-tensor
          (into output-batch [rows cols])
          (fn [& output-coordinate]
            (let [output-coordinate (vec output-coordinate)
                  batch-coordinate (subvec output-coordinate 0 batch-rank)
                  row (nth output-coordinate batch-rank)
                  col (nth output-coordinate (inc batch-rank))
                  left-coordinate
                  (source-batch-coordinate batch-coordinate left-batch)
                  right-coordinate
                  (source-batch-coordinate batch-coordinate right-batch)]
              (double
                (reduce +
                        (map (fn [index]
                               (* (apply tensor/mget left
                                         (into left-coordinate [row index]))
                                  (apply tensor/mget right
                                         (into right-coordinate [index col]))))
                             (range shared))))))
          :float64)))))

(def batches
  (tensor/reshape
    (tensor/->tensor (range 12) {:datatype :int64})
    [2 2 3]))

(def weights
  (tensor/->tensor [[1 2]
                    [3 4]
                    [5 6]]
                   {:datatype :int64}))

;; The same rank-two matrix is used for both batches.
(assert (= [[[13.0 16.0]
             [40.0 52.0]]
            [[67.0 88.0]
             [94.0 124.0]]]
           (tensor/->jvm (batch-matmul batches weights))))

;; Batch shapes [2 1] and [1 3] broadcast to [2 3].
(let [left (tensor/reshape
             (tensor/->tensor (range 12) {:datatype :int64})
             [2 1 2 3])
      right (tensor/reshape
              (tensor/->tensor (range 18) {:datatype :int64})
              [1 3 3 2])
      result (batch-matmul left right)]
  (assert (= [2 3 2 2] (vec (dtype/shape result))))
  (assert (= 298.0 (tensor/mget result 1 2 0 0))))

;; Rank-two inputs have an empty batch shape.
(assert (= [2 2]
           (vec (dtype/shape
                  (batch-matmul
                    (tensor/select batches 0 :all :all)
                    weights)))))
```

## Common Uses

- Apply one weight matrix to a batch.
- Transform every token in a sequence.
- Use one matrix per sample.
- Compute attention score matrices.
- Process several coordinate systems together.

## Recognition Clues

Look for `batch`, `per sample`, `per token`, `last two axes`, or `broadcast matrices`.

## Memory Hooks

- Last two axes form each matrix.
- Earlier axes form the batch.
- Batch axes broadcast from the right.
- Matrix inner sizes must match.
- Matrix outer sizes remain.

## Key Insight

Batch matrix multiplication adds broadcasting around ordinary matrix multiplication. The last two axes keep their matrix roles.

