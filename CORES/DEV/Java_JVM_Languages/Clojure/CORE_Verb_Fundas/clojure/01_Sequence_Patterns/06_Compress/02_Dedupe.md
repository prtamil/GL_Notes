# Pattern 18 — Dedupe

## Mental Model

Remove **consecutive duplicate elements** while keeping duplicates that appear later.

Unlike **Distinct**, which removes **all duplicates**, **Dedupe** only compresses **runs of repeated values**.

---

## Relationship to Cognitive Verb

```text
Compress
    ↓
Dedupe
```

Dedupe is a **Compress** pattern because it reduces repeated **adjacent** values into a single value.

---

## Clojure Functions & Common Idioms

|Variation|Example|Common Clojure|
|---|---|---|
|Remove Consecutive Duplicates|`1 2 3 2`|`dedupe`|
|Dedupe After Sorting|Global dedupe|`sort` + `dedupe`|
|Dedupe by Key|Adjacent equal keys|`partition-by` + `map first`|
|Compress Runs|`AAAABBCC → ABC`|`dedupe`|
|Count Runs|`AAABB → (AAA) (BB)`|`partition-by identity`|

> **Note:** `dedupe` only removes **adjacent duplicates**. If duplicate values are separated by other values, they are preserved.

---

## Common Uses

- Compress repeated events
    
- Remove repeated log entries
    
- Sensor noise cleanup
    
- Keyboard repeat filtering
    
- Consecutive state changes
    
- Run compression
    
- Data cleanup
    
- Stream processing
    

---

## Hidden Interview Problems

- Remove adjacent duplicates
    
- Compress repeated characters
    
- Eliminate repeated log messages
    
- Simplify state transitions
    
- Remove duplicate clicks
    
- Run compression
    

---

## Recognition Clues

If you hear:

- Consecutive duplicates
    
- Adjacent duplicates
    
- Runs
    
- Collapse repeated values
    
- Compress repeated characters
    
- Ignore repeated neighbors
    

Think:

**→ Dedupe**

---

## Pattern Summary

|Property|Value|
|---|---|
|Cognitive Verb|Compress|
|Pattern|Dedupe|
|Removes|Adjacent duplicates only|
|Preserves Order|Yes|
|Keeps|First value of each run|
|Primary Use|Run compression|

---

## Clojure Recipe Book

```clojure
;;--------------------------------------------------------
;; Input
;;--------------------------------------------------------

(def xs [1 1 2 2 2 3 2 2 4 4 5])


;;--------------------------------------------------------
;; Remove Consecutive Duplicates
;;--------------------------------------------------------

(dedupe xs)

;; =>
(1 2 3 2 4 5)


;;--------------------------------------------------------
;; Distinct vs Dedupe
;;--------------------------------------------------------

(distinct xs)

;; =>
(1 2 3 4 5)

(dedupe xs)

;; =>
(1 2 3 2 4 5)


;;--------------------------------------------------------
;; Compress Repeated Characters
;;--------------------------------------------------------

(apply str
       (dedupe "aaabbbccccdde"))

;; =>
"abcde"


;;--------------------------------------------------------
;; Partition into Runs
;;--------------------------------------------------------

(partition-by identity xs)

;; =>
((1 1)
 (2 2 2)
 (3)
 (2 2)
 (4 4)
 (5))


;;--------------------------------------------------------
;; Keep First Element of Each Run
;;--------------------------------------------------------

(map first
     (partition-by identity xs))

;; =>
(1 2 3 2 4 5)


;;--------------------------------------------------------
;; Count Run Lengths
;;--------------------------------------------------------

(map count
     (partition-by identity xs))

;; =>
(2 3 1 2 2 1)


;;--------------------------------------------------------
;; Run-Length Encoding (Foundation)
;;--------------------------------------------------------

(map (fn [grp]
       [(first grp) (count grp)])
     (partition-by identity xs))

;; =>
([1 2]
 [2 3]
 [3 1]
 [2 2]
 [4 2]
 [5 1])


;;--------------------------------------------------------
;; Dedupe After Sorting
;;--------------------------------------------------------

(->> xs
     sort
     dedupe)

;; =>
(1 2 3 4 5)


;;--------------------------------------------------------
;; Dedupe by Key
;;--------------------------------------------------------

(def people
  [{:id 1 :name "Alice"}
   {:id 1 :name "Alice"}
   {:id 2 :name "Bob"}
   {:id 2 :name "Bob"}
   {:id 3 :name "Carol"}])

(map first
     (partition-by :id people))

;; =>
({:id 1 :name "Alice"}
 {:id 2 :name "Bob"}
 {:id 3 :name "Carol"})
```