# Pattern 29 — Running Sum (Prefix Sum)

## Mental Model

Compute the **cumulative total** at every step of a sequence.

Instead of returning only the final sum, **Running Sum** keeps every intermediate result.

---

## Relationship to Cognitive Verb

```text
Scan
   ↓
Running Sum (Prefix Sum)
```

Running Sum is a **Scan** pattern because it scans the sequence while carrying forward an accumulated state.

---

## Clojure Functions & Common Idioms

|Variation|Example|Common Clojure|
|---|---|---|
|Running Sum|`1 3 6 10`|`reductions +`|
|Running Product|`1 2 6 24`|`reductions *`|
|Running Maximum|`3 5 5 8`|`reductions max`|
|Running Minimum|`5 3 3 2`|`reductions min`|
|Running String|`"a" "ab" "abc"`|`reductions str`|
|Running Collection|Growing vector|`reductions conj []`|
|Custom Running State|Running balance|`reductions`|

> **Note:** `reduce` returns the **final result**, while `reductions` returns **every intermediate result**.

---

## Common Uses

- Prefix sums
    
- Running balance
    
- Progress tracking
    
- Cumulative statistics
    
- Financial ledgers
    
- Time series
    
- Dynamic programming
    
- Streaming analytics
    

---

## Hidden Interview Problems

- Prefix sum array
    
- Range sum queries
    
- Running average
    
- Running maximum
    
- Cumulative balance
    
- Scan algorithms
    

---

## Recognition Clues

If you hear:

- Running
    
- Cumulative
    
- Prefix
    
- So far
    
- Up to this point
    
- Accumulate while traversing
    
- Rolling total
    

Think:

**→ Running Sum (Prefix Sum)**

---

## Pattern Summary

|Property|Value|
|---|---|
|Cognitive Verb|Scan|
|Pattern|Running Sum (Prefix Sum)|
|Output Size|Same as input|
|Keeps Intermediate Results|Yes|
|Builds State|Yes|
|Primary Use|Cumulative computation|

---

## Clojure Recipe Book

```clojure
;;--------------------------------------------------------
;; Input
;;--------------------------------------------------------

(def xs [1 2 3 4 5])


;;--------------------------------------------------------
;; Running Sum
;;--------------------------------------------------------

(reductions + xs)

;; =>
;; (1 3 6 10 15)


;;--------------------------------------------------------
;; Running Product
;;--------------------------------------------------------

(reductions * xs)

;; =>
;; (1 2 6 24 120)


;;--------------------------------------------------------
;; Running Maximum
;;--------------------------------------------------------

(reductions max [3 1 5 2 8 4])

;; =>
;; (3 3 5 5 8 8)


;;--------------------------------------------------------
;; Running Minimum
;;--------------------------------------------------------

(reductions min [5 7 3 8 2 6])

;; =>
;; (5 5 3 3 2 2)


;;--------------------------------------------------------
;; Running String
;;--------------------------------------------------------

(reductions str ["a" "b" "c" "d"])

;; =>
;; ("a"
 ;; "ab"
 ;; "abc"
 ;; "abcd")


;;--------------------------------------------------------
;; Growing Collection
;;--------------------------------------------------------

(reductions conj [] [:a :b :c])

;; =>
;; ([]
 ;; [:a]
 ;; [:a :b]
 ;; [:a :b :c])


;;--------------------------------------------------------
;; Running Balance
;;--------------------------------------------------------

(reductions + 100 [20 -10 50 -30])

;; =>
;; (100
 ;; 120
 ;; 110
 ;; 160
 ;; 130)


;;--------------------------------------------------------
;; Running Average
;;--------------------------------------------------------

(map-indexed
  (fn [i sum]
    (/ sum (inc i)))
  (reductions + xs))

;; =>
;; (1
 ;; 3/2
 ;; 2
 ;; 5/2
 ;; 3)


;;--------------------------------------------------------
;; Compare reduce vs reductions
;;--------------------------------------------------------

(reduce + xs)

;; =>
;; 15

(reductions + xs)

;; =>
;; (1 3 6 10 15)


;;--------------------------------------------------------
;; Custom Running State
;;--------------------------------------------------------

(reductions
  (fn [{:keys [sum]} x]
    {:sum (+ sum x)})
  {:sum 0}
  xs)

;; =>
;; ({:sum 0}
 ;; {:sum 1}
 ;; {:sum 3}
 ;; {:sum 6}
 ;; {:sum 10}
 ;; {:sum 15})
```

---

### Readable Clojure Functions

```clojure
(defn running-sums [values]
  (rest (reductions + 0 values)))

(defn running-products [values]
  (rest (reductions * 1 values)))

(defn running-balances [opening transactions]
  (reductions + opening transactions))

(defn running-averages [values]
  (->> values
       (reductions (fn [{:keys [sum count]} value]
                     {:sum (+ sum value)
                      :count (inc count)})
                   {:sum 0 :count 0})
       rest
       (map (fn [{:keys [sum count]}]
              (/ sum count)))))

(defn adjacent-differences [values]
  (map - (rest values) values))

(defn maximum-profit [prices]
  (when-let [[first-price & later] (seq prices)]
    (:best
      (reduce (fn [{:keys [minimum best]} price]
                {:minimum (min minimum price)
                 :best (max best (- price minimum))})
              {:minimum first-price :best 0}
              later))))

(defn cumulative-distribution [histogram]
  (let [total (reduce + 0 (vals histogram))]
    (when (pos? total)
      (->> histogram
           (sort-by key)
           (reductions (fn [{:keys [count]} [value frequency]]
                         {:value value
                          :count (+ count frequency)})
                       {:value nil :count 0})
           rest
           (map (fn [{:keys [value count]}]
                  [value (/ count total)]))))))

(running-balances 100 [20 -5 -30 10])
;; => (100 120 115 85 95)

(running-averages [2 4 8 10])
;; => (2 3 14/3 6)

(adjacent-differences [3 8 10 7])
;; => (5 2 -3)

(maximum-profit [7 1 5 3 6 4])
;; => 5
```

Floating-point addition is not associative, so long scans of doubles can accumulate rounding drift. Use ratios, integers, `bigdec`, or a compensated numeric algorithm when exactness matters.

### Memory Hooks

|You want|You reach for|
|---|---|
|running totals|`reductions +`|
|opening balance included|three-argument `reductions`|
|running average|carry both sum and count|
|undo a numeric scan|adjacent differences|
|best profit|running minimum plus best difference|
|streaming scan|consume the lazy result incrementally|

### Key Insight

A scan returns the state after every input, while a reduction returns only the final state. Once the accumulator becomes structured, use a map with named keys so the transition function documents itself.
