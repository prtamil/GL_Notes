---
tags: clojure
---
# Using Clojure maps  
```clojure

(def m {:key 1 , :key2 2})

(get m :key)
(get m :key3 0)

(m :key)  ;map as functions replacement for get
(m :key3 0)

(:key m)
(:key2 m)
(:key3 m 0) ;this also works as get

(assoc m :key4 22) ;returns copy maps are immutable.
(assoc m :key2 (- (:key2 m) 1)) ;update 

(update m :key2 dec) ;returns new copy.
(update m :key2 - 10) ; - is function

(dissoc m :key2)
(dissoc m :key2 :key)

```

# 3 types of Maps

1. array-maps
2. hash-maps
3. sorted maps

