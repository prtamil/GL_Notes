# Pattern 4 — Overlapping Window

## Mental Model

Process **windows that intentionally share elements**. The amount of overlap can vary depending on the application.

> **Sliding Window is the most common type of Overlapping Window.**

---

## Relationship to Cognitive Verb

```text
Window
   ↓
Overlapping Window
```

Overlapping Window is a general pattern where consecutive windows reuse some of the previous elements.

---

## Clojure Functions & Common Variations

|Variation|Example|Clojure Function|
|---|---|---|
|1-element overlap|`(1 2 3) (3 4 5)`|`partition 3 2`|
|2-element overlap (Sliding)|`(1 2 3) (2 3 4)`|`partition 3 1`|
|Large overlap|`(1 2 3 4) (2 3 4 5)`|`partition 4 1`|
|Configurable overlap|Window = `n`, Step = `n - overlap`|`partition n step`|
|Keep Partial End|Include incomplete final window|`partition-all n step`|

---

## Common Uses

- Audio signal processing
    
- Image convolution
    
- Video frame analysis
    
- Speech recognition
    
- Time-series forecasting
    
- DNA sequence analysis
    
- Text n-grams
    
- Streaming analytics
    

---

## Hidden Interview Problems

- Moving averages
    
- Rolling statistics
    
- Consecutive pattern detection
    
- Window-based anomaly detection
    
- Sequence matching
    
- Time-series feature extraction
    

---

## Recognition Clues

If you hear:

- Overlapping data
    
- Shared neighbors
    
- Rolling window
    
- Reuse previous values
    
- Sliding analysis
    
- Context preservation
    
- Neighboring elements
    

Think:

**→ Overlapping Window**

---

## Pattern Summary

| Property            | Value                 |
| ------------------- | --------------------- |
| Cognitive Verb      | Window                |
| Pattern             | Overlapping Window    |
| Overlap             | Yes (configurable)    |
| Window Size         | Fixed                 |
| Step Size           | Less than Window Size |
| Preserves Order     | Yes                   |
| Covers All Elements | Usually Yes           |

---

## Clojure Recipe Book

