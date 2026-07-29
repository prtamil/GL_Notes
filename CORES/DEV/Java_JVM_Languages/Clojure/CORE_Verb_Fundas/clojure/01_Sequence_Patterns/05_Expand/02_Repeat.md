# Pattern 16 — Repeat

## Mental Model

Generate the **same value multiple times** or **repeat an entire sequence**.

Unlike **FlatMap**, which expands by transformation, **Repeat** expands by duplication.

---

## Relationship to Cognitive Verb

```text
Expand
   ↓
Repeat
```

Repeat is an **Expand** pattern because it increases the size of a sequence by duplicating values or sequences.

---

## Clojure Functions & Common Idioms

|Variation|Example|Common Clojure|
|---|---|---|
|Repeat Value N Times|`A A A`|`repeat n`|
|Infinite Repeat|`A A A ...`|`repeat`|
|Repeat Entire Sequence|`1 2 3 1 2 3`|`cycle`|
|Repeat with Limit|First N repeated values|`take` + `repeat`|
|Repeat Pattern|`A B A B A B`|`cycle` + `take`|
|Duplicate Each Element|`1 1 2 2 3 3`|`mapcat` + `repeat`|

> **Note:** `repeat` duplicates **one value**, whereas `cycle` repeats an **entire sequence**.

---

## Common Uses

- Default values
    
- Padding
    
- Test data generation
    
- Infinite streams
    
- Animation loops
    
- Round-robin processing
    
- Sequence duplication
    
- Pattern generation
    

---

## Hidden Interview Problems

- Initialize an array
    
- Pad sequences
    
- Generate repeated patterns
    
- Create infinite streams
    
- Duplicate each element
    
- Repeat values K times
    

---

## Recognition Clues

If you hear:

- Repeat
    
- Duplicate
    
- Same value
    
- Fill
    
- Pad
    
- Infinite sequence
    
- Cycle
    
- Repeat K times
    

Think:

**→ Repeat**

---

## Pattern Summary

|Property|Value|
|---|---|
|Cognitive Verb|Expand|
|Pattern|Repeat|
|Output Size|Larger than input|
|Expands By|Duplication|
|Infinite Version|Yes|
|Primary Use|Replication|

---

## Clojure Recipe Book

```clojure
;;--------------------------------------------------------
;; Repeat a Value N Times
;;--------------------------------------------------------

(repeat 5 :x)

;; =>
(:x :x :x :x :x)


;;--------------------------------------------------------
;; Infinite Repeat
;;--------------------------------------------------------

(take 6 (repeat "Hi"))

;; =>
("Hi" "Hi" "Hi" "Hi" "Hi" "Hi")


;;--------------------------------------------------------
;; Repeat an Entire Sequence
;;--------------------------------------------------------

(take 8 (cycle [1 2 3]))

;; =>
(1 2 3 1 2 3 1 2)


;;--------------------------------------------------------
;; Repeat a Pattern
;;--------------------------------------------------------

(take 10 (cycle [:A :B]))

;; =>
(:A :B :A :B :A :B :A :B :A :B)


;;--------------------------------------------------------
;; Duplicate Every Element
;;--------------------------------------------------------

(mapcat #(repeat 2 %) [1 2 3])

;; =>
(1 1 2 2 3 3)


;;--------------------------------------------------------
;; Repeat Each Element Three Times
;;--------------------------------------------------------

(mapcat #(repeat 3 %) [1 2 3])

;; =>
(1 1 1 2 2 2 3 3 3)


;;--------------------------------------------------------
;; Create an Initialized Vector
;;--------------------------------------------------------

(vec (repeat 5 0))

;; =>
[0 0 0 0 0]


;;--------------------------------------------------------
;; Pad a Sequence
;;--------------------------------------------------------

(concat [1 2 3]
        (repeat 3 0))

;; =>
(1 2 3 0 0 0)


;;--------------------------------------------------------
;; Alternate Repeated Patterns
;;--------------------------------------------------------

(take 12
      (cycle [:red :green :blue]))

;; =>
(:red :green :blue
 :red :green :blue
 :red :green :blue
 :red :green :blue)


;;--------------------------------------------------------
;; Repeat Characters
;;--------------------------------------------------------

(apply str (repeat 8 "*"))

;; =>
"********"
```