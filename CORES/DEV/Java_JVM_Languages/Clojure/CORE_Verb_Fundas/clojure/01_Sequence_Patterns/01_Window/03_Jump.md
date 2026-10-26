# Pattern 3 — Jump Window (Strided Window)

## Mental Model

Move a **fixed-size window** through a sequence by **jumping multiple elements** each time. Windows may overlap, touch, or have gaps depending on the jump size.

---

## Relationship to Cognitive Verb

```text
Window
   ↓
Jump Window
```

Jump Window is a **Window** pattern where the window advances by a **fixed stride greater than one**.

---

## Clojure Functions & Common Variations

|Variation|Example|Clojure Function|
|---|---|---|
|Jump 2, Window 3|`(1 2 3) (3 4 5) (5 6 7)`|`partition 3 2`|
|Jump 3, Window 4|`(1 2 3 4) (4 5 6 7)`|`partition 4 3`|
|Jump = Window (Chunk)|`(1 2 3) (4 5 6)`|`partition 3 3`|
|Jump > Window (Gapped)|`(1 2) (5 6) (9 10)`|`partition 2 4`|
|Keep Partial End|Include incomplete final window|`partition-all n step`|

---

## Common Uses

- Downsampling signals
    
- Video frame sampling
    
- Processing every Nth record
    
- Sparse feature extraction
    
- Time-series sampling
    
- Data compression
    
- Game AI tick processing
    
- Large dataset sampling
    

---

## Hidden Interview Problems

- Process every Kth element
    
- Analyze every Nth frame
    
- Sample logs periodically
    
- Downsample sensor readings
    
- Feature extraction from streams
    
- Efficient large-scale scanning
    

---

## Recognition Clues

If you hear:

- Every **K** elements
    
- Skip **N**
    
- Sample periodically
    
- Jump ahead
    
- Stride
    
- Downsample
    
- Every third frame
    
- Every fifth record
    

Think:

**→ Jump Window**

---

## Pattern Summary

| Property            | Value                |
| ------------------- | -------------------- |
| Cognitive Verb      | Window               |
| Pattern             | Jump Window          |
| Overlap             | Depends on stride    |
| Window Size         | Fixed                |
| Step Size           | Any positive integer |
| Preserves Order     | Yes                  |
| Covers All Elements | Not necessarily      |

---

## Clojure Recipe Book

```clojure
;; ============================================
;; Setup

(def xs [1 2 3 4 5 6 7 8 9 10])

;; ============================================
;; The one function that covers every case
;;
;;   (partition size step coll)
;;
;; Python needs a helper with a `partial` flag and a hand-computed
;; range stop. Clojure needs two arguments. Everything below is this
;; one call with different numbers.

;; ============================================
;; Jump 2, Window 3 — overlapping by 1

(partition 3 2 xs)
;; => ((1 2 3) (3 4 5) (5 6 7) (7 8 9))

;; ============================================
;; Jump 3, Window 4 — overlapping by 1

(partition 4 3 xs)
;; => ((1 2 3 4) (4 5 6 7) (7 8 9 10))

;; ============================================
;; Jump == Window → this is just Chunk

(partition 3 3 xs)
;; => ((1 2 3) (4 5 6) (7 8 9))          ; 10 dropped

(partition-all 3 3 xs)
;; => ((1 2 3) (4 5 6) (7 8 9) (10))     ; 10 kept

;; ============================================
;; Jump > Window → gaps, elements are skipped entirely

(partition 2 4 xs)
;; => ((1 2) (5 6) (9 10))
;;      ^^^^      3,4 and 7,8 are never seen

;; ============================================
;; Keep the partial final window

(partition-all 3 4 xs)
;; => ((1 2 3) (5 6 7) (9 10))

;; partition drops a short final window, partition-all keeps it.
;; Same distinction as everywhere else in this family.

;; ============================================
;; Window of 1 → plain sampling

(take-nth 3 xs)              ;; => (1 4 7 10)
(take-nth 3 (rest xs))       ;; => (2 5 8)      (phase offset 1)

;; take-nth IS the jump when the window is a single element.
;; Note it takes the collection LAST, so it threads and composes.

;; ============================================
;; Lazy stride over a stream — nothing extra required

(take 3 (partition 3 2 (range)))
;; => ((0 1 2) (2 3 4) (4 5 6))

;; Python needs a jump_lazy generator that reuses the tail when
;; step < n and burns the gap when step > n. partition already
;; does both, lazily, for any combination.

;; ============================================
;; Downsample: one value per window

(map #(double (/ (reduce + %) (count %))) (partition 3 3 xs))
;; => (2.0 5.0 8.0)

(map #(apply max %) (partition 4 2 xs))
;; => (4 6 8 10)                          ; peak-preserving downsample

;; ============================================
;; Process every Nth record, keeping the index

(keep-indexed (fn [i x] (when (zero? (mod i 3)) x)) xs)
;; => (1 4 7 10)

;; same result as take-nth, but you still have i if you need it

;; ============================================
;; Sampling from a stream of unknown length

(count (take-nth 250 (range 1000000)))
;; => 4000

;; lazy the whole way: no million-element sequence is ever realized

;; ============================================
;; Compare — the whole Window family in four lines

(partition 3 1 xs)     ; step < size   → Sliding / Overlapping
(partition 3 3 xs)     ; step == size  → Chunk
(partition 3 5 xs)     ; step > size   → Gapped, skips data
(take-nth 3 xs)        ; size 1        → Sample / Stride
```

---

### Memory Hooks

|You want|You reach for|
|---|---|
|windows of n every k|`(partition n k xs)`|
|include the ragged tail|`(partition-all n k xs)`|
|every kth element|`(take-nth k xs)`|
|every kth, offset by j|`(take-nth k (drop j xs))`|
|every kth, lazily|`(take-nth k …)` — already lazy|
|every kth, keeping the index|`(keep-indexed …)`|
|no overlap at all|`step >= size`|
|nothing skipped|`step <= size`|

---

### Key Insight

**The step value selects the window pattern.** Step `1` gives sliding windows. Step `n` gives chunks. A step greater than `n` gives gaps.

A practical warning that survives the translation: once `step > size`, you are **throwing data away silently**. That is exactly what you want when downsampling and a bug everywhere else. Bind the step to a named value rather than burying a magic number in the call, so the intent is visible at the call site.
