# 27. Tile and Repeat

## Mental Model

Tile repeats a complete pattern. Repeat duplicates each item in place.

```text
input    [1 2 3]
tile 2   [1 2 3 1 2 3]
repeat 2 [1 1 2 2 3 3]
```

Both operations allocate repeated values. Broadcasting is the read-only view alternative when its alignment rule applies.

## Relationship to Cognitive Verb

```text
Replicate -> choose whole-pattern or per-item repetition -> build a larger tensor
```

## Clojure Functions and Common Idioms

|Need|Use|
|---|---|
|Repeat whole blocks|tile with one repetition count per axis|
|Repeat each item|repeat along a named axis|
|Variable item counts|one count per source position|
|Nearest-neighbor upsample|repeat spatial axes|
|Mosaic|tile spatial axes|
|Avoid allocation|broadcast when the pattern uses size-one axes|

## Shape and Edge Behavior

- Tile counts must not be negative.
- Short tile-count vectors receive leading ones.
- Long tile-count vectors add leading axes.
- Repeat keeps rank when an axis is named.
- Variable repeat counts must match the selected axis size.
- Count zero removes that source position.
- Both helpers return independent storage.

## Clojure Recipe Book

```clojure
(require '[tech.v3.datatype :as dtype]
         '[tech.v3.tensor :as tensor])

(defn pad-left [values size fill]
  (vec (concat (repeat (- size (count values)) fill) values)))

(defn normalize-axis [rank axis]
  (let [axis (if (neg? axis) (+ rank axis) axis)]
    (when-not (< -1 axis rank)
      (throw (ex-info "Axis is outside the tensor rank"
                      {:axis axis :rank rank})))
    axis))

(defn tile [t repetitions]
  (let [source-shape (vec (dtype/shape t))
        repetitions (vec repetitions)
        rank (max (count source-shape) (count repetitions))
        padded-shape (pad-left source-shape rank 1)
        padded-repetitions (pad-left repetitions rank 1)]
    (when (some neg? padded-repetitions)
      (throw (ex-info "Tile counts must not be negative"
                      {:repetitions repetitions})))
    (let [source (tensor/reshape t padded-shape)
          output-shape (mapv * padded-shape padded-repetitions)]
      (tensor/clone
        (tensor/compute-tensor
          output-shape
          (fn [& output-coordinate]
            (let [source-coordinate
                  (mapv (fn [index axis-size]
                          (mod index axis-size))
                        output-coordinate
                        padded-shape)]
              (apply tensor/mget source source-coordinate)))
          (dtype/elemwise-datatype t))))))

(defn repeat-axis [t counts axis]
  (let [shape (vec (dtype/shape t))
        axis (normalize-axis (count shape) axis)
        axis-size (nth shape axis)
        counts (if (number? counts)
                 (vec (repeat axis-size counts))
                 (vec counts))]
    (when-not (= axis-size (count counts))
      (throw (ex-info "Repeat counts must match the axis size"
                      {:axis-size axis-size :counts counts})))
    (when (some neg? counts)
      (throw (ex-info "Repeat counts must not be negative"
                      {:counts counts})))
    (let [source-indices
          (vec (mapcat (fn [index count]
                         (repeat count index))
                       (range axis-size)
                       counts))
          output-shape (assoc shape axis (count source-indices))]
      (tensor/clone
        (tensor/compute-tensor
          output-shape
          (fn [& output-coordinate]
            (let [source-coordinate
                  (assoc (vec output-coordinate)
                         axis
                         (nth source-indices
                              (nth output-coordinate axis)))]
              (apply tensor/mget t source-coordinate)))
          (dtype/elemwise-datatype t))))))

(def values (tensor/->tensor [1 2 3] {:datatype :int64}))

(assert (= [1 2 3 1 2 3]
           (dtype/->vector (tile values [2]))))
(assert (= [1 1 2 2 3 3]
           (dtype/->vector (repeat-axis values 2 0))))
(assert (= [1 2 2 3 3 3]
           (dtype/->vector (repeat-axis values [1 2 3] 0))))

(def image
  (tensor/->tensor [[1 2]
                    [3 4]]
                   {:datatype :int64}))

;; Repeat creates nearest-neighbor upsampling.
(let [upsampled (-> image
                    (repeat-axis 2 0)
                    (repeat-axis 2 1))]
  (assert (= [[1 1 2 2]
              [1 1 2 2]
              [3 3 4 4]
              [3 3 4 4]]
             (tensor/->jvm upsampled))))

;; Tile creates a mosaic with the same output shape.
(let [mosaic (tile image [2 2])]
  (assert (= [[1 2 1 2]
              [3 4 3 4]
              [1 2 1 2]
              [3 4 3 4]]
             (tensor/->jvm mosaic))))

;; Longer repetition vectors add leading axes.
(assert (= [2 2 2]
           (vec (dtype/shape (tile image [2 1 1])))))
```

## Common Uses

- Upsample categorical images.
- Build repeated test fixtures.
- Create mosaics.
- Oversample selected groups.
- Expand variable-length groups.

## Recognition Clues

Look for `duplicate each`, `repeat pattern`, `mosaic`, `upsample`, `oversample`, or `tile`.

## Memory Hooks

- Tile repeats the full pattern.
- Repeat duplicates each position.
- Order distinguishes the operations.
- Broadcasting can avoid a read-only copy.
- Explicit repeated tensors allocate storage.

## Key Insight

Tile repeats blocks. Repeat stretches positions. Equal output shapes can still contain different value orders.

