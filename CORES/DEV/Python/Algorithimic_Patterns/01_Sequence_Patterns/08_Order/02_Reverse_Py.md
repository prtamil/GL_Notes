# Pattern 24 — Reverse

## Mental Model

Traverse or view a sequence in the **opposite order**, making the last element first and the first element last.

**Sort** orders by value. **Reverse** just flips whatever order is already there.

Python gives you three spellings, and what separates them is what you get back: **`xs[::-1]`** hands you a new copy, **`reversed(xs)`** a lazy iterator, and **`xs.reverse()`** mutates in place and returns `None`.

---

## Relationship to Cognitive Verb

```text
Order
   ↓
Reverse
```

Reverse is an **Order** pattern because it rearranges elements without touching the elements themselves.

---

## Python Functions & Common Idioms

|Variation|Example|Common Python|
|---|---|---|
|Reverse a Sequence|`3 2 1`|`xs[::-1]`|
|Reverse Lazily|no copy|`reversed(xs)`|
|Reverse In Place|mutate|`xs.reverse()`|
|Reverse a String|`"olleh"`|`s[::-1]`|
|Reverse Then Process|process backwards|`[f(x) for x in reversed(xs)]`|
|Reverse Sorted Order|largest first|`sorted(xs, reverse=True)`|
|Reverse Iterate with Index|`(4,'e') (3,'d')`|`reversed(list(enumerate(xs)))`|
|Reverse Words|`"c b a"`|`" ".join(s.split()[::-1])`|
|Reverse Nested|inner lists|`[r[::-1] for r in rows]`|

> **Note:** `reversed()` needs a sequence with `__len__` and `__getitem__` (or `__reversed__`) — it does **not** work on a generator. To reverse a stream you must materialize it first: `reversed(list(gen))`.

---

## Common Uses

- Undo history

- Stack processing

- Reverse traversal

- Text reversal

- Backtracking

- Reverse chronological order

- Reverse animations

- Data transformation

---

## Hidden Interview Problems

- Reverse an array

- Reverse a string

- Check palindrome

- Reverse a linked list

- Reverse words in a sentence

- Process newest first

- Reverse in place with O(1) memory

---

## Recognition Clues

If you hear:

- Reverse

- Backwards

- Last to first

- Flip order

- Opposite direction

- Undo order

- Reverse traversal

- Mirror

Think:

**→ Reverse**

---

## Pattern Summary

|Property|Value|
|---|---|
|Cognitive Verb|Order|
|Pattern|Reverse|
|Rearranges Elements|Yes|
|Preserves All Elements|Yes|
|Changes Values|No|
|`[::-1]`|new copy, O(n) memory|
|`reversed()`|lazy view, O(1) memory|
|`.reverse()`|in place, returns `None`|
|Primary Use|Reverse ordering|

---

## Python Recipe Book

