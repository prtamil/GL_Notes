# ⭐ **Understanding Arity in Clojure’s Higher-Order Functions — The Intuitive Way**

_(With deeper examples for real-world intuition)_

Many Clojure developers struggle at first with this question:

> **“When I pass a lambda (`#()`, `fn`) into functions like `map`, `reduce`, `update`, or `group-by`,  
> how do I know how many parameters that lambda should take?”**

It feels random — until you learn the **one simple rule**.

---

# 🌟 **THE ONE RULE**

## 👉 **Your lambda always receives exactly what the higher-order function is currently iterating over.**

You don’t need to memorize anything.  
You just need to know _what the function loops over_ internally.

Once that’s clear, arity is obvious.

---

# 🧠 **THE UNIVERSAL INTUITION**

Every higher-order function is basically a hidden loop:

```js
for each x in data:
    (apply lambda-to-x)

```

So ask yourself:

## ❓ “What does this function process at each step?”

Whatever that is → those are your lambda parameters
This intuition works for simple and complex cases.

---

# 1️⃣ **map — “I loop over elements from each collection”**

### Basic example

```js
(map #(str "Hello " %) ["Alice" "Bob"])

```

Your fn gets **1 argument**: each element.

### Multiple collections (parallel mapping)

```js
(map (fn [price tax] (+ price (* price tax)))
     [100 200 300]
     [0.1 0.2 0.05])

```

Your lambda receives **two arguments**:  
`(price, tax)` because `map` iterates over pairs.

### More complex: mapping over a list of maps
```js
(map #(update % :value inc)
     [{:id 1 :value 10}
      {:id 2 :value 20}])

```

Your lambda receives a **whole map**, not just one key.

✔ Intuition:  
Map loops over elements → elements are maps → fn receives maps.

---

# 2️⃣ **filter — “I loop over each element and ask YES/NO”**

### Example: filter map entries

```js
(filter #(> (:age %) 30)
        [{:name "A" :age 20}
         {:name "B" :age 40}])

```

Lambda receives **one argument**: the element.

### Example: filter nested vectors

```js
(filter #(> (count %) 2) [[1] [1 2 3] [9 8 7 6]])

```

Still exactly **one argument**: each element, even if nested.

✔ Intuition:  
Filter loops over elements → fn receives just the current element.

---

# 3️⃣ **reduce — “I loop over (accumulator, element) pairs”**

Always 2 arguments: `(acc element)`.

### Basic

```js
(reduce #(+ %1 %2) 0 [1 2 3])

```

### More complex: building grouped counts

```js
(reduce
  (fn [acc {:keys [category]}]
    (update acc category (fnil inc 0)))
  {}
  [{:category :fruit}
   {:category :veg}
   {:category :fruit}])

```

Your lambda receives:

1. `acc` — a map like `{:fruit 1}`
2. `element` — a map like `{:category :veg}`
    

### Nested reduction

```js
(reduce
  (fn [acc row]
    (reduce (fn [a v] (conj a (* v v)))  ; inner reduce
            acc                          ; inner acc
            row))
  []
  [[1 2] [3 4 5]])

```

- Outer reduce: `(acc row)`
- Inner reduce: `(a v)`
    

✔ Intuition:  
Reduce loops over pairs → always receives accumulator + next element.

---

# 4️⃣ **update — "I operate on the old value at the key"**

### Basic

```js
(update {:a 10} :a inc)
;; f receives: old-value = 10

```

### With extra args

```js
(update {:a 10} :a (fn [old x] (+ old x)) 5)
;; f receives: (old-value, x) = (10, 5)

```

### Updating nested collections

```js
(update {:a [1 2 3]} :a #(map inc %))

```

Lambda receives **the entire vector** `[1 2 3]`.

### Updating inside reduce

```js
(reduce
  (fn [m {:keys [k v]}]
    (update m k (fnil conj []) v))
  {}
  [{:k :x :v 10} {:k :x :v 20} {:k :y :v 1}])

```

Here inside reduce:

```js
update → f receives (old-value, v)
reduce → lambda receives (acc, element)

```

Multiple layers but each follows the same rule.

✔ Intuition:  
Update deals with one thing → the old value → fn takes old-value (+ extra args if any).

---

# 5️⃣ **sort-by — “I ask your fn for a sorting key for each element”**

### Basic

```js
(sort-by :age [{:age 20} {:age 50}])
; f receives each element map

```

### More complex

```js
(sort-by (fn [{:keys [first-name last-name]}]
           [last-name first-name])
         users)

```

Lambda receives a full complex map like:

```js
{:id 1, :first-name "Alice", :last-name "Zed"}

```

### Sorting map entries

```js
(sort-by (fn [[k v]] v) {:a 10 :b 5 :c 99})

```

Lambda receives **key-value pairs**, e.g. `[:b 5]`.

✔ Intuition:  
Sort-by loops over elements → fn gets one element.

---

# 6️⃣ **group-by — “I ask your fn for grouping keys”**

### Example

```js
(group-by #(> (:age %) 30)
          [{:name "A" :age 20}
           {:name "B" :age 40}])

```

Lambda receives the whole element map.

### More complex grouping

```js
(group-by (fn [{:keys [score]}]
            (cond
              (< score 50) :low
              (< score 80) :mid
              :else :high))
          students)

```

Again: 1 argument — the element.

---

# 7️⃣ **transducers — “The same arity rules apply inside pipeline stages”**

Example XF pipeline:

```js
(transduce
  (comp
    (map #(select-keys % [:name :age]))
    (filter #(> (:age %) 30))
    (map :name))
  conj
  users)

```

Even here:

- Each `map` → fn gets 1 element
- `filter` → fn gets 1 element
- Final `map` → fn gets 1 element
    

The pattern never changes.

---

# 🎯 **THE KEY TAKEAWAY**

> **To know the arity, ask what the higher-order function is iterating over.  
> Your lambda receives exactly that — no more, no less.**

This works for all cases:  
simple, nested, multi-collection, pipelines, reducers, updates, grouping, sorting.

You don’t need to memorize anything.  
You just need the intuition.