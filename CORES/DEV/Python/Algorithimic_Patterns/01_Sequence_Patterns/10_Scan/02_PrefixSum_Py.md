# Pattern 30 — Prefix Sum

## Mental Model

Precompute cumulative sums so that **any range sum can be answered in O(1)** instead of summing repeatedly.

Unlike **Running Sum**, whose goal is to observe cumulative progress, **Prefix Sum** is built as a **data structure for fast queries**.

The Python build is one line — `list(accumulate(xs, initial=0))` — and the leading zero is not decoration. It is what makes `P[j+1] - P[i]` work without a special case at index 0.

---

## Relationship to Cognitive Verb

```text
Scan
   ↓
Prefix Sum
```

Prefix Sum is a **Scan** pattern because it scans the sequence once, storing cumulative information for future use.

---

## Python Functions & Common Idioms

|Variation|Example|Common Python|
|---|---|---|
|Build Prefix Sum|`[0,1,3,6,10]`|`list(accumulate(xs, initial=0))`|
|Range Sum Query|sum of `i..j`|`P[j+1] - P[i]`|
|Prefix Product|running multiply|`accumulate(xs, mul, initial=1)`|
|Prefix XOR|range XOR|`accumulate(xs, xor, initial=0)`|
|Prefix Count|how many so far|`accumulate(p(x) for x in xs)`|
|Subarray Sum = K|count subarrays|prefix sums + a `Counter`|
|Difference Array|many range updates|update two cells, then `accumulate`|
|2D Prefix Sum|submatrix sums|inclusion–exclusion on a 2-D table|

> **Note:** With a leading `0`, the sum of `xs[i:j]` is exactly `P[j] - P[i]` — the same half-open convention as Python slicing. Build it that way and the off-by-one errors disappear.

---

## Common Uses

- Range sum queries

- Sliding window optimization

- Image integral tables

- Dynamic programming

- Financial reports

- Analytics dashboards

- Histogram preprocessing

- Competitive programming

---

## Hidden Interview Problems

- Range Sum Query

- Subarray Sum Equals K

- Count subarrays with a given property

- Continuous Subarray Sum

- Maximum Sum Rectangle (2-D prefix sum)

- Integral image

- Product of Array Except Self

---

## Recognition Clues

If you hear:

- Range sum

- Sum between indices

- Many sum queries

- Precompute

- Cumulative array

- O(1) range query

- Prefix table

Think:

**→ Prefix Sum**

---

## Pattern Summary

|Property|Value|
|---|---|
|Cognitive Verb|Scan|
|Pattern|Prefix Sum|
|Built Once|Yes|
|Build Time|O(n)|
|Query Time|O(1)|
|Extra Memory|O(n)|
|Array Length|`len(xs) + 1`|
|Requires|an invertible operation (+, ×, XOR)|
|Primary Use|Fast range queries|

---

## Python Recipe Book

