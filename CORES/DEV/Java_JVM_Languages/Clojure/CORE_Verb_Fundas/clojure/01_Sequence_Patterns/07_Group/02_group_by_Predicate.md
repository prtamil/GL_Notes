# Pattern 21 — Group By Predicate

## Mental Model

Split a sequence into groups based on whether elements **satisfy one or more conditions**.

Unlike **Group By Key**, where the key can be any computed value, **Group By Predicate** groups according to **boolean conditions**.

---

## Relationship to Cognitive Verb

```text
Group
   ↓
Group By Predicate
```

Group By Predicate is a **Group** pattern where each predicate defines a category.

---

## Clojure Functions & Common Idioms

|Variation|Example|Common Clojure|
|---|---|---|
|True / False Groups|Even / Odd|`group-by predicate`|
|Pass / Fail|Score ≥ 50|`group-by`|
|Positive / Negative|Numbers|`group-by pos?`|
|Nil / Non-nil|Missing values|`group-by nil?`|
|Blank / Non-blank|Strings|`group-by clojure.string/blank?`|
|Multi-category Predicate|Small / Medium / Large|`group-by` + `cond`|

> **Note:** A predicate normally creates **two groups** (`true` and `false`). For more than two categories, return labels such as `:small`, `:medium`, and `:large` instead of booleans.

---

## Common Uses

- Pass / Fail classification
    
- Valid / Invalid records
    
- Active / Inactive users
    
- Positive / Negative values
    
- Error / Success logs
    
- Data validation
    
- Rule engines
    
- Filtering pipelines
    

---

## Hidden Interview Problems

- Partition by condition
    
- Separate positive and negative numbers
    
- Split valid and invalid records
    
- Categorize values by thresholds
    
- Bucket data into ranges
    
- Classify events
    

---

## Recognition Clues

If you hear:

- Pass or fail
    
- Valid or invalid
    
- True or false
    
- Meets condition
    
- Categorize by rule
    
- Threshold
    
- Bucket by condition
    

Think:

**→ Group By Predicate**

---

## Pattern Summary

|Property|Value|
|---|---|
|Cognitive Verb|Group|
|Pattern|Group By Predicate|
|Output|Map of predicate result → collection|
|Key Source|Boolean or Category|
|Preserves Group Order|Yes|
|Primary Use|Rule-based grouping|

---

## Clojure Recipe Book

```clojure
;;--------------------------------------------------------
;; Input
;;--------------------------------------------------------

(def xs [-3 -2 -1 0 1 2 3 4])


;;--------------------------------------------------------
;; Group Even / Odd
;;--------------------------------------------------------

(group-by even? xs)

;; =>
;; {true  [-2 0 2 4]
 ;; false [-3 -1 1 3]}


;;--------------------------------------------------------
;; Group Positive / Non-positive
;;--------------------------------------------------------

(group-by pos? xs)

;; =>
;; {true  [1 2 3 4]
 ;; false [-3 -2 -1 0]}


;;--------------------------------------------------------
;; Group Nil / Non-nil
;;--------------------------------------------------------

(group-by nil?
          [1 nil 2 nil 3])

;; =>
;; {false [1 2 3]
 ;; true  [nil nil]}


;;--------------------------------------------------------
;; Group Strings by Blank?
;;--------------------------------------------------------

(require '[clojure.string :as str])

(group-by str/blank?
          ["hello" "" " " "world"])

;; =>
;; {false ["hello" "world"]
 ;; true  ["" " "]}


;;--------------------------------------------------------
;; Pass / Fail
;;--------------------------------------------------------

(def scores [85 42 90 61 35 78])

(group-by #(>= % 50) scores)

;; =>
;; {true  [85 90 61 78]
 ;; false [42 35]}


;;--------------------------------------------------------
;; Multi-category Classification
;;--------------------------------------------------------

(group-by
  #(cond
     (< % 10) :small
     (< % 20) :medium
     :else    :large)
  [3 8 12 17 21 30])

;; =>
;; {:small  [3 8]
 ;; :medium [12 17]
 ;; :large  [21 30]}


;;--------------------------------------------------------
;; Valid / Invalid Records
;;--------------------------------------------------------

(def users
  [{:id 1 :email "a@test.com"}
   {:id 2 :email nil}
   {:id 3 :email "b@test.com"}])

(group-by #(some? (:email %))
          users)

;; =>
;; {true
;;  [{:id 1 :email "a@test.com"}
;;   {:id 3 :email "b@test.com"}]
;;  false
;;  [{:id 2 :email nil}]}


;;--------------------------------------------------------
;; Group by Range
;;--------------------------------------------------------

(group-by
  #(cond
     (< % 0) :negative
     (zero? %) :zero
     :else :positive)
  xs)

;; =>
;; {:negative [-3 -2 -1]
 ;; :zero [0]
 ;; :positive [1 2 3 4]}
```

> **Note:** Clojure uses `group-by` for both patterns. **Group By Key** uses a computed value. **Group By Predicate** uses a rule or condition.

---

### Readable Clojure Functions

```clojure
(defn partition-by-predicate [predicate values]
  (reduce (fn [result value]
            (update result
                    (if (predicate value) :matches :non-matches)
                    conj
                    value))
          {:matches [] :non-matches []}
          values))

(defn classify-sign [number]
  (cond
    (neg? number) :negative
    (zero? number) :zero
    :else :positive))

(defn classify-score [score]
  (cond
    (>= score 90) :excellent
    (>= score 60) :pass
    :else :fail))

(defn count-by [classifier values]
  (->> values
       (map classifier)
       frequencies))

(defn classify-many [rules value]
  (keep (fn [[label predicate]]
          (when (predicate value) label))
        rules))

(partition-by-predicate even? (range 7))
;; => {:matches [0 2 4 6], :non-matches [1 3 5]}

(group-by classify-sign [-2 -1 0 1 2])
;; => {:negative [-2 -1], :zero [0], :positive [1 2]}

(count-by classify-score [95 72 40 88 51])
;; => {:excellent 1, :pass 2, :fail 2}

(classify-many [[:positive pos?]
                [:even even?]
                [:large #(> % 10)]]
               12)
;; => (:positive :even :large)
```

A true partition assigns every input to exactly one bucket. Independent predicates can overlap, so call that classification rather than partitioning.

### Memory Hooks

|You want|You reach for|
|---|---|
|two realized buckets|a single `reduce`|
|true/false map keys|`group-by pred`|
|named categories|a classifier returning keywords|
|category counts only|classify, then `frequencies`|
|overlapping labels|test every rule with `keep`|
|lazy matching side|`filter` or `remove`|

### Key Insight

A predicate produces two possible keys, while a classifier can produce any number. Give meaningful names to the buckets instead of leaking `true` and `false` into downstream code.
