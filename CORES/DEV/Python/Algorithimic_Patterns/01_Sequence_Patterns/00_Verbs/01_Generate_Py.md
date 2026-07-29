# Sequence Processing — Verb 1: Generate

## Introduction

Every sequence has a beginning.

Before we can search, transform, group, or summarize data, **there must first be a sequence to work with**.

**Generate** is the act of creating a sequence. Sometimes the sequence comes from existing data (a file, database, API), but often we generate one ourselves from a rule, a seed value, or by repeating a pattern.

The mental question is simple:

> **"Where does this sequence come from?"**

Unlike most other verbs, **Generate** doesn't transform an existing sequence—it **creates one**.

In Python, generation is usually **lazy**: `range` computes values on demand, `itertools` produces them one at a time, and a generator function yields them as they're asked for. This lets us describe infinite sequences without computing them all at once.

---

# Generate → Python

|Thinking Verb|Mental Question|Common Python|
|---|---|---|
|**Generate**|Where does the sequence come from?|`range`, `itertools.repeat`, `itertools.count`, `itertools.cycle`, generator functions, `yield`|

> **Note:** `range` is a lazy **sequence** — it has a length, supports indexing, and can be iterated repeatedly. Everything in `itertools` is a **one-shot iterator**. That difference decides whether you can use a result twice.

---

# Common Generation Patterns

|Pattern|Python|Example Output|
|---|---|---|
|Number sequence|`range`|`list(range(5))` → `[0, 1, 2, 3, 4]`|
|Repeat one value|`repeat`|`list(repeat("A", 4))` → `['A','A','A','A']`|
|Repeated computation|generator expression|`[random() for _ in range(3)]` → `[0.73, 0.18, 0.92]`|
|Generate from previous value|generator + `while True`|`islice(iterate(inc, 1), 5)` → `[1, 2, 3, 4, 5]`|
|Repeat a pattern forever|`cycle`|`list(islice(cycle("RGB"), 7))` → `['R','G','B','R','G','B','R']`|
|Count forever|`count`|`list(islice(count(10, 5), 3))` → `[10, 15, 20]`|
|Custom rule|`def … yield`|`list(fib_gen(5))` → `[0, 1, 1, 2, 3]`|

---

# The Python-specific catch

Infinite generators (`count`, `cycle`, `repeat` without a count, `while True`) **must always be bounded** — with `islice`, with `takewhile`, or by zipping against something finite. There is no error for forgetting; the program simply never returns.

---

# One Sentence to Remember

> **Generate creates a sequence from a rule, a seed, or a repeated pattern — usually lazily, so infinite sequences cost nothing until consumed.**
