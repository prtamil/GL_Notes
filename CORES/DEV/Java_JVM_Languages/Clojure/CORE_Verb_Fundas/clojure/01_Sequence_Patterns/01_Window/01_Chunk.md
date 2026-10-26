# Pattern 1 — Chunk (Fixed-Size Blocks)

## Mental Model

Cut a sequence into **fixed-size blocks that don't overlap**. Every element lands in **exactly one** chunk.

Chunking is what a window becomes when **step size equals window size**. The window moves on and never looks back at an element it has already seen.

---

## Relationship to Cognitive Verb

```text
Window
   ↓
Chunk
```

Chunk is a **Window** pattern where the window jumps forward by **its own width**, so two windows in a row never share an element.

---

## Clojure Functions & Common Variations

|Variation|Example|Clojure Function|
|---|---|---|
|Chunk of 3 (drop partial tail)|`(1 2 3) (4 5 6)`|`(partition 3 xs)`|
|Chunk of 3 (keep partial tail)|`(1 2 3) (4 5)`|`(partition-all 3 xs)`|
|Chunk with an explicit step|step = size|`(partition 3 3 xs)`|
|Pad the last chunk|`(4 5 _)`|`(partition 3 3 (repeat 0) xs)`|
|Chunk a lazy stream|infinite seqs, line seqs|`partition-all` (already lazy)|
|Chunk inside a transducer|no intermediate seq|`(partition-all 3)`|
|Chunk a string|`"abcdef"` → `"abc" "def"`|`(map #(apply str %) (partition-all 3 s))`|

---

## Common Uses

- Batching API / DB writes

- Pagination

- Fixed-width record parsing

- Memory-bounded stream processing

- Splitting work across workers

- Building grid rows from a flat list

- Byte-block / packet framing

- Mini-batches in ML training

---

## Hidden Interview Problems

- Split an array into groups of K

- Reshape a flat list into a matrix

- Batch requests with a size limit

- Chunk a string every N characters

- Average of every K elements

- Reverse each group of K in a linked list

- Distribute items round-robin across N buckets

---

## Recognition Clues

If you hear:

- Groups of **K**

- Batches of **N**

- Pages of size **N**

- Blocks

- Non-overlapping

- Split evenly

- Every N items at a time

Think:

**→ Chunk**

---

## Pattern Summary

|Property|Value|
|---|---|
|Cognitive Verb|Window|
|Pattern|Chunk|
|Overlap|No|
|Window Size|Fixed (`n`)|
|Step Size|`n` (same as window)|
|Preserves Order|Yes|
|Covers All Elements|Yes with `partition-all`, No with `partition`|

---

## Clojure Recipe Book

