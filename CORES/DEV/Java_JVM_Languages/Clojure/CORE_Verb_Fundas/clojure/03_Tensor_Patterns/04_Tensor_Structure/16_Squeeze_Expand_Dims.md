# 16. Squeeze and Expand Dimensions

## Mental Model

Expand inserts a size-one axis. Squeeze removes a named size-one axis.

These operations preserve values and logical order. They prepare shapes for later alignment.

## Relationship to Cognitive Verb

```text
Align -> insert or remove a size-one slot -> preserve the value sequence
```

## Clojure Functions and Common Idioms

|Need|Use|
|---|---|
|Add one axis|insert `1` into the shape and reshape|
|Drop one axis|validate size one, remove it, and reshape|
|Keep a reduced axis|reduce, then insert `1` at that position|
|Keep an indexed axis|select a one-index range|
|Normalize and broadcast|keep the reduced dimension|

## Shape and Edge Behavior

- Expand increases rank by one.
- Squeeze decreases rank by one.
- Squeeze accepts only an axis of size one.
- Named squeeze protects other meaningful size-one axes.
- A bare squeeze can remove batch or channel axes by accident.
- Expand and squeeze return views.

## Clojure Recipe Book

```clojure
(require '[tech.v3.datatype :as dtype]
         '[tech.v3.datatype.functional :as dfn]
         '[tech.v3.tensor :as tensor])

(defn normalize-axis [rank axis]
  (let [axis (if (neg? axis) (+ rank axis) axis)]
    (when-not (< -1 axis rank)
      (throw (ex-info "Axis is outside the tensor rank"
                      {:axis axis :rank rank})))
    axis))

(defn normalize-insertion-axis [rank axis]
  (let [new-rank (inc rank)
        axis (if (neg? axis) (+ new-rank axis) axis)]
    (when-not (< -1 axis new-rank)
      (throw (ex-info "Insertion axis is outside the new rank"
                      {:axis axis :rank rank})))
    axis))

(defn insert-at [values index value]
  (vec (concat (subvec (vec values) 0 index)
               [value]
               (subvec (vec values) index))))

(defn remove-at [values index]
  (into (subvec (vec values) 0 index)
        (subvec (vec values) (inc index))))

(defn expand-dims [t axis]
  (let [shape (vec (dtype/shape t))
        axis (normalize-insertion-axis (count shape) axis)]
    (tensor/reshape t (insert-at shape axis 1))))

(defn squeeze [t axis]
  (let [shape (vec (dtype/shape t))
        axis (normalize-axis (count shape) axis)]
    (when-not (= 1 (nth shape axis))
      (throw (ex-info "Squeeze requires a size-one axis"
                      {:shape shape :axis axis})))
    (when (= 1 (count shape))
      (throw (ex-info "Use a Clojure scalar for a rank-0 result" {})))
    (tensor/reshape t (remove-at shape axis))))

(defn reduce-keep-dims [t reduce-fn axis]
  (let [shape (vec (dtype/shape t))
        axis (normalize-axis (count shape) axis)
        reduced (tensor/reduce-axis t reduce-fn axis)]
    (tensor/reshape reduced (insert-at (dtype/shape reduced) axis 1))))

(def t
  (tensor/reshape
    (dtype/make-container :jvm-heap :int64 (range 24))
    [2 3 4]))

(assert (= [1 2 3 4] (vec (dtype/shape (expand-dims t 0)))))
(assert (= [2 3 1 4] (vec (dtype/shape (expand-dims t 2)))))
(assert (= [2 3 4 1] (vec (dtype/shape (expand-dims t -1)))))

(let [expanded (expand-dims t 2)
      restored (squeeze expanded 2)]
  (assert (= [2 3 4] (vec (dtype/shape restored))))
  (assert (= (dtype/->vector t) (dtype/->vector restored))))

;; Keep the reduced axis for later broadcasting.
(let [matrix (tensor/reshape
               (dtype/make-container :jvm-heap :float64 (range 1 13))
               [3 4])
      row-sums (reduce-keep-dims matrix dfn/sum 1)
      aligned-sums (tensor/broadcast row-sums [3 4])
      normalized (dfn// matrix aligned-sums)
      checks (tensor/reduce-axis normalized dfn/sum 1)]
  (assert (= [3 1] (vec (dtype/shape row-sums))))
  (assert (= [3 4] (vec (dtype/shape normalized))))
  (assert (every? #(< (Math/abs (- 1.0 (double %))) 1.0e-12)
                  (dtype/->reader checks))))

;; Named squeeze rejects a wrong assumption.
(assert (try
          (squeeze t 0)
          false
          (catch clojure.lang.ExceptionInfo _ true)))

;; A size-one view shares source storage.
(let [source (tensor/reshape
               (dtype/make-container :jvm-heap :int64 (range 6))
               [2 3])
      expanded (expand-dims source 0)]
  (tensor/mset! expanded 0 0 0 69)
  (assert (= 69 (tensor/mget source 0 0))))
```

## Common Uses

- Keep a batch dimension of one.
- Add a channel dimension.
- Align tensors for broadcasting.
- Retain a reduction axis.
- Validate that a dimension is a singleton.

## Recognition Clues

Look for `singleton`, `batch of one`, `keep dimensions`, `expand`, `squeeze`, or `broadcast back`.

## Memory Hooks

- Expand inserts size one.
- Squeeze removes only size one.
- Name the squeezed axis.
- Keep reduced axes before broadcasting back.
- Value count and order do not change.

## Key Insight

Size-one axes are alignment slots. Preserve them when the next operation must match the original tensor.

