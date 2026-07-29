# Pattern 14 — Circular Traversal

## Mental Model

Walk a sequence **as if the end joins back onto the beginning**, so iteration wraps around forever or for a set number of laps.

Python gives you two ways to write this, and they are not interchangeable:

- **`itertools.cycle(xs)`** — an infinite stream. You stop it with `islice` or a `break`.
- **`xs[i % len(xs)]`** — arithmetic wrap-around. You keep random access and never build a stream at all.

---

## Relationship to Cognitive Verb

```text
Traversal
      ↓
Circular Traversal
```

Circular Traversal is a **Traversal** pattern where hitting the end **wraps you back to the start** instead of stopping.

---

## Python Functions & Common Idioms

|Variation|Example|Common Python|
|---|---|---|
|Infinite Cycle|`1 2 3 1 2 3 …`|`itertools.cycle(xs)`|
|Fixed Circular Traversal|one complete wrap|`islice(cycle(xs), n)`|
|Circular Pair|`(3, 1)` wraps|`pairwise(xs + xs[:1])`|
|Circular Window|last connects to first|`islice(sliding(cycle(xs), n), len(xs))`|
|Circular Index|`i % n`|`xs[i % len(xs)]`|
|Rotate Then Traverse|different start|`xs[k:] + xs[:k]`, `deque.rotate(-k)`|
|Ring Buffer|bounded, self-evicting|`collections.deque(maxlen=n)`|
|Round-robin turns|next player|`next(cycle_iterator)`|

> **Note:** Unlike Forward Traversal, Circular Traversal never naturally reaches an end. You control it with `islice`, a `break`, or an explicit counter. **`cycle` also caches its input**, so it holds the whole sequence in memory forever — never call it on a huge or infinite iterator.

---

## Common Uses

- Round-robin scheduling

- Ring buffers

- Circular queues

- Game turns

- Polygon processing

- Clock arithmetic

- Music loops

- Animation loops

---

## Hidden Interview Problems

- Next player in a game

- Josephus problem

- Circular array

- Gas station problem

- Circular buffer

- Polygon edge traversal

---

## Recognition Clues

If you hear:

- Wrap around

- Circular array

- Ring

- Loop forever

- Repeat sequence

- Next after last

- Clock

- Round-robin

Think:

**→ Circular Traversal**

---

## Pattern Summary

|Property|Value|
|---|---|
|Cognitive Verb|Traversal|
|Pattern|Circular Traversal|
|Direction|Forward (typically)|
|Stops at End|No|
|Wrap Around|Yes|
|Primary Use|Cyclic processing|
|Python Caveat|`cycle` caches its input — memory grows to `len(xs)`|

---

## Python Recipe Book

