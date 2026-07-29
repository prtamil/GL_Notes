# 7. Snake Traversal

## Mental Model

Snake traversal visits the matrix in a **single continuous path** by traversing one row left→right, the next row right→left, and so on.

Unlike the general Zigzag pattern, Snake traversal emphasizes **path continuity**—the traversal ends one row exactly where the next row begins, like a snake moving across the matrix.

---

## Relationship to Cognitive Verb

```text
Serpentine
      ↓
Snake Traversal
```

Related verbs:

- Snake through
    
- Wind through
    
- Weave
    
- Serpentine
    
- Sweep continuously
    

---

## Clojure Functions & Common Idioms

|Variation|Example|Common Clojure|
|---|---|---|
|Row snake|alternate rows|`map-indexed`, `reverse`, `mapcat`|
|Column snake|alternate columns|`apply map vector`, `reverse`|
|Continuous path|flatten traversal|`mapcat`, `concat`|
|Indexed snake|preserve coordinates|`map-indexed`|
|General serpentine|alternate any dimension|`even?`, `odd?`|

---

## Common Uses

- Robot vacuum paths
    
- CNC and 3D printer toolpaths
    
- Agricultural field coverage
    
- Image raster acquisition
    
- LED matrix animations
    
- Warehouse robots
    
- Autonomous vehicles
    
- Terrain scanning
    

---

## Hidden Interview Problems

- Print matrix in snake order
    
- Flatten matrix serpentine style
    
- Alternate row traversal
    
- Robot coverage path
    
- Raster scan optimization
    
- Continuous matrix walk
    
- Boustrophedon traversal
    

---

## Recognition Clues

If you hear...

- "snake through..."
    
- "serpentine..."
    
- "continuous path..."
    
- "lawn mower pattern..."
    
- "back-and-forth without lifting..."
    

...think **Snake Traversal**.

---

## Pattern Summary

|Property|Value|
|---|---|
|Dimension|2D|
|Traversal Unit|Row (usually)|
|Direction|Alternating|
|Primary Goal|Continuous path|
|Time Complexity|O(rows × cols)|
|Space Complexity|O(1) extra (excluding output)|
|Common Domains|Robotics, graphics, automation|

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
;; Snake traversal

(mapcat
 identity
 (map-indexed
  (fn [r row]
    (if (even? r)
      row
      (reverse row)))
  m))

;; =>
;; (1 2 3 4
;;  8 7 6 5
;;  9 10 11 12
;; 16 15 14 13)

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;; Visit cells

(doseq [[r row]
        (map-indexed vector m)]
  (doseq [cell (if (even? r)
                 row
                 (reverse row))]
    (println cell)))

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;; Snake by columns

(def cols
  (apply map vector m))

(mapcat
 identity
 (map-indexed
  (fn [c col]
    (if (even? c)
      col
      (reverse col)))
  cols))

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;; Generic serpentine

(defn snake [coll]
  (mapcat
   identity
   (map-indexed
    (fn [i xs]
      (if (even? i)
        xs
        (reverse xs)))
    coll)))

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;; Compare

;; Normal
1 2 3 4
5 6 7 8
9 10 11 12

;; Snake
1 2 3 4
8 7 6 5
9 10 11 12
```

---

## Key Insight

Snake traversal optimizes for a **continuous movement path**.

```text
→→→→
←←←←
→→→→
←←←←
```

Notice that the endpoint of one row is the starting point of the next:

```text
1 → 2 → 3 → 4
              ↓
5 ← 6 ← 7 ← 8
↓
9 → 10 → 11 → 12
```

There is **no jump back to the beginning of the next row**. This is why robots, printers, scanners, and CNC machines often use snake traversal—it minimizes unnecessary movement.

---

## Zigzag vs Snake

These two patterns are closely related but emphasize different ideas:

|Pattern|Core Idea|
|---|---|
|**Zigzag**|Alternate the direction of each traversal unit (rows, columns, or diagonals).|
|**Snake**|Follow one continuous serpentine path through the matrix, usually by alternating rows.|

Think of it this way:

```text
Zigzag
========
Focus:
Alternating Direction

Snake
========
Focus:
Continuous Path
```

Every row-based snake traversal is a **zigzag**, but not every zigzag traversal is a **snake** (for example, JPEG's diagonal zigzag is not a snake path).
