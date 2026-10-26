# 11. Boolean Masking

## Mental Model

A comparison produces a Boolean tensor. Each true value selects the value at the same coordinate.

An arbitrary set of matching cells has no rectangular shape. Extraction therefore returns a rank-1 tensor.

## Relationship to Cognitive Verb

```text
Filter -> compute one Boolean per value -> extract, count, locate, or replace
```

## Clojure Functions and Common Idioms

|Need|Use|
|---|---|
|Build a mask|`dfn/>`, `dfn/<`, or `dfn/eq`|
|Combine masks|`dfn/and`, `dfn/or`, or `dfn/not`|
|Extract values|filter paired value and mask readers|
|Count matches|count true mask values|
|Find positions|traverse mask coordinates|
|Keep the shape|choose a value per coordinate|
|Assign matches|write through matching coordinates|

## Shape and Edge Behavior

- A full mask must have the same shape as its target.
- Full-mask extraction returns rank 1.
- No matches produce shape `[0]`.
- Mask combination is element-wise.
- Shape-preserving selection keeps the source shape.
- Assignment visits each matching coordinate once.

## Clojure Recipe Book

```clojure
(require '[tech.v3.datatype :as dtype]
         '[tech.v3.datatype.functional :as dfn]
         '[tech.v3.tensor :as tensor])

(defn tensor-indices [shape]
  (reduce
    (fn [prefixes axis-size]
      (for [prefix prefixes
            index (range axis-size)]
        (conj prefix index)))
    [[]]
    shape))

(defn require-same-shape [left right]
  (when-not (= (vec (dtype/shape left))
               (vec (dtype/shape right)))
    (throw (ex-info "Mask and tensor shapes must match"
                    {:tensor-shape (vec (dtype/shape left))
                     :mask-shape (vec (dtype/shape right))}))))

(defn masked-values [t mask]
  (require-same-shape t mask)
  (tensor/->tensor
    (into []
          (comp (filter second)
                (map first))
          (map vector (dtype/->reader t) (dtype/->reader mask)))
    {:datatype (dtype/elemwise-datatype t)}))

(defn matching-coordinates [mask]
  (into []
        (filter (fn [coordinate]
                  (true? (apply tensor/mget mask coordinate))))
        (tensor-indices (dtype/shape mask))))

(defn choose-values [pred true-value false-value t]
  (tensor/compute-tensor
    (vec (dtype/shape t))
    (fn [& coordinate]
      (let [value (apply tensor/mget t coordinate)]
        (if (pred value) true-value false-value)))
    (dtype/elemwise-datatype t)))

(defn assign-mask! [t mask value]
  (require-same-shape t mask)
  (doseq [coordinate (matching-coordinates mask)]
    (apply tensor/mset! t (concat coordinate [value])))
  t)

(def t
  (tensor/reshape
    (dtype/make-container :jvm-heap :int64 (range 24))
    [2 3 4]))

(def over-15 (dfn/> t 15))
(def between-5-and-10
  (dfn/and (dfn/> t 5) (dfn/< t 10)))

(dtype/->vector (masked-values t over-15))
;; => [16 17 18 19 20 21 22 23]

(matching-coordinates (dfn/> t 20))
;; => [[1 2 1] [1 2 2] [1 2 3]]

(assert (= [2 3 4] (vec (dtype/shape over-15))))
(assert (= :boolean (dtype/elemwise-datatype over-15)))
(assert (= [16 17 18 19 20 21 22 23]
           (dtype/->vector (masked-values t over-15))))
(assert (= [6 7 8 9]
           (dtype/->vector (masked-values t between-5-and-10))))
(assert (= 8 (count (filter true? (dtype/->reader over-15)))))
(assert (= [[1 2 1] [1 2 2] [1 2 3]]
           (matching-coordinates (dfn/> t 20))))

;; Shape-preserving choice does not flatten the result.
(let [binary (choose-values #(> % 20) 1 0 t)]
  (assert (= [2 3 4] (vec (dtype/shape binary))))
  (assert (= 3 (reduce + (dtype/->reader binary)))))

;; Assignment changes only matching positions.
(let [source (tensor/clone t)
      mask (dfn/> source 20)]
  (assign-mask! source mask 0)
  (assert (= [20 0 0 0]
             (subvec (dtype/->vector source) 20 24))))

;; No matches return a typed empty tensor.
(let [empty-result (masked-values t (dfn/> t 100))]
  (assert (= [0] (vec (dtype/shape empty-result))))
  (assert (= :int64 (dtype/elemwise-datatype empty-result))))
```

## Common Uses

- Remove invalid values.
- Find threshold crossings.
- Clip or replace outliers.
- Count values that satisfy a condition.
- Convert dense data to sparse coordinates.

## Recognition Clues

Look for `where`, `condition`, `threshold`, `filter`, `replace matching`, or `valid values`.

## Memory Hooks

- A comparison returns a Boolean tensor.
- A full mask has the target shape.
- Extraction becomes rank one.
- Coordinates preserve position information.
- Conditional choice can preserve the shape.

## Key Insight

Boolean masking separates selection logic from the action taken on matching values.