```clojure
;; ============================================
;; Setup

(require '[clojure.set :as set])

(def xs [1 2 3 4 5 6 7 8 9 10])

;; ============================================
;; Say it in terms of overlap, not step
;;
;;   overlap = size - step        step = size - overlap
;;
;; partition speaks in steps. If your domain speaks in overlap
;; (DSP hop, tokenizer stride, embedding chunk overlap), convert once
;; at the boundary and stay in partition's language inside.

(defn windows
  "Windows of the given size that share `overlap` elements."
  [values size overlap]
  (when-not (and (pos? size) (<= 0 overlap) (< overlap size))
    (throw (ex-info "Window size or overlap is invalid"
                    {:size size :overlap overlap})))
  (partition size (- size overlap) values))

;; ============================================
;; 1-element overlap  (n=3, step=2)

(windows xs 3 1)
;; => ((1 2 3) (3 4 5) (5 6 7) (7 8 9))
;;          ^^^^^ 3 appears in two windows

;; ============================================
;; 2-element overlap = Sliding Window  (n=3, step=1)

(take 3 (windows xs 3 2))
;; => ((1 2 3) (2 3 4) (3 4 5))

;; ============================================
;; Large overlap  (n=4, step=1) — 75% shared

(take 3 (windows xs 4 3))
;; => ((1 2 3 4) (2 3 4 5) (3 4 5 6))

;; ============================================
;; No overlap → you have left the pattern; this is Chunk

(windows xs 3 0)
;; => ((1 2 3) (4 5 6) (7 8 9))

;; ============================================
;; 50% overlap — the audio/DSP default ("hop size = n/2")

(partition 4 2 xs)
;; => ((1 2 3 4) (3 4 5 6) (5 6 7 8) (7 8 9 10))

;; ============================================
;; Streaming overlap — again, nothing extra required

(take 2 (partition 4 2 (range)))
;; => ((0 1 2 3) (2 3 4 5))

;; Python needs a deque(maxlen=n) plus a countdown to emit a window
;; every `step` arrivals. partition is lazy, so the streaming version
;; is the same call you already wrote.

;; ============================================
;; Rolling statistics over overlapping windows

(take 3 (map #(double (/ (reduce + %) 4)) (partition 4 1 xs)))
;; => (2.5 3.5 4.5)                          rolling mean

(take 3 (map #(- (apply max %) (apply min %)) (partition 4 1 xs)))
;; => (3 3 3)                                rolling range

;; ============================================
;; Rolling standard deviation

(defn pstdev [ws]
  (let [mu (/ (reduce + ws) (count ws))]
    (Math/sqrt (double (/ (reduce + (map #(let [d (- % mu)] (* d d)) ws))
                          (count ws))))))

(take 3 (map #(-> (pstdev %) (* 1000) Math/round (/ 1000.0))
             (partition 4 1 xs)))
;; => (1.118 1.118 1.118)

;; ============================================
;; Anomaly detection — compare a point to its NEIGHBOURS

(defn anomalies
  ([xs] (anomalies xs 5 3.0))
  ([xs n k]
   (let [mid (quot n 2)]
     (keep-indexed
       (fn [i w]
         (let [w   (vec w)
               ctx (concat (subvec w 0 mid) (subvec w (inc mid)))  ; drop the centre
               mu  (/ (reduce + ctx) (count ctx))
               sd  (max (pstdev ctx) 1e-9)]
           (when (> (Math/abs (double (- (w mid) mu))) (* k sd))
             [(+ i mid) (w mid)])))
       (partition n 1 xs)))))

(anomalies [1 1 1 1 9 1 1 1 1])
;; => ([4 9])

;; Excluding the centre matters: a spike large enough to care about also
;; drags the mean and stdev of its own window, and can hide itself from
;; the test. Caveat: a perfectly flat context gives sd = 0, so the 1e-9
;; guard makes ANY deviation an anomaly. On real data pick a floor
;; on purpose.

;; ============================================
;; Character n-grams (overlap = n-1) — fuzzy matching, plagiarism

(defn ngrams [text size]
  (set (map (fn [characters] (apply str characters))
            (partition size 1 text))))

(let [a (ngrams "clojure" 3)
      b (ngrams "closure" 3)]
  (/ (count (set/intersection a b))
     (count (set/union a b))))
;; => 1/4        Jaccard similarity

;; note the exact ratio rather than 0.25 — call double on it if you
;; are feeding a threshold that expects a float

;; ============================================
;; Overlap-add — reconstruct a signal from windowed frames

(defn add-frame [hop output frame-index frame]
  (reduce (fn [result [sample-index sample]]
            (update result
                    (+ (* frame-index hop) sample-index)
                    +
                    sample))
          output
          (map-indexed vector frame)))

(defn overlap-add [frames hop]
  (let [frames (vec frames)]
    (if (empty? frames)
      []
      (let [frame-size (count (first frames))
            output-size (+ (* hop (dec (count frames))) frame-size)]
        (reduce-kv (partial add-frame hop)
                   (vec (repeat output-size 0))
                   frames)))))

(overlap-add [[1 1] [1 1] [1 1]] 1)
;; => [1 2 2 1]
;; the 2s are exactly where the windows overlapped

;; ============================================
;; Compare — overlap is derived, not primitive

(windows xs 3 2)       ; step 1 → Sliding
(windows xs 3 1)       ; step 2 → Jump, still overlapping
(windows xs 3 0)       ; step 3 → Chunk, no sharing
(partition 3 5 xs)     ; step > size → Gapped, data skipped (see 03_Jump)
```

---

### Memory Hooks

|You want|You reach for|
|---|---|
|overlap of k|`(partition n (- n k) xs)`|
|maximum overlap|`(partition n 1 xs)` → Sliding Window|
|50% overlap (DSP hop)|`(partition n (quot n 2) xs)`|
|no overlap|`(partition n n xs)` → Chunk|
|streaming overlap|`partition` — already lazy|
|rolling stat|`(map f (partition n 1 xs))`|
|put the pieces back|`overlap-add` into a zeroed vector|

---

### Key Insight

**Calculate overlap with `step = size - overlap`.** Digital signal processing, tokenizers, and chunked embeddings use the same calculation. Pass the calculated step to `partition`.

So why overlap at all? Because **windows destroy context at their edges.** An event sitting across a chunk boundary is invisible to both chunks. Overlap buys that context back, and it costs you `size / step` times the work. The question you are really tuning is "how much context do I need?", not "how big should the window be?".
