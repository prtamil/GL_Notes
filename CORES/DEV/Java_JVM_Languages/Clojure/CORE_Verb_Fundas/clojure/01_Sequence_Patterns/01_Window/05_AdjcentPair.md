# Pattern 5 — Adjacent Pair

## Mental Model

Process **neighboring elements** together to compare, transform, or detect transitions.

---

## Relationship to Cognitive Verb

```text
Window
   ↓
Adjacent Pair
```

Adjacent Pair is a specialized **Sliding Window** where the **window size is always 2**.

---

## Clojure Functions & Common Idioms

| Variation                          | Example             | Common Clojure                                      |
| ---------------------------------- | ------------------- | --------------------------------------------------- |
| Forward Pair (Current → Next)      | `(1 2) (2 3) (3 4)` | `partition 2 1`                                     |
| Forward Pair (keep partial tail)   | `(1 2) (2 3) (3)`   | `partition-all 2 1`                                 |
| Current + Next                     | `(curr next)`       | `(map vector xs (rest xs))`                         |
| Previous + Current                 | `(prev curr)`       | `(map vector xs (rest xs))` _(viewed from current)_ |
| Previous + Current + Next          | `(prev curr next)`  | `partition 3 1`                                     |
| Compare Adjacent Values            | `(< curr next)`     | `partition 2 1` + `map`                             |
| Difference Between Adjacent Values | `(- next curr)`     | `partition 2 1` + `map`                             |
| Adjacent with Index                | `(idx curr next)`   | `map-indexed` + `rest`                              |
|                                    |                     |                                                     |
|                                    |                     |                                                     |
> **Note:** `Current + Next` and `Previous + Current` use the **same Clojure idiom**: `(map vector xs (rest xs))`, which produces `(10 20) (20 30) (30 40)`. The difference is **how you interpret each pair**. If you stand on the **first element**, each pair means **(current next)**—"I'm at 10, the next is 20." If you stand on the **second element**, the same pair means **(previous current)**—"I'm at 20, the previous was 10." The implementation is identical; only the mental perspective changes depending on the problem you're solving.
---

## Common Uses

- Compare neighboring values
    
- Consecutive differences (delta)
    
- Trend detection
    
- Transition detection
    
- Sortedness checking
    
- Duplicate detection
    
- Velocity from positions
    
- Line / edge construction
    
- Change-point detection
    

---

## Hidden Interview Problems

- Check if an array is sorted
    
- Find adjacent duplicates
    
- Compute differences between consecutive values
    
- Count increasing/decreasing pairs
    
- Detect peaks and valleys
    
- Find transition points
    
- Compare neighboring timestamps
    

---

## Recognition Clues

If you hear:

- Previous element
    
- Next element
    
- Neighbor
    
- Adjacent
    
- Consecutive
    
- Delta
    
- Transition
    
- Compare with previous
    
- Compare with next
    
- Pairwise
    

Think:

**→ Adjacent Pair**

---

## Pattern Summary

|Property|Value|
|---|---|
|Cognitive Verb|Window|
|Pattern|Adjacent Pair|
|Overlap|Yes|
|Window Size|2 (or 3 for both neighbors)|
|Step Size|1|
|Preserves Order|Yes|
|Covers All Elements|Yes (except boundaries unless handled explicitly)|

