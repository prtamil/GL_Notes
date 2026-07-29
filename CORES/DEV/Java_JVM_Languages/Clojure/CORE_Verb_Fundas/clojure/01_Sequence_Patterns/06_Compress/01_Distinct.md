# Pattern 17 — Distinct

## Mental Model

Keep **only the first occurrence** of each unique element and discard all later duplicates.

Unlike **Dedupe**, which removes only **consecutive duplicates**, **Distinct** removes duplicates **regardless of where they appear**.

---

## Relationship to Cognitive Verb

```text
Compress
    ↓
Distinct
```

Distinct is a **Compress** pattern because it reduces a sequence by eliminating repeated values.

---

## Clojure Functions & Common Idioms

|Variation|Example|Common Clojure|
|---|---|---|
|Distinct Values|`1 2 3`|`distinct`|
|Distinct by Key|Unique `:id`|`distinct-by` _(custom)_|
|Count Unique Values|`3`|`count` + `distinct`|
|Distinct After Transform|Ignore case|`map` + `distinct`|
|Preserve First Occurrence|Default behavior|`distinct`|
|Convert to Set _(order not preserved)_|`{1 2 3}`|`set`|

> **Note:** `distinct` preserves the **first occurrence and original order**, while `set` removes duplicates but does **not** preserve order.

---

## Common Uses

- Remove duplicate records
    
- Unique IDs
    
- Unique tags
    
- Remove repeated words
    
- Deduplicate search results
    
- Unique user list
    
- Data cleaning
    
- Preprocessing
    

---

## Hidden Interview Problems

- Remove duplicates from an array
    
- Count unique elements
    
- Find unique words
    
- Deduplicate records
    
- Keep first occurrence
    
- Remove repeated IDs
    

---

## Recognition Clues

If you hear:

- Unique
    
- Remove duplicates
    
- Deduplicate
    
- First occurrence
    
- Unique values
    
- Eliminate repeats
    
- Remove repeated items
    

Think:

**→ Distinct**

---

## Pattern Summary

|Property|Value|
|---|---|
|Cognitive Verb|Compress|
|Pattern|Distinct|
|Removes|All duplicate values|
|Preserves Order|Yes|
|Keeps|First occurrence|
|Primary Use|Deduplication|

---

## Clojure Recipe Book

```clojure
;;--------------------------------------------------------
;; Input
;;--------------------------------------------------------

(def xs [1 2 1 3 2 4 1 5])


;;--------------------------------------------------------
;; Distinct Values
;;--------------------------------------------------------

(distinct xs)

;; =>
(1 2 3 4 5)


;;--------------------------------------------------------
;; Count Unique Values
;;--------------------------------------------------------

(count (distinct xs))

;; => 5


;;--------------------------------------------------------
;; Distinct After Transformation
;;--------------------------------------------------------

(distinct
 (map clojure.string/lower-case
      ["Apple" "APPLE" "Banana" "banana"]))

;; =>
("apple" "banana")


;;--------------------------------------------------------
;; Remove Duplicate Characters
;;--------------------------------------------------------

(apply str
       (distinct "banana"))

;; =>
"ban"


;;--------------------------------------------------------
;; Distinct by Key
;;--------------------------------------------------------

(def users
  [{:id 1 :name "Alice"}
   {:id 2 :name "Bob"}
   {:id 1 :name "Alice Updated"}])

(vals
 (into {}
       (map (juxt :id identity))
       users))

;; =>
({:id 1 :name "Alice Updated"}
 {:id 2 :name "Bob"})

;; (Keeps last occurrence. To keep the first occurrence,
;; use a custom reduce.)


;;--------------------------------------------------------
;; Keep First Record by ID
;;--------------------------------------------------------

(reduce
 (fn [acc x]
   (if (contains? acc (:id x))
     acc
     (assoc acc (:id x) x)))
 {}
 users)

;; =>
{1 {:id 1 :name "Alice"}
 2 {:id 2 :name "Bob"}}


;;--------------------------------------------------------
;; Distinct vs Set
;;--------------------------------------------------------

(distinct [3 1 2 3 2 1])

;; =>
(3 1 2)

(set [3 1 2 3 2 1])

;; =>
#{1 2 3}


;;--------------------------------------------------------
;; Unique Words
;;--------------------------------------------------------

(distinct
 ["the" "cat" "the" "sat" "cat"])

;; =>
("the" "cat" "sat")
```