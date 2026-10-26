# 11. Radius Neighborhood

## Mental Model

A radius neighborhood includes every offset that passes a distance rule. The distance rule defines the shape.

## Relationship to Cognitive Verb

```text
Expand -> all cells within a distance
```

## Clojure Functions and Common Idioms

|Metric|Rule|Shape|
|---|---|---|
|Manhattan|`abs(dr) + abs(dc)`|diamond|
|Chebyshev|`max(abs(dr), abs(dc))`|square|
|Euclidean|`dr^2 + dc^2`|disk|

## Common Uses

- Apply area effects.
- Blur a chosen radius.
- Dilate a binary mask.
- Build distance maps.
- Select nearby cells.

## Hidden Interview Problems

- Return only the outer ring.
- Clip the neighborhood at edges.
- Use distance-based weights.
- Expand from many source cells.

## Recognition Clues

Look for `within distance`, `radius`, `range`, `disk`, `diamond`, or `square area`.

## Pattern Summary

Generate candidate offsets in a square. Keep only offsets accepted by the selected metric.

## Shape and Edge Behavior

- Matrix functions expect a finite rectangular matrix.
- Radius values and dimensions must not be negative.
- Matrix functions reject ragged rows with `ExceptionInfo`.
- Centered readers require an in-bounds coordinate.

## Clojure Recipe Book

```clojure
(defn rectangular? [matrix]
  (or (empty? matrix)
      (apply = (map count matrix))))

(defn require-rectangular [matrix]
  (when-not (rectangular? matrix)
    (throw (ex-info "Matrix must be rectangular"
                    {:row-lengths (mapv count matrix)})))
  matrix)

(defn squared [number]
  (* number number))

(defn offset-distance [metric [row-change column-change]]
  (case metric
    :manhattan (+ (abs row-change) (abs column-change))
    :chebyshev (max (abs row-change) (abs column-change))
    :euclidean-squared (+ (squared row-change) (squared column-change))
    (throw (ex-info "Unknown distance metric" {:metric metric}))))

(defn radius-offsets
  ([radius] (radius-offsets radius :chebyshev))
  ([radius metric]
   (when (neg? radius)
     (throw (ex-info "Radius must not be negative" {:radius radius})))
   (let [limit (if (= metric :euclidean-squared)
                 (squared radius)
                 radius)]
     (vec
       (for [row-change (range (- radius) (inc radius))
             column-change (range (- radius) (inc radius))
             :let [offset [row-change column-change]]
             :when (<= (offset-distance metric offset) limit)]
         offset)))))

(defn radius-ring [radius metric]
  (let [outer (set (radius-offsets radius metric))
        inner (if (zero? radius)
                #{}
                (set (radius-offsets (dec radius) metric)))]
    (vec (remove inner outer))))

(defn in-bounds? [rows columns [row column]]
  (and (<= 0 row) (< row rows)
       (<= 0 column) (< column columns)))

(defn radius-neighbors [rows columns [row column] radius metric]
  (when (or (neg? rows) (neg? columns))
    (throw (ex-info "Matrix dimensions must not be negative"
                    {:rows rows :columns columns})))
  (vec
    (for [[row-change column-change :as offset]
          (radius-offsets radius metric)
          :when (not= [0 0] offset)
          :let [neighbor [(+ row row-change)
                          (+ column column-change)]]
          :when (in-bounds? rows columns neighbor)]
      neighbor)))

(defn centered-block [matrix coordinate radius]
  (require-rectangular matrix)
  (let [rows (count matrix)
        columns (if-let [row (first matrix)] (count row) 0)]
    (when-not (in-bounds? rows columns coordinate)
      (throw (ex-info "Coordinate is outside the matrix"
                      {:coordinate coordinate})))
    (mapv (fn [row]
            (mapv (fn [column] (get-in matrix [row column]))
                  (range (max 0 (- (second coordinate) radius))
                         (min columns (inc (+ (second coordinate) radius))))))
          (range (max 0 (- (first coordinate) radius))
                 (min rows (inc (+ (first coordinate) radius)))))))

(defn radius-average [matrix coordinate radius metric]
  (require-rectangular matrix)
  (let [rows (count matrix)
        columns (if-let [row (first matrix)] (count row) 0)
        _ (when-not (in-bounds? rows columns coordinate)
            (throw (ex-info "Coordinate is outside the matrix"
                            {:coordinate coordinate})))
        cells (conj (radius-neighbors rows columns coordinate radius metric)
                    coordinate)
        values (map (fn [position] (get-in matrix position)) cells)]
    (/ (reduce + values) (count values))))

(defn weighted-falloff [matrix coordinate radius]
  (require-rectangular matrix)
  (let [rows (count matrix)
        columns (if-let [row (first matrix)] (count row) 0)]
    (when-not (in-bounds? rows columns coordinate)
      (throw (ex-info "Coordinate is outside the matrix"
                      {:coordinate coordinate})))
    (reduce (fn [total position]
              (let [distance (Math/sqrt
                               (double
                                 (offset-distance
                                   :euclidean-squared
                                   (mapv - position coordinate))))
                    weight (/ 1.0 (+ 1.0 distance))]
                (+ total (* weight (get-in matrix position)))))
            0.0
            (conj (radius-neighbors rows columns coordinate radius
                                    :euclidean-squared)
                  coordinate))))

(defn blast-mask [rows columns center radius metric]
  (when (or (neg? rows) (neg? columns))
    (throw (ex-info "Matrix dimensions must not be negative"
                    {:rows rows :columns columns})))
  (let [affected (set (conj (radius-neighbors rows columns center radius metric)
                            center))]
    (mapv (fn [row]
            (mapv (fn [column]
                    (if (affected [row column]) 1 0))
                  (range columns)))
          (range rows))))

(defn dilate [grid radius metric]
  (require-rectangular grid)
  (let [rows (count grid)
        columns (if-let [row (first grid)] (count row) 0)]
    (mapv (fn [row]
            (mapv (fn [column]
                    (let [coordinate [row column]
                          cells (conj (radius-neighbors rows columns coordinate radius metric)
                                      coordinate)]
                      (if (some #(= 1 (get-in grid %)) cells) 1 0)))
                  (range columns)))
          (range rows))))

(defn within-radius? [from to radius metric]
  (when (neg? radius)
    (throw (ex-info "Radius must not be negative" {:radius radius})))
  (let [offset (mapv - to from)
        limit (if (= metric :euclidean-squared)
                (squared radius)
                radius)]
    (<= (offset-distance metric offset) limit)))

(radius-offsets 1 :manhattan)
;; => [[-1 0] [0 -1] [0 0] [0 1] [1 0]]

;; Executable checks

(assert (= [[-1 0] [0 -1] [0 0] [0 1] [1 0]]
           (radius-offsets 1 :manhattan)))
(assert (within-radius? [0 0] [2 1] 3 :manhattan))
```

These functions clip coordinates at matrix edges. Padding and wraparound are separate boundary policies.

### Memory Hooks

- Manhattan makes a diamond.
- Chebyshev makes a square.
- Squared Euclidean distance avoids a square root.
- A ring is one radius minus the prior radius.

### Key Insight

Radius is not enough. State the distance metric because it defines which cells belong to the neighborhood.

## The Neighborhood Section in One Table

|Pattern|Moves or shape|Typical distance|
|---|---|---|
|Four-neighborhood|orthogonal steps|Manhattan|
|Eight-neighborhood|all adjacent steps|Chebyshev|
|Radius neighborhood|all accepted offsets|selected metric|
