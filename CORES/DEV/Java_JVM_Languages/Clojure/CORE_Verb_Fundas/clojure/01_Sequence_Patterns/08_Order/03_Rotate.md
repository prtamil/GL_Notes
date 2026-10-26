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
;; (3 4 5 1 2)


;;--------------------------------------------------------
;; Rotate Right by 2
;;--------------------------------------------------------

(let [n 2]
  (concat (take-last n xs)
          (drop-last n xs)))

;; =>
;; (4 5 1 2 3)


;;--------------------------------------------------------
;; Rotate Using cycle
;;--------------------------------------------------------

(take 5
      (drop 2
            (cycle xs)))

;; =>
;; (3 4 5 1 2)


;;--------------------------------------------------------
;; Normalize Large Rotation
;;--------------------------------------------------------

(let [n (mod 12 (count xs))]
  (concat (drop n xs)
          (take n xs)))

;; =>
;; (3 4 5 1 2)


;;--------------------------------------------------------
;; All Left Rotations
;;--------------------------------------------------------

(map
  #(take (count xs)
         (drop %
               (cycle xs)))
  (range (count xs)))

;; =>
;; ((1 2 3 4 5)
 ;; (2 3 4 5 1)
 ;; (3 4 5 1 2)
 ;; (4 5 1 2 3)
 ;; (5 1 2 3 4))


;;--------------------------------------------------------
;; Rotate a String
;;--------------------------------------------------------

(let [s "abcde"
      n 2]
  (str (subs s n)
       (subs s 0 n)))

;; =>
;; "cdeab"


;;--------------------------------------------------------
;; Circular Index Access
;;--------------------------------------------------------

(map #(nth xs
           (mod % (count xs)))
     (range 3 8))

;; =>
;; (4 5 1 2 3)


;;--------------------------------------------------------
;; Rotate Then Reverse
;;--------------------------------------------------------

(->> xs
     cycle
     (drop 2)
     (take (count xs))
     reverse)

;; =>
;; (2 1 5 4 3)


;;--------------------------------------------------------
;; Rotate Right by 1
;;--------------------------------------------------------

(concat
  (take-last 1 xs)
  (drop-last 1 xs))

;; =>
;; (5 1 2 3 4)


;;--------------------------------------------------------
;; Rotate Left by 1
;;--------------------------------------------------------

(concat
  (rest xs)
  [(first xs)])

;; =>
;; (2 3 4 5 1)
```

---

### Readable Clojure Functions

```clojure
(defn rotate-left [distance collection]
  (let [values (vec collection)
        size (count values)]
    (if (zero? size)
      []
      (let [cut (mod distance size)]
        (into (subvec values cut)
              (subvec values 0 cut))))))

(defn rotate-right [distance values]
  (rotate-left (- distance) values))

(defn all-rotations [values]
  (map (fn [distance] (rotate-left distance values))
       (range (count values))))

(defn rotationally-equal? [left-values right-values]
  (and (= (count left-values) (count right-values))
       (boolean
         (some (fn [rotation]
                 (= (vec right-values) rotation))
               (all-rotations left-values)))))

(defn round-robin-pairs [values]
  (map vector values (rotate-left 1 values)))

(defn rotation-point [sorted-rotated]
  (let [values (vec sorted-rotated)]
    (when (seq values)
      (or (some (fn [[index [left right]]]
                  (when (> left right) (inc index)))
                (map-indexed vector (partition 2 1 values)))
          0))))

(rotate-left 2 [1 2 3 4 5])
;; => [3 4 5 1 2]

(rotate-right 2 [1 2 3 4 5])
;; => [4 5 1 2 3]

(rotate-left -1 [1 2 3 4 5])
;; => [5 1 2 3 4]

(rotationally-equal? [1 2 3] [3 1 2])
;; => true

(rotation-point [4 5 6 1 2 3])
;; => 3
```

This course defines a positive distance as a left rotation. Negative distances rotate right. Normalize with `mod` once so oversized and negative distances cannot create separate bugs.

### Memory Hooks

|You want|You reach for|
|---|---|
|visible finite rotation|split a vector, then join|
|wrap any signed distance|`mod`|
|rotate right|rotate left by the negative distance|
|all rotations|rotate by every valid offset|
|circular access only|use modular indexing instead|
|matrix rotation|transpose plus reversal—covered in Part 2|

### Key Insight

Rotation preserves relative cyclic order and changes only the chosen starting point. Put the sign convention in one named function and derive every other rotation operation from it.
