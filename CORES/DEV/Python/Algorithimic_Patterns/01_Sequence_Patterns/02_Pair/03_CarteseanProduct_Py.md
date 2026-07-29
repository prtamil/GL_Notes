# Pattern 8 — Cartesian Product

## Mental Model

Generate **every possible combination** by pairing each element of one sequence with **every** element of another sequence.

Python spells this two ways that mean the same thing: **`itertools.product`** (the noun) and a **nested comprehension** (the verb). Use `product` when the sources are data, the comprehension when you also want to filter or transform.

---

## Relationship to Cognitive Verb

```text
Pair
   ↓
Cartesian Product
```

Cartesian Product is a **Pair** pattern that creates **all possible pairs**, not just corresponding or alternating ones.

---

## Python Functions & Common Idioms

|Variation|Example|Common Python|
|---|---|---|
|Cartesian Product (2 sequences)|`(1,'a') (1,'b') (2,'a')`|`product(xs, ys)`|
|Cartesian Product (3 sequences)|`(1,'a','x') …`|`product(xs, ys, zs)`|
|Pair then Transform|`(x, y) → f(x, y)`|`[f(x, y) for x in xs for y in ys]`|
|Cartesian with Filter|valid combinations only|`[… for x in xs for y in ys if cond]`|
|Self-product (n²)|every item × every item|`product(xs, repeat=2)`|
|Unordered pairs (i < j)|`(0,1) (0,2) (1,2)`|`itertools.combinations(xs, 2)`|
|Ordered pairs, no self-pair|`(0,1) (1,0)`|`itertools.permutations(xs, 2)`|
|Fixed-length strings|`'aa' 'ab' 'ba' 'bb'`|`product(alphabet, repeat=n)`|
|Grid coordinates|`(r, c)`|`product(range(rows), range(cols))`|

---

## Common Uses

- Grid generation

- Chess board coordinates

- Game state generation

- Test case generation

- Password combinations

- Hyperparameter search

- SQL CROSS JOIN

- All pair comparisons

- Ray/object intersection tests

---

## Hidden Interview Problems

- Generate all pairs

- Generate all combinations of two arrays

- Sudoku coordinate generation

- Matrix coordinate traversal

- Compare every item with every other item

- Brute-force search

- CROSS JOIN implementation

---

## Recognition Clues

If you hear:

- Every possible combination

- All pairs

- Every X with every Y

- Cross join

- Nested loops

- Exhaustive search

- Grid coordinates

- Combinations of two lists

Think:

**→ Cartesian Product**

---

## Pattern Summary

|Property|Value|
|---|---|
|Cognitive Verb|Pair|
|Pattern|Cartesian Product|
|Input|Two or more sequences|
|Output|Every possible combination|
|Pairing Rule|Every element with every other|
|Complexity|O(n × m) — multiplicative, not additive|
|Preserves Order|Yes (rightmost argument varies fastest)|
|Laziness|`product` is lazy, but materializes its inputs first|

---

## Python Recipe Book

