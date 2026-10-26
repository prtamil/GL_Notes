# 28. Patch Extraction

## Mental Model

A sliding window exposes each local patch as another tensor dimension.

```text
[0 1 2 3 4] with width 3
-> [[0 1 2]
    [1 2 3]
    [2 3 4]]
```

The leading axes select a window position. The trailing axes select a position inside that window.

## Relationship to Cognitive Verb

```text
Extract -> move a fixed shape across selected axes -> expose all local patches
```

## Clojure Functions and Common Idioms

`dtype-next` has no direct equivalent of NumPy `sliding_window_view`. A computed tensor can provide the same lazy read behavior.

|Need|Use|
|---|---|
|All windows|Compute position axes and append window axes|
|Window selected axes|Keep other source axes unchanged|
|Stride|Advance each position by a step|
|Independent patches|Clone or reshape into new storage|
|Immediate reduction|Read the computed tensor without cloning it|

## Shape and Edge Behavior

- Each window size must be positive.
- Each step must be positive.
- Selected axes must be distinct.
- A window larger than its source axis gives a size-zero position axis.
- Empty input is valid when the result has no window positions.
- A tensor is rectangular. Ragged input must be validated before tensor creation.
- The helper returns a lazy read view. Source changes remain visible.

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

(defn sliding-window
  ([t window-shape]
   (sliding-window t window-shape
                   (range (count (dtype/shape t)))
                   (repeat (count window-shape) 1)))
  ([t window-shape axes steps]
   (let [shape (vec (dtype/shape t))
         rank (count shape)
         window-shape (vec window-shape)
         axes (mapv #(normalize-axis rank %) axes)
         steps (vec steps)]
     (when-not (= (count window-shape) (count axes) (count steps))
       (throw (ex-info "Window sizes, axes, and steps must have equal counts"
                       {:window-shape window-shape :axes axes :steps steps})))
     (when-not (= (count axes) (count (distinct axes)))
       (throw (ex-info "Window axes must be distinct" {:axes axes})))
     (when (some #(not (pos? %)) window-shape)
       (throw (ex-info "Window sizes must be positive"
                       {:window-shape window-shape})))
     (when (some #(not (pos? %)) steps)
       (throw (ex-info "Window steps must be positive" {:steps steps})))
     (let [axis-options (zipmap axes (map vector window-shape steps))
           position-shape
           (mapv (fn [axis axis-size]
                   (if-let [[window-size step] (get axis-options axis)]
                     (if (> window-size axis-size)
                       0
                       (inc (quot (- axis-size window-size) step)))
                     axis-size))
                 (range rank)
                 shape)
           output-shape (into position-shape window-shape)]
       (tensor/compute-tensor
         output-shape
         (fn [& output-coordinate]
           (let [position (subvec (vec output-coordinate) 0 rank)
                 offsets (subvec (vec output-coordinate) rank)
                 source-coordinate
                 (reduce-kv
                   (fn [coordinate window-axis source-axis]
                     (assoc coordinate
                            source-axis
                            (+ (* (nth position source-axis)
                                  (nth steps window-axis))
                               (nth offsets window-axis))))
                   position
                   axes)]
             (apply tensor/mget t source-coordinate)))
         (dtype/elemwise-datatype t))))))

(def values
  (tensor/->tensor [0 1 2 3 4 5 6 7] {:datatype :int64}))

(def windows (sliding-window values [3]))

(assert (= [6 3] (vec (dtype/shape windows))))
(assert (= [[0 1 2]
            [1 2 3]
            [2 3 4]
            [3 4 5]
            [4 5 6]
            [5 6 7]]
           (tensor/->jvm windows)))

;; Step two changes only the position axis.
(assert (= [[0 1 2]
            [2 3 4]
            [4 5 6]]
           (tensor/->jvm
             (sliding-window values [3] [0] [2]))))

(def matrix
  (tensor/->tensor [[0  1  2  3  4]
                    [5  6  7  8  9]
                    [10 11 12 13 14]
                    [15 16 17 18 19]]
                   {:datatype :int64}))

(def patches (sliding-window matrix [2 2]))

(assert (= [3 4 2 2] (vec (dtype/shape patches))))
(assert (= [[7 8] [12 13]]
           (tensor/->jvm (tensor/select patches 1 2 :all :all))))

;; Window only the row axis. The column axis stays in place.
(let [vertical (sliding-window matrix [3] [0] [1])]
  (assert (= [2 5 3] (vec (dtype/shape vertical))))
  (assert (= [2 7 12]
             (tensor/->jvm (tensor/select vertical 0 2 :all)))))

;; The computed tensor reads from the source when a value is requested.
(tensor/mset! values 2 99)
(assert (= 99 (tensor/mget windows 0 2)))
```

## Common Uses

- Extract image patches.
- Build moving statistics.
- Prepare convolution inputs.
- Find local patterns.
- Convert patches into rows for matrix multiplication.

## Recognition Clues

Look for `sliding`, `local patch`, `moving`, `kernel`, `window`, or `neighborhood`.

## Memory Hooks

- Leading axes locate each patch.
- Trailing axes describe each patch.
- Step changes the position axes.
- A lazy computed tensor avoids patch copies.
- Clone only when independent storage is required.

## Key Insight

Patch extraction changes how coordinates are read. The window values do not need separate storage.