```python
# ============================================
# Input

from itertools import accumulate
from operator import mul, xor
from collections import Counter

xs = [2, 4, 6, 8, 10]

# ============================================
# Build it — always with the leading zero

P = list(accumulate(xs, initial=0))     # => [0, 2, 6, 12, 20, 30]

# len(P) == len(xs) + 1. P[k] is the sum of the FIRST k elements,
# so P[0] == 0 (sum of nothing) and P[-1] == sum(xs).

list(accumulate(xs))                    # => [2, 6, 12, 20, 30]   no zero
# usable, but every query needs an `if i == 0` special case. Don't.

# ============================================
# Range sum in O(1) — half-open, exactly like a slice

def range_sum(P, i, j):
    """sum(xs[i:j]) — j exclusive, matching Python slicing."""
    return P[j] - P[i]

range_sum(P, 1, 4)                      # => 18      xs[1:4] = 4+6+8
sum(xs[1:4])                            # => 18      the slow check

range_sum(P, 0, len(xs))                # => 30      everything
range_sum(P, 2, 2)                      # => 0       empty range

# INCLUSIVE version, if the problem states i..j:
def range_sum_incl(P, i, j):
    return P[j + 1] - P[i]

range_sum_incl(P, 1, 3)                 # => 18

# pick ONE convention and write it in the docstring. Mixing the two
# is the source of nearly every prefix-sum bug.

# ============================================
# Why it pays — the cost model

# naive: q queries × O(n) each   = O(n·q)
# prefix: O(n) build + O(1) each = O(n + q)

queries = [(0, 3), (1, 4), (2, 5)]
[range_sum(P, i, j) for i, j in queries]            # => [12, 18, 24]

# one query? just use sum(xs[i:j]). The table only pays off when
# queries are repeated — and it costs O(n) memory to get there.

# ============================================
# Running sum vs prefix sum — same numbers, different purpose

list(accumulate(xs))                    # [2, 6, 12, 20, 30]   to LOOK at
list(accumulate(xs, initial=0))         # [0, 2, 6, 12, 20, 30] to QUERY

# Running Sum is an output. Prefix Sum is an index.

# ============================================
# Prefix product

PP = list(accumulate([2, 3, 4, 5], mul, initial=1))         # => [1, 2, 6, 24, 120]
PP[4] // PP[1]                          # => 60      product of xs[1:4] = 3*4*5

# division only works if no element is ZERO. That's why
# "Product of Array Except Self" is normally solved with a prefix
# pass and a suffix pass instead of dividing:
def product_except_self(a):
    n = len(a)
    pre = list(accumulate(a, mul, initial=1))       # products before i
    suf = list(accumulate(a[::-1], mul, initial=1))[::-1]    # after i
    return [pre[i] * suf[i + 1] for i in range(n)]

product_except_self([1, 2, 3, 4])       # => [24, 12, 8, 6]

# ============================================
# Prefix XOR — range XOR in O(1)

X = list(accumulate([1, 2, 3, 4], xor, initial=0))  # => [0, 1, 3, 0, 4]
X[4] ^ X[1]                             # => 5       XOR of xs[1:4] = 2^3^4

# XOR is its own inverse, so the "subtraction" is another XOR.
# The requirement for ANY prefix structure is exactly this: the
# operation must be invertible. max/min are NOT — that's why
# range-max needs a sparse table or segment tree, not a prefix array.

# ============================================
# Prefix COUNT — the most underused variant

flags = [1, 0, 1, 1, 0, 1, 0]
C = list(accumulate(flags, initial=0))  # => [0, 1, 1, 2, 3, 3, 4, 4]
C[6] - C[2]                             # => 2       how many 1s in [2:6]

# any predicate works:
text = "hello world"
V = list(accumulate((c in "aeiou" for c in text), initial=0))
V[5] - V[0]                             # => 2       vowels in text[0:5]

# "how many X between i and j" is a prefix sum over booleans

# ============================================
# Subarray Sum Equals K — the classic prefix trick

def subarray_sum(a, k):
    """Count subarrays summing to exactly k. O(n)."""
    seen = Counter({0: 1})              # empty prefix, seen once
    total = count = 0
    for x in a:
        total += x
        count += seen[total - k]        # how many earlier prefixes work
        seen[total] += 1
    return count

subarray_sum([1, 1, 1], 2)              # => 2
subarray_sum([3, 4, 7, 2, -3, 1, 4, 2], 7)          # => 4

# the insight: sum(a[i:j]) == k  ⟺  P[j] - P[i] == k  ⟺  P[i] == P[j] - k.
# so at each j, ask the Counter how many earlier prefixes equal P[j]-k.
# O(n²) pair scanning collapses to O(n) with a hash map.
# `Counter({0: 1})` seeds the empty prefix — forget it and every
# subarray starting at index 0 goes uncounted.

# ============================================
# Continuous Subarray Sum — same trick, modular

def has_subarray_multiple_of(a, k):
    seen = {0: -1}                      # remainder -> earliest index
    total = 0
    for i, x in enumerate(a):
        total = (total + x) % k
        if total in seen:
            if i - seen[total] > 1:     # length >= 2
                return True
        else:
            seen[total] = i
    return False

has_subarray_multiple_of([23, 2, 4, 6, 7], 6)       # => True

# equal remainders ⟹ the span between them is divisible by k

# ============================================
# Difference array — the DUAL: O(1) range UPDATE, O(n) read

def apply_updates(n, updates):
    """updates: (i, j, delta) adding delta to a[i:j]."""
    diff = [0] * (n + 1)
    for i, j, d in updates:
        diff[i] += d
        diff[j] -= d                    # two touches per range
    return list(accumulate(diff))[:n]

apply_updates(5, [(0, 3, 2), (1, 5, 3)])            # => [2, 5, 5, 3, 3]

# prefix sum: fast QUERIES on static data.
# difference array: fast UPDATES, then one accumulate to read.
# Need both fast? That's a Fenwick / segment tree.

# ============================================
# 2-D prefix sum (integral image)

def build2d(m):
    rows, cols = len(m), len(m[0])
    P = [[0] * (cols + 1) for _ in range(rows + 1)]
    for r in range(rows):
        for c in range(cols):
            P[r + 1][c + 1] = (m[r][c] + P[r][c + 1]
                               + P[r + 1][c] - P[r][c])
    return P

def rect_sum(P, r1, c1, r2, c2):
    """sum of m[r1:r2][c1:c2] — half-open, like slicing."""
    return P[r2][c2] - P[r1][c2] - P[r2][c1] + P[r1][c1]

m = [[1, 2, 3],
     [4, 5, 6],
     [7, 8, 9]]
P2 = build2d(m)
rect_sum(P2, 0, 0, 2, 2)                # => 12      the 1,2,4,5 block
rect_sum(P2, 1, 1, 3, 3)                # => 28      the 5,6,8,9 block

# inclusion–exclusion: whole - top - left + the corner counted twice.
# This is the integral image behind Haar cascades and box blurs —
# any rectangle, any size, in four array reads.

# ============================================
# The float caveat

P = list(accumulate([0.1] * 10, initial=0))
P[10] - P[7]                            # => 0.30000000000000027

# subtracting two large accumulated floats amplifies drift.
# For money, use integer cents or Decimal; the prefix trick is
# exact on integers and only approximate on floats.

# ============================================
# Compare

list(accumulate(xs))            # to display progress      → Running Sum
list(accumulate(xs, initial=0)) # to answer queries        → Prefix Sum
P[j] - P[i]                     # range sum, O(1)          → Prefix Sum
diff[i] += d; diff[j] -= d      # range update, O(1)       → Difference array
sum(xs[i:j])                    # one-off, O(n), no memory → Slice + Reduce
```

