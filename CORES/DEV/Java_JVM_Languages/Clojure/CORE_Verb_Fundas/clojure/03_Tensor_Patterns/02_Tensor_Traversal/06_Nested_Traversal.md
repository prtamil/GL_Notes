# 6. Nested Traversal

## Mental Model

Nested traversal visits every coordinate and value.

The rank controls the conceptual loop depth. A rank-independent function builds coordinates from the shape.

Row-major traversal changes the last index fastest.

## Relationship to Cognitive Verb

```text
Enumerate -> form every valid coordinate -> read its value
```

## Clojure Functions and Common Idioms

|Need|Use|
|---|---|
|All coordinates|Cartesian product of axis ranges|
|Coordinate and value|`map` with `tensor/mget`|
|First matching coordinate|`some`|
|All matching coordinates|`filter`|
|Coordinate-based tensor|`tensor/compute-tensor`|
|Only values|use flat traversal|

## Shape and Edge Behavior

- A scalar shape has one conceptual coordinate: `[]`.
- A shape with a zero axis has no coordinates.
- Finite shapes produce a finite lazy coordinate sequence.
- Negative shape values are invalid.
- Visit count equals the product of the shape values.

## Clojure Recipe Book

```clojure
(require '[tech.v3.datatype :as dtype]
         '[tech.v3.tensor :as tensor])

(defn shape-size [shape]
  (reduce * 1 shape))

(defn tensor-indices [shape]
  (when (some neg? shape)
    (throw (ex-info "Shape values must not be negative"
                    {:shape shape})))
  (reduce
    (fn [prefixes axis-size]
      (for [prefix prefixes
            index (range axis-size)]
        (conj prefix index)))
    [[]]
    shape))

(defn indexed-values [t]
  (map (fn [coordinate]
         [coordinate (apply tensor/mget t coordinate)])
       (tensor-indices (dtype/shape t))))

(defn first-coordinate [pred t]
  (some (fn [[coordinate value]]
          (when (pred value) coordinate))
        (indexed-values t)))

(defn matching-coordinates [pred t]
  (into []
        (comp (filter (fn [[_ value]] (pred value)))
              (map first))
        (indexed-values t)))

(def t
  (tensor/reshape
    (dtype/make-container :jvm-heap :int64 (range 24))
    [2 3 4]))

(take 5 (indexed-values t))
;; => ([[0 0 0] 0]
;;     [[0 0 1] 1]
;;     [[0 0 2] 2]
;;     [[0 0 3] 3]
;;     [[0 1 0] 4])

(first-coordinate #(= 21 %) t)
;; => [1 2 1]

(matching-coordinates #(zero? (mod % 7)) t)
;; => [[0 0 0] [0 1 3] [1 0 2] [1 2 1]]

(assert (= 24 (count (tensor-indices [2 3 4]))))
(assert (= (shape-size [2 3 4])
           (count (indexed-values t))))
(assert (= [[0 0 0] 0] (first (indexed-values t))))
(assert (= [[1 2 3] 23] (last (indexed-values t))))
(assert (= [1 2 1] (first-coordinate #(= 21 %) t)))
(assert (= [[0 0 0] [0 1 3] [1 0 2] [1 2 1]]
           (matching-coordinates #(zero? (mod % 7)) t)))

;; Rank zero has one conceptual coordinate.
(assert (= [[]] (vec (tensor-indices []))))

;; Any zero axis makes the coordinate product empty.
(assert (empty? (tensor-indices [2 0 4])))

;; Generate a value from each coordinate.
(let [grid (tensor/compute-tensor
             [2 3 4]
             (fn [i j k] (+ i j k))
             :int64)]
  (assert (= 0 (tensor/mget grid 0 0 0)))
  (assert (= 6 (tensor/mget grid 1 2 3))))

(assert (try
          (doall (tensor-indices [2 -1 4]))
          false
          (catch clojure.lang.ExceptionInfo _ true)))
```

Traversal is useful when coordinates are part of the answer. Use element-wise operations when only values matter.

## Common Uses

- Build sparse coordinate-value pairs.
- Find a matching position.
- Debug a generic tensor function.
- Generate values from coordinates.
- Serialize data with explicit coordinates.

## Recognition Clues

Look for `every coordinate`, `position and value`, `any rank`, `sparse`, or `where`.

## Memory Hooks

- Build one range for each axis.
- The last coordinate changes fastest.
- The visit count is the shape product.
- Keep coordinates only when the result needs them.

## Key Insight

Nested traversal converts shape metadata into a sequence of coordinate-value pairs.

