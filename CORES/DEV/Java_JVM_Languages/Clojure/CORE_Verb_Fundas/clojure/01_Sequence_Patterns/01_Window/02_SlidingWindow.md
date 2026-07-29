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