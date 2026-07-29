# Pattern 16 — Repeat

## Mental Model

Generate the **same value multiple times** or **repeat an entire sequence**.

Unlike **FlatMap**, which expands by transformation, **Repeat** expands by duplication.

Python splits this three ways: **`*`** for lists and strings (eager), **`itertools.repeat`** for one value (lazy), **`itertools.cycle`** for a whole sequence (lazy).

---

## Relationship to Cognitive Verb

```text
Expand
   ↓
Repeat
```

Repeat is an **Expand** pattern because it increases the size of a sequence by duplicating values or sequences.

---

## Python Functions & Common Idioms

|Variation|Example|Common Python|
|---|---|---|
|Repeat Value N Times|`A A A`|`["A"] * 3`, `repeat("A", 3)`|
|Infinite Repeat|`A A A …`|`itertools.repeat("A")`|
|Repeat Entire Sequence|`1 2 3 1 2 3`|`[1,2,3] * 2`, `cycle([1,2,3])`|
|Repeat with Limit|first N repeats|`islice(repeat(x), n)`|
|Repeat Pattern|`A B A B`|`islice(cycle("AB"), n)`|
|Duplicate Each Element|`1 1 2 2 3 3`|`[y for x in xs for y in [x]*2]`|
|Repeat a String|`"***"`|`"*" * 3`|
|Initialize a List|`[0,0,0,0,0]`|`[0] * 5`|
|Pad a Sequence|`1 2 3 0 0 0`|`xs + [0] * 3`|

> **Note:** `repeat` duplicates **one value**; `cycle` repeats an **entire sequence**. Python adds a third: the `*` operator, which does both eagerly — `[x] * n` for a value, `xs * n` for a sequence.

---

## Common Uses

- Default values

- Padding

- Test data generation

- Infinite streams

- Animation loops

- Round-robin processing

- Sequence duplication

- Pattern generation

---

## Hidden Interview Problems

- Initialize an array

- Pad sequences

- Generate repeated patterns

- Create infinite streams

- Duplicate each element

- Repeat values K times

---

## Recognition Clues

If you hear:

- Repeat

- Duplicate

- Same value

- Fill

- Pad

- Infinite sequence

- Cycle

- Repeat K times

Think:

**→ Repeat**

---

## Pattern Summary

|Property|Value|
|---|---|
|Cognitive Verb|Expand|
|Pattern|Repeat|
|Output Size|Larger than input|
|Expands By|Duplication|
|Infinite Version|Yes (`repeat`, `cycle`)|
|Primary Use|Replication|
|Python Caveat|`[[]] * n` shares ONE inner list|

---

## Python Recipe Book

