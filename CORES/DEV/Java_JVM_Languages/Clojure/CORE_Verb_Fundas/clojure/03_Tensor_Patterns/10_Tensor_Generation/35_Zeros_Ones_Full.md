# 35. Zeros, Ones, and Full

## Mental Model

Generation starts with a shape, a data type, and an initial value.

```text
shape + data type + fill value -> new tensor storage
```

Choose the data type before you write values. An integer tensor cannot keep fractional data.

## Relationship to Cognitive Verb

```text
Initialize -> choose shape and data type -> allocate once -> set a known value
```

## Clojure Functions and Common Idioms

|Need|Use|
|---|---|
|Zeros|`tensor/new-tensor`|
|Constant values|Create a filled typed container, then reshape it|
|Ones|Use the constant-value helper with `1`|
|Match another tensor|Read its shape and element data type|
|Build incrementally|Allocate once, then use `tensor/mset!`|

## Shape and Edge Behavior

- Shape dimensions must not be negative.
- A zero dimension creates an empty tensor.
- Each call creates independent storage.
- The data type controls conversion on assignment.
- Rank-zero tensors are not used in this course. Use Clojure scalars instead.
- Tensor input must be rectangular.

## Clojure Recipe Book

```clojure
(require '[tech.v3.datatype :as dtype]
         '[tech.v3.tensor :as tensor])

(defn valid-shape [shape]
  (let [shape (vec shape)]
    (when (some neg? shape)
      (throw (ex-info "Shape dimensions must not be negative"
                      {:shape shape})))
    shape))

(defn zeros
  ([shape]
   (zeros shape :float64))
  ([shape datatype]
   (tensor/new-tensor (valid-shape shape) {:datatype datatype})))

(defn full
  ([shape value]
   (full shape value :float64))
  ([shape value datatype]
   (let [shape (valid-shape shape)
         item-count (reduce * 1 shape)]
     (tensor/reshape
       (dtype/make-container :jvm-heap datatype
                             (repeat item-count value))
       shape))))

(defn ones
  ([shape]
   (ones shape :float64))
  ([shape datatype]
   (full shape 1 datatype)))

(defn zeros-like
  ([t]
   (zeros (dtype/shape t) (dtype/elemwise-datatype t)))
  ([t datatype]
   (zeros (dtype/shape t) datatype)))

(defn full-like
  ([t value]
   (full (dtype/shape t) value (dtype/elemwise-datatype t)))
  ([t value datatype]
   (full (dtype/shape t) value datatype)))

(assert (= [[0.0 0.0 0.0]
            [0.0 0.0 0.0]]
           (tensor/->jvm (zeros [2 3]))))

(assert (= [[1 1 1]
            [1 1 1]]
           (tensor/->jvm (ones [2 3] :int64))))

(assert (= [[7 7]
            [7 7]]
           (tensor/->jvm (full [2 2] 7 :int64))))

(def source
  (tensor/->tensor [[1 2 3]
                    [4 5 6]]
                   {:datatype :int64}))

(let [result (zeros-like source)]
  (assert (= [2 3] (vec (dtype/shape result))))
  (assert (= :int64 (dtype/elemwise-datatype result))))

(assert (= [[-1.0 -1.0 -1.0]
            [-1.0 -1.0 -1.0]]
           (tensor/->jvm (full-like source -1 :float64))))

;; Each call owns its storage.
(let [left (zeros [2 2] :int64)
      right (zeros [2 2] :int64)]
  (tensor/mset! left 0 0 9)
  (assert (= 0 (tensor/mget right 0 0))))

;; Preallocate when the final shape is known.
(let [result (zeros [4 3] :int64)]
  (doseq [row (range 4)
          col (range 3)]
    (tensor/mset! result row col row))
  (assert (= [[0 0 0]
              [1 1 1]
              [2 2 2]
              [3 3 3]]
             (tensor/->jvm result))))

(assert (= [0 3] (vec (dtype/shape (zeros [0 3])))))
```

## Common Uses

- Create accumulators.
- Preallocate output buffers.
- Build masks.
- Set sentinel values.
- Initialize model state.

## Recognition Clues

Look for `initialize`, `preallocate`, `same shape`, `fill`, `mask`, or `sentinel`.

## Memory Hooks

- Shape controls layout.
- Data type controls stored values.
- Fill gives known initial state.
- Each call allocates independent storage.
- Allocate once when the final shape is known.

## Key Insight

Initialization is a design choice. Set the shape, data type, and starting value before later operations depend on them.

