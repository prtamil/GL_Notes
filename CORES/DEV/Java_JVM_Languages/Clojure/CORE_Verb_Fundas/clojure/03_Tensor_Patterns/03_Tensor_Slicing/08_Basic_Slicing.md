# 8. Basic Slicing

## Mental Model

A slice selects a regular range on each axis.

An integer removes an axis. A range or `:all` keeps an axis.

`dtype-next` represents a slice as an index-space view. The selected values do not need a new buffer.

## Relationship to Cognitive Verb

```text
Slice -> choose regular index ranges -> keep a tensor view
```

## Clojure Functions and Common Idioms

|Need|Use|
|---|---|
|Whole axis|`:all`|
|Contiguous range|`(range start stop)`|
|Every step|`(range start stop step)`|
|Reverse one axis|`:lla`|
|Keep a size-one axis|a one-index range|
|Programmatic axis|build selectors, then `apply tensor/select`|

## Shape and Edge Behavior

- Integer selectors remove axes.
- Range selectors keep axes.
- A step greater than one creates an indirect view.
- `:lla` reverses an axis.
- `dtype-next` index ranges must contain valid indices.
- Build clipped ranges explicitly when user bounds can exceed an axis.
- A slice can share mutable storage with its source.

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

(defn clipped-range
  ([axis-size start stop]
   (clipped-range axis-size start stop 1))
  ([axis-size start stop step]
   (when-not (pos? step)
     (throw (ex-info "Slice step must be positive"
                     {:step step})))
   (range (max 0 start) (min axis-size stop) step)))

(defn select-axis [t axis selector]
  (let [rank (count (dtype/shape t))
        axis (normalize-axis rank axis)
        selectors (assoc (vec (repeat rank :all)) axis selector)]
    (apply tensor/select t selectors)))

(def t
  (tensor/reshape
    (dtype/make-container :jvm-heap :int64 (range 24))
    [2 3 4]))

(tensor/->jvm (tensor/select t :all (range 1 3) :all))
;; => [[[4 5 6 7] [8 9 10 11]]
;;     [[16 17 18 19] [20 21 22 23]]]

(tensor/->jvm (tensor/select t :all :all (range 0 4 2)))
;; => [[[0 2] [4 6] [8 10]]
;;     [[12 14] [16 18] [20 22]]]

(tensor/->jvm (select-axis t 0 :lla))
;; => [[[12 13 14 15] [16 17 18 19] [20 21 22 23]]
;;     [[0 1 2 3] [4 5 6 7] [8 9 10 11]]]

(assert (= [2 2 4]
           (vec (dtype/shape
                  (tensor/select t :all (range 1 3) :all)))))
(assert (= [2 3 2]
           (vec (dtype/shape
                  (tensor/select t :all :all (range 0 4 2))))))

;; Integer selection removes an axis.
(assert (= [3 4] (vec (dtype/shape (tensor/select t 0)))))

;; Range selection keeps an axis.
(assert (= [1 3 4]
           (vec (dtype/shape
                  (tensor/select t (range 0 1) :all :all)))))

;; User bounds can be clipped before selection.
(assert (= [2 3 4]
           (vec (dtype/shape
                  (select-axis t 2 (clipped-range 4 -5 99))))))

;; Slices are views.
(let [source (tensor/reshape
               (dtype/make-container :jvm-heap :int64 (range 24))
               [2 3 4])
      view (tensor/select source :all (range 1 3) :all)]
  (tensor/mset! view 0 0 0 64)
  (assert (= 64 (tensor/mget source 0 1 0))))

;; A scalar assignment fills a selected block.
(let [source (tensor/reshape
               (dtype/make-container :jvm-heap :int64 (range 24))
               [2 3 4])
      first-row (tensor/select source :all 0 :all)]
  (tensor/mset! first-row -1)
  (assert (= [[-1 -1 -1 -1]
              [-1 -1 -1 -1]]
             (tensor/->jvm first-row))))
```

## Common Uses

- Crop images or volumes.
- Keep a batch axis of size one.
- Subsample signals.
- Reverse an axis.
- Assign a value to a regular block.

## Recognition Clues

Look for `range`, `crop`, `every other`, `reverse`, `band`, or `sub-block`.

## Memory Hooks

- Integer removes an axis.
- Range keeps an axis.
- `:all` keeps the whole axis.
- `:lla` reverses one axis.
- Selected views can mutate the source.

## Key Insight

Basic slicing changes the index mapping. It does not need to copy the selected values.

