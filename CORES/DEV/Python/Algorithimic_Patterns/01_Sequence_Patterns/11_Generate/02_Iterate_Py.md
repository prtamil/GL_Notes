# Pattern 32 — Iterate

## Mental Model

Generate a sequence by **repeatedly applying the same function** to the previous value.

**Range** moves forward by a fixed numeric step. **Iterate** moves forward by applying a rule.

There's no `iterate` in Python, but a **generator function with a `while True` loop** does the same job, and `accumulate(repeat(seed), lambda acc, _: f(acc))` is the one-liner if you want one.

---

## Relationship to Cognitive Verb

```text
Generate
    ↓
Iterate
```

Iterate is a **Generate** pattern: every new element comes out of the previous one.

---

## Python Functions & Common Idioms

|Variation|Example|Common Python|
|---|---|---|
|Repeated Function|`1 2 4 8`|generator with `while True: yield x; x = f(x)`|
|One-liner|no def needed|`accumulate(repeat(x0), lambda a, _: f(a))`|
|Finite Iteration|first n values|`islice(iterate(f, x0), n)`|
|Stop on a Condition|until converged|`takewhile(p, iterate(f, x0))`|
|Find the First|first past a threshold|`next(x for x in iterate(f, x0) if p(x))`|
|Tuple State|Fibonacci|`(a, b) = (b, a + b)`|
|Sentinel Loop|read until EOF|`iter(callable, sentinel)`|
|State Machine|next state|generator over a dict of transitions|

> **Note:** `iterate` yields the **seed first**, then `f(seed)`, then `f(f(seed))` — the sequence starts with the value you gave it. Getting that off by one changes every index downstream.

---

## Common Uses

- Simulation

- State machines

- Game loops

- Numerical methods

- Physics simulation

- AI search

- Random walks

- Functional loops

---

## Hidden Interview Problems

- Generate powers of two

- Fibonacci

- Collatz sequence

- Newton's method / square root

- Happy number (cycle detection)

- BFS/DFS state expansion

- Repeated transformations until fixpoint

---

## Recognition Clues

If you hear:

- Repeatedly apply

- Next state

- Update until

- Simulation

- Current becomes next

- Functional loop

- State transition

- Until it converges

Think:

**→ Iterate**

---

## Pattern Summary

|Property|Value|
|---|---|
|Cognitive Verb|Generate|
|Pattern|Iterate|
|Input|initial value + function|
|Output|infinite lazy sequence|
|First Element|the seed itself|
|Termination|caller's job (`islice`/`takewhile`/`next`)|
|Memory|O(1) — one state at a time|
|Primary Use|State evolution|

---

## Python Recipe Book

```python
# ============================================
# The building block — write this once, reuse everywhere

from itertools import islice, takewhile, dropwhile, accumulate, repeat, count

def iterate(f, x):
    """x, f(x), f(f(x)), ... forever."""
    while True:
        yield x
        x = f(x)

# yield BEFORE applying f — the seed is element 0.

# ============================================
# Double every time

list(islice(iterate(lambda n: n * 2, 1), 6))        # => [1, 2, 4, 8, 16, 32]

# the one-liner form, no helper needed:
list(islice(accumulate(repeat(1), lambda a, _: a * 2), 6))
# => [1, 2, 4, 8, 16, 32]

# accumulate ignores the repeated element and just re-applies f.
# Clever, but the generator reads better. Know both; write the first.

# ============================================
# Increment / countdown

list(islice(iterate(lambda n: n + 1, 0), 10))       # => [0..9]
list(islice(iterate(lambda n: n - 1, 10), 6))       # => [10, 9, 8, 7, 6, 5]

# both of these are just range(). Use iterate when the step is a
# FUNCTION, not a constant.

# ============================================
# Powers

list(islice(iterate(lambda n: n * 3, 1), 6))        # => [1, 3, 9, 27, 81, 243]
[3 ** i for i in range(6)]                          # => same, directly

# when a closed form exists, use it — iterate is for when it doesn't

# ============================================
# Fibonacci — tuple state is the trick

def fib():
    a, b = 0, 1
    while True:
        yield a
        a, b = b, a + b                 # simultaneous, no temp needed

list(islice(fib(), 10))                 # => [0,1,1,2,3,5,8,13,21,34]

# same thing through iterate, carrying a pair:
pairs = iterate(lambda ab: (ab[1], ab[0] + ab[1]), (0, 1))
[a for a, _ in islice(pairs, 10)]       # => [0,1,1,2,3,5,8,13,21,34]

# when one value isn't enough state, iterate over a TUPLE and
# project out the part you want. That generalizes to any recurrence.

# ============================================
# Collatz

def collatz_step(n):
    return n // 2 if n % 2 == 0 else 3 * n + 1

list(islice(iterate(collatz_step, 7), 12))
# => [7, 22, 11, 34, 17, 52, 26, 13, 40, 20, 10, 5]

# the whole sequence until it hits 1 — note the +[1] for the endpoint:
list(takewhile(lambda n: n != 1, iterate(collatz_step, 27))) + [1]
# 112 steps

# takewhile DROPS the element that fails, so the terminator has to
# be added back. This bites constantly.

# ============================================
# Newton's method — iterate until it converges

def newton_sqrt(n, x0=1.0):
    return iterate(lambda x: (x + n / x) / 2, x0)

list(islice(newton_sqrt(2), 6))
# => [1.0, 1.5, 1.4166666666666665, 1.4142156862745097,
#     1.4142135623746899, 1.414213562373095]

# stop when the change is negligible — pairwise on the stream:
from itertools import pairwise
def converge(it, tol=1e-12):
    for a, b in pairwise(it):
        if abs(b - a) < tol:
            return b
    return None

converge(newton_sqrt(2))                # => 1.414213562373095

# ALWAYS bound a convergence loop. A non-converging f plus an
# unbounded generator is an infinite hang, not an error.
next(islice(newton_sqrt(2), 100, None)) # or cap the iteration count

# ============================================
# Fixpoint — iterate until nothing changes

def fixpoint(f, x, max_steps=1000):
    for _ in range(max_steps):
        nxt = f(x)
        if nxt == x:
            return x
        x = nxt
    raise RuntimeError("no fixpoint")

fixpoint(lambda s: s.replace("aa", "a"), "aaaabaaa")         # => 'aba'

# "keep simplifying until it stops changing" — parsers, layout
# engines, and constant folders are all this loop

# ============================================
# Stop conditions — three ways to bound an infinite iterate

g = lambda: iterate(lambda n: n * 2, 1)

list(islice(g(), 5))                            # => [1,2,4,8,16]   first n
list(takewhile(lambda n: n < 100, g()))         # => [1,2,4,8,16,32,64]
next(x for x in g() if x >= 100)                # => 128     first past

# takewhile stops BEFORE the failing element; the `next` genexp
# returns it. Pick by whether you want the crossing value.

list(islice(dropwhile(lambda n: n < 100, g()), 3))          # => [128,256,512]

# ============================================
# State machine

transitions = {
    "idle":    "running",
    "running": "paused",
    "paused":  "running",
}
list(islice(iterate(transitions.get, "idle"), 5))
# => ['idle', 'running', 'paused', 'running', 'paused']

# dict.get IS a transition function. For richer state, iterate over
# a dict or a dataclass and return a NEW one each step:
def tick(s):
    return {**s, "t": s["t"] + 1, "x": s["x"] + s["v"]}

list(islice(iterate(tick, {"t": 0, "x": 0, "v": 3}), 3))
# => [{'t':0,'x':0,'v':3}, {'t':1,'x':3,'v':3}, {'t':2,'x':6,'v':3}]

# return a NEW dict. Mutating and returning the same object gives
# you n references to one state, all showing the final values.

# ============================================
# Random walk — a stateful f is fine, it just isn't pure

import random
random.seed(0)
list(islice(iterate(lambda x: x + random.choice([-1, 1]), 0), 8))
# => [0, 1, 2, 3, 2, 3, 4, 3]

# ============================================
# Cycle detection — iterate can loop forever without terminating

def has_cycle(f, x0, limit=10_000):
    seen = set()
    for x in islice(iterate(f, x0), limit):
        if x in seen:
            return True
        seen.add(x)
    return False

def happy_step(n):
    return sum(int(d) ** 2 for d in str(n))

has_cycle(happy_step, 4)                # => True    4 is not a happy number

# an iterate over a finite state space MUST eventually repeat.
# Track seen states or bound the steps — "it converges" is an
# assumption, not a guarantee.

# ============================================
# iter(callable, sentinel) — the built-in iterate for I/O

# read 4KB blocks until EOF:
# with open("f.bin", "rb") as fh:
#     for block in iter(lambda: fh.read(4096), b""):
#         ...

# calls the function repeatedly, stops when it returns the sentinel.
# The one place the standard library gives you this pattern directly.

# ============================================
# range vs iterate

list(range(0, 10, 2))                           # => [0,2,4,6,8]
list(islice(iterate(lambda n: n + 2, 0), 5))    # => [0,2,4,6,8]

# identical output. range knows its length and endpoint; iterate
# doesn't and can't. Use range for arithmetic progressions,
# iterate when the next value depends on the current one in any
# other way.

# ============================================
# Compare

iterate(f, x0)                  # x, f(x), f(f(x))...     → Iterate
range(a, b, s)                  # fixed numeric step      → Range
accumulate(xs, f)               # folds over INPUT data   → Scan
cycle(xs)                       # repeats a fixed list    → Cycle
repeat(x)                       # the same value forever  → Repeat
```

---

### Memory Hooks

|You want|You reach for|
|---|---|
|repeated application|`while True: yield x; x = f(x)`|
|the first n values|`islice(iterate(f, x0), n)`|
|values while a condition holds|`takewhile(p, iterate(f, x0))`|
|the first value that crosses|`next(x for x in iterate(...) if p(x))`|
|more than one state variable|iterate over a tuple / dict|
|Fibonacci|`a, b = b, a + b`|
|convergence|`pairwise` + a tolerance + a step cap|
|"until nothing changes"|a `fixpoint` loop|
|to detect a loop|a `seen` set|
|read-until-sentinel|`iter(callable, sentinel)`|

---

### Key Insight

**Iterate is a `while` loop in functional clothing, and the defining thing about it is that stopping isn't its job.** The generator produces values forever and the caller decides how many to take, with `islice`, `takewhile` or `next`. That separation is the whole benefit: the *rule* for advancing state is written once and stays independent of the *reason* for stopping, so the same Collatz stepper serves "first 12 values", "until it reaches 1", and "how many steps does 27 take".

**When one value isn't enough state, iterate over a tuple.** Fibonacci is the classic demo: `a, b = b, a + b` carries two values through one function and you pull out what you want afterwards. Every recurrence that looks back more than one step, every simulation with position and velocity, every parser with a cursor and a stack — they're all `iterate` over a compound state. If you're returning a dict, return a *new* one. Mutating and re-yielding the same object leaves you with n references to a single state and a sequence that looks like it was the final value all along.

The danger mirrors the benefit: **an unbounded generator with no exit condition hangs, it doesn't raise.** Newton's method on a bad seed, a state machine with an absorbing loop, a fixpoint that never arrives — none of these throw anything. Bound the steps, or keep a `seen` set. A finite state space guarantees repetition eventually, so "it will converge" is something to check rather than assume.
