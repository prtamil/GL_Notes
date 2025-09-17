# 1. Accumulate Tricks for Groupby Operations
```clojure
; reduce function for groupby operation equiv to frequencies
(reduce (fn [acc it]
			(assoc acc it (inc (acc it 0))))
			{} lst)

(reduce (fn [acc it]
            (assoc acc it (int (get acc it 0))))
            {} lst)
            
(reduce (fn [acc it]
           (update acc it (fnil inc 0)))
           {} lst)
```
