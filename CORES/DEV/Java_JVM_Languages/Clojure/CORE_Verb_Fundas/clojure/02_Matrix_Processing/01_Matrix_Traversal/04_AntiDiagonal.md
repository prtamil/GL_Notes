# 4. Anti-Diagonal Traversal

## Mental Model

Cells share an anti-diagonal when `row + column` is constant. The main path starts at the top-right corner.

## Relationship to Cognitive Verb

```text
Trace -> keep row + column constant
```

## Clojure Functions and Common Idioms

|Need|Use|
|---|---|
|Main anti-diagonal|start at `[0, last-column]`|
|Offset anti-diagonal|select a coordinate sum|
|Both main lines|combine two coordinate sets|
|All anti-diagonals|map all valid sums|

## Common Uses

- Check board wins.
- Find X-shaped patterns.
- Compare diagonal sums.
- Group cells by coordinate sum.

## Hidden Interview Problems

- Remove the duplicate center of an X.
- Check anti-diagonal symmetry.
- Traverse rectangular input.
- Find the maximum value on one diagonal.

## Recognition Clues

Look for `top-right to bottom-left`, `opposite diagonal`, or a constant coordinate sum.

## Pattern Summary

For sum `s`, every coordinate satisfies `row + column = s`.

## Shape and Edge Behavior

- The traversal functions expect a finite rectangular matrix.
- A matrix with no cells returns empty anti-diagonal results.
- The traversal functions reject ragged rows with `ExceptionInfo`.

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

(defn matrix-shape [matrix]
  (require-rectangular matrix)
  [(count matrix) (if-let [row (first matrix)] (count row) 0)])

(defn anti-diagonal-coordinates [matrix coordinate-sum]
  (let [[rows columns] (matrix-shape matrix)
        first-row (max 0 (- coordinate-sum (dec columns)))
        end-row (min rows (inc coordinate-sum))]
    (mapv (fn [row]
            [row (- coordinate-sum row)])
          (range first-row end-row))))

(defn anti-diagonal [matrix coordinate-sum]
  (mapv #(get-in matrix %)
        (anti-diagonal-coordinates matrix coordinate-sum)))

(defn main-anti-diagonal [matrix]
  (let [[_ columns] (matrix-shape matrix)]
    (if (zero? columns)
      []
      (anti-diagonal matrix (dec columns)))))

(defn all-anti-diagonals [matrix]
  (let [[rows columns] (matrix-shape matrix)]
    (if (or (zero? rows) (zero? columns))
      []
      (mapv #(anti-diagonal matrix %)
            (range (dec (+ rows columns)))))))

(defn x-coordinates [size]
  (set (concat
         (map (fn [index] [index index]) (range size))
         (map (fn [index] [index (- (dec size) index)])
              (range size)))))

(defn x-pattern? [grid mark]
  (let [size (count grid)
        x-cells (x-coordinates size)]
    (and (every? #(= size (count %)) grid)
         (every? (fn [[row column]]
                   (= (= mark (get-in grid [row column]))
                      (contains? x-cells [row column])))
                 (for [row (range size)
                       column (range size)]
                   [row column])))))

(defn anti-diagonal-symmetric? [matrix]
  (let [[rows columns] (matrix-shape matrix)]
    (and (= rows columns)
         (every? (fn [[row column]]
                   (= (get-in matrix [row column])
                      (get-in matrix [(- (dec rows) column)
                                      (- (dec rows) row)])))
                 (for [row (range rows)
                       column (range columns)]
                   [row column])))))

(def matrix [[1 2 3] [4 5 6] [7 8 9]])

(main-anti-diagonal matrix)
;; => [3 5 7]

(all-anti-diagonals matrix)
;; => [[1] [2 4] [3 5 7] [6 8] [9]]

;; Executable checks

(assert (= [3 5 7] (main-anti-diagonal matrix)))
(assert (= [[1] [2 4] [3 5 7] [6 8] [9]]
           (all-anti-diagonals matrix)))
```

The functions return `[]` when the matrix has no cells.

### Memory Hooks

- Main diagonal: coordinate difference.
- Anti-diagonal: coordinate sum.
- Use a set when two diagonals can share the center.

### Key Insight

The sum groups every anti-diagonal. This rule removes special cases for square and rectangular matrices.