```python
# ============================================
# Input

from collections import deque
from itertools import islice

xs = [1, 2, 3, 4, 5]

# ============================================
# The three reversals — pick by what you need back

xs[::-1]                                # => [5, 4, 3, 2, 1]    new list
reversed(xs)                            # => <list_reverseiterator>  lazy
xs.reverse()                            # => None               mutates xs

# slice   → you need a list you can keep
# reversed → you're about to iterate once (no copy made)
# .reverse → you own the list and want it flipped

list(reversed(xs))                      # => [5, 4, 3, 2, 1]    same as [::-1]

# ============================================
# Reverse a string

"clojure"[::-1]                         # => 'erujolc'
"".join(reversed("clojure"))            # => 'erujolc'   slower, more typing

# strings are immutable — there is no s.reverse()

# ============================================
# Reverse then map

[n + 1 for n in reversed(xs)]           # => [6, 5, 4, 3, 2]

# reversed() here builds nothing — the comprehension consumes it directly

# ============================================
# Reverse sorted order — do NOT reverse a sort

sorted(xs, reverse=True)                # => [5, 4, 3, 2, 1]    correct
sorted(xs)[::-1]                        # => [5, 4, 3, 2, 1]    same VALUES

# but with ties they differ: reverse=True keeps the original order of
# equal elements, [::-1] flips it. Stability is the reason to prefer
# reverse=True on records.

# ============================================
# Reverse iterate with the ORIGINAL indices

for i, x in reversed(list(enumerate(xs))):
    ...                                 # (4, 5), (3, 4), (2, 3), ...

# the common mistake is enumerate(reversed(xs)) — that renumbers
# from 0 and loses the real positions:
list(enumerate(reversed(xs)))           # => [(0,5), (1,4), (2,3), (3,2), (4,1)]
list(reversed(list(enumerate(xs))))     # => [(4,5), (3,4), (2,3), (1,2), (0,1)]

# ============================================
# Backwards loop without building anything

for i in range(len(xs) - 1, -1, -1):
    ...                                 # 4, 3, 2, 1, 0

# the classic off-by-one trio: start at len-1, stop BEFORE -1, step -1.
# range(len(xs))[::-1] reads better and is just as lazy.

# ============================================
# Reverse nested sequences

rows = [[1, 2, 3], [4, 5], [6, 7, 8]]

[row[::-1] for row in rows]             # => [[3, 2, 1], [5, 4], [8, 7, 6]]

# reverse the ROWS instead of within them:
rows[::-1]                              # => [[6, 7, 8], [4, 5], [1, 2, 3]]

# both at once = 180° rotation of a matrix:
[row[::-1] for row in rows[::-1]]

# ============================================
# Palindrome check

s = "level"
s == s[::-1]                            # => True

# real-world version — ignore case and punctuation:
def is_palindrome(s):
    t = [c.lower() for c in s if c.isalnum()]
    return t == t[::-1]

is_palindrome("A man, a plan, a canal: Panama")     # => True

# O(1)-memory version with two pointers:
def is_palindrome2(s):
    i, j = 0, len(s) - 1
    while i < j:
        if s[i] != s[j]:
            return False
        i, j = i + 1, j - 1
    return True

# ============================================
# Reverse words

" ".join("one two three".split()[::-1])         # => 'three two one'

# reverse the words but not the letters — note split() with no args
# also collapses runs of whitespace, which is usually what you want

# reverse letters within each word instead:
" ".join(w[::-1] for w in "one two three".split())      # => 'eno owt eerht'

# ============================================
# Reverse in place, O(1) memory — the interview answer

def reverse_inplace(a):
    i, j = 0, len(a) - 1
    while i < j:
        a[i], a[j] = a[j], a[i]         # tuple swap, no temp variable
        i, j = i + 1, j - 1
    return a

reverse_inplace([1, 2, 3, 4, 5])        # => [5, 4, 3, 2, 1]

# this is what list.reverse() does. Write it only when asked to.

# ============================================
# THE TRAP — reversed() on a generator

gen = (n for n in range(5))
reversed(gen)
# TypeError: argument to reversed() must be a sequence

reversed(list(gen))                     # fine — but materializes everything

# a stream has no "last element" until it ends. Reversing is inherently
# non-lazy: you cannot yield the tail before reading the head.

# ============================================
# Reverse a file, last line first

# reading it all is fine for small files:
# lines = open("f.txt").readlines()[::-1]

# for a huge file, keep only the tail you need:
# last10 = deque(open("f.txt"), maxlen=10)      # O(10) memory, one pass

# deque(maxlen=n) over a stream is the "last n items" idiom

# ============================================
# Stack / undo — reverse chronological by construction

undo = []
undo.append("typed a")
undo.append("typed b")
undo.pop()                              # => 'typed b'     newest first

# a stack IS reversal, amortized. If you always want newest-first,
# don't reverse a list — append and pop, or use a deque and appendleft.

d = deque()
d.appendleft("oldest")
d.appendleft("newest")                  # newest is now d[0]

# ============================================
# Reverse a slice, and the double-negative trap

xs[::-1]                                # => [5, 4, 3, 2, 1]    whole thing
xs[3:0:-1]                              # => [4, 3, 2]   from 3 DOWN to 1
xs[:2][::-1]                            # => [2, 1]      first two, flipped
xs[-2:]                                 # => [4, 5]      last two, in order

# with a negative step, start and stop swap roles. When it gets confusing,
# slice forward first, then reverse — two clear steps beat one clever one.

# ============================================
# Compare

xs[::-1]                        # flip order, new list      → Reverse
sorted(xs, reverse=True)        # order BY VALUE, descending → Sort
xs[n:] + xs[:n]                 # flip nothing, move start   → Rotate
list(reversed(xs))              # flip order, lazily then    → Reverse
```

---

### Memory Hooks

|You want|You reach for|
|---|---|
|a reversed copy|`xs[::-1]`|
|to iterate backwards|`reversed(xs)`|
|to flip a list you own|`xs.reverse()`|
|a reversed string|`s[::-1]`|
|backwards with real indices|`reversed(list(enumerate(xs)))`|
|a countdown of indices|`range(len(xs))[::-1]`|
|largest-first ordering|`sorted(xs, reverse=True)`|
|palindrome check|`s == s[::-1]`|
|words backwards|`" ".join(s.split()[::-1])`|
|the last n of a stream|`deque(stream, maxlen=n)`|
|O(1)-memory reversal|two-pointer swap loop|

---

### Key Insight

**The three reversals differ only in what they hand back, and that's the entire decision.** `xs[::-1]` copies, `reversed(xs)` doesn't, `xs.reverse()` returns `None`. Iterating once? Use `reversed` and allocate nothing. Keeping the result? Use the slice. Writing `xs = xs.reverse()` is the same `None` bug you get from `.sort()`, and it'll catch you at least once.

**Reversal can't be lazy the way mapping and filtering are.** `reversed()` looks lazy, but it needs random access and a known length. It's a backwards *cursor*, not a pipeline stage. That's why it refuses generators outright: you can't know the last element of a stream until the stream ends. If you want to reverse a stream, what you usually want is `deque(maxlen=n)` to hold just the tail.

Finally, watch for reversals that shouldn't be there at all. **`sorted(xs)[::-1]` should be `sorted(xs, reverse=True)`**, and a "reverse chronological" list is usually better built by appending to a stack than by flipping a list afterwards. Reverse is cheap, but reversing to undo an ordering you chose yourself means the ordering was built backwards.
