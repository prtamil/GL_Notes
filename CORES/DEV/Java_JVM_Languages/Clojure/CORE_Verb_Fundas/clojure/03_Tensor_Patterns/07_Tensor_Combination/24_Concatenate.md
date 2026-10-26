# 24. Concatenate

## Mental Model

Concatenate joins tensors on an existing axis.

The join-axis sizes add. Every other axis size must match.

```text
[2 3] concatenate [2 4] on axis 1 -> [2 7]
```

Rank does not change.

## Relationship to Cognitive Verb

```text
Join -> choose an existing axis -> append values along that axis
```

## Clojure Functions and Common Idioms

|Need|Use|
|---|---|
|Join one axis|validate shapes, then map output coordinates to inputs|
|Join many tensors|one call over the complete collection|
|Join all values|flatten each input, then concatenate rank-1 values|
|Add a new axis|use stack instead|
|Build incrementally|collect tensors, then concatenate once|

## Shape and Edge Behavior

- At least one input tensor is required.
- All inputs must have the same rank.
- Non-join axes must match exactly.
- Join-axis sizes add.
- Empty join axes are valid.
- The result has independent storage.
- Repeated concatenation in a loop copies earlier results again.

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

(defn concatenate-shape [shapes axis]
  (when (empty? shapes)
    (throw (ex-info "Concatenate requires an input tensor" {})))
  (let [shapes (mapv vec shapes)
        rank (count (first shapes))
        axis (normalize-axis rank axis)]
    (when-not (every? #(= rank (count %)) shapes)
      (throw (ex-info "All tensors must have the same rank"
                      {:shapes shapes})))
    (doseq [current (rest shapes)
            other-axis (remove #{axis} (range rank))]
      (when-not (= (get-in shapes [0 other-axis])
                   (nth current other-axis))
        (throw (ex-info "Non-join axes must match"
                        {:shapes shapes :axis axis}))))
    (assoc (first shapes)
           axis
           (reduce + (map #(nth % axis) shapes)))))

(defn locate-source [axis-index axis-sizes]
  (loop [source 0
         index axis-index
         sizes axis-sizes]
    (let [size (first sizes)]
      (if (< index size)
        [source index]
        (recur (inc source) (- index size) (next sizes))))))

(defn concatenate [tensors axis]
  (let [tensors (vec tensors)]
    (when (empty? tensors)
      (throw (ex-info "Concatenate requires an input tensor" {})))
    (let [shapes (mapv #(vec (dtype/shape %)) tensors)
          rank (count (first shapes))
          axis (normalize-axis rank axis)
          output-shape (concatenate-shape shapes axis)
          axis-sizes (mapv #(nth % axis) shapes)
          datatype (dtype/elemwise-datatype (first tensors))]
      (tensor/clone
        (tensor/compute-tensor
          output-shape
          (fn [& output-coordinate]
            (let [[source local-index]
                  (locate-source (nth output-coordinate axis) axis-sizes)
                  source-coordinate (assoc (vec output-coordinate)
                                           axis
                                           local-index)]
              (apply tensor/mget (nth tensors source) source-coordinate)))
          datatype)))))

(def a
  (tensor/reshape
    (dtype/make-container :jvm-heap :int64 (range 6))
    [2 3]))

(def b
  (tensor/reshape
    (dtype/make-container :jvm-heap :int64 (range 6 12))
    [2 3]))

(tensor/->jvm (concatenate [a b] 0))
;; => [[0 1 2]
;;     [3 4 5]
;;     [6 7 8]
;;     [9 10 11]]

(tensor/->jvm (concatenate [a b] 1))
;; => [[0 1 2 6 7 8]
;;     [3 4 5 9 10 11]]

(assert (= [4 3]
           (vec (dtype/shape (concatenate [a b] 0)))))
(assert (= [2 6]
           (vec (dtype/shape (concatenate [a b] 1)))))
(assert (= [[0 1 2 6 7 8]
            [3 4 5 9 10 11]]
           (tensor/->jvm (concatenate [a b] 1))))

;; The result is independent from every input buffer.
(let [joined (concatenate [a b] 0)]
  (tensor/mset! joined 0 0 90)
  (assert (= 0 (tensor/mget a 0 0))))

(assert (try
          (concatenate [a (tensor/new-tensor [2 4] {:datatype :int64})] 0)
          false
          (catch clojure.lang.ExceptionInfo _ true)))
```

## Common Uses

- Assemble batches.
- Join feature groups.
- Add rows or columns.
- Recombine split tensors.
- Collect chunks after parallel work.

## Recognition Clues

Look for `join`, `append rows`, `combine features`, `same rank`, or `existing axis`.

## Memory Hooks

- Rank stays unchanged.
- Join-axis sizes add.
- Other axis sizes must match.
- Concatenation copies.
- Collect first and concatenate once.

## Key Insight

Concatenate extends one existing dimension. It never creates a new dimension.

