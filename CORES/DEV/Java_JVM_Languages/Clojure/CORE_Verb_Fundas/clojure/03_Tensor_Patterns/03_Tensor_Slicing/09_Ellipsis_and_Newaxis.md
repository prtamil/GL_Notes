# 9. Ellipsis and New Axis

## Mental Model

NumPy ellipsis means all unlisted axes. Clojure has no tensor ellipsis syntax.

Build the required `:all` selectors when you need rank-independent selection.

A new axis has size one. Add it with reshape because it contains no new values.

## Relationship to Cognitive Verb

```text
Align -> select from an end or insert a size-one axis -> preserve intent across ranks
```

## Clojure Functions and Common Idioms

|Need|Use|
|---|---|
|First axis, any rank|`tensor/select` with the first selector|
|Last axis, any rank|generate leading `:all` selectors|
|Add an axis|insert `1` into the shape, then reshape|
|Remove a size-one axis|remove it from the shape, then reshape|
|Programmatic axis|normalize it before shape editing|

## Shape and Edge Behavior

- Adding an axis increases rank by one.
- The inserted axis always has size one.
- Adding an axis preserves the element count.
- Squeeze is valid only for an axis of size one.
- This course does not reshape a rank-1 tensor into a rank-0 `dtype-next` tensor.
- Expand and squeeze views can share storage.

## Clojure Recipe Book

```clojure
(require '[tech.v3.datatype :as dtype]
         '[tech.v3.tensor :as tensor])

(defn normalize-insertion-axis [rank axis]
  (let [new-rank (inc rank)
        axis (if (neg? axis) (+ new-rank axis) axis)]
    (when-not (< -1 axis new-rank)
      (throw (ex-info "Insertion axis is outside the new rank"
                      {:axis axis :rank rank})))
    axis))

(defn normalize-axis [rank axis]
  (let [axis (if (neg? axis) (+ rank axis) axis)]
    (when-not (< -1 axis rank)
      (throw (ex-info "Axis is outside the tensor rank"
                      {:axis axis :rank rank})))
    axis))

(defn insert-at [values index value]
  (vec (concat (subvec (vec values) 0 index)
               [value]
               (subvec (vec values) index))))

(defn remove-at [values index]
  (into (subvec (vec values) 0 index)
        (subvec (vec values) (inc index))))

(defn expand-axis [t axis]
  (let [shape (vec (dtype/shape t))
        axis (normalize-insertion-axis (count shape) axis)]
    (tensor/reshape t (insert-at shape axis 1))))

(defn squeeze-axis [t axis]
  (let [shape (vec (dtype/shape t))
        rank (count shape)
        axis (normalize-axis rank axis)]
    (when-not (= 1 (nth shape axis))
      (throw (ex-info "Only a size-one axis can be removed"
                      {:shape shape :axis axis})))
    (when (= rank 1)
      (throw (ex-info "Use a Clojure scalar for a rank-0 result"
                      {:shape shape})))
    (tensor/reshape t (remove-at shape axis))))

(defn select-last [t selector]
  (let [rank (count (dtype/shape t))]
    (apply tensor/select
           t
           (concat (repeat (dec rank) :all) [selector]))))

(def t
  (tensor/reshape
    (dtype/make-container :jvm-heap :int64 (range 24))
    [2 3 4]))

(tensor/->jvm (select-last t 0))
;; => [[0 4 8]
;;     [12 16 20]]

(assert (= [2 3] (vec (dtype/shape (select-last t 0)))))
(assert (= [1 2 3 4] (vec (dtype/shape (expand-axis t 0)))))
(assert (= [2 1 3 4] (vec (dtype/shape (expand-axis t 1)))))
(assert (= [2 3 4 1] (vec (dtype/shape (expand-axis t -1)))))

;; Squeeze reverses a named expansion.
(let [expanded (expand-axis t 1)
      squeezed (squeeze-axis expanded 1)]
  (assert (= [2 3 4] (vec (dtype/shape squeezed))))
  (assert (= (dtype/->vector t) (dtype/->vector squeezed))))

;; Expand is a view.
(let [source (tensor/reshape
               (dtype/make-container :jvm-heap :int64 (range 6))
               [2 3])
      expanded (expand-axis source 1)]
  (tensor/mset! expanded 0 0 0 42)
  (assert (= 42 (tensor/mget source 0 0))))

(assert (try
          (squeeze-axis t 0)
          false
          (catch clojure.lang.ExceptionInfo _ true)))
```

Size-one axes control later alignment. They are structural placeholders, not extra data.

## Common Uses

- Add a batch axis.
- Add a channel axis.
- Prepare shapes for broadcasting.
- Index the last axis for any input rank.
- Restore an axis after a reduction.

## Recognition Clues

Look for `any rank`, `last axis`, `batch of one`, `new axis`, `expand`, or `squeeze`.

## Memory Hooks

- Ellipsis intent becomes generated `:all` selectors.
- A new axis has size one.
- Reshape inserts or removes the placeholder.
- Name the axis that you squeeze.
- These operations can remain views.

## Key Insight

Size-one axes make alignment explicit. They carry meaning even though they add no values.

