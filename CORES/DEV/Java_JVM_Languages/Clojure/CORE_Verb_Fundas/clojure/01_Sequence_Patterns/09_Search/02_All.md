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
(10 12 20)


;;--------------------------------------------------------
;; All Numbers Greater Than 10
;;--------------------------------------------------------

(filter #(< 10 %) xs)

;; =>
(12 15 20)


;;--------------------------------------------------------
;; Remove Even Numbers
;;--------------------------------------------------------

(remove even? xs)

;; =>
(3 7 15)


;;--------------------------------------------------------
;; Find Matching Indices
;;--------------------------------------------------------

(keep-indexed
  (fn [i x]
    (when (even? x) i))
  xs)

;; =>
(2 3 5)


;;--------------------------------------------------------
;; Find Matching Maps
;;--------------------------------------------------------

(def users
  [{:id 1 :active true}
   {:id 2 :active false}
   {:id 3 :active true}])

(filter :active users)

;; =>
({:id 1 :active true}
 {:id 3 :active true})


;;--------------------------------------------------------
;; Search then Transform
;;--------------------------------------------------------

(->> xs
     (filter even?)
     (map #(* % 10)))

;; =>
(100 120 200)


;;--------------------------------------------------------
;; Compare some vs filter
;;--------------------------------------------------------

(some #(when (even? %) %) xs)

;; =>
10

(filter even? xs)

;; =>
(10 12 20)


;;--------------------------------------------------------
;; Find All Non-empty Strings
;;--------------------------------------------------------

(filter seq
        ["" "hello" "" "world"])

;; =>
("hello" "world")


;;--------------------------------------------------------
;; Find All Matching Keywords
;;--------------------------------------------------------

(filter #{:error :fatal}
        [:info :error :debug :fatal :warn])

;; =>
(:error :fatal)


;;--------------------------------------------------------
;; Search with keep
;;--------------------------------------------------------

(keep #(when (even? %)
         (* % 10))
      xs)

;; =>
(100 120 200)
```