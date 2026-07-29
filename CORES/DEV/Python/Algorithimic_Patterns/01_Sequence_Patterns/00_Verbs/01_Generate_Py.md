# Sequence Processing — Verb 1: Generate

## Introduction

Every sequence starts somewhere.

You can't search, transform, group or summarize anything until **you have a sequence in hand**.

**Generate** is how you get one. Sometimes it arrives from outside — a file, a database, an API. Often you build it yourself from a rule, a seed value, or a pattern you keep repeating.

The question you're asking is simple:

> **"Where does this sequence come from?"**

Most verbs take a sequence and change it. Generate is the odd one out: it **makes** the sequence.

Python generates **lazily** most of the time. `range` works out values when you ask for them, `itertools` hands them over one at a time, and a generator function yields on demand. That's what lets you describe an infinite sequence without ever computing all of it.

---

# Generate → Python

|Thinking Verb|Mental Question|Common Python|
|---|---|---|
|**Generate**|Where does the sequence come from?|`range`, `itertools.repeat`, `itertools.count`, `itertools.cycle`, generator functions, `yield`|

> **Note:** `range` is a lazy **sequence**. It has a length, you can index it, and you can loop over it as many times as you like. Everything in `itertools` is a **one-shot iterator**. That one difference decides whether you can use a result twice.

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

Always put a bound on an infinite generator — `count`, `cycle`, `repeat` with no count, `while True`. Use `islice`, use `takewhile`, or zip it against something finite. Forget, and Python won't warn you. The program just never comes back.

---

# One Sentence to Remember

> **Generate builds a sequence from a rule, a seed, or a repeating pattern. It's usually lazy, so an infinite sequence costs you nothing until you start pulling from it.**
