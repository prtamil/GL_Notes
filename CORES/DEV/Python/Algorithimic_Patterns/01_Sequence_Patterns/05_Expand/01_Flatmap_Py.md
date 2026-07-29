# Pattern 15 — FlatMap

## Mental Model

Transform each element into **zero, one, or many elements**, then **flatten** the results into a single sequence.

Unlike `map`, which returns one output per input, **FlatMap can change the size of the sequence**.

Python has no `flatMap` function. Instead it has **two spellings**, and you should know both:

- **`[y for x in xs for y in f(x)]`** — the comprehension; the everyday form.
- **`chain.from_iterable(map(f, xs))`** — the lazy form, for streams and pipelines.

---

## Relationship to Cognitive Verb

```text
Expand
   ↓
FlatMap
```

FlatMap is an **Expand** pattern because each input element can produce **multiple output elements**.

---

## Python Functions & Common Idioms

|Variation|Example|Common Python|
|---|---|---|
|Map then Flatten|`[1,2] → 1 -1 2 -2`|`[y for x in xs for y in f(x)]`|
|Map then Flatten (lazy)|streams|`chain.from_iterable(map(f, xs))`|
|Expand One-to-Many|`2 → 2 4 8`|comprehension with an inner iterable|
|Zero-or-Many Results|drop or expand|inner iterable may be empty|
|Flatten Only|`[[1,2],[3]] → 1 2 3`|`chain.from_iterable(xss)`|
|Nested Iteration|every outer × inner|`[… for a in A for b in B]`|
|Expand Strings|`"ab" → 'a','b'`|`chain.from_iterable(words)`|
|Filter + Expand|conditional expansion|comprehension with `if`|

> **Note:** The comprehension's clause order reads **exactly like nested `for` loops** — `for x in xs for y in f(x)` is outer-then-inner. It is the *expression* that moves to the front, not the loops that reverse.

---

## Common Uses

- Tokenization

- Parsing

- Tree expansion

- Exploding nested collections

- Expanding search states

- Processing nested JSON

- Generating neighboring nodes

- Event expansion

---

## Hidden Interview Problems

- Flatten nested lists

- Tokenize text

- Generate neighbors in a graph

- Expand ranges

- Parse CSV fields

- Generate search states

---

## Recognition Clues

If you hear:

- One-to-many

- Expand

- Explode

- Flatten after mapping

- Nested results

- Variable number of outputs

- Generate children

Think:

**→ FlatMap**

---

## Pattern Summary

|Property|Value|
|---|---|
|Cognitive Verb|Expand|
|Pattern|FlatMap|
|Input|One element|
|Output|Zero, one, or many elements|
|Changes Sequence Size|Yes|
|Automatically Flattens|One level only|
|Laziness|Comprehension is eager; `chain.from_iterable` is lazy|

---

## Python Recipe Book

