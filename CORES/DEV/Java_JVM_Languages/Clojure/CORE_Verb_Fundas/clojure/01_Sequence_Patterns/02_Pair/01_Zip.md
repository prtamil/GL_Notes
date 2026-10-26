# Pattern 6 — Zip

## Mental Model

Combine **multiple sequences element-by-element** into a single sequence of tuples.

---

## Relationship to Cognitive Verb

```text
Pair
   ↓
Zip
```

Zip is the simplest implementation of the **Pair** verb. It pairs corresponding elements from two or more sequences.

---

## Clojure Functions & Common Idioms

|Variation|Example|Common Clojure|
|---|---|---|
|Zip Two Sequences|`(1 a) (2 b) (3 c)`|`map vector xs ys`|
|Zip Three Sequences|`(1 a x)`|`map vector xs ys zs`|
|Zip with Function|`(1 10) → 11`|`map + xs ys`|
|Zip with Index|`(0 a) (1 b) (2 c)`|`map-indexed vector xs`|
|Zip Keys & Values|`{:a 1 :b 2}`|`zipmap keys vals`|
|Zip Until Shortest Ends|Default behavior|`map`|

---

## Common Uses

- Pair IDs with values
    
- Combine names and scores
    
- Merge columns
    
- Join parallel arrays
    
- Create coordinate pairs `(x, y)`
    
- Build key-value maps
    
- Combine timestamps with events
    
- Pair labels with predictions
    

---

## Hidden Interview Problems

- Merge two sorted results
    
- Create coordinate points
    
- Associate IDs with objects
    
- Build dictionaries/maps
    
- Pair questions with answers
    
- Combine parallel datasets
    

---

## Recognition Clues

If you hear:

- Corresponding elements
    
- Pair two arrays
    
- Parallel lists
    
- Match positions
    
- Combine columns
    
- X and Y coordinates
    
- Keys and values
    
- Element-wise combine
    

Think:

**→ Zip**

---

## Pattern Summary

| Property        | Value                                          |
| --------------- | ---------------------------------------------- |
| Cognitive Verb  | Pair                                           |
| Pattern         | Zip                                            |
| Input           | Two or more sequences                          |
| Output          | One sequence of tuples (or transformed values) |
| Pairing Rule    | Same index                                     |
| Stops At        | Shortest sequence                              |
| Preserves Order | Yes                                            |

---

## Clojure Recipe Book

