# Pattern 15 — FlatMap

## Mental Model

Transform each element into **zero, one, or many elements**, then **flatten** the results into a single sequence.

Unlike `map`, which returns one output per input, **FlatMap can change the size of the sequence**.

---

## Relationship to Cognitive Verb

```text
Expand
   ↓
FlatMap
```

FlatMap is an **Expand** pattern because each input element can produce **multiple output elements**.

---

## Clojure Functions & Common Idioms

|Variation|Example|Common Clojure|
|---|---|---|
|Map then Flatten|`[1 2] → (1 -1 2 -2)`|`mapcat`|
|Expand One-to-Many|`2 → (2 4 8)`|`mapcat`|
|Zero-or-Many Results|Remove or Expand|`keep` / `mapcat`|
|Nested Iteration|Flatten nested results|`for`|
|Expand Strings|`"ab" → \a \b`|`mapcat seq`|

> **Note:** `mapcat` is essentially **`map` followed by one level of `flatten`**.

---

## Common Uses

- Tokenization
    
- Parsing
    
- Tree expansion
    
- Exploding nested collections
    
- Expanding search states
    
- Processing nested JSON
    
- Generating neighboring nodes
    
- Event expansion
    

---

## Hidden Interview Problems

- Flatten nested lists
    
- Tokenize text
    
- Generate neighbors in a graph
    
- Expand ranges
    
- Parse CSV fields
    
- Generate search states
    

---

## Recognition Clues

If you hear:

- One-to-many
    
- Expand
    
- Explode
    
- Flatten after mapping
    
- Nested results
    
- Variable number of outputs
    
- Generate children
    

Think:

**→ FlatMap**

---

## Pattern Summary

|Property|Value|
|---|---|
|Cognitive Verb|Expand|
|Pattern|FlatMap|
|Input|One element|
|Output|Zero, one, or many elements|
|Changes Sequence Size|Yes|
|Automatically Flattens|One level|

---

## Clojure Recipe Book

```clojure
;;--------------------------------------------------------
;; Input
;;--------------------------------------------------------

(def xs [1 2 3])


;;--------------------------------------------------------
;; Map
;;--------------------------------------------------------

(map #(vector % (* % 10)) xs)

;; =>
;; ([1 10]
 ;; [2 20]
 ;; [3 30])


;;--------------------------------------------------------
;; FlatMap (mapcat)
;;--------------------------------------------------------

(mapcat #(vector % (* % 10)) xs)

;; =>
;; (1 10 2 20 3 30)


;;--------------------------------------------------------
;; Duplicate Every Element
;;--------------------------------------------------------

(mapcat #(repeat 2 %) xs)

;; =>
;; (1 1 2 2 3 3)


;;--------------------------------------------------------
;; Expand Into a Range
;;--------------------------------------------------------

(mapcat range [1 3 5])

;; =>
;; (0
 ;; 0 1 2
 ;; 0 1 2 3 4)


;;--------------------------------------------------------
;; Split Strings into Characters
;;--------------------------------------------------------

(mapcat seq ["ab" "cd" "ef"])

;; =>
;; (\a \b \c \d \e \f)


;;--------------------------------------------------------
;; Remove and Expand Together
;;--------------------------------------------------------

(mapcat #(if (even? %)
           [% (* % 10)]
           [])
        xs)

;; =>
;; (2 20)


;;--------------------------------------------------------
;; FlatMap with for
;;--------------------------------------------------------

(for [x [1 2]
      y [:a :b]]
  [x y])

;; =>
;; ([1 :a]
 ;; [1 :b]
 ;; [2 :a]
 ;; [2 :b])


;;--------------------------------------------------------
;; Compare map vs mapcat
;;--------------------------------------------------------

(map #(range %) [1 3 5])

;; =>
;; ((0)
 ;; (0 1 2)
 ;; (0 1 2 3 4))


(mapcat #(range %) [1 3 5])

;; =>
;; (0
 ;; 0 1 2
 ;; 0 1 2 3 4)


;;--------------------------------------------------------
;; Expand Nested Collections
;;--------------------------------------------------------

(mapcat identity [[1 2] [3 4] [5]])

;; =>
;; (1 2 3 4 5)
```

---

### Readable Clojure Functions

```clojure
(require '[clojure.string :as str])

(defn flat-map [transform values]
  (mapcat transform values))

(defn duplicate-each [values]
  (flat-map (fn [value] (repeat 2 value)) values))

(defn expand-ranges [limits]
  (flat-map range limits))

(defn tokenize-lines [lines]
  (flat-map (fn [line] (str/split line #"\s+")) lines))

(defn keep-and-expand [predicate expand-fn values]
  (flat-map (fn [value]
              (if (predicate value)
                (expand-fn value)
                []))
            values))

(defn cartesian-product [left-values right-values]
  (for [left left-values
        right right-values]
    [left right]))

(defn next-bfs-layer [neighbors visited frontier]
  (->> frontier
       (mapcat neighbors)
       (remove visited)
       distinct
       vec))

(duplicate-each [:a :b :c])
;; => (:a :a :b :b :c :c)

(expand-ranges [1 3 5])
;; => (0 0 1 2 0 1 2 3 4)

(tokenize-lines ["functional data" "simple functions"])
;; => ("functional" "data" "simple" "functions")

(keep-and-expand odd? #(repeat % %) [1 2 3 4])
;; => (1 3 3 3)
```

`mapcat` removes exactly one level of nesting. Use recursive `flatten` only when every sequential level is meant to disappear.

### Memory Hooks

|You want|You reach for|
|---|---|
|one result per input|`map`|
|zero or many results per input|`mapcat`|
|only remove one nesting level|`mapcat identity`|
|nested-loop combinations|`for`|
|delete during expansion|return an empty collection|
|one BFS expansion|`mapcat neighbors`|

### Key Insight

FlatMap is `map` followed by a one-level concatenation. The mapping function controls cardinality: an empty result deletes an input, one value preserves it, and several values expand it. In Clojure that idea is directly represented by `mapcat`.
