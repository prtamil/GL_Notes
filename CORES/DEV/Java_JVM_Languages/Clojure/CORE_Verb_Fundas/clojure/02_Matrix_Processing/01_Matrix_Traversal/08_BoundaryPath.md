# 8. Boundary Traversal

## Mental Model

Visit one outer ring only. Walk the top, right, bottom, and left edges without repeating corners.

## Relationship to Cognitive Verb

```text
Outline -> one outer ring
```

## Clojure Functions and Common Idioms

|Need|Use|
|---|---|
|Test one cell|border predicate|
|Keep clockwise order|four coordinate ranges|
|Read values|`mapv` with `get-in`|
|Change ring values|`reduce` with `assoc-in`|

## Common Uses

- Calculate a perimeter sum.
- Draw a frame.
- Inspect image borders.
- Rotate the outside ring.

## Hidden Interview Problems

- Avoid duplicate corners.
- Handle one row or one column.
- Generate counter-clockwise order.
- Rotate only the boundary values.

## Recognition Clues

Look for `border`, `perimeter`, `outer ring`, `frame`, or `edge cells`.

## Pattern Summary

Traversal needs ordered edges. Aggregation can use a simple border predicate.

## Shape and Edge Behavior

- Matrix operations expect a finite rectangular matrix.
- Empty and zero-width matrices return empty paths.
- Coordinate generation rejects negative dimensions.
- Matrix operations reject ragged rows with `ExceptionInfo`.

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

(defn require-nonnegative-dimensions [rows columns]
  (when (or (neg? rows) (neg? columns))
    (throw (ex-info "Matrix dimensions must not be negative"
                    {:rows rows :columns columns}))))

(defn on-border? [row column rows columns]
  (and (pos? rows)
       (pos? columns)
       (or (zero? row)
           (zero? column)
           (= row (dec rows))
           (= column (dec columns)))))

(defn boundary-coordinates [rows columns]
  (require-nonnegative-dimensions rows columns)
  (cond
    (or (zero? rows) (zero? columns)) []
    (= rows 1) (mapv (fn [column] [0 column]) (range columns))
    (= columns 1) (mapv (fn [row] [row 0]) (range rows))
    :else
    (vec
      (concat
        (for [column (range columns)] [0 column])
        (for [row (range 1 rows)] [row (dec columns)])
        (for [column (range (- columns 2) -1 -1)]
          [(dec rows) column])
        (for [row (range (- rows 2) 0 -1)] [row 0])))))

(defn boundary-order [matrix]
  (require-rectangular matrix)
  (let [rows (count matrix)
        columns (if-let [row (first matrix)] (count row) 0)]
    (mapv #(get-in matrix %)
          (boundary-coordinates rows columns))))

(defn counter-clockwise-boundary [matrix]
  (let [clockwise (boundary-order matrix)]
    (if (empty? clockwise)
      []
      (into [(first clockwise)] (reverse (rest clockwise))))))

(defn boundary-sum [matrix]
  (reduce + 0 (boundary-order matrix)))

(defn frame [rows columns edge fill]
  (require-nonnegative-dimensions rows columns)
  (mapv (fn [row]
          (mapv (fn [column]
                  (if (on-border? row column rows columns)
                    edge
                    fill))
                (range columns)))
        (range rows)))

(defn rotate-boundary [matrix steps]
  (require-rectangular matrix)
  (let [rows (count matrix)
        columns (if-let [row (first matrix)] (count row) 0)
        path (boundary-coordinates rows columns)
        values (mapv #(get-in matrix %) path)
        size (count path)]
    (if (zero? size)
      matrix
      (let [shift (mod steps size)
            shifted (mapv (fn [index]
                            (values (mod (- index shift) size)))
                          (range size))]
        (reduce (fn [result [coordinate value]]
                  (assoc-in result coordinate value))
                matrix
                (map vector path shifted))))))

(def matrix
  [[1  2  3  4]
   [5  6  7  8]
   [9 10 11 12]
   [13 14 15 16]])

(boundary-order matrix)
;; => [1 2 3 4 8 12 16 15 14 13 9 5]

(frame 3 4 "#" ".")
;; => [["#" "#" "#" "#"] ["#" "." "." "#"] ["#" "#" "#" "#"]]

;; Executable checks

(assert (= [1 2 3 4 8 12 16 15 14 13 9 5]
           (boundary-order matrix)))
(assert (= [["#" "#" "#" "#"]
            ["#" "." "." "#"]
            ["#" "#" "#" "#"]]
           (frame 3 4 "#" ".")))
```

The coordinate function handles empty, single-row, single-column, and single-cell shapes.

### Memory Hooks

- Top includes both top corners.
- Right excludes the top corner.
- Bottom excludes the right corner.
- Left excludes both corners.

### Key Insight

Generate boundary coordinates once. Reuse them to read, sum, compare, draw, or rotate the border.

## Boundary vs Spiral

Boundary traversal stops after one ring. Spiral traversal repeats the same idea after it shrinks all four bounds.
