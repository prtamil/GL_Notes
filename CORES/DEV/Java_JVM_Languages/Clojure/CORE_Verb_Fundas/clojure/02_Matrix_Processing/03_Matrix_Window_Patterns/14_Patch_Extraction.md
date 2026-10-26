# 14. Patch Extraction

## Mental Model

Extract every local window with its origin. Keep the patches for later processing, batching, or reconstruction.

## Relationship to Cognitive Verb

```text
Extract -> matrix -> ordered patch collection
```

## Clojure Functions and Common Idioms

|Need|Use|
|---|---|
|Patch positions|stepped `range`|
|Keep origin data|maps with `:origin` and `:values`|
|Flatten patches|`into [] cat`|
|Read outside edges|a named boundary policy|
|Reconstruct overlaps|sum and count each destination cell|

## Common Uses

- Prepare image model input.
- Extract local features.
- Build an `im2col` matrix.
- Reconstruct data from overlapping patches.
- Inspect centered areas near edges.

## Hidden Interview Problems

- Calculate output shape.
- Add zero, clamp, wrap, or reflect padding.
- Map patch indexes back to source cells.
- Average overlaps during reconstruction.

## Recognition Clues

Look for `extract patches`, `crop every region`, `im2col`, `unfold`, or `reconstruct overlaps`.

## Pattern Summary

Patch extraction materializes windows. This choice uses more memory but supports reuse and batch work.

## Shape and Edge Behavior

- The functions expect a finite rectangular matrix.
- Patch dimensions and stride must be positive.
- Padding and output dimensions must not be negative.
- The functions reject ragged rows with `ExceptionInfo`.

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

(defn output-length [input-size patch-size stride padding]
  (when (or (neg? input-size) (not (pos? patch-size))
            (not (pos? stride)) (neg? padding))
    (throw (ex-info "Patch dimensions, stride, or padding are invalid"
                    {:input-size input-size :patch-size patch-size
                     :stride stride :padding padding})))
  (if (> patch-size (+ input-size (* 2 padding)))
    0
    (inc (quot (- (+ input-size (* 2 padding)) patch-size)
               stride))))

(defn output-shape [rows columns height width stride padding]
  [(output-length rows height stride padding)
   (output-length columns width stride padding)])

(defn reflect-index [index size]
  (cond
    (zero? size) nil
    (= size 1) 0
    :else
    (let [period (* 2 (dec size))
          position (mod index period)]
      (if (< position size)
        position
        (- period position)))))

(defn sample-cell
  ([matrix coordinate mode] (sample-cell matrix coordinate mode 0))
  ([matrix [row column] mode fill]
   (let [rows (count matrix)
         columns (if-let [source-row (first matrix)] (count source-row) 0)
         in-bounds? (and (<= 0 row) (< row rows)
                         (<= 0 column) (< column columns))]
     (if in-bounds?
       (get-in matrix [row column])
       (case mode
         :zero fill
         :clamp (when (and (pos? rows) (pos? columns))
                  (get-in matrix [(min (dec rows) (max 0 row))
                                  (min (dec columns) (max 0 column))]))
         :wrap (when (and (pos? rows) (pos? columns))
                 (get-in matrix [(mod row rows) (mod column columns)]))
         :reflect (when (and (pos? rows) (pos? columns))
                    (get-in matrix [(reflect-index row rows)
                                    (reflect-index column columns)]))
         (throw (ex-info "Unknown boundary mode" {:mode mode})))))))

(defn patch-at [matrix [row column] height width mode fill]
  (require-rectangular matrix)
  (when (or (not (pos? height)) (not (pos? width)))
    (throw (ex-info "Patch dimensions must be positive"
                    {:height height :width width})))
  (mapv (fn [row-offset]
          (mapv (fn [column-offset]
                  (sample-cell matrix
                               [(+ row row-offset) (+ column column-offset)]
                               mode
                               fill))
                (range width)))
        (range height)))

(defn patch-origins [rows columns height width stride padding]
  (let [[output-rows output-columns]
        (output-shape rows columns height width stride padding)]
    (vec
      (for [output-row (range output-rows)
            output-column (range output-columns)]
        [(- (* output-row stride) padding)
         (- (* output-column stride) padding)]))))

