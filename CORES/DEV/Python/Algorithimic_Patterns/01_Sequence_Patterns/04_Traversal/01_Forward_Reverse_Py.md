# Pattern 12 — Forward & Reverse Traversal

## Mental Model

Visit every element in a sequence **from beginning to end** or **from end to beginning**.

Traversal decides **the order you process elements in**, not what you do to them.

Forward traversal is `for x in xs`, reverse is `for x in reversed(xs)`. The one thing really worth learning here is the difference between `reversed(xs)` and `xs[::-1]`: a view versus a copy.

---

## Relationship to Cognitive Verb

```text
Traversal
      ↓
Forward & Reverse
```

Forward and Reverse are the two fundamental **Traversal** patterns.

---

## Python Functions & Common Idioms

|Variation|Example|Common Python|
|---|---|---|
|Forward Traversal|`1 2 3 4`|`for x in xs`, `map`, comprehension|
|Reverse Traversal|`4 3 2 1`|`reversed(xs)` (lazy), `xs[::-1]` (copy)|
|Reverse Then Process|reverse first|`[f(x) for x in reversed(xs)]`|
|Reverse Reduce (foldr)|right-to-left|`reduce(f, reversed(xs))`|
|Indexed Traversal|`(0,1) (1,2)`|`enumerate(xs)`|
|Reverse Indexed|`(4,5) (3,4)`|`reversed(list(enumerate(xs)))`|
|Side-effect Traversal|print, write, log|plain `for` loop|
|Lazy Traversal|process on demand|generators, `map`, `islice`|
|In-place Reverse|mutate the list|`xs.reverse()`|

> **Note:** Most Python sequence tools traverse **forward** by default. `reversed()` needs a sequence that knows its own length (`__len__` + `__getitem__`) or defines `__reversed__` — it does **not** work on a plain generator.

---

## Common Uses

- Sequence processing

- File processing

- Tree traversals

- Rendering pipelines

- Parsing

- Undo operations

- Stack processing

- Right-to-left algorithms

---

## Hidden Interview Problems

- Traverse linked lists

- Reverse print a list

- Palindrome checking

- Reverse iteration

- Right-to-left accumulation

- Expression evaluation

---

## Recognition Clues

If you hear:

- Visit every element

- Iterate

- Walk the sequence

- Scan left to right

- Scan right to left

- Reverse iteration

- Process in order

Think:

**→ Traversal**

---

## Pattern Summary

|Property|Value|
|---|---|
|Cognitive Verb|Traversal|
|Pattern|Forward & Reverse|
|Direction|Front → Back / Back → Front|
|Visits Every Element|Yes|
|Preserves Relative Order|Yes (within traversal direction)|
|Primary Use|Sequential processing|
|Memory|`reversed` O(1), `[::-1]` O(n)|

---

## Python Recipe Book

