Once you understand the **mental model**, all map functions (`assoc`, `update`, `get`, `get-in`, `update-in`) become obvious and predictable.

---

## 🔥 Master mental model:

### **A map is a dictionary of keys → values.

Every function answers one of 2 questions:**

1. **How do I READ a value from this map?**
2. **How do I CHANGE a value in this map?**
    

That’s it.

---

## 📌 Reading values

|Intent|Function|Mental model|Example|
|---|---|---|---|
|Read _one_ key|`get`|“Give me the value at this key”|`(get m :name)`|
|Read _nested_ key(s)|`get-in`|“Walk this path of keys and give the value”|`(get-in m [:user :profile :age])`|

### How to think
```js
m --map
k --one key
ks --a path of keys (vector)

(get m k)
(get-in m ks)

```

When you use `get-in`, imagine **walking** inside the map step by step.

---

## ✍️ Changing values

|Intent|Function|Mental model|Example|
|---|---|---|---|
|Add or replace a value at one key|`assoc`|“Put this value at this key”|`(assoc m :age 30)`|
|Change a value using a function|`update`|“Apply this function to the value at this key”|`(update m :count inc)`|
|Change a nested value|`update-in`|“Walk this path → apply function at the end”|`(update-in m [:user :score] + 10)`|

### How to think
```js
(assoc m k value)
→ take m and return a *new* map where k = value

(update m k f)
→ take m and return a *new* map where value = f(old value)

(update-in m ks f args...)
→ walk into nested structure
→ at the end, apply f to final value

```

---

## 🧠 Intuition instead of memorizing

Ask yourself:

|What do I want?|Function|
|---|---|
|Look up 1 key|`get`|
|Look up nested keys|`get-in`|
|Add / override 1 key|`assoc`|
|Transform 1 value|`update`|
|Transform nested value|`update-in`|

---

## 🌟 Example to unify everything

```js
(def m {:user {:name "Tom"
               :score 5}})

```

|Intent|Code|Result|
|---|---|---|
|read name|`(get-in m [:user :name])`|`"Tom"`|
|set age|`(assoc-in m [:user :age] 22)`|adds age|
|add 10 to score|`(update-in m [:user :score] + 10)`|score = 15|
|change username|`(assoc-in m [:user :name] "Tim")`|name = "Tim"|

> Tip: `assoc-in` is just like `assoc` but for nested structures (parallel to `update-in`).

---

## 🔑 Core idea to remember forever

```js
get       → read 1 key
get-in    → read nested keys
assoc     → set 1 key to a value
assoc-in  → set nested key to a value
update    → transform 1 value
update-in → transform nested value

```
They form a **perfect grid**:


