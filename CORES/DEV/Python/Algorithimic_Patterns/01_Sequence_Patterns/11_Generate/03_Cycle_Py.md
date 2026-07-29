# Pattern 33 — Cycle

## Mental Model

Generate an **infinite repeating sequence** by looping over the same collection again and again.

**Repeat** duplicates a single value. **Cycle** repeats an **entire sequence**.

`itertools.cycle` does exactly this, with one property worth knowing before you start: it **caches every element it sees**, so cycling a large or infinite iterable buys you an unbounded copy in memory.

---

## Relationship to Cognitive Verb

```text
Generate
    ↓
Cycle
```

Cycle is a **Generate** pattern that keeps producing values by starting the sequence over each time it runs out.

---

## Python Functions & Common Idioms

|Variation|Example|Common Python|
|---|---|---|
|Repeat a Sequence|`1 2 3 1 2 3`|`cycle(xs)`|
|Finite Cycle|first n values|`islice(cycle(xs), n)`|
|Alternate|`on off on off`|`cycle(["on", "off"])`|
|Round Robin|repeating turns|`cycle(players)` + `next()`|
|Offset Cycle|start mid-list|`islice(cycle(xs), k, k + n)`|
|Zip with a Cycle|assign colors|`zip(items, cycle(palette))`|
|Exactly k Repeats|`1 2 1 2`|`chain.from_iterable(repeat(xs, k))`|
|List Repetition|eager|`xs * k`|
|Toggle Two States|flip-flop|`next(toggler)`|

> **Note:** `cycle` returns a **lazy infinite iterator**, so it must always be bounded — by `islice`, by `zip` against something finite, or by calling `next()` a controlled number of times. Iterating it bare in a `for` loop never ends.

---

## Common Uses

- Round-robin scheduling

- Game turns

- Animation loops

- Infinite playlists

- Periodic signals

- UI themes

- Color palettes

- Ring buffers

---

## Hidden Interview Problems

- Round-robin iterator

- Alternate values

- Repeat patterns

- Circular traversal

- Infinite stream generation

- Scheduling tasks

- Deal cards to n players

---

## Recognition Clues

If you hear:

- Repeat forever

- Loop back

- Circular

- Round robin

- Infinite pattern

- Wrap around

- Endless repetition

Think:

**→ Cycle**

---

## Pattern Summary

|Property|Value|
|---|---|
|Cognitive Verb|Generate|
|Pattern|Cycle|
|Input|any iterable|
|Output|infinite repeating iterator|
|Lazy|Yes|
|Memory|O(n) — caches the source|
|Terminates|Never — the caller must bound it|
|Primary Use|Circular generation|

---

## Python Recipe Book

