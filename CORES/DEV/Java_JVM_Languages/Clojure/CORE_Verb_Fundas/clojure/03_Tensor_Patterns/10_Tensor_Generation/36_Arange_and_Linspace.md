# 36. Arange and Linspace

## Mental Model

An arithmetic range specifies a step. A linear space specifies a point count.

```text
arange:   start, stop, step
linspace: start, stop, count
```

Use an arithmetic range for integer indices. Use a linear space for sampled numeric intervals.

## Relationship to Cognitive Verb

```text
Generate -> choose step or count -> create one ordered numeric axis
```

## Clojure Functions and Common Idioms

|Need|Use|
|---|---|
|Integer indices|Clojure `range` in a typed tensor|
|Known step|Arithmetic range|
|Known sample count|Linear space|
|Include the stop|Linear space with endpoint enabled|
|Exclude the stop|Arithmetic range or endpoint-disabled linear space|
|Build test data|Generate a range, then reshape it|

## Shape and Edge Behavior

- An arithmetic range excludes its stop value.
- Its step must not be zero.
- A positive step can produce an empty descending request.
- A negative step can produce an empty ascending request.
- Linear-space count must not be negative.
- Count zero produces an empty tensor.
- Count one produces only the start value.
- Use tolerance when you compare computed floating-point values.

## Clojure Recipe Book

```clojure
(require '[tech.v3.datatype :as dtype]
         '[tech.v3.tensor :as tensor])

(defn vector-tensor [datatype values]
  (let [values (vec values)]
    (tensor/reshape
      (dtype/make-container :jvm-heap datatype values)
      [(count values)])))

(defn arange
  ([stop]
   (arange 0 stop 1))
  ([start stop]
   (arange start stop 1))
  ([start stop step]
   (when-not (every? integer? [start stop step])
     (throw (ex-info "This arange helper accepts integers only"
                     {:start start :stop stop :step step})))
   (when (zero? step)
     (throw (ex-info "Range step must not be zero" {:step step})))
   (vector-tensor :int64 (range start stop step))))

(defn linspace
  ([start stop count]
   (linspace start stop count true))
  ([start stop count endpoint?]
   (when (neg? count)
     (throw (ex-info "Point count must not be negative"
                     {:count count})))
   (let [values
         (cond
           (zero? count) []
           (= count 1) [(double start)]
           :else
           (let [divisor (if endpoint? (dec count) count)
                 step (/ (- (double stop) (double start)) divisor)]
             (mapv (fn [index]
                     (if (and endpoint? (= index (dec count)))
                       (double stop)
                       (+ (double start) (* index step))))
                   (range count))))]
     (vector-tensor :float64 values))))

(defn close-vector? [expected actual]
  (every? (fn [[left right]]
            (< (Math/abs (- (double left) (double right))) 1.0e-12))
          (map vector expected actual)))

(assert (= [0 1 2 3 4] (dtype/->vector (arange 5))))
(assert (= [2 5 8] (dtype/->vector (arange 2 10 3))))
(assert (= [5 3 1] (dtype/->vector (arange 5 0 -2))))
(assert (= [] (dtype/->vector (arange 5 0 1))))

(assert (close-vector? [0.0 0.25 0.5 0.75 1.0]
                       (dtype/->vector (linspace 0 1 5))))
(assert (close-vector? [0.0 0.25 0.5 0.75]
                       (dtype/->vector (linspace 0 1 4 false))))
(assert (= [3.0] (dtype/->vector (linspace 3 9 1))))
(assert (= [0] (vec (dtype/shape (linspace 0 1 0)))))

;; Generate flat test values, then give them tensor structure.
(assert (= [[0 1 2]
            [3 4 5]]
           (tensor/->jvm (tensor/reshape (arange 6) [2 3]))))

(assert (try
          (arange 0 10 0)
          false
          (catch clojure.lang.ExceptionInfo _ true)))
```

Do not use repeated floating-point addition when the final point count matters. Rounding can change the apparent stop behavior.

## Common Uses

- Generate indices.
- Create time axes.
- Sample a mathematical interval.
- Build predictable test tensors.
- Create reshape examples.

## Recognition Clues

Look for `sequence`, `sample count`, `fixed step`, `time axis`, `indices`, or `even spacing`.

## Memory Hooks

- Arange chooses the step.
- Linspace chooses the count.
- Arange excludes the stop.
- Linspace can include the stop.
- Use linspace for stable floating-point sample counts.

## Key Insight

Step and count solve different problems. Choose the form that states the required invariant directly.

