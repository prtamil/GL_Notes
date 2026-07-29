# Pattern 28 — Nearest Match

## Mental Model

Find the element **closest to a target value** according to some distance or similarity measure.

Unlike **First Match**, which stops at the first valid element, or **Search All**, which returns every match, **Nearest Match** searches for the **best (closest)** match.

---

## Relationship to Cognitive Verb

```text
Search
   ↓
Nearest Match
```

Nearest Match is a **Search** pattern because it searches the sequence to find the element with the **minimum distance** from a target.

---

## Clojure Functions & Common Idioms

|Variation|Example|Common Clojure|
|---|---|---|
|Nearest Number|Closest to `23`|`apply min-key`|
|Nearest by Property|Closest age|`min-key`|
|Minimum Distance|Smallest difference|`min-key` + `abs`|
|Maximum Similarity|Best score|`max-key`|
|Nearest Object|Closest point|`min-key`|
|Top K Nearest|Closest N items|`sort-by` + `take`|

> **Note:** Clojure has no dedicated nearest function. The common idiom is `min-key` with a distance function.

---

## Common Uses

- Nearest value lookup
    
- Closest point
    
- Nearest timestamp
    
- Best recommendation
    
- Fuzzy matching
    
- Nearest sensor reading
    
- Spatial search
    
- AI nearest neighbor
    

---

## Hidden Interview Problems

- Closest number to target
    
- K nearest numbers
    
- Closest point to origin
    
- Nearest timestamp
    
- Closest interval
    
- Nearest neighbor
    

---

## Recognition Clues

If you hear:

- Closest
    
- Nearest
    
- Minimum distance
    
- Best match
    
- Similarity
    
- Nearest neighbor
    
- Closest value
    

Think:

**→ Nearest Match**

---

## Pattern Summary

|Property|Value|
|---|---|
|Cognitive Verb|Search|
|Pattern|Nearest Match|
|Stops Early|No|
|Returns|Best matching element|
|Comparison|Distance / Similarity|
|Primary Use|Approximate search|

---

## Clojure Recipe Book

```clojure
;;--------------------------------------------------------
;; Input
;;--------------------------------------------------------

(def xs [10 15 22 30 42 55])


;;--------------------------------------------------------
;; Nearest Number to 25
;;--------------------------------------------------------

(apply min-key
       #(Math/abs (- % 25))
       xs)

;; => 22


;;--------------------------------------------------------
;; Nearest Number to 40
;;--------------------------------------------------------

(apply min-key
       #(Math/abs (- % 40))
       xs)

;; => 42


;;--------------------------------------------------------
;; Farthest Number
;;--------------------------------------------------------

(apply max-key
       #(Math/abs (- % 25))
       xs)

;; => 55


;;--------------------------------------------------------
;; Nearest Object by Property
;;--------------------------------------------------------

(def people
  [{:name "Alice" :age 24}
   {:name "Bob"   :age 31}
   {:name "Carol" :age 27}])

(apply min-key
       #(Math/abs (- (:age %) 26))
       people)

;; =>
{:name "Carol" :age 27}


;;--------------------------------------------------------
;; Top 3 Nearest Values
;;--------------------------------------------------------

(take 3
      (sort-by #(Math/abs (- % 25))
               xs))

;; =>
(22 30 15)


;;--------------------------------------------------------
;; Nearest Timestamp
;;--------------------------------------------------------

(def times [100 140 180 250])

(apply min-key
       #(Math/abs (- % 160))
       times)

;; => 180


;;--------------------------------------------------------
;; Closest Point to Origin
;;--------------------------------------------------------

(def points [[3 4] [1 2] [5 5]])

(apply min-key
       (fn [[x y]]
         (+ (* x x) (* y y)))
       points)

;; =>
[1 2]


;;--------------------------------------------------------
;; Highest Score (Maximum Similarity)
;;--------------------------------------------------------

(def scores
  [{:name "A" :score 0.81}
   {:name "B" :score 0.95}
   {:name "C" :score 0.76}])

(apply max-key :score scores)

;; =>
{:name "B" :score 0.95}


;;--------------------------------------------------------
;; Compare First vs Nearest
;;--------------------------------------------------------

(first xs)

;; =>
10

(apply min-key
       #(Math/abs (- % 25))
       xs)

;; =>
22
```