```clojure
;; ============================================
;; Setup

(def xs [1 2 3 4 5 6 7 8])

;; ============================================
;; Chunk, keeping the partial tail — the usual default

(partition-all 3 xs)
;; => ((1 2 3) (4 5 6) (7 8))

;; ============================================
;; Chunk, dropping the partial tail

(partition 3 xs)
;; => ((1 2 3) (4 5 6))          ; 7 and 8 are silently dropped

;; partition and partition-all differ in EXACTLY one way: the tail.
;; That is the whole decision, and it is the classic chunking bug.

;; ============================================
;; The step argument IS the pattern

(partition 3 3 xs)     ; step = size  → chunks, no overlap
;; => ((1 2 3) (4 5 6))

(partition 3 1 xs)     ; step = 1     → sliding window, overlap
;; => ((1 2 3) (2 3 4) (3 4 5) (4 5 6) (5 6 7) (6 7 8))

;; (partition 3 xs) is just (partition 3 3 xs) with the step defaulted.
;; Chunk and Sliding Window are one function and one number apart.

;; ============================================
;; Pad the last chunk instead of dropping it

(partition 3 3 (repeat 0) xs)
;; => ((1 2 3) (4 5 6) (7 8 0))

;; the 4-arity pad collection is only drawn from when the tail is short.
;; A finite pad works too, and runs out honestly:
(partition 3 3 [:x] xs)
;; => ((1 2 3) (4 5 6) (7 8 :x))

;; ============================================
;; Chunk a lazy stream — nothing special required

;; partition-all is lazy, so an infinite source is fine
(take 3 (partition-all 3 (range)))
;; => ((0 1 2) (3 4 5) (6 7 8))

;; and so is a file, one block of lines at a time
(comment
  (with-open [r (clojure.java.io/reader "big.log")]
    (doseq [batch (partition-all 500 (line-seq r))]
      (process batch))))

;; Python needs an islice loop for this. Clojure does not:
;; the sequence functions are lazy by default, so streaming
;; is the same code as batching a vector.

;; ============================================
;; Aggregate per chunk

(map #(reduce + %) (partition-all 3 xs))     ;; => (6 15 15)
(map #(apply max %) (partition-all 3 xs))    ;; => (3 6 8)

;; average of every K elements
(map #(/ (reduce + %) (count %)) (partition-all 3 xs))
;; => (2 5 15/2)

;; note 15/2 — Clojure keeps exact ratios. Force a double when
;; you actually want 7.5:
(map #(double (/ (reduce + %) (count %))) (partition-all 3 xs))
;; => (2.0 5.0 7.5)

;; ============================================
;; Chunk inside a transducer — no intermediate sequence

(into [] (comp (partition-all 3)
               (map #(reduce + %)))
      xs)
;; => [6 15 15]

;; partition-all has a transducer arity; partition does not.
;; If you are chunking as one step in a pipeline, this is the version
;; that does not allocate the chunks just to throw them away.

;; ============================================
;; Reshape a flat list into a matrix

(def flat [1 2 3 4 5 6])

(mapv vec (partition-all 3 flat))
;; => [[1 2 3] [4 5 6]]

;; mapv vec matters: partition returns seqs, and a matrix you intend
;; to index with get-in wants vectors.

;; ============================================
;; Chunk a string

(def s "abcdefgh")

(map #(apply str %) (partition-all 3 s))
;; => ("abc" "def" "gh")

;; a string is seqable as characters, so every chunking recipe above
;; works on it unchanged — you only add the apply str to put it back.

;; ============================================
;; Batch side effects (the real-world use)

(comment
  (doseq [batch (partition-all 100 (range 1000))]
    (write-to-db batch)))          ; 10 calls instead of 1000

;; ============================================
;; Round-robin distribution (chunk's cousin)

(map #(take-nth 3 (drop % xs)) (range 3))
;; => ((1 4 7) (2 5 8) (3 6))

;; take-nth takes every nth item; partition takes n in a row.
;; Deal cards to 3 players vs. hand each player 3 cards off the top.

;; ============================================
;; Compare

(partition-all 3 xs)   ; blocks, keep tail  → ((1 2 3) (4 5 6) (7 8))
(partition 3 xs)       ; blocks, drop tail  → ((1 2 3) (4 5 6))
(partition 3 1 xs)     ; sliding window     → ((1 2 3) (2 3 4) ...)
(take-nth 3 xs)        ; every 3rd item     → (1 4 7)
```

---

### Memory Hooks

|You want|You reach for|
|---|---|
|blocks of n, keep tail|`(partition-all n xs)`|
|blocks of n, drop tail|`(partition n xs)`|
|blocks of n, pad tail|`(partition n n (repeat pad) xs)`|
|blocks from a matrix row|`(mapv vec (partition-all n flat))`|
|blocks from a stream|`(partition-all n …)` — already lazy|
|blocks in a transducer|`(partition-all n)`|
|one number per block|`(map #(reduce + %) (partition-all n xs))`|
|every nth item (not a block)|`(take-nth n xs)`|

---

### Key Insight

**Chunk and Sliding Window use the same function with different step values.** `(partition n n xs)` gives separate chunks. `(partition n 1 xs)` gives sliding windows. An intermediate step gives jump windows.

You must select how to process the short final group. `partition` drops it. `partition-all` keeps it. The four-argument `partition` fills it with pad values.
