# Pattern 6 — Zip

## Mental Model

Fold **several sequences together element by element** into one sequence of tuples.

Python names this pattern outright: **`zip`** is a builtin. It's lazy, handing over tuples as you ask for them, and it stops the moment the shortest input runs out.

---

## Relationship to Cognitive Verb

```text
Pair
   ↓
Zip
```

Zip is the simplest form of the **Pair** verb, matching up corresponding elements from two or more sequences.

---

## Python Functions & Common Idioms

|Variation|Example|Common Python|
|---|---|---|
|Zip Two Sequences|`(1,'a') (2,'b')`|`zip(xs, ys)`|
|Zip Three Sequences|`(1,'a','x')`|`zip(xs, ys, zs)`|
|Zip with Function|`(1, 10) → 11`|`[a + b for a, b in zip(xs, ys)]`, `map(add, xs, ys)`|
|Zip with Index|`(0,'a') (1,'b')`|`enumerate(xs)`|
|Zip Keys & Values|`{'a': 1}`|`dict(zip(keys, vals))`|
|Zip Until Shortest Ends|default behaviour|`zip(...)`|
|Zip Requiring Equal Length|raise on mismatch|`zip(..., strict=True)` (3.10+)|
|Zip Until Longest Ends|pad the short one|`itertools.zip_longest(..., fillvalue=…)`|
|Unzip|`[(1,'a'),(2,'b')]` → two lists|`zip(*pairs)`|

---

## Common Uses

- Pair IDs with values

- Combine names and scores

- Merge columns

- Join parallel arrays

- Create coordinate pairs `(x, y)`

- Build key-value maps

- Combine timestamps with events

- Pair labels with predictions

---

## Hidden Interview Problems

- Merge two sorted results

- Create coordinate points

- Associate IDs with objects

- Build dictionaries/maps

- Pair questions with answers

- Combine parallel datasets

---

## Recognition Clues

If you hear:

- Corresponding elements

- Pair two arrays

- Parallel lists

- Match positions

- Combine columns

- X and Y coordinates

- Keys and values

- Element-wise combine

Think:

**→ Zip**

---

## Pattern Summary

|Property|Value|
|---|---|
|Cognitive Verb|Pair|
|Pattern|Zip|
|Input|Two or more sequences|
|Output|One iterator of tuples (or transformed values)|
|Pairing Rule|Same index|
|Stops At|Shortest sequence (unless `strict=True` / `zip_longest`)|
|Preserves Order|Yes|
|Laziness|Lazy — `zip` returns an iterator, not a list|

---

## Python Recipe Book

