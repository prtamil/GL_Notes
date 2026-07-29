# Pattern 25 — Rotate

## Mental Model

Shift a sequence **left or right**, wrapping the elements around instead of discarding them.

**Reverse** flips the order. **Rotate** keeps the relative order and just moves where you start.

Lists have no `rotate` in Python, so you write `xs[n:] + xs[:n]`. `collections.deque` **does** have `.rotate(n)`, in place and in O(k), which is why a deque is the real answer for ring buffers and round-robin.

---

## Relationship to Cognitive Verb

```text
Order
   ↓
Rotate
```

Rotate is an **Order** pattern: it picks a new starting point and leaves the circular order intact.

---

## Python Functions & Common Idioms

|Variation|Example|Common Python|
|---|---|---|
|Rotate Left N|`3 4 5 1 2`|`xs[n:] + xs[:n]`|
|Rotate Right N|`4 5 1 2 3`|`xs[-n:] + xs[:-n]`|
|Rotate In Place|ring buffer|`deque.rotate(-n)` left, `.rotate(n)` right|
|Infinite Rotation|circular traversal|`islice(cycle(xs), n, n + len(xs))`|
|All Rotations|every start point|`[xs[i:] + xs[:i] for i in range(len(xs))]`|
|Normalize Rotation|handle large n|`n %= len(xs)`|
|Rotate a String|`"cdeab"`|`s[n:] + s[:n]`|
|Circular Index|wrap access|`xs[i % len(xs)]`|
|Fixed-size Ring|drop oldest|`deque(maxlen=k)`|

> **Note:** `deque.rotate(k)` rotates **right** for positive `k` — the opposite sign convention from slicing, where `xs[n:] + xs[:n]` shifts **left**. Getting this backwards is the single most common rotation bug.

---

## Common Uses

- Circular buffers

- Ring structures

- Round-robin scheduling

- Caesar cipher

- Array rotation

- Playlist rotation

- Cyclic algorithms

- Game turns

---

## Hidden Interview Problems

- Rotate array by k

- Rotate a string

- Check if one string is a rotation of another

- Circular queue

- Ring buffer

- Next player

- Circular indexing

- Find the rotation point of a sorted array

---

## Recognition Clues

If you hear:

- Rotate

- Shift left

- Shift right

- Wrap around

- Circular shift

- New starting point

- Ring

- Cyclic order

Think:

**→ Rotate**

---

## Pattern Summary

|Property|Value|
|---|---|
|Cognitive Verb|Order|
|Pattern|Rotate|
|Rearranges Elements|Yes|
|Wrap Around|Yes|
|Preserves Relative Order|Yes|
|List Cost|O(n) — builds a new list|
|Deque Cost|O(k) — in place|
|Primary Use|Circular reordering|

---

## Python Recipe Book

