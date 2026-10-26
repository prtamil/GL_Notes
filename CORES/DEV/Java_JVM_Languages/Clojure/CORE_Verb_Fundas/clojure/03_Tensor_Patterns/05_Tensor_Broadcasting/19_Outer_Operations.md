# 19. Outer Operations

## Mental Model

An outer operation combines every value from one input with every value from another input.

Give one vector a column shape and the other vector a row shape.

```text
[n 1] operation [1 m] -> [n m]
```

The operation can add, multiply, subtract, compare, or apply another element-wise function.

## Relationship to Cognitive Verb

```text
Pair all -> add perpendicular size-one axes -> apply one element-wise operation
```

## Clojure Functions and Common Idioms

|Need|Use|
|---|---|
|Outer operation|reshape, broadcast, then apply `dfn` operation|
|Outer product|`dfn/*`|
|Outer sum|`dfn/+`|
|All pair differences|expand sample axes in opposite positions|
|Pairwise distance|square, reduce feature axis, then square root|
|One-hot mask|outer equality against class indices|

## Shape and Edge Behavior

- Rank-1 inputs of sizes `n` and `m` produce shape `[n m]`.
- Empty input produces a zero axis in the result.
- Reversing operands usually transposes the result.
- Pairwise row operations retain the feature axis until reduction.
- The output contains a real value for every pair.

## Clojure Recipe Book

```clojure
(require '[tech.v3.datatype :as dtype]
         '[tech.v3.datatype.functional :as dfn]
         '[tech.v3.tensor :as tensor])

(defn require-vector [t]
  (let [shape (vec (dtype/shape t))]
    (when-not (= 1 (count shape))
      (throw (ex-info "Outer vector input must have rank one"
                      {:shape shape})))
    (first shape)))

(defn outer-operation [op left right]
  (let [left-size (require-vector left)
        right-size (require-vector right)
        target-shape [left-size right-size]
        left-column (tensor/reshape left [left-size 1])
        right-row (tensor/reshape right [1 right-size])]
    (op (tensor/broadcast left-column target-shape)
        (tensor/broadcast right-row target-shape))))

(defn pairwise-differences [points]
  (let [[point-count feature-count] (vec (dtype/shape points))
        target-shape [point-count point-count feature-count]
        left (tensor/reshape points [point-count 1 feature-count])
        right (tensor/reshape points [1 point-count feature-count])]
    (dfn/- (tensor/broadcast left target-shape)
           (tensor/broadcast right target-shape))))

(defn pairwise-distances [points]
  (-> points
      pairwise-differences
      dfn/sq
      (tensor/reduce-axis dfn/sum -1)
      dfn/sqrt))

(def a (tensor/->tensor [1 2 3] {:datatype :int64}))
(def b (tensor/->tensor [10 20 30 40] {:datatype :int64}))

(tensor/->jvm (outer-operation dfn/+ a b))
;; => [[11 21 31 41]
;;     [12 22 32 42]
;;     [13 23 33 43]]

(tensor/->jvm (outer-operation dfn/* a b))
;; => [[10 20 30 40]
;;     [20 40 60 80]
;;     [30 60 90 120]]

(assert (= [3 4]
           (vec (dtype/shape (outer-operation dfn/+ a b)))))
(assert (= [[11 21 31 41]
            [12 22 32 42]
            [13 23 33 43]]
           (tensor/->jvm (outer-operation dfn/+ a b))))

;; Comparison creates a triangular relation matrix.
(let [indices (tensor/->tensor [0 1 2] {:datatype :int64})
      greater (outer-operation dfn/> indices indices)]
  (assert (= [[false false false]
              [true false false]
              [true true false]]
             (tensor/->jvm greater))))

;; Pairwise distances between 2-D points.
(let [points (tensor/->tensor [[0.0 0.0]
                               [3.0 4.0]
                               [6.0 8.0]
                               [0.0 1.0]]
                              {:datatype :float64})
      distances (pairwise-distances points)]
  (assert (= [4 4] (vec (dtype/shape distances))))
  (assert (< (Math/abs (- 5.0 (tensor/mget distances 0 1))) 1.0e-12))
  (assert (< (Math/abs (- 1.0 (tensor/mget distances 0 3))) 1.0e-12))
  (assert (every? zero?
                  (map #(tensor/mget distances % %)
                       (range 4)))))

;; One-hot encoding is outer equality.
(let [labels (tensor/->tensor [0 2 1 2] {:datatype :int64})
      classes (tensor/->tensor [0 1 2] {:datatype :int64})
      mask (outer-operation dfn/eq labels classes)]
  (assert (= [[true false false]
              [false false true]
              [false true false]
              [false false true]]
             (tensor/->jvm mask))))
```

## Common Uses

- Build multiplication or comparison tables.
- Compute pairwise distances.
- Create one-hot masks.
- Generate coordinate fields.
- Compare every sample with every prototype.

## Recognition Clues

Look for `every pair`, `all combinations`, `distance matrix`, `outer product`, or `one-hot`.

## Memory Hooks

- Make one operand a column.
- Make the other operand a row.
- Broadcast to the pair grid.
- Apply any element-wise operation.
- Reduce the feature axis after all-pairs vector work.

## Key Insight

Outer operations turn a nested pair loop into perpendicular shapes and one element-wise expression.

