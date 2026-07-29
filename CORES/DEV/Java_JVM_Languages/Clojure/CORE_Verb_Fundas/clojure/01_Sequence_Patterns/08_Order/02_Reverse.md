# Pattern 24 — Reverse

## Mental Model

Traverse or view a sequence in the **opposite order**, making the last element first and the first element last.

Unlike **Sort**, which orders by value, **Reverse** simply flips the existing order.

---

## Relationship to Cognitive Verb

```text
Order
   ↓
Reverse
```

Reverse is an **Order** pattern because it changes the ordering of elements without changing the elements themselves.

---

## Clojure Functions & Common Idioms

|Variation|Example|Common Clojure|
|---|---|---|
|Reverse Sequence|`3 2 1`|`reverse`|
|Reverse Then Process|Process backwards|`reverse` + `map`|
|Reverse String|`"olleh"`|`reverse` + `apply str`|
|Reverse Sorted Order|Largest → Smallest|`reverse` + `sort`|
|Reverse During Reduce|Build reversed sequence|`reduce` + `conj`|
|Reverse Vector Efficiently|Vector output|`into [] (reverse xs)`|

> **Note:** `reverse` preserves all elements and only changes their order.

---

## Common Uses

- Undo history
    
- Stack processing
    
- Reverse traversal
    
- Text reversal
    
- Backtracking
    
- Reverse chronological order
    
- Reverse animations
    
- Data transformation
    

---

## Hidden Interview Problems

- Reverse an array
    
- Reverse a string
    
- Check palindrome
    
- Reverse linked list
    
- Reverse words
    
- Process newest first
    

---

## Recognition Clues

If you hear:

- Reverse
    
- Backwards
    
- Last to first
    
- Flip order
    
- Opposite direction
    
- Undo order
    
- Reverse traversal
    
- Mirror
    

Think:

**→ Reverse**

---

## Pattern Summary

|Property|Value|
|---|---|
|Cognitive Verb|Order|
|Pattern|Reverse|
|Rearranges Elements|Yes|
|Preserves All Elements|Yes|
|Changes Values|No|
|Primary Use|Reverse ordering|

---

## Clojure Recipe Book

```clojure
;;--------------------------------------------------------
;; Input
;;--------------------------------------------------------

(def xs [1 2 3 4 5])


;;--------------------------------------------------------
;; Reverse Sequence
;;--------------------------------------------------------

(reverse xs)

;; =>
(5 4 3 2 1)


;;--------------------------------------------------------
;; Reverse Vector
;;--------------------------------------------------------

(into [] (reverse xs))

;; =>
[5 4 3 2 1]


;;--------------------------------------------------------
;; Reverse String
;;--------------------------------------------------------

(apply str
       (reverse "clojure"))

;; =>
"erujolc"


;;--------------------------------------------------------
;; Reverse Then Map
;;--------------------------------------------------------

(map inc
     (reverse xs))

;; =>
(6 5 4 3 2)


;;--------------------------------------------------------
;; Reverse Sorted Order
;;--------------------------------------------------------

(reverse
 (sort xs))

;; =>
(5 4 3 2 1)

;; Equivalent

(sort > xs)

;; =>
(5 4 3 2 1)


;;--------------------------------------------------------
;; Build Reverse with reduce
;;--------------------------------------------------------

(reduce conj
        '()
        xs)

;; =>
(5 4 3 2 1)


;;--------------------------------------------------------
;; Reverse Nested Sequences
;;--------------------------------------------------------

(map reverse
     [[1 2 3]
      [4 5]
      [6 7 8]])

;; =>
((3 2 1)
 (5 4)
 (8 7 6))


;;--------------------------------------------------------
;; Palindrome Check
;;--------------------------------------------------------

(let [s "level"]
  (= (seq s)
     (reverse s)))

;; =>
true


;;--------------------------------------------------------
;; Reverse Words
;;--------------------------------------------------------

(clojure.string/join
 " "
 (reverse
  (clojure.string/split
   "one two three"
   #" ")))

;; =>
"three two one"


;;--------------------------------------------------------
;; Reverse with Indices
;;--------------------------------------------------------

(map-indexed vector
             (reverse xs))

;; =>
([0 5]
 [1 4]
 [2 3]
 [3 2]
 [4 1])
```