---

### Memory Hooks

|You want|You reach for|
|---|---|
|the prefix table|`list(accumulate(xs, initial=0))`|
|sum of `xs[i:j]`|`P[j] - P[i]`|
|sum of `xs[i..j]` inclusive|`P[j+1] - P[i]`|
|range product|`accumulate(xs, mul, initial=1)` + divide|
|range XOR|`accumulate(xs, xor, initial=0)` + `^`|
|count of matches in a range|prefix sum over booleans|
|subarrays summing to k|prefix sums + `Counter({0: 1})`|
|fast range updates instead|difference array + one `accumulate`|
|submatrix sums|2-D prefix + inclusion–exclusion|
|range max|**not** a prefix sum — sparse table|

---

### Key Insight

**The leading zero is the whole design.** `accumulate(xs, initial=0)` makes `P[k]` mean "the sum of the first k elements", so `P[j] - P[i]` is `sum(xs[i:j])` under the exact same half-open convention Python slicing already uses. Without it you need a branch at `i == 0`, and that branch is where prefix-sum code goes wrong.

**A prefix array trades memory for repetition, and it only works for invertible operations.** Addition, multiplication, and XOR all have an inverse, so a range answer is `combine(P[j], undo(P[i]))`. Max and min do not — you cannot "un-max" a value — which is precisely why range-maximum queries need a sparse table or segment tree instead. Recognizing that dividing line saves you from trying to force the wrong structure onto the problem.

The deeper move is **prefix sums plus a hash map**, which is what turns "Subarray Sum Equals K" from O(n²) into O(n). Once the range condition is rewritten as `P[j] - P[i] == k`, you're no longer looking for subarrays at all — you're looking for *pairs of prefix values*, and a `Counter` answers that in one pass. Nearly every hard subarray problem is that same rewrite: express the condition in terms of two prefix values, then let a dict find the pairs.
