# 28. Identity Matrix

## Mental Model

Generate one at coordinates where `row = column`. Generate zero at all other coordinates.

## Relationship to Cognitive Verb

```text
Generate -> apply a coordinate rule to every cell
```

## Clojure Functions and Common Idioms

|Need|Use|
|---|---|
|Identity matrix|an equality predicate|
|Diagonal matrix|index matching|
|Permutation matrix|one selected column per row|
|Matrix power|binary exponentiation with identity|
|Check identity|test diagonal and non-diagonal cells|

## Common Uses

- Start matrix multiplication.
- Represent a no-change transform.
- Build diagonal and permutation matrices.
- Calculate matrix powers.

## Hidden Interview Problems

- Explain why identity is the multiplication unit.
- Reorder rows with a permutation matrix.
- Flip axes with an exchange matrix.
- Use binary exponentiation for Fibonacci numbers.

## Recognition Clues

Look for `ones on the diagonal`, `multiplicative identity`, `no-change matrix`, or `I`.

## Pattern Summary

Identity is a coordinate predicate. It is also the starting value for repeated matrix multiplication.

## Shape and Edge Behavior

- Generation uses finite nonnegative sizes.
- Size zero produces the empty identity matrix.
- Matrix multiplication requires rectangular inputs with aligned dimensions.
- Matrix power requires a square matrix and a nonnegative exponent.

## Clojure Recipe Book

```clojure
(defn rectangular? [matrix]
  (or (empty? matrix)
      (apply = (map count matrix))))

(defn require-rectangular [matrix label]
  (when-not (rectangular? matrix)
    (throw (ex-info (str label " must be rectangular")
                    {:row-lengths (mapv count matrix)})))
  matrix)

(defn identity-matrix [size]
  (when (neg? size)
    (throw (ex-info "Size must not be negative" {:size size})))
  (mapv (fn [row]
          (mapv (fn [column]
                  (if (= row column) 1 0))
                (range size)))
        (range size)))

(defn diagonal-matrix [values]
  (let [size (count values)]
    (mapv (fn [row]
            (mapv (fn [column]
                    (if (= row column) (nth values row) 0))
                  (range size)))
          (range size))))

(defn transpose [matrix]
  (require-rectangular matrix "Matrix")
  (if (empty? matrix) [] (apply mapv vector matrix)))

(defn matrix-multiply [left right]
  (require-rectangular left "Left matrix")
  (require-rectangular right "Right matrix")
  (let [left-columns (if-let [row (first left)] (count row) 0)
        right-rows (count right)]
    (when-not (= left-columns right-rows)
      (throw (ex-info "Matrix dimensions do not align"
                      {:left-columns left-columns
                       :right-rows right-rows})))
    (let [right-columns (transpose right)]
      (mapv (fn [left-row]
              (mapv (fn [right-column]
                      (reduce + 0 (map * left-row right-column)))
                    right-columns))
            left))))

(defn permutation-matrix [permutation]
  (let [size (count permutation)]
    (when-not (= (set permutation) (set (range size)))
      (throw (ex-info "Values must form a permutation" {})))
    (mapv (fn [row]
            (mapv (fn [column]
                    (if (= column (nth permutation row)) 1 0))
                  (range size)))
          (range size))))

(defn exchange-matrix [size]
  (vec (reverse (identity-matrix size))))

(defn matrix-power [matrix exponent]
  (when (neg? exponent)
    (throw (ex-info "Exponent must not be negative"
                    {:exponent exponent})))
  (let [size (count matrix)]
    (when-not (every? #(= size (count %)) matrix)
      (throw (ex-info "Matrix must be square" {})))
    (loop [power exponent
           base matrix
           result (identity-matrix size)]
      (if (zero? power)
        result
        (recur (quot power 2)
               (matrix-multiply base base)
               (if (odd? power)
                 (matrix-multiply result base)
                 result))))))

(defn identity-matrix? [matrix]
  (let [size (count matrix)]
    (and (every? #(= size (count %)) matrix)
         (every? (fn [[row column]]
                   (= (get-in matrix [row column])
                      (if (= row column) 1 0)))
                 (for [row (range size)
                       column (range size)]
                   [row column])))))

(identity-matrix 3)
;; => [[1 0 0] [0 1 0] [0 0 1]]

(diagonal-matrix [2 5 7])
;; => [[2 0 0] [0 5 0] [0 0 7]]

(matrix-power [[1 1] [1 0]] 5)
;; => [[8 5] [5 3]]

;; Executable checks

(assert (= [[1 0 0] [0 1 0] [0 0 1]] (identity-matrix 3)))
(assert (= [[2 0 0] [0 5 0] [0 0 7]]
           (diagonal-matrix [2 5 7])))
(assert (= [[8 5] [5 3]] (matrix-power [[1 1] [1 0]] 5)))
```

Clojure persistent vectors do not have Python's repeated-row aliasing problem. Repeated immutable rows are safe.

### Memory Hooks

- Identity rule: `row = column`.
- Diagonal values can replace the ones.
- Identity starts exponentiation.
- A permutation matrix moves rows through multiplication.

### Key Insight

Identity is both a generated pattern and an algebraic unit. Multiplying by it leaves the other matrix unchanged.

## The Generation Section

Each lesson in this section generates a value from its coordinate.