```python
# ============================================
# Input

from collections import deque
from itertools import cycle, islice

xs = [1, 2, 3, 4, 5]

# ============================================
# Rotate left by 2 — the idiom

n = 2
xs[n:] + xs[:n]                         # => [3, 4, 5, 1, 2]

# read it as "everything from n onward, then the head we cut off"

# ============================================
# Rotate right by 2

xs[-n:] + xs[:-n]                       # => [4, 5, 1, 2, 3]

# same shape with negative indices. Or just rotate left by len - n:
xs[len(xs) - n:] + xs[:len(xs) - n]     # => [4, 5, 1, 2, 3]

# ============================================
# One function, signed — do this once and stop thinking about it

def rotate(xs, n):
    """n > 0 rotates LEFT, n < 0 rotates RIGHT."""
    if not xs:
        return list(xs)
    n %= len(xs)                        # normalizes AND handles negatives
    return xs[n:] + xs[:n]

rotate(xs, 2)                           # => [3, 4, 5, 1, 2]
rotate(xs, -2)                          # => [4, 5, 1, 2, 3]
rotate(xs, 12)                          # => [3, 4, 5, 1, 2]     12 % 5 == 2
rotate(xs, 0)                           # => [1, 2, 3, 4, 5]

# Python's % always returns a non-negative result for a positive modulus,
# so -2 % 5 == 3 — negative rotation falls out for free. In C it would not.

# ============================================
# THE BUG this prevents

xs[7:] + xs[:7]                         # => [1, 2, 3, 4, 5]   silently WRONG
                                        # (both slices clamp; nothing rotates)
# always take n % len(xs) first

# empty input: len(xs) == 0 → ZeroDivisionError on the modulo. Guard it.

# ============================================
# deque.rotate — in place, O(k), and the SIGN IS FLIPPED

d = deque([1, 2, 3, 4, 5])
d.rotate(2)                             # => deque([4, 5, 1, 2, 3])   RIGHT
d.rotate(-2)                            # back to [1, 2, 3, 4, 5]     LEFT

# deque: positive = right.  slicing xs[n:]+xs[:n]: positive = left.
# The mnemonic: rotate(1) moves the LAST element to the FRONT.

# rotate() mutates and returns None — like list.sort() and list.reverse()

# ============================================
# Rotate with cycle — lazy, no negative-index arithmetic

list(islice(cycle(xs), 2, 2 + len(xs)))         # => [3, 4, 5, 1, 2]

# reads as "start reading the infinite loop at offset 2, take len(xs)".
# Works on any iterable; O(n) time but allocates nothing up front.

# ============================================
# All rotations

[xs[i:] + xs[:i] for i in range(len(xs))]
# => [[1,2,3,4,5], [2,3,4,5,1], [3,4,5,1,2], [4,5,1,2,3], [5,1,2,3,4]]

# used for: canonical form of a necklace, checking rotational equality,
# trying every starting point in a circular problem

# ============================================
# Rotate a string

s, n = "abcde", 2
s[n:] + s[:n]                           # => 'cdeab'

# "is b a rotation of a?" — the one-line trick:
def is_rotation(a, b):
    return len(a) == len(b) and b in a + a

is_rotation("abcde", "cdeab")           # => True
is_rotation("abcde", "cdaeb")           # => False

# a + a contains EVERY rotation of a as a substring. Nice and O(n).

# ============================================
# Circular index access — the wrap that needs no rotation at all

[xs[i % len(xs)] for i in range(3, 8)]  # => [4, 5, 1, 2, 3]

# if you only need to READ in a wrapped order, don't build a rotated
# list — index with % and touch nothing.

next_player = (current + 1) % n_players         # the whole of turn order

# ============================================
# Round-robin scheduling

turns = deque(["alice", "bob", "carol"])
for _ in range(5):
    who = turns[0]
    turns.rotate(-1)                    # move to the next player
    ...                                 # alice, bob, carol, alice, bob

# rotate(-1) is O(1) on a deque. xs.append(xs.pop(0)) on a list is O(n).

# ============================================
# Ring buffer — fixed capacity, oldest falls off

ring = deque(maxlen=3)
for x in [1, 2, 3, 4, 5]:
    ring.append(x)
list(ring)                              # => [3, 4, 5]

# maxlen makes appends drop from the far end automatically —
# the "last N events" structure, with no manual trimming

# ============================================
# Caesar cipher — rotation in the alphabet, not the list

import string
def caesar(text, shift):
    a = string.ascii_lowercase
    table = str.maketrans(a, a[shift:] + a[:shift])     # a rotated alphabet
    return text.translate(table)

caesar("hello", 3)                      # => 'khoor'
caesar("khoor", -3)                     # => 'hello'

# ROT13 is caesar(text, 13) — and its own inverse

# ============================================
# Find the rotation point of a sorted-then-rotated array

def rotation_point(a):
    lo, hi = 0, len(a) - 1
    while lo < hi:
        mid = (lo + hi) // 2
        if a[mid] > a[hi]:
            lo = mid + 1
        else:
            hi = mid
    return lo                           # index of the smallest element

rotation_point([4, 5, 1, 2, 3])         # => 2

# O(log n): the rotation preserves enough order for binary search.
# Undo it with rotate(a, rotation_point(a)).

# ============================================
# Rotate then reverse — order matters

rotate(xs, 2)[::-1]                     # => [2, 1, 5, 4, 3]
rotate(xs[::-1], 2)                     # => [3, 2, 1, 5, 4]

# not the same operation. Rotation is not commutative with reversal.

# ============================================
# Rotate a matrix 90° — reverse + transpose, not a "rotate"

m = [[1, 2], [3, 4]]
[list(r) for r in zip(*m[::-1])]        # => [[3, 1], [4, 2]]    clockwise
[list(r) for r in zip(*m)][::-1]        # => [[2, 4], [1, 3]]    counter-cw

# "rotate" in the 2-D sense is a different pattern — see 12_Structure

# ============================================
# Compare

xs[n:] + xs[:n]                 # wrap around, order kept   → Rotate
xs[::-1]                        # flip order                → Reverse
xs[n:]                          # DROP the head, no wrap    → Slice
xs[i % len(xs)]                 # wrapped read, no copy     → Circular index
deque(xs, maxlen=k)             # keep the last k           → Compress
```

---

### Memory Hooks

|You want|You reach for|
|---|---|
|rotate a list left by n|`xs[n:] + xs[:n]`|
|rotate a list right by n|`xs[-n:] + xs[:-n]`|
|safe rotation for any n|`n %= len(xs)` first|
|rotate in place, cheaply|`deque.rotate(n)` (positive = right)|
|to advance a turn|`(i + 1) % n`|
|to read in a wrapped order|`xs[i % len(xs)]`|
|every rotation|`[xs[i:] + xs[:i] for i in range(len(xs))]`|
|"is b a rotation of a?"|`b in a + a`|
|round-robin|`deque` + `rotate(-1)`|
|the last k items only|`deque(maxlen=k)`|
|a rotated sorted array's origin|binary search on `a[mid] > a[hi]`|

---

### Key Insight

**`n %= len(xs)` isn't an optimization, it's the fix that makes this correct.** Slicing clamps out-of-range indices rather than raising, so `xs[7:] + xs[:7]` on a 5-element list quietly hands back the input unrotated. Take the modulo first and two problems disappear at once: an oversized `n` wraps, and a negative `n` becomes a right-rotation for free, because Python's `%` always returns a non-negative result.

**The sign conventions disagree, so pick one and wrap it in a function.** `deque.rotate(2)` goes right; `xs[2:] + xs[:2]` goes left. Nothing at the call site will remind you, and when you get it wrong you get a plausible-looking wrong answer instead of an exception. One `rotate(xs, n)` helper with a docstring beats trying to remember.

Above all: **ask whether you need the rotated sequence at all.** Round-robin turn order is `(i + 1) % n`, an integer, no list. A wrapped read is `xs[i % len(xs)]`, no copy. A ring buffer is `deque(maxlen=k)`, no rotation. Building a rotated list is O(n) of pure allocation, and once rotation happens repeatedly — a scheduler, a game loop, a circular buffer — a `deque` turns that O(n) per step into O(1).
