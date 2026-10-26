# Pattern 9 — Prefix

## Mental Model

Take the **beginning portion** of a sequence.

---

## Relationship to Cognitive Verb

```text
Slice
   ↓
Prefix
```

Prefix is a **Slice** pattern that extracts elements **from the start** of a sequence.

---

## Clojure Functions & Common Idioms

| Variation              | Example             | Common Clojure       |
| ---------------------- | ------------------- | -------------------- |
| First N Elements       | `1 2 3`             | `take n`             |
| First Element          | `1`                 | `first`              |
| First While Condition  | `1 2 3`             | `take-while`         |
| All Prefixes           | `(1) (1 2) (1 2 3)` | `reductions conj []` |
| Prefix Until Predicate | Until match         | `take-while`         |

```clojure
(reductions conj [] [1 2 3 4])

;; =>
[]
[1]
[1 2]
[1 2 3]
[1 2 3 4]
```
---

## Common Uses

- Preview data
    
- Pagination (first page)
    
- File headers
    
- String prefixes
    
- Autocomplete
    
- Initial samples
    
- Bootstrapping algorithms
    
- Reading protocol headers
    

---

## Hidden Interview Problems

- Return first K elements
    
- Longest common prefix
    
- Check string starts with prefix
    
- Read file header
    
- Process first page of results
    
- Extract startup records
    

---

## Recognition Clues

If you hear:

- First N
    
- Beginning
    
- Starts with
    
- Leading elements
    
- Initial segment
    
- Header
    
- Front of sequence
    
- Prefix
    

Think:

**→ Prefix**

---

## Pattern Summary

| Property                 | Value                    |
| ------------------------ | ------------------------ |
| Cognitive Verb           | Slice                    |
| Pattern                  | Prefix                   |
| Direction                | Front                    |
| Size                     | Fixed or Predicate-based |
| Preserves Order          | Yes                      |
| Includes Entire Sequence | Possible                 |

---

## Clojure Recipe Book

