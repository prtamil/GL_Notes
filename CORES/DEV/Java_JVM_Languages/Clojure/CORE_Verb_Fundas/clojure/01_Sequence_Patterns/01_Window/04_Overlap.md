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