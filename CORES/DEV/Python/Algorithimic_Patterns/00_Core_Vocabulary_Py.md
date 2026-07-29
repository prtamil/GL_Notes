# Core Vocabulary — what the whole course actually uses

Measured, not guessed: every fenced Python block across parts 1–3 was extracted and counted.

```text
130 files   150 code blocks   6,935 lines of Python
P1 Sequences  2,154 loc     P2 Matrices  2,412 loc     P3 Tensors  2,369 loc
```

Counts below are occurrences in that corpus, split by part.

---

## The Top 20

Learn these and you can read essentially every code block in the course.

|#|Thing|Total|P1|P2|P3|What it is for|
|---|---|---|---|---|---|---|
|1|**`range(n)`**|501|122|328|51|Drive every index loop|
|2|**slicing `a[i:j]`**|492|170|142|180|Take a sub-range — the most portable idea in Python|
|3|**`list(...)`**|485|376|78|31|Force a lazy iterator to show itself|
|4|**`len(x)`**|447|115|289|43|Size, and the bound of every loop|
|5|**list comprehension** `[f(x) for x in xs]`|350|142|156|52|Transform + filter in one expression|
|6|**`for a, b in ...`**|274|115|140|19|Unpack while iterating — pairs, coords, items|
|7|**tuple assign** `a, b = ...`|190|57|109|24|Two values at once; `rows, cols = ...`|
|8|**step slice `a[::k]`**|176|59|90|27|Every k-th element|
|9|**`zip(a, b)`**|168|84|79|5|Walk two sequences in lockstep|
|10|**`sum(xs)`**|162|34|65|63|Total — and counting, via booleans|
|11|**`lambda`**|135|89|43|3|A function as an argument (`key=`, `f=`)|
|12|**call unpack `f(*xs)`**|128|44|67|17|Spread a sequence into arguments|
|13|**reverse `a[::-1]`**|124|33|82|9|Backwards, in one token|
|14|**`enumerate(xs)`**|120|35|81|4|Index *and* value|
|15|**`zip(*m)`** — transpose|99|35|64|0|Rows ↔ columns. The single best idiom in part 2|
|16|**`max` / `sorted` / `min`**|169|94|61|14|Extremes and ordering, with `key=`|
|17|**generator expression** `(f(x) for x in xs)`|67|34|27|6|A comprehension that stays lazy|
|18|**`next(gen, default)`**|58|50|7|1|First match, with a miss value — the search idiom|
|19|**bool-as-int** `sum(x > 0)`|82|7|6|69|Count without a loop; `True == 1`|
|20|**`itertools` + `collections`**|501|455|43|3|`accumulate` `islice` `groupby` `cycle` `pairwise` · `Counter` `deque` `defaultdict`|

---

## The same 20, grouped by idea

Easier to memorise in clusters than as a flat list.

### 1. Get a piece of something — *slicing*
```python
a[i:j]        a[::k]        a[::-1]        a[-1]
m[r][c]       [row[c] for row in m]        row[c:c+k]
```
`492 + 176 + 124` uses. Slicing is the highest-value syntax in the language: it does *take*, *skip*, *reverse* and *crop* with no function call. Parts 2 and 3 are built almost entirely on it.

### 2. Build a new sequence — *comprehensions*
```python
[f(x)      for x in xs]              # transform          350
[x         for x in xs if p(x)]      # filter              51
[f(r,c)    for r in R for c in C]    # nested / flatten    55
(f(x)      for x in xs)              # lazy version        67
{k: v      for k, v in pairs}        # dict                14
```
One form, four jobs. Read it **left to right**: `for` → `if` → expression.

### 3. Walk more than one thing — *zip / enumerate / unpacking*
```python
for i, x    in enumerate(xs)         # 120
for a, b    in zip(xs, ys)           # 168
for a, b    in pairwise(xs)          #  28
rows, cols  = len(m), len(m[0])      # 190
zip(*m)                              #  99   ← transpose
f(*args)                             # 128
```
`zip(*m)` deserves separate memorising. It is transpose, it is unzip, and it makes every column operation a row operation.

