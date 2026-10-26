# Pattern 12 — Forward & Reverse Traversal

## Mental Model

Visit every element in a sequence **from beginning to end** or **from end to beginning**.

Traversal determines **the order in which elements are processed**, not what is done to them.

---

## Relationship to Cognitive Verb

```text
Traversal
      ↓
Forward & Reverse
```

Forward and Reverse are the two fundamental **Traversal** patterns.

---

## Clojure Functions & Common Idioms

|Variation|Example|Common Clojure|
|---|---|---|
|Forward Traversal|`1 2 3 4`|`map`, `doseq`, `reduce`|
|Reverse Traversal|`4 3 2 1`|`reverse`|
|Reverse Then Process|Reverse first|`reverse` + `map`|
|Reverse Reduce|Right-to-left reduction|`reduce` + `reverse`|
|Indexed Traversal|`(0 1) (1 2)`|`map-indexed`|
|Side-effect Traversal|Print, write, log|`doseq`|
|Lazy Traversal|Process on demand|`map`, `filter`, `sequence`|

> **Note:** Most Clojure sequence functions traverse **forward** by default. Reverse traversal is usually expressed by applying `reverse` first.

---

## Common Uses

- Sequence processing
    
- File processing
    
- Tree traversals
    
- Rendering pipelines
    
- Parsing
    
- Undo operations
    
- Stack processing
    
- Right-to-left algorithms
    

---

## Hidden Interview Problems

- Traverse linked lists
    
- Reverse print a list
    
- Palindrome checking
    
- Reverse iteration
    
- Right-to-left accumulation
    
- Expression evaluation
    

---

## Recognition Clues

If you hear:

- Visit every element
    
- Iterate
    
- Walk the sequence
    
- Scan left to right
    
- Scan right to left
    
- Reverse iteration
    
- Process in order
    

Think:

**→ Traversal**

---

## Pattern Summary

|Property|Value|
|---|---|
|Cognitive Verb|Traversal|
|Pattern|Forward & Reverse|
|Direction|Front → Back / Back → Front|
|Visits Every Element|Yes|
|Preserves Relative Order|Yes (within traversal direction)|
|Primary Use|Sequential processing|

---

## Clojure Recipe Book

```clojure
;;--------------------------------------------------------
;; Input
;;--------------------------------------------------------

(def xs [1 2 3 4 5])


;;--------------------------------------------------------
;; Forward Traversal
;;--------------------------------------------------------

(map inc xs)

;; => (2 3 4 5 6)


;;--------------------------------------------------------
;; Reverse Traversal
;;--------------------------------------------------------

(reverse xs)

;; => (5 4 3 2 1)


;;--------------------------------------------------------
;; Reverse Then Process
;;--------------------------------------------------------

(map inc (reverse xs))

;; => (6 5 4 3 2)


;;--------------------------------------------------------
;; Indexed Traversal
;;--------------------------------------------------------

(map-indexed vector xs)

;; => ([0 1] [1 2] [2 3] [3 4] [4 5])


;;--------------------------------------------------------
;; Side-effect Traversal
;;--------------------------------------------------------

(doseq [x xs]
  (println x))

;; Prints:
;; 1
;; 2
;; 3
;; 4
;; 5


;;--------------------------------------------------------
;; Forward Reduce
;;--------------------------------------------------------

(reduce + xs)

;; => 15


;;--------------------------------------------------------
;; Reverse Reduce
;;--------------------------------------------------------

(reduce - (reverse xs))

;; => 3


;;--------------------------------------------------------
;; Traverse with Position
;;--------------------------------------------------------

(map-indexed
  (fn [i x]
    {:index i :value x})
  xs)

;; =>
;; ({:index 0 :value 1}
 ;; {:index 1 :value 2}
 ;; {:index 2 :value 3}
 ;; {:index 3 :value 4}
 ;; {:index 4 :value 5})


;;--------------------------------------------------------
;; Lazy Traversal
;;--------------------------------------------------------

(take 3
  (map #(* % %) (range)))

;; => (0 1 4)
```

---

### Readable Clojure Functions

```clojure
(defn indexed-values [values]
  (map-indexed (fn [index value]
                 {:index index :value value})
               values))

(defn reverse-indexed-values [collection]
  (let [values (vec collection)]
    (map (fn [index]
           {:index index :value (nth values index)})
         (range (dec (count values)) -1 -1))))

(defn fold-right [combine initial values]
  (reduce (fn [result value]
            (combine value result))
          initial
          (rseq (vec values))))

(defn palindrome? [values]
  (= (seq values) (seq (reverse values))))

(indexed-values [:a :b :c])
;; => ({:index 0, :value :a}
;;     {:index 1, :value :b}
;;     {:index 2, :value :c})

(reverse-indexed-values [:a :b :c])
;; => ({:index 2, :value :c}
;;     {:index 1, :value :b}
;;     {:index 0, :value :a})

(fold-right cons [] [1 2 3])
;; => (1 2 3)

(palindrome? "level")
;; => true
```

Persistent collections do not need in-place reversal. Use `rseq` for vectors and sorted collections. Use `reverse` for general finite sequences.

### Memory Hooks

|You want|You reach for|
|---|---|
|forward values|`seq`, `map`, `doseq`|
|reverse a general finite sequence|`reverse`|
|efficient reverse traversal of a vector|`rseq`|
|index and value|`map-indexed`|
|original indices in reverse|descending `range` plus `nth`|
|right-associated fold|reverse, then `reduce` with flipped arguments|

### Key Insight

Traversal order and result order are separate decisions. `reverse` changes the order of values, while reverse traversal with original indices must carry those indices explicitly. Because Clojure data is normally immutable, many mutation-during-iteration hazards from imperative languages simply do not arise.
