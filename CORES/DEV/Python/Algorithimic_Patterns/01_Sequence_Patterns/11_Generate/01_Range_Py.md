# Pattern 31 — Range Generation

## Mental Model

Generate a **sequence of values following a regular interval**.

Unlike **Repeat**, which duplicates the same value, **Range** generates **progressively changing values**.

Python's `range` is not a generator — it is a **lazy sequence object**. It has a length, supports indexing and slicing, tests membership in O(1), and can be iterated any number of times. `itertools.count` is the unbounded, float-capable cousin.

---

## Relationship to Cognitive Verb

```text
Generate
    ↓
Range
```

Range is a **Generate** pattern because it creates a new sequence from a start, end, and optional step.

---

## Python Functions & Common Idioms

|Variation|Example|Common Python|
|---|---|---|
|Natural Numbers|`0 1 2 3`|`range(4)`|
|Start & End|`3 4 5 6 7`|`range(3, 8)`|
|Step Size|`0 2 4 6 8`|`range(0, 10, 2)`|
|Descending|`10 8 6 4 2`|`range(10, 0, -2)`|
|Infinite|`0 1 2 …`|`itertools.count()`|
|Float Steps|`0.0 0.5 1.0`|`count(0, 0.5)` or integer math|
|Index + Value|`(0,'a') (1,'b')`|`enumerate(xs)`|
|Grid Coordinates|`(x, y)` pairs|`itertools.product(range, range)`|
|Chunk Boundaries|batching|`range(0, len(xs), n)`|
|Letters|`A B C`|`string.ascii_uppercase`|

> **Note:** `range` is **half-open** — `range(a, b)` includes `a` and excludes `b`, so `len(range(a, b)) == b - a`. Every other Python slicing convention agrees with it, which is why `xs[i:j]` and `range(i, j)` line up exactly.

---

## Common Uses

- Loop indices

- Coordinate generation

- Animation frames

- Time intervals

- Pagination

- Test data

- Number sequences

- Grid generation

---

## Hidden Interview Problems

- Generate numbers from 1 to N

- FizzBuzz

- Matrix coordinates

- Pagination

- Number series

- Iterate over indices

- Binary search bounds

---

## Recognition Clues

If you hear:

- Generate numbers

- From X to Y

- Every N steps

- Indices

- Sequence of integers

- Counting

- Loop N times

Think:

**→ Range**

---

## Pattern Summary

|Property|Value|
|---|---|
|Cognitive Verb|Generate|
|Pattern|Range|
|Input|start, stop, step|
|Output|lazy integer sequence|
|Bounds|half-open `[start, stop)`|
|Memory|O(1) — stores only 3 ints|
|Re-iterable|Yes (unlike a generator)|
|Integers Only|Yes — use `count` for floats|
|Primary Use|Sequential generation|

---

## Python Recipe Book