```python
# ============================================
# Input

from itertools import cycle, islice, pairwise
from collections import deque

xs = [1, 2, 3]

# ============================================
# Infinite cycle

c = cycle(xs)                           # 1, 2, 3, 1, 2, 3, ... forever
next(c), next(c), next(c), next(c)      # => (1, 2, 3, 1)

# NEVER do list(cycle(xs)) — it will not stop.

# ============================================
# Traverse two complete cycles

list(islice(cycle(xs), 6))              # => [1, 2, 3, 1, 2, 3]

# ============================================
# Start from a different position

list(islice(cycle(xs), 1, 7))           # => [2, 3, 1, 2, 3, 1]

# ============================================
# Rotate then traverse

list(islice(cycle(xs), 2, 5))           # => [3, 1, 2]

# eagerly, without itertools — this is THE rotation idiom
k = 2
xs[k:] + xs[:k]                         # => [3, 1, 2]     rotate left by 2
xs[-k:] + xs[:-k]                       # => [2, 3, 1]     rotate right by 2

# or with a deque, which rotates in place in O(k)
d = deque(xs)
d.rotate(-2)                            # negative = leftwards
list(d)                                 # => [3, 1, 2]

# ============================================
# Circular indexing — the arithmetic form

n = len(xs)
[xs[i % n] for i in range(8)]           # => [1, 2, 3, 1, 2, 3, 1, 2]

# `i % n` also handles negatives correctly in Python:
xs[-1 % 3]                              # => 3      (-1 % 3 == 2, not -1)

# This is the form to use when you need the INDEX, not just the value —
# neighbours on a ring, clock arithmetic, hash probing.

# ============================================
# Circular pair — last element pairs back to the first

list(pairwise(xs + xs[:1]))
# => [(1, 2), (2, 3), (3, 1)]

# the index form, same result
[(xs[i], xs[(i + 1) % n]) for i in range(n)]
# => [(1, 2), (2, 3), (3, 1)]

# this is exactly polygon-edge traversal: n vertices → n edges

# ============================================
# Circular window of size 3

wrapped = xs + xs[:2]                   # => [1, 2, 3, 1, 2]
[wrapped[i:i+3] for i in range(len(xs))]
# => [[1, 2, 3], [2, 3, 1], [3, 1, 2]]

# rule: to get circular windows of size k, append the first k-1 elements

# ============================================
# Enumerate a circular traversal

list(enumerate(islice(cycle(xs), 7)))
# => [(0,1), (1,2), (2,3), (3,1), (4,2), (5,3), (6,1)]

# ============================================
# Game turns — next player

players = cycle(["Alice", "Bob", "Cara"])
[next(players) for _ in range(5)]
# => ['Alice', 'Bob', 'Cara', 'Alice', 'Bob']

# the deque version, when you need to SEE the whole rotation
turn = deque(["Alice", "Bob", "Cara"])
turn.rotate(-1)
list(turn)                              # => ['Bob', 'Cara', 'Alice']

# ============================================
# Ring buffer — fixed capacity, oldest falls off

buf = deque(maxlen=3)
for x in [1, 2, 3, 4, 5]:
    buf.append(x)
list(buf)                               # => [3, 4, 5]

# deque(maxlen=n) IS a ring buffer; you never write the wrap logic.

# ============================================
# Josephus problem — eliminate every k-th person around a circle

def josephus(n, k):
    ring = deque(range(1, n + 1))
    order = []
    while ring:
        ring.rotate(-(k - 1))           # step k-1 forward
        order.append(ring.popleft())    # the k-th one is eliminated
    return order

josephus(7, 3)                          # => [3, 6, 2, 7, 5, 1, 4]
josephus(7, 3)[-1]                      # => 4     the survivor

# rotate + popleft is the whole algorithm — no modular index bookkeeping

# ============================================
# Gas station problem — a circular scan in one pass

def can_complete(gas, cost):
    if sum(gas) < sum(cost):
        return -1
    start, tank = 0, 0
    for i, (g, c) in enumerate(zip(gas, cost)):
        tank += g - c
        if tank < 0:                    # can't reach i+1 from `start`
            start, tank = i + 1, 0      # so restart after i
    return start

can_complete([1, 2, 3, 4, 5], [3, 4, 5, 1, 2])      # => 3

# The circular problem is solved WITHOUT wrapping — the insight is that
# if total gas >= total cost, exactly one start works, and it's the one
# after the last deficit. Wrapping would make this O(n²).

# ============================================
# Clock arithmetic

def add_hours(hour, delta):
    return (hour + delta) % 12 or 12    # 12-hour clock, no zero

add_hours(11, 3)                        # => 2

# ============================================
# Neighbours on a ring

def ring_neighbours(xs, i):
    n = len(xs)
    return xs[(i - 1) % n], xs[(i + 1) % n]

ring_neighbours([10, 20, 30], 0)        # => (30, 20)    wraps both ways

# ============================================
# THE TRAP — cycle() caches everything it sees

# c = cycle(open("huge.log"))     ← reads the entire file into memory
#                                   before the second lap, forever.
# cycle is for SMALL, finite sequences. For anything big, re-open
# or re-create the source each lap instead.

# and cycle on an empty sequence hangs rather than raising:
# next(cycle([]))                 ← StopIteration... actually loops forever
#                                   producing nothing. Guard with `if xs:`.

# ============================================
# Compare

list(islice(cycle(xs), 7))              # wrap forever, stop by count
[xs[i % len(xs)] for i in range(7)]     # wrap by arithmetic, keeps indices
xs[k:] + xs[:k]                         # ONE wrap — that's Rotate, not cycle
deque(xs, maxlen=3)                     # bounded ring, self-evicting
```

---

### Memory Hooks

|You want|You reach for|
|---|---|
|forever|`cycle(xs)`|
|n items, wrapping|`islice(cycle(xs), n)`|
|wrap by index|`xs[i % len(xs)]`|
|rotate once|`xs[k:] + xs[:k]`|
|rotate in place|`deque.rotate(-k)`|
|edges of a polygon|`pairwise(xs + xs[:1])`|
|circular windows of k|append the first `k-1`, then window|
|a ring buffer|`deque(maxlen=n)`|
|next player|`next(cycle_iter)`|

---

### Key Insight

**There are two ways to implement this, and picking the wrong one is what makes it feel hard.** `cycle` is a *stream*, perfect for "keep taking turns" and useless the moment you need to know *where* you are. `i % len(xs)` is *arithmetic*, perfect for neighbours, edges and clocks, because you still have the index.

For circular *windows* there's a trick worth stealing: **tack the first `k-1` elements onto the end and treat it as a linear problem.** `pairwise(xs + xs[:1])` gives you polygon edges; `xs + xs[:2]` gives you circular triples. No modular indexing, no special case for the last element.

One Python-specific warning: **`cycle` memorises its input.** It has to, so it can replay it, which means it quietly turns any iterator into a fully buffered list. On a small ring of players that costs nothing. On a log file it's your whole memory budget.
