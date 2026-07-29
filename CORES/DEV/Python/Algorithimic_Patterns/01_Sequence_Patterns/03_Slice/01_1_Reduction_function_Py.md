`itertools.accumulate` is Python's version of Clojure's `reductions`, and it's lovely for the same reason: you get back **the whole history**, not just the final answer.

An easy way to hold it:

> **`functools.reduce` = Final state**
> **`itertools.accumulate` = Every intermediate state**

The signature worth memorising:

```python
accumulate(iterable, func=operator.add, *, initial=None)
```

A few places where Python parts ways with Clojure:

| | Clojure `reductions` | Python `accumulate` |
|---|---|---|
|Default operation|must be given|`operator.add` — sum is free|
|Argument order|`(reductions f init xs)`|`accumulate(xs, f, initial=…)` — iterable **first**|
|With an initial value|`(reductions f init xs)`|`initial=` keyword (3.8+), output is one longer|
|Laziness|lazy seq|lazy iterator — wrap in `list()` to see it|

Here are the same examples.

```python
# ============================================
# Setup
# ============================================

from itertools import accumulate
import operator

# ============================================
# 1. Running Sum (Prefix Sum)
# ============================================

list(accumulate([1, 2, 3, 4, 5]))

# => [1, 3, 6, 10, 15]
# add is the DEFAULT — no function needed

# ============================================
# 2. Running Product (Factorial Sequence)
# ============================================

list(accumulate([1, 2, 3, 4, 5], operator.mul))

# => [1, 2, 6, 24, 120]

# ============================================
# 3. Running Maximum
# ============================================

list(accumulate([3, 1, 5, 2, 7, 4], max))

# => [3, 3, 5, 5, 7, 7]
# max/min are plain functions — pass them directly

# ============================================
# 4. Running Minimum
# ============================================

list(accumulate([5, 7, 3, 8, 2, 9], min))

# => [5, 5, 3, 3, 2, 2]

# ============================================
# 5. Growing Prefixes
# ============================================

list(accumulate([1, 2, 3, 4], lambda acc, x: acc + [x], initial=[]))

# =>
# []
# [1]
# [1, 2]
# [1, 2, 3]
# [1, 2, 3, 4]

# note: `acc + [x]` builds a NEW list each step (correct but O(n²)).
# `acc.append(x)` would mutate and return None — every element would
# end up being the same object. Accumulators must be immutable-ish.

# ============================================
# 6. Growing String
# ============================================

list(accumulate(["H", "e", "l", "l", "o"], initial=""))

# =>
# ''
# 'H'
# 'He'
# 'Hel'
# 'Hell'
# 'Hello'

# str + str is just add, so the default function already works

# ============================================
# 7. Building a Path
# ============================================

list(accumulate(
    [(1, 0), (0, 1), (2, 0), (-1, -1)],
    lambda pos, d: (pos[0] + d[0], pos[1] + d[1]),
    initial=(0, 0),
))

# =>
# (0, 0)
# (1, 0)
# (1, 1)
# (3, 1)
# (2, 0)

# ============================================
# 8. Running Frequency Map
# ============================================

from collections import Counter

list(accumulate("abaca", lambda c, x: c + Counter(x), initial=Counter()))

# =>
# Counter()
# Counter({'a': 1})
# Counter({'a': 1, 'b': 1})
# Counter({'a': 2, 'b': 1})
# Counter({'a': 2, 'b': 1, 'c': 1})
# Counter({'a': 3, 'b': 1, 'c': 1})

# Counter + Counter is defined, which is why this stays a one-liner

# ============================================
# 9. Running Set
# ============================================

list(accumulate([1, 2, 1, 3, 2], lambda s, x: s | {x}, initial=set()))

# =>
# set()
# {1}
# {1, 2}
# {1, 2}
# {1, 2, 3}
# {1, 2, 3}

# `s | {x}` returns a new set;  s.add(x) returns None — same trap as #5

# ============================================
# 10. Running Map Construction
# ============================================

list(accumulate([("a", 1), ("b", 2), ("c", 3)],
                lambda m, kv: m | {kv[0]: kv[1]},
                initial={}))

# =>
# {}
# {'a': 1}
# {'a': 1, 'b': 2}
# {'a': 1, 'b': 2, 'c': 3}

# `m | {k: v}` is dict-merge (3.9+) — the immutable assoc

# ============================================
# 11. Undo / History (State Machine)
# ============================================

list(accumulate([-20, +50, -10, +30], initial=100))

# =>
# 100
# 80
# 130
# 120
# 150

# a running balance is just accumulate with an opening balance

# ============================================
# 12. Tree Traversal Path
# ============================================

list(accumulate(["home", "documents", "projects", "clojure"],
                lambda p, seg: p + [seg],
                initial=[]))

# =>
# []
# ['home']
# ['home', 'documents']
# ['home', 'documents', 'projects']
# ['home', 'documents', 'projects', 'clojure']

# for real paths, use pathlib:
from pathlib import Path
list(accumulate(["home", "documents", "projects"],
                lambda p, seg: p / seg,
                initial=Path(".")))
# => [Path('.'), Path('home'), Path('home/documents'), ...]
```

