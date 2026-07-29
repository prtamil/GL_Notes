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