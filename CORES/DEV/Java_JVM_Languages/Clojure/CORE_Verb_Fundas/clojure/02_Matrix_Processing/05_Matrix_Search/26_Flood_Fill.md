# 26. Flood Fill

## Mental Model

Start at one seed. Visit every connected cell with the source value, then replace that region.

## Relationship to Cognitive Verb

```text
Replace -> discover seed region -> write the new value
```

## Clojure Functions and Common Idioms

|Need|Use|
|---|---|
|Search region|queue or stack|
|Avoid repeat work|a visited set|
|Return new matrix|`reduce` with `assoc-in`|
|Fill many seeds|reduce the single-seed function|
|Stop at a border value|a passable predicate|

## Common Uses

- Implement a paint bucket.
- Mark maze reachability.
- Replace one image region.
- Fill a bounded board area.

## Hidden Interview Problems

- Return fill size without changing values.
- Avoid an infinite loop when old and new values match.
- Use diagonal connectivity.
- Fill from several seeds.
- Stop at explicit boundary cells.

## Recognition Clues

Look for `paint bucket`, `replace connected color`, `seed`, `fill region`, or `boundary fill`.

## Pattern Summary

Flood fill has two phases in immutable Clojure: discover coordinates, then create the updated matrix.

## Shape and Edge Behavior

- The functions accept a finite ragged grid.
- An empty grid returns an empty region.
- An invalid seed leaves the grid unchanged.
- A valid cell can contain `nil`.

## Clojure Recipe Book

```clojure
(def four-directions [[-1 0] [0 1] [1 0] [0 -1]])

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

(defn reachable-region [grid seeds passable? directions]
  (let [valid-seeds (filter #(and (in-bounds? grid %)
                                  (passable? (get-in grid %)))
                            seeds)]
    (loop [queue (into clojure.lang.PersistentQueue/EMPTY valid-seeds)
           seen (set valid-seeds)]
      (if (empty? queue)
        seen
        (let [coordinate (peek queue)
              next-cells
              (filter (fn [next-coordinate]
                        (and (not (contains? seen next-coordinate))
                             (passable? (get-in grid next-coordinate))))
                      (neighbors grid coordinate directions))]
          (recur (into (pop queue) next-cells)
                 (into seen next-cells)))))))

(defn flood-region
  ([grid seed] (flood-region grid seed four-directions))
  ([grid seed directions]
   (if-not (in-bounds? grid seed)
     #{}
     (let [source (get-in grid seed)]
       (reachable-region grid [seed] #(= source %) directions)))))

(defn flood-fill
  ([grid seed replacement]
   (flood-fill grid seed replacement four-directions))
  ([grid seed replacement directions]
   (if-not (in-bounds? grid seed)
     grid
     (let [source (get-in grid seed)]
       (if (= source replacement)
         grid
         (reduce (fn [result coordinate]
                   (assoc-in result coordinate replacement))
                 grid
                 (flood-region grid seed directions)))))))

(defn fill-size
  ([grid seed] (fill-size grid seed four-directions))
  ([grid seed directions]
   (count (flood-region grid seed directions))))

(defn flood-region-dfs [grid seed directions]
  (if-not (in-bounds? grid seed)
    #{}
    (let [source (get-in grid seed)]
      (loop [stack [seed]
             seen #{}]
        (if (empty? stack)
          seen
          (let [coordinate (peek stack)
                stack (pop stack)]
            (if (or (contains? seen coordinate)
                    (not= source (get-in grid coordinate)))
              (recur stack seen)
              (recur (into stack (neighbors grid coordinate directions))
                     (conj seen coordinate)))))))))

(defn boundary-fill [grid seed replacement border]
  (let [region (reachable-region grid [seed] #(not= border %) four-directions)]
    (reduce (fn [result coordinate]
              (assoc-in result coordinate replacement))
            grid
            region)))

(defn multi-seed-fill [grid seeds replacement]
  (reduce (fn [result seed]
            (flood-fill result seed replacement))
          grid
          seeds))

(def grid
  [[1 1 0]
   [1 0 0]
   [0 0 1]])

(flood-fill grid [0 0] 9)
;; => [[9 9 0] [9 0 0] [0 0 1]]

(fill-size grid [1 1])
;; => 5

;; Executable checks

(assert (= [[9 9 0] [9 0 0] [0 0 1]]
           (flood-fill grid [0 0] 9)))
(assert (= 5 (fill-size grid [1 1])))
(assert (= [[nil nil] [0 nil]]
           (flood-fill [[nil nil] [0 nil]] [0 0] nil)))
(assert (= 3 (fill-size [[nil nil] [0 nil]] [0 0])))
```

A scanline fill processes horizontal runs. It can reduce queue entries for large mutable images.

For persistent vectors, coordinate search plus `assoc-in` is easier to verify.

### Memory Hooks

- Read the source value once.
- Return early when replacement equals source.
- Discover only passable cells.
- Apply writes after discovery.

### Key Insight

Separate region discovery from value replacement. This design makes fill size, labels, and pure updates share one search.

## The Search Section Complete

Cell search finds positions. Components partition all regions. Flood fill changes one or more selected regions.
