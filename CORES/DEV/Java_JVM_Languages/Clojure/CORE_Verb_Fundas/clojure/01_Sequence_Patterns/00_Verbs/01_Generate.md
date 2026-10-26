# Sequence Processing — Verb 1: Generate

## Introduction

Every sequence has a beginning.

Before we can search, transform, group, or summarize data, **there must first be a sequence to work with**.

**Generate** means to create a sequence. The data can come from a file, database, or application programming interface (API). It can also come from a rule, seed, or pattern.

The mental question is simple:

> **"Where does this sequence come from?"**

Unlike most other verbs, **Generate** doesn't transform an existing sequence—it **creates one**.

In Clojure, sequences are often generated lazily, meaning values are produced only when they are needed. This allows us to describe infinite sequences without computing them all at once.

---

# Generate → Clojure

|Thinking Verb|Mental Question|Common Clojure Functions|
|---|---|---|
|**Generate**|Where does the sequence come from?|`range`, `repeat`, `repeatedly`, `iterate`, `cycle`|

---

# Common Generation Patterns

|Pattern|Clojure|Example Output|
|---|---|---|
|Number sequence|`range`|`(range 5)` → `(0 1 2 3 4)`|
|Repeat one value|`repeat`|`(repeat 4 "A")` → `("A" "A" "A" "A")`|
|Repeated computation|`repeatedly`|`(repeatedly 3 rand)` → `(0.73 0.18 0.92)`|
|Generate from previous value|`iterate`|`(take 5 (iterate inc 1))` → `(1 2 3 4 5)`|
|Repeat a pattern forever|`cycle`|`(take 7 (cycle [:R :G :B]))` → `(:R :G :B :R :G :B :R)`|

---

# The Clojure-specific catches

**`repeat` takes a value. `repeatedly` takes a function.** `(repeat 3 (rand-int 1000))` evaluates `rand-int` once. It returns the same number three times. `(repeatedly 3 #(rand-int 1000))` calls the function three times.

**Bound every infinite source.** `range`, `cycle`, `repeat`, and `iterate` can produce infinite sequences. Apply `take` or `take-while` before realization.

**Lazy sequences can realize in chunks of 32.** `(take 1 (map f (range 40)))` can call `f` 32 times. Keep lazy functions free of side effects.

---

# One Sentence to Remember

> **Generate creates a sequence from a rule, seed, or repeating pattern. Lazy generation calculates values only when a consumer requests them.**
