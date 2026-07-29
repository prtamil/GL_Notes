# Pattern 11 — Head & Tail

## Mental Model

Split a sequence into its **first element (Head)** and **everything else (Tail)**. This is the fundamental decomposition pattern in functional programming.

Python writes it with **starred unpacking**: `head, *tail = xs`. That single line is `first` and `rest` at once — and it is the closest Python gets to Clojure's `[head & tail]` destructuring.

---

## Relationship to Cognitive Verb

```text
Slice
   ↓
Head & Tail
```

Head & Tail is the most basic **Slice** pattern. Many recursive algorithms begin by separating a sequence into its head and tail.

---

## Python Functions & Common Idioms

|Variation|Example|Common Python|
|---|---|---|
|Head|`1`|`xs[0]`, `next(it)`|
|Tail|`[2, 3, 4]`|`xs[1:]`|
|Head + Tail|`1, [2, 3, 4]`|`head, *tail = xs`|
|Head + Tail (lazy)|stream|`next(it)`, then `it` itself|
|Remove Head|`[2, 3, 4]`|`xs[1:]`, `xs.pop(0)` (mutates, O(n))|
|Safe Head|`None` if empty|`next(iter(xs), None)`|
|Safe Empty Check|truthiness|`if xs:` / `if not xs:`|
|Destructure Multiple Heads|`a, b, *rest`|starred unpacking|
|Head & Tail & Last|`a, *mid, z`|starred unpacking|
|Pattern-match on shape|`case [x, *rest]`|`match` / `case` (3.10+)|

> **Note:** Python has no `nil`-vs-empty distinction like Clojure's `next` vs `rest`. `xs[1:]` on a one-element list gives `[]`, never `None` — and `[]` is falsy, so `while xs:` is the natural loop guard.

---

## Common Uses

- Recursive algorithms

- Stream processing

- Parser implementation

- Tree traversal

- Functional list processing

- Pattern matching

- State machines

---

## Hidden Interview Problems

- Recursive sum

- Recursive reverse

- Linked list traversal

- Token parsing

- DFS / BFS traversal

- Expression evaluation

---

## Recognition Clues

If you hear:

- First element

- Remaining elements

- Consume one item

- Peel one element

- Recursive processing

- Process until empty

Think:

**→ Head & Tail**

---

## Pattern Summary

|Property|Value|
|---|---|
|Cognitive Verb|Slice|
|Pattern|Head & Tail|
|Direction|Front|
|Output|One element + Remaining sequence|
|Preserves Order|Yes|
|Primary Use|Recursive decomposition|
|Python Caveat|`head, *tail` **copies** the tail — O(n) per peel|

---

## Python Recipe Book

