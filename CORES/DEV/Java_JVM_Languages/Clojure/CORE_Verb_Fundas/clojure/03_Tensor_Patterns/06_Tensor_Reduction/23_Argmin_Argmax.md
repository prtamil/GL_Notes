# 23. Argmin and Argmax

## Mental Model

Maximum returns a value. Argmax returns the position of that value along the reduced axis.

The result uses the same shape rule as other reductions. The selected axis disappears.

## Relationship to Cognitive Verb

```text
Locate an extreme -> compare values along one axis -> return the winning position
```

## Clojure Functions and Common Idioms

|Need|Use|
|---|---|
|Flat maximum position|`argops/argmax` on a flat reader|
|Flat minimum position|`argops/argmin` on a flat reader|
|One-axis positions|`tensor/reduce-axis` with an arg operation|
|Flat position to coordinate|divide by row-major strides|
|Recover source values|insert each winning axis index|
|All matching positions|Boolean-mask coordinates, not argmax|

## Shape and Edge Behavior

- Results contain indices, not source values.
- Axis indices start at zero.
- Ties select the first occurrence.
- Global argmax returns one flat index.
- One-axis argmax lowers rank by one.
- Empty input has no winning position.
- Several reduced axes must first be merged.

## Clojure Recipe Book

```clojure
(require '[tech.v3.datatype :as dtype]
         '[tech.v3.datatype.argops :as argops]
         '[tech.v3.tensor :as tensor])

(defn normalize-axis [rank axis]
  (let [axis (if (neg? axis) (+ rank axis) axis)]
    (when-not (< -1 axis rank)
      (throw (ex-info "Axis is outside the tensor rank"
                      {:axis axis :rank rank})))
    axis))

(defn row-major-strides [shape]
  (if (empty? shape)
    []
    (->> (reverse (rest shape))
         (reductions * 1)
         reverse
         vec)))

(defn flat->coordinate [shape flat-index]
  (when-not (< -1 flat-index (reduce * 1 shape))
    (throw (ex-info "Flat index is outside the tensor"
                    {:shape shape :flat-index flat-index})))
  (loop [remaining flat-index
         strides (row-major-strides shape)
         coordinate []]
    (if-let [stride (first strides)]
      (recur (mod remaining stride)
             (next strides)
             (conj coordinate (quot remaining stride)))
      coordinate)))

(defn insert-at [values index value]
  (vec (concat (subvec (vec values) 0 index)
               [value]
               (subvec (vec values) index))))

(defn tensor-indices [shape]
  (reduce
    (fn [prefixes axis-size]
      (for [prefix prefixes
            index (range axis-size)]
        (conj prefix index)))
    [[]]
    shape))

(defn argmax-axis [t axis]
  (let [shape (vec (dtype/shape t))
        axis (normalize-axis (count shape) axis)]
    (when (zero? (nth shape axis))
      (throw (ex-info "Argmax requires a value on the reduced axis"
                      {:shape shape :axis axis})))
    (if (= 1 (count shape))
      (argops/argmax (dtype/->reader t))
      (tensor/reduce-axis t argops/argmax axis :int64))))

(defn values-at-axis-indices [source axis index-tensor]
  (let [source-shape (vec (dtype/shape source))
        axis (normalize-axis (count source-shape) axis)
        result-shape (vec (dtype/shape index-tensor))]
    (tensor/compute-tensor
      result-shape
      (fn [& result-coordinate]
        (let [axis-index (apply tensor/mget index-tensor result-coordinate)
              source-coordinate (insert-at result-coordinate axis axis-index)]
          (apply tensor/mget source source-coordinate)))
      (dtype/elemwise-datatype source))))

(def matrix
  (tensor/->tensor [[1 9 3 7]
                    [8 2 6 4]
                    [5 5 1 0]]
                   {:datatype :int64}))

(def positions (argmax-axis matrix 1))

(dtype/->vector positions)
;; => [1 0 0]

(assert (= [3] (vec (dtype/shape positions))))
(assert (= [1 0 0] (dtype/->vector positions)))
(assert (= [9 8 5]
           (dtype/->vector
             (values-at-axis-indices matrix 1 positions))))

;; Ties select the first position.
(let [ties (tensor/->tensor [[5 5 5] [2 2 2]] {:datatype :int64})]
  (assert (= [0 0]
             (dtype/->vector (argmax-axis ties 1)))))

;; Global argmax uses a flat row-major position.
(let [flat-index (argops/argmax (dtype/->reader matrix))
      coordinate (flat->coordinate (dtype/shape matrix) flat-index)]
  (assert (= 1 flat-index))
  (assert (= [0 1] coordinate))
  (assert (= 9 (apply tensor/mget matrix coordinate))))

;; Rank-1 argmax returns a Clojure integer.
(let [values (tensor/->tensor [3 8 8 2] {:datatype :int64})]
  (assert (= 1 (argmax-axis values 0))))

;; Argmin uses the same position rule.
(assert (= 3 (argops/argmin (dtype/->reader
                              (tensor/->tensor [3 8 8 2]
                                               {:datatype :int64})))))

(assert (try
          (argmax-axis (tensor/->tensor [] {:datatype :int64}) 0)
          false
          (catch clojure.lang.ExceptionInfo _ true)))
```

Use maximum when only the value matters. Use argmax when the position selects related data from another tensor.

## Common Uses

- Select the predicted class.
- Locate a global peak.
- Recover labels at winning scores.
- Find the closest or farthest candidate.
- Rank values by position.

## Recognition Clues

Look for `position of maximum`, `winning index`, `predicted class`, `where is the minimum`, or `best candidate`.

## Memory Hooks

- Arg operations return positions.
- Positions are relative to the reduced axis.
- Ties choose the first value.
- Global positions are flat.
- Convert flat positions back with the shape.

## Key Insight

Argmin and argmax preserve location information that an ordinary minimum or maximum discards.

