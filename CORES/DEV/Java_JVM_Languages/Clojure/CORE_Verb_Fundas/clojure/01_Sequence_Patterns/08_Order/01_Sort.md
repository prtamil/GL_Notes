# Pattern 23 — Sort

## Mental Model

Rearrange a sequence into a **defined order** based on natural ordering or a custom comparison.

Unlike **Group**, which partitions data, **Sort** produces a **single ordered sequence**.

---

## Relationship to Cognitive Verb

```text
Order
   ↓
Sort
```

Sort is the fundamental **Order** pattern. It establishes a consistent ordering of elements.

---

## Clojure Functions & Common Idioms

|Variation|Example|Common Clojure|
|---|---|---|
|Ascending Sort|`1 2 3`|`sort`|
|Descending Sort|`3 2 1`|`sort >`|
|Sort by Property|Age, Name|`sort-by`|
|Sort by Multiple Keys|Dept then Age|`sort-by` + `juxt`|
|Custom Comparator|Domain-specific order|`sort comparator`|
|Reverse Sorted|Largest first|`reverse` + `sort` or `sort >`|

> **Note:** `sort` compares the values themselves, while `sort-by` computes a key and sorts using that key.

---

## Common Uses

- Leaderboards
    
- Ranking
    
- Alphabetical ordering
    
- Date ordering
    
- Sorting records
    
- Report generation
    
- Preparing binary search
    
- Data presentation
    

---

## Hidden Interview Problems

- Sort an array
    
- Sort intervals
    
- Merge overlapping intervals
    
- Top K elements
    
- Sort by frequency
    
- Custom object sorting
    

---

## Recognition Clues

If you hear:

- Sort
    
- Order
    
- Rank
    
- Ascending
    
- Descending
    
- Alphabetical
    
- Smallest first
    
- Largest first
    

Think:

**→ Sort**

---

## Pattern Summary

|Property|Value|
|---|---|
|Cognitive Verb|Order|
|Pattern|Sort|
|Rearranges Elements|Yes|
|Preserves All Elements|Yes|
|Changes Order|Yes|
|Primary Use|Ordering|

---

## Clojure Recipe Book

```clojure
;;--------------------------------------------------------
;; Input
;;--------------------------------------------------------

(def xs [5 3 1 4 2])


;;--------------------------------------------------------
;; Ascending Sort
;;--------------------------------------------------------

(sort xs)

;; =>
;; (1 2 3 4 5)


;;--------------------------------------------------------
;; Descending Sort
;;--------------------------------------------------------

(sort > xs)

;; =>
;; (5 4 3 2 1)


;;--------------------------------------------------------
;; Sort Strings
;;--------------------------------------------------------

(sort ["pear" "apple" "banana"])

;; =>
;; ("apple" "banana" "pear")


;;--------------------------------------------------------
;; Sort by Length
;;--------------------------------------------------------

(sort-by count
         ["pear" "kiwi" "banana" "fig"])

;; =>
;; ("fig" "pear" "kiwi" "banana")


;;--------------------------------------------------------
;; Sort Maps by Property
;;--------------------------------------------------------

(def employees
  [{:name "Bob"   :age 30}
   {:name "Alice" :age 25}
   {:name "Carol" :age 35}])

(sort-by :age employees)

;; =>
;; ({:name "Alice" :age 25}
 ;; {:name "Bob"   :age 30}
 ;; {:name "Carol" :age 35})


;;--------------------------------------------------------
;; Sort by Multiple Keys
;;--------------------------------------------------------

(def people
  [{:dept :IT :age 30}
   {:dept :HR :age 25}
   {:dept :IT :age 22}
   {:dept :HR :age 35}])

(sort-by (juxt :dept :age) people)

;; =>
;; ({:dept :HR :age 25}
 ;; {:dept :HR :age 35}
 ;; {:dept :IT :age 22}
 ;; {:dept :IT :age 30})


;;--------------------------------------------------------
;; Reverse a Sorted Sequence
;;--------------------------------------------------------

(reverse (sort xs))

;; =>
;; (5 4 3 2 1)


;;--------------------------------------------------------
;; Sort by Frequency
;;--------------------------------------------------------

(sort-by val >
         (frequencies [1 2 1 3 2 1 4]))

;; =>
;; ([1 3]
 ;; [2 2]
 ;; [3 1]
 ;; [4 1])


;;--------------------------------------------------------
;; Custom Comparator
;;--------------------------------------------------------

(sort #(compare (count %2)
                (count %1))
      ["a" "apple" "cat" "banana"])

;; =>
;; ("banana"
 ;; "apple"
 ;; "cat"
 ;; "a")


;;--------------------------------------------------------
;; Stable Multi-step Sort
;;--------------------------------------------------------

(->> people
     (sort-by :age)
     (sort-by :dept))

;; =>
;; ({:dept :HR :age 25}
 ;; {:dept :HR :age 35}
 ;; {:dept :IT :age 22}
 ;; {:dept :IT :age 30})
```

---

### Readable Clojure Functions

```clojure
(defn sort-records [records]
  (sort-by (juxt :department :age) records))

(defn sort-by-score-desc [records]
  (sort-by :score > records))

(defn sort-mixed-directions [records]
  ;; Department ascending, score descending.
  (sort-by (juxt :department (comp - :score)) records))

(defn top-k-by [amount key-fn values]
  (take (max 0 amount)
        (sort-by key-fn > values)))

(defn sort-intervals [intervals]
  (sort-by (juxt first second) intervals))

(defn sort-heterogeneous [values]
  (sort-by (fn [value]
             (cond
               (number? value) [0 value]
               (string? value) [1 value]
               (keyword? value) [2 value]
               :else [3 (pr-str value)]))
           values))

(sort-records [{:department :sales :age 40}
               {:department :engineering :age 35}
               {:department :engineering :age 25}])
;; => ({:department :engineering, :age 25}
;;     {:department :engineering, :age 35}
;;     {:department :sales, :age 40})

(top-k-by 2 :score [{:name "A" :score 8}
                    {:name "B" :score 10}
                    {:name "C" :score 9}])
;; => ({:name "B", :score 10} {:name "C", :score 9})
```

Clojure's `sort` and `sort-by` are stable. When two keys compare equally, their original relative order is preserved. For very large inputs and very small `k`, use a priority-queue library rather than sorting the entire input.

### Memory Hooks

|You want|You reach for|
|---|---|
|natural ascending order|`sort`|
|descending numbers|`sort >`|
|order by a property|`sort-by`|
|several keys|`sort-by (juxt ...)`|
|mixed numeric directions|negate descending key components|
|top `k` in core Clojure|sort descending, then `take`|
|nonstandard order|a three-way comparator|

### Key Insight

Prefer a key function to a custom comparator. Keys are easier to read and test. `(juxt ...)` creates a multi-field sort key.
