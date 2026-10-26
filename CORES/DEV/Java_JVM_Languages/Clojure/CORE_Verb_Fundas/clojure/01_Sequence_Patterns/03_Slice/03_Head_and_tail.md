# Pattern 11 — Head & Tail

## Mental Model

Split a sequence into its **first element (Head)** and **everything else (Tail)**. This is the fundamental decomposition pattern in functional programming.

---

## Relationship to Cognitive Verb

```text
Slice
   ↓
Head & Tail
```

Head & Tail is the most basic **Slice** pattern. Many recursive algorithms begin by separating a sequence into its head and tail.

---

## Clojure Functions & Common Idioms

|Variation|Example|Common Clojure|
|---|---|---|
|Head|`1`|`first`|
|Tail|`(2 3 4)`|`rest`|
|Head + Tail|`1 (2 3 4)`|`first` + `rest`|
|Remove Head|`(2 3 4)`|`next` / `rest`|
|Safe Empty Check|`nil` or sequence|`seq`|
|Destructure Head & Tail|`[head & tail]`|Destructuring|

> **Note:** `rest` returns an empty sequence when possible, whereas `next` returns `nil` when no elements remain.

---

## Common Uses

- Recursive algorithms
    
- Stream processing
    
- Parser implementation
    
- Tree traversal
    
- Functional list processing
    
- Pattern matching
    
- State machines
    

---

## Hidden Interview Problems

- Recursive sum
    
- Recursive reverse
    
- Linked list traversal
    
- Token parsing
    
- DFS / BFS traversal
    
- Expression evaluation
    

---

## Recognition Clues

If you hear:

- First element
    
- Remaining elements
    
- Consume one item
    
- Peel one element
    
- Recursive processing
    
- Process until empty
    

Think:

**→ Head & Tail**

---

## Pattern Summary

|Property|Value|
|---|---|
|Cognitive Verb|Slice|
|Pattern|Head & Tail|
|Direction|Front|
|Output|One element + Remaining sequence|
|Preserves Order|Yes|
|Primary Use|Recursive decomposition|

---

## Clojure Recipe Book

```clojure
;;--------------------------------------------------------
;; Input
;;--------------------------------------------------------

(def xs [1 2 3 4 5])


;;--------------------------------------------------------
;; Head
;;--------------------------------------------------------

(first xs)

;; => 1


;;--------------------------------------------------------
;; Tail
;;--------------------------------------------------------

(rest xs)

;; => (2 3 4 5)


;;--------------------------------------------------------
;; Head + Tail
;;--------------------------------------------------------

[(first xs)
 (rest xs)]

;; =>
;; [1
 ;; (2 3 4 5)]


;;--------------------------------------------------------
;; Safe Tail
;;--------------------------------------------------------

(next xs)

;; => (2 3 4 5)

(next [1])

;; => nil


;;--------------------------------------------------------
;; Is Sequence Empty?
;;--------------------------------------------------------

(seq xs)

;; => (1 2 3 4 5)

(seq [])

;; => nil


;;--------------------------------------------------------
;; Destructure Head & Tail
;;--------------------------------------------------------

(let [[head & tail] xs]
  [head tail])

;; =>
;; [1
 ;; (2 3 4 5)]


;;--------------------------------------------------------
;; Recursive Processing Pattern
;;--------------------------------------------------------

(loop [[head & tail] xs]
  (when head
    (println head)
    (recur tail)))

;; Prints:
;; 1
;; 2
;; 3
;; 4
;; 5


;;--------------------------------------------------------
;; Head with Default
;;--------------------------------------------------------

(or (first []) :empty)

;; => :empty


;;--------------------------------------------------------
;; Skip Multiple Heads
;;--------------------------------------------------------

(nthrest xs 2)

;; => (3 4 5)


;;--------------------------------------------------------
;; Destructure Multiple Heads
;;--------------------------------------------------------

(let [[a b & tail] xs]
  [a b tail])

;; =>
;; [1
 ;; 2
 ;; (3 4 5)]
```

---

### Readable Clojure Functions

Clojure destructuring expresses head-and-tail decomposition directly. Wrap it only when the empty case or the returned shape deserves a name.

```clojure
(defn uncons [values]
  (when-let [items (seq values)]
    [(first items) (next items)]))

(defn head-or [default values]
  (if-let [items (seq values)]
    (first items)
    default))

(defn describe-sequence [[head & tail :as values]]
  (cond
    (empty? values) :empty
    (empty? tail) {:kind :single :value head}
    :else {:kind :many :head head :tail tail}))

(defn parse-command [[command & arguments]]
  {:command command
   :arguments (vec arguments)})

(defn depth-first-values [root children]
  (loop [stack [root]
         result []]
    (if-let [node (peek stack)]
      (recur (into (pop stack) (reverse (children node)))
             (conj result node))
      result)))

(uncons [1 2 3])
;; => [1 (2 3)]

(uncons [])
;; => nil

(head-or :missing [])
;; => :missing

(let [[first-token second-token & remaining] [:a :b :c :d]]
  [first-token second-token remaining])
;; => [:a :b (:c :d)]
```

### Memory Hooks

|You want|You reach for|
|---|---|
|head|`first`|
|tail, possibly empty|`rest`|
|tail, or `nil` when absent|`next`|
|head and tail together|`[head & tail]`|
|safe decomposition|`when-let` with `seq`|
|skip several heads|`nthrest` or `drop`|

### Key Insight

Head and tail are structural operations. Use destructuring for a known shape. `rest` returns an empty sequence. `next` returns `nil` when no items remain.
