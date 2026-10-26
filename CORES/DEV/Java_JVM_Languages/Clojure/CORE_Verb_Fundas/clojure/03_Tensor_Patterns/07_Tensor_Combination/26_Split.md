# 26. Split

## Mental Model

Split cuts one axis into several ranges. Each piece keeps the input rank.

Split is slicing, so each piece is a view.

## Relationship to Cognitive Verb

```text
Partition -> choose one axis and cut points -> return slice views
```

## Clojure Functions and Common Idioms

|Need|Use|
|---|---|
|Explicit cuts|build ranges between cut points|
|Equal pieces|require exact division|
|Balanced pieces|distribute the remainder to early pieces|
|Fixed-size batches|step through the axis by batch size|
|Recombine|concatenate on the same axis|

## Shape and Edge Behavior

- Each piece keeps the input rank.
- Explicit cuts occur before the named index.
- Equal split requires exact divisibility.
- Balanced piece sizes differ by at most one.
- Fixed-size batching can produce a short final piece.
- Split pieces share storage with the source.
- Zero-size pieces are valid views.

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

(defn split-at-points [t axis cut-points]
  (let [shape (vec (dtype/shape t))
        rank (count shape)
        axis (normalize-axis rank axis)
        axis-size (nth shape axis)
        cuts (mapv #(-> % (max 0) (min axis-size)) cut-points)]
    (when-not (apply <= cuts)
      (throw (ex-info "Cut points must not decrease"
                      {:cut-points cuts})))
    (let [bounds (concat [0] cuts [axis-size])
          selectors (vec (repeat rank :all))]
      (mapv (fn [[start end]]
              (apply tensor/select
                     t
                     (assoc selectors axis (range start end))))
            (partition 2 1 bounds)))))

(defn split-equal [t part-count axis]
  (when-not (pos? part-count)
    (throw (ex-info "Part count must be positive" {})))
  (let [axis (normalize-axis (count (dtype/shape t)) axis)
        axis-size (nth (dtype/shape t) axis)]
    (when-not (zero? (mod axis-size part-count))
      (throw (ex-info "Axis size must divide by the part count"
                      {:axis-size axis-size :part-count part-count})))
    (let [part-size (quot axis-size part-count)]
      (split-at-points t axis (range part-size axis-size part-size)))))

(defn split-balanced [t part-count axis]
  (when-not (pos? part-count)
    (throw (ex-info "Part count must be positive" {})))
  (let [axis (normalize-axis (count (dtype/shape t)) axis)
        axis-size (nth (dtype/shape t) axis)
        base-size (quot axis-size part-count)
        extra-count (mod axis-size part-count)
        sizes (mapv (fn [part]
                      (+ base-size (if (< part extra-count) 1 0)))
                    (range part-count))
        cuts (butlast (reductions + sizes))]
    (split-at-points t axis cuts)))

(defn fixed-size-batches [t batch-size axis]
  (when-not (pos? batch-size)
    (throw (ex-info "Batch size must be positive" {})))
  (let [axis (normalize-axis (count (dtype/shape t)) axis)
        axis-size (nth (dtype/shape t) axis)]
    (split-at-points t axis (range batch-size axis-size batch-size))))

(def matrix
  (tensor/reshape
    (dtype/make-container :jvm-heap :int64 (range 12))
    [4 3]))

(assert (= [[2 3] [2 3]]
           (mapv #(vec (dtype/shape %))
                 (split-equal matrix 2 0))))
(assert (= [[[0 1 2] [3 4 5]]
            [[6 7 8] [9 10 11]]]
           (mapv tensor/->jvm (split-equal matrix 2 0))))

;; Balanced pieces receive extras from the front.
(let [values (tensor/->tensor (range 10) {:datatype :int64})]
  (assert (= [4 3 3]
             (mapv #(first (dtype/shape %))
                   (split-balanced values 3 0)))))

;; Fixed-size batches keep a short final batch.
(let [values (tensor/->tensor (range 10) {:datatype :int64})]
  (assert (= [3 3 3 1]
             (mapv #(first (dtype/shape %))
                   (fixed-size-batches values 3 0)))))

;; Split results are views.
(let [source (tensor/reshape
               (dtype/make-container :jvm-heap :int64 (range 12))
               [4 3])
      first-part (first (split-equal source 2 0))]
  (tensor/mset! first-part 0 0 72)
  (assert (= 72 (tensor/mget source 0 0))))

(assert (try
          (split-equal matrix 3 0)
          false
          (catch clojure.lang.ExceptionInfo _ true)))
```

## Common Uses

- Create training and validation partitions.
- Form mini-batches.
- Split packed query, key, and value features.
- Separate channel groups.
- Divide work into balanced chunks.

## Recognition Clues

Look for `chunks`, `parts`, `cut points`, `mini-batch`, `divide evenly`, or `balanced split`.

## Memory Hooks

- Split keeps rank.
- Equal split is strict.
- Balanced split distributes the remainder early.
- Fixed batches can end short.
- Pieces are views.

## Key Insight

Split is a list of slices. Its policy decides only where the slice boundaries occur.