```clojure
;; ============================================
;; Setup

(def nums  [1 2 3])
(def letters ["a" "b" "c"])

;; ============================================
;; Zip two sequences

(map vector nums letters)
;; => ([1 "a"] [2 "b"] [3 "c"])

;; There is no zip function — map IS zip when you give it more than
;; one collection. That is the whole idea, and it generalizes for free.

;; map is lazy; realizing the first element realizes only that element
(first (map vector nums letters))     ;; => [1 "a"]

;; ============================================
;; Zip three sequences — nothing changes

(map vector nums letters "xyz")
;; => ([1 "a" \x] [2 "b" \y] [3 "c" \z])

;; ============================================
;; Zip with a function — element-wise combine

(map + [1 2 3] [10 20 30])
;; => (11 22 33)

;; Python needs zip + a comprehension, or map(add, …), or starmap for
;; the already-paired case. In Clojure they are one call: the function
;; you pass to map receives one element from each collection.
;; vector is just the function that happens to keep them as a pair.

;; ============================================
;; Zip with index

(map-indexed vector letters)
;; => ([0 "a"] [1 "b"] [2 "c"])

(map-indexed (fn [index letter]
               [(inc index) letter])
             letters)                          ; start at 1
;; => ([1 "a"] [2 "b"] [3 "c"])

;; don't write (map vector (range (count xs)) xs) — map-indexed exists

;; ============================================
;; Zip keys and values into a map

(zipmap letters nums)
;; => {"a" 1, "b" 2, "c" 3}

;; a dedicated function, because building a map from two parallel
;; sequences is common enough to deserve one

;; and back out again — a map IS a sequence of pairs
(seq {:a 1 :b 2})
;; => ([:a 1] [:b 2])

;; ============================================
;; THE TRAP — map stops at the shortest, silently

(map vector [1 2 3] ["a"])
;; => ([1 "a"])            2 and 3 vanish, no warning

;; ============================================
;; No strict= here — say it yourself

(defn zip-strict [& collections]
  (let [sizes (mapv count collections)]
    (when-not (apply = sizes)
      (throw (ex-info "Input sizes must match" {:sizes sizes})))
    (apply map vector collections)))

(zip-strict [1 2 3] ["a" "b" "c"])     ;; => ([1 "a"] [2 "b"] [3 "c"])

(try
  (zip-strict [1 2 3] ["a"])
  (catch clojure.lang.ExceptionInfo error
    (ex-data error)))
;; => {:sizes [3 1]}

;; Python 3.10 added zip(..., strict=True) for exactly this.
;; Clojure has no equivalent, so when the inputs are SUPPOSED to be
;; parallel, check on purpose — it turns silent data loss into a
;; loud failure. Note this realizes the collections to count them,
;; so it is for finite, in-memory inputs only.

;; ============================================
;; Pad instead of truncate

(defn zip-longest [fill-value & collections]
  (let [longest-size (apply max (map count collections))]
    (apply map vector
           (map (fn [collection]
                  (concat collection
                          (repeat (- longest-size (count collection))
                                  fill-value)))
                collections))))

(zip-longest "-" [1 2 3] ["a"])
;; => ([1 "a"] [2 "-"] [3 "-"])

;; ============================================
;; Unzip — the same call, run backwards

(apply map vector [[1 "a"] [2 "b"] [3 "c"]])
;; => ([1 2 3] ["a" "b" "c"])

;; apply spreads the pairs as separate arguments, so this is
;; (map vector [1 "a"] [2 "b"] [3 "c"]) — it transposes.

;; ============================================
;; Zip IS transpose

(apply map vector [[1 2 3]
                   [4 5 6]])
;; => ([1 4] [2 5] [3 6])

;; ============================================
;; Coordinate points

(map vector [0 1 2] [10 11 12])
;; => ([0 10] [1 11] [2 12])

(defn dist [[x1 y1] [x2 y2]]
  (Math/sqrt (+ (* (- x2 x1) (- x2 x1))
                (* (- y2 y1) (- y2 y1)))))

(map dist [[0 0] [3 0]] [[0 4] [0 0]])
;; => (4.0 3.0)

;; destructuring in the parameter list means dist reads like maths,
;; and map feeds it corresponding points with no unpacking step

;; ============================================
;; Labels with predictions — accuracy in one line

(/ (count (filter true? (map = [1 0 1 1] [1 0 0 1]))) 4)
;; => 3/4

;; (map = a b) compares element-wise and yields booleans

;; ============================================
;; Sorting by a parallel array

(map second (sort-by first > (map vector [72 95 88] ["carol" "alice" "bob"])))
;; => ("alice" "bob" "carol")

;; zip the two together, sort on the key half, keep the value half

;; ============================================
;; Rows to maps with named columns

(map #(zipmap [:id :name] %) [[1 "a"] [2 "b"]])
;; => ({:id 1, :name "a"} {:id 2, :name "b"})

;; this is the CSV-header-to-records move, and it is one line

;; ============================================
;; Compare

(map vector nums chars)          ; same index      → Zip (this pattern)
(partition 2 1 nums)             ; index i, i+1    → Adjacent Pair (one seq)
(for [x nums y chars] [x y])     ; every × every   → Cartesian Product
(concat nums chars)              ; one after other → Concatenate
```

---

### Memory Hooks

|You want|You reach for|
|---|---|
|corresponding elements|`(map vector xs ys)`|
|…combined by a function|`(map f xs ys)`|
|…and they must match in length|hand-rolled `zip-strict`|
|…and they might not|hand-rolled `zip-longest`|
|position + element|`(map-indexed vector xs)`|
|a map from two sequences|`(zipmap keys vals)`|
|element-wise arithmetic|`(map + xs ys)`|
|split pairs back apart|`(apply map vector pairs)`|
|transpose a matrix|`(apply map vector rows)`|

---

### Key Insight

**Clojure does not need a separate `zip` function.** `map` can process multiple collections. Use `vector` to keep pairs, `+` to add, or `=` to compare.

**Zipping and unzipping use the same operation.** `(apply map vector pairs)` transposes the input. It can unzip pairs or transpose a matrix.

**`map` stops at the shortest input without a warning.** Check the input lengths when all collections must have the same size.
