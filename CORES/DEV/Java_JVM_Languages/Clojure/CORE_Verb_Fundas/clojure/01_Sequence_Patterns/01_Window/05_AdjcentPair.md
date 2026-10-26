# Pattern 5 — Adjacent Pair

## Mental Model

Process **neighboring elements** together to compare, transform, or detect transitions.

---

## Relationship to Cognitive Verb

```text
Window
   ↓
Adjacent Pair
```

Adjacent Pair is a specialized **Sliding Window** where the **window size is always 2**.

---

## Clojure Functions & Common Idioms

| Variation                          | Example             | Common Clojure                                      |
| ---------------------------------- | ------------------- | --------------------------------------------------- |
| Forward Pair (Current → Next)      | `(1 2) (2 3) (3 4)` | `partition 2 1`                                     |
| Forward Pair (keep partial tail)   | `(1 2) (2 3) (3)`   | `partition-all 2 1`                                 |
| Current + Next                     | `(curr next)`       | `(map vector xs (rest xs))`                         |
| Previous + Current                 | `(prev curr)`       | `(map vector xs (rest xs))` _(viewed from current)_ |
| Previous + Current + Next          | `(prev curr next)`  | `partition 3 1`                                     |
| Compare Adjacent Values            | `(< curr next)`     | `partition 2 1` + `map`                             |
| Difference Between Adjacent Values | `(- next curr)`     | `partition 2 1` + `map`                             |
| Adjacent with Index                | `(idx curr next)`   | `map-indexed` + `rest`                              |
|                                    |                     |                                                     |
|                                    |                     |                                                     |
> **Note:** `Current + Next` and `Previous + Current` use `(map vector xs (rest xs))`. The code is the same. Only the interpretation of each pair changes.
---

## Common Uses

- Compare neighboring values
    
- Consecutive differences (delta)
    
- Trend detection
    
- Transition detection
    
- Sortedness checking
    
- Duplicate detection
    
- Velocity from positions
    
- Line / edge construction
    
- Change-point detection
    

---

## Hidden Interview Problems

- Check if an array is sorted
    
- Find adjacent duplicates
    
- Compute differences between consecutive values
    
- Count increasing/decreasing pairs
    
- Detect peaks and valleys
    
- Find transition points
    
- Compare neighboring timestamps
    

---

## Recognition Clues

If you hear:

- Previous element
    
- Next element
    
- Neighbor
    
- Adjacent
    
- Consecutive
    
- Delta
    
- Transition
    
- Compare with previous
    
- Compare with next
    
- Pairwise
    

Think:

**→ Adjacent Pair**

---

## Pattern Summary

|Property|Value|
|---|---|
|Cognitive Verb|Window|
|Pattern|Adjacent Pair|
|Overlap|Yes|
|Window Size|2 (or 3 for both neighbors)|
|Step Size|1|
|Preserves Order|Yes|
|Covers All Elements|Yes (except boundaries unless handled explicitly)|

---

## Clojure Recipe Book

