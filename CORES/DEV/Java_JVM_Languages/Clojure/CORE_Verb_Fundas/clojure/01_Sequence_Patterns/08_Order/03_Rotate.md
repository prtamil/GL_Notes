# Pattern 25 — Rotate

## Mental Model

Shift a sequence **left or right**, wrapping the elements around instead of discarding them.

Unlike **Reverse**, which flips the order, **Rotate** preserves the relative order and only changes the starting position.

---

## Relationship to Cognitive Verb

```text
Order
   ↓
Rotate
```

Rotate is an **Order** pattern because it rearranges the sequence by choosing a new starting point while keeping the circular order intact.

---

## Clojure Functions & Common Idioms

|Variation|Example|Common Clojure|
|---|---|---|
|Rotate Left N|`3 4 5 1 2`|`drop` + `take` + `concat`|
|Rotate Right N|`4 5 1 2 3`|`take-last` + `drop-last` + `concat`|
|Infinite Rotation|Circular traversal|`cycle` + `drop` + `take`|
|All Rotations|Every starting position|`map` + `range` + `cycle`|
|Normalize Rotation|Handle large N|`mod`|
|Rotate String|`"cdeab"`|`subs` + `str`|

> **Note:** Clojure has no built-in `rotate` function. It is typically implemented using `take`, `drop`, `concat`, and `cycle`.

---

## Common Uses

- Circular buffers
    
- Ring structures
    
- Round-robin scheduling
    
- Caesar cipher
    
- Array rotation
    
- Playlist rotation
    
- Cyclic algorithms
    
- Game turns
    

---

## Hidden Interview Problems

- Rotate array
    
- Rotate string
    
- Circular queue
    
- Ring buffer
    
- Next player
    
- Circular indexing
    

---

## Recognition Clues

If you hear:

- Rotate
    
- Shift left
    
- Shift right
    
- Wrap around
    
- Circular shift
    
- New starting point
    
- Ring
    
- Cyclic order
    

Think:

**→ Rotate**

---

## Pattern Summary

|Property|Value|
|---|---|
|Cognitive Verb|Order|
|Pattern|Rotate|
|Rearranges Elements|Yes|
|Wrap Around|Yes|
|Preserves Relative Order|Yes|
|Primary Use|Circular reordering|

---

## Clojure Recipe Book

```clojure
;;--------------------------------------------------------
;; Input
;;--------------------------------------------------------

(def xs [1 2 3 4 5])


;;--------------------------------------------------------
;; Rotate Left by 2
;;--------------------------------------------------------

(let [n 2]
  (concat (drop n xs)
          (take n xs)))

;; =>
(3 4 5 1 2)


;;--------------------------------------------------------
;; Rotate Right by 2
;;--------------------------------------------------------

(let [n 2]
  (concat (take-last n xs)
          (drop-last n xs)))

;; =>
(4 5 1 2 3)


;;--------------------------------------------------------
;; Rotate Using cycle
;;--------------------------------------------------------

(take 5
      (drop 2
            (cycle xs)))

;; =>
(3 4 5 1 2)


;;--------------------------------------------------------
;; Normalize Large Rotation
;;--------------------------------------------------------

(let [n (mod 12 (count xs))]
  (concat (drop n xs)
          (take n xs)))

;; =>
(3 4 5 1 2)


;;--------------------------------------------------------
;; All Left Rotations
;;--------------------------------------------------------

(map
  #(take (count xs)
         (drop %
               (cycle xs)))
  (range (count xs)))

;; =>
((1 2 3 4 5)
 (2 3 4 5 1)
 (3 4 5 1 2)
 (4 5 1 2 3)
 (5 1 2 3 4))


;;--------------------------------------------------------
;; Rotate a String
;;--------------------------------------------------------

(let [s "abcde"
      n 2]
  (str (subs s n)
       (subs s 0 n)))

;; =>
"cdeab"


;;--------------------------------------------------------
;; Circular Index Access
;;--------------------------------------------------------

(map #(nth xs
           (mod % (count xs)))
     (range 3 8))

;; =>
(4 5 1 2 3)


;;--------------------------------------------------------
;; Rotate Then Reverse
;;--------------------------------------------------------

(->> xs
     cycle
     (drop 2)
     (take (count xs))
     reverse)

;; =>
(2 1 5 4 3)


;;--------------------------------------------------------
;; Rotate Right by 1
;;--------------------------------------------------------

(concat
  (take-last 1 xs)
  (drop-last 1 xs))

;; =>
(5 1 2 3 4)


;;--------------------------------------------------------
;; Rotate Left by 1
;;--------------------------------------------------------

(concat
  (rest xs)
  [(first xs)])

;; =>
(2 3 4 5 1)
```