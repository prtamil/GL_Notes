# Pattern 7 — Interleave

## Mental Model

Combine **multiple sequences by alternating elements** from each sequence.

Python has no `interleave` builtin — the idiom is **`chain.from_iterable(zip(...))`**: zip to group corresponding elements, then flatten to lay them out end to end.

---

## Relationship to Cognitive Verb

```text
Pair
   ↓
Interleave
```

Interleave is a **Pair** pattern that combines sequences by taking **one element from each sequence in turn**.

---

## Python Functions & Common Idioms

|Variation|Example|Common Python|
|---|---|---|
|Interleave Two Sequences|`1 a 2 b 3 c`|`chain.from_iterable(zip(xs, ys))`|
|Interleave Three Sequences|`1 a x 2 b y`|`chain.from_iterable(zip(xs, ys, zs))`|
|Interleave Until Shortest Ends|default behaviour|`zip` inside the chain|
|Interleave Keeping Leftovers|`1 a 2 b 3`|`zip_longest` + filter the sentinel|
|Separate (Reverse Interleave)|`1 2 3` / `a b c`|slicing `xs[0::2]`, `xs[1::2]`|
|Round-robin (uneven lengths)|`1 a 2 b 3`|`itertools` round-robin recipe|
|Interleave with a separator|`a , b , c`|`", ".join(xs)`, or `chain` with `repeat`|
|Alternate Processing|`A B A B`|`cycle` over the sources|

---

## Common Uses

- Merge two event streams

- Alternate animation frames

- Stereo audio (Left, Right)

- RGB component layout

- UI layouts

- Round-robin scheduling

- Alternate turns in games

- Weaving two datasets

---

## Hidden Interview Problems

- Merge two arrays alternately

- Shuffle cards perfectly

- Round-robin task scheduling

- Alternate characters from two strings

- Weave linked lists

- Merge logs chronologically (alternating source)

---

## Recognition Clues

If you hear:

- Alternate

- Every other

- Weave

- Round-robin

- Left, Right

- A B A B

- Alternate turns

- Intermix

Think:

**→ Interleave**

---

## Pattern Summary

|Property|Value|
|---|---|
|Cognitive Verb|Pair|
|Pattern|Interleave|
|Input|Two or more sequences|
|Output|One flat alternating sequence|
|Pairing Rule|Take one from each sequence in turn|
|Stops At|Shortest sequence (unless round-robin)|
|Preserves Order|Yes (within each sequence)|

---

## Python Recipe Book

