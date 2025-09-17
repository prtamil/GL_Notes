
Use `lazy-seq` to build a potentially infinite sequence. Use recursion to compute a final value.

```clojure
; generates final collapsedd value
(defn sum [xs]
  (if (empty? xs)
    0
    (+ (first xs) (sum (rest xs)))))

(comment "generate sequence of natureal numners)
(defn nats-from [n]
  (cons n (lazy-seq (nats-from (inc n)))))



```