```python
# ============================================
# Input

from itertools import chain, starmap

xs = [1, 2, 3]

# ============================================
# Map — one output per input, nesting preserved

[(x, x * 10) for x in xs]
# => [(1, 10), (2, 20), (3, 30)]

# ============================================
# FlatMap — the nesting dissolves

[y for x in xs for y in (x, x * 10)]
# => [1, 10, 2, 20, 3, 30]

# the lazy form
list(chain.from_iterable((x, x * 10) for x in xs))
# => [1, 10, 2, 20, 3, 30]

# ============================================
# Read the comprehension left to right

# [y            for x in xs      for y in f(x)]
#  ^expression   ^outer loop      ^inner loop
#
# identical to:
out = []
for x in xs:
    for y in (x, x * 10):
        out.append(y)

# ============================================
# Duplicate every element

[y for x in xs for y in [x] * 2]        # => [1, 1, 2, 2, 3, 3]

# ============================================
# Expand into a range

[y for x in [1, 3, 5] for y in range(x)]
# => [0,  0, 1, 2,  0, 1, 2, 3, 4]

list(chain.from_iterable(map(range, [1, 3, 5])))    # same, point-free

# ============================================
# Split strings into characters

list(chain.from_iterable(["ab", "cd", "ef"]))
# => ['a', 'b', 'c', 'd', 'e', 'f']

# strings are already iterable, so no f() is needed at all
[ch for word in ["ab", "cd"] for ch in word]        # => ['a','b','c','d']

# ============================================
# Remove AND expand together — zero-or-many

[y for x in xs for y in ([x, x * 10] if x % 2 == 0 else [])]
# => [2, 20]

# an empty inner iterable DELETES the element. That is what makes
# flatmap strictly more powerful than map: it can also filter.

# clearer with an explicit if-clause when you're only filtering
[x * 10 for x in xs if x % 2 == 0]                  # => [20]

# ============================================
# FlatMap with two independent sources = Cartesian product

[(x, y) for x in [1, 2] for y in ['a', 'b']]
# => [(1,'a'), (1,'b'), (2,'a'), (2,'b')]

# the inner loop doesn't have to depend on x — when it doesn't,
# flatmap IS the cartesian product (see pattern 8)

# ...and when it DOES depend on x, you get triangular iteration
[(i, j) for i in range(4) for j in range(i)]
# => [(1,0), (2,0), (2,1), (3,0), (3,1), (3,2)]

# ============================================
# Compare map vs flatmap

[list(range(x)) for x in [1, 3, 5]]
# => [[0], [0, 1, 2], [0, 1, 2, 3, 4]]              nested

[y for x in [1, 3, 5] for y in range(x)]
# => [0, 0, 1, 2, 0, 1, 2, 3, 4]                    flat

# ============================================
# Flatten nested collections (no transformation)

list(chain.from_iterable([[1, 2], [3, 4], [5]]))    # => [1, 2, 3, 4, 5]
[y for sub in [[1, 2], [3, 4], [5]] for y in sub]   # => [1, 2, 3, 4, 5]

# chain(*xss) also works but materializes the outer level first —
# chain.from_iterable is the lazy one. Prefer it.

# ============================================
# ONE LEVEL ONLY — the thing everyone forgets

list(chain.from_iterable([[1, [2, 3]], [4]]))       # => [1, [2, 3], 4]

# for arbitrary depth you need recursion:
def flatten(x):
    for item in x:
        if isinstance(item, (list, tuple)):
            yield from flatten(item)
        else:
            yield item

list(flatten([1, [2, [3, [4]]], 5]))                # => [1, 2, 3, 4, 5]

# note: strings are iterable, so a naive flatten recurses into "abc"
# forever. The isinstance check above deliberately excludes str.

# ============================================
# Tokenization — the archetypal real use

lines = ["hello world", "flat map"]
[w for line in lines for w in line.split()]
# => ['hello', 'world', 'flat', 'map']

# ============================================
# Exploding nested JSON

orders = [
    {"id": 1, "items": ["a", "b"]},
    {"id": 2, "items": []},
    {"id": 3, "items": ["c"]},
]
[(o["id"], item) for o in orders for item in o["items"]]
# => [(1, 'a'), (1, 'b'), (3, 'c')]

# order 2 disappears — zero items, zero rows. This is exactly a SQL
# LATERAL join / pandas explode().

# ============================================
# Generating graph neighbours

def neighbours(cell):
    r, c = cell
    return [(r+dr, c+dc) for dr, dc in ((-1,0), (1,0), (0,-1), (0,1))]

frontier = [(0, 0), (2, 2)]
list(chain.from_iterable(map(neighbours, frontier)))
# => [(-1,0), (1,0), (0,-1), (0,1), (1,2), (3,2), (2,1), (2,3)]

# one BFS expansion step IS a flatmap

# ============================================
# BFS — flatmap applied until nothing new appears

def bfs(start, expand, depth):
    frontier, seen = [start], {start}
    for _ in range(depth):
        nxt = [n for x in frontier for n in expand(x) if n not in seen]
        seen.update(nxt)
        frontier = nxt
    return sorted(seen)

len(bfs((0, 0), neighbours, 2))                     # => 13

# ============================================
# Expanding date/event ranges

events = [("meeting", 3), ("break", 1)]
[name for name, n in events for _ in range(n)]
# => ['meeting', 'meeting', 'meeting', 'break']

# ============================================
# Compare

[f(x) for x in xs]                       # 1 → 1        → Map
[x for x in xs if p(x)]                  # 1 → 0 or 1   → Filter
[y for x in xs for y in f(x)]            # 1 → 0..n     → FlatMap
list(chain.from_iterable(xss))           # flatten only → FlatMap with f = identity
```

---

### Memory Hooks

|You want|You reach for|
|---|---|
|one-to-many|`[y for x in xs for y in f(x)]`|
|one-to-many, lazily|`chain.from_iterable(map(f, xs))`|
|just flatten|`chain.from_iterable(xss)`|
|flatten all the way down|a recursive generator with `yield from`|
|drop some inputs|return `[]` from `f`|
|nested loops as data|the same comprehension|
|explode a JSON array|`[(row, item) for row in rows for item in row[k]]`|

---

### Key Insight

**FlatMap is `map` and `filter` in a single operation.** Return one element and it's a map; return none and it's a filter; return several and it's an expansion. That is why so many pipelines collapse into one comprehension — you don't need a separate filtering pass when the mapping function can simply return an empty list.

The thing that trips people: **it flattens exactly one level.** `chain.from_iterable` will not dig into `[1, [2, 3]]` — arbitrary depth needs recursion, and that recursion needs an `isinstance(..., str)` guard, because a string is an iterable of one-character strings and will recurse until the stack gives out.
