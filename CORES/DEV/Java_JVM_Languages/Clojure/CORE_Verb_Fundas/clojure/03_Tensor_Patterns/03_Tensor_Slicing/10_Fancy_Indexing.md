# 10. Fancy Indexing

## Mental Model

Fancy indexing gathers arbitrary positions. The indices can reorder or repeat values.

A regular slice describes a view. A gather describes a new ordered result.

This lesson clones gathered results to match NumPy copy semantics.

## Relationship to Cognitive Verb

```text
Gather -> list the positions -> build the result in that order
```

## Clojure Functions and Common Idioms

|Need|Use|
|---|---|
|Gather one axis|`tensor/select`, then `tensor/clone`|
|Reorder|use indices in the required order|
|Repeat|repeat an index|
|Paired positions|map `tensor/mget` over coordinates|
|Cross-product sub-grid|nested row and column indices|
|Accumulate repeats|update each index in sequence|

## Shape and Edge Behavior

- Gather indices must be valid integers.
- Indices can appear in any order.
- Duplicate indices are valid.
- A gathered axis size equals the index count.
- Paired coordinate lists must have equal lengths.
- This course returns independent storage from gather helpers.
- Empty index input produces a zero-sized gathered axis.

## Clojure Recipe Book

```clojure
(require '[tech.v3.datatype :as dtype]
         '[tech.v3.tensor :as tensor])

(defn normalize-axis [rank axis]
  (let [axis (if (neg? axis) (+ rank axis) axis)]
    (when-not (< -1 axis rank)
      (throw (ex-info "Axis is outside the tensor rank"
                      {:axis axis :rank rank})))
    axis))

(defn gather-axis [t axis indices]
  (let [rank (count (dtype/shape t))
        axis (normalize-axis rank axis)
        selectors (assoc (vec (repeat rank :all)) axis (vec indices))]
    (tensor/clone (apply tensor/select t selectors))))

(defn gather-coordinates [t coordinates]
  (mapv (fn [coordinate]
          (apply tensor/mget t coordinate))
        coordinates))

(defn gather-grid [matrix rows columns]
  (tensor/->tensor
    (mapv (fn [row]
            (mapv (fn [column]
                    (tensor/mget matrix row column))
                  columns))
          rows)
    {:datatype (dtype/elemwise-datatype matrix)}))

(defn gather-each-row [matrix column-indices]
  (let [rows (first (dtype/shape matrix))]
    (when-not (= rows (count column-indices))
      (throw (ex-info "Each row needs one column index"
                      {:rows rows
                       :index-count (count column-indices)})))
    (mapv (fn [row column]
            (tensor/mget matrix row column))
          (range rows)
          column-indices)))

(defn scatter-add! [target indices values]
  (when-not (= (count indices) (count values))
    (throw (ex-info "Indices and values must have equal lengths" {})))
  (doseq [[index value] (map vector indices values)]
    (tensor/mset! target index
                  (+ (tensor/mget target index) value)))
  target)

(def matrix
  (tensor/reshape
    (dtype/make-container :jvm-heap :int64 (range 12))
    [3 4]))

(tensor/->jvm (gather-axis matrix 0 [2 0 2]))
;; => [[8 9 10 11]
;;     [0 1 2 3]
;;     [8 9 10 11]]

(gather-coordinates matrix [[0 1] [1 2]])
;; => [1 6]

(tensor/->jvm (gather-grid matrix [0 1] [1 2]))
;; => [[1 2]
;;     [5 6]]

(gather-each-row matrix [3 2 1])
;; => [3 6 9]

(assert (= [3 4]
           (vec (dtype/shape (gather-axis matrix 0 [2 0 2])))))
(assert (= [[8 9 10 11] [0 1 2 3] [8 9 10 11]]
           (tensor/->jvm (gather-axis matrix 0 [2 0 2]))))
(assert (= [1 6]
           (gather-coordinates matrix [[0 1] [1 2]])))
(assert (= [[1 2] [5 6]]
           (tensor/->jvm (gather-grid matrix [0 1] [1 2]))))
(assert (= [3 6 9] (gather-each-row matrix [3 2 1])))

;; Gather returns independent storage.
(let [gathered (gather-axis matrix 0 [2 0])]
  (tensor/mset! gathered 0 0 99)
  (assert (= 8 (tensor/mget matrix 2 0))))

;; Duplicate scatter positions accumulate one update at a time.
(let [target (tensor/new-tensor [3] {:datatype :int64})]
  (scatter-add! target [0 0 0 2] [1 1 1 5])
  (assert (= [3 0 5] (dtype/->vector target))))
```

Raw `tensor/select` can keep an indexed view. The `gather-axis` helper clones it to give clear gather semantics.

## Common Uses

- Select a batch by identifier.
- Reorder rows by a permutation.
- Gather embeddings.
- Read paired coordinates.
- Accumulate repeated indices.

## Recognition Clues

Look for `specific positions`, `reorder`, `permutation`, `gather`, `repeat`, or `index list`.

## Memory Hooks

- Gather order follows index order.
- Duplicate indices stay duplicated.
- Paired indices zip.
- Nested index loops form a cross product.
- Clone when the gather result must be independent.

## Key Insight

Fancy indexing describes output order with explicit positions. It is selection by address, not selection by interval.

