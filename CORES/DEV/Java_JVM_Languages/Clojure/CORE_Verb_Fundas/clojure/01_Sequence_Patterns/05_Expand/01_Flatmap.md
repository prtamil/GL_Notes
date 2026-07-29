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
([1 10]
 [2 20]
 [3 30])


;;--------------------------------------------------------
;; FlatMap (mapcat)
;;--------------------------------------------------------

(mapcat #(vector % (* % 10)) xs)

;; =>
(1 10 2 20 3 30)


;;--------------------------------------------------------
;; Duplicate Every Element
;;--------------------------------------------------------

(mapcat #(repeat 2 %) xs)

;; =>
(1 1 2 2 3 3)


;;--------------------------------------------------------
;; Expand Into a Range
;;--------------------------------------------------------

(mapcat range [1 3 5])

;; =>
(0
 0 1 2
 0 1 2 3 4)


;;--------------------------------------------------------
;; Split Strings into Characters
;;--------------------------------------------------------

(mapcat seq ["ab" "cd" "ef"])

;; =>
(\a \b \c \d \e \f)


;;--------------------------------------------------------
;; Remove and Expand Together
;;--------------------------------------------------------

(mapcat #(if (even? %)
           [% (* % 10)]
           [])
        xs)

;; =>
(2 20)


;;--------------------------------------------------------
;; FlatMap with for
;;--------------------------------------------------------

(for [x [1 2]
      y [:a :b]]
  [x y])

;; =>
([1 :a]
 [1 :b]
 [2 :a]
 [2 :b])


;;--------------------------------------------------------
;; Compare map vs mapcat
;;--------------------------------------------------------

(map #(range %) [1 3 5])

;; =>
((0)
 (0 1 2)
 (0 1 2 3 4))


(mapcat #(range %) [1 3 5])

;; =>
(0
 0 1 2
 0 1 2 3 4)


;;--------------------------------------------------------
;; Expand Nested Collections
;;--------------------------------------------------------

(mapcat identity [[1 2] [3 4] [5]])

;; =>
(1 2 3 4 5)
```