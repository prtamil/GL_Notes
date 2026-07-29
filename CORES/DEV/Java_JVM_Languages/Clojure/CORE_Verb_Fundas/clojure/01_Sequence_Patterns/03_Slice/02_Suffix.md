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
((1 2 3 4 5 6)
 (2 3 4 5 6)
 (3 4 5 6)
 (4 5 6)
 (5 6)
 (6))


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
[(1 2 3)
 (4 5 6)]


;;--------------------------------------------------------
;; Prefix + Suffix Around an Index
;;--------------------------------------------------------

[(take 3 xs)
 (drop 3 xs)]

;; =>
[(1 2 3)
 (4 5 6)]


;;--------------------------------------------------------
;; Sliding Suffixes
;;--------------------------------------------------------

(map #(drop % xs)
     (range (count xs)))

;; =>
((1 2 3 4 5 6)
 (2 3 4 5 6)
 (3 4 5 6)
 (4 5 6)
 (5 6)
 (6))
```