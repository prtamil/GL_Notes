# Pattern 10 — Suffix

## Mental Model

Take the **ending portion** of a sequence.

Python hands you something Clojure doesn't have here: **negative indices**. `xs[-3:]` is the last three, with no arithmetic and no length to look up.

There's a catch, though. Negative indices need a **known length**. On a stream you have to reach for `deque(maxlen=n)` instead.

---

## Relationship to Cognitive Verb

```text
Slice
   ↓
Suffix
```

Suffix is a **Slice** pattern that takes elements **from the end** of a sequence.

---

## Python Functions & Common Idioms

|Variation|Example|Common Python|
|---|---|---|
|Last N Elements|`4 5 6`|`xs[-n:]`|
|Last Element|`6`|`xs[-1]`|
|Last N of a Stream|tail a log|`collections.deque(it, maxlen=n)`|
|Drop First N (Keep Suffix)|`4 5 6`|`xs[n:]`, `islice(it, n, None)`|
|All Suffixes|`[1,2,3] [2,3] [3]`|`[xs[i:] for i in range(len(xs))]`|
|Suffix After Predicate|remaining elements|`itertools.dropwhile(pred, xs)`|
|Remove Last Element|`1 2 3 4 5`|`xs[:-1]`|
|Test For a Suffix|"ends with"|`str.endswith`, `xs[-n:] == s`|
|Split Prefix / Suffix|`([1,2,3], [4,5,6])`|`xs[:n], xs[n:]`|

> **Note:** Unlike Clojure, Python needs no special function for "last N" — `xs[-n:]` covers it. The catch is that slicing requires a **sized, indexable** sequence; for iterators, `deque(it, maxlen=n)` is the equivalent and runs in O(1) memory.

---

## Common Uses

- Last N records

- Recent history

- Tail of a stream

- File extensions

- String suffixes

- Remaining elements after a point

- Incremental parsing

- Resume processing

---

## Hidden Interview Problems

- Return last K elements

- Check string ends with suffix

- Tail a log file

- Keep recent history

- Remove leading elements

- Resume processing from a position

---

## Recognition Clues

If you hear:

- Last N

- End of sequence

- Ends with

- Tail

- Recent

- Remaining

- Trailing elements

- Suffix

Think:

**→ Suffix**

---

## Pattern Summary

|Property|Value|
|---|---|
|Cognitive Verb|Slice|
|Pattern|Suffix|
|Direction|Back|
|Size|Fixed or Predicate-based|
|Preserves Order|Yes|
|Includes Entire Sequence|Possible|
|Needs Length|Yes for slicing, No for `deque(maxlen=n)`|

---

## Python Recipe Book