```clojure
;; ============================================
;; Setup

(def xs [10 20 30 40])

;; ============================================
;; The pattern itself

(partition 2 1 xs)
;; => ((10 20) (20 30) (30 40))

(map vector xs (rest xs))          ; the zip view, if you prefer vectors
;; => ([10 20] [20 30] [30 40])

;; n pairs from n+1 elements — there is always one fewer pair than element.

;; ============================================
;; Descriptive names make the direction clear.

(for [[current next-value] (partition 2 1 xs)]
  {:current current :next next-value})
;; => ({:current 10, :next 20} {:current 20, :next 30} {:current 30, :next 40})

(for [[previous current] (partition 2 1 xs)]
  {:previous previous :current current})
;; => ({:previous 10, :current 20} {:previous 20, :current 30} {:previous 30, :current 40})

;; ============================================
;; Deltas — the classic use

(map (fn [[a b]] (- b a)) (partition 2 1 xs))
;; => (10 10 10)

;; but the shorter Clojure phrasing skips the pairing entirely:
(map - (rest xs) xs)
;; => (10 10 10)

;; map stops at the shortest input, so (rest xs) against xs IS the
;; pairwise difference. Worth knowing — it reads as "each minus its
;; predecessor" with no destructuring at all.

;; velocity from positions + timestamps
(let [ts  [0 1 3 6]
      pos [0 5 15 45]]
  (map / (map - (rest pos) pos) (map - (rest ts) ts)))
;; => (5 5 10)

;; ============================================
;; Sortedness — Clojure's comparators are variadic

(apply <= xs)     ;; => true    non-decreasing
(apply <  xs)     ;; => true    strictly increasing

;; that is the whole check. No pairing, no every?.
;; The explicit form, for when the predicate is not a comparator:
(every? #(apply <= %) (partition 2 1 xs))     ;; => true
(some   #(apply >  %) (partition 2 1 xs))     ;; => nil   (any inversion?)

;; caveat: apply on a comparator realizes the whole collection,
;; so use the partition form on a lazy or very large sequence.

;; ============================================
;; Adjacent duplicates

(map first (filter #(apply = %) (partition 2 1 [1 2 2 3 3 3])))
;; => (2 3 3)

(some #(apply = %) (partition 2 1 [1 2 2 3]))
;; => true

;; ============================================
;; Count increasing / decreasing steps

(let [s     [3 1 4 1 5]
      steps (map - (rest s) s)]
  [steps
   (count (filter pos? steps))
   (count (filter neg? steps))])
;; => [(-2 3 -3 4) 2 2]

;; ============================================
;; Transition points — where the value changes

(keep-indexed (fn [i [a b]] (when (not= a b) (inc i)))
              (partition 2 1 ["a" "a" "b" "b" "c"]))
;; => (2 4)     indices where a new run begins

;; ============================================
;; Peaks and valleys — needs THREE neighbours, not two

(def ys [1 3 2 5 4])

(keep-indexed (fn [i [a b c]] (when (and (< a b) (> b c)) (inc i)))
              (partition 3 1 ys))
;; => (1 3)     peaks

(keep-indexed (fn [i [a b c]] (when (and (> a b) (< b c)) (inc i)))
              (partition 3 1 ys))
;; => (2)       valleys

;; the (inc i) is because window i is centred on element i+1

;; ============================================
;; Both neighbours with the edges handled

(map vector (cons nil [1 2 3]) [1 2 3] (concat (rest [1 2 3]) [nil]))
;; => ([nil 1 2] [1 2 3] [2 3 nil])

;; Boundaries are where adjacent-pair bugs live — pad them on purpose.

;; ============================================
;; Cyclic pairs — last element wraps to the first

(partition 2 1 (concat xs [(first xs)]))
;; => ((10 20) (20 30) (30 40) (40 10))

;; polygon edges, round-robin schedules, ring buffers

;; ============================================
;; Gap detection in timestamps

(filter (fn [[a b]] (> (- b a) 5)) (partition 2 1 [0 1 2 10 11]))
;; => ((2 10))

;; ============================================
;; Trend direction as a string

(defn trend [values]
  (apply str (map (fn [[a b]] (cond (> b a) \+ (< b a) \- :else \=))
                  (partition 2 1 values))))

(trend [1 3 3 2])         ;; => "+=-"

;; then partition-by finds the runs — Clojure's groupby-on-adjacency
(map (fn [g] [(first g) (count g)])
     (partition-by identity (trend [1 2 3 2 1])))
;; => ([\+ 2] [\- 2])

;; ============================================
;; Keep the ragged tail (rare, but asked for sometimes)

(partition-all 2 1 xs)
;; => ((10 20) (20 30) (30 40) (40))

;; ============================================
;; Compare

(partition 2 1 xs)     ; size 2, step 1  ← this pattern
(partition 3 1 xs)     ; size 3, step 1  ← both neighbours
(partition 2 2 xs)     ; size 2, step 2  ← disjoint pairs (Chunk)
;; => ((10 20) (30 40))
```

---

### Memory Hooks

|You want|You reach for|
|---|---|
|each item with its next|`(partition 2 1 xs)`|
|each item with its previous|`(partition 2 1 xs)`, read right-to-left|
|both neighbours|`(partition 3 1 xs)`|
|differences|`(map - (rest xs) xs)`|
|"is it sorted?"|`(apply <= xs)`|
|"where does it change?"|`(keep-indexed …)` over `(partition 2 1 xs)`|
|runs of the same value|`(partition-by identity …)`|
|wrap-around|`(partition 2 1 (concat xs [(first xs)]))`|
|disjoint pairs instead|`(partition 2 2 xs)`|

---

### Key Insight

**Adjacent pairs turn values into changes.** `[10 20 30]` has three states and two transitions. Many order and rate questions use these transitions.

Clojure provides two useful short forms. `(map - (rest xs) xs)` calculates adjacent changes. `(apply <= xs)` tests the order without building pairs.

Two things to watch. The result is **one element shorter**, and **the endpoints have no neighbour**. Every off-by-one in this pattern traces back to one of those two.

