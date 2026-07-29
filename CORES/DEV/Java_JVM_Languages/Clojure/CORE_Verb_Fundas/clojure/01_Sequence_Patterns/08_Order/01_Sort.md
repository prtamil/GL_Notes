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
(1 2 3 4 5)


;;--------------------------------------------------------
;; Descending Sort
;;--------------------------------------------------------

(sort > xs)

;; =>
(5 4 3 2 1)


;;--------------------------------------------------------
;; Sort Strings
;;--------------------------------------------------------

(sort ["pear" "apple" "banana"])

;; =>
("apple" "banana" "pear")


;;--------------------------------------------------------
;; Sort by Length
;;--------------------------------------------------------

(sort-by count
         ["pear" "kiwi" "banana" "fig"])

;; =>
("fig" "pear" "kiwi" "banana")


;;--------------------------------------------------------
;; Sort Maps by Property
;;--------------------------------------------------------

(def employees
  [{:name "Bob"   :age 30}
   {:name "Alice" :age 25}
   {:name "Carol" :age 35}])

(sort-by :age employees)

;; =>
({:name "Alice" :age 25}
 {:name "Bob"   :age 30}
 {:name "Carol" :age 35})


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
({:dept :HR :age 25}
 {:dept :HR :age 35}
 {:dept :IT :age 22}
 {:dept :IT :age 30})


;;--------------------------------------------------------
;; Reverse a Sorted Sequence
;;--------------------------------------------------------

(reverse (sort xs))

;; =>
(5 4 3 2 1)


;;--------------------------------------------------------
;; Sort by Frequency
;;--------------------------------------------------------

(sort-by val >
         (frequencies [1 2 1 3 2 1 4]))

;; =>
([1 3]
 [2 2]
 [3 1]
 [4 1])


;;--------------------------------------------------------
;; Custom Comparator
;;--------------------------------------------------------

(sort #(compare (count %2)
                (count %1))
      ["a" "apple" "cat" "banana"])

;; =>
("banana"
 "apple"
 "cat"
 "a")


;;--------------------------------------------------------
;; Stable Multi-step Sort
;;--------------------------------------------------------

(->> people
     (sort-by :age)
     (sort-by :dept))

;; =>
({:dept :HR :age 25}
 {:dept :HR :age 35}
 {:dept :IT :age 22}
 {:dept :IT :age 30})
```