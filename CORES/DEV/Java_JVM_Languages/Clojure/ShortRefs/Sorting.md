## 🔧 Core Sorting Functions in Clojure

|Function|Description|
|---|---|
|`sort`|Sorts values using natural order|
|`sort-by`|Sorts using a key function|
|`sort >`|Sorts in descending order|
|`reverse`|Reverses a sequence (not a sorter, just useful!)|
## 🔹 `sort`

**Usage:**


```clojure
(sort coll) (sort comparator coll)
```


### 🧠 Parameters:

- `coll` — collection of comparable elements
    
- `comparator` — optional function (`<`, `>`, `compare`, etc.)
    

### ✅ Examples:

1. Sort numbers (ascending):
```clojure
(sort [5 2 9 1]) ; => (1 2 5 9)
``` 
    
2. Sort numbers (descending):

```clojure
(sort > [5 2 9 1]) ; => (9 5 2 1)
```
  
  
3. Sort strings:
```clojure
(sort ["banana" "apple" "cherry"]) ; => ("apple" "banana" "cherry")
```
    
4. Sort with `compare` explicitly:
```clojure
(sort compare [4 2 5 1]) ; => (1 2 4 5)
```
   
    
5. Sort characters:
    
```clojure
(sort [\d \a \z \b]) ; => (\a \b \d \z)
```

## 🔹 `sort-by`

**Usage:**
```clojure
(sort-by key-fn coll)
(sort-by key-fn comparator coll)
```

### 🧠 Parameters:

- `key-fn` — function to extract a value for sorting 
- `comparator` — optional, for custom order (e.g., `>`)
- `coll` — collection

### ✅ Examples:

1. Sort people by age:
```clojure
(sort-by :age [{:name "A" :age 40} {:name "B" :age 25}])
;; => [{:name "B" :age 25} {:name "A" :age 40}]
```
2. Sort strings by length:
```clojure
(sort-by count ["abc" "a" "abcd"])
;; => ["a" "abc" "abcd"]
```  
3. Sort maps by value:
```clojure
(sort-by val {:a 3 :b 1 :c 2})
;; => ([:b 1] [:c 2] [:a 3])
```

4. Descending sort by value:
```clojure
(sort-by val > {:a 3 :b 1 :c 2})
;; => ([:a 3] [:c 2] [:b 1])
```
4. Sort using multiple keys:
```clojure
(sort-by (juxt :age :name) [{:name "Bob" :age 30} {:name "Ann" :age 30}])
;; => [{:name "Ann" :age 30} {:name "Bob" :age 30}]
```

---

## 🔹 `reverse`

**Usage:**
```clojure
(reverse coll)
```

### 🧠 Parameters:

- `coll` — any sequence  

### ✅ Examples:

1. Reverse a list:
```clojure
(reverse [1 2 3]) ; => (3 2 1)
```
2. Reverse a string (char seq):
```clojure
(apply str (reverse "clojure")) ; => "erujolc"
``` 
3. Reverse a sorted list:
```clojure
(reverse (sort [2 5 1])) ; => (5 2 1)
```
3. Reverse keywords:
```clojure
(reverse [:a :b :c]) ; => (:c :b :a)
```  
5. Combine with take:
```clojure
(->> [5 1 8 2]
     sort
     reverse
     (take 2)) ; => (8 5)

```

## ✅ TL;DR

- Use `**sort**` for **flat**, **comparable** data (`[3 1 5]`, `["a" "b"]`)
- Use `**sort-by**` for **nested** or **structured** data (`[{:name "X"} ...]`)
- `sort-by` = `map` + `sort` under the hood (transform, then compare)