# 8. Boundary Traversal

## Mental Model

Boundary traversal visits **only the outer border** of a matrix, ignoring all interior cells.

Unlike spiral traversal, which repeatedly peels inward, boundary traversal processes **exactly one ring**—the outermost perimeter.

---

## Relationship to Cognitive Verb

```text
Outline
    ↓
Boundary Traversal
```

Related verbs:

- Outline
    
- Trace the border
    
- Walk the perimeter
    
- Follow the edge
    
- Visit the frame
    

---

## Clojure Functions & Common Idioms

|Variation|Example|Common Clojure|
|---|---|---|
|Top edge|first row|`first`, `for`|
|Bottom edge|last row|`last`, `for`|
|Left edge|first column|`map`, `first`|
|Right edge|last column|`map`, `last`|
|Clockwise boundary|complete border|`concat`, `for`|
|Counter-clockwise|reverse order|`reverse`, `concat`|

---

## Common Uses

- Image border detection
    
- Frame rendering
    
- Map boundaries
    
- Collision boundaries
    
- Grid visualization
    
- Maze entrances
    
- Geographic borders
    
- UI outlines
    

---

## Hidden Interview Problems

- Print matrix boundary
    
- Sum boundary elements
    
- Count perimeter cells
    
- Draw rectangular border
    
- Rotate boundary elements
    
- Compare boundary values
    
- Boundary maximum/minimum
    
- Extract matrix frame
    

---

## Recognition Clues

If you hear...

- "outer boundary..."
    
- "border..."
    
- "perimeter..."
    
- "frame..."
    
- "outer ring only..."
    

...think **Boundary Traversal**.

---

## Pattern Summary

|Property|Value|
|---|---|
|Dimension|2D|
|Traversal Unit|Outer Boundary|
|Direction|Usually Clockwise|
|Coordinate Rule|First/Last row or column|
|Time Complexity|O(rows + cols)|
|Space Complexity|O(1) extra|
|Common Domains|Graphics, maps, UI, games|

---

## Clojure Recipe Book

```clojure
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;; Basic matrix

(def m
  [[1  2  3  4]
   [5  6  7  8]
   [9 10 11 12]
   [13 14 15 16]])

(def rows (count m))
(def cols (count (first m)))

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;; Top edge

(for [c (range cols)]
  (get-in m [0 c]))

;; => (1 2 3 4)

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;; Right edge

(for [r (range 1 rows)]
  (get-in m [r (dec cols)]))

;; => (8 12 16)

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;; Bottom edge

(for [c (reverse (range (dec cols)))]
  (get-in m [(dec rows) c]))

;; => (15 14 13)

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;; Left edge

(for [r (reverse (range 1 (dec rows)))]
  (get-in m [r 0]))

;; => (9 5)

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;; Complete clockwise boundary

(concat

 ;; top
 (for [c (range cols)]
   (get-in m [0 c]))

 ;; right
 (for [r (range 1 rows)]
   (get-in m [r (dec cols)]))

 ;; bottom
 (for [c (reverse (range (dec cols)))]
   (get-in m [(dec rows) c]))

 ;; left
 (for [r (reverse (range 1 (dec rows)))]
   (get-in m [r 0])))

;; =>
;; (1 2 3 4
;;  8 12 16
;; 15 14 13
;; 9 5)

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;; Boundary sum

(reduce +
        (concat
          ...boundary...))

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;; Compare

;; Entire matrix
(mapcat identity m)

;; Boundary only
(concat top right bottom left)
```

---

## Key Insight

Boundary traversal is simply walking around the **perimeter** of the matrix.

```text
Top Edge
    ↓
Right Edge
    ↓
Bottom Edge
    ↓
Left Edge
```

The traversal always consists of the same four logical segments:

1. Top row
    
2. Right column
    
3. Bottom row (reverse)
    
4. Left column (reverse)
    

Unlike **Spiral Traversal**, you **stop after one complete circuit**.

---

## Boundary vs Spiral

|Pattern|Core Idea|
|---|---|
|**Boundary Traversal**|Visit the **outer border once**.|
|**Spiral Traversal**|Visit the outer border, **shrink the boundaries**, then repeat until the center is reached.|

Think of boundary traversal as:

```text
One Ring
```

and spiral traversal as:

```text
Ring 1
   ↓
Ring 2
   ↓
Ring 3
   ↓
...
```

> **Mental shift:** Boundary traversal is a **single perimeter walk**, whereas spiral traversal is **repeated boundary traversal with shrinking boundaries**.
