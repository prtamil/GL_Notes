# Pattern 27 — Search All Matches

## Mental Model

Search the entire sequence and **return every element that satisfies a condition**.

Unlike **First Match**, which stops at the first result, **Search All** examines the entire sequence.

---

## Relationship to Cognitive Verb

```text
Search
   ↓
Search All
```

Search All is a **Search** pattern because it finds **every matching element** in the sequence.

---

## Clojure Functions & Common Idioms

|Variation|Example|Common Clojure|
|---|---|---|
|All Matching Elements|All even numbers|`filter`|
|Reject Non-matches|Keep matches|`filter`|
|Remove Matches|Keep non-matches|`remove`|
|Matching Indices|Positions of matches|`keep-indexed`|
|Find Maps|Objects matching predicate|`filter`|
|Search then Transform|Match then project|`filter` + `map`|

> **Note:** `filter` returns every matching element, while `remove` returns every non-matching element.

---

## Common Uses

- Find all errors
    
- Search logs
    
- Query records
    
- Data filtering
    
- Find all users
    
- Validation reports
    
- Event filtering
    
- Database-style queries
    

---

## Hidden Interview Problems

- Find all duplicates
    
- Find all primes
    
- Find all intervals
    
- Return matching records
    
- Search text
    
- Filter dataset
    

---

## Recognition Clues

If you hear:

- All matches
    
- Every occurrence
    
- Find all
    
- Search entire sequence
    
- Matching records
    
- Filter results
    
- Collect matches
    

Think:

**→ Search All**

---

## Pattern Summary

|Property|Value|
|---|---|
|Cognitive Verb|Search|
|Pattern|Search All|
|Stops Early|No|
|Returns|All matching values|
|Preserves Order|Yes|
|Primary Use|Complete search|

---

## Clojure Recipe Book

```clojure
;;--------------------------------------------------------
;; Input
;;--------------------------------------------------------

(def xs [3 7 10 12 15 20])


;;--------------------------------------------------------
;; All Even Numbers
;;--------------------------------------------------------

(filter even? xs)

;; =>
;; (10 12 20)


;;--------------------------------------------------------
;; All Numbers Greater Than 10
;;--------------------------------------------------------

(filter #(< 10 %) xs)

;; =>
;; (12 15 20)


;;--------------------------------------------------------
;; Remove Even Numbers
;;--------------------------------------------------------

(remove even? xs)

;; =>
;; (3 7 15)


;;--------------------------------------------------------
;; Find Matching Indices
;;--------------------------------------------------------

(keep-indexed
  (fn [i x]
    (when (even? x) i))
  xs)

;; =>
;; (2 3 5)


;;--------------------------------------------------------
;; Find Matching Maps
;;--------------------------------------------------------

(def users
  [{:id 1 :active true}
   {:id 2 :active false}
   {:id 3 :active true}])

(filter :active users)

;; =>
;; ({:id 1 :active true}
 ;; {:id 3 :active true})


;;--------------------------------------------------------
;; Search then Transform
;;--------------------------------------------------------

(->> xs
     (filter even?)
     (map #(* % 10)))

;; =>
;; (100 120 200)


;;--------------------------------------------------------
;; Compare some vs filter
;;--------------------------------------------------------

(some #(when (even? %) %) xs)

;; =>
;; 10

(filter even? xs)

;; =>
;; (10 12 20)


;;--------------------------------------------------------
;; Find All Non-empty Strings
;;--------------------------------------------------------

(filter seq
        ["" "hello" "" "world"])

;; =>
;; ("hello" "world")


;;--------------------------------------------------------
;; Find All Matching Keywords
;;--------------------------------------------------------

(filter #{:error :fatal}
        [:info :error :debug :fatal :warn])

;; =>
;; (:error :fatal)


;;--------------------------------------------------------
;; Search with keep
;;--------------------------------------------------------

(keep #(when (even? %)
         (* % 10))
      xs)

;; =>
;; (100 120 200)
```

---

### Readable Clojure Functions

```clojure
(defn matching-values [predicate values]
  (filter predicate values))

(defn matching-indices [predicate values]
  (keep-indexed (fn [index value]
                  (when (predicate value) index))
                values))

(defn count-matches [predicate values]
  (count (filter predicate values)))

(defn filter-by-mask [mask values]
  (keep (fn [[keep? value]]
          (when keep? value))
        (map vector mask values)))

(defn duplicate-values [values]
  (let [counts (frequencies values)]
    (filter (fn [value] (> (get counts value) 1))
            (distinct values))))

(defn prime? [number]
  (and (integer? number)
       (>= number 2)
       (not-any? (fn [divisor]
                   (zero? (mod number divisor)))
                 (range 2 (inc (long (Math/sqrt number)))))))

(defn overlaps? [[start-a end-a] [start-b end-b]]
  ;; Half-open intervals: [start, end).
  (and (< start-a end-b)
       (< start-b end-a)))

(matching-indices even? [3 4 7 8 10])
;; => (1 3 4)

(count-matches pos? [-2 0 3 4])
;; => 2

(filter-by-mask [true false true] [:a :b :c])
;; => (:a :c)

(duplicate-values [1 2 1 3 2 2])
;; => (1 2)

(filter prime? (range 20))
;; => (2 3 5 7 11 13 17 19)
```

For membership tests against many candidates, build a set once and use it as the predicate: `(filter allowed? xs)`. Regular-expression searches use `re-seq`, which returns every non-overlapping match lazily.

### Memory Hooks

|You want|You reach for|
|---|---|
|all matching values|`filter`|
|all nonmatching values|`remove`|
|transform successful items|`keep`|
|matching positions|`keep-indexed`|
|a count only|a filtering transducer|
|membership filtering|a set as a function|
|all regex matches|`re-seq`|

### Key Insight

Search-all preserves every match. Keep the pipeline lazy when the consumer can use a prefix. Use a transducer when you need only a summary.
