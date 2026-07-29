# 28. Identity Matrix

## Mental Model

Every lesson so far started with a matrix that already existed. This section **builds one from nothing**: dimensions plus a rule.

The rule is always a function of the coordinates:

```text
m[r][c] = f(r, c)
```

and in Python that's one comprehension, covering all three lessons in this section:

```python
[[f(r, c) for c in range(cols)] for r in range(rows)]
```

The identity matrix is the simplest interesting `f`: **ones on the diagonal, zeros everywhere else.**

```text
f(r, c) = int(r == c)

[[1, 0, 0, 0],
 [0, 1, 0, 0],
 [0, 0, 1, 0],
 [0, 0, 0, 1]]
```

Why it earns a lesson of its own is what it *does*, not what it looks like. `I` is the **multiplicative identity**: `A @ I == A` and `I @ A == A`, exactly as `x * 1 == x`. That makes it the starting value for matrix exponentiation, the base case of every "compose these transforms" fold, and the template that generalises to diagonal, permutation and exchange matrices — the last of which turn out to be lessons 20 and 21 written as multiplication.

And because this is the first lesson that *builds* a grid, it is where the single most damaging Python grid bug lives: **`[[0]*n]*n` gives you `n` references to the same row.**

---

## Relationship to Cognitive Verb

```text
Construct
    ↓
Identity Matrix
```

Related verbs:

- Construct
- Generate
- Fabricate
- Seed
- Initialise

---

## Python Functions & Common Idioms

|Variation|Example|Common Python|
|---|---|---|
|Identity|the whole thing|`[[int(r==c) for c in range(n)] for r in range(n)]`|
|Blank grid|zeros|`[[0]*cols for _ in range(rows)]`|
|**Never**|the aliasing bug|`[[0]*cols]*rows`|
|By mutation|set the diagonal|`for i in range(n): m[i][i] = 1`|
|Diagonal matrix|arbitrary values|`vals[r] if r == c else 0`|
|Read the diagonal|extract|`[m[i][i] for i in range(n)]`|
|Trace|sum of the diagonal|`sum(m[i][i] for i in range(n))`|
|Matrix multiply|needs columns|`zip(*B)` (lesson 16)|
|Permutation matrix|reorder rows|`int(p[r] == c)`|
|Exchange matrix|reverse rows|`[row[::-1] for row in eye(n)]`|
|Matrix power|`I` as the seed|binary exponentiation from `eye(n)`|

---

## Common Uses

- The starting value for matrix multiplication chains
- Matrix exponentiation (Fibonacci, linear recurrences, graph path counts)
- Neutral element in transform composition
- Testing that a transform pipeline is correct
- Building diagonal and scaling matrices
- Permutation matrices for reordering
- Initialising a transform stack in graphics
- Basis vectors in linear algebra

---

## Hidden Interview Problems

- Generate an n × n identity matrix
- Matrix multiplication
- Matrix exponentiation / nth Fibonacci in O(log n)
- Check if a matrix is the identity
- Check if a matrix is diagonal
- Compute the trace
- Build a permutation matrix
- Verify that two matrices are inverses

---

## Recognition Clues

If you hear...

- "identity matrix..."
- "the neutral element..."
- "raise this matrix to the nth power..."
- "diagonal matrix..."
- "leaves the matrix unchanged..."
- "start with no transformation applied..."

...think **Identity Matrix**.

---

## Pattern Summary

|Property|Value|
|---|---|
|Dimension|2D, always **square**|
|Rule|`f(r, c) = int(r == c)`|
|Shape|`n × n`|
|Trace|`n`|
|Symmetric|Yes — `I == transpose(I)`|
|Its own inverse|Yes — `I @ I == I`|
|Algebraic role|`A @ I == I @ A == A`|
|Time Complexity|O(n²) to build|
|Space Complexity|O(n²)|
|Common Domains|Linear algebra, graphics, DP, graph theory|

---

## Python Recipe Book

