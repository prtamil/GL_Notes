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
;; (2 6 12 20 30)


;;--------------------------------------------------------
;; Prefix Sum with Leading Zero
;;--------------------------------------------------------

(def prefix
  (vec (cons 0 (reductions + xs))))

prefix

;; =>
;; [0 2 6 12 20 30]


;;--------------------------------------------------------
;; Range Sum [start, end) — half-open like `subvec`
;;--------------------------------------------------------

(defn range-sum-example [prefix start end-exclusive]
  (- (nth prefix end-exclusive)
     (nth prefix start)))

(range-sum-example prefix 1 4)

;; =>
;; 18

;; (4 + 6 + 8)


;;--------------------------------------------------------
;; Multiple Range Queries
;;--------------------------------------------------------

(map #(apply range-sum-example prefix %)
     [[0 2]
      [1 3]
      [2 4]])

;; =>
;; (12 18 24)


;;--------------------------------------------------------
;; Prefix Product
;;--------------------------------------------------------

(reductions * [2 3 4 5])

;; =>
;; (2 6 24 120)


;;--------------------------------------------------------
;; Running XOR (Prefix XOR)
;;--------------------------------------------------------

(reductions bit-xor [1 2 3 4])

;; =>
;; (1 3 0 4)


;;--------------------------------------------------------
;; Running Maximum
;;--------------------------------------------------------

(reductions max xs)

;; =>
;; (2 4 6 8 10)


;;--------------------------------------------------------
;; Difference Between Running Sum and Prefix Sum
;;--------------------------------------------------------

(reductions + xs)

;; =>
;; (2 6 12 20 30)

;; Prefix Sum Data Structure

(def prefix
  (vec (cons 0 (reductions + xs))))

;; =>
;; [0 2 6 12 20 30]

;; Query the half-open range [2, 5)

(range-sum-example prefix 2 5)

;; =>
;; 24


;;--------------------------------------------------------
;; Custom Prefix State
;;--------------------------------------------------------

(reductions
  (fn [{:keys [sum]} x]
    {:sum (+ sum x)})
  {:sum 0}
  xs)

;; =>
;; ({:sum 0}
 ;; {:sum 2}
 ;; {:sum 6}
 ;; {:sum 12}
 ;; {:sum 20}
 ;; {:sum 30})
```

---

### Readable Clojure Functions

```clojure
(defn prefix-sums [values]
  (vec (reductions + 0 values)))

(defn range-sum [prefix start end-exclusive]
  (- (nth prefix end-exclusive)
     (nth prefix start)))

(defn prefix-xors [values]
  (vec (reductions bit-xor 0 values)))

(defn range-xor [prefix start end-exclusive]
  (bit-xor (nth prefix start)
           (nth prefix end-exclusive)))

(defn prefix-counts [predicate values]
  (vec (reductions + 0
                   (map (fn [value]
                          (if (predicate value) 1 0))
                        values))))

(defn subarray-sum-count [target values]
  (loop [remaining (seq values)
         running-sum 0
         prefix-counts {0 1}
         matches 0]
    (if-not remaining
      matches
      (let [next-sum (+ running-sum (first remaining))]
        (recur (next remaining)
               next-sum
               (update prefix-counts next-sum (fnil inc 0))
               (+ matches
                  (get prefix-counts (- next-sum target) 0)))))))

(defn apply-range-additions [size updates]
  ;; Every update is [start end amount] for the half-open range [start,end).
  (let [difference
(reduce (fn [difference [start end amount]]
                  (-> difference
                      (update start + amount)
                      (update end - amount)))
                (vec (repeat (inc size) 0))
                updates)]
    (vec (take size (reductions + difference)))))

(defn add-prefix-cell [matrix table [row column]]
  (let [prefix-row (inc row)
        prefix-column (inc column)
        total (+ (get-in matrix [row column])
                 (get-in table [row prefix-column])
                 (get-in table [prefix-row column])
                 (- (get-in table [row column])))]
    (assoc-in table [prefix-row prefix-column] total)))

(defn prefix-sums-2d [matrix]
  (when-not (or (empty? matrix)
                (apply = (map count matrix)))
    (throw (ex-info "Cannot scan a ragged matrix"
                    {:row-lengths (mapv count matrix)})))
  (let [rows (count matrix)
        cols (if (seq matrix) (count (first matrix)) 0)
        empty-table (vec (repeat (inc rows)
                                 (vec (repeat (inc cols) 0))))]
    (reduce (partial add-prefix-cell matrix)
            empty-table
            (for [row (range rows)
                  column (range cols)]
              [row column]))))

(defn area-sum [prefix top left bottom right]
  ;; Rectangle [top,bottom) × [left,right).
  (- (+ (get-in prefix [bottom right])
        (get-in prefix [top left]))
     (get-in prefix [top right])
     (get-in prefix [bottom left])))

(def p (prefix-sums [2 4 6 8 10]))
(range-sum p 2 5)
;; => 24

(prefix-counts even? [1 2 4 5])
;; => [0 0 1 2 2]

(subarray-sum-count 3 [1 2 1 2])
;; => 3

(apply-range-additions 5 [[1 4 10] [2 5 -3]])
;; => [0 10 7 7 -3]
```

### Memory Hooks

|You want|You reach for|
|---|---|
|build a query table|leading zero plus `reductions`|
|sum `[start,end)`|`prefix[end] - prefix[start]`|
|count a property in a range|prefix-sum 0/1 indicators|
|range XOR|two prefix XORs with `bit-xor`|
|count target-sum subarrays|frequency map of earlier prefix sums|
|fast range updates|difference array, then one scan|
|rectangle sums|2-D prefix table with a zero border|

### Key Insight

The leading zero makes prefix indices identical to half-open sequence boundaries. That removes special cases: every query becomes one subtraction, and the same algebra extends to counts, XOR, difference arrays, and two-dimensional integral images.
