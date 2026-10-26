# Pattern 31 — Range Generation

## Mental Model

Generate a **sequence of values following a regular interval**.

Unlike **Repeat**, which duplicates the same value, **Range** generates **progressively changing values**.

---

## Relationship to Cognitive Verb

```text
Generate
    ↓
Range
```

Range is a **Generate** pattern because it creates a new sequence from a start, end, and optional step.

---

## Clojure Functions & Common Idioms

|Variation|Example|Common Clojure|
|---|---|---|
|Natural Numbers|`0 1 2 3`|`range`|
|Start & End|`5 6 7 8`|`range start end`|
|Step Size|`0 2 4 6`|`range start end step`|
|Descending Range|`10 8 6 4`|`range start end -2`|
|Infinite Range|`0 1 2 ...`|`range`|
|Enumerate Indices|`0..n-1`|`range` + `count`|

> **Note:** `range` generates values **lazily**, so even infinite ranges are practical when combined with `take`.

---

## Common Uses

- Loop indices
    
- Coordinate generation
    
- Animation frames
    
- Time intervals
    
- Pagination
    
- Test data
    
- Number sequences
    
- Grid generation
    

---

## Hidden Interview Problems

- Generate numbers from 1 to N
    
- FizzBuzz
    
- Matrix coordinates
    
- Pagination
    
- Number series
    
- Iterate over indices
    

---

## Recognition Clues

If you hear:

- Generate numbers
    
- From X to Y
    
- Every N steps
    
- Indices
    
- Sequence of integers
    
- Counting
    
- Loop N times
    

Think:

**→ Range**

---

## Pattern Summary

|Property|Value|
|---|---|
|Cognitive Verb|Generate|
|Pattern|Range|
|Input|Start, End, Step|
|Output|Generated sequence|
|Lazy|Yes|
|Primary Use|Sequential generation|

---

## Clojure Recipe Book

```clojure
;;--------------------------------------------------------
;; Default Range
;;--------------------------------------------------------

(range 5)

;; =>
;; (0 1 2 3 4)


;;--------------------------------------------------------
;; Start and End
;;--------------------------------------------------------

(range 3 8)

;; =>
;; (3 4 5 6 7)


;;--------------------------------------------------------
;; Step Size
;;--------------------------------------------------------

(range 0 10 2)

;; =>
;; (0 2 4 6 8)


;;--------------------------------------------------------
;; Descending Range
;;--------------------------------------------------------

(range 10 0 -2)

;; =>
;; (10 8 6 4 2)


;;--------------------------------------------------------
;; Infinite Range
;;--------------------------------------------------------

(take 10 (range))

;; =>
;; (0 1 2 3 4 5 6 7 8 9)


;;--------------------------------------------------------
;; Enumerate Indices
;;--------------------------------------------------------

(map vector
     (range)
     [:a :b :c])

;; =>
;; ([0 :a]
 ;; [1 :b]
 ;; [2 :c])


;;--------------------------------------------------------
;; Build Coordinate Grid
;;--------------------------------------------------------

(for [x (range 3)
      y (range 2)]
  [x y])

;; =>
;; ([0 0]
 ;; [0 1]
 ;; [1 0]
 ;; [1 1]
 ;; [2 0]
 ;; [2 1])


;;--------------------------------------------------------
;; Generate Alphabet Positions
;;--------------------------------------------------------

(map #(char (+ (int \A) %))
     (range 5))

;; =>
;; (\A \B \C \D \E)


;;--------------------------------------------------------
;; Generate Every 15 Minutes
;;--------------------------------------------------------

(range 0 61 15)

;; =>
;; (0 15 30 45 60)


;;--------------------------------------------------------
;; Repeat N Times Using Range
;;--------------------------------------------------------

(dotimes [i 5]
  (println i))

;; or

(doseq [i (range 5)]
  (println i))

;; =>
;; 0
;; 1
;; 2
;; 3
;; 4
```

---

### Readable Clojure Functions

```clojure
(defn inclusive-range
  ([end]
   (inclusive-range 0 end 1))
  ([start end]
   (inclusive-range start end 1))
  ([start end step]
   (when (zero? step)
     (throw (ex-info "Step must not be zero" {:step step})))
   (if (pos? step)
     (take-while (fn [value] (<= value end))
                 (iterate (fn [value] (+ value step)) start))
     (take-while (fn [value] (>= value end))
                 (iterate (fn [value] (+ value step)) start)))))

(defn float-range [start end step]
  (when (zero? step)
    (throw (ex-info "Step must not be zero" {:step step})))
  (let [inside? (if (pos? step)
                  (fn [value] (< value end))
                  (fn [value] (> value end)))]
    (take-while inside?
                (iterate (fn [value] (+ value step)) start))))

(defn chunk-boundaries [size width]
  (when (or (neg? size) (not (pos? width)))
    (throw (ex-info "Size and width are invalid"
                    {:size size :width width})))
  (range 0 size width))

(defn coordinate-grid [rows columns]
  (for [row (range rows)
        column (range columns)]
    [row column]))

(defn character-range [first-char last-char]
  (map char
       (inclusive-range (int first-char)
                        (int last-char))))

(defn fizzbuzz [limit]
  (map (fn [value]
         (cond
           (zero? (mod value 15)) "FizzBuzz"
           (zero? (mod value 3)) "Fizz"
           (zero? (mod value 5)) "Buzz"
           :else (str value)))
       (range 1 (inc limit))))

(range 5)
;; => (0 1 2 3 4)

(range 5 0 -1)
;; => (5 4 3 2 1)

(take 5 (range))
;; => (0 1 2 3 4)

(chunk-boundaries 12 5)
;; => (0 5 10)

(coordinate-grid 2 3)
;; => ([0 0] [0 1] [0 2] [1 0] [1 1] [1 2])

(character-range \a \e)
;; => (\a \b \c \d \e)
```

For domain values such as dates and timestamps, generate numeric offsets with `range` and map the domain's addition operation over them. That keeps numeric stepping separate from calendar rules.

### Memory Hooks

|You want|You reach for|
|---|---|
|`0` through `n-1`|`(range n)`|
|start, exclusive end|`(range start end)`|
|custom step|`(range start end step)`|
|unbounded integers|`(range)`|
|index and value|`map-indexed`, not a manual range|
|page/chunk starts|`(range 0 size width)`|
|coordinate grid|nested `for`|

### Key Insight

`range` generates arithmetic positions lazily. Its end value is exclusive. Use `iterate` when a function calculates each next value.