```python
# ============================================
# The one idiom to remember
#
#   f(r, c) = int(r == c)
#
# int(True) is 1 and int(False) is 0, so the predicate
# IS the value. No conditional needed.

def eye(n):
    return [[int(r == c) for c in range(n)] for r in range(n)]

eye(4)
# =>
# [[1, 0, 0, 0],
#  [0, 1, 0, 0],
#  [0, 0, 1, 0],
#  [0, 0, 0, 1]]

eye(1)                              # => [[1]]

# ============================================
# THE BUG THIS SECTION EXISTS TO WARN YOU ABOUT
#
# `*` on a list repeats the REFERENCE, not the contents.
# Every "row" is the same list object.

bad = [[0] * 3] * 3
bad[0][0] = 9
bad
# =>
# [[9, 0, 0],
#  [9, 0, 0],
#  [9, 0, 0]]      <-- all three rows changed

bad[0] is bad[1]                    # => True   ONE list, three names

# the fix is a comprehension, which evaluates the inner
# expression once per row:
good = [[0] * 3 for _ in range(3)]
good[0][0] = 9
good
# =>
# [[9, 0, 0],
#  [0, 0, 0],
#  [0, 0, 0]]

good[0] is good[1]                  # => False  three distinct lists
#
# `[0] * 3` for a row of IMMUTABLE ints is fine — it is
# the OUTER `* rows` that aliases. Every grid you build
# in the rest of this section uses the comprehension.

# ============================================
# By mutation, when you prefer it

def eye_mut(n):
    m = [[0] * n for _ in range(n)]
    for i in range(n):
        m[i][i] = 1
    return m

eye_mut(4) == eye(4)                # => True

# ============================================
# Diagonal matrices — the same shape, arbitrary values

def diag(vals):
    n = len(vals)
    return [[vals[r] if r == c else 0 for c in range(n)] for r in range(n)]

diag([2, 5, 7])
# =>
# [[2, 0, 0],
#  [0, 5, 0],
#  [0, 0, 7]]

diag([1] * 4) == eye(4)             # => True   identity is diag(1,1,...)

# reading a diagonal back out:
[diag([2, 5, 7])[i][i] for i in range(3)]           # => [2, 5, 7]

# the trace:
sum(eye(4)[i][i] for i in range(4))                 # => 4
sum(diag([2, 5, 7])[i][i] for i in range(3))        # => 14

# ============================================
# Why it is called the identity
#
# Matrix multiply needs B's COLUMNS, which is zip(*B)
# from lesson 16 — transpose earning its keep again.

def transpose(m):
    return [list(r) for r in zip(*m)]

def matmul(A, B):
    Bt = transpose(B)
    return [[sum(a * b for a, b in zip(row, col)) for col in Bt]
            for row in A]

A = [[1, 2, 3],
     [4, 5, 6],
     [7, 8, 9]]

matmul(A, eye(3))
# =>
# [[1, 2, 3],
#  [4, 5, 6],
#  [7, 8, 9]]

matmul(A, eye(3)) == A              # => True
matmul(eye(3), A) == A              # => True
matmul(eye(3), eye(3)) == eye(3)    # => True
#
# I is the only matrix that commutes with EVERY matrix.

eye(4) == transpose(eye(4))         # => True   symmetric

# ============================================
# Permutation matrices — identity with the rows moved
#
# Put the 1 of row r in column p[r]. Multiplying by it
# reorders rows.

def perm_matrix(p):
    n = len(p)
    return [[int(p[r] == c) for c in range(n)] for r in range(n)]

P = perm_matrix([2, 0, 1])
P
# =>
# [[0, 0, 1],
#  [1, 0, 0],
#  [0, 1, 0]]

matmul(P, A)
# =>
# [[7, 8, 9],
#  [1, 2, 3],
#  [4, 5, 6]]

matmul(P, A) == [A[i] for i in [2, 0, 1]]           # => True
#
# a permutation matrix is just "reorder the rows",
# expressed as arithmetic

# ============================================
# The exchange matrix — lessons 20 and 21, as algebra
#
# Reverse the identity's rows and you get the matrix
# that performs a flip.

def exchange(n):
    return [row[::-1] for row in eye(n)]

E = exchange(3)
E
# =>
# [[0, 0, 1],
#  [0, 1, 0],
#  [1, 0, 0]]

matmul(E, A) == A[::-1]                             # => True   flip VERTICAL
matmul(A, E) == [row[::-1] for row in A]            # => True   flip HORIZONTAL
matmul(E, E) == eye(3)                              # => True   its own inverse
#
# left-multiply flips rows, right-multiply flips columns.
# Lesson 21 said flip_v was `m[::-1]`; this is the same
# operation written as multiplication — and it explains
# why the two flips commute (E@A@E either way).
#
# note: TRANSPOSE cannot be written this way. Reflections
# across the diagonal are not linear maps on the grid.

# ============================================
# Matrix power — where I is genuinely necessary
#
# Binary exponentiation needs a starting value that
# means "multiplied by nothing yet". That is I.

def matpow(M, k):
    R = eye(len(M))                 # <-- the seed
    while k:
        if k & 1:
            R = matmul(R, M)
        M = matmul(M, M)
        k >>= 1
    return R

F = [[1, 1],
     [1, 0]]

matpow(F, 0) == eye(2)              # => True   anything^0 is I

matpow(F, 2)
# => [[2, 1],
#     [1, 1]]

matpow(F, 10)
# => [[89, 55],
#     [55, 34]]

matpow(F, 10)[0][1]                 # => 55     fib(10)
#
# the Fibonacci matrix: F^k holds fib(k+1), fib(k) in
# its top row. O(log k) multiplications instead of O(k)
# additions — and it only works because eye() gives the
# loop something correct to start from.

# ============================================
# Testing a matrix IS the identity

def is_identity(m):
    n = len(m)
    return (all(len(row) == n for row in m)
            and m == eye(n))

is_identity(eye(5))                 # => True
is_identity(A)                      # => False

# ============================================
# Compare — generation is a coordinate predicate

n = 4
[[int(r == c)      for c in range(n)] for r in range(n)]    # identity
[[int(c >= r)      for c in range(n)] for r in range(n)]    # upper triangular
[[int(r + c == n-1) for c in range(n)] for r in range(n)]   # anti-diagonal
[[(r + c) % 2      for c in range(n)] for r in range(n)]    # checkerboard (30)
[[(r, c)           for c in range(n)] for r in range(n)]    # coordinates (29)
#
# same comprehension, different f. That is the whole
# section in five lines.
```