```python
# ============================================
# Input

from itertools import cycle, islice, repeat, chain, count

xs = [1, 2, 3]

# ============================================
# Repeat a sequence

list(islice(cycle(xs), 10))             # => [1,2,3,1,2,3,1,2,3,1]

# cycle alone is infinite:
# for x in cycle(xs): ...               # never ends. Always bound it.

# ============================================
# Alternate two values

list(islice(cycle(["on", "off"]), 8))
# => ['on','off','on','off','on','off','on','off']

# ============================================
# Cycle characters / any iterable

"".join(islice(cycle("ABC"), 12))       # => 'ABCABCABCABC'
list(islice(cycle({1, 2}), 4))          # works on sets too (order arbitrary)

# ============================================
# Round robin — next() one at a time

players = cycle(["Alice", "Bob", "Carol"])
[next(players) for _ in range(7)]
# => ['Alice','Bob','Carol','Alice','Bob','Carol','Alice']

# a cycle object holds its POSITION. Keep the object, call next()
# when a turn happens — that's a scheduler in two lines.

# ============================================
# Offset cycle — start from the middle

list(islice(cycle([1, 2, 3, 4]), 2, 10))            # => [3,4,1,2,3,4,1,2]

# skip 2, then take 8. This is also how you rotate:
n, k = len([1,2,3,4,5]), 2
list(islice(cycle([1,2,3,4,5]), k, k + n))          # => [3,4,5,1,2]

# ============================================
# Zip with a cycle — the single most useful application

items = ["a", "b", "c", "d", "e"]
palette = ["red", "green", "blue"]

list(zip(items, cycle(palette)))
# => [('a','red'), ('b','green'), ('c','blue'), ('d','red'), ('e','green')]

# zip stops at the SHORTEST — the finite side bounds the infinite one.
# No islice needed, no length arithmetic. This is the pattern:
# "give every item one of these, wrapping as needed".

# alternating table rows:
rows = ["r1", "r2", "r3"]
[(r, cls) for r, cls in zip(rows, cycle(["even", "odd"]))]
# => [('r1','even'), ('r2','odd'), ('r3','even')]

# ============================================
# Deal into n buckets — round-robin distribution

from collections import defaultdict
hands = defaultdict(list)
for card, player in zip(range(10), cycle("ABC")):
    hands[player].append(card)
dict(hands)
# => {'A': [0,3,6,9], 'B': [1,4,7], 'C': [2,5,8]}

# the slicing equivalent, when you already have a list:
deck = list(range(10))
[deck[i::3] for i in range(3)]          # => [[0,3,6,9], [1,4,7], [2,5,8]]

# ============================================
# Exactly k repetitions — cycle can't count

list(chain.from_iterable(repeat(xs, 3)))            # => [1,2,3,1,2,3,1,2,3]
xs * 3                                              # => same, eager, simpler
list(islice(cycle(xs), len(xs) * 3))                # => same, awkward

# `xs * k` for lists, `s * k` for strings. Reach for cycle only when
# the repeat count is unknown or the consumer decides when to stop.

# ============================================
# repeat vs cycle — one value vs one sequence

list(islice(repeat("x"), 6))            # => ['x','x','x','x','x','x']
list(islice(cycle(["x", "y"]), 6))      # => ['x','y','x','y','x','y']

list(repeat("x", 6))                    # => repeat TAKES a count; cycle doesn't

# ============================================
# THE MEMORY TRAP — cycle caches everything

# cycle(open("huge.log"))               # buffers the ENTIRE file in RAM
# cycle(count())                        # grows forever, then MemoryError

# cycle must remember what it saw in order to replay it. That's fine
# for a 3-colour palette and fatal for a large stream. If the source
# is already a list, cycle costs nothing extra — it just holds a
# reference and an index.

# ============================================
# THE MUTATION TRAP — the cache is a snapshot

src = [1, 2, 3]
c = cycle(src)
[next(c) for _ in range(3)]             # => [1, 2, 3]
src.append(4)
[next(c) for _ in range(4)]             # => [1, 2, 3, 1]     no 4!

# once cycle has consumed the source, it replays its own copy.
# Changes to the original never appear.

# ============================================
# A toggle — a cycle of two, as a switch

toggle = cycle([True, False])
next(toggle), next(toggle), next(toggle)            # => (True, False, True)

# clearer than `flag = not flag` scattered through a loop, and
# it generalizes to three or more states for free

# ============================================
# Periodic signal / animation frames

frames = cycle(["|", "/", "-", "\\"])
[next(frames) for _ in range(6)]        # => ['|','/','-','\\','|','/']

# a spinner. Combined with a timer, that's the whole implementation.

# ============================================
# Weekdays forever

days = ["Mon", "Tue", "Wed", "Thu", "Fri"]
list(islice(cycle(days), 10))
# => ['Mon','Tue','Wed','Thu','Fri','Mon','Tue','Wed','Thu','Fri']

# nth weekday from a start point, without generating anything:
days[(days.index("Wed") + 4) % len(days)]           # => 'Tue'

# for a single lookup, MODULAR INDEXING beats cycle — no iterator,
# no state, O(1). Use cycle when you're streaming, not indexing.

# ============================================
# Interleave two cycles of different lengths

list(islice(zip(cycle("AB"), cycle("123")), 6))
# => [('A','1'),('B','2'),('A','3'),('B','1'),('A','2'),('B','3')]

# the combined pattern repeats every lcm(2, 3) = 6 steps

# ============================================
# Bounding an infinite cycle — the three ways

c = lambda: cycle(xs)
list(islice(c(), 7))                    # by COUNT
list(zip(range(4), c()))                # by another finite iterable
next(c())                               # one at a time, caller decides

# there is no takewhile option that's safe here: a predicate that
# never goes false over a repeating sequence loops forever.

# ============================================
# Compare

cycle(xs)               # repeats the whole sequence, forever  → Cycle
repeat(x)               # one value, forever                   → Repeat
repeat(x, n)            # one value, n times                   → Repeat
xs * n                  # whole sequence, n times, eager       → Repeat
xs[i % len(xs)]         # wrapped INDEXING, no iterator        → Rotate
islice(cycle(xs), k, k + len(xs))       # a rotation           → Rotate
```

---

### Memory Hooks

|You want|You reach for|
|---|---|
|an endless repeat of a list|`cycle(xs)`|
|the first n of it|`islice(cycle(xs), n)`|
|to alternate|`cycle([a, b])`|
|turn order|keep the `cycle` object, call `next()`|
|to assign colors/classes|`zip(items, cycle(palette))`|
|to deal into k buckets|`zip(items, cycle(range(k)))`|
|exactly k copies|`xs * k`|
|one value forever|`repeat(x)`|
|to start mid-sequence|`islice(cycle(xs), k, k + n)`|
|a single wrapped lookup|`xs[i % len(xs)]`|

---

### Key Insight

**`zip(items, cycle(pattern))` is why this pattern earns its keep.** Colours for bars, CSS classes for rows, workers for tasks, players for cards — every one of them is "give each item the next thing from a short repeating list". Zip stops at the shortest input, so the finite side bounds the infinite side for you. No length arithmetic, no modulo, no off-by-one.

**Cycle caches, and that's the constraint to remember.** To replay a sequence it has to remember it, so `cycle` over a file handle or an infinite counter grows without limit until the process dies. Over an existing list it costs essentially nothing. There's a corollary that catches people too: once the source has been consumed, `cycle` is replaying its own private copy, so appending to the original list changes nothing.

Finally, know when *not* to use it. **For a single wrapped lookup, use `xs[i % len(xs)]`** — O(1), no iterator, no state. **For exactly k copies, use `xs * k`.** `cycle` is for when the consumer decides when to stop, which is the streaming case: turn order, animation frames, spinners, schedulers. Keeping the `cycle` object alive between calls is what makes it a scheduler instead of a list-builder.
