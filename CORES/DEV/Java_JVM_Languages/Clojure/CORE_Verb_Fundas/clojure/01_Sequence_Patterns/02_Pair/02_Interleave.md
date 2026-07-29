# Pattern 7 — Interleave

## Mental Model

Combine **multiple sequences by alternating elements** from each sequence.

---

## Relationship to Cognitive Verb

```text
Pair
   ↓
Interleave
```

Interleave is a **Pair** pattern that combines sequences by taking **one element from each sequence in turn**.

---

## Clojure Functions & Common Idioms

|Variation|Example|Common Clojure|
|---|---|---|
|Interleave Two Sequences|`1 a 2 b 3 c`|`interleave xs ys`|
|Interleave Three Sequences|`1 a x 2 b y`|`interleave xs ys zs`|
|Interleave Until Shortest Ends|Default behavior|`interleave`|
|Separate (Reverse Interleave)|`(1 2 3) (a b c)`|`partition` + `take-nth` / `map`|
|Alternate Processing|`A B A B A B`|`interleave` + sequence operations|

---

## Common Uses

- Merge two event streams
    
- Alternate animation frames
    
- Stereo audio (Left, Right)
    
- RGB component layout
    
- UI layouts
    
- Round-robin scheduling
    
- Alternate turns in games
    
- Weaving two datasets
    

---

## Hidden Interview Problems

- Merge two arrays alternately
    
- Shuffle cards perfectly
    
- Round-robin task scheduling
    
- Alternate characters from two strings
    
- Weave linked lists
    
- Merge logs chronologically (alternating source)
    

---

## Recognition Clues

If you hear:

- Alternate
    
- Every other
    
- Weave
    
- Round-robin
    
- Left, Right
    
- A B A B
    
- Alternate turns
    
- Intermix
    

Think:

**→ Interleave**

---

## Pattern Summary

| Property        | Value                               |
| --------------- | ----------------------------------- |
| Cognitive Verb  | Pair                                |
| Pattern         | Interleave                          |
| Input           | Two or more sequences               |
| Output          | One alternating sequence            |
| Pairing Rule    | Take one from each sequence in turn |
| Stops At        | Shortest sequence                   |
| Preserves Order | Yes (within each sequence)          |