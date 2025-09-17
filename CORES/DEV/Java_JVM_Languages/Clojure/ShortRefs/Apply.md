# apply

```clojure
(apply f [args]) ; (f args[0] args[1] , ...)
(apply sq [1])  ; (sq 1)
(apply map sq [[1 2 3]]) ; (map sq [1 2 3]) -> apply add arguments array, 
(apply map vector [[1 2 3 4]]) ; (map vector [1 2 3 4]) 
```

```clojure
;best use case
(map #(apply str %) [ [1 2 3] [4 5 6] [7 8 9] ]) ; [3 6 9]
(apply str [1 2 3]) ; "123" (str [1 2 3]) => "[1 2 3]" 
```
