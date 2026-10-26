# Pattern 2 — Sliding Window

## Mental Model

Move a **fixed-size window** through a sequence **one element at a time**. Consecutive windows **share (overlap)** most of their elements.

---

## Relationship to Cognitive Verb

```text
Window
   ↓
Sliding Window
```

Sliding Window is a **Window** pattern where the window advances by **one position** each step.

---

## Clojure Functions & Common Variations

|Variation|Example|Clojure Function|
|---|---|---|
|Sliding Window (size 2)|`(1 2) (2 3) (3 4)`|`partition 2 1`|
|Sliding Window (size 3)|`(1 2 3) (2 3 4)`|`partition 3 1`|
|Sliding Window (size N)|Overlapping windows|`partition n 1`|
|Sliding Window (keep partial end)|`(1 2 3) (2 3) (3)`|`partition-all n 1`|

---

## Common Uses

- Moving average
    
- Time-series analysis
    
- Signal processing
    
- Image filters (convolution)
    
- Video frame analysis
    
- Text n-grams
    
- DNA sequence analysis
    
- Network traffic monitoring
    
- Sensor data streams
    

---

## Hidden Interview Problems

- Maximum sum subarray of size K
    
- Longest substring without duplicates
    
- Minimum window substring
    
- Sliding window maximum
    
- Moving average
    
- Consecutive pattern detection
    
- Fraud detection over recent transactions
    

---

## Recognition Clues

If you hear:

- Moving
    
- Rolling
    
- Recent **N**
    
- Last **K**
    
- Consecutive elements
    
- Running window
    
- Window slides
    
- Neighboring values
    

Think:

**→ Sliding Window**

---

## Pattern Summary

|Property|Value|
|---|---|
|Cognitive Verb|Window|
|Pattern|Sliding Window|
|Overlap|Yes|
|Window Size|Fixed|
|Step Size|1|
|Preserves Order|Yes|
|Covers All Elements|Yes (except incomplete tail unless using `partition-all`)|

---

## Clojure Recipe Book

