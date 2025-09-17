---
tags: clojure, awesomecode
---

```clojure
(take 10 (iterate
			  (fn [above]
				  (mapv + (conj above 0) (cons 0 above)))
		  [1]))
		  
```

1. conj -> Insert somewhere
2. cons -> Insert at head 
3. iterate -> f(x), f(f(x)),   f(f(f(x))) ,....
4. mapv -> mapv , fn, [1,2,3] , [4,5,6]  =>  [fn(1+4), fn(2+5), fn(3+6)]