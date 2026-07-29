`reductions` is one of Clojure's most beautiful functions because it returns **the entire history**, not just the final answer.

Think of it as:

> **`reduce` = Final state**  
> **`reductions` = Every intermediate state**

Here are some examples.

```clojure
;;--------------------------------------------------------
;; 1. Running Sum (Prefix Sum)
;;--------------------------------------------------------

(reductions + [1 2 3 4 5])

;; => (1 3 6 10 15)


;;--------------------------------------------------------
;; 2. Running Product (Factorial Sequence)
;;--------------------------------------------------------

(reductions * [1 2 3 4 5])

;; => (1 2 6 24 120)


;;--------------------------------------------------------
;; 3. Running Maximum
;;--------------------------------------------------------

(reductions max [3 1 5 2 7 4])

;; => (3 3 5 5 7 7)


;;--------------------------------------------------------
;; 4. Running Minimum
;;--------------------------------------------------------

(reductions min [5 7 3 8 2 9])

;; => (5 5 3 3 2 2)


;;--------------------------------------------------------
;; 5. Growing Prefixes
;;--------------------------------------------------------

(reductions conj [] [1 2 3 4])

;; =>
[]
[1]
[1 2]
[1 2 3]
[1 2 3 4]


;;--------------------------------------------------------
;; 6. Growing String
;;--------------------------------------------------------

(reductions str "" ["H" "e" "l" "l" "o"])

;; =>
""
"H"
"He"
"Hel"
"Hell"
"Hello"


;;--------------------------------------------------------
;; 7. Building a Path
;;--------------------------------------------------------

(reductions
  (fn [[x y] [dx dy]]
    [(+ x dx) (+ y dy)])
  [0 0]
  [[1 0] [0 1] [2 0] [-1 -1]])

;; =>
[0 0]
[1 0]
[1 1]
[3 1]
[2 0]


;;--------------------------------------------------------
;; 8. Running Frequency Map
;;--------------------------------------------------------

(reductions
  (fn [m x]
    (update m x (fnil inc 0)))
  {}
  [:a :b :a :c :a])

;; =>
{}
{:a 1}
{:a 1 :b 1}
{:a 2 :b 1}
{:a 2 :b 1 :c 1}
{:a 3 :b 1 :c 1}


;;--------------------------------------------------------
;; 9. Running Set
;;--------------------------------------------------------

(reductions conj #{} [1 2 1 3 2])

;; =>
#{}
#{1}
#{1 2}
#{1 2}
#{1 2 3}
#{1 2 3}


;;--------------------------------------------------------
;; 10. Running Map Construction
;;--------------------------------------------------------

(reductions
  (fn [m [k v]]
    (assoc m k v))
  {}
  [[:a 1] [:b 2] [:c 3]])

;; =>
{}
{:a 1}
{:a 1 :b 2}
{:a 1 :b 2 :c 3}


;;--------------------------------------------------------
;; 11. Undo / History (State Machine)
;;--------------------------------------------------------

(reductions
  (fn [balance tx]
    (+ balance tx))
  100
  [-20 +50 -10 +30])

;; =>
100
80
130
120
150


;;--------------------------------------------------------
;; 12. Tree Traversal Path
;;--------------------------------------------------------

(reductions conj [] [:home :documents :projects :clojure])

;; =>
[]
[:home]
[:home :documents]
[:home :documents :projects]
[:home :documents :projects :clojure]
```

## The common mental model

|Pattern|Example|
|---|---|
|Running Sum|Prefix sums|
|Running Product|Factorials|
|Running Max/Min|Best-so-far|
|Growing Collection|Build prefixes|
|Running String|Progressive parsing|
|Running Set|Seen-so-far|
|Running Map|Index construction|
|Running Frequency|Histogram over time|
|Running Position|Path simulation|
|Running State|Undo/redo, FSM|

**Rule of thumb:**

- `map` → transform each item independently.
    
- `reduce` → compute one final result.
    
- `reductions` → **show the journey**, returning every intermediate state. This is why it's so useful for debugging, visualizations, animations, state machines, dynamic programming, and algorithms where the evolution of state matters just as much as the final answer.