```python
# ============================================
# Input

from functools import reduce
from itertools import islice, count
import operator

xs = [1, 2, 3, 4, 5]

# ============================================
# Forward traversal

[x + 1 for x in xs]                     # => [2, 3, 4, 5, 6]
list(map(lambda x: x + 1, xs))          # => [2, 3, 4, 5, 6]

for x in xs:
    ...                                 # the plain loop is also traversal

# ============================================
# Reverse traversal

list(reversed(xs))                      # => [5, 4, 3, 2, 1]
xs[::-1]                                # => [5, 4, 3, 2, 1]

# THE DIFFERENCE:
#   reversed(xs) → a lazy ITERATOR, O(1) memory, walks backwards
#   xs[::-1]     → a new LIST,      O(n) memory, a full copy
#
# In a for loop, always prefer reversed(). Use [::-1] when you need
# a real list back (or when reversing a string, where reversed()
# gives you an iterator of characters instead of a string).

"hello"[::-1]                           # => 'olleh'
"".join(reversed("hello"))              # => 'olleh'   same, more typing

# ============================================
# reversed() needs a SIZED sequence

list(reversed(range(5)))                # => [4, 3, 2, 1, 0]   range knows its len
list(reversed((1, 2, 3)))               # => [3, 2, 1]

gen = (x for x in xs)
# list(reversed(gen))                   # TypeError: argument to reversed()
                                        # must be a sequence
list(reversed(list(gen)))               # => [5, 4, 3, 2, 1]   materialize first

# You cannot walk a stream backwards. That is a property of streams,
# not a limitation of Python.

# ============================================
# In-place reverse — mutates, returns None

ys = [1, 2, 3]
ys.reverse()
ys                                      # => [3, 2, 1]

# ys = ys.reverse()  ← the classic bug: ys becomes None

# ============================================
# Reverse then process

[x + 1 for x in reversed(xs)]           # => [6, 5, 4, 3, 2]

# ============================================
# Indexed traversal

list(enumerate(xs))
# => [(0, 1), (1, 2), (2, 3), (3, 4), (4, 5)]

[{"index": i, "value": x} for i, x in enumerate(xs)]
# => [{'index': 0, 'value': 1}, {'index': 1, 'value': 2}, ...]

# ============================================
# Reverse traversal WITH the original indices

list(reversed(list(enumerate(xs))))
# => [(4, 5), (3, 4), (2, 3), (1, 2), (0, 1)]

# or count down explicitly
[(i, xs[i]) for i in range(len(xs) - 1, -1, -1)]
# => [(4, 5), (3, 4), (2, 3), (1, 2), (0, 1)]

# range(len(xs)-1, -1, -1) — the stop is -1 because it's EXCLUSIVE,
# so index 0 is still visited. Getting this wrong drops the first element.

# careful: enumerate(reversed(xs)) renumbers from 0, it does NOT
# give you the original positions
list(enumerate(reversed(xs)))
# => [(0, 5), (1, 4), (2, 3), (3, 2), (4, 1)]     indices are NEW

# ============================================
# Side-effect traversal

for x in xs:
    print(x)
# 1 2 3 4 5  (one per line)

# ============================================
# Forward reduce (foldl)

reduce(operator.add, xs)                # => 15
sum(xs)                                 # => 15   use the builtin

reduce(operator.sub, xs)                # => -13    ((((1-2)-3)-4)-5)

# ============================================
# Reverse reduce

reduce(operator.sub, reversed(xs))      # => -5     ((((5-4)-3)-2)-1)

# For non-commutative operations, direction changes the answer.
# For + and max it doesn't — which is why the bug hides so well.

# ============================================
# ...but reversing the input is NOT a foldr

# reduce is always foldl: it applies f(accumulator, element).
# Reversing the source only changes the ORDER OF ARRIVAL, not the
# associativity. A true foldr nests the other way:
#     foldr(-, [1,2,3,4,5]) = 1 - (2 - (3 - (4 - 5)))

reduce(lambda acc, x: x - acc, reversed(xs), 0)   # => 3

# note the flipped parameters: `x - acc`, not `acc - x`. That flip,
# plus the reversed input, is what turns foldl into foldr.

reduce(operator.sub, reversed(xs))                # => -5   foldl backwards
reduce(lambda acc, x: x - acc, reversed(xs), 0)   # => 3    genuine foldr

# ============================================
# Palindrome — the honest use of reverse

def is_pal(s):
    return s == s[::-1]

is_pal("racecar")                       # => True

# without the copy — two pointers walking toward each other
def is_pal_2p(s):
    lo, hi = 0, len(s) - 1
    while lo < hi:
        if s[lo] != s[hi]:
            return False
        lo, hi = lo + 1, hi - 1
    return True

is_pal_2p("racecar")                    # => True

# same answer, O(1) extra space, and it exits early on a mismatch

# ============================================
# Reverse traversal is how you process a stack

stack = [1, 2, 3]
while stack:
    stack.pop()                         # 3, then 2, then 1

# ============================================
# Why reverse traversal matters: mutating while iterating

nums = [1, 2, 3, 4, 5, 6]
for i in range(len(nums) - 1, -1, -1):  # BACKWARDS
    if nums[i] % 2 == 0:
        del nums[i]                     # safe — later indices already visited
nums                                    # => [1, 3, 5]

# Forward deletion skips elements, because the list shifts under you.
# Going backwards is the standard fix (a comprehension is still nicer).

# ============================================
# Lazy traversal — never materializes the source

list(islice((x * x for x in count()), 3))       # => [0, 1, 4]

# the generator is infinite; islice stops it. Nothing is built in memory.

# ============================================
# Compare

for x in xs: ...                        # forward, lazy
for x in reversed(xs): ...              # reverse, lazy, O(1) memory
for x in xs[::-1]: ...                  # reverse, but copies the whole list
for i, x in enumerate(xs): ...          # forward with positions
for i in range(len(xs)-1, -1, -1): ...  # reverse with ORIGINAL positions
```

---

### Memory Hooks

|You want|You reach for|
|---|---|
|forward|`for x in xs`|
|backward|`for x in reversed(xs)`|
|backward, as a list|`xs[::-1]`|
|backward, a string|`s[::-1]`|
|backward, in place|`xs.reverse()`|
|positions too|`enumerate(xs)`|
|backward with real positions|`reversed(list(enumerate(xs)))`|
|right-to-left fold|`reduce(f, reversed(xs))`|
|delete while looping|iterate backwards|

---

### Key Insight

**Direction is a separate decision from the operation.** `map`, `filter`, `reduce` and comprehensions all go forward. You change direction by reversing the *source*, not by hunting for a different function. That's why Python never needed an `rmap` or `rfilter`: `reversed()` composes with everything.

Two facts to hang onto. **`reversed()` is free, `[::-1]` copies**, so the first is the one you want inside a loop. And **`reversed()` needs a real sequence**, because a stream has no reachable end. A generator has to be materialised before you can walk it backwards, which is precisely the cost you were avoiding by using a generator in the first place.

There's one case where going backwards isn't a style choice but a correctness requirement: **deleting from a list while you iterate it.** Go forward and the indices shift under your feet. Go backward and every index you still care about stays put.