---

## The common mental model

|Pattern|Example|Python|
|---|---|---|
|Running Sum|prefix sums|`accumulate(xs)`|
|Running Product|factorials|`accumulate(xs, mul)`|
|Running Max/Min|best-so-far|`accumulate(xs, max)`|
|Growing Collection|build prefixes|`accumulate(xs, lambda a, x: a + [x], initial=[])`|
|Running String|progressive parsing|`accumulate(xs, initial="")`|
|Running Set|seen-so-far|`accumulate(xs, lambda s, x: s \| {x}, initial=set())`|
|Running Map|index construction|`accumulate(xs, lambda m, kv: m \| dict([kv]), initial={})`|
|Running Frequency|histogram over time|`accumulate(xs, lambda c, x: c + Counter(x), initial=Counter())`|
|Running Position|path simulation|`accumulate(deltas, add_vec, initial=origin)`|
|Running State|undo/redo, FSM|`accumulate(events, step, initial=state0)`|

**Rule of thumb:**

- `map` → transform each item independently.

- `functools.reduce` → compute one final result.

- `itertools.accumulate` → **show the journey**, returning every intermediate state. This is why it's so useful for debugging, visualizations, animations, state machines, dynamic programming, and algorithms where the evolution of state matters just as much as the final answer.

---

## Python-specific notes

```python
from functools import reduce
from itertools import accumulate
import operator

xs = [1, 2, 3, 4]

# reduce and accumulate are the same fold; one keeps the tape.
reduce(operator.add, xs)                # => 10          the destination
list(accumulate(xs))                    # => [1,3,6,10]  the journey
reduce(operator.add, xs) == list(accumulate(xs))[-1]     # => True

# --- ARGUMENT ORDER differs between them (a real source of bugs)
reduce(operator.add, xs, 100)           # func FIRST, initial POSITIONAL
list(accumulate(xs, operator.add, initial=100))   # iterable FIRST, initial KEYWORD

# --- `initial` makes the output ONE LONGER
len(list(accumulate(xs)))                       # => 4
len(list(accumulate(xs, initial=0)))            # => 5
# the extra element is the initial value itself, emitted before any input

# --- accumulate is LAZY and single-pass
acc = accumulate(xs)
next(acc)                                       # => 1     computed on demand
list(acc)                                       # => [3, 6, 10]
list(acc)                                       # => []    already exhausted

# --- the accumulator function is f(accumulated, element) — NOT commutative-safe
list(accumulate([1, 2, 3], operator.sub))       # => [1, -1, -4]
# 1, then 1-2 = -1, then -1-3 = -4.  Order matters; check it.

# --- infinite streams work fine, because it's lazy
from itertools import count, islice
list(islice(accumulate(count(1)), 5))           # => [1, 3, 6, 10, 15]

# --- when the accumulator is a mutable object, yield copies
def running_seen(xs):
    seen = set()
    for x in xs:
        seen.add(x)
        yield frozenset(seen)      # snapshot! yielding `seen` gives N aliases
list(running_seen([1, 2, 1]))
# => [frozenset({1}), frozenset({1, 2}), frozenset({1, 2})]

# --- there is also a sum-only shortcut for numeric data
import statistics
# no stdlib "cumsum"; accumulate IS it. (numpy has np.cumsum for arrays.)
```

---

### Memory Hooks

|You want|You reach for|
|---|---|
|prefix sums|`accumulate(xs)`|
|running product|`accumulate(xs, mul)`|
|best so far|`accumulate(xs, max)`|
|start from a seed|`accumulate(xs, f, initial=seed)`|
|just the final answer|`reduce(f, xs)`|
|the journey, infinitely|`islice(accumulate(count()), n)`|
|state machine trace|`accumulate(events, step, initial=state0)`|

---

### Key Insight

**`reduce` and `accumulate` are the same fold. The only question is whether you keep the tape.** Once that clicks, a surprising number of problems stop needing a loop at all. "Best so far", "running balance", "everything seen up to here", "where was I after each move" — all one `accumulate` with the right two-argument function.

The trap in Python is **mutation**. Your accumulator function has to *return a new value* rather than change one in place. `lambda s, x: s | {x}` works; `lambda s, x: s.add(x)` quietly accumulates `None`. Clojure's immutable defaults make this impossible to get wrong. In Python it's the first thing to check when an `accumulate` gives you a column of `None`s, or N references to the same object.
