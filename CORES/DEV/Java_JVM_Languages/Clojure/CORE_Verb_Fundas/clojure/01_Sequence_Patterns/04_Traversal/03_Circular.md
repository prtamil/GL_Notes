# Pattern 14 — Circular Traversal

## Mental Model

Traverse a sequence **as if the end connects back to the beginning**, allowing iteration to wrap around indefinitely or for a fixed number of cycles.

---

## Relationship to Cognitive Verb

```text
Traversal
      ↓
Circular Traversal
```

Circular Traversal is a **Traversal** pattern where reaching the end of a sequence **wraps back to the start** instead of stopping.

---

## Clojure Functions & Common Idioms

|Variation|Example|Common Clojure|
|---|---|---|
|Infinite Cycle|`1 2 3 1 2 3 ...`|`cycle`|
|Fixed Circular Traversal|One complete wrap|`take` + `cycle`|
|Circular Pair|`(3 1)` wraps around|`concat` + `partition`|
|Circular Window|Last connects to first|`concat` + `take` + `partition`|
|Circular Index|`(mod i n)`|`mod` + `nth`|
|Rotate Then Traverse|Different starting point|`cycle` + `drop` + `take`|

> **Note:** Unlike Forward Traversal, Circular Traversal never naturally reaches an end. You usually control it with `take`, `drop`, or an explicit stopping condition.

---

## Common Uses

- Round-robin scheduling
    
- Ring buffers
    
- Circular queues
    
- Game turns
    
- Polygon processing
    
- Clock arithmetic
    
- Music loops
    
- Animation loops
    

---

## Hidden Interview Problems

- Next player in a game
    
- Josephus problem
    
- Circular array
    
- Gas station problem
    
- Circular buffer
    
- Polygon edge traversal
    

---

## Recognition Clues

If you hear:

- Wrap around
    
- Circular array
    
- Ring
    
- Loop forever
    
- Repeat sequence
    
- Next after last
    
- Clock
    
- Round-robin
    

Think:

**→ Circular Traversal**

---

## Pattern Summary

|Property|Value|
|---|---|
|Cognitive Verb|Traversal|
|Pattern|Circular Traversal|
|Direction|Forward (typically)|
|Stops at End|No|
|Wrap Around|Yes|
|Primary Use|Cyclic processing|

---

## Clojure Recipe Book

```clojure
;;--------------------------------------------------------
;; Input
;;--------------------------------------------------------

(def xs [1 2 3])


;;--------------------------------------------------------
;; Infinite Cycle
;;--------------------------------------------------------

(cycle xs)

;; => (1 2 3 1 2 3 1 2 3 ...)


;;--------------------------------------------------------
;; Traverse Two Complete Cycles
;;--------------------------------------------------------

(take 6 (cycle xs))

;; => (1 2 3 1 2 3)


;;--------------------------------------------------------
;; Start from a Different Position
;;--------------------------------------------------------

(take 6
      (drop 1 (cycle xs)))

;; => (2 3 1 2 3 1)


;;--------------------------------------------------------
;; Circular Pair
;;--------------------------------------------------------

(partition 2 1
           (concat xs [(first xs)]))

;; => ((1 2)
;;     (2 3)
;;     (3 1))


;;--------------------------------------------------------
;; Circular Window (Size 3)
;;--------------------------------------------------------

(partition 3 1
           (concat xs (take 2 xs)))

;; => ((1 2 3)
;;     (2 3 1)
;;     (3 1 2))


;;--------------------------------------------------------
;; Circular Indexing
;;--------------------------------------------------------

(map #(nth xs (mod % (count xs)))
     (range 8))

;; => (1 2 3 1 2 3 1 2)


;;--------------------------------------------------------
;; Rotate Then Traverse
;;--------------------------------------------------------

(->> (cycle xs)
     (drop 2)
     (take 3))

;; => (3 1 2)


;;--------------------------------------------------------
;; Enumerate Circular Traversal
;;--------------------------------------------------------

(map-indexed vector
             (take 7 (cycle xs)))

;; => ([0 1]
;;     [1 2]
;;     [2 3]
;;     [3 1]
;;     [4 2]
;;     [5 3]
;;     [6 1])
```