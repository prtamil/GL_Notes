- **Window:** chunk, sliding, jump, overlap, adjacent pair
- **Pair:** zip, interleave, Cartesian product
- **Slice:** prefix, suffix, head, tail
- **Traversal:** forward, reverse, stride, circular
- **Expand:** flatMap, repeat
- **Compress:** distinct, dedupe, run-length encoding
- **Group:** by key, by predicate, histogram
- **Order:** sort, reverse, rotate
- **Search:** first, all, nearest
- **Scan:** running sum, prefix sum
- **Generate:** range, iterate, cycle
- **Structure:** flatten, transpose, reshape

> **Course baseline:** Clojure **1.12.6**, the current stable release. Part 1 uses only `clojure.core`, except where an example explicitly requires `clojure.string` or `clojure.set`.

---

# The Clojure tool for each pattern

|Family|Pattern|Reach for|
|---|---|---|
|**Window**|chunk|`(partition-all n xs)`|
||sliding|`(partition n 1 xs)`|
||jump / overlap|same, with a `step`: `(partition n step xs)`|
||adjacent pair|`(partition 2 1 xs)`|
|**Pair**|zip|`(map vector a b)` — stops at the shortest|
||interleave|`(interleave a b)`|
||Cartesian product|`(for [x a y b] [x y])`|
|**Slice**|prefix / suffix|`(take n xs)` / `(take-last n xs)`|
||head / tail|`(let [[h & t] xs] …)`|
||lazy slice|`(->> xs (drop a) (take (- b a)))`|
|**Traversal**|forward|`(doseq [x xs] …)` — or just `map`|
||reverse|`(reverse xs)` / `(rseq v)` for vectors|
||stride|`(take-nth k xs)`|
||circular|`(cycle xs)` / `(nth xs (mod i (count xs)))`|
|**Expand**|flatMap|`(mapcat f xs)`|
||repeat|`(repeat n x)` / `(apply concat (repeat n xs))`|
|**Compress**|distinct|`(distinct xs)`|
||dedupe|`(dedupe xs)` — consecutive only|
||RLE|`(map (juxt first count) (partition-by identity xs))`|
|**Group**|by key|`(group-by f xs)`|
||by predicate|`(group-by pred xs)` → `{true […] false […]}`|
||histogram|`(frequencies xs)`|
|**Order**|sort|`(sort-by f xs)`|
||reverse|`(reverse xs)`|
||rotate|`(->> (cycle xs) (drop n) (take (count xs)))`|
|**Search**|first|`(first (filter pred xs))`|
||all|`(filter pred xs)`|
||nearest|`(apply min-key #(Math/abs (- % t)) xs)`|
|**Scan**|running sum|`(reductions + xs)`|
||prefix sum|`(reductions + 0 xs)` then `(- (P j) (P i))`|
|**Generate**|range|`(range a b s)` / `(range)`|
||iterate|`(iterate f x)`|
||cycle|`(cycle xs)`|
|**Structure**|flatten|`(apply concat xs)` — one level|
||transpose|`(apply map vector rows)`|
||reshape|`(partition-all n flat)`|

---

# The imports that cover almost everything

```clojure
;; none
```

That is not a joke. Every function in the table above is in `clojure.core` and is already referred into your namespace. Python needs four import lines — `itertools`, `collections`, `functools`, `operator`, plus `heapq` and `bisect` — to reach the same vocabulary. Clojure needs none.

The two you will occasionally want:

```clojure
(require '[clojure.string :as str]     ; join, split, starts-with?
         '[clojure.set :as set])       ; union, intersection, difference
```

Three rules run through all of it:

1. **Sequence functions compose, so learn the threading macros.** `->>` puts the collection last, which is where every sequence function wants it. One pipeline replaces the nested calls you would otherwise read inside-out.
2. **Laziness is the default, and it is cached.** Nothing runs until a consumer realizes it. A realized lazy sequence keeps its values.
3. **`partition` and `reductions` are central functions in this course.** Different arguments make the complete window family. `reductions` makes running values and prefix values.

---

# Next 
```txt
Part 1
1D Sequence Patterns
        ↓
Part 2
Matrix Patterns
        ↓
Part 3
Tensor Patterns
        ↓
Part 4
Tree Traversal Patterns
        ↓
Part 5
Graph Traversal Patterns
```
