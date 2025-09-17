---
tags: clojure_web
---
# Reframe Framework 
## Core Concepts 5 Dominoes
1. Event dispatch
2. Event handling 
3. Effect Handling 
4. Query
5. View 
6. DOM 

Effects => Side Effect 

### Flow Chart 


![[6dominoes.png|500x500]]

(1)Dispatch --(event)--> (2)Event handler --(effects)--> (3) Effect handler --(state)-(app state)-(state)--> (4)Query --(materialized view)--> (5)view --(hiccup)--> (6)Reagent/React.


### v = f(s)

query,view,reagent/react => v=f(s) 
4,5,6 -> v = f(s)

V => View 
f => Function 
s => App State

A view, v,is a function, f, of the app state, s.

## Application State

Entire app state is one Big Ratom (app-db) (in-memory data)
```clojure
(def app-db (reagent/atom {})) ;ratom
```