```clojure
;; ============================================
;; Setup

(require '[clojure.string :as str])

(def xs [1 2 3 4 5])

;; ============================================
;; Window of 2 — the one you use most

(partition 2 1 xs)
;; => ((1 2) (2 3) (3 4) (4 5))

;; ============================================
;; Window of 3 — same function, same step

(partition 3 1 xs)
;; => ((1 2 3) (2 3 4) (3 4 5))

;; ============================================
;; Window of N

(partition 3 1 xs)     ; n = 3
(partition 4 1 xs)     ; n = 4

;; There is no off-by-one to memorise. Python needs
;; (range (- (count xs) n -1)) to count its windows;
;; partition works it out and stops on its own.

;; ============================================
;; The zip-of-offsets view — same result, different picture

(map vector xs (rest xs))
;; => ([1 2] [2 3] [3 4] [4 5])

(map vector xs (rest xs) (nnext xs))
;; => ([1 2 3] [2 3 4] [3 4 5])

;; column i is the sequence offset by i, and map stops at the
;; shortest. Worth seeing once because it explains WHY the window
;; count is (- (count xs) n -1) — but reach for partition in real code.

;; ============================================
;; Streaming and infinite sources — no separate implementation

(take 3 (partition 3 1 (range)))
;; => ((0 1 2) (1 2 3) (2 3 4))

;; This is the big one. Python needs a deque(maxlen=n) loop or an
;; itertools.tee trick to slide over a stream. partition is lazy, so
;; the streaming version and the vector version are the same code.

;; ============================================
;; Keep the shrinking tail

(partition-all 3 1 xs)
;; => ((1 2 3) (2 3 4) (3 4 5) (4 5) (5))

;; ============================================
;; Moving average

(map #(double (/ (reduce + %) 3)) (partition 3 1 xs))
;; => (2.0 3.0 4.0)

;; ============================================
;; Rolling sum in O(n) — add the new, drop the old

(defn rolling-sum [values window-size]
  (when-not (pos? window-size)
    (throw (ex-info "Window size must be positive"
                    {:window-size window-size})))
  (let [values (vec values)]
    (if (> window-size (count values))
      ()
      (reductions
        (fn [total index]
          (+ total
             (values index)
             (- (values (- index window-size)))))
        (reduce + (take window-size values))
        (range window-size (count values))))))

(rolling-sum xs 3)
;; => (6 9 12)

;; This is THE sliding-window optimization: recompute the delta,
;; not the window. reductions is the natural fit — it carries the
;; running total and emits every intermediate value, which is
;; exactly the shape of the problem.

;; the naive version re-adds the whole window every step:
(map #(reduce + %) (partition 3 1 xs))   ; O(n*k) — correct but wasteful

;; ============================================
;; Maximum sum subarray of size K

(apply max (rolling-sum xs 3))          ;; => 12

;; ============================================
;; Sliding window maximum — monotonic deque, O(n)

(defn drop-weaker-indexes [candidate-indexes values current-value]
  (loop [indexes candidate-indexes]
    (if (and (seq indexes)
             (<= (values (peek indexes)) current-value))
      (recur (pop indexes))
      indexes)))

(defn drop-expired-index [candidate-indexes index window-size]
  (if (and (seq candidate-indexes)
           (<= (first candidate-indexes) (- index window-size)))
    (subvec candidate-indexes 1)
    candidate-indexes))

(defn window-max [values window-size]
  (when-not (pos? window-size)
    (throw (ex-info "Window size must be positive"
                    {:window-size window-size})))
  (let [values (vec values)]
    (second
      (reduce
        (fn [[candidate-indexes maximums] index]
          (let [current-value (values index)
                stronger-indexes
                (drop-weaker-indexes candidate-indexes values current-value)
                candidate-indexes
                (-> stronger-indexes
                    (conj index)
                    (drop-expired-index index window-size))]
            [candidate-indexes
             (if (>= index (dec window-size))
               (conj maximums (values (first candidate-indexes)))
               maximums)]))
        [[] []]
        (range (count values))))))

(window-max [1 3 -1 -3 5 3 6 7] 3)
;; => [3 3 5 5 6 7]

;; a vector doubles as the deque: peek/pop work the back,
;; `first` and `subvec` work at the front. The candidate vector holds
;; indices whose values are strictly decreasing, so the front is
;; always the window's maximum.

;; ============================================
;; Variable-size window — longest substring without repeats

(defn longest-unique [text]
  (:best-length
    (reduce
      (fn [{:keys [last-index left best-length]}
           [right character]]
        (let [previous-index (last-index character)
              next-left (if (and previous-index
                                 (>= previous-index left))
                          (inc previous-index)
                          left)
              current-length (inc (- right next-left))]
          {:last-index (assoc last-index character right)
           :left next-left
           :best-length (max best-length current-length)}))
      {:last-index {} :left 0 :best-length 0}
      (map-indexed vector text))))

(longest-unique "abcabcbb")     ;; => 3
(longest-unique "bbbbb")        ;; => 1
(longest-unique "pwwkew")       ;; => 3

;; Two pointers = a window whose size is decided by the data, not by n.
;; The state that a Python loop keeps in three mutable locals becomes
;; one map threaded through reduce.

;; ============================================
;; Text n-grams

(->> (str/split "the quick brown fox jumps" #" ")
     (partition 2 1)
     (map #(str/join " " %)))
;; => ("the quick" "quick brown" "brown fox" "fox jumps")

;; ============================================
;; Compare

(partition 2 1 xs)     ; size 2, step 1  → ((1 2) (2 3) (3 4) (4 5))
(partition 3 1 xs)     ; size 3, step 1  → overlap
(partition 3 3 xs)     ; size 3, step 3  → chunk, no overlap → ((1 2 3))
(take-nth 3 xs)        ; every 3rd item, no window → (1 4)
```

---

### Memory Hooks

|You want|You reach for|
|---|---|
|neighbours, size 2|`(partition 2 1 xs)`|
|size n, any input|`(partition n 1 xs)`|
|size n, keep shrinking tail|`(partition-all n 1 xs)`|
|size n over a stream|`(partition n 1 …)` — already lazy|
|the offset-columns view|`(map vector xs (rest xs) …)`|
|rolling sum in O(n)|`reductions` with `(+ total (- new old))`|
|window max in O(n)|monotonic vector-as-deque of indices|
|window size set by data|`reduce` carrying `{:left … :seen …}`|

---

### Key Insight

**A sliding window can reduce O(n·k) work to O(n).** Update the window summary after each step. Do not calculate the complete summary again.

Clojure uses `partition` for the complete fixed-size window family. Laziness lets the same code process vectors and infinite sequences. Data-dependent window sizes use two pointers and a small state value.
