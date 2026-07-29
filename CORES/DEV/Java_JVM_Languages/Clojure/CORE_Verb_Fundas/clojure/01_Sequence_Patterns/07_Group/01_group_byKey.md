# Pattern 20 — Group By Key

## Mental Model

Partition a sequence into **groups based on a key or property**.

All elements with the same key are collected into the same group.

---

## Relationship to Cognitive Verb

```text
Group
   ↓
Group By Key
```

Group By Key is the fundamental **Group** pattern. Instead of grouping by position, it groups by a **computed key**.

---

## Clojure Functions & Common Idioms

|Variation|Example|Common Clojure|
|---|---|---|
|Group by Property|Age, Department|`group-by`|
|Group by Function|Even/Odd|`group-by`|
|Group by First Letter|`"apple"` → `\a`|`group-by first`|
|Group by Type|String, Number|`group-by type`|
|Group by Boolean|Pass / Fail|`group-by predicate`|
|Group then Transform|Groups → Counts|`group-by` + `map`|

---

## Common Uses

- Group employees by department
    
- Group students by grade
    
- Group orders by customer
    
- Group files by extension
    
- Group words by length
    
- Group numbers by parity
    
- SQL `GROUP BY`
    
- MapReduce
    

---

## Hidden Interview Problems

- Group anagrams
    
- Group words by length
    
- Group numbers by parity
    
- Group objects by property
    
- Bucket records
    
- Categorize events
    

---

## Recognition Clues

If you hear:

- Group by
    
- Bucket
    
- Categorize
    
- Classify
    
- Partition by property
    
- Collect by key
    
- Organize by field
    

Think:

**→ Group By Key**

---

## Pattern Summary

|Property|Value|
|---|---|
|Cognitive Verb|Group|
|Pattern|Group By Key|
|Output|Map of key → collection|
|Key Source|Property or Function|
|Preserves Group Order|Yes|
|Primary Use|Categorization|

---

## Clojure Recipe Book

```clojure
;;--------------------------------------------------------
;; Input
;;--------------------------------------------------------

(def xs [1 2 3 4 5 6 7 8])


;;--------------------------------------------------------
;; Group Even / Odd
;;--------------------------------------------------------

(group-by even? xs)

;; =>
{false [1 3 5 7]
 true  [2 4 6 8]}


;;--------------------------------------------------------
;; Group by Remainder
;;--------------------------------------------------------

(group-by #(mod % 3) xs)

;; =>
{1 [1 4 7]
 2 [2 5 8]
 0 [3 6]}


;;--------------------------------------------------------
;; Group Strings by First Letter
;;--------------------------------------------------------

(group-by first
          ["apple" "ape" "bat" "ball"])

;; =>
{\a ["apple" "ape"]
 \b ["bat" "ball"]}


;;--------------------------------------------------------
;; Group Strings by Length
;;--------------------------------------------------------

(group-by count
          ["a" "to" "cat" "dog" "tree"])

;; =>
{1 ["a"]
 2 ["to"]
 3 ["cat" "dog"]
 4 ["tree"]}


;;--------------------------------------------------------
;; Group Maps by Property
;;--------------------------------------------------------

(def employees
  [{:name "Alice" :dept :IT}
   {:name "Bob"   :dept :HR}
   {:name "Carol" :dept :IT}
   {:name "Dave"  :dept :Sales}])

(group-by :dept employees)

;; =>
{:IT
 [{:name "Alice" :dept :IT}
  {:name "Carol" :dept :IT}]

 :HR
 [{:name "Bob" :dept :HR}]

 :Sales
 [{:name "Dave" :dept :Sales}]}


;;--------------------------------------------------------
;; Count Elements in Each Group
;;--------------------------------------------------------

(into {}
      (map (fn [[k v]]
             [k (count v)]))
      (group-by even? xs))

;; =>
{false 4
 true 4}


;;--------------------------------------------------------
;; Group Then Extract Names
;;--------------------------------------------------------

(into {}
      (map (fn [[k v]]
             [k (map :name v)]))
      (group-by :dept employees))

;; =>
{:IT ("Alice" "Carol")
 :HR ("Bob")
 :Sales ("Dave")}


;;--------------------------------------------------------
;; Group Characters
;;--------------------------------------------------------

(group-by identity
          "banana")

;; =>
{\b [\b]
 \a [\a \a \a]
 \n [\n \n]}


;;--------------------------------------------------------
;; Group by Type
;;--------------------------------------------------------

(group-by type
          [1 "hello" 2.5 :x 7])

;; =>
{java.lang.Long   [1 7]
 java.lang.String ["hello"]
 java.lang.Double [2.5]
 clojure.lang.Keyword [:x]}
```