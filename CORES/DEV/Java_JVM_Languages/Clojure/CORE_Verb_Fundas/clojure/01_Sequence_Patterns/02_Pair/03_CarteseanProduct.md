# Pattern 8 — Cartesian Product

## Mental Model

Generate **every possible combination** by pairing each element of one sequence with **every** element of another sequence.

---

## Relationship to Cognitive Verb

```text
Pair
   ↓
Cartesian Product
```

Cartesian Product is a **Pair** pattern that creates **all possible pairs**, not just corresponding or alternating ones.

---

## Clojure Functions & Common Idioms

|Variation|Example|Common Clojure|
|---|---|---|
|Cartesian Product (2 sequences)|`(1 a) (1 b) (2 a) (2 b)`|`for`|
|Cartesian Product (3 sequences)|`(1 a x) (1 a y) ...`|`for`|
|Pair then Transform|`(x y) → f(x,y)`|`for` + expression|
|Cartesian with Filter|Valid combinations only|`for :when`|
|Nested Iteration|Every outer × inner|`for` / nested `mapcat`|

---

## Common Uses

- Grid generation
    
- Chess board coordinates
    
- Game state generation
    
- Test case generation
    
- Password combinations
    
- Hyperparameter search
    
- SQL CROSS JOIN
    
- All pair comparisons
    
- Ray/object intersection tests
    

---

## Hidden Interview Problems

- Generate all pairs
    
- Generate all combinations of two arrays
    
- Sudoku coordinate generation
    
- Matrix coordinate traversal
    
- Compare every item with every other item
    
- Brute-force search
    
- CROSS JOIN implementation
    

---

## Recognition Clues

If you hear:

- Every possible combination
    
- All pairs
    
- Every X with every Y
    
- Cross join
    
- Nested loops
    
- Exhaustive search
    
- Grid coordinates
    
- Combinations of two lists
    

Think:

**→ Cartesian Product**

---

## Pattern Summary

| Property        | Value                          |
| --------------- | ------------------------------ |
| Cognitive Verb  | Pair                           |
| Pattern         | Cartesian Product              |
| Input           | Two or more sequences          |
| Output          | Every possible combination     |
| Pairing Rule    | Every element with every other |
| Complexity      | O(n × m)                       |
| Preserves Order | Yes (nested iteration order)   |

---

## Clojure Recipe Book

```clojure
;; 1. Cartesian Product of Two Sequences

(for [x [1 2 3]
      y [:a :b]]
  [x y])

;; =>
;; ([1 :a]
 ;; [1 :b]
 ;; [2 :a]
 ;; [2 :b]
 ;; [3 :a]
 ;; [3 :b])


;; 2. Cartesian Product of Three Sequences

(for [x [1 2]
      y [:a :b]
      z [:x :y]]
  [x y z])

;; =>
;; ([1 :a :x]
 ;; [1 :a :y]
 ;; [1 :b :x]
 ;; [1 :b :y]
 ;; [2 :a :x]
 ;; [2 :a :y]
 ;; [2 :b :x]
 ;; [2 :b :y])


;; 3. Transform While Pairing

(for [x [1 2 3]
      y [10 20]]
  (+ x y))

;; =>
;; (11 21 12 22 13 23)


;; 4. Cartesian Product with Filtering

(for [x (range 5)
      y (range 5)
      :when (< x y)]
  [x y])

;; =>
;; ([0 1]
 ;; [0 2]
 ;; [0 3]
 ;; [0 4]
 ;; [1 2]
 ;; [1 3]
 ;; [1 4]
 ;; [2 3]
 ;; [2 4]
 ;; [3 4])


;; 5. Matrix Coordinates

(for [row (range 3)
      col (range 4)]
  [row col])

;; =>
;; ([0 0] [0 1] [0 2] [0 3]
 ;; [1 0] [1 1] [1 2] [1 3]
 ;; [2 0] [2 1] [2 2] [2 3])


;; 6. Chess Board Coordinates

(for [file [:a :b :c]
      rank [1 2 3]]
  [file rank])

;; =>
;; ([:a 1] [:a 2] [:a 3]
 ;; [:b 1] [:b 2] [:b 3]
 ;; [:c 1] [:c 2] [:c 3])


;; 7. Self-product — every item with every item, including itself

(def v3 [1 2 3])

(count (for [x v3 y v3] [x y]))          ;; => 9      n² pairs


;; 8. The four "all pairs" variants — know which one you mean

;; Clojure has no combinatorics in core. For the pair case the index
;; arithmetic says it directly; for the general case use
;; org.clojure/math.combinatorics.

(defn pairs
  "Unordered pairs, no self-pairing — n(n-1)/2 of them."
  [xs]
  (let [v (vec xs)]
    (for [i (range (count v))
          j (range (inc i) (count v))]
      [(v i) (v j)])))

(count (for [x v3 y v3] [x y]))                              ;; => 9  ordered, self ok
(count (for [i (range 3) j (range 3) :when (not= i j)] [i j])) ;; => 6  ordered, no self
(count (pairs v3))                                            ;; => 3  unordered, no self
(count (for [i (range 3) j (range i 3)] [i j]))               ;; => 6  unordered, self ok

;; "compare every item with every other" is usually the 3, not the 9 —
;; you rarely want (a,a), and you rarely want both (a,b) and (b,a).
;; Note the index-based forms: comparing by VALUE would also drop
;; legitimate duplicates in the input.


;; 9. All pair comparisons — the real use of pairs

(defn dist [[x1 y1] [x2 y2]]
  (Math/sqrt (+ (* (- x2 x1) (- x2 x1))
                (* (- y2 y1) (- y2 y1)))))

(def pts [[0 0] [3 4] [6 8]])

(map (fn [[p q]] (dist p q)) (pairs pts))
;; => (5.0 10.0 5.0)

;; the closest pair — and a portability trap
(apply min-key (fn [[p q]] (dist p q)) (pairs pts))
;; => [[3 4] [6 8]]           the LAST of the tied minima

(first (sort-by (fn [[p q]] (dist p q)) (pairs pts)))
;; => [[0 0] [3 4]]           the FIRST — sort-by is stable

;; min-key returns the later element when keys tie; Python's min returns
;; the earlier one. Two distances here are both 5.0, so the two languages
;; disagree on the answer. If ties are possible and the choice matters,
;; use the stable sort-by form and say what you meant.


;; 10. Hyperparameter grid search

(defn cartesian [collections]
  (if-let [[values & remaining-collections] (seq collections)]
    (for [value values
          remaining-product (cartesian remaining-collections)]
      (cons value remaining-product))
    [[]]))

(let [grid {:lr [0.1 0.01] :depth [3 5] :seed [0]}]
  (map #(zipmap (keys grid) %) (cartesian (vals grid))))
;; => ({:lr 0.1,  :depth 3, :seed 0}
;;     {:lr 0.1,  :depth 5, :seed 0}
;;     {:lr 0.01, :depth 3, :seed 0}
;;     {:lr 0.01, :depth 5, :seed 0})

;; cartesian over (vals m) plus zipmap over (keys m) is the whole
;; grid-search library. Works because for a literal map of this size
;; keys and vals walk in the same order.


;; 11. Test case generation

(for [user   ["admin" "guest"]
      action ["read" "write"]
      state  ["on" "off"]]
  [user action state])
;; => 8 cases, no nested loops


;; 12. Brute-force strings — where the cost becomes real

(for [a "ab" b "ab" c "ab"] (str a b c))
;; => ("aaa" "aab" "aba" "abb" "baa" "bab" "bba" "bbb")

(long (Math/pow 26 8))       ;; => 208827064576

;; for is lazy, so this LOOPS forever rather than exploding memory.
;; Laziness saves your RAM; it does not save your afternoon.


;; 13. for is lazy all the way down — unlike Python's product

(take 5 (for [x (range) y [:a :b]] [x y]))
;; => ([0 :a] [0 :b] [1 :a] [1 :b] [2 :a])

;; itertools.product buffers every input eagerly, so an infinite source
;; hangs it. Clojure's for consumes the outer collection lazily, so an
;; infinite OUTER sequence is fine. The inner ones are re-traversed per
;; outer element, so those still need to be finite and re-iterable.


;; 14. SQL CROSS JOIN

(let [users [{:id 1} {:id 2}]
      roles [{:r "a"} {:r "b"}]]
  (for [u users r roles] (merge u r)))
;; => ({:id 1, :r "a"} {:id 1, :r "b"} {:id 2, :r "a"} {:id 2, :r "b"})

;; an INNER JOIN is a filtered cross join — and :when says so
(let [users  [{:id 1} {:id 2}]
      orders [{:uid 1 :n 10} {:uid 2 :n 20}]]
  (for [u users o orders :when (= (:id u) (:uid o))] [u o]))
;; => ([{:id 1} {:uid 1, :n 10}] [{:id 2} {:uid 2, :n 20}])


;; 15. Compare

(map vector [1 2] "ab")        ; => ([1 \a] [2 \b])                  n pairs
(for [x [1 2] y "ab"] [x y])   ; => ([1 \a] [1 \b] [2 \a] [2 \b])    n × m
(pairs [1 2 3])                ; => ([1 2] [1 3] [2 3])              n choose 2

;; map walks in lockstep. for nests. pairs picks a subset.
```

---

### Memory Hooks

|You want|You reach for|
|---|---|
|every X with every Y|`(for [x xs y ys] [x y])`|
|every X with every X|`(for [x xs y xs] [x y])`|
|all unordered pairs|`(for [i (range n) j (range (inc i) n)] …)`|
|…with self-pairing|`(for [i (range n) j (range i n)] …)`|
|filtered combinations|`:when` inside the `for`|
|grid coordinates|`(for [r (range rows) c (range cols)] [r c])`|
|a parameter grid|`cartesian` over `vals` + `zipmap` over `keys`|
|all strings of length n|`(for [a alpha b alpha …] (str a b …))`|
|the general case|`org.clojure/math.combinatorics`|

---

### Key Insight

**This is the only pattern here whose output multiplies.** Zip gives you `n` results, interleave gives you `n + m`, product gives you `n × m`. Add a third source and that multiplication becomes the dominant cost of your whole program. Every "let's just try all the combinations" disaster is someone underestimating it.

Before you add another `for` binding, decide if you need ordered or unordered pairs. Unordered pairs produce `n(n-1)/2` results. They also remove duplicate comparisons.

Clojure `for` supports products, filters, and projections. Use `:when` for the filter and the body for the transformation. The outer binding is lazy.
