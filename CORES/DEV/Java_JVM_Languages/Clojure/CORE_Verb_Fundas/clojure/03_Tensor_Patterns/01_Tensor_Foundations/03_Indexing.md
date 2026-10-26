# 3. Indexing

## Mental Model

Each integer index consumes one axis. A partial index returns the remaining sub-tensor.

```text
shape [2 3 4]

index [1]       -> shape [3 4]
index [1 2]     -> shape [4]
index [1 2 3]   -> scalar value
```

A selection range keeps its axis. An integer selection removes its axis.

## Relationship to Cognitive Verb

```text
Locate -> give one coordinate per consumed axis -> read the value or view
```

## Clojure Functions and Common Idioms

|Need|Use|
|---|---|
|Read one value|`tensor/mget`|
|Read a sub-tensor|`tensor/mget` with fewer indices|
|Select axes|`tensor/select`|
|Keep all values on an axis|`:all`|
|Keep a bounded range|a Clojure `range`|
|Write through a view|`tensor/mset!`|
|Independent storage|`tensor/clone`|

## Shape and Edge Behavior

- A complete coordinate returns a scalar.
- A partial coordinate returns a tensor view.
- An integer selection removes one axis.
- A range or `:all` keeps one axis.
- An invalid integer index throws.
- A selected view can share mutable storage with its source.
- Empty selections produce an axis of size zero.

## Clojure Recipe Book

```clojure
(require '[tech.v3.datatype :as dtype]
         '[tech.v3.tensor :as tensor])

(defn tensor-value [t coordinate]
  (apply tensor/mget t coordinate))

(defn all-indices [shape]
  (reduce
    (fn [prefixes axis-size]
      (for [prefix prefixes
            index (range axis-size)]
        (conj prefix index)))
    [[]]
    shape))

(defn select-last [t index]
  (let [rank (count (dtype/shape t))]
    (apply tensor/select
           t
           (concat (repeat (dec rank) :all) [index]))))

(def t
  (tensor/reshape
    (dtype/make-container :jvm-heap :int64 (range 24))
    [2 3 4]))

(tensor/mget t 1 2 3)
;; => 23

(tensor/->jvm (tensor/mget t 1))
;; => [[12 13 14 15]
;;     [16 17 18 19]
;;     [20 21 22 23]]

(tensor/->jvm (tensor/select t 0 :all 1))
;; => [1 5 9]

(tensor/->jvm (tensor/select t (range 0 1) :all :all))
;; => [[[0 1 2 3]
;;      [4 5 6 7]
;;      [8 9 10 11]]]

(tensor/->jvm (select-last t 0))
;; => [[0 4 8]
;;     [12 16 20]]

(assert (= 23 (tensor-value t [1 2 3])))
(assert (= [3 4] (vec (dtype/shape (tensor/mget t 1)))))
(assert (= [3] (vec (dtype/shape (tensor/select t 0 :all 1)))))
(assert (= [1 3 4]
           (vec (dtype/shape
                  (tensor/select t (range 0 1) :all :all)))))
(assert (= [2 3] (vec (dtype/shape (select-last t 0)))))

;; Row-major index order changes the last axis fastest.
(assert (= [[0 0 0]
            [0 0 1]
            [0 0 2]
            [0 0 3]
            [0 1 0]]
           (vec (take 5 (all-indices [2 3 4])))))
(assert (= 24 (count (all-indices [2 3 4]))))

;; Index order agrees with the row-major buffer.
(let [flat-values (dtype/->vector t)]
  (assert
    (every?
      true?
      (map-indexed
        (fn [flat-index coordinate]
          (= (nth flat-values flat-index)
             (tensor-value t coordinate)))
        (all-indices (dtype/shape t))))))

;; Partial indexing returns a view that shares storage.
(let [source (tensor/reshape
               (dtype/make-container :jvm-heap :int64 (range 24))
               [2 3 4])
      view (tensor/mget source 0)]
  (tensor/mset! view 0 0 99)
  (assert (= 99 (tensor/mget source 0 0 0))))

;; Clone creates independent storage.
(let [source (tensor/reshape
               (dtype/make-container :jvm-heap :int64 (range 6))
               [2 3])
      copy (tensor/clone source)]
  (tensor/mset! copy 0 0 77)
  (assert (= 0 (tensor/mget source 0 0)))
  (assert (= 77 (tensor/mget copy 0 0))))

(assert (try
          (tensor/mget t 2 0 0)
          false
          (catch IndexOutOfBoundsException _ true)))
```

NumPy uses ellipsis syntax for rank-independent indexing. `select-last` provides that intent with an explicit Clojure helper.

`dtype-next` selection is an index-space view. This differs from NumPy fancy indexing, which usually copies.

## Common Uses

- Read one cell.
- Select one batch item.
- Keep a batch axis of size one.
- Read one feature across all samples.
- Enumerate every coordinate.

## Recognition Clues

Look for `coordinate`, `sub-tensor`, `first item`, `last axis`, `slice`, or `view`.

## Memory Hooks

- Integer selection consumes an axis.
- Range selection keeps an axis.
- Partial indexing returns a view.
- Views can mutate their source.
- Clone when storage must be independent.

## Key Insight

Indexing changes both the selected values and the result rank. Predict both before you read the result.