(defn extract-patches
  ([matrix size] (extract-patches matrix size size 1 0 :zero))
  ([matrix height width stride padding mode]
   (require-rectangular matrix)
   (let [rows (count matrix)
         columns (if-let [row (first matrix)] (count row) 0)]
     (mapv (fn [origin]
             {:origin origin
              :values (patch-at matrix origin height width mode 0)})
           (patch-origins rows columns height width stride padding)))))

(defn im2col [matrix size stride]
  (mapv (fn [{:keys [values]}]
          (vec (mapcat identity values)))
        (extract-patches matrix size size stride 0 :zero)))

(defn centered-patch [matrix [row column] radius mode]
  (when (neg? radius)
    (throw (ex-info "Radius must not be negative" {:radius radius})))
  (let [size (inc (* 2 radius))]
    (patch-at matrix [(- row radius) (- column radius)]
              size size mode 0)))

(defn patch-indexes [matrix size stride]
  (mapv (fn [{:keys [origin values]}]
          {:origin origin
           :coordinates
           (mapv (fn [row-offset]
                   (mapv (fn [column-offset]
                           (mapv + origin [row-offset column-offset]))
                         (range size)))
                 (range size))
           :values values})
        (extract-patches matrix size size stride 0 :zero)))

(defn inside-shape? [rows columns [row column]]
  (and (<= 0 row) (< row rows)
       (<= 0 column) (< column columns)))

(defn add-patch-cell [state origin values rows columns
                      [row-offset column-offset]]
  (let [coordinate (mapv + origin [row-offset column-offset])]
    (if (inside-shape? rows columns coordinate)
      (-> state
          (update-in (into [:sums] coordinate)
                     + (get-in values [row-offset column-offset]))
          (update-in (into [:counts] coordinate) inc))
      state)))

(defn add-patch [state rows columns {:keys [origin values]}]
  (reduce (fn [current offsets]
            (add-patch-cell current origin values rows columns offsets))
          state
          (for [row-offset (range (count values))
                column-offset (range (count (first values)))]
            [row-offset column-offset])))

(defn averaged-cell [sums counts row column]
  (let [count-at-cell (get-in counts [row column])]
    (if (zero? count-at-cell)
      0
      (/ (get-in sums [row column]) count-at-cell))))

(defn fold-patches [patches rows columns]
  (when (or (neg? rows) (neg? columns))
    (throw (ex-info "Output dimensions must not be negative"
                    {:rows rows :columns columns})))
  (let [blank (vec (repeat rows (vec (repeat columns 0))))
        initial {:sums blank :counts blank}
        {:keys [sums counts]}
        (reduce (fn [state patch]
                  (add-patch state rows columns patch))
                initial
                patches)]
    (mapv (fn [row]
            (mapv (fn [column]
                    (averaged-cell sums counts row column))
                  (range columns)))
          (range rows))))

(def matrix [[1 2 3] [4 5 6] [7 8 9]])

(im2col matrix 2 1)
;; => [[1 2 4 5] [2 3 5 6] [4 5 7 8] [5 6 8 9]]

(fold-patches (extract-patches matrix 2 2 1 0 :zero) 3 3)
;; => the original matrix

;; Executable checks

(assert (= [[1 2 4 5] [2 3 5 6] [4 5 7 8] [5 6 8 9]]
           (im2col matrix 2 1)))
(assert (= matrix
           (fold-patches (extract-patches matrix 2 2 1 0 :zero)
                         3
                         3)))
```

`extract-patches` returns a vector. Use `for` directly when patches should remain lazy.

### Memory Hooks

- A patch needs values and an origin.
- Padding changes legal origins.
- `im2col` makes each patch one row.
- Folding must combine overlap counts.

### Key Insight

Keep patch coordinates with patch values. Reconstruction and debugging then stay direct.

## The Three Window Patterns So Far

|Pattern|Overlap|Main result|
|---|---|---|
|Sliding window|usually yes|one result per placement|
|Tile|no|independent blocks|
|Patch extraction|configurable|stored local matrices|