```clojure
;; ============================================
;; Setup

(require '[clojure.string :as str])

(def xs [1 2 3 4 5 6])

;; ============================================
;; First N elements

(take 3 xs)              ;; => (1 2 3)
(take 100 xs)            ;; => (1 2 3 4 5 6)     no error, just clamps

;; take NEVER complains about an out-of-range count. subvec does:
(subvec xs 0 3)          ;; => [1 2 3]
(try
  (subvec xs 0 100)
  (catch IndexOutOfBoundsException _
    :out-of-bounds))
;; => :out-of-bounds

;; take returns a lazy seq, subvec returns a VECTOR sharing structure
;; with the original — O(1) and no copy. Use subvec when you have a
;; vector, know the bounds are good, and want a vector back.

;; ============================================
;; First N from a stream — the same function

(take 5 (range))         ;; => (0 1 2 3 4)

;; This is the whole story. Python needs islice the moment the source
;; stops being indexable; take never cared in the first place, and it
;; does not consume the source the way islice does.

;; ============================================
;; First element

(first xs)               ;; => 1
(first [])               ;; => nil        no exception

;; nil-punning is the difference from Python. xs[0] on an empty list
;; raises IndexError; (first []) simply gives you nil, which is why
;; the "safe" idiom and the plain idiom are the same code here.

(nth xs 0)               ;; => 1
(try
  (nth [] 0)
  (catch IndexOutOfBoundsException _
    :out-of-bounds))     ;; nth is strict
(nth [] 0 :empty)        ;; => :empty     with a default

;; ============================================
;; First element MATCHING a condition — stops at the first hit

(first (filter even? xs))          ;; => 2
(first (filter #(> % 99) xs))      ;; => nil

;; filter is lazy, so first pulls exactly one match and stops.
;; This is NOT the wasteful "filter everything then take one" it looks
;; like — that trap exists in Python, not here.

(some #(when (even? %) %) xs)      ;; => 2
(some even? xs)                    ;; => true     careful: the PREDICATE's value

;; some returns what the predicate returns, so use the when form when
;; you want the element rather than a boolean.

;; ============================================
;; First while a condition holds — take-while

(take-while #(< % 4) xs)           ;; => (1 2 3)

;; THE distinction that matters:
(take-while #(< % 4) [1 2 9 3])    ;; => (1 2)        stops at 9
(filter     #(< % 4) [1 2 9 3])    ;; => (1 2 3)      keeps scanning

;; take-while = "the leading run".  filter = "every match anywhere".

;; ============================================
;; All prefixes

(reductions conj [] [1 2 3 4])
;; => ([] [1] [1 2] [1 2 3] [1 2 3 4])

;; reductions again — "every intermediate state of building this up"
;; is exactly what all-prefixes means.

;; ============================================
;; Prefix sums — the useful kind of "all prefixes"

(reductions + [1 2 3 4])           ;; => (1 3 6 10)
(reductions + 0 [1 2 3 4])         ;; => (0 1 3 6 10)

;; ============================================
;; Does it start with a prefix?

(str/starts-with? "hello.txt" "hello")                  ;; => true
(some #(str/starts-with? "a.py" %) [".py" "a."])        ;; => true

(= (take 3 xs) '(1 2 3))                                ;; => true

;; ============================================
;; Longest common prefix — the classic interview question

(defn lcp [strs]
  (if (empty? strs)
    ""
    (->> (apply map vector strs)      ; walk the strings column-wise
         (take-while #(apply = %))    ; keep columns that are unanimous
         (map first)
         (apply str))))

(lcp ["flower" "flow" "flight"])          ;; => "fl"
(lcp ["interspecies" "interstellar"])     ;; => "inters"
(lcp ["abc" "xyz"])                       ;; => ""

;; This is the pattern at its best: (apply map vector strs) transposes
;; and stops at the shortest string, take-while ends at the first column
;; that isn't unanimous, and there is no index arithmetic anywhere.

;; ============================================
;; Pagination

(take 2 xs)                        ;; page 1  => (1 2)
(->> xs (drop 2) (take 2))         ;; page 2  => (3 4)
(partition-all 2 xs)               ;; all pages => ((1 2) (3 4) (5 6))

;; ============================================
;; File header — read N lines without loading the file

(comment
  (with-open [r (clojure.java.io/reader "data.csv")]
    (doall (take 5 (line-seq r)))))

;; the doall matters: line-seq is lazy and with-open closes the reader
;; on exit, so an unrealized seq would be read after the file is gone.
;; This is the one place laziness needs a deliberate nudge.

;; ============================================
;; Top-K — a prefix of the SORTED sequence

(take 3 (sort > [5 1 9 3 7]))      ;; => (9 7 5)
(take 3 (sort   [5 1 9 3 7]))      ;; => (1 3 5)

;; Clojure has no heapq.nlargest, so this sorts everything: O(n log n)
;; against heapq's O(n log k). Fine for ordinary n; if k is tiny and n
;; is huge, reach for a priority queue rather than pretending otherwise.

;; ============================================
;; Drop the prefix instead of taking it

(drop 3 xs)                        ;; => (4 5 6)

;; ============================================
;; Compare

(take 3 xs)                        ; first 3, by COUNT      → Prefix
(take-while #(< % 4) xs)           ; leading run, by VALUE  → Prefix
(take-last 3 xs)                   ; last 3                 → Suffix
[(first xs) (rest xs)]             ; one + the rest         → Head & Tail
```

---

### Memory Hooks

|You want|You reach for|
|---|---|
|first n|`(take n xs)`|
|first n, as a vector, O(1)|`(subvec v 0 n)`|
|first element|`(first xs)` — `nil` when empty|
|first element, strictly|`(nth xs 0)` — throws when empty|
|first match|`(first (filter pred xs))`|
|the leading run|`(take-while pred xs)`|
|every match|`(filter pred xs)` — not the same thing|
|all prefixes|`(reductions conj [] xs)`|
|first n lines of a file|`(take n (line-seq r))` + `doall`|
|top k|`(take k (sort > xs))`|

---

### Key Insight

**“First n” and “first while” are different patterns.** `take` uses a count. `take-while` uses a condition and stops at the first false result. `filter` continues to scan.

**Clojure `take` is always lazy.** The same call works with a vector, `line-seq`, or infinite `range`. `first` returns `nil` for empty input.

The flip side is worth knowing: laziness that usually helps can bite at an I/O boundary. `(take 5 (line-seq r))` inside `with-open` reads *after* the reader closes unless you force it — which is what the `doall` is for.
