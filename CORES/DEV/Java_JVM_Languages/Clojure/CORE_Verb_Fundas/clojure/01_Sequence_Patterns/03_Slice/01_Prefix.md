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