
Transudcer function using conj is frequent

```clojure
(def xf (comp (map inc) (filter even?)))
(transduce xf conj [1 2 3 4 5])
```

This is usually based on vector. but i want for cons and sequence then i need to define custom reducer function 
which handles multiple arity 

```clojure
(transduce xf cons '() [1 2 3 4 5]) ; Not work
(sequence xf [1 2 3 4 5])  ;work fine.
```

Above function will not work for transduce function.  we need reducer function which handles multiple arity

```clojure
(defn cons-reducer
  ([] '())                           ;; init
  ([acc] acc)                        ;; completion
  ([acc x] (cons x acc)))            ;; actual cons

(transduce xf cons-reducer [1 2 3 4 5])  ; Works fine
```

Remember Reducer function for transduce 
should handle 3 arities 
1. init
2. completion 
3. actual combination

```clojure
(defn cons-reducer
  ([] '())                           ;; init
  ([acc] acc)                        ;; completion
  ([acc x] (cons x acc))) 
```

Like this