```python
# ============================================
# Setup

from collections import deque

xs = [1, 2, 3, 4, 5]

# ============================================
# Head

xs[0]                           # => 1

# ============================================
# Tail

xs[1:]                          # => [2, 3, 4, 5]
xs[1:] if xs else []            # safe on empty

# ============================================
# Head + Tail in one line — starred unpacking

head, *tail = xs
# head => 1        tail => [2, 3, 4, 5]

# tail is always a LIST, even when the source was a tuple or a string
h, *t = "abc"                   # h => 'a'   t => ['b', 'c']
h, *t = (1, 2, 3)               # h => 1     t => [2, 3]

# ============================================
# Empty and single-element behaviour

h, *t = [1]                     # h => 1     t => []
# h, *t = []                    # ValueError: not enough values to unpack

# so guard first
if xs:
    head, *tail = xs

# ============================================
# Safe head with a default

next(iter(xs), None)            # => 1
next(iter([]), None)            # => None
next(iter([]), "empty")         # => 'empty'

# or the plain conditional
head = xs[0] if xs else None

# ============================================
# Destructure multiple heads

a, b, *tail = xs
# a => 1   b => 2   tail => [3, 4, 5]

# head, middle, last — the star can sit anywhere (once)
first, *middle, last = xs
# first => 1   middle => [2, 3, 4]   last => 5

*init, last = xs
# init => [1, 2, 3, 4]   last => 5

# ============================================
# Skip multiple heads

xs[2:]                          # => [3, 4, 5]

# ============================================
# Recursive processing — the textbook shape

def rsum(xs):
    if not xs:                  # base case: empty is falsy
        return 0
    head, *tail = xs
    return head + rsum(tail)

rsum([1, 2, 3, 4, 5])           # => 15

def rreverse(xs):
    if not xs:
        return []
    head, *tail = xs
    return rreverse(tail) + [head]

rreverse([1, 2, 3])             # => [3, 2, 1]

# ============================================
# ...and why you rarely write it that way in Python

# 1. head, *tail COPIES the tail → O(n) per call → O(n²) overall
# 2. Python's recursion limit is ~1000 frames, and there is NO tail-call
#    optimization. rsum(list(range(2000))) raises RecursionError.

import sys
sys.getrecursionlimit()         # => 1000

# The idiomatic Python is a loop:
def isum(xs):
    total = 0
    for x in xs:                # the for loop IS head-and-tail, iterated
        total += x
    return total

# Head & Tail is a THINKING tool in Python, not usually a coding one.

# ============================================
# Iterative peeling that is actually O(n) — use an iterator

it = iter(xs)
head = next(it)                 # => 1
# `it` is now the tail — no copy, no length needed
list(it)                        # => [2, 3, 4, 5]

# this is the streaming version of head & tail, and it's free

# ============================================
# Peeling from the front repeatedly — use a deque, not a list

q = deque(xs)
while q:
    head = q.popleft()          # O(1)   —  xs.pop(0) on a list is O(n)
    ...

# list.pop(0) inside a loop is the classic accidental-O(n²) in Python.

# ============================================
# Structural pattern matching (3.10+) — the closest thing to real destructuring

def describe(xs):
    match xs:
        case []:              return "empty"
        case [x]:             return f"one: {x}"
        case [x, y]:          return f"two: {x}, {y}"
        case [head, *tail]:   return f"head {head}, {len(tail)} more"

[describe(v) for v in ([], [1], [1, 2], [1, 2, 3])]
# => ['empty', 'one: 1', 'two: 1, 2', 'head 1, 2 more']

# match/case handles the base cases and the decomposition in one construct —
# this is where head & tail reads best in modern Python.

# ============================================
# Token parsing — the real-world use

def parse(tokens):
    match tokens:
        case []:
            return None, []
        case ["(", *rest]:
            inner, rest = parse(rest)
            return inner, rest[1:] if rest[:1] == [")"] else rest
        case [tok, *rest]:
            return tok, rest

parse(["a", "b", "c"])          # => ('a', ['b', 'c'])

# ============================================
# DFS with an explicit stack — head & tail without recursion

def dfs(tree):
    stack, out = [tree], []
    while stack:
        node, *stack = stack        # head & tail, literally
        out.append(node["v"])
        stack = node.get("kids", []) + stack
    return out

t = {"v": 1, "kids": [{"v": 2, "kids": [{"v": 4}]}, {"v": 3}]}
dfs(t)                          # => [1, 2, 4, 3]

# ============================================
# Compare

xs[0], xs[1:]                   # head + tail          → this pattern
xs[:3]                          # first 3              → Prefix
xs[-1], xs[:-1]                 # last + everything    → Suffix (mirrored)
next(it)                        # head, tail is `it`   → streaming head & tail
```

---

### Memory Hooks

|You want|You reach for|
|---|---|
|head and tail|`head, *tail = xs`|
|head only, safely|`next(iter(xs), None)`|
|first two and the rest|`a, b, *rest = xs`|
|everything but the last|`*init, last = xs`|
|head and tail, no copy|`it = iter(xs); next(it)`|
|repeated front-peeling|`deque.popleft()`|
|base case + decomposition|`match` / `case`|
|"is it empty?"|`if not xs:`|

---

### Key Insight

**In Clojure, head & tail is how you traverse; in Python, it is how you *think* about traversing.** `head, *tail = xs` copies the tail every time, and there is no tail-call optimization to save the recursion — so the literal translation of a Clojure recursion is both O(n²) and depth-limited to about a thousand elements.

What survives the translation is the *decomposition*: "handle one element, then the same problem on a smaller input." Python spells that as a `for` loop, an iterator you keep calling `next` on, or a `while stack:` with an explicit stack. All three are head & tail — the peeling is just done by the language instead of by you.

The one place the literal form earns its keep is **`match`/`case`**, where `case [head, *tail]` sits alongside `case []` and `case [x]`. There, the pattern isn't a performance choice; it's the clearest way to say what the shapes of your input are.
