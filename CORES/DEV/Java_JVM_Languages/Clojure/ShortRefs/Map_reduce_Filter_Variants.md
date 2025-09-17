1. Mapping functions
	1. map
	2. mapv
	3. map-indexed
	4. map-cat
	5. pmap
2. Reduce Functions
	1. reduce
	2. reduce-kv
	3. reductions
3. Filter Functions
	1. filter
	2. filterv
	3. remove
	4. keep
	5. keep-indexed

## Map
```clojure
;; 1. map
(map f & colls)
(map + [1 2 3] [4 5 6]) ;; => (5 7 9) ; Applies + to each pair across collections

(map-indexed f coll)
(map-indexed (fn [idx item] [idx item]) ["a" "b" "c"]) ;; => ([0 "a"] [1 "b"] [2 "c"])

(mapcat f & colls) ;`mapcat` is equivalent to 
(apply concat (map f colls)) ;f must return collections
(mapcat (fn [x] [x x]) [1 2 3]) ;; => (1 1 2 2 3 3) ; Maps f then concatenates results

(pmap f & colls)
(pmap #(do (Thread/sleep 100) (* % %)) [1 2 3 4]) ;; => (1 4 9 16) ; Processes in parallel

```

## Reduce

```clojure

(reduce f val? coll)
;`f`: Function that takes 2 arguments: accumulator and item
;val?`: Optional initial value (if omitted, first item becomes initial value)
; `coll`: Collection to process

(reduce + 0 [1 2 3 4]) ;; => 10 ; 0+1+2+3+4

(reduce-kv f init coll)
(reduce-kv (fn [acc k v] (assoc acc k (* v 2))) {} {:a 1 :b 2}) ;; => {:a 2 :b 4} ; Doubles each value

(reductions f val? coll) ;Like `reduce` but returns all intermediate values
(reductions + [1 2 3 4]) ;; => (1 3 6 10) ; Shows each step of the accumulation


```

## Filter

```clojure

(filter pred coll)
(filter even? [1 2 3 4 5 6]) ;; => (2 4 6) ; Keeps only items where even? returns true

(filterv pred coll)
(filterv even? [1 2 3 4 5 6]) ;; => [2 4 6] ; Note the vector brackets


(remove pred coll) ; Negative filter
(remove even? [1 2 3 4 5 6]) ;; => (1 3 5) ; Keeps only items where even? returns false

(keep f coll) ;`f`: Function applied to each item; nil results are removed
(keep #(when (even? %) (* % %)) [1 2 3 4]) ;; => (4 16) ; Squares even numbers, drops odd ones

(keep-indexed f coll)
(keep-indexed (fn [idx val] (when (even? idx) [idx val])) ["a" "b" "c" "d"]) ;; => ([0 "a"] [2 "c"]) ; Keeps only items at even indices

```

## Key Patterns to Remember

1. **Function parameters always come first**
    - The function that will process each item is always the first parameter
2. **Collection parameters come last**
    - The collections being processed are almost always the final parameters
3. **-indexed variants**
    - Add the index as the first parameter to your function
    - Function signature changes from `(fn [item])` to `(fn [idx item])`
4. **-kv variants**
    - Work with key-value pairs (maps) or indexed collections (vectors)
    - Function signature is `(fn [accumulator key value])`
5. **Initial value patterns**
    - Many functions accept an optional initial value
    - If missing, they'll use the first item in the collection

These patterns should help you remember the parameter orders across these function families. The most important thing to remember is that Clojure generally puts the data last and the operations first.