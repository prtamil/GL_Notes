# Sequence Processing — Verb 12: Expand

## Introduction

Sometimes one element needs to become **multiple elements**.

**Expand** is the act of replacing each element with zero, one, or many output elements, producing a larger sequence.

The mental question is:

> **"How can one element become many?"**

Unlike **Transform**, which maps one element to one element, **Expand** maps one element to many elements.

---

# Expand → Clojure

|Thinking Verb|Mental Question|Common Clojure Functions|
|---|---|---|
|**Expand**|How can one element become many?|`mapcat`, `for`, `repeat`, `cycle`, `iterate`|

> **Note:** `mapcat` is the primary expansion function. It maps each element to a sequence and then concatenates the results into a single sequence.

---

# Common Expansion Patterns

|Pattern|Clojure|Example Result|
|---|---|---|
|One element to many|`mapcat`|`(mapcat #(repeat 2 %) [1 2 3])` → `(1 1 2 2 3 3)`|
|Expand into sub-elements|`mapcat`|`(mapcat seq ["ab" "cd"])` → `(\a \b \c \d)`|
|Generate combinations|`for`|`(for [x [1 2] y [:a :b]] [x y])` → `([1 :a] [1 :b] [2 :a] [2 :b])`|
|Repeat values|`repeat`|`(repeat 3 :x)` → `(:x :x :x)`|
|Repeat a pattern|`cycle`|`(take 6 (cycle [:R :G]))` → `(:R :G :R :G :R :G)`|

---

# The Clojure-specific catches

**`mapcat`'s function must return a collection.** Return a scalar and you get an `IllegalArgumentException` on realisation — often far from the line that caused it. Wrap single results in a vector.

**`mapcat` inherits `concat`'s layering cost.** It is fine for one pass over a sequence and a poor choice inside an accumulating loop.

**`flatten` is blunter than you want.** It descends *every* level, so one unexpectedly nested element changes your result shape. It also returns `()` for a map — `(flatten {:a 1})` is empty, not the pairs. For one level, use `(apply concat …)` or `mapcat`.

**Expansion sources are frequently infinite.** Unbounded `repeat` and `cycle` do not end. Apply `take` before you realize the result.

---

# One Sentence to Remember

> **Expand produces a larger sequence by allowing each input element to generate multiple output elements.**
