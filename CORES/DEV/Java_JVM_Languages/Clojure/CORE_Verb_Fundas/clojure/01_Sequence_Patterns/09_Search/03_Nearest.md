# Pattern 28 — Nearest Match

## Mental Model

Find the element **closest to a target value** according to some distance or similarity measure.

Unlike **First Match**, which stops at the first valid element, or **Search All**, which returns every match, **Nearest Match** searches for the **best (closest)** match.

---

## Relationship to Cognitive Verb

```text
Search
   ↓
Nearest Match
```

Nearest Match is a **Search** pattern because it searches the sequence to find the element with the **minimum distance** from a target.

---

## Clojure Functions & Common Idioms

|Variation|Example|Common Clojure|
|---|---|---|
|Nearest Number|Closest to `23`|`apply min-key`|
|Nearest by Property|Closest age|`min-key`|
|Minimum Distance|Smallest difference|`min-key` + `abs`|
|Maximum Similarity|Best score|`max-key`|
|Nearest Object|Closest point|`min-key`|
|Top K Nearest|Closest N items|`sort-by` + `take`|

> **Note:** Clojure has no dedicated nearest function. The common idiom is `min-key` with a distance function.

---

## Common Uses

- Nearest value lookup
    
- Closest point
    
- Nearest timestamp
    
- Best recommendation
    
- Fuzzy matching
    
- Nearest sensor reading
    
- Spatial search
    
- AI nearest neighbor
    

---

## Hidden Interview Problems

- Closest number to target
    
- K nearest numbers
    
- Closest point to origin
    
- Nearest timestamp
    
- Closest interval
    
- Nearest neighbor
    

---

## Recognition Clues

If you hear:

- Closest
    
- Nearest
    
- Minimum distance
    
- Best match
    
- Similarity
    
- Nearest neighbor
    
- Closest value
    

Think:

**→ Nearest Match**

---

## Pattern Summary

|Property|Value|
|---|---|
|Cognitive Verb|Search|
|Pattern|Nearest Match|
|Stops Early|No|
|Returns|Best matching element|
|Comparison|Distance / Similarity|
|Primary Use|Approximate search|

---

## Clojure Recipe Book

```clojure
;;--------------------------------------------------------
;; Input
;;--------------------------------------------------------

(def xs [10 15 22 30 42 55])


;;--------------------------------------------------------
;; Nearest Number to 25
;;--------------------------------------------------------

(apply min-key
       #(Math/abs (- % 25))
       xs)

;; => 22


;;--------------------------------------------------------
;; Nearest Number to 40
;;--------------------------------------------------------

(apply min-key
       #(Math/abs (- % 40))
       xs)

;; => 42


;;--------------------------------------------------------
;; Farthest Number
;;--------------------------------------------------------

(apply max-key
       #(Math/abs (- % 25))
       xs)

;; => 55


;;--------------------------------------------------------
;; Nearest Object by Property
;;--------------------------------------------------------

(def people
  [{:name "Alice" :age 24}
   {:name "Bob"   :age 31}
   {:name "Carol" :age 27}])

(apply min-key
       #(Math/abs (- (:age %) 26))
       people)

;; =>
;; {:name "Carol" :age 27}


;;--------------------------------------------------------
;; Top 3 Nearest Values
;;--------------------------------------------------------

(take 3
      (sort-by #(Math/abs (- % 25))
               xs))

;; =>
;; (22 30 15)


;;--------------------------------------------------------
;; Nearest Timestamp
;;--------------------------------------------------------

(def times [100 140 180 250])

(apply min-key
       #(Math/abs (- % 160))
       times)

;; => 180


;;--------------------------------------------------------
;; Closest Point to Origin
;;--------------------------------------------------------

(def points [[3 4] [1 2] [5 5]])

(apply min-key
       (fn [[x y]]
         (+ (* x x) (* y y)))
       points)

;; =>
;; [1 2]


;;--------------------------------------------------------
;; Highest Score (Maximum Similarity)
;;--------------------------------------------------------

(def scores
  [{:name "A" :score 0.81}
   {:name "B" :score 0.95}
   {:name "C" :score 0.76}])

(apply max-key :score scores)

;; =>
;; {:name "B" :score 0.95}


;;--------------------------------------------------------
;; Compare First vs Nearest
;;--------------------------------------------------------

(first xs)

;; =>
;; 10

(apply min-key
       #(Math/abs (- % 25))
       xs)

;; =>
;; 22
```

---

### Readable Clojure Functions

```clojure
(defn nearest-by [distance-fn values]
  (when-let [[first-value & remaining-values] (seq values)]
    (reduce (fn [best value]
              ;; Strict < preserves the earliest value on a tie.
              (if (< (distance-fn value) (distance-fn best))
                value
                best))
            first-value
            remaining-values)))

(defn nearest-number [target values]
  (nearest-by #(Math/abs (double (- % target))) values))

(defn nearest-with-distance [distance-fn values]
  (when-let [nearest-value (nearest-by distance-fn values)]
    {:value nearest-value
     :distance (distance-fn nearest-value)}))

(defn top-k-nearest [k distance-fn values]
  (->> values
       (sort-by distance-fn)
       (take (max 0 k))))

(defn pair-gap [[left right]]
  (- right left))

(defn closest-pair [values]
  (when-let [[first-pair & remaining-pairs]
             (seq (partition 2 1 (sort values)))]
    (reduce (fn [best pair]
              ;; Strict < preserves the first sorted pair on a tie.
              (if (< (pair-gap pair) (pair-gap best))
                pair
                best))
            first-pair
            remaining-pairs)))

(nearest-number 25 [10 22 28 40])
;; => 22

(nearest-by #(Math/abs (- (:score %) 90))
            [{:name "A" :score 82}
             {:name "B" :score 93}])
;; => {:name "B", :score 93}

(nearest-with-distance #(Math/abs (- % 25)) [10 22 28 40])
;; => {:value 22, :distance 3}

(top-k-nearest 3 #(Math/abs (- % 10)) [1 7 9 12 20])
;; => (9 12 7)

(closest-pair [10 3 20 8 9])
;; => (8 9)
```

For repeated queries of sorted data, use binary search. Compare the two values near the insertion point. A complete `min-key` scan is O(n).

### Memory Hooks

|You want|You reach for|
|---|---|
|nearest by a distance|`nearest-by`|
|farthest by a score|`max-key`|
|nearest record|distance function over a field|
|value and distance|map to `[distance value]` once|
|top `k` nearest|sort by distance, then `take`|
|closest pair of numbers|sort, then inspect adjacent pairs|
|maximum acceptable distance|check the winning distance afterward|

### Key Insight

Nearest search is ordinary minimization once distance has been defined. Tie behavior is part of the contract: the named reducer above deliberately keeps the earliest value, whereas `min-key` may select a later equal-key argument.
