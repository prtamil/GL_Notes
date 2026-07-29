# Pattern 30 — Prefix Sum

## Mental Model

Precompute cumulative sums so that **any range sum can be answered in O(1)** instead of summing repeatedly.

Unlike **Running Sum**, whose goal is to observe cumulative progress, **Prefix Sum** is built as a **data structure for fast queries**.

---

## Relationship to Cognitive Verb

```text
Scan
   ↓
Prefix Sum
```

Prefix Sum is a **Scan** pattern because it scans the sequence once, storing cumulative information for future use.

---

## Clojure Functions & Common Idioms

|Variation|Example|Common Clojure|
|---|---|---|
|Build Prefix Sum|`[1 3 6 10]`|`reductions +`|
|Prefix with Zero|`[0 1 3 6 10]`|`cons` + `reductions`|
|Range Sum Query|Sum from `i` to `j`|`nth` + subtraction|
|Prefix Product|Running multiplication|`reductions *`|
|Generic Prefix State|Custom cumulative state|`reductions`|

> **Note:** Prefix Sum is usually implemented using `reductions +`, often with a leading `0` to simplify range queries.

---

## Common Uses

- Range sum queries
    
- Sliding window optimization
    
- Image integral tables
    
- Dynamic programming
    
- Financial reports
    
- Analytics dashboards
    
- Histogram preprocessing
    
- Competitive programming
    

---

## Hidden Interview Problems

- Range Sum Query
    
- Subarray Sum Equals K
    
- Count Subarrays
    
- Continuous Subarray Sum
    
- Maximum Sum Rectangle (2D Prefix Sum)
    
- Integral Image
    

---

## Recognition Clues

If you hear:

- Range sum
    
- Sum between indices
    
- Many sum queries
    
- Precompute
    
- Cumulative array
    
- O(1) range query
    
- Prefix table
    

Think:

**→ Prefix Sum**

---

## Pattern Summary

|Property|Value|
|---|---|
|Cognitive Verb|Scan|
|Pattern|Prefix Sum|
|Built Once|Yes|
|Query Time|O(1)|
|Build Time|O(n)|
|Primary Use|Fast range queries|

---

## Clojure Recipe Book

```clojure
;;--------------------------------------------------------
;; Input
;;--------------------------------------------------------

(def xs [2 4 6 8 10])


;;--------------------------------------------------------
;; Basic Prefix Sum
;;--------------------------------------------------------

(reductions + xs)

;; =>
(2 6 12 20 30)


;;--------------------------------------------------------
;; Prefix Sum with Leading Zero
;;--------------------------------------------------------

(def prefix
  (vec (cons 0 (reductions + xs))))

prefix

;; =>
[0 2 6 12 20 30]


;;--------------------------------------------------------
;; Range Sum (i..j)
;;--------------------------------------------------------

(defn range-sum [prefix i j]
  (- (nth prefix (inc j))
     (nth prefix i)))

(range-sum prefix 1 3)

;; =>
18

;; (4 + 6 + 8)


;;--------------------------------------------------------
;; Multiple Range Queries
;;--------------------------------------------------------

(map #(apply range-sum prefix %)
     [[0 2]
      [1 3]
      [2 4]])

;; =>
(12 18 24)


;;--------------------------------------------------------
;; Prefix Product
;;--------------------------------------------------------

(reductions * [2 3 4 5])

;; =>
(2 6 24 120)


;;--------------------------------------------------------
;; Running XOR (Prefix XOR)
;;--------------------------------------------------------

(reductions bit-xor [1 2 3 4])

;; =>
(1 3 0 4)


;;--------------------------------------------------------
;; Running Maximum
;;--------------------------------------------------------

(reductions max xs)

;; =>
(2 4 6 8 10)


;;--------------------------------------------------------
;; Difference Between Running Sum and Prefix Sum
;;--------------------------------------------------------

(reductions + xs)

;; =>
(2 6 12 20 30)

;; Prefix Sum Data Structure

(def prefix
  (vec (cons 0 (reductions + xs))))

;; =>
[0 2 6 12 20 30]

;; Query sum of indices 2..4

(range-sum prefix 2 4)

;; =>
24


;;--------------------------------------------------------
;; Custom Prefix State
;;--------------------------------------------------------

(reductions
  (fn [{:keys [sum]} x]
    {:sum (+ sum x)})
  {:sum 0}
  xs)

;; =>
({:sum 0}
 {:sum 2}
 {:sum 6}
 {:sum 12}
 {:sum 20}
 {:sum 30})
```