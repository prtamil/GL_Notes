# Pattern 10 — Suffix

## Mental Model

Take the **ending portion** of a sequence.

---

## Relationship to Cognitive Verb

```text
Slice
   ↓
Suffix
```

Suffix is a **Slice** pattern that extracts elements **from the end** of a sequence.

---

## Clojure Functions & Common Idioms

|Variation|Example|Common Clojure|
|---|---|---|
|Last N Elements|`8 9 10`|`take-last n`|
|Last Element|`10`|`last`|
|Drop First N (Keep Suffix)|`4 5 6`|`drop n`|
|All Suffixes|`(1 2 3) (2 3) (3)`|`iterate rest` + `take-while seq`|
|Suffix After Predicate|Remaining elements|`drop-while`|

> **Note:** Unlike prefixes, Clojure has no built-in function that directly returns all suffixes.

---

## Common Uses

- Last N records
    
- Recent history
    
- Tail of a stream
    
- File extensions
    
- String suffixes
    
- Remaining elements after a point
    
- Incremental parsing
    
- Resume processing
    

---

## Hidden Interview Problems

- Return last K elements
    
- Check string ends with suffix
    
- Tail a log file
    
- Keep recent history
    
- Remove leading elements
    
- Resume processing from a position
    

---

## Recognition Clues

If you hear:

- Last N
    
- End of sequence
    
- Ends with
    
- Tail
    
- Recent
    
- Remaining
    
- Trailing elements
    
- Suffix
    

Think:

**→ Suffix**

---

## Pattern Summary

|Property|Value|
|---|---|
|Cognitive Verb|Slice|
|Pattern|Suffix|
|Direction|Back|
|Size|Fixed or Predicate-based|
|Preserves Order|Yes|
|Includes Entire Sequence|Possible|

---

## Clojure Recipe Book

```clojure
;;--------------------------------------------------------
;; Input
;;--------------------------------------------------------

(def xs [1 2 3 4 5 6])


;;--------------------------------------------------------
;; Last Element
;;--------------------------------------------------------

(last xs)

;; => 6


;;--------------------------------------------------------
;; Last N Elements
;;--------------------------------------------------------

(take-last 3 xs)

;; => (4 5 6)


;;--------------------------------------------------------
;; Keep Suffix by Dropping Prefix
;;--------------------------------------------------------

(drop 3 xs)

;; => (4 5 6)


;;--------------------------------------------------------
;; Suffix While Predicate Holds
;;--------------------------------------------------------

(drop-while #(< % 4) xs)

;; => (4 5 6)


;;--------------------------------------------------------
;; All Suffixes
;;--------------------------------------------------------

(take-while seq
  (iterate rest xs))

;; =>
;; ((1 2 3 4 5 6)
 ;; (2 3 4 5 6)
 ;; (3 4 5 6)
 ;; (4 5 6)
 ;; (5 6)
 ;; (6))


;;--------------------------------------------------------
;; Nth Suffix
;;--------------------------------------------------------

(nth (iterate rest xs) 2)

;; => (3 4 5 6)


;;--------------------------------------------------------
;; Remove Last Element
;;--------------------------------------------------------

(butlast xs)

;; => (1 2 3 4 5)


;;--------------------------------------------------------
;; Split into Prefix and Suffix
;;--------------------------------------------------------

(split-at 3 xs)

;; =>
;; [(1 2 3)
 ;; (4 5 6)]


;;--------------------------------------------------------
;; Prefix + Suffix Around an Index
;;--------------------------------------------------------

[(take 3 xs)
 (drop 3 xs)]

;; =>
;; [(1 2 3)
 ;; (4 5 6)]


;;--------------------------------------------------------
;; Sliding Suffixes
;;--------------------------------------------------------

(map #(drop % xs)
     (range (count xs)))

;; =>
;; ((1 2 3 4 5 6)
 ;; (2 3 4 5 6)
 ;; (3 4 5 6)
 ;; (4 5 6)
 ;; (5 6)
 ;; (6))
```

---

### Readable Clojure Functions

Suffix operations on counted collections are clearest when the boundary calculation is named. For an unbounded stream, keep only a bounded queue instead of counting the entire input.

```clojure
(defn last-n [amount values]
  (take-last (max 0 amount) values))

(defn drop-prefix [amount values]
  (drop (max 0 amount) values))

(defn all-suffixes [values]
  (map (fn [start] (drop start values))
       (range (inc (count values)))))

(defn split-prefix-suffix [amount values]
  [(take amount values) (drop amount values)])

(defn ends-with? [values ending]
  (and (<= (count ending) (count values))
       (= (seq ending)
          (seq (take-last (count ending) values)))))

(defn longest-common-suffix [& collections]
  (->> collections
       (map reverse)
       (apply map vector)
       (take-while #(apply = %))
       (map first)
       reverse
       vec))

(defn recent-items [capacity values]
  (if-not (pos? capacity)
    []
    (->> values
         (reduce (fn [queue value]
                   (let [queue (conj queue value)]
                     (if (> (count queue) capacity)
                       (pop queue)
                       queue)))
                 clojure.lang.PersistentQueue/EMPTY)
         vec)))

(last-n 3 [1 2 3 4 5])
;; => (3 4 5)

(drop-while neg? [-3 -1 0 2 4])
;; => (0 2 4)

(all-suffixes [1 2 3])
;; => ((1 2 3) (2 3) (3) ())

(longest-common-suffix [1 2 8 9] [3 8 9] [8 9])
;; => [8 9]

(recent-items 3 (range 10))
;; => [7 8 9]
```

### Memory Hooks

|You want|You reach for|
|---|---|
|last item|`last`|
|last `n` items|`take-last`|
|everything after position `n`|`drop`|
|split at `n`|`split-at` or `[take drop]`|
|drop while a prefix matches|`drop-while`|
|all suffixes|`drop` at every boundary|
|bounded recent history|a persistent queue|

### Key Insight

A suffix depends on the removed prefix. Use `drop` when you know the start position. Use `take-last` when you know the suffix size. Use a bounded queue for a stream.
