# Pattern 7 — Interleave

## Mental Model

Combine **multiple sequences by alternating elements** from each sequence.

---

## Relationship to Cognitive Verb

```text
Pair
   ↓
Interleave
```

Interleave is a **Pair** pattern that combines sequences by taking **one element from each sequence in turn**.

---

## Clojure Functions & Common Idioms

|Variation|Example|Common Clojure|
|---|---|---|
|Interleave Two Sequences|`1 a 2 b 3 c`|`interleave xs ys`|
|Interleave Three Sequences|`1 a x 2 b y`|`interleave xs ys zs`|
|Interleave Until Shortest Ends|Default behavior|`interleave`|
|Separate (Reverse Interleave)|`(1 2 3) (a b c)`|`partition` + `take-nth` / `map`|
|Alternate Processing|`A B A B A B`|`interleave` + sequence operations|

---

## Common Uses

- Merge two event streams
    
- Alternate animation frames
    
- Stereo audio (Left, Right)
    
- RGB component layout
    
- UI layouts
    
- Round-robin scheduling
    
- Alternate turns in games
    
- Weaving two datasets
    

---

## Hidden Interview Problems

- Merge two arrays alternately
    
- Shuffle cards perfectly
    
- Round-robin task scheduling
    
- Alternate characters from two strings
    
- Weave linked lists
    
- Merge logs chronologically (alternating source)
    

---

## Recognition Clues

If you hear:

- Alternate
    
- Every other
    
- Weave
    
- Round-robin
    
- Left, Right
    
- A B A B
    
- Alternate turns
    
- Intermix
    

Think:

**→ Interleave**

---

## Pattern Summary

| Property        | Value                               |
| --------------- | ----------------------------------- |
| Cognitive Verb  | Pair                                |
| Pattern         | Interleave                          |
| Input           | Two or more sequences               |
| Output          | One alternating sequence            |
| Pairing Rule    | Take one from each sequence in turn |
| Stops At        | Shortest sequence                   |
| Preserves Order | Yes (within each sequence)          |

---

## Clojure Recipe Book

```clojure
;; ============================================
;; Setup

(require '[clojure.string :as str])

(def nums  [1 2 3])
(def chars ["a" "b" "c"])

;; ============================================
;; Interleave two sequences — it has its own function

(interleave nums chars)
;; => (1 "a" 2 "b" 3 "c")

;; Python builds this out of chain.from_iterable(zip(a, b)).
;; Clojure ships it, because weaving is common enough to name.

;; the built-from-parts version, for when you want to see the shape:
(mapcat vector nums chars)
;; => (1 "a" 2 "b" 3 "c")
;;
;;   map vector → ([1 "a"] [2 "b"] [3 "c"])    group by position
;;   mapcat     → 1 "a" 2 "b" 3 "c"            flatten one level

;; ============================================
;; Interleave three sequences — the call doesn't change

(interleave nums chars "xyz")
;; => (1 "a" \x 2 "b" \y 3 "c" \z)

;; ============================================
;; THE TRAP — interleave stops at the shortest

(interleave [1 2 3 4 5] ["a" "b"])
;; => (1 "a" 2 "b")            3, 4, 5 are gone

;; ============================================
;; Keep the leftovers

(defn interleave-all
  "Like interleave, but exhausted collections drop out of the rotation
   instead of ending it."
  [& collections]
  (lazy-seq
    (let [active-collections (filter seq collections)]
      (when (seq active-collections)
        (concat (map first active-collections)
                (apply interleave-all
                       (map rest active-collections)))))))

(interleave-all [1 2 3 4 5] ["a" "b"])
;; => (1 "a" 2 "b" 3 4 5)

;; ============================================
;; …and this is also round-robin

(interleave-all "ABC" "D" "EF")
;; => (\A \D \E \B \F \C)

;; Python needs a separate roundrobin recipe with cycle and islice.
;; It is the same function: "interleave that doesn't stop at the
;; shortest" and "round-robin until every source is empty" describe
;; identical behavior. One definition covers both.

;; ============================================
;; Separate (reverse interleave)

(def woven [1 "a" 2 "b" 3 "c"])

(take-nth 2 woven)              ;; => (1 2 3)         even positions
(take-nth 2 (rest woven))       ;; => ("a" "b" "c")   odd positions

;; for k sources:
(map #(take-nth 3 (drop % ["r1" "g1" "b1" "r2" "g2" "b2"])) (range 3))
;; => (("r1" "r2") ("g1" "g2") ("b1" "b2"))

;; ============================================
;; Stereo audio: two channels ↔ one interleaved buffer

(def buf (interleave [1 3 5] [2 4 6]))
buf                                     ;; => (1 2 3 4 5 6)
[(take-nth 2 buf) (take-nth 2 (rest buf))]
;; => [(1 3 5) (2 4 6)]

;; ============================================
;; Perfect riffle shuffle

(let [deck (vec (range 8))
      h    (quot (count deck) 2)]
  (interleave (take h deck) (drop h deck)))
;; => (0 4 1 5 2 6 3 7)

;; ============================================
;; Alternate characters from two strings

(apply str (interleave "abc" "XYZ"))
;; => "aXbYcZ"

;; ============================================
;; Interleave with a constant separator — again, it has a name

(interpose "|" nums)
;; => (1 "|" 2 "|" 3)

;; interpose is "weave this one value between the elements", which is
;; the separator case of interleave with no off-by-one to trim.
;; Python does (chain.from_iterable(zip(nums, repeat('|'))))[:-1].

;; for strings, join is the direct route
(str/join "|" nums)
;; => "1|2|3"

;; ============================================
;; Alternate turns (infinite)

(take 5 (cycle ["X" "O"]))
;; => ("X" "O" "X" "O" "X")

;; ============================================
;; Merge two sorted streams — NOT interleave

(defn merge-sorted [a b]
  (lazy-seq
    (cond (empty? a) b
          (empty? b) a
          (<= (first a) (first b)) (cons (first a) (merge-sorted (rest a) b))
          :else                    (cons (first b) (merge-sorted a (rest b))))))

(merge-sorted [1 4 7] [2 3 8])
;; => (1 2 3 4 7 8)

;; Interleave alternates by POSITION; merge orders by VALUE.
;; "Merge logs chronologically" is this, not interleave. Clojure has no
;; heapq.merge, but the lazy recursive version is short and streams.

;; ============================================
;; Compare

(map vector nums chars)      ;; => ([1 "a"] [2 "b"] [3 "c"])   pairing kept
(interleave nums chars)      ;; => (1 "a" 2 "b" 3 "c")         pairing dissolved
(concat nums chars)          ;; => (1 2 3 "a" "b" "c")         appended, not woven
(interleave-all nums chars)  ;; => (1 "a" 2 "b" 3 "c")         uneven-safe
```

---

### Memory Hooks

|You want|You reach for|
|---|---|
|weave two sequences|`(interleave a b)`|
|weave, uneven lengths|`interleave-all` (also round-robin)|
|weave a constant between|`(interpose sep xs)`|
|…into a string|`(str/join sep xs)`|
|unweave|`(take-nth 2 xs)`, `(take-nth 2 (rest xs))`|
|unweave k sources|`(map #(take-nth k (drop % xs)) (range k))`|
|concatenate instead|`(concat a b)`|
|order by value instead|a lazy `merge-sorted`|
|endless alternation|`(cycle [...])`|

---

### Key Insight

**Interleave is a flattened zip operation.** `(map vector a b)` keeps the pairs. `(interleave a b)` returns one flat sequence. `interpose` inserts separators.

**`interleave-all` also implements round-robin selection.** It takes one value from each source until all sources are empty.

One distinction worth holding onto: **interleave alternates by position, merge orders by value.** Give them two sorted, equal-length inputs and they look identical. Give them anything else and they diverge completely. "Merge these two log files" almost always means the merge, not this pattern.
