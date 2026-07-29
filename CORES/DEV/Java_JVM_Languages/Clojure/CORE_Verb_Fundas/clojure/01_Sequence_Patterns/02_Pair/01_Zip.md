# Pattern 6 — Zip

## Mental Model

Combine **multiple sequences element-by-element** into a single sequence of tuples.

---

## Relationship to Cognitive Verb

```text
Pair
   ↓
Zip
```

Zip is the simplest implementation of the **Pair** verb. It pairs corresponding elements from two or more sequences.

---

## Clojure Functions & Common Idioms

|Variation|Example|Common Clojure|
|---|---|---|
|Zip Two Sequences|`(1 a) (2 b) (3 c)`|`map vector xs ys`|
|Zip Three Sequences|`(1 a x)`|`map vector xs ys zs`|
|Zip with Function|`(1 10) → 11`|`map + xs ys`|
|Zip with Index|`(0 a) (1 b) (2 c)`|`map-indexed vector xs`|
|Zip Keys & Values|`{:a 1 :b 2}`|`zipmap keys vals`|
|Zip Until Shortest Ends|Default behavior|`map`|

---

## Common Uses

- Pair IDs with values
    
- Combine names and scores
    
- Merge columns
    
- Join parallel arrays
    
- Create coordinate pairs `(x, y)`
    
- Build key-value maps
    
- Combine timestamps with events
    
- Pair labels with predictions
    

---

## Hidden Interview Problems

- Merge two sorted results
    
- Create coordinate points
    
- Associate IDs with objects
    
- Build dictionaries/maps
    
- Pair questions with answers
    
- Combine parallel datasets
    

---

## Recognition Clues

If you hear:

- Corresponding elements
    
- Pair two arrays
    
- Parallel lists
    
- Match positions
    
- Combine columns
    
- X and Y coordinates
    
- Keys and values
    
- Element-wise combine
    

Think:

**→ Zip**

---

## Pattern Summary

| Property        | Value                                          |
| --------------- | ---------------------------------------------- |
| Cognitive Verb  | Pair                                           |
| Pattern         | Zip                                            |
| Input           | Two or more sequences                          |
| Output          | One sequence of tuples (or transformed values) |
| Pairing Rule    | Same index                                     |
| Stops At        | Shortest sequence                              |
| Preserves Order | Yes                                            |