```python
# ============================================
# Setup

from collections import deque
from itertools import islice, dropwhile

xs = [1, 2, 3, 4, 5, 6]

# ============================================
# Last element

xs[-1]                          # => 6      IndexError if empty
xs[-1] if xs else None          # => 6      safe form

# ============================================
# Last N elements

xs[-3:]                         # => [4, 5, 6]
xs[-100:]                       # => [1,2,3,4,5,6]   clamps, never raises

# THE TRAP — n = 0 does not mean "nothing"
n = 0
xs[-n:]                         # => [1,2,3,4,5,6]   because xs[0:] is everything!
xs[len(xs) - n:]                # => []              the correct form

# If n can be 0, don't use the negative-index form.

# ============================================
# Last N of a STREAM — deque with maxlen, O(n) time, O(k) memory

deque(iter(xs), maxlen=3)                       # => deque([4, 5, 6], maxlen=3)
list(deque(iter(xs), maxlen=3))                 # => [4, 5, 6]

# This is how you tail a 10GB file without loading it:
# with open("app.log") as f:
#     last_100 = list(deque(f, maxlen=100))
#
# The deque keeps only 100 lines in memory no matter how big the file is.

# ============================================
# Keep the suffix by dropping the prefix

xs[3:]                                          # => [4, 5, 6]
list(islice(iter(xs), 3, None))                 # => [4, 5, 6]   lazy

# ============================================
# Suffix while a predicate held at the front — dropwhile

list(dropwhile(lambda x: x < 4, xs))            # => [4, 5, 6]

# dropwhile stops testing after the FIRST failure — it does not filter
list(dropwhile(lambda x: x < 4, [1, 2, 9, 1, 2]))
# => [9, 1, 2]      the trailing 1, 2 survive; dropwhile stopped caring

# dropwhile is the exact complement of takewhile:
#   takewhile + dropwhile = the original sequence

# ============================================
# All suffixes

[xs[i:] for i in range(len(xs))]
# => [[1,2,3,4,5,6], [2,3,4,5,6], [3,4,5,6], [4,5,6], [5,6], [6]]

# lazily, without copying (views over the same list)
def suffixes(xs):
    for i in range(len(xs)):
        yield xs[i:]

# ============================================
# Nth suffix

xs[2:]                                          # => [3, 4, 5, 6]

# ============================================
# Remove the last element

xs[:-1]                                         # => [1, 2, 3, 4, 5]
xs[:-2]                                         # => [1, 2, 3, 4]

# ============================================
# Split into prefix and suffix

head, tail = xs[:3], xs[3:]
# head => [1, 2, 3]     tail => [4, 5, 6]

# a one-liner splitter
def split_at(xs, n):
    return xs[:n], xs[n:]

split_at(xs, 3)                                 # => ([1,2,3], [4,5,6])

# for iterators, tee + islice (you can't slice a generator twice)
from itertools import tee
def split_at_lazy(it, n):
    a, b = tee(it)
    return islice(a, n), islice(b, n, None)

p, s = split_at_lazy(iter(xs), 3)
list(p), list(s)                                # => ([1,2,3], [4,5,6])

# ============================================
# Does it end with a suffix?

"report.tar.gz".endswith(".gz")                 # => True
"a.py".endswith((".py", ".pyi"))                # => True   tuple = any of

xs[-2:] == [5, 6]                               # => True

# ============================================
# File extensions — use the library, not string surgery

import os
os.path.splitext("archive.tar.gz")              # => ('archive.tar', '.gz')

from pathlib import Path
Path("archive.tar.gz").suffix                   # => '.gz'
Path("archive.tar.gz").suffixes                 # => ['.tar', '.gz']
Path("archive.tar.gz").stem                     # => 'archive.tar'

# ============================================
# Recent history — a bounded window that forgets

history = deque(maxlen=3)
for x in xs:
    history.append(x)                           # oldest falls off the left
list(history)                                   # => [4, 5, 6]

# this is a suffix that maintains ITSELF as data arrives

# ============================================
# Longest common suffix — reverse, solve as a prefix, reverse back

def lcs_suffix(strs):
    rev = [s[::-1] for s in strs]
    for i, group in enumerate(zip(*rev)):
        if len(set(group)) > 1:
            return rev[0][:i][::-1]
    return min(strs, key=len)

lcs_suffix(["testing", "running", "coding"])    # => 'ing'

# Every suffix problem is a prefix problem on the reversed sequence.

# ============================================
# Resume processing from a saved position

processed_upto = 4
for item in xs[processed_upto:]:
    ...                                         # 5, 6

# ============================================
# Compare

xs[:3]                          # first 3               → Prefix
xs[-3:]                         # last 3                → Suffix
xs[3:]                          # everything after 3    → Suffix (by drop)
xs[:-1]                         # all but the last      → Suffix (by trim)
list(deque(it, maxlen=3))       # last 3 of a stream    → Suffix (bounded)
```

---

### Memory Hooks

|You want|You reach for|
|---|---|
|last element|`xs[-1]`|
|last n|`xs[-n:]` (but not when `n` may be 0)|
|last n of a stream|`deque(it, maxlen=n)`|
|everything after n|`xs[n:]`|
|all but the last|`xs[:-1]`|
|drop the leading run|`dropwhile(pred, xs)`|
|"ends with"|`s.endswith(…)`|
|a file extension|`Path(p).suffix`|
|a self-trimming history|`deque(maxlen=n)`|

---

### Key Insight

**Negative indexing makes suffixes as cheap as prefixes, as long as the sequence has a size.** The moment your data is a file, a socket, or a generator, "the last N" stops being a slice and turns into `deque(maxlen=n)`. You can't know where the end is until you reach it, so you keep a rolling buffer of candidates and let everything else fall off the back.

That's the real asymmetry here. **You can take a prefix without reading the whole input. You can't take a suffix that way.** `islice(f, 100)` reads 100 lines. `deque(f, maxlen=100)` reads all ten million and keeps 100. The code looks the same and the cost isn't remotely the same, which is why `tail` is a harder program to write than `head`.

And when a suffix problem gets genuinely awkward, flip it. `s[::-1]` turns any suffix question into the prefix question you already know how to answer.
