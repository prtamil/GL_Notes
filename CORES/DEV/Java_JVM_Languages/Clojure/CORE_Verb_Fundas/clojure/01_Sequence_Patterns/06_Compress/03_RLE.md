# Pattern 19 — Run-Length Encoding (RLE)

## Mental Model

Compress a sequence by replacing each **run of consecutive identical elements** with **(value, count)**.

Instead of storing repeated values, store **what the value is** and **how many times it repeats**.

---

## Relationship to Cognitive Verb

```text
Compress
    ↓
Run-Length Encoding
```

Run-Length Encoding is a **Compress** pattern that summarizes **runs** into compact `(value, count)` pairs.

---

## Clojure Functions & Common Idioms

|Variation|Example|Common Clojure|
|---|---|---|
|Encode Runs|`AAA → [A 3]`|`partition-by` + `map`|
|Count Runs|`AAA BB C`|`partition-by` + `count`|
|Decode RLE|`[A 3] → AAA`|`mapcat` + `repeat`|
|Compress Characters|`"aaabb"`|`partition-by`|
|Compress Numbers|`111223`|`partition-by`|

> **Note:** RLE only compresses **consecutive duplicates**. It does not remove duplicates separated by other values.

---

## Common Uses

- Simple lossless compression
    
- Bitmap/image compression
    
- DNA sequences
    
- Log compression
    
- Sensor data
    
- Character compression
    
- Data serialization
    
- Network protocols
    

---

## Hidden Interview Problems

- String compression
    
- Compress repeated characters
    
- Encode repeated numbers
    
- Count consecutive values
    
- Decode compressed data
    
- Run statistics
    

---

## Recognition Clues

If you hear:

- Compress repeated values
    
- Count consecutive items
    
- String compression
    
- Encode runs
    
- Value and frequency
    
- Consecutive repetitions
    

Think:

**→ Run-Length Encoding**

---

## Pattern Summary

|Property|Value|
|---|---|
|Cognitive Verb|Compress|
|Pattern|Run-Length Encoding|
|Compresses|Consecutive duplicates|
|Output|`(value count)` pairs|
|Preserves Order|Yes|
|Compression Type|Lossless|

---

## Clojure Recipe Book

```clojure
;;--------------------------------------------------------
;; Input
;;--------------------------------------------------------

(def xs [1 1 1 2 2 3 3 3 3 4])


;;--------------------------------------------------------
;; Partition into Runs
;;--------------------------------------------------------

(partition-by identity xs)

;; =>
;; ((1 1 1)
 ;; (2 2)
 ;; (3 3 3 3)
 ;; (4))


;;--------------------------------------------------------
;; Basic Run-Length Encoding
;;--------------------------------------------------------

(map (fn [grp]
       [(first grp) (count grp)])
     (partition-by identity xs))

;; =>
;; ([1 3]
 ;; [2 2]
 ;; [3 4]
 ;; [4 1])


;;--------------------------------------------------------
;; Compress Characters
;;--------------------------------------------------------

(map (fn [grp]
       [(first grp) (count grp)])
     (partition-by identity "aaabbccccd"))

;; =>
;; ([\a 3]
 ;; [\b 2]
 ;; [\c 4]
 ;; [\d 1])


;;--------------------------------------------------------
;; Keep Only Run Lengths
;;--------------------------------------------------------

(map count
     (partition-by identity xs))

;; =>
;; (3 2 4 1)


;;--------------------------------------------------------
;; Keep Only Run Values
;;--------------------------------------------------------

(map first
     (partition-by identity xs))

;; =>
;; (1 2 3 4)


;;--------------------------------------------------------
;; Decode Run-Length Encoding
;;--------------------------------------------------------

(mapcat (fn [[v n]]
          (repeat n v))
        [[1 3] [2 2] [3 4] [4 1]])

;; =>
;; (1 1 1
 ;; 2 2
 ;; 3 3 3 3
 ;; 4)


;;--------------------------------------------------------
;; Encode then Decode
;;--------------------------------------------------------

(->> xs
     (partition-by identity)
     (map (fn [grp]
            [(first grp) (count grp)]))
     (mapcat (fn [[v n]]
               (repeat n v))))

;; =>
;; (1 1 1 2 2 3 3 3 3 4)


;;--------------------------------------------------------
;; Compression Ratio
;;--------------------------------------------------------

(let [encoded (map (fn [grp]
                     [(first grp) (count grp)])
                   (partition-by identity xs))]
  [(count xs)
   (count encoded)])

;; =>
;; [10 4]


;;--------------------------------------------------------
;; Run Statistics
;;--------------------------------------------------------

(map (fn [grp]
       {:value (first grp)
        :count (count grp)})
     (partition-by identity xs))

;; =>
;; ({:value 1 :count 3}
 ;; {:value 2 :count 2}
 ;; {:value 3 :count 4}
 ;; {:value 4 :count 1})
```

---

### Readable Clojure Functions

```clojure
(defn encode-run [run]
  [(first run) (count run)])

(defn encode-runs [values]
  (map encode-run (partition-by identity values)))

(defn decode-runs [encoded]
  (mapcat (fn [[value run-length]]
            (repeat run-length value))
          encoded))

(defn describe-run [key-fn run]
  {:key (key-fn (first run))
   :count (count run)
   :items (vec run)})

(defn encode-runs-by [key-fn values]
  (map (partial describe-run key-fn)
       (partition-by key-fn values)))

(defn compression-ratio [values]
  (if (empty? values)
    1.0
    (/ (double (count (encode-runs values)))
       (count values))))

(defn longest-encoded-run [values]
  (when-let [encoded (seq (encode-runs values))]
    (apply max-key second encoded)))

(defn encode-repeated-messages [messages]
  (map (fn [[message repetitions]]
         (if (= repetitions 1)
           message
           (str message " (x" repetitions ")")))
       (encode-runs messages)))

(def encoded (encode-runs "aaabbccccd"))

encoded
;; => ([\a 3] [\b 2] [\c 4] [\d 1])

(apply str (decode-runs encoded))
;; => "aaabbccccd"

(= (seq "aaabbccccd")
   (seq (decode-runs encoded)))
;; => true
```

Because `partition-by` and `map` are lazy, this encoder can process a stream one completed run at a time. An infinite run can never finish and therefore cannot emit its count—an unavoidable property of run-length encoding.

### Memory Hooks

|You want|You reach for|
|---|---|
|adjacent runs|`partition-by identity`|
|encode|`[first count]` for each run|
|decode|`mapcat repeat`|
|encode by a field|`partition-by key-fn`|
|verify correctness|decode after encode and compare|
|judge usefulness|compare encoded entries with input size|

### Key Insight

Run-length encoding preserves order and is reversible. A histogram does not preserve order. Measure the compression ratio because alternating data can become larger.