### 4. Reduce to one value — *the aggregate family*
```python
sum(xs)   max(xs)   min(xs)   len(xs)   any(xs)   all(xs)   sorted(xs)
max(m, key=sum)                      # key= is what makes them general
sum(x > 0 for x in xs)               # count, because True == 1
```
The `key=` parameter turns four functions into forty.

### 5. Find something — *lazy search*
```python
next((x for x in xs if p(x)), None)  #  58   first match, or None
[x for x in xs if p(x)]              #        all matches
```
The `None` default is the whole idiom — a miss becomes a value, not an exception.

### 6. The two imports that carry part 1
```python
from itertools   import accumulate, islice, groupby, cycle, pairwise, product, chain
from collections import Counter, defaultdict, deque
```
| | uses | for |
|---|---|---|
|`accumulate`|72|running totals, prefix sums|
|`islice`|71|slice a lazy iterator|
|`Counter`|48|histograms in one call|
|`groupby`|40|runs and run-length encoding|
|`cycle`|40|repeat forever|
|`deque`|33|BFS queues, rolling windows|
|`pairwise`|28|adjacent pairs|
|`product`|24|nested loops, flattened|
|`batched`|22|fixed-size chunks (3.12+)|

**501 uses in total — but 455 of them are in part 1.** These two modules essentially *are* part 1's vocabulary, and they almost vanish by part 3, where NumPy does the same jobs on arrays.

---

## Part 3 adds a second vocabulary (NumPy)

Parts 1–2 are pure stdlib. Part 3 replaces most of the above with array operations — the concepts do not carry over one-for-one, so learn it as a separate layer.

|NumPy|uses|Replaces|
|---|---|---|
|`np.arange(n).reshape(...)`|201|`range` + nested lists — the standard test tensor|
|`.sum(axis=k)` / `.mean(axis=k)`|213|every accumulation loop|
|`.reshape(...)`|87|regrouping without moving data|
|`.ravel()` / `.transpose()` / `.swapaxes()`|126|flatten and `zip(*m)`|
|`np.einsum('ij,jk->ik', …)`|71|any contraction, named|
|`np.zeros` / `ones` / `full` / `eye`|106|list-of-list construction|
|`np.stack` / `concatenate` / `split`|97|`+` and slicing on lists|
|`np.moveaxis`|41|"bring this axis to the front"|

**The one parameter to internalise:** `axis=` appears **429 times** — every reduction, stack, split, concatenate and argmax takes it. Together with `keepdims=True` (70 uses) it is most of what part 3 teaches.

---

## Honest notes on the numbers

- **`list()` at 485 is inflated.** Much of it is `list(...)` wrapped around lazy `itertools` results just to *display* them. That is itself the lesson — `itertools` is lazy and one-shot — but you will write it less in real code.
- **`range` is 328× in part 2** because grid loops are `for r in range(rows)`. In part 3 it drops to 51 — replaced by `axis=`.
- **"keyword argument" was the raw #1 at 693**, but 429 of those are NumPy's `axis=`. It is listed under part 3 rather than as a general concept, which is more honest.
- **`np.array_equal` / `shares_memory` / `allclose`** appear often in part 3 but are *verification* calls used to prove claims in the text — not idioms to memorise.
- Counts come from fenced ```python blocks only. Part 1's `00_Verbs/` folder (21 files) is reference tables with no fenced code; its vocabulary is counted separately and matches the list above.

---

## If you only memorise five things

```python
a[i:j]  a[::-1]  a[::k]              # 1. slicing
[f(x) for x in xs if p(x)]           # 2. comprehension
for i, x in enumerate(xs)            # 3. index and value
zip(a, b)      and      zip(*m)      # 4. lockstep, and transpose
next((x for x in xs if p(x)), None)  # 5. first match or None
```

Those five appear in **over 1,600** of the ~6,900 lines of code in this course.
