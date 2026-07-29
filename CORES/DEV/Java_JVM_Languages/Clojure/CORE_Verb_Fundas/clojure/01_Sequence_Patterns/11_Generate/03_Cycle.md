# Pattern 33 — Cycle

## Mental Model

Generate an **infinite repeating sequence** by looping over the same collection again and again.

Unlike **Repeat**, which duplicates a single value, **Cycle** repeats an **entire sequence**.

---

## Relationship to Cognitive Verb

```text
Generate
    ↓
Cycle
```

Cycle is a **Generate** pattern because it continuously generates values by restarting the sequence after reaching the end.

---

## Clojure Functions & Common Idioms

|Variation|Example|Common Clojure|
|---|---|---|
|Repeat Sequence|`1 2 3 1 2 3`|`cycle`|
|Finite Cycle|First N values|`take` + `cycle`|
|Alternate Pattern|`A B A B`|`cycle`|
|Round Robin|Repeating turns|`cycle`|
|Circular Iteration|Endless traversal|`cycle`|
|Offset Cycle|Start from middle|`drop` + `cycle`|

> **Note:** `cycle` returns a **lazy infinite sequence**, so it is almost always used with `take`, `drop`, or another limiting operation.

---

## Common Uses

- Round-robin scheduling
    
- Game turns
    
- Animation loops
    
- Infinite playlists
    
- Periodic signals
    
- UI themes
    
- Color palettes
    
- Ring buffers
    

---

## Hidden Interview Problems

- Round-robin iterator
    
- Alternate values
    
- Repeat patterns
    
- Circular traversal
    
- Infinite stream generation
    
- Scheduling tasks
    

---

## Recognition Clues

If you hear:

- Repeat forever
    
- Loop back
    
- Circular
    
- Round robin
    
- Infinite pattern
    
- Wrap around
    
- Endless repetition
    

Think:

**→ Cycle**

---

## Pattern Summary

|Property|Value|
|---|---|
|Cognitive Verb|Generate|
|Pattern|Cycle|
|Input|Sequence|
|Output|Infinite repeating sequence|
|Lazy|Yes|
|Primary Use|Circular generation|

---

## Clojure Recipe Book

```clojure
;;--------------------------------------------------------
;; Repeat a Sequence
;;--------------------------------------------------------

(take 10
      (cycle [1 2 3]))

;; =>
(1 2 3 1 2 3 1 2 3 1)


;;--------------------------------------------------------
;; Alternate Two Values
;;--------------------------------------------------------

(take 8
      (cycle [:on :off]))

;; =>
(:on :off :on :off :on :off :on :off)


;;--------------------------------------------------------
;; Repeat Characters
;;--------------------------------------------------------

(take 12
      (cycle "ABC"))

;; =>
(\A \B \C \A \B \C \A \B \C \A \B \C)


;;--------------------------------------------------------
;; Round Robin Players
;;--------------------------------------------------------

(take 10
      (cycle ["Alice" "Bob" "Carol"]))

;; =>
("Alice" "Bob" "Carol"
 "Alice" "Bob" "Carol"
 "Alice" "Bob" "Carol"
 "Alice")


;;--------------------------------------------------------
;; Offset Cycle
;;--------------------------------------------------------

(take 8
      (drop 2
            (cycle [1 2 3 4])))

;; =>
(3 4 1 2 3 4 1 2)


;;--------------------------------------------------------
;; Zip with a Cycle
;;--------------------------------------------------------

(map vector
     (range 8)
     (cycle [:A :B]))

;; =>
([0 :A]
 [1 :B]
 [2 :A]
 [3 :B]
 [4 :A]
 [5 :B]
 [6 :A]
 [7 :B])


;;--------------------------------------------------------
;; Infinite Color Pattern
;;--------------------------------------------------------

(take 10
      (cycle [:red :green :blue]))

;; =>
(:red :green :blue
 :red :green :blue
 :red :green :blue
 :red)


;;--------------------------------------------------------
;; Compare repeat vs cycle
;;--------------------------------------------------------

(take 6
      (repeat :x))

;; =>
(:x :x :x :x :x :x)

(take 6
      (cycle [:x :y]))

;; =>
(:x :y :x :y :x :y)


;;--------------------------------------------------------
;; Rotate Using cycle
;;--------------------------------------------------------

(take 5
      (drop 2
            (cycle [1 2 3 4 5])))

;; =>
(3 4 5 1 2)


;;--------------------------------------------------------
;; Generate Weekdays Forever
;;--------------------------------------------------------

(take 10
      (cycle
        [:Mon :Tue :Wed :Thu :Fri]))

;; =>
(:Mon :Tue :Wed :Thu :Fri
 :Mon :Tue :Wed :Thu :Fri)
```