```python
# ============================================
# Setup

from itertools import chain, zip_longest, cycle, islice, repeat

nums  = [1, 2, 3]
chars = ['a', 'b', 'c']

# ============================================
# Interleave two sequences — THE idiom

list(chain.from_iterable(zip(nums, chars)))
# => [1, 'a', 2, 'b', 3, 'c']

# read it inside-out:
#   zip   → [(1,'a'), (2,'b'), (3,'c')]     group by position
#   chain → 1, 'a', 2, 'b', 3, 'c'          flatten one level

# comprehension form, same thing
[x for pair in zip(nums, chars) for x in pair]
# => [1, 'a', 2, 'b', 3, 'c']

# ============================================
# Interleave three sequences — the idiom doesn't change

list(chain.from_iterable(zip(nums, chars, "xyz")))
# => [1, 'a', 'x', 2, 'b', 'y', 3, 'c', 'z']

# ============================================
# THE TRAP — zip truncates, so leftovers are lost

list(chain.from_iterable(zip([1, 2, 3, 4, 5], ['a', 'b'])))
# => [1, 'a', 2, 'b']         3, 4, 5 are gone

# ============================================
# Keep the leftovers — zip_longest + drop the sentinel

_MISSING = object()
def interleave_all(*seqs):
    zipped = zip_longest(*seqs, fillvalue=_MISSING)
    return [x for group in zipped for x in group if x is not _MISSING]

interleave_all([1, 2, 3, 4, 5], ['a', 'b'])
# => [1, 'a', 2, 'b', 3, 4, 5]

# a sentinel object() is used, not None — None may be a legitimate value

# ============================================
# Round-robin — the itertools recipe, exhausts each source in turn

def roundrobin(*iterables):
    iterators = map(iter, iterables)
    for n in range(len(iterables), 0, -1):
        iterators = cycle(islice(iterators, n))
        yield from map(next, iterators)

list(roundrobin('ABC', 'D', 'EF'))
# => ['A', 'D', 'E', 'B', 'F', 'C']

# Round-robin is interleave that DOESN'T stop at the shortest —
# an exhausted source just drops out of the rotation.

# ============================================
# Separate (reverse interleave) — a slice with a step

woven = [1, 'a', 2, 'b', 3, 'c']
woven[0::2]                       # => [1, 2, 3]      even positions
woven[1::2]                       # => ['a', 'b', 'c'] odd positions

# for k sources: [woven[i::k] for i in range(k)]
rgb = ['r1','g1','b1','r2','g2','b2']
[rgb[i::3] for i in range(3)]
# => [['r1', 'r2'], ['g1', 'g2'], ['b1', 'b2']]

# ============================================
# Stereo audio: two channels ↔ one interleaved buffer

left, right = [1, 3, 5], [2, 4, 6]
buf = list(chain.from_iterable(zip(left, right)))   # => [1, 2, 3, 4, 5, 6]
buf[0::2], buf[1::2]                                # => ([1,3,5], [2,4,6])

# ============================================
# Perfect riffle shuffle

deck = list(range(8))
half = len(deck) // 2
list(chain.from_iterable(zip(deck[:half], deck[half:])))
# => [0, 4, 1, 5, 2, 6, 3, 7]

# ============================================
# Alternate characters from two strings

"".join(chain.from_iterable(zip("abc", "XYZ")))     # => 'aXbYcZ'

# ============================================
# Interleave with a constant separator

list(chain.from_iterable(zip(nums, repeat('|'))))[:-1]
# => [1, '|', 2, '|', 3]

# for strings, just use join — don't be clever
"|".join(map(str, nums))                            # => '1|2|3'

# ============================================
# Alternate turns (infinite)

players = cycle(['X', 'O'])
[next(players) for _ in range(5)]                   # => ['X','O','X','O','X']

# ============================================
# Merge two sorted streams — NOT interleave

import heapq
list(heapq.merge([1, 4, 7], [2, 3, 8]))             # => [1, 2, 3, 4, 7, 8]

# Interleave alternates by POSITION; merge orders by VALUE.
# "Merge logs chronologically" is heapq.merge, not interleave.

# ============================================
# Compare

list(zip(nums, chars))                          # => [(1,'a'), (2,'b'), (3,'c')]
list(chain.from_iterable(zip(nums, chars)))     # => [1,'a',2,'b',3,'c']
list(chain(nums, chars))                        # => [1,2,3,'a','b','c']
list(roundrobin(nums, chars))                   # => [1,'a',2,'b',3,'c'] (uneven-safe)

# zip keeps the pairing. chain.from_iterable(zip(...)) dissolves it.
# chain alone concatenates instead of alternating.
```

---

### Memory Hooks

|You want|You reach for|
|---|---|
|weave two lists|`chain.from_iterable(zip(a, b))`|
|weave, uneven lengths|`roundrobin(a, b)`|
|unweave|`xs[0::2]`, `xs[1::2]`|
|unweave k sources|`[xs[i::k] for i in range(k)]`|
|concatenate instead|`chain(a, b)`|
|order by value instead|`heapq.merge(a, b)`|
|endless alternation|`cycle([...])`|

---

### Key Insight

**Interleave is Zip plus a flatten.** Zip groups elements by position and *keeps* the grouping; interleave dissolves it into a flat stream. Every interleave question in Python is answered by choosing which of those two you want, then whether the flatten should stop at the shortest input.

The distinction worth holding on to: **interleave alternates by position, merge orders by value.** They look identical on two sorted equal-length inputs and diverge completely on everything else — so "merge these two log files" almost always means `heapq.merge`, not this pattern.
