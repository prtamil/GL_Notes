# 25. Stack

## Mental Model

Stack adds a new axis and places one input tensor at each position on that axis.

```text
three tensors of shape [2 4]
stack at axis 0 -> [3 2 4]
stack at axis 2 -> [2 4 3]
```

All input shapes must match exactly.

## Relationship to Cognitive Verb

```text
Collect -> insert a new axis -> place one tensor at each new-axis position
```

## Clojure Functions and Common Idioms

|Need|Use|
|---|---|
|Create a batch|stack at axis zero|
|Create channels|stack at the final axis|
|Predict shape|insert the input count into the shape|
|Undo stack|integer-select each new-axis position|
|Equivalent operation|expand each input, then concatenate|

## Shape and Edge Behavior

- Stack requires at least one input.
- All input shapes must be identical.
- Rank increases by one.
- The new axis size equals the input count.
- Stack copies values into independent storage.
- Unstack returns views.

## Clojure Recipe Book

```clojure
(require '[tech.v3.datatype :as dtype]
         '[tech.v3.tensor :as tensor])

(defn normalize-insertion-axis [rank axis]
  (let [new-rank (inc rank)
        axis (if (neg? axis) (+ new-rank axis) axis)]
    (when-not (< -1 axis new-rank)
      (throw (ex-info "Stack axis is outside the result rank"
                      {:axis axis :rank rank})))
    axis))

(defn insert-at [values index value]
  (vec (concat (subvec (vec values) 0 index)
               [value]
               (subvec (vec values) index))))

(defn remove-at [values index]
  (into (subvec (vec values) 0 index)
        (subvec (vec values) (inc index))))

(defn stack [tensors axis]
  (let [tensors (vec tensors)]
    (when (empty? tensors)
      (throw (ex-info "Stack requires an input tensor" {})))
    (let [input-shape (vec (dtype/shape (first tensors)))
          axis (normalize-insertion-axis (count input-shape) axis)]
      (when-not (every? #(= input-shape (vec (dtype/shape %))) tensors)
        (throw (ex-info "All stacked tensor shapes must match"
                        {:shapes (mapv #(vec (dtype/shape %)) tensors)})))
      (let [output-shape (insert-at input-shape axis (count tensors))
            datatype (dtype/elemwise-datatype (first tensors))]
        (tensor/clone
          (tensor/compute-tensor
            output-shape
            (fn [& output-coordinate]
              (let [source-index (nth output-coordinate axis)
                    source-coordinate (remove-at output-coordinate axis)]
                (apply tensor/mget
                       (nth tensors source-index)
                       source-coordinate)))
            datatype))))))

(defn unstack [t axis]
  (let [rank (count (dtype/shape t))
        axis (let [axis (if (neg? axis) (+ rank axis) axis)]
               (when-not (< -1 axis rank)
                 (throw (ex-info "Axis is outside the tensor rank" {})))
               axis)
        selectors (vec (repeat rank :all))]
    (mapv (fn [index]
            (apply tensor/select t (assoc selectors axis index)))
          (range (nth (dtype/shape t) axis)))))

(def a
  (tensor/reshape
    (dtype/make-container :jvm-heap :int64 (range 6))
    [2 3]))

(def b
  (tensor/reshape
    (dtype/make-container :jvm-heap :int64 (range 6 12))
    [2 3]))

(tensor/->jvm (stack [a b] 0))
;; => [[[0 1 2] [3 4 5]]
;;     [[6 7 8] [9 10 11]]]

(tensor/->jvm (stack [a b] -1))
;; => [[[0 6] [1 7] [2 8]]
;;     [[3 9] [4 10] [5 11]]]

(assert (= [2 2 3] (vec (dtype/shape (stack [a b] 0)))))
(assert (= [2 3 2] (vec (dtype/shape (stack [a b] -1)))))
(assert (= [[0 1 2] [3 4 5]]
           (tensor/->jvm (first (unstack (stack [a b] 0) 0)))))

;; Stack copies; unstack returns views into that new buffer.
(let [batch (stack [a b] 0)
      first-item (first (unstack batch 0))]
  (tensor/mset! batch 0 0 0 71)
  (assert (= 0 (tensor/mget a 0 0)))
  (assert (= 71 (tensor/mget first-item 0 0))))

(assert (try
          (stack [a (tensor/new-tensor [3 2] {:datatype :int64})] 0)
          false
          (catch clojure.lang.ExceptionInfo _ true)))
```

## Common Uses

- Build a batch from samples.
- Build color channels from planes.
- Collect equal-shape loop results.
- Add an ensemble axis.
- Group repeated measurements.

## Recognition Clues

Look for `new axis`, `batch from list`, `same shape`, `channels`, or `collect samples`.

## Memory Hooks

- Stack always adds one axis.
- Every input shape must match.
- New-axis size equals input count.
- Axis placement changes meaning.
- Stack copies and unstack views.

## Key Insight

Stack records which input a value came from by creating a new dimension.

