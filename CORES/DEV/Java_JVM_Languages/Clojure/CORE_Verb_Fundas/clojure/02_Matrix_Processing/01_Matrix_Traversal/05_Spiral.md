# 5. Spiral Traversal

## Mental Model

Spiral traversal visits a matrix by **walking around its boundary, then shrinking inward layer by layer** until every cell has been visited.

Instead of thinking in terms of rows or columns, think in terms of **nested rectangles (layers or rings)**.

---

## Relationship to Cognitive Verb

```text
Peel
   ↓
Spiral Traversal
```

Related verbs:

- Peel layers
    
- Walk around the boundary
    
- Traverse in a spiral
    
- Visit concentric rings
    
- Shrink inward
    

---

## Clojure Functions & Common Idioms

|Variation|Example|Common Clojure|
|---|---|---|
|Clockwise spiral|outer → inner|`loop/recur`|
|Counter-clockwise|reverse direction|`loop/recur`|
|Layer traversal|process one ring|nested `doseq`|
|Spiral generation|fill matrix|mutable/transient structures|
|Boundary shrinking|move edges inward|`top`, `bottom`, `left`, `right`|

> Unlike row or diagonal traversal, spiral traversal is **stateful**, so `loop/recur` is usually the clearest approach.

---

## Common Uses

- Matrix printing
    
- UI animations
    
- Robot navigation
    
- Image scanning
    
- Game map exploration
    
- CNC/Laser tool paths
    
- Puzzle generation
    
- Memory-efficient visualization
    

---

## Hidden Interview Problems

- Print matrix in spiral order
    
- Fill matrix in spiral order
    
- Spiral Matrix I / II
    
- Traverse concentric layers
    
- Rotate matrix layer-by-layer
    
- Count spiral rings
    
- Spiral search
    

---

## Recognition Clues

If you hear...

- "spiral..."
    
- "clockwise..."
    
- "outer layer..."
    
- "ring..."
    
- "move inward..."
    
- "peel the matrix..."
    

...think **Spiral Traversal**.

---

## Pattern Summary

|Property|Value|
|---|---|
|Dimension|2D|
|Traversal Unit|Layer (Ring)|
|Direction|Usually Clockwise|
|Coordinate Rule|Shrinking boundaries|
|Time Complexity|O(rows × cols)|
|Space Complexity|O(1) extra (excluding output)|
|Common Domains|Graphics, robotics, interview problems|

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
;; Four boundaries

(def top 0)
(def bottom (dec (count m)))
(def left 0)
(def right (dec (count (first m))))

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;; Top edge

(for [c (range left (inc right))]
  (get-in m [top c]))

;; => (1 2 3 4)

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;; Right edge

(for [r (range (inc top) (inc bottom))]
  (get-in m [r right]))

;; => (8 12 16)

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;; Bottom edge (reverse)

(for [c (reverse (range left right))]
  (get-in m [bottom c]))

;; => (15 14 13)

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;; Left edge (reverse)

(for [r (reverse (range (inc top) bottom))]
  (get-in m [r left]))

;; => (9 5)

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;; Complete first ring

(concat
 (for [c (range left (inc right))]
   (get-in m [top c]))

 (for [r (range (inc top) (inc bottom))]
   (get-in m [r right]))

 (for [c (reverse (range left right))]
   (get-in m [bottom c]))

 (for [r (reverse (range (inc top) bottom))]
   (get-in m [r left]))

)

;; => (1 2 3 4 8 12 16 15 14 13 9 5)

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;; Shrink boundaries

(top    +1)
(bottom -1)
(left   +1)
(right  -1)

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;; Typical implementation

(loop [top 0
       bottom (dec rows)
       left 0
       right (dec cols)
       result []]

  ;; visit four edges

  ;; shrink boundaries

  ;; recur until
  ;; top > bottom
  ;; or
  ;; left > right
)
```

---

## Key Insight

Unlike previous traversal patterns, spiral traversal is **not defined by a simple coordinate formula**.

Instead, it maintains **four moving boundaries**:

```text
top
bottom
left
right
```

Each iteration performs the same cycle:

```text
Top Edge
    ↓
Right Edge
    ↓
Bottom Edge
    ↓
Left Edge
    ↓
Shrink Boundaries
    ↓
Repeat
```

You can think of spiral traversal as **peeling an onion**: process the outermost ring, remove it conceptually, then repeat on the smaller inner matrix.

> **Mental shift:** The fundamental unit is no longer a row, column, or diagonal—it is a **layer (ring)**.
