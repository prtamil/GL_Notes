# 37. Meshgrid

## Mental Model

A meshgrid expands one coordinate vector per axis across a common grid.

```text
x shape [3], y shape [2]
-> x-grid [3 2], y-grid [3 2]
```

Each output stores one coordinate component at every grid position.

## Relationship to Cognitive Verb

```text
Coordinate -> provide one vector per axis -> expand each vector across the grid
```

## Clojure Functions and Common Idioms

|Need|Use|
|---|---|
|Matrix-index order|Place the first vector on axis zero|
|Dense coordinate tensors|Compute one full tensor per coordinate axis|
|Sparse coordinate views|Reshape each vector with size-one axes|
|Integer coordinate indices|Use `range` for each dimension|
|Evaluate a field|Combine the coordinate tensors element by element|

## Shape and Edge Behavior

- Each input coordinate tensor must have rank one.
- Dense outputs all have the combined axis-length shape.
- Sparse outputs have one non-unit axis each.
- A size-zero coordinate axis makes every dense grid empty.
- One input produces one rank-one grid.
- This lesson uses matrix-index order, also called `ij` order.

## Clojure Recipe Book

```clojure
(require '[tech.v3.datatype :as dtype]
         '[tech.v3.tensor :as tensor])

(defn validate-coordinate-axes [axes]
  (doseq [axis axes]
    (when-not (= 1 (count (dtype/shape axis)))
      (throw (ex-info "Each coordinate axis must have rank one"
                      {:shape (vec (dtype/shape axis))}))))
  axes)

(defn meshgrid-ij [& axes]
  (let [axes (vec (validate-coordinate-axes axes))
        shape (mapv #(first (dtype/shape %)) axes)]
    (mapv
      (fn [axis-index axis-values]
        (tensor/compute-tensor
          shape
          (fn [& coordinate]
            (tensor/mget axis-values (nth coordinate axis-index)))
          (dtype/elemwise-datatype axis-values)))
      (range (count axes))
      axes)))

(defn open-grid [& axes]
  (let [axes (vec (validate-coordinate-axes axes))
        rank (count axes)]
    (mapv
      (fn [axis-index axis-values]
        (let [shape (assoc (vec (repeat rank 1))
                           axis-index
                           (first (dtype/shape axis-values)))]
          (tensor/reshape axis-values shape)))
      (range rank)
      axes)))

(defn coordinate-indices [shape]
  (apply meshgrid-ij
         (map (fn [size]
                (tensor/reshape
                  (dtype/make-container :jvm-heap :int64 (range size))
                  [size]))
              shape)))

(def x (tensor/->tensor [10 20 30] {:datatype :int64}))
(def y (tensor/->tensor [1 2] {:datatype :int64}))
(def grids (meshgrid-ij x y))

(assert (= [[10 10]
            [20 20]
            [30 30]]
           (tensor/->jvm (nth grids 0))))
(assert (= [[1 2]
            [1 2]
            [1 2]]
           (tensor/->jvm (nth grids 1))))

(assert (= [[3 1] [1 2]]
           (mapv #(vec (dtype/shape %)) (open-grid x y))))

(let [[rows cols] (coordinate-indices [2 3])]
  (assert (= [[0 0 0] [1 1 1]] (tensor/->jvm rows)))
  (assert (= [[0 1 2] [0 1 2]] (tensor/->jvm cols))))

;; A scalar field can read both coordinate grids.
(let [[x-grid y-grid]
      (meshgrid-ij
        (tensor/->tensor [-1.0 0.0 1.0] {:datatype :float64})
        (tensor/->tensor [-2.0 0.0 2.0] {:datatype :float64}))
      radius-squared
      (tensor/compute-tensor
        [3 3]
        (fn [row col]
          (+ (Math/pow (tensor/mget x-grid row col) 2)
             (Math/pow (tensor/mget y-grid row col) 2)))
        :float64)]
  (assert (= 0.0 (tensor/mget radius-squared 1 1)))
  (assert (= 5.0 (tensor/mget radius-squared 0 0))))

(assert (= [[2 3 4] [2 3 4] [2 3 4]]
           (mapv #(vec (dtype/shape %))
                 (coordinate-indices [2 3 4]))))
```

The common NumPy `xy` default swaps the first two axes. This helper uses explicit `ij` order to match tensor indexing.

## Common Uses

- Build image coordinates.
- Evaluate functions over a grid.
- Compute distance fields.
- Create positional encodings.
- Generate integer index tensors.

## Recognition Clues

Look for `coordinate grid`, `x and y values`, `field`, `lattice`, `indices`, or `sample every combination`.

## Memory Hooks

- Start with one vector per axis.
- The result shape contains every vector length.
- Each grid changes along one axis.
- Sparse grids use size-one axes.
- Use `ij` order for direct tensor indexing.

## Key Insight

A meshgrid converts independent coordinate axes into aligned coordinate tensors. It makes multidimensional formulas direct and explicit.

