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
;; (1 2 3 1 2 3 1 2 3 1)


;;--------------------------------------------------------
;; Alternate Two Values
;;--------------------------------------------------------

(take 8
      (cycle [:on :off]))

;; =>
;; (:on :off :on :off :on :off :on :off)


;;--------------------------------------------------------
;; Repeat Characters
;;--------------------------------------------------------

(take 12
      (cycle "ABC"))

;; =>
;; (\A \B \C \A \B \C \A \B \C \A \B \C)


;;--------------------------------------------------------
;; Round Robin Players
;;--------------------------------------------------------

(take 10
      (cycle ["Alice" "Bob" "Carol"]))

;; =>
;; ("Alice" "Bob" "Carol"
 ;; "Alice" "Bob" "Carol"
 ;; "Alice" "Bob" "Carol"
 ;; "Alice")


;;--------------------------------------------------------
;; Offset Cycle
;;--------------------------------------------------------

(take 8
      (drop 2
            (cycle [1 2 3 4])))

;; =>
;; (3 4 1 2 3 4 1 2)


;;--------------------------------------------------------
;; Zip with a Cycle
;;--------------------------------------------------------

(map vector
     (range 8)
     (cycle [:A :B]))

;; =>
;; ([0 :A]
 ;; [1 :B]
 ;; [2 :A]
 ;; [3 :B]
 ;; [4 :A]
 ;; [5 :B]
 ;; [6 :A]
 ;; [7 :B])


;;--------------------------------------------------------
;; Infinite Color Pattern
;;--------------------------------------------------------

(take 10
      (cycle [:red :green :blue]))

;; =>
;; (:red :green :blue
 ;; :red :green :blue
 ;; :red :green :blue
 ;; :red)


;;--------------------------------------------------------
;; Compare repeat vs cycle
;;--------------------------------------------------------

(take 6
      (repeat :x))

;; =>
;; (:x :x :x :x :x :x)

(take 6
      (cycle [:x :y]))

;; =>
;; (:x :y :x :y :x :y)


;;--------------------------------------------------------
;; Rotate Using cycle
;;--------------------------------------------------------

(take 5
      (drop 2
            (cycle [1 2 3 4 5])))

;; =>
;; (3 4 5 1 2)


;;--------------------------------------------------------
;; Generate Weekdays Forever
;;--------------------------------------------------------

(take 10
      (cycle
        [:Mon :Tue :Wed :Thu :Fri]))

;; =>
;; (:Mon :Tue :Wed :Thu :Fri
 ;; :Mon :Tue :Wed :Thu :Fri)
```

---

### Readable Clojure Functions

```clojure
(defn offset-cycle [offset values]
  (drop (max 0 offset) (cycle values)))

(defn cycle-exactly [repetitions values]
  (take (* (max 0 repetitions) (count values))
        (cycle values)))

(defn label-periodically [labels values]
  (map vector (cycle labels) values))

(defn deal-round-robin [bucket-count values]
  (when-not (pos? bucket-count)
    (throw (ex-info "Bucket count must be positive"
                    {:bucket-count bucket-count})))
  (reduce (fn [buckets [index value]]
            (update buckets
                    (mod index bucket-count)
                    conj
                    value))
          (vec (repeat bucket-count []))
          (map-indexed vector values)))

(defn periodic-value [pattern index]
  (let [values (vec pattern)]
    (when (seq values)
      (nth values (mod index (count values))))))

(take 7 (offset-cycle 1 [:a :b :c]))
;; => (:b :c :a :b :c :a :b)

(cycle-exactly 3 [1 2])
;; => (1 2 1 2 1 2)

(label-periodically [:odd :even] (range 6))
;; => ([:odd 0] [:even 1] [:odd 2] [:even 3] [:odd 4] [:even 5])

(deal-round-robin 3 (range 8))
;; => [[0 3 6] [1 4 7] [2 5]]

(periodic-value [:Mon :Tue :Wed :Thu :Fri] 8)
;; => :Thu
```

`cycle` retains its finite input so it can replay it. Do not apply it to an unbounded source, and do not create it from mutable objects whose later changes are expected to appear automatically.

### Memory Hooks

|You want|You reach for|
|---|---|
|repeat one value|`repeat`|
|repeat a finite pattern|`cycle`|
|start partway through|`drop` over `cycle`|
|pair finite data with repeating labels|multi-collection `map`|
|deal into buckets|index modulo bucket count|
|direct periodic lookup|`nth` with `mod`|

### Key Insight

A cycle is infinite behavior built from finite state. Let the finite side of a multi-collection `map`, or an explicit `take`, provide the bound. For direct lookup, modular indexing is clearer and cheaper than generating all preceding values.