```python
# ============================================
# Setup

from itertools import zip_longest, starmap, pairwise, product, chain
from operator import add

nums  = [1, 2, 3]
chars = ['a', 'b', 'c']

# ============================================
# Zip two sequences

list(zip(nums, chars))
# => [(1, 'a'), (2, 'b'), (3, 'c')]

# zip() itself is LAZY — list() is only for display
z = zip(nums, chars)
next(z)                          # => (1, 'a')

# ============================================
# Zip three sequences

list(zip(nums, chars, "xyz"))
# => [(1, 'a', 'x'), (2, 'b', 'y'), (3, 'c', 'z')]

# ============================================
# Zip with a function — element-wise combine

[a + b for a, b in zip([1, 2, 3], [10, 20, 30])]     # => [11, 22, 33]

list(map(add, [1, 2, 3], [10, 20, 30]))              # map takes N iterables
# => [11, 22, 33]

# starmap when the function takes separate args and you already have tuples
list(starmap(add, [(1, 10), (2, 20)]))               # => [11, 22]

# ============================================
# Zip with index — that's enumerate, not zip

list(enumerate(chars))                    # => [(0, 'a'), (1, 'b'), (2, 'c')]
list(enumerate(chars, start=1))           # => [(1, 'a'), (2, 'b'), (3, 'c')]

# don't write zip(range(len(xs)), xs) — enumerate exists for this

# ============================================
# Zip keys and values into a dict

dict(zip(chars, nums))                    # => {'a': 1, 'b': 2, 'c': 3}

# and back out again
d = {'a': 1, 'b': 2}
list(d.items())                           # => [('a', 1), ('b', 2)]

# ============================================
# THE TRAP — zip stops at the shortest, silently

list(zip([1, 2, 3], ['a']))               # => [(1, 'a')]      2 and 3 vanish

# ============================================
# strict=True — refuse to silently truncate (3.10+)

try:
    list(zip([1, 2, 3], ['a'], strict=True))
except ValueError as e:
    print(e)                              # zip() argument 2 is shorter than argument 1

# Use strict=True whenever the inputs are SUPPOSED to be the same length.
# It turns a silent data-loss bug into a loud one.

# ============================================
# zip_longest — pad instead of truncate

list(zip_longest([1, 2, 3], ['a'], fillvalue='-'))
# => [(1, 'a'), (2, '-'), (3, '-')]

# ============================================
# Unzip — the same function, run backwards

pairs = [(1, 'a'), (2, 'b'), (3, 'c')]
ns, cs = zip(*pairs)
# ns => (1, 2, 3)     cs => ('a', 'b', 'c')

# zip(*pairs) is zip((1,'a'), (2,'b'), (3,'c')) — it transposes.
# Note: you get TUPLES back, not lists.

# ============================================
# Zip IS transpose

m = [[1, 2, 3],
     [4, 5, 6]]
list(zip(*m))                             # => [(1, 4), (2, 5), (3, 6)]

# ============================================
# Coordinate points

xs, ys = [0, 1, 2], [10, 11, 12]
points = list(zip(xs, ys))                # => [(0, 10), (1, 11), (2, 12)]

# distance between corresponding points
import math
a, b = [(0, 0), (3, 0)], [(0, 4), (0, 0)]
[math.dist(p, q) for p, q in zip(a, b)]   # => [4.0, 3.0]

# ============================================
# Labels with predictions — accuracy in one line

y_true = [1, 0, 1, 1]
y_pred = [1, 0, 0, 1]
sum(t == p for t, p in zip(y_true, y_pred)) / len(y_true)      # => 0.75

# ============================================
# Sorting by a parallel array

names  = ['carol', 'alice', 'bob']
scores = [72, 95, 88]
[n for _, n in sorted(zip(scores, names), reverse=True)]
# => ['alice', 'bob', 'carol']

# ============================================
# Rows to columns and back (named columns)

header = ['id', 'name']
rows   = [(1, 'a'), (2, 'b')]
[dict(zip(header, r)) for r in rows]
# => [{'id': 1, 'name': 'a'}, {'id': 2, 'name': 'b'}]

# ============================================
# Compare

list(zip(xs, ys))            # same index      → Zip           (this pattern)
list(pairwise(xs))           # index i, i+1    → Adjacent Pair (one sequence)
list(product(xs, ys))        # every × every   → Cartesian Product
list(chain(xs, ys))          # one after other → Concatenate
```

---

### Memory Hooks

|You want|You reach for|
|---|---|
|corresponding elements|`zip(xs, ys)`|
|…and they must match in length|`zip(xs, ys, strict=True)`|
|…and they might not|`zip_longest(xs, ys, fillvalue=…)`|
|position + element|`enumerate(xs)`|
|a dict from two lists|`dict(zip(keys, vals))`|
|element-wise arithmetic|`map(add, xs, ys)`|
|split pairs back apart|`zip(*pairs)`|
|transpose a matrix|`zip(*rows)`|

---

### Key Insight

**`zip` undoes itself.** `zip(*zip(a, b))` hands `a, b` straight back, which is why one builtin covers pairing, unzipping and matrix transposition. Once you see that, three things collapse into one.

The part that catches everyone: **`zip` truncates to the shortest input and never mentions it.** If your sequences are supposed to be parallel, a length mismatch means your data is broken, and `strict=True` is how you hear about it instead of quietly processing three of your five records.
