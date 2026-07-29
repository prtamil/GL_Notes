- **Window:** chunk, sliding, jump, overlap, adjacent pair
- **Pair:** zip, interleave, Cartesian product
- **Slice:** prefix, suffix, head, tail
- **Traversal:** forward, reverse, stride, circular
- **Expand:** flatMap, repeat
- **Compress:** distinct, dedupe, run-length encoding
- **Group:** by key, by predicate, histogram
- **Order:** sort, reverse, rotate
- **Search:** first, all, nearest
- **Scan:** running sum, prefix sum
- **Generate:** range, iterate, cycle
- **Structure:** flatten, transpose, reshape

---

# The Python tool for each pattern

|Family|Pattern|Reach for|
|---|---|---|
|**Window**|chunk|`batched(xs, n)`|
||sliding|`[xs[i:i+n] for i in range(len(xs)-n+1)]`|
||jump / overlap|same, with a `step` in `range`|
||adjacent pair|`pairwise(xs)`|
|**Pair**|zip|`zip(a, b)` — stops at the shortest|
||interleave|`chain.from_iterable(zip(a, b))`|
||Cartesian product|`product(a, b)`|
|**Slice**|prefix / suffix|`xs[:n]` / `xs[-n:]`|
||head / tail|`first, *rest = xs`|
||lazy slice|`islice(it, a, b)`|
|**Traversal**|forward|`for x in xs`|
||reverse|`reversed(xs)` / `xs[::-1]`|
||stride|`xs[::k]`|
||circular|`xs[i % len(xs)]` / `cycle(xs)`|
|**Expand**|flatMap|`[y for x in xs for y in f(x)]`|
||repeat|`repeat(x, n)` / `xs * n`|
|**Compress**|distinct|`list(dict.fromkeys(xs))`|
||dedupe|`[k for k, _ in groupby(xs)]`|
||RLE|`[(k, len(list(g))) for k, g in groupby(xs)]`|
|**Group**|by key|`defaultdict(list)` + `d[f(x)].append(x)`|
||by predicate|`out[bool(p(x))].append(x)`|
||histogram|`Counter(xs)`|
|**Order**|sort|`sorted(xs, key=…)`|
||reverse|`xs[::-1]`|
||rotate|`xs[n:] + xs[:n]` / `deque.rotate`|
|**Search**|first|`next((x for x in xs if p(x)), None)`|
||all|`[x for x in xs if p(x)]`|
||nearest|`min(xs, key=lambda x: abs(x - t))`|
|**Scan**|running sum|`accumulate(xs)`|
||prefix sum|`accumulate(xs, initial=0)` then `P[j] - P[i]`|
|**Generate**|range|`range(a, b, s)` / `count()`|
||iterate|a generator: `while True: yield x; x = f(x)`|
||cycle|`cycle(xs)`|
|**Structure**|flatten|`chain.from_iterable(xs)`|
||transpose|`zip(*rows)`|
||reshape|`batched(flat, n)`|

---

# The four imports that cover almost everything

```python
from itertools import (accumulate, batched, chain, count, cycle,
                       groupby, islice, pairwise, product, repeat,
                       takewhile, dropwhile, zip_longest)
from collections import Counter, defaultdict, deque
from functools import reduce
from operator import itemgetter, attrgetter
import heapq, bisect
```

Three rules cut across all of it:

1. **The comprehension is the default** — it covers Transform, Select, Reject, and flatMap in one form, and it reads *for → if → expression*.
2. **`itertools` is lazy and one-shot** — nothing is computed until consumed, and consuming it twice gives you an empty second read with no error.
3. **The right structure removes the code** — `Counter` for histograms, `defaultdict(list)` for grouping, `deque(maxlen=n)` for rolling windows, `bisect` for sorted lookups, `heapq` for top-k.

---

# Next

```txt
Part 1
1D Sequence Patterns
        ↓
Part 2
Matrix Patterns
        ↓
Part 3
Tensor Patterns
        ↓
Part 4
Tree Traversal Patterns
        ↓
Part 5
Graph Traversal Patterns
```
