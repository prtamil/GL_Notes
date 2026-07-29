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
(0 1 2 3 4)


;;--------------------------------------------------------
;; Start and End
;;--------------------------------------------------------

(range 3 8)

;; =>
(3 4 5 6 7)


;;--------------------------------------------------------
;; Step Size
;;--------------------------------------------------------

(range 0 10 2)

;; =>
(0 2 4 6 8)


;;--------------------------------------------------------
;; Descending Range
;;--------------------------------------------------------

(range 10 0 -2)

;; =>
(10 8 6 4 2)


;;--------------------------------------------------------
;; Infinite Range
;;--------------------------------------------------------

(take 10 (range))

;; =>
(0 1 2 3 4 5 6 7 8 9)


;;--------------------------------------------------------
;; Enumerate Indices
;;--------------------------------------------------------

(map vector
     (range)
     [:a :b :c])

;; =>
([0 :a]
 [1 :b]
 [2 :c])


;;--------------------------------------------------------
;; Build Coordinate Grid
;;--------------------------------------------------------

(for [x (range 3)
      y (range 2)]
  [x y])

;; =>
([0 0]
 [0 1]
 [1 0]
 [1 1]
 [2 0]
 [2 1])


;;--------------------------------------------------------
;; Generate Alphabet Positions
;;--------------------------------------------------------

(map #(char (+ (int \A) %))
     (range 5))

;; =>
(\A \B \C \D \E)


;;--------------------------------------------------------
;; Generate Every 15 Minutes
;;--------------------------------------------------------

(range 0 61 15)

;; =>
(0 15 30 45 60)


;;--------------------------------------------------------
;; Repeat N Times Using Range
;;--------------------------------------------------------

(dotimes [i 5]
  (println i))

;; or

(doseq [i (range 5)]
  (println i))

;; =>
0
1
2
3
4
```