```python
# ============================================
# Input

from itertools import repeat, cycle, islice, chain

# ============================================
# Repeat a value N times

["x"] * 5                               # => ['x','x','x','x','x']
list(repeat("x", 5))                    # => ['x','x','x','x','x']

# `*` is eager and gives a list; repeat() is lazy and gives an iterator.

# ============================================
# Infinite repeat

list(islice(repeat("Hi"), 6))
# => ['Hi','Hi','Hi','Hi','Hi','Hi']

# repeat() with no count never ends — always bound it

# ============================================
# Repeat an entire sequence

[1, 2, 3] * 2                           # => [1, 2, 3, 1, 2, 3]
list(islice(cycle([1, 2, 3]), 8))       # => [1, 2, 3, 1, 2, 3, 1, 2]

# `*` requires a whole-number multiple; cycle can stop mid-lap.

# ============================================
# Repeat a pattern

list(islice(cycle(["A", "B"]), 10))
# => ['A','B','A','B','A','B','A','B','A','B']

list(islice(cycle(["red", "green", "blue"]), 12))
# => ['red','green','blue', 'red','green','blue', 'red','green','blue', ...]

# ============================================
# Duplicate every element (interleaved, not appended)

xs = [1, 2, 3]
[y for x in xs for y in [x] * 2]        # => [1, 1, 2, 2, 3, 3]
[y for x in xs for y in [x] * 3]        # => [1,1,1, 2,2,2, 3,3,3]

# the lazy form
list(chain.from_iterable(repeat(x, 2) for x in xs))     # => [1,1,2,2,3,3]

# CONTRAST — note where the repetition lands:
xs * 2                                  # => [1, 2, 3, 1, 2, 3]   whole seq
[y for x in xs for y in [x] * 2]        # => [1, 1, 2, 2, 3, 3]   each element

# ============================================
# Repeat characters

"*" * 8                                 # => '********'
"ab" * 3                                # => 'ababab'
"".join(repeat("-", 20))                # => '--------------------'

# for formatting, prefer the built-in string methods
"x".center(9, "-")                      # => '----x----'
"5".rjust(3, "0")                       # => '005'
f"{5:03d}"                              # => '005'

# ============================================
# Initialize a list

[0] * 5                                 # => [0, 0, 0, 0, 0]
[None] * 3                              # => [None, None, None]

# ============================================
# THE TRAP — `*` copies REFERENCES, not objects

grid = [[0] * 3] * 3                    # looks like a 3x3 grid
grid[0][0] = 9
grid                                    # => [[9,0,0], [9,0,0], [9,0,0]]
                                        #     all three rows are the SAME list

# correct: build a new inner list each time
grid = [[0] * 3 for _ in range(3)]
grid[0][0] = 9
grid                                    # => [[9,0,0], [0,0,0], [0,0,0]]

# [0] * 3 is safe because ints are immutable — you can't mutate a 0.
# [[]] * 3 is not. The rule: `*` is safe for immutable elements only.

# ============================================
# Pad a sequence

xs + [0] * 3                            # => [1, 2, 3, 0, 0, 0]

# pad TO a length (the common real need)
def pad_to(xs, n, fill=0):
    return list(xs) + [fill] * max(0, n - len(xs))

pad_to([1, 2, 3], 6)                    # => [1, 2, 3, 0, 0, 0]
pad_to([1, 2, 3], 2)                    # => [1, 2, 3]   never truncates

# strings have this built in
"7".zfill(4)                            # => '0007'
"ab".ljust(5, ".")                      # => 'ab...'

# pad several sequences to a common length
from itertools import zip_longest
list(zip_longest([1, 2, 3], [4], fillvalue=0))
# => [(1, 4), (2, 0), (3, 0)]

# ============================================
# repeat() as a constant argument to map/zip

list(map(pow, [1, 2, 3], repeat(2)))    # => [1, 4, 9]   square each

# repeat() with no count is the idiomatic "constant column" for map.
# It never ends, but map stops at the shortest argument.

list(zip("abc", repeat(0)))             # => [('a',0), ('b',0), ('c',0)]

# ============================================
# repeat() as a fast loop counter

for _ in repeat(None, 3):
    ...        # marginally faster than range(3) — no int objects created

# ============================================
# Test data generation

rows = [{"id": i, "status": s}
        for i, s in enumerate(islice(cycle(["ok", "fail"]), 6))]
# => [{'id':0,'status':'ok'}, {'id':1,'status':'fail'}, ...]

# ============================================
# Repeat vs the Compress patterns — they're inverses

from itertools import groupby
rle = [(v, len(list(g))) for v, g in groupby([1, 1, 1, 2, 2])]
# => [(1, 3), (2, 2)]                                encode

list(chain.from_iterable(repeat(v, n) for v, n in rle))
# => [1, 1, 1, 2, 2]                                 decode — pure repeat

# RLE decoding IS this pattern. See 06_Compress/03_RLE.

# ============================================
# Compare

["x"] * 3                               # value × 3, eager   → list
list(repeat("x", 3))                    # value × 3, lazy    → iterator
xs * 3                                  # sequence × 3       → [1,2,3,1,2,3,1,2,3]
list(islice(cycle(xs), 7))              # sequence, any len  → [1,2,3,1,2,3,1]
[y for x in xs for y in [x]*3]          # each element × 3   → [1,1,1,2,2,2,3,3,3]
```

---

### Memory Hooks

|You want|You reach for|
|---|---|
|n copies of a value|`[x] * n`|
|n copies, lazily|`repeat(x, n)`|
|forever|`repeat(x)`|
|the sequence n times|`xs * n`|
|the sequence, any length|`islice(cycle(xs), k)`|
|each element n times|`[y for x in xs for y in [x]*n]`|
|a filled list|`[0] * n`|
|a filled 2D grid|`[[0]*c for _ in range(r)]` — never `[[0]*c]*r`|
|padding|`xs + [fill] * (n - len(xs))`|
|a constant column for `map`|`repeat(k)`|

---

### Key Insight

**`*` duplicates references, not objects.** `[0] * 5` is fine forever because you cannot mutate an integer; `[[]] * 5` gives you five names for one list, and the bug only appears when something writes to it. The rule that always holds: **`*` for immutable elements, a comprehension for mutable ones.**

The second distinction worth keeping sharp is *where* the repetition lands. `xs * 2` repeats the **whole sequence** (`1 2 3 1 2 3`); a flatmap over `[x] * 2` repeats **each element** (`1 1 2 2 3 3`). Both are "repeat twice", and they produce completely different data — the question to ask out loud is "repeat the list, or repeat the items?"
