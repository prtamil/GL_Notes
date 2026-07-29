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
((1 1 1)
 (2 2)
 (3 3 3 3)
 (4))


;;--------------------------------------------------------
;; Basic Run-Length Encoding
;;--------------------------------------------------------

(map (fn [grp]
       [(first grp) (count grp)])
     (partition-by identity xs))

;; =>
([1 3]
 [2 2]
 [3 4]
 [4 1])


;;--------------------------------------------------------
;; Compress Characters
;;--------------------------------------------------------

(map (fn [grp]
       [(first grp) (count grp)])
     (partition-by identity "aaabbccccd"))

;; =>
([\a 3]
 [\b 2]
 [\c 4]
 [\d 1])


;;--------------------------------------------------------
;; Keep Only Run Lengths
;;--------------------------------------------------------

(map count
     (partition-by identity xs))

;; =>
(3 2 4 1)


;;--------------------------------------------------------
;; Keep Only Run Values
;;--------------------------------------------------------

(map first
     (partition-by identity xs))

;; =>
(1 2 3 4)


;;--------------------------------------------------------
;; Decode Run-Length Encoding
;;--------------------------------------------------------

(mapcat (fn [[v n]]
          (repeat n v))
        [[1 3] [2 2] [3 4] [4 1]])

;; =>
(1 1 1
 2 2
 3 3 3 3
 4)


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
(1 1 1 2 2 3 3 3 3 4)


;;--------------------------------------------------------
;; Compression Ratio
;;--------------------------------------------------------

(let [encoded (map (fn [grp]
                     [(first grp) (count grp)])
                   (partition-by identity xs))]
  [(count xs)
   (count encoded)])

;; =>
[10 4]


;;--------------------------------------------------------
;; Run Statistics
;;--------------------------------------------------------

(map (fn [grp]
       {:value (first grp)
        :count (count grp)})
     (partition-by identity xs))

;; =>
({:value 1 :count 3}
 {:value 2 :count 2}
 {:value 3 :count 4}
 {:value 4 :count 1})
```