```python
# ============================================
# Setup

from itertools import product, combinations, permutations, combinations_with_replacement

# ============================================
# 1. Cartesian product of two sequences

list(product([1, 2, 3], ['a', 'b']))
# => [(1, 'a'), (1, 'b'),
#     (2, 'a'), (2, 'b'),
#     (3, 'a'), (3, 'b')]

# comprehension form — identical order
[(x, y) for x in [1, 2, 3] for y in ['a', 'b']]

# The RIGHTMOST source varies fastest, exactly like nested for loops
# where the last loop is the innermost.

# ============================================
# 2. Cartesian product of three sequences

list(product([1, 2], ['a', 'b'], ['x', 'y']))
# => [(1,'a','x'), (1,'a','y'), (1,'b','x'), (1,'b','y'),
#     (2,'a','x'), (2,'a','y'), (2,'b','x'), (2,'b','y')]

# ============================================
# 3. Transform while pairing

[x + y for x in [1, 2, 3] for y in [10, 20]]
# => [11, 21, 12, 22, 13, 23]

# with product, you unpack in the comprehension target
[x + y for x, y in product([1, 2, 3], [10, 20])]
# => [11, 21, 12, 22, 13, 23]

# ============================================
# 4. Cartesian product with filtering

[(x, y) for x in range(5) for y in range(5) if x < y]
# => [(0,1), (0,2), (0,3), (0,4),
#     (1,2), (1,3), (1,4),
#     (2,3), (2,4),
#     (3,4)]

# but if the filter is "i < j", combinations says it directly and is faster:
list(combinations(range(5), 2))          # same 10 pairs, no rejected work

# ============================================
# 5. Matrix coordinates

list(product(range(3), range(4)))
# => [(0,0),(0,1),(0,2),(0,3),
#     (1,0),(1,1),(1,2),(1,3),
#     (2,0),(2,1),(2,2),(2,3)]

# iterate a grid without nesting two loops
grid = [[1, 2], [3, 4]]
[grid[r][c] for r, c in product(range(2), range(2))]     # => [1, 2, 3, 4]

# ============================================
# 6. Chess board coordinates

list(product("abc", range(1, 4)))
# => [('a',1),('a',2),('a',3),
#     ('b',1),('b',2),('b',3),
#     ('c',1),('c',2),('c',3)]

[f"{f}{r}" for f, r in product("abcdefgh", range(1, 9))][:4]
# => ['a1', 'a2', 'a3', 'a4']

# ============================================
# Self-product — every item with every item, including itself

list(product([1, 2], repeat=2))
# => [(1,1), (1,2), (2,1), (2,2)]      n² pairs

# ============================================
# The four "all pairs" variants — know which one you mean

xs = [1, 2, 3]
list(product(xs, repeat=2))                      # 9  — ordered, self allowed
list(permutations(xs, 2))                        # 6  — ordered, no self
list(combinations(xs, 2))                        # 3  — unordered, no self
list(combinations_with_replacement(xs, 2))       # 6  — unordered, self allowed

# "compare every item with every other" is usually combinations (3),
# not product (9) — you don't want (a,a) or both (a,b) and (b,a).

# ============================================
# All pair comparisons — the real use of combinations

points = [(0, 0), (3, 4), (6, 8)]
import math
[(p, q, math.dist(p, q)) for p, q in combinations(points, 2)]
# => [((0,0),(3,4),5.0), ((0,0),(6,8),10.0), ((3,4),(6,8),5.0)]

closest = min(combinations(points, 2), key=lambda pq: math.dist(*pq))
# => ((0, 0), (3, 4))

# ============================================
# Hyperparameter grid search

grid = {"lr": [0.1, 0.01], "depth": [3, 5], "seed": [0]}
configs = [dict(zip(grid, combo)) for combo in product(*grid.values())]
# => [{'lr':0.1,'depth':3,'seed':0}, {'lr':0.1,'depth':5,'seed':0},
#     {'lr':0.01,'depth':3,'seed':0}, {'lr':0.01,'depth':5,'seed':0}]

# product(*d.values()) + zip(d, combo) is the whole grid-search library

# ============================================
# Test case generation

for user, action, state in product(["admin", "guest"], ["read", "write"], ["on", "off"]):
    ...        # 2 × 2 × 2 = 8 cases, no nested loops

# ============================================
# Brute-force strings — where the cost becomes real

list(product("ab", repeat=2))            # => 4 tuples: aa ab ba bb
["".join(p) for p in product("ab", repeat=3)]
# => ['aaa','aab','aba','abb','baa','bab','bba','bbb']

len("abcdefghijklmnopqrstuvwxyz") ** 8    # => 208,827,064,576
# product is lazy, so this LOOPS forever rather than exploding memory.
# Laziness saves your RAM; it does not save your afternoon.

# ============================================
# SQL CROSS JOIN

users  = [{"id": 1}, {"id": 2}]
roles  = [{"r": "a"}, {"r": "b"}]
[u | r for u, r in product(users, roles)]        # dict merge, 3.9+
# => [{'id':1,'r':'a'}, {'id':1,'r':'b'}, {'id':2,'r':'a'}, {'id':2,'r':'b'}]

# an INNER JOIN is a filtered cross join
orders = [{"uid": 1, "n": 10}, {"uid": 2, "n": 20}]
[(u, o) for u, o in product(users, orders) if u["id"] == o["uid"]]
# => [({'id':1}, {'uid':1,'n':10}), ({'id':2}, {'uid':2,'n':20})]

# ============================================
# Careful: product() consumes its inputs eagerly

g = (x for x in range(3))
list(product(g, repeat=2))               # works — product buffers g internally
# => [(0,0),(0,1),(0,2),(1,0),(1,1),(1,2),(2,0),(2,1),(2,2)]
# but an INFINITE generator will hang here. product needs finite inputs.

# ============================================
# Compare

list(zip([1,2], "ab"))                   # => [(1,'a'), (2,'b')]           n pairs
list(product([1,2], "ab"))               # => [(1,'a'),(1,'b'),(2,'a'),(2,'b')]  n×m
list(combinations([1,2,3], 2))           # => [(1,2),(1,3),(2,3)]          n choose 2

# zip walks in lockstep. product nests. combinations picks a subset.
```

---

### Memory Hooks

|You want|You reach for|
|---|---|
|every X with every Y|`product(xs, ys)`|
|every X with every X|`product(xs, repeat=2)`|
|all unordered pairs|`combinations(xs, 2)`|
|all orderings of pairs|`permutations(xs, 2)`|
|grid coordinates|`product(range(r), range(c))`|
|a parameter grid|`product(*d.values())` + `zip(d, combo)`|
|all strings of length n|`product(alphabet, repeat=n)`|
|filtered combinations|comprehension with `if`|

---

### Key Insight

**Cartesian product is the only pattern here whose output grows multiplicatively.** Zip gives you `n` results, interleave gives you `n + m`, product gives you `n × m` — and with three or more sources that becomes the dominant cost of your program. Every "try all combinations" bug is this multiplication being underestimated.

The practical follow-through: **before reaching for `product`, ask whether you actually want `combinations`.** "Compare every pair of items" almost always means unordered pairs without self-comparison — `n(n-1)/2` results, not `n²`. Choosing the right one both halves the work and removes the `if x != y` guard you would otherwise have to remember to write.