```python
# ============================================
# The three forms

list(range(5))                          # => [0, 1, 2, 3, 4]
list(range(3, 8))                       # => [3, 4, 5, 6, 7]
list(range(0, 10, 2))                   # => [0, 2, 4, 6, 8]

# stop is EXCLUSIVE. range(1, 11) for "1 to 10" — this is the
# single most common off-by-one in Python.

# ============================================
# range is a SEQUENCE, not a generator

r = range(1_000_000)
len(r)                                  # => 1000000     instant
r[500]                                  # => 500         O(1) indexing
r[10:20:2]                              # => range(10, 20, 2)   slices!
999_999 in r                            # => True        O(1) for ints
list(r) == list(r)                      # => True        re-iterable

import sys
sys.getsizeof(range(10 ** 9))           # => 48 bytes    regardless of size

# a generator would fail every line above. range stores start/stop/step
# and computes the rest — which is why `for i in range(10**9)` is fine.

# ============================================
# Descending

list(range(10, 0, -2))                  # => [10, 8, 6, 4, 2]
list(range(5, -1, -1))                  # => [5, 4, 3, 2, 1, 0]   down to 0

# the stop is still exclusive, so counting down TO zero stops at -1.
# easier to read:
list(reversed(range(6)))                # => [5, 4, 3, 2, 1, 0]

# the silent-empty trap — wrong step sign gives you nothing, no error:
list(range(10, 0))                      # => []      needs step=-1
list(range(0, 10, -1))                  # => []      same mistake

# ============================================
# Infinite

from itertools import count, islice, takewhile

list(islice(count(), 10))               # => [0..9]
list(islice(count(10, 5), 4))           # => [10, 15, 20, 25]

# count() is the unbounded range. ALWAYS pair it with islice,
# takewhile, zip against a finite sequence, or a break.

# ============================================
# Float steps — range refuses, count allows

# range(0, 1, 0.1)   → TypeError: 'float' object cannot be interpreted as int

list(islice(count(0, 0.5), 5))          # => [0, 0.5, 1.0, 1.5, 2.0]

# but floats drift. The safe idiom is integer math, scaled:
[i / 10 for i in range(0, 11, 2)]       # => [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]

# n evenly-spaced points including both ends:
def linspace(a, b, n):
    return [a + (b - a) * i / (n - 1) for i in range(n)]

linspace(0, 1, 5)                       # => [0.0, 0.25, 0.5, 0.75, 1.0]

# ============================================
# Index + value — don't range(len())

xs = ["a", "b", "c"]

for i, x in enumerate(xs):              # => (0,'a') (1,'b') (2,'c')
    ...

list(enumerate(xs, start=1))            # => [(1,'a'), (2,'b'), (3,'c')]

# `for i in range(len(xs)): x = xs[i]` is the classic non-Pythonic loop.
# range(len(xs)) is only right when you need the INDEX ALONE — e.g.
# to mutate xs[i], or to index two lists at once.

# ============================================
# Loop n times, index unused

for _ in range(3):
    ...                                 # `_` says "I don't need it"

# ============================================
# Chunk / page boundaries — the real workhorse

xs = list(range(10))
[xs[i:i + 3] for i in range(0, len(xs), 3)]
# => [[0,1,2], [3,4,5], [6,7,8], [9]]

# range(0, len, n) generates the START of each chunk. Pagination:
page_size = 20
[(off, off + page_size) for off in range(0, 100, page_size)]
# => [(0,20), (20,40), (40,60), (60,80), (80,100)]

# ============================================
# Coordinate grid

from itertools import product

list(product(range(3), range(2)))
# => [(0,0), (0,1), (1,0), (1,1), (2,0), (2,1)]

# same as the nested comprehension, one level flatter:
[(x, y) for x in range(3) for y in range(2)]         # identical

# a matrix of zeros — note the trap:
grid = [[0] * 3 for _ in range(2)]      # correct: 2 independent rows
bad  = [[0] * 3] * 2                    # WRONG: 2 refs to ONE row
bad[0][0] = 9                           # => [[9,0,0], [9,0,0]]

# ============================================
# Letters and characters

import string
string.ascii_uppercase[:5]              # => 'ABCDE'
[chr(ord("A") + i) for i in range(5)]   # => ['A','B','C','D','E']
list(map(chr, range(65, 70)))           # => ['A','B','C','D','E']

# string.ascii_lowercase, .digits, .punctuation — prefer these
# over chr/ord arithmetic when a name exists

# ============================================
# Time intervals

list(range(0, 61, 15))                  # => [0, 15, 30, 45, 60]

from datetime import date, timedelta
start = date(2026, 1, 1)
[start + timedelta(days=i) for i in range(5)]
# => 2026-01-01 .. 2026-01-05

# range generates the OFFSETS; the domain type does the arithmetic.
# That indirection is how you "range" over anything non-integer.

# ============================================
# FizzBuzz — range's traditional home

["Fizz" * (i % 3 == 0) + "Buzz" * (i % 5 == 0) or str(i)
 for i in range(1, 16)]
# => ['1','2','Fizz','4','Buzz','Fizz','7','8','Fizz','Buzz',
#     '11','Fizz','13','14','FizzBuzz']

# "str" * False is "", and "" or str(i) falls through to the number

# ============================================
# Sum without materializing

sum(range(1, 101))                      # => 5050
sum(range(0, 1_000_000, 3))             # instant, no list built

# ============================================
# Reversed, stepped, sliced — all still lazy

r = range(0, 100, 5)
r[-1]                                   # => 95
list(r[2:5])                            # => [10, 15, 20]
list(reversed(r))[:3]                   # => [95, 90, 85]

# slicing a range gives back a RANGE, not a list. Nothing is built
# until you iterate or call list().

# ============================================
# Compare

range(0, 10, 2)                 # bounded, integer, indexable  → Range
count(0, 2)                     # unbounded                    → Range
accumulate(repeat(2), initial=0)        # same values, slower  → Scan
enumerate(xs)                   # index paired with value      → Range + Zip
cycle([1, 2, 3])                # repeats a pattern            → Cycle
```

---

### Memory Hooks

|You want|You reach for|
|---|---|
|0 to n-1|`range(n)`|
|1 to n|`range(1, n + 1)`|
|every kth|`range(0, n, k)`|
|countdown|`range(n, -1, -1)` or `reversed(range(n+1))`|
|forever|`itertools.count()`|
|float steps|`[i / k for i in range(...)]`|
|index with value|`enumerate(xs)`|
|chunk starts|`range(0, len(xs), n)`|
|a coordinate grid|`product(range(w), range(h))`|
|n times, index unused|`for _ in range(n)`|
|letters|`string.ascii_uppercase`|
|dates|`start + timedelta(days=i) for i in range(n)`|

---

### Key Insight

**`range` is a lazy *sequence*, not a lazy *stream*, and the difference is worth understanding precisely.** It supports `len`, indexing, slicing, reversal, O(1) membership testing, and unlimited re-iteration — all from three stored integers. A generator can do none of that. This is why `range(10**9)` costs 48 bytes while `list(range(10**9))` costs tens of gigabytes, and why you can pass a `range` around and iterate it twice without it silently emptying.

**Half-open bounds are a feature, not a quirk.** `range(a, b)` has exactly `b - a` elements, `range(n)` covers every valid index of a length-`n` list, adjacent ranges tile without overlap or gaps (`range(0,3)` then `range(3,6)`), and `xs[i:j]` matches `range(i, j)` element for element. Every "1 to 10" bug comes from fighting that convention rather than using it.

The habit to build is **generating offsets rather than values**. `range` only makes integers, but almost nothing you actually want is an integer — you want dates, chunk boundaries, grid cells, page windows, characters. In each case `range` produces the index and the domain does the arithmetic: `start + timedelta(days=i)`, `xs[i:i+n]`, `chr(65 + i)`. Once you see `range` as an index generator rather than a number generator, it stops being a loop counter and becomes the backbone of every batching and windowing pattern in the book.
