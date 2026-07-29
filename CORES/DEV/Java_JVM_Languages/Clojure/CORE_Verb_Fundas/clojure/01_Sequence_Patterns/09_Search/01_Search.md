# Pattern 26 — First Match

## Mental Model

Traverse a sequence until the **first element satisfying a condition** is found, then **stop immediately**.

Unlike **Filter**, which returns **all matching elements**, **First Match** returns only the first one.

---

## Relationship to Cognitive Verb

```text
Search
   ↓
First Match
```

First Match is a **Search** pattern because it searches until a match is found, then terminates.

---

## Clojure Functions & Common Idioms

|Variation|Example|Common Clojure|
|---|---|---|
|First Matching Element|First even|`some`|
|First Element Satisfying Predicate|`> 10`|`some`|
|First Truthy Value|First non-`nil`|`some`|
|Find Position|Index of first match|`keep-indexed`|
|First Matching Map|Find by `:id`|`some`|
|Search Then Transform|Return computed value|`some`|

> **Note:** `some` stops as soon as a truthy value is returned, making it ideal for early termination.

---

## Common Uses

- Find a user
    
- Find first error
    
- Lookup configuration
    
- Find first available slot
    
- Search logs
    
- Validation
    
- Rule matching
    
- Event detection
    

---

## Hidden Interview Problems

- Find first duplicate
    
- First non-repeating character
    
- First missing value
    
- Search sorted array
    
- First valid record
    
- Find target element
    

---

## Recognition Clues

If you hear:

- First match
    
- Find first
    
- Stop when found
    
- Exists
    
- Search until
    
- First valid
    
- First occurrence satisfying
    

Think:

**→ First Match**

---

## Pattern Summary

|Property|Value|
|---|---|
|Cognitive Verb|Search|
|Pattern|First Match|
|Stops Early|Yes|
|Returns|First matching value|
|Preserves Order|Yes|
|Primary Use|Early search|

---

## Clojure Recipe Book

```clojure
;;--------------------------------------------------------
;; Input
;;--------------------------------------------------------

(def xs [3 7 10 12 15 20])


;;--------------------------------------------------------
;; First Even Number
;;--------------------------------------------------------

(some #(when (even? %) %) xs)

;; => 10


;;--------------------------------------------------------
;; First Number Greater Than 10
;;--------------------------------------------------------

(some #(when (> % 10) %) xs)

;; => 12


;;--------------------------------------------------------
;; Does Any Match?
;;--------------------------------------------------------

(boolean
  (some even? xs))

;; => true


;;--------------------------------------------------------
;; First Truthy Value
;;--------------------------------------------------------

(some identity
      [nil false nil "hello" :x])

;; => "hello"


;;--------------------------------------------------------
;; Find First Map by Property
;;--------------------------------------------------------

(def users
  [{:id 1 :name "Alice"}
   {:id 2 :name "Bob"}
   {:id 3 :name "Carol"}])

(some #(when (= 2 (:id %)) %) users)

;; =>
{:id 2 :name "Bob"}


;;--------------------------------------------------------
;; Find Index of First Match
;;--------------------------------------------------------

(first
 (keep-indexed
   (fn [i x]
     (when (even? x) i))
   xs))

;; => 2


;;--------------------------------------------------------
;; Return a Computed Value
;;--------------------------------------------------------

(some #(when (even? %)
         (* % 10))
      xs)

;; => 100


;;--------------------------------------------------------
;; Compare filter vs some
;;--------------------------------------------------------

(filter even? xs)

;; =>
(10 12 20)

(some #(when (even? %) %) xs)

;; =>
10


;;--------------------------------------------------------
;; Find First Non-empty String
;;--------------------------------------------------------

(some #(when (seq %) %)
      ["" "" "hello" "world"])

;; =>
"hello"


;;--------------------------------------------------------
;; First Matching Keyword
;;--------------------------------------------------------

(some #{:error}
      [:info :debug :warn :error :fatal])

;; =>
:error
```