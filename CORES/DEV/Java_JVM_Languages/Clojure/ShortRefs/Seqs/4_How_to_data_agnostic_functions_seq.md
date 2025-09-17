How to write data-agnostic functions that take any sequence

###### ChatGPT said:

To write **data-agnostic functions** in Clojure that work on **any sequence-like data** — lists, vectors, sets, strings, maps — you need to:

---

## ✅ Use `seq` to normalize inputs

The `seq` function turns many types of collections into a **sequence abstraction** (i.e., something that implements `ISeq`):

```clojure 
(seq [1 2 3])      ;; => (1 2 3)
(seq '(1 2 3))     ;; => (1 2 3)
(seq #{1 2 3})     ;; => (1 3 2) ;; unordered
(seq "abc")        ;; => (\a \b \c)
(seq {:a 1 :b 2})  ;; => ([:a 1] [:b 2])


```

So, if you always start your function with `(seq x)`, it will work on many kinds of inputs.

---

## 🛠 Example: a generic `sum` function

```clojure 
(defn sum [coll]
  (reduce + (seq coll)))


```

This will work with:

```clojure
(sum [1 2 3])      ;; => 6
(sum '(1 2 3))     ;; => 6
(sum #{1 2 3})     ;; => 6


```

---

## ⚠️ Map Quirk

With maps, `seq` returns a sequence of `[k v]` pairs, so you'll need to handle that specially:

```clojure
(defn keys-sum [m]
  (reduce + (map (comp int first) (seq m))))


```
---

## ✅ Summary: Guidelines for Data-Agnostic Functions

|Tip|Why|
|---|---|
|Use `(seq coll)` to get a sequence view|Works with vectors, lists, sets, strings, maps|
|Avoid assuming order unless needed|Sets and maps are unordered|
|Avoid indexed access (`nth`, `get`)|Seqs are not indexed|
|Use `map`, `filter`, `reduce`, etc.|These work on any `seq`|
|Don't mutate – work with transformations|Seqs are immutable|

---

## 📦 Examples of Data-Agnostic Functions

```clojure
(defn count-evens [coll]
  (count (filter even? (seq coll))))

(defn stringify [coll]
  (map str (seq coll)))


```