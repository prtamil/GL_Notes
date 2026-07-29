# Pattern 13 — Stride Traversal

## Mental Model

Traverse a sequence by **skipping a fixed number of elements** between visits.

Instead of visiting every element, you visit **every Nth element**.

---

## Relationship to Cognitive Verb

```text
Traversal
      ↓
Stride Traversal
```

Stride Traversal is a **Traversal** pattern where the traversal advances by a fixed **stride** instead of one element at a time.

---

## Clojure Functions & Common Idioms

|Variation|Example|Common Clojure|
|---|---|---|
|Every 2nd Element|`1 3 5`|`take-nth 2`|
|Every 3rd Element|`1 4 7`|`take-nth 3`|
|Drop then Stride|`2 4 6`|`drop` + `take-nth`|
|Indexed Stride|Keep indices divisible by N|`map-indexed` + `filter`|
|Stride Windows|Window size ≠ Step size|`partition n step`|

> **Note:** Unlike **Jump Window**, which returns **windows**, Stride Traversal returns **individual elements**.

---

## Common Uses

- Downsampling
    
- Periodic sampling
    
- Sparse traversal
    
- Data inspection
    
- Signal processing
    
- Image processing
    
- Frame skipping
    
- Performance optimization
    

---

## Hidden Interview Problems

- Print every Kth element
    
- Sample large datasets
    
- Skip alternate elements
    
- Read every Nth record
    
- Downsample a signal
    
- Sparse matrix traversal
    

---

## Recognition Clues

If you hear:

- Every Nth element
    
- Skip elements
    
- Every other
    
- Every third
    
- Downsample
    
- Sample periodically
    
- Sparse traversal
    
- Stride
    

Think:

**→ Stride Traversal**

---

## Pattern Summary

|Property|Value|
|---|---|
|Cognitive Verb|Traversal|
|Pattern|Stride Traversal|
|Direction|Usually Forward|
|Visits Every Element|No|
|Step Size|Fixed|
|Primary Use|Sparse traversal|

---

## Clojure Recipe Book

```clojure
;;--------------------------------------------------------
;; Input
;;--------------------------------------------------------

(def xs [1 2 3 4 5 6 7 8 9 10])


;;--------------------------------------------------------
;; Every 2nd Element
;;--------------------------------------------------------

(take-nth 2 xs)

;; => (1 3 5 7 9)


;;--------------------------------------------------------
;; Every 3rd Element
;;--------------------------------------------------------

(take-nth 3 xs)

;; => (1 4 7 10)


;;--------------------------------------------------------
;; Skip First, Then Every 2nd
;;--------------------------------------------------------

(take-nth 2 (rest xs))

;; => (2 4 6 8 10)


;;--------------------------------------------------------
;; Drop 3, Then Every 2nd
;;--------------------------------------------------------

(take-nth 2 (drop 3 xs))

;; => (4 6 8 10)


;;--------------------------------------------------------
;; Using Indices
;;--------------------------------------------------------

(->> xs
     (map-indexed vector)
     (filter #(zero? (mod (first %) 2)))
     (map second))

;; => (1 3 5 7 9)


;;--------------------------------------------------------
;; Even Indexed Elements
;;--------------------------------------------------------

(keep-indexed
  (fn [i x]
    (when (even? i) x))
  xs)

;; => (1 3 5 7 9)


;;--------------------------------------------------------
;; Odd Indexed Elements
;;--------------------------------------------------------

(keep-indexed
  (fn [i x]
    (when (odd? i) x))
  xs)

;; => (2 4 6 8 10)


;;--------------------------------------------------------
;; Enumerate Every 3rd Element
;;--------------------------------------------------------

(map-indexed vector
             (take-nth 3 xs))

;; => ([0 1]
;;     [1 4]
;;     [2 7]
;;     [3 10])


;;--------------------------------------------------------
;; Stride with Windows
;;--------------------------------------------------------

(partition 3 2 xs)

;; => ((1 2 3)
;;     (3 4 5)
;;     (5 6 7)
;;     (7 8 9))
```