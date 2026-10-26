# 29. Pooling

## Mental Model

Pooling divides data into local windows and reduces each window to one value.

```text
window -> max, mean, sum, or another reduction -> one output value
```

The window size controls the local area. The step controls how far the next window moves.

## Relationship to Cognitive Verb

```text
Summarize -> extract local windows -> reduce each window -> keep position axes
```

## Clojure Functions and Common Idioms

|Need|Use|
|---|---|
|Non-overlapping pooling|Set each step equal to its window size|
|Overlapping pooling|Use a step smaller than the window|
|Global pooling|Reduce the complete spatial area|
|Maximum signal|Use `max`|
|Average signal|Divide the window sum by its item count|
|Preserve edges|Pad before pooling|

## Shape and Edge Behavior

- This recipe pools a rank-two tensor.
- Window sizes and steps must be positive.
- Partial edge windows are not included.
- A window larger than the input gives a size-zero output axis.
- Empty input gives an empty result when no complete window exists.
- The input must be rectangular.

## Clojure Recipe Book

```clojure
(require '[tech.v3.datatype :as dtype]
         '[tech.v3.tensor :as tensor])

(defn window-count [axis-size window-size step]
  (if (> window-size axis-size)
    0
    (inc (quot (- axis-size window-size) step))))

(defn mean-values [values]
  (/ (double (reduce + values)) (count values)))

(defn max-values [values]
  (reduce max values))

(defn pool-2d
  ([matrix window-shape reducer]
   (pool-2d matrix window-shape window-shape reducer))
  ([matrix window-shape steps reducer]
   (let [shape (vec (dtype/shape matrix))
         [window-rows window-cols] (vec window-shape)
         [row-step col-step] (vec steps)]
     (when-not (= 2 (count shape))
       (throw (ex-info "Pooling requires a rank-two tensor"
                       {:shape shape})))
     (when (some #(not (pos? %))
                 [window-rows window-cols row-step col-step])
       (throw (ex-info "Window sizes and steps must be positive"
                       {:window-shape window-shape :steps steps})))
     (let [[rows cols] shape
           output-shape [(window-count rows window-rows row-step)
                         (window-count cols window-cols col-step)]]
       (tensor/clone
         (tensor/compute-tensor
           output-shape
           (fn [output-row output-col]
             (let [start-row (* output-row row-step)
                   start-col (* output-col col-step)
                   values
                   (for [row (range start-row (+ start-row window-rows))
                         col (range start-col (+ start-col window-cols))]
                     (tensor/mget matrix row col))]
               (reducer values)))
           :float64))))))

(def matrix
  (tensor/->tensor [[0  1  2  3]
                    [4  5  6  7]
                    [8  9 10 11]
                    [12 13 14 15]]
                   {:datatype :int64}))

(assert (= [[5.0 7.0]
            [13.0 15.0]]
           (tensor/->jvm (pool-2d matrix [2 2] max-values))))

(assert (= [[2.5 4.5]
            [10.5 12.5]]
           (tensor/->jvm (pool-2d matrix [2 2] mean-values))))

;; A smaller step creates overlapping windows.
(assert (= [[5.0 6.0 7.0]
            [9.0 10.0 11.0]
            [13.0 14.0 15.0]]
           (tensor/->jvm (pool-2d matrix [2 2] [1 1] max-values))))

;; Window height and width are independent.
(assert (= [[8.0 9.0 10.0]
            [13.0 14.0 15.0]
            [18.0 19.0 20.0]]
           (tensor/->jvm
             (pool-2d
               (tensor/->tensor [[1  2  3  4  5]
                                  [6  7  8  9 10]
                                  [11 12 13 14 15]
                                  [16 17 18 19 20]]
                                 {:datatype :int64})
               [2 3]
               [1 1]
               max-values))))

;; Global average pooling returns one spatial value.
(assert (= [[7.5]]
           (tensor/->jvm (pool-2d matrix [4 4] mean-values))))

(assert (= [0 0]
           (vec (dtype/shape (pool-2d matrix [5 5] max-values)))))
```

## Common Uses

- Reduce image resolution.
- Keep the strongest local feature.
- Compute local averages.
- Summarize a complete spatial plane.
- Build fixed-size features from variable spatial data.

## Recognition Clues

Look for `downsample`, `local maximum`, `local average`, `pool`, or `block summary`.

## Memory Hooks

- Extract a window.
- Reduce its values.
- Keep its position.
- Step equal to window means no overlap.
- Step one means maximum overlap.

## Key Insight

Pooling is window extraction followed by reduction. Only the position axes remain in the result.

