# 6. Zigzag Traversal

## Mental Model

Zigzag traversal visits the matrix by **alternating the traversal direction** after each line. Instead of always moving in the same direction, the traversal **bounces back and forth**.

The line being traversed can be rows, columns, or diagonals. The most famous zigzag pattern is the **JPEG diagonal zigzag scan**.

---

## Relationship to Cognitive Verb

```text
Alternate
     ↓
Zigzag Traversal
```

Related verbs:

- Alternate direction
    
- Bounce
    
- Reverse every pass
    
- Sweep back and forth
    
- Oscillate
    

---

## Clojure Functions & Common Idioms

|Variation|Example|Common Clojure|
|---|---|---|
|Row zigzag|alternate rows|`map-indexed`, `reverse`|
|Column zigzag|alternate columns|`apply map vector`, `reverse`|
|Diagonal zigzag|JPEG ordering|`loop/recur`|
|Alternate direction|even/odd test|`even?`, `odd?`|
|Flatten result|produce sequence|`mapcat`, `concat`|

---

## Common Uses

- JPEG image compression
    
- Matrix serialization
    
- Robot sweep patterns
    
- Raster scanning
    
- Cache-friendly processing
    
- Game AI search
    
- Hardware image sensors
    
- Scientific visualization
    

---

## Hidden Interview Problems

- Print matrix in zigzag order
    
- Alternate every row
    
- Zigzag level traversal
    
- JPEG scan ordering
    
- Reverse alternate rows
    
- Serialize matrix
    
- Snake vs Zigzag comparison
    

---

## Recognition Clues

If you hear...

- "alternate direction..."
    
- "back and forth..."
    
- "reverse every row..."
    
- "bounce..."
    
- "zigzag..."
    

...think **Zigzag Traversal**.

---

## Pattern Summary

|Property|Value|
|---|---|
|Dimension|2D|
|Traversal Unit|Row, Column, or Diagonal|
|Direction|Alternating|
|Coordinate Rule|Reverse every other pass|
|Time Complexity|O(rows × cols)|
|Space Complexity|O(1) extra (excluding output)|
|Common Domains|JPEG, graphics, robotics|

---

## Clojure Recipe Book

```clojure
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;; Basic matrix

(def m
  [[1 2 3 4]
   [5 6 7 8]
   [9 10 11 12]
   [13 14 15 16]])

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;; Zigzag by rows

(map-indexed
 (fn [i row]
   (if (even? i)
     row
     (reverse row)))
 m)

;; =>
;; ((1 2 3 4)
;;  (8 7 6 5)
;;  (9 10 11 12)
;;  (16 15 14 13))

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;; Flatten zigzag traversal

(mapcat identity
        (map-indexed
         (fn [i row]
           (if (even? i)
             row
             (reverse row)))
         m))

;; =>
;; (1 2 3 4
;;  8 7 6 5
;;  9 10 11 12
;; 16 15 14 13)

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;; Zigzag by columns

(def cols
  (apply map vector m))

(map-indexed
 (fn [i col]
   (if (even? i)
     col
     (reverse col)))
 cols)

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;; Generic alternating pattern

(map-indexed
 (fn [i xs]
   (if (even? i)
     xs
     (reverse xs)))
 collection)

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;; Explicit traversal

(doseq [[i row]
        (map-indexed vector m)]
  (doseq [x (if (even? i)
              row
              (reverse row))]
    (println x)))

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;; Compare

;; Always forward
(mapcat identity m)

;; Alternate direction
(mapcat identity
        (map-indexed
          (fn [i row]
            (if (even? i)
              row
              (reverse row)))
          m))
```

---

## Key Insight

The defining idea of zigzag traversal is **alternating direction**.

```text
→→→→
←←←←
→→→→
←←←←
```

Unlike spiral traversal, which changes **boundaries**, zigzag traversal changes only the **direction of travel** after each pass.

The traversal unit can be:

|Unit|Example|
|---|---|
|Row|Read left→right, then right→left|
|Column|Read top→bottom, then bottom→top|
|Diagonal|JPEG zigzag ordering|

Think of zigzag as the general pattern:

```text
Forward
   ↓
Reverse
   ↓
Forward
   ↓
Reverse
```

> **Mental shift:** Zigzag traversal is not about _where_ you move next; it's about _changing the direction_ of each successive sweep.

---

### Zigzag vs Snake

Although many resources use the terms interchangeably, it's useful to distinguish them conceptually:

|Pattern|Primary Idea|
|---|---|
|**Zigzag**|Alternate the direction of each traversal unit (rows, columns, or diagonals). The concept is general.|
|**Snake**|A specific zigzag where the traversal unit is **rows** (or sometimes columns), producing a continuous snake-like path.|

In this course, we'll treat **Snake Traversal** as a specialized form of zigzag because it appears frequently in graphics, game maps, and interview problems.

---
