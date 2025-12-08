# 🧠 How to Think About `assoc`, `update`, `get`, and Their `-in` Variants in Clojure

Maps are the most fundamental data structure in Clojure: they store keys and values, often in deeply nested structures. When working with maps, developers frequently need to **read** values and **change** values. Almost every map operation falls into these two categories.

Understanding the core intent behind each function is much more effective than memorizing syntax.

---

## 1. The Mental Model: Reading vs. Changing

Every time you interact with a map, ask:

> **Am I trying to read something, or am I trying to change something?**

And if changing, ask:

> **Do I already know the new value, or do I need to compute it based on the existing one?**

From these questions, all functions become obvious.

---

### Reading

- **`get`** — read a single key
- **`get-in`** — read a nested path of keys
    

### Changing

- **`assoc`** — write a new value directly (you already know the new value)
- **`update`** — compute the new value from the old one (apply a function)
- **`assoc-in`** — write a nested value directly
- **`update-in`** — compute a nested value from the old one
    

This forms a clean grid:

|Depth|Read|Write directly|Compute from old|
|---|---|---|---|
|1 key|`get`|`assoc`|`update`|
|Nested|`get-in`|`assoc-in`|`update-in`|

---

## 2. Analogy: A Dictionary vs. a Calculator

Think of a map as a **dictionary notebook**.

### When you use `assoc` / `assoc-in`

You **erase the old word and write a new word**.  
You don’t calculate anything — you simply write what you already know.

`(assoc m :age 30)`

You are saying: “Set age to 30 — I already know the value.”

### When you use `update` / `update-in`

You **look at the current value, run it through a calculator, and write back the result.**

`(update m :age inc)`

This means: “Take the current age, run `inc` on it, and store the result.”

So:

- `assoc` = **overwrite**
- `update` = **overwrite by calculation**
    

---

## 3. Clear Examples

Let’s start with a sample map:

```js
(def m {:a 1
        :b {:c 2
            :d {:e 3}}})

```

### Reading

```js
(get m :a)                     ; => 1
(get-in m [:b :c])             ; => 2
(get-in m [:b :d :e])          ; => 3

```

### Writing directly (`assoc` and `assoc-in`)

```js
(assoc m :a 10)                ; => {:a 10, :b {:c 2, :d {:e 3}}}
(assoc-in m [:b :c] 20)        ; => {:a 1, :b {:c 20, :d {:e 3}}}

```

You can write multiple keys at once with `assoc`:

`(assoc m :a 100 :x 5)`

### Computing new value using old (`update` and `update-in`)

```js
(update m :a inc)              ; => {:a 2,  ...}
(update m :a + 5)              ; => {:a 6,  ...}
(update-in m [:b :c] * 10)     ; => {:a 1, :b {:c 20, ...}}
(update-in m [:b :d :e] + 100) ; => {:a 1, :b {:c 2, :d {:e 103}}}

```

### Key missing? `update` still works

If a key doesn’t exist, the old value is `nil`:

`(update m :new-key inc)        ; => error (inc expects number)`

To handle this safely, use `fnil`:

`(update m :new-key (fnil inc 0))   ; => {:new-key 1}`

---

## 4. When to Use Which

|Ask yourself|If yes|Function|
|---|---|---|
|Am I just reading?|top level|`get`|
||nested|`get-in`|
|Am I changing?|I already know the exact new value|`assoc` / `assoc-in`|
||New value depends on old value|`update` / `update-in`|

Examples:

- Add an item to a vector → `update`
- Insert a brand-new fixed value → `assoc`
- Increase a numeric counter → `update`
- Replace a user profile map loaded from database → `assoc-in`
    

---

## 5. The Cleanest Intuition

Say these short sentences when coding:

- `get`: **Read value at key.**
- `get-in`: **Walk the path and read.**
- `assoc`: **Write this value here.**
- `assoc-in`: **Walk the path and write.**
- `update`: **Look up old value, compute new one, write it.**
- `update-in`: **Walk path, compute, write.**
    

If you can say the intent, you automatically know the function.

---

## 6. Final summary for reference

- Use `get`/`get-in` to **read**.
- Use `assoc`/`assoc-in` to **write the value you already know**.
- Use `update`/`update-in` to **compute the new value from the old value**.
- Use `fnil` when `update` might receive `nil`.
    

```js
assoc     = assignment (overwrite with known value)
update    = transformation (compute new using old)

```

Once you internalize this distinction, the syntax becomes effortless and you stop memorizing — everything flows from intention.