---

### Memory Hooks

|You want|You reach for|
|---|---|
|the identity|`[[int(r==c) for c in range(n)] for r in range(n)]`|
|a blank grid|`[[0]*cols for _ in range(rows)]`|
|**never**|`[[0]*cols]*rows` — one row, aliased|
|a diagonal matrix|`vals[r] if r == c else 0`|
|the trace|`sum(m[i][i] for i in range(n))`|
|to multiply|`zip(*B)` for the columns|
|a row reorder|permutation matrix, `int(p[r] == c)`|
|a flip, as algebra|the exchange matrix `eye(n)` reversed|
|matrix power|start the accumulator at `eye(n)`|

---

## Key Insight

**Generation inverts the whole course: instead of asking what is in a cell, you declare it.** Every matrix in this section is `f(r, c)` wrapped in one comprehension, and the identity is the simplest `f` worth knowing — `int(r == c)`, using the fact that a Python bool *is* an int.

What makes it more than a curiosity is its algebra. `I` is the neutral element, so it is the correct starting value whenever you fold a sequence of transforms — most visibly in binary matrix exponentiation, where `matpow(F, 10)[0][1]` gives `fib(10) == 55` in four multiplications instead of ten additions.

Its variations are worth carrying too:

- **Diagonal** — replace the `1` with `vals[r]`; a scaling matrix.
    
- **Permutation** — move the `1` to column `p[r]`; multiplying reorders rows.
    
- **Exchange** — reverse the identity's rows; `E @ A` is lesson 21's `flip_v`, `A @ E` is lesson 20's `flip_h`. The flips *are* matrix multiplications. Transpose is not, which is a real distinction rather than a gap in the analogy.
    

And the Python trap that makes this the right lesson to introduce grid construction: **`[[0]*3]*3` creates one row and three references to it.** Writing to `bad[0][0]` changes all three rows. The comprehension `[[0]*3 for _ in range(3)]` evaluates the inner list once per iteration and is the only form to use.

---

## The Generation Section

|Lesson|`f(r, c)`|Produces|
|---|---|---|
|**28 Identity**|`int(r == c)`|structure — a specific matrix|
|**29 Coordinate Grid**|`(r, c)`, or any function of them|the general case|
|**30 Checkerboard**|`(r + c) % 2`|pattern — parity|

```text
                 ┌── int(r == c)   ──►  28   a landmark matrix
  f(r, c)  ──────┼── (r, c)        ──►  29   the general template
                 └── (r + c) % 2   ──►  30   a periodic pattern
```

> **Mental shift:** traversal, neighborhood, windows, structure and search all consumed a matrix. Generation produces one, and the producer is always a function from coordinates to a value. Once that lands, "build an identity matrix", "build a distance field" and "build a checkerboard" stop being three problems and become one comprehension with three different `f`s.
