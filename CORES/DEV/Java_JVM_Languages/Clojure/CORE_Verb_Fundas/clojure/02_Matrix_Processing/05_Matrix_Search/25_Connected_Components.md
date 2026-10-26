# 25. Connected Components

## Mental Model

A component is a maximal set of matching cells connected by allowed moves. Search one component, mark it, then continue.

## Relationship to Cognitive Verb

```text
Partition -> search connected cells -> mark component -> repeat
```

## Clojure Functions and Common Idioms

|Need|Use|
|---|---|
|Breadth-first search|`PersistentQueue`|
|Depth-first search|a vector stack|
|Track visited cells|a set|
|Create labels|`reduce` with `assoc-in`|
|Choose connectivity|direction data|

## Common Uses

- Count islands.
- Label image regions.
- Find board groups.
- Measure component area and perimeter.
- Group equal adjacent values.

## Hidden Interview Problems

- Compare four-connectivity with eight-connectivity.
- Return component coordinates, not only a count.
- Label each component.
- Find regions for every value.
- Calculate perimeter from missing neighbors.

## Recognition Clues

Look for `islands`, `regions`, `connected groups`, `clusters`, or `label components`.

## Pattern Summary

Each cell belongs to at most one component for one target rule. Visited state prevents repeated searches.

## Shape and Edge Behavior

- The functions accept a finite ragged grid.
- An empty grid has no components.
- An invalid start coordinate produces an empty component.
- Component labels use deterministic row-major start order.

## Clojure Recipe Book

```clojure
(require '[clojure.set :as set])

(def four-directions [[-1 0] [0 1] [1 0] [0 -1]])

(def eight-directions
  (vec
    (for [row-change [-1 0 1]
          column-change [-1 0 1]
          :when (not= [0 0] [row-change column-change])]
      [row-change column-change])))

(defn in-bounds? [grid [row column]]
  (and (<= 0 row) (< row (count grid))
       (<= 0 column) (< column (count (nth grid row)))))

(defn neighbors [grid [row column] directions]
  (vec
    (for [[row-change column-change] directions
          :let [coordinate [(+ row row-change)
                            (+ column column-change)]]
          :when (in-bounds? grid coordinate)]
      coordinate)))

(defn unseen-target-neighbors [grid coordinate target directions seen]
  (filter (fn [neighbor]
            (and (not (contains? seen neighbor))
                 (= target (get-in grid neighbor))))
          (neighbors grid coordinate directions)))

(defn component-from [grid start target directions]
  (if (or (not (in-bounds? grid start))
          (not= target (get-in grid start)))
    #{}
    (loop [queue (conj clojure.lang.PersistentQueue/EMPTY start)
           seen #{start}]
      (if (empty? queue)
        seen
        (let [coordinate (peek queue)
              next-cells (unseen-target-neighbors
                           grid coordinate target directions seen)]
          (recur (into (pop queue) next-cells)
                 (into seen next-cells)))))))

(defn components
  ([grid] (components grid four-directions 1))
  ([grid directions target]
   (let [candidates
         (set
           (for [row (range (count grid))
                 column (range (count (nth grid row)))
                 :when (= target (get-in grid [row column]))]
             [row column]))]
     (loop [remaining candidates
            result []]
       (if (empty? remaining)
         result
         (let [start (first (sort remaining))
               component (component-from grid start target directions)]
           (recur (set/difference remaining component)
                  (conj result component))))))))

(defn component-from-dfs [grid start target directions]
  (if-not (in-bounds? grid start)
    #{}
    (loop [stack [start]
           seen #{}]
      (if (empty? stack)
        seen
        (let [coordinate (peek stack)
              stack (pop stack)]
          (if (or (contains? seen coordinate)
                  (not= target (get-in grid coordinate)))
            (recur stack seen)
            (recur (into stack (neighbors grid coordinate directions))
                   (conj seen coordinate))))))))

(defn label-components [grid directions target]
  (let [blank (mapv (fn [row] (mapv (constantly 0) row)) grid)]
    (reduce-kv
      (fn [labels component-index component]
        (reduce (fn [result coordinate]
                  (assoc-in result coordinate (inc component-index)))
                labels
                component))
      blank
      (components grid directions target))))

(defn regions-by-value [grid directions]
  (let [all-cells (set
                    (for [row (range (count grid))
                          column (range (count (nth grid row)))]
                      [row column]))]
    (loop [remaining all-cells
           result []]
      (if (empty? remaining)
        result
        (let [start (first (sort remaining))
              value (get-in grid start)
              component (component-from grid start value directions)]
          (recur (set/difference remaining component)
                 (conj result {:value value :cells component})))))))

(defn component-perimeter [component]
  (reduce + 0
          (for [[row column] component]
            (count
              (remove component
                      (map (fn [[row-change column-change]]
                             [(+ row row-change) (+ column column-change)])
                           four-directions))))))

(def grid
  [[1 1 0 0]
   [1 0 0 1]
   [0 0 1 1]])

(count (components grid four-directions 1))
;; => 2

(label-components grid four-directions 1)
;; => [[1 1 0 0] [1 0 0 2] [0 0 2 2]]

;; Executable checks

(assert (= 2 (count (components grid four-directions 1))))
(assert (= [[1 1 0 0] [1 0 0 2] [0 0 2 2]]
           (label-components grid four-directions 1)))
```

Use disjoint-set union when connections arrive over time. Breadth-first search is clearer for a fixed matrix.

### Memory Hooks

- Find one unvisited target cell.
- Search its complete region.
- Remove or mark that region.
- Repeat until no target cells remain.

### Key Insight

Connectivity is part of the problem definition. Four-neighborhood and eight-neighborhood can produce different component counts.

## Components vs Flood Fill

Component search discovers regions. Flood fill changes the values in one discovered region.
