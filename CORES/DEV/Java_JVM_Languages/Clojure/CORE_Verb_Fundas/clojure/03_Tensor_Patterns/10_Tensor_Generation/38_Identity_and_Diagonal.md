# 38. Identity and Diagonal

## Mental Model

Diagonal generation selects coordinates with a fixed difference between column and row indices.

```text
column - row = offset
```

Offset zero selects the main diagonal. Positive offsets move above it. Negative offsets move below it.

## Relationship to Cognitive Verb

```text
Align -> compare row and column indices -> select one diagonal band
```

## Clojure Functions and Common Idioms

|Need|Use|
|---|---|
|Identity matrix|Place ones on offset zero|
|Rectangular identity|Choose separate row and column counts|
|Build from a vector|Place vector values on an offset diagonal|
|Extract a diagonal|Read coordinates with a fixed offset|
|Causal mask|Keep coordinates where column is not greater than row|

## Shape and Edge Behavior

- Row and column counts must not be negative.
- A positive offset selects an upper diagonal.
- A negative offset selects a lower diagonal.
- An offset outside the matrix produces an empty extracted diagonal.
- Diagonal extraction requires rank two.
- Empty rectangular matrices are valid.
- The generated tensors own their storage unless stated otherwise.

## Clojure Recipe Book

```clojure
(require '[tech.v3.datatype :as dtype]
         '[tech.v3.tensor :as tensor])

(defn valid-size [size name]
  (when (neg? size)
    (throw (ex-info "Matrix sizes must not be negative"
                    {name size})))
  size)

(defn eye
  ([size]
   (eye size size 0 :float64))
  ([rows cols]
   (eye rows cols 0 :float64))
  ([rows cols offset datatype]
   (valid-size rows :rows)
   (valid-size cols :cols)
   (tensor/clone
     (tensor/compute-tensor
       [rows cols]
       (fn [row col]
         (if (= (- col row) offset) 1 0))
       datatype))))

(defn diagonal-from
  ([values]
   (diagonal-from values 0))
  ([values offset]
   (let [shape (vec (dtype/shape values))]
     (when-not (= 1 (count shape))
       (throw (ex-info "Diagonal values must have rank one"
                       {:shape shape})))
     (let [size (first shape)
           rows (+ size (max 0 (- offset)))
           cols (+ size (max 0 offset))]
       (tensor/clone
         (tensor/compute-tensor
           [rows cols]
           (fn [row col]
             (if (= (- col row) offset)
               (let [index (if (neg? offset) col row)]
                 (tensor/mget values index))
               0))
           (dtype/elemwise-datatype values)))))))

(defn diagonal
  ([matrix]
   (diagonal matrix 0))
  ([matrix offset]
   (let [shape (vec (dtype/shape matrix))]
     (when-not (= 2 (count shape))
       (throw (ex-info "Diagonal extraction requires rank two"
                       {:shape shape})))
     (let [[rows cols] shape
           start-row (max 0 (- offset))
           start-col (max 0 offset)
           size (max 0 (min (- rows start-row)
                            (- cols start-col)))]
       (tensor/clone
         (tensor/compute-tensor
           [size]
           (fn [index]
             (tensor/mget matrix
                          (+ start-row index)
                          (+ start-col index)))
           (dtype/elemwise-datatype matrix)))))))

(defn fill-diagonal!
  ([matrix value]
   (fill-diagonal! matrix value 0))
  ([matrix value offset]
   (let [start-row (max 0 (- offset))
         start-col (max 0 offset)
         size (first (dtype/shape (diagonal matrix offset)))]
     (doseq [index (range size)]
       (tensor/mset! matrix
                     (+ start-row index)
                     (+ start-col index)
                     value))
     matrix)))

(defn lower-triangle-mask [rows cols offset]
  (tensor/clone
    (tensor/compute-tensor
      [rows cols]
      (fn [row col]
        (<= (- col row) offset))
      :boolean)))

(assert (= [[1.0 0.0 0.0]
            [0.0 1.0 0.0]
            [0.0 0.0 1.0]]
           (tensor/->jvm (eye 3))))

(assert (= [[0 1 0 0]
            [0 0 1 0]
            [0 0 0 1]]
           (tensor/->jvm (eye 3 4 1 :int64))))

(def values
  (tensor/->tensor [5 6 7] {:datatype :int64}))

(assert (= [[0 5 0 0]
            [0 0 6 0]
            [0 0 0 7]]
           (tensor/->jvm (diagonal-from values 1))))

(def matrix
  (tensor/->tensor [[0 1 2 3]
                    [4 5 6 7]
                    [8 9 10 11]]
                   {:datatype :int64}))

(assert (= [0 5 10] (dtype/->vector (diagonal matrix))))
(assert (= [1 6 11] (dtype/->vector (diagonal matrix 1))))
(assert (= [4 9] (dtype/->vector (diagonal matrix -1))))
(assert (= [] (dtype/->vector (diagonal matrix 8))))

(let [target (tensor/clone matrix)]
  (fill-diagonal! target -1)
  (assert (= [-1 -1 -1] (dtype/->vector (diagonal target)))))

(assert (= [[true false false false]
            [true true false false]
            [true true true false]
            [true true true true]]
           (tensor/->jvm (lower-triangle-mask 4 4 0))))

(assert (= [0 3] (vec (dtype/shape (eye 0 3)))))
```

## Common Uses

- Create identity transforms.
- Add diagonal regularization.
- Extract matrix traces.
- Build causal attention masks.
- Select upper or lower triangular regions.

## Recognition Clues

Look for `identity`, `main diagonal`, `offset diagonal`, `triangular`, `trace`, or `causal mask`.

## Memory Hooks

- Compare column with row.
- Equal indices form the main diagonal.
- Positive offset moves up.
- Negative offset moves down.
- Inequalities form triangular masks.

## Key Insight

Identity, diagonal, and triangular patterns all come from simple relations between row and column coordinates.

