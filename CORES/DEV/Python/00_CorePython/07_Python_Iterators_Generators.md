# Never Be Surprised by a Python Generator Again

*Modern Python — 3.12 and later. Every output in this essay is real Python output.*

There is **one** mental model in this essay. Not one for iterators and another for generators, not a special case for `yield from`. One.

Learn it in Part 1, then watch it explain every `for` loop, every generator, every `itertools` function, and every "why is my list empty the second time" bug you will ever hit.

**And to answer the question up front, because it comes up constantly: `yield from` is not deprecated.** It is fully current and is the right tool for delegation in 3.12+. What *was* removed is `yield from` as the coroutine mechanism (`@asyncio.coroutine`), which `async`/`await` replaced. Part 6 has the details.

---

# Part 1 — The mental model: a tap, not a bucket

```
   A LIST — a bucket                     AN ITERATOR — a tap
   ┌──────────────────────────┐          ┌──────────────────────────┐
   │   a   b   c   d   e      │          │   ▼  turn once → 'a'     │
   │   all of it, right now   │          │   nothing behind it yet  │
   └──────────────────────────┘          └──────────────────────────┘
     len() works                           len() does not
     xs[3] works                           no index, no going back
     loop over it forever                  one pass, then dry
     memory = every item                   memory = one item
     built before you use it               built as you pull
```

A `for` loop does not "run over" a collection. It **pulls**, one item at a time, and stops when the source says it's out.

```python
xs = ["a", "b", "c"]

it = iter(xs)           # <list_iterator>   ← ask for a tap
next(it)                # 'a'               ← turn it
next(it)                # 'b'
next(it)                # 'c'
next(it)                # StopIteration     ← dry
```

Those two builtins are the entire protocol, and `for` is sugar over them:

```python
for x in xs:                    it = iter(xs)
    body            ≡           while True:
                                    try:    x = next(it)
                                    except StopIteration: break
                                    body
```

> ## **Iteration is a pull. `next()` runs code until one value comes out — then everything stops until you pull again.**

Say it out loud when something surprises you. "Then everything stops" is doing the heavy lifting: between two pulls, **nothing in the source is running**.

## The three consequences

Everything else in this essay is one of these three.

| Consequence | Because |
|---|---|
| **It can be infinite.** `itertools.count()` never ends and never fills memory. | you only ever hold one item |
| **It can be one-shot.** Pull it dry and it stays dry. | there's nothing behind the tap to rewind to |
| **It can be lazy.** Side effects don't happen until someone pulls. | code between pulls isn't running |

```python
import sys
big_list = [x*x for x in range(100_000)]
big_gen  = (x*x for x in range(100_000))

sys.getsizeof(big_list)     # 800984  bytes
sys.getsizeof(big_gen)      # 208     bytes
```

Same numbers, same order, four thousand times less memory. That's not an optimisation trick — it's the difference between a bucket and a tap.

That's the model. Now we just apply it.

---

# Part 2 — Iterable vs iterator: the distinction that fixes everything

Two words, one letter apart, and almost every iteration bug is confusing them.

| | **Iterable** | **Iterator** |
|---|---|---|
| has | `__iter__` | `__next__` **and** `__iter__` |
| `__iter__` returns | a **fresh** iterator | **itself** |
| think of it as | a tap you can install | a tap that's been turned on |
| examples | `list`, `str`, `dict`, `range`, `set` | `list_iterator`, generators, `zip`, `map`, `filter`, file objects |
| reusable? | yes | **no** |

```python
xs = ["a", "b", "c"]
hasattr(xs, "__iter__")     # True
hasattr(xs, "__next__")     # False       ← a list is NOT an iterator

it = iter(xs)
hasattr(it, "__next__")     # True

iter(xs) is iter(xs)        # False       ← a list hands out a NEW tap each time
iter(it) is it              # True        ← an iterator hands out itself
```

That last pair is the whole thing. `iter(iterator) is iterator` is *why* `for` over an iterator consumes it, and why `for` over a list doesn't.

## 2.1 The one-shot family

These all return **iterators**, not collections. They are dry after one pass:

```python
z = zip([1, 2], [3, 4])
list(z)                 # [(1, 3), (2, 4)]
list(z)                 # []              ← gone

m = map(str, [1, 2])
list(m), list(m)        # (['1', '2'], [])

g = (x for x in [1, 2])
list(g), list(g)        # ([1, 2], [])

r = range(2)
list(r), list(r)        # ([0, 1], [0, 1])    ← range is an ITERABLE, not an iterator
```

`range` is the odd one out and worth remembering as the counterexample: it's lazy *and* reusable, because it computes values from arithmetic rather than holding a cursor.

Also in the one-shot family: `filter`, `reversed`, `enumerate`, every `itertools` function, every generator, and **open file objects**.

> ### **If it came from `zip`, `map`, `filter`, `enumerate`, a genexp, or `itertools` — you get one pass. Call `list()` on it if you need two.**

## 2.2 The bug this causes

```python
results = filter(is_valid, records)

print(f"found {sum(1 for _ in results)}")   # consumes it
for r in results:                            # ...and this loop never runs
    process(r)
```

No error, no warning, an empty loop. The fix is a `list()` at the top, or restructuring so you only pass over it once. **An empty second iteration is the signature of this bug** — recognise the shape and you'll spot it in seconds.

## 2.3 `iter(callable, sentinel)` — the forgotten two-argument form

`iter` has a second calling convention: call this function repeatedly until it returns the sentinel.

```python
data = iter([1, 2, 0, 3])
list(iter(lambda: next(data), 0))       # [1, 2]      ← stops at 0
```

The real use is reading in chunks without a `while True`:

```python
for chunk in iter(lambda: f.read(4096), b""):
    process(chunk)
```

---

# Part 3 — Writing an iterator by hand

You need two things: a way to produce the next value, and somewhere to remember **where you were**.

## 3.1 The reusable pattern: two classes

```python
class Countdown:                        # the ITERABLE
    def __init__(self, n): self.n = n
    def __iter__(self):
        return CountdownIter(self.n)    # a fresh cursor every time

class CountdownIter:                    # the ITERATOR
    def __init__(self, n): self.cur = n
    def __iter__(self): return self
    def __next__(self):
        if self.cur <= 0:
            raise StopIteration
        self.cur -= 1
        return self.cur + 1

c = Countdown(3)
list(c)                 # [3, 2, 1]
list(c)                 # [3, 2, 1]      ← reusable
```

The state (`self.cur`) lives in the iterator, not the iterable. That's why each `for` gets its own.

## 3.2 The one-shot pattern: one class

```python
class SelfIter:
    def __init__(self, n): self.cur = n
    def __iter__(self): return self      # ← I am my own cursor
    def __next__(self):
        if self.cur <= 0: raise StopIteration
        self.cur -= 1
        return self.cur + 1

s = SelfIter(3)
list(s)                 # [3, 2, 1]
list(s)                 # []             ← one-shot
```

Both patterns are correct — for different things.

> **Return `self` from `__iter__` only when your object genuinely IS a cursor over a stream: a file, a socket, a network cursor. For a collection, return a fresh iterator.**

## 3.3 The ancient fallback

If a class has `__getitem__` but no `__iter__`, `for` will call it with 0, 1, 2, … until `IndexError`:

```python
class OldStyle:
    def __getitem__(self, i):
        if i > 2: raise IndexError
        return i * 10

list(OldStyle())        # [0, 10, 20]
```

Recognise it in old code; don't write it.

## 3.4 …and then don't do any of this

Everything in Part 3 is written more clearly with a generator. Part 4 is why the two-class pattern above is almost never what you'll type.

---

# Part 4 — Generators: the pause button

A function containing `yield` is a **generator function**. Calling it does not run it — it hands you a **generator object**, which is an iterator.

```python
def gen():
    print("[start]")
    yield 1
    print("[between]")
    yield 2
    print("[end]")

g = gen()               # <generator object gen>   — NOTHING printed
```

Read that again: the body has not executed. Not one line. The `def` was compiled into something that builds a paused frame.

```python
next(g)
# [start]
# → 1

next(g)
# [between]
# → 2

next(g)
# [end]
# → StopIteration
```

> ## **`yield` is a pause button. The function hands out one value and freezes — locals, position, everything — until the next pull resumes it exactly where it stopped.**

That is the same model as Part 1, seen from the other side. `next()` runs code until a value comes out; `yield` is where the code decides a value has come out.

## 4.1 What "frozen" means

The whole frame is preserved: local variables, the loop counter, the position inside nested blocks, even a half-finished `try`. You don't store "where was I" — the frame *is* where you were.

```python
import inspect

g = gen()
inspect.getgeneratorstate(g)    # 'GEN_CREATED'
next(g)
inspect.getgeneratorstate(g)    # 'GEN_SUSPENDED'
```

Compare Part 3.1: `CountdownIter` needed `self.cur` because a plain method starts from the top every time. A generator needs nothing, because it doesn't start from the top.

Same thing as a generator:

```python
class Countdown:
    def __init__(self, n): self.n = n
    def __iter__(self):
        cur = self.n
        while cur > 0:
            yield cur
            cur -= 1

c = Countdown(3)
list(c), list(c)        # ([3, 2, 1], [3, 2, 1])     ← still reusable
```

Nine lines became five, the second class vanished, and it's still reusable — because each call to `__iter__` builds a **new generator**. That is the "fresh iterator" rule from 3.1, satisfied for free.

## 4.2 A generator IS an iterator

```python
g = gen()
hasattr(g, "__iter__")  # True
hasattr(g, "__next__")  # True
iter(g) is g            # True        ← so it's one-shot, per 2.1
```

Which is why `__iter__` returning a generator gives you reuse, but a generator object handed around directly does not.

## 4.3 `return` inside a generator

`return` ends the generator. Its value doesn't come out of the loop — it rides on the `StopIteration`:

```python
def with_return():
    yield 1
    return "the answer"
    yield 2                 # unreachable

g = with_return()
next(g)                 # 1
next(g)                 # StopIteration: the answer
                        # → caught as e, e.value == 'the answer'

list(with_return())     # [1]         ← list() discards the value entirely
```

So a bare `return` is just "stop here", and `return value` is a channel almost nobody reads — except `yield from`, which is exactly what makes Part 6 interesting.

---

# Part 5 — Generator expressions

A comprehension in round brackets. Same syntax, lazy semantics.

```python
squares_list = [x*x for x in range(5)]      # a bucket: [0, 1, 4, 9, 16]
squares_gen  = (x*x for x in range(5))      # a tap:    <generator object>
```

| | `[...]` | `(...)` |
|---|---|---|
| when does the work happen | immediately, all of it | one item per pull |
| memory | every item | one item |
| reusable | yes | **no** |
| `len()` | yes | no |
| best for | you need it all, more than once | feeding something that consumes once |

## 5.1 Drop the parentheses when it's the only argument

```python
sum(x*x for x in range(5))              # ✓ clean
sum((x*x for x in range(5)))            # same thing, noisier
max(len(w) for w in words)
any(e.level == "ERROR" for e in entries)
"\n".join(f"{k}={v}" for k, v in items)
```

But you need them if there's another argument:

```python
sorted((x for x in xs), reverse=True)   # parens required
```

## 5.2 The one thing that is *not* lazy

The **outermost iterable is evaluated immediately**, at creation time. Everything else waits.

```python
def source():
    print("source() called")
    return [1, 2, 3]

g = (x for x in source())
# source() called           ← already, before any pull

list(g)                 # [1, 2, 3]
```

This is usually what you want (it fails fast on a bad source), but it's a real difference from "nothing runs until you pull", and it bites when the source is expensive or has side effects.

## 5.3 When to use which

**Use a list comprehension** when the result is small, you need it more than once, or you need `len`/indexing.

**Use a generator expression** when it feeds straight into `sum`, `any`, `all`, `min`, `max`, `join`, `set`, a `for` loop, or another generator — and especially when the input is large or infinite.

**Never** write `list(x for x in xs)` — that's `[x for x in xs]` with extra steps.

---

# Part 6 — `yield from`

> ### **`yield from` is not deprecated. It is current, correct, and the right tool for delegation in 3.12+.**

The confusion comes from history. Before `async`/`await`, `yield from` was *also* how you wrote coroutines (`@asyncio.coroutine` + `yield from`). **That** usage was deprecated in 3.8 and removed in 3.11. The generator-delegation feature it was built on is untouched and heavily used — `contextlib`, `asyncio` internals, and every recursive traversal in the standard library.

## 6.1 What it does

```python
def inner():
    yield 1
    yield 2
    return "inner done"

def outer_manual():
    for v in inner():
        yield v
    yield "after"

def outer_yf():
    result = yield from inner()         # ← captures the return value
    yield f"after ({result})"

list(outer_manual())    # [1, 2, 'after']
list(outer_yf())        # [1, 2, 'after (inner done)']
```

At the level of *values produced*, `yield from sub` and `for v in sub: yield v` are identical. Everything else is different:

| `yield from sub` | `for v in sub: yield v` |
|---|---|
| captures `sub`'s **return value** | discards it |
| forwards `send()` into `sub` | swallows it |
| forwards `throw()` into `sub` | raises at the wrong level |
| forwards `close()` into `sub` | leaves `sub` unclosed |
| one bytecode-level handoff | a Python-level loop per item |

For a plain read-only iteration the two are interchangeable and `yield from` is just shorter. The moment `send`, `throw`, `close`, or a return value is involved, only `yield from` is correct.

## 6.2 The everyday use: recursion

```python
def flatten(nested):
    for item in nested:
        if isinstance(item, (list, tuple)):
            yield from flatten(item)
        else:
            yield item

list(flatten([1, [2, (3, [4])], 5]))    # [1, 2, 3, 4, 5]
```

Tree traversal is the same shape and reads beautifully:

```python
class Tree:
    def __init__(self, v, kids=()): self.v, self.kids = v, list(kids)
    def __iter__(self):
        yield self.v
        for k in self.kids:
            yield from k

t = Tree(1, [Tree(2, [Tree(4)]), Tree(3)])
list(t)                 # [1, 2, 4, 3]
list(t)                 # [1, 2, 4, 3]      ← still reusable
```

## 6.3 Concatenating sources

```python
def all_records():
    yield from read_cache()
    yield from read_disk()
    yield from read_network()
```

Three lines, zero intermediate lists, and it stops as soon as the consumer stops. (For simple concatenation of iterables, `itertools.chain` is equally good and slightly faster.)

## 6.4 The forwarding, demonstrated

```python
def echo():
    while True:
        received = yield
        print("inner got", received)

def wrapper():
    yield from echo()               # transparent pipe

w = wrapper()
next(w)                 # prime it
w.send("hello")         # inner got hello
w.send("world")         # inner got world
w.close()               # closes echo() too
```

Replace `yield from echo()` with a `for` loop and none of that works. This is the feature `yield from` was actually added for.

---

# Part 7 — Two-way generators: `send`, `throw`, `close`

`yield` is an **expression**, not just a statement. Its value is whatever gets sent in.

```python
def accumulator():
    total = 0
    while True:
        x = yield total             # hand out total, wait for a value
        if x is None:
            break
        total += x
    return total

a = accumulator()
next(a)                 # 0     ← "priming": run to the first yield
a.send(10)              # 10
a.send(5)               # 15
a.send(1)               # 16
a.send(None)            # StopIteration: 16
```

**Priming is mandatory.** A freshly created generator is paused *before* the first line; there's no suspended `yield` to receive a value. `next(a)` (or `a.send(None)`, which is the same thing) advances it to the first `yield`. Skip it and you get `TypeError: can't send non-None value to a just-started generator`.

## 7.1 `close()` and `GeneratorExit`

```python
def managed():
    print("open")
    try:
        yield 1
        yield 2
    finally:
        print("cleanup")

g = managed()
next(g)                 # open → 1
g.close()               # cleanup
```

`close()` raises `GeneratorExit` at the paused `yield`. Your `finally` runs. This is what makes `@contextlib.contextmanager` possible — and what makes a `try/finally` inside a generator trustworthy.

You may catch `GeneratorExit` to log, but you must let it propagate:

```python
def catches():
    try:
        yield 1
    except GeneratorExit:
        print("saw GeneratorExit")
        raise                       # ← re-raise. Yielding again is a RuntimeError.
```

Note the timing caveat: if you abandon a generator without closing it, cleanup happens whenever garbage collection gets round to it. For anything holding a real resource, use `contextlib.closing` (or `aclosing` for async).

## 7.2 `throw()`

```python
def resilient():
    while True:
        try:
            yield "ok"
        except ValueError as e:
            yield f"handled {e}"

g = resilient(); next(g)
g.throw(ValueError("boom"))     # 'handled boom'
```

Raises an exception at the paused `yield`, letting the generator handle it in its own context.

## 7.3 Should you use any of this?

Mostly no. `send`/`throw` were the foundation of pre-`async` coroutines, and **`async`/`await` has replaced that entire use case**. What remains legitimate:

- a running aggregation you feed incrementally
- a state machine where each step depends on what the caller supplies
- writing a context manager or a pipeline library

For everything else, a plain class with a method is clearer. **Know how to read `send` in someone else's code; think twice before writing it in yours.**

---

# Part 8 — Async iteration

Every dunder gets an `a`-prefixed twin.

| Sync | Async |
|---|---|
| `__iter__` / `__next__` | `__aiter__` / `__anext__` |
| `StopIteration` | `StopAsyncIteration` |
| `for x in it` | `async for x in it` |
| `next(it)` | `await anext(it)` |
| `iter(x)` | `aiter(x)` |

## 8.1 Async generators — the easy way

An `async def` containing `yield` is an async generator:

```python
async def aticks(n):
    for i in range(n):
        await asyncio.sleep(0)
        yield i

async def main():
    async for i in aticks(3):
        print(i)
    values = [x async for x in aticks(3)]       # async comprehension
    first = await anext(aticks(3))
```

## 8.2 By hand

```python
class ManualAiter:
    def __init__(self, n): self.n = n
    def __aiter__(self): return self            # NOT async
    async def __anext__(self):                  # IS async
        if self.n <= 0:
            raise StopAsyncIteration
        self.n -= 1
        return self.n
```

Two details people get wrong: **`__aiter__` is a plain method** (it returns the async iterator directly), and the sentinel is **`StopAsyncIteration`**.

## 8.3 Cleaning up

An abandoned async generator can't rely on garbage collection to run its `finally` at a sensible time. Use `contextlib.aclosing`:

```python
from contextlib import aclosing

async with aclosing(aticks(5)) as g:
    async for v in g:
        if v == 2:
            break                   # the generator is closed on the way out
```

## 8.4 What you cannot do

`yield from` does not work in an async generator — it's a hard `SyntaxError: 'yield from' inside async function`. Delegate with a loop instead:

```python
async def outer():
    async for v in inner():
        yield v
```

---

# Part 9 — `itertools`: the toolkit

Every one of these takes iterators and returns an iterator. They compose, they're lazy, and they're written in C.

## 9.1 Infinite

```python
import itertools as it

list(it.islice(it.count(10, 5), 4))     # [10, 15, 20, 25]     start, step
list(it.islice(it.cycle("ab"), 5))      # ['a','b','a','b','a']
list(it.repeat("x", 3))                 # ['x', 'x', 'x']
```

Always pair an infinite one with something that stops: `islice`, `takewhile`, `zip`, or a `break`.

## 9.2 Reshaping a stream

```python
it.chain([1,2], "ab", (3,))             # 1 2 'a' 'b' 3
it.chain.from_iterable([[1,2],[3]])     # 1 2 3            — flatten one level
it.islice(range(20), 2, 10, 3)          # 2 5 8            — slicing, but lazy
it.pairwise([1,2,3,4])                  # (1,2) (2,3) (3,4)        3.10+
it.batched(range(7), 3)                 # (0,1,2) (3,4,5) (6,)     3.12+
it.zip_longest("ab", "xyz", fillvalue="-")   # ('a','x') ('b','y') ('-','z')
a, b = it.tee([1,2,3])                  # two independent passes over one source
```

**`batched` is new in 3.12** and replaces a chunking helper everyone used to write by hand. In 3.13 it gained `strict=True`, which raises if the last batch is short:

```python
list(it.batched(range(7), 3))                   # [(0,1,2), (3,4,5), (6,)]
list(it.batched(range(7), 3, strict=True))      # ValueError: batched(): incomplete batch
```

`tee` looks free and isn't: it buffers everything one branch has seen that the other hasn't. If the branches move at different speeds, that buffer is your whole stream.

## 9.3 Filtering

```python
it.takewhile(lambda x: x < 3, [1,2,3,1])    # 1 2      — stops at the first False
it.dropwhile(lambda x: x < 3, [1,2,3,1])    # 3 1      — skips until the first False
it.filterfalse(lambda x: x % 2, range(6))   # 0 2 4    — the opposite of filter
it.compress("abcd", [1,0,1,0])              # 'a' 'c'  — by a mask
```

`takewhile` vs `filter` is worth pinning down: `filter` checks every item, `takewhile` **stops** at the first failure. On a sorted or infinite stream that's the difference between finishing and not.

## 9.4 Transforming and folding

```python
it.starmap(pow, [(2,3), (3,2)])                 # 8 9    — like map, but unpacks
it.accumulate([1,2,3,4])                        # 1 3 6 10        running sum
it.accumulate([1,2,3,4], lambda a,b: a*b)       # 1 2 6 24        running anything
```

## 9.5 Grouping

```python
data = [("a",1), ("a",3), ("b",2)]
[(k, list(v)) for k, v in it.groupby(data, key=lambda t: t[0])]
# [('a', [('a',1), ('a',3)]), ('b', [('b',2)])]
```

Two hard rules, both consequences of laziness:

**Sort first.** `groupby` only groups *adjacent* equal keys — it never buffers.

```python
unsorted = [("a",1), ("b",2), ("a",3)]
[(k, len(list(v))) for k, v in it.groupby(unsorted, key=lambda t: t[0])]
# [('a', 1), ('b', 1), ('a', 1)]           ← three groups, not two
```

**Consume each group before moving on.** The sub-iterators share the underlying stream:

```python
groups = list(it.groupby("aabb"))           # advanced past everything
[(k, list(g)) for k, g in groups]           # [('a', []), ('b', [])]      ← all empty
```

If you need the groups later, materialise them as you go: `{k: list(g) for k, g in groupby(...)}`.

## 9.6 Combinatorics

```python
it.product("ab", [1,2])                     # ('a',1) ('a',2) ('b',1) ('b',2)
it.permutations("abc", 2)                   # ('a','b') ('a','c') ('b','a') …
it.combinations("abcd", 2)                  # ('a','b') ('a','c') ('a','d') …
it.combinations_with_replacement("ab", 2)   # ('a','a') ('a','b') ('b','b')
```

`product(xs, repeat=n)` is the lazy nested loop, and it grows explosively. Count before you run.

---

# Part 10 — The traps

## 10.1 The exhausted iterator

*(2.1.)* Second pass is empty, no error. If you need two passes, `list()` it once at the top.

## 10.2 Nothing happens until you pull

```python
def sideeffect():
    print("side effect!")
    yield 1

g = sideeffect()        # nothing printed
list(g)                 # side effect!
```

A generator that "does" something — writes a file, sends a request, logs — does nothing until consumed. If the caller ignores the return value, the work never happens.

## 10.3 `len()` doesn't work

```python
len(x for x in range(3))    # TypeError: object of type 'generator' has no len()
sum(1 for _ in range(5))    # 5      ← count without materialising
```

## 10.4 The closure trap

```python
fs = [lambda: i for i in range(3)]
[f() for f in fs]           # [2, 2, 2]      ← not [0, 1, 2]
```

Closures capture the **variable**, not its value, and lazy evaluation means everyone reads it after the loop finished. Fix with a default argument (`lambda i=i: i`) or `functools.partial`.

## 10.5 Mutating the source mid-iteration

```python
lst = [1, 2, 3, 4]
for x in lst[:]:            # ← iterate a COPY
    if x % 2: lst.remove(x)
lst                         # [2, 4]
```

Removing from the list you're iterating skips items; adding to it can loop forever. For dicts and sets, mutation during iteration raises `RuntimeError` outright.

## 10.6 PEP 479 — `StopIteration` inside a generator

```python
def bad():
    it = iter([1])
    while True:
        yield next(it)              # next() raises StopIteration when dry

list(bad())
# RuntimeError: generator raised StopIteration
```

Since 3.7, a `StopIteration` that escapes a generator body becomes a `RuntimeError` instead of silently ending the generator. This is a **good** change — the old behaviour hid bugs — but the error message confuses people. The fix is to catch it and `return`:

```python
def good():
    it = iter([1])
    while True:
        try:
            yield next(it)
        except StopIteration:
            return
```

## 10.7 `list(gen)` defeats the purpose

If you build a lazy pipeline and then wrap it in `list()`, you've paid for the machinery and kept the memory cost. Only materialise at the point where you genuinely need a collection.

## 10.8 `groupby` without sorting

*(9.5.)* Adjacent-only. Sort by the same key first.

## 10.9 `tee` on a large stream

*(9.2.)* Buffers the gap between the branches. If one branch is a `sum()` and the other is a `for` loop, you've buffered everything.

## 10.10 The generator sees later mutations

```python
xs = [1, 2, 3]
g = (x for x in xs)
xs.append(4)
list(g)                 # [1, 2, 3, 4]
```

The generator holds the *iterator over* `xs`, not a snapshot. Usually fine; occasionally a genuine surprise.

## 10.11 Cleanup is deferred if you abandon a generator

*(7.1.)* A `finally` in an unclosed generator runs at garbage-collection time, whenever that is. Use `contextlib.closing`/`aclosing` for anything holding a resource.

---

# Part 11 — The whole thing on one page

## The protocol

```python
iter(x)                 # → an iterator.        Calls type(x).__iter__(x)
next(it)                # → the next value.     Calls type(it).__next__(it)
next(it, default)       # → default instead of raising StopIteration
raise StopIteration     # → "I'm dry"

for x in xs:  ≡  it = iter(xs);  while True: try: x = next(it) except StopIteration: break
```

| Role | Must have | `__iter__` returns |
|---|---|---|
| iterable | `__iter__` | a **fresh** iterator |
| iterator | `__iter__` + `__next__` | **itself** |

## Ways to make one

| Want | Write |
|---|---|
| a reusable iterable | a class whose `__iter__` is a generator |
| a one-shot stream | a generator function |
| an inline lazy transform | `(expr for x in xs)` |
| a cursor with explicit state | a class with `__next__` |
| delegation to a sub-source | `yield from sub` |
| "call this until it returns X" | `iter(callable, sentinel)` |

## Generator methods

| Call | Does |
|---|---|
| `next(g)` / `g.send(None)` | resume; run to the next `yield` |
| `g.send(v)` | resume, and `yield` evaluates to `v` (must be primed) |
| `g.throw(Exc)` | raise `Exc` at the paused `yield` |
| `g.close()` | raise `GeneratorExit` there; runs `finally` |
| `return v` in the body | ends it; `v` rides on `StopIteration.value` |
| `inspect.getgeneratorstate(g)` | `GEN_CREATED` / `GEN_SUSPENDED` / `GEN_RUNNING` / `GEN_CLOSED` |

## `yield from sub` vs `for v in sub: yield v`

| | `yield from` | the loop |
|---|---|---|
| values | same | same |
| `sub`'s return value | captured | lost |
| `send` / `throw` / `close` | forwarded | not forwarded |

**Not deprecated.** What went away was `yield from` for *coroutines*; `async`/`await` replaced that.

## `itertools`, by job

| Job | Functions |
|---|---|
| infinite | `count`, `cycle`, `repeat` |
| join / flatten | `chain`, `chain.from_iterable` |
| slice / window | `islice`, `pairwise` (3.10), `batched` (3.12) |
| filter | `takewhile`, `dropwhile`, `filterfalse`, `compress` |
| transform | `starmap`, `accumulate` |
| pair up | `zip_longest`, `tee` |
| group | `groupby` (sort first!) |
| combinatorics | `product`, `permutations`, `combinations`, `combinations_with_replacement` |

## Consuming without materialising

```python
sum(e.ms for e in stream)
any(e.level == "ERROR" for e in stream)
all(e.ms < 1000 for e in stream)
max(stream, key=lambda e: e.ms)
sum(1 for _ in stream)                  # count
next((e for e in stream if pred(e)), None)   # first match, or None
sorted(stream, key=...)                 # materialises — sorting needs everything
```

## Async

| Sync | Async |
|---|---|
| `__iter__` / `__next__` | `__aiter__` (plain) / `__anext__` (async) |
| `StopIteration` | `StopAsyncIteration` |
| `for` / `next()` / `iter()` | `async for` / `await anext()` / `aiter()` |
| `contextlib.closing` | `contextlib.aclosing` |
| `yield from` | *not available* — use `async for … : yield` |

---

# Part 12 — When it surprises you, ask three questions

1. **"Is this an iterable or an iterator?"** `hasattr(x, '__next__')` answers it in one line. If it's an iterator, you get one pass — and if you already spent it, the second pass is silently empty.

2. **"Has anything actually been pulled yet?"** A generator that hasn't been consumed has run zero lines. Empty output, missing side effects, and "my logging never fires" are all this.

3. **"Where is the state kept?"** In a generator it's the frozen frame; in a hand-written iterator it's the attributes you set. If two loops are interfering with each other, you're sharing one cursor where you needed two.

And the universal move: **wrap it in `list()` once and look.** If the content is right but the second pass is empty, it's exhaustion. If the content is wrong, it's your logic.

---

# Part 13 — Real code, using all of it

A lazy log pipeline. Constant memory, arbitrarily large input, and every stage is a generator.

```python
import itertools
from collections.abc import Iterable, Iterator
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Entry:
    day: str
    level: str
    service: str
    message: str
    ms: int


# --- stage 1: parse. One line in, zero-or-one Entry out. ---
def parse(lines: Iterable[str]) -> Iterator[Entry]:
    for line in lines:
        parts = line.split(maxsplit=4)
        if len(parts) < 5 or parts[1] not in {"INFO", "WARN", "ERROR"}:
            continue                                # drop bad lines, don't raise
        day, level, service = parts[0], parts[1], parts[2]
        *words, tail = (parts[3] + " " + parts[4]).split()
        yield Entry(day, level, service, " ".join(words), int(tail))


# --- stage 2: filter. A genexp is enough; no `def` needed. ---
def only(entries: Iterable[Entry], level: str) -> Iterator[Entry]:
    return (e for e in entries if e.level == level)


# --- a REUSABLE iterable: __iter__ builds a fresh generator each call ---
class Tail:
    def __init__(self, source: Iterable[Entry], n: int):
        self._source, self._n = list(source), n
    def __iter__(self) -> Iterator[Entry]:
        yield from self._source[-self._n:]
    def __len__(self) -> int:
        return min(self._n, len(self._source))


# --- recursive delegation ---
def flatten(nested) -> Iterator:
    for item in nested:
        if isinstance(item, (list, tuple)):
            yield from flatten(item)
        else:
            yield item
```

With this input:

```python
RAW = """\
2026-07-01 INFO  api    request ok 12
2026-07-01 WARN  api    slow response 340
bad line with no level
2026-07-01 ERROR db     connection lost 0
2026-07-02 INFO  api    request ok 15
2026-07-02 ERROR api    timeout 5000
2026-07-02 ERROR db     deadlock 12
2026-07-03 INFO  cache  hit 1
""".splitlines()
```

**Composing the stages:**

```python
errors = only(parse(RAW), "ERROR")
[f"{e.service}:{e.message}" for e in errors]
# ['db:connection lost', 'api:timeout', 'db:deadlock']
```

**Nothing runs until pulled:**

```python
pipeline = only(parse(RAW), "ERROR")
type(pipeline).__name__     # 'generator'      — not one line has been parsed
next(pipeline)              # Entry(day='2026-07-01', level='ERROR', service='db', …)
[e.message for e in pipeline]   # ['timeout', 'deadlock']    ← picks up where it left off
```

**itertools on the stream:**

```python
[e.ms for e in itertools.islice(parse(RAW), 3)]         # [12, 340, 0]
[len(b) for b in itertools.batched(parse(RAW), 3)]      # [3, 3, 1]
list(itertools.accumulate(e.ms for e in parse(RAW)))    # [12, 352, 352, 367, 5367, 5379, 5380]

[e.day for e in itertools.takewhile(lambda e: e.day == "2026-07-01", parse(RAW))]
# ['2026-07-01', '2026-07-01', '2026-07-01']            ← stopped at the first other day

[(day, sum(e.ms for e in group))
 for day, group in itertools.groupby(parse(RAW), key=lambda e: e.day)]
# [('2026-07-01', 352), ('2026-07-02', 5027), ('2026-07-03', 1)]
```

That `groupby` works because the log is already in date order — which is 9.5's rule, satisfied by the data rather than by a `sorted()` call.

**Reusable vs one-shot, side by side:**

```python
tail = Tail(parse(RAW), 3)
len(tail)                               # 3
[e.message for e in tail]               # ['timeout', 'deadlock', 'hit']
[e.message for e in tail]               # ['timeout', 'deadlock', 'hit']   ← still works

once = only(parse(RAW), "INFO")
[e.message for e in once]               # ['request ok', 'request ok', 'hit']
[e.message for e in once]               # []                               ← exhausted
```

**Aggregating without ever building a list:**

```python
sum(e.ms for e in parse(RAW))                       # 5380
sum(1 for e in parse(RAW) if e.level == "ERROR")    # 3
max(parse(RAW), key=lambda e: e.ms).message         # 'timeout'
any(e.ms > 1000 for e in parse(RAW))                # True
sorted({e.service for e in parse(RAW)})             # ['api', 'cache', 'db']
```

**And delegation:**

```python
list(flatten([1, [2, (3, [4])], 5]))    # [1, 2, 3, 4, 5]
```

Swap `RAW` for `open("app.log")` and not one line of the pipeline changes — and the memory usage doesn't either, whether the file is eight lines or eight million. That is the entire payoff of the tap: **the pipeline's cost is set by one item, not by the input.**

---

# Appendix

## A. `itertools`, complete

| Function | Yields |
|---|---|
| `count(start=0, step=1)` | `start, start+step, …` forever |
| `cycle(it)` | the items, forever (buffers a copy) |
| `repeat(x, n=∞)` | `x`, `n` times |
| `chain(*its)` | each iterable in turn |
| `chain.from_iterable(its)` | the same, from one iterable of iterables |
| `islice(it, stop)` / `(it, start, stop, step)` | a lazy slice — **no negative indices** |
| `pairwise(it)` | overlapping pairs (3.10) |
| `batched(it, n, *, strict=False)` | tuples of `n` (3.12; `strict` 3.13) |
| `zip_longest(*its, fillvalue=None)` | pads the short ones |
| `tee(it, n=2)` | `n` independent iterators (buffers!) |
| `takewhile(pred, it)` | until the first false |
| `dropwhile(pred, it)` | from the first false |
| `filterfalse(pred, it)` | items where `pred` is false |
| `compress(it, selectors)` | items where the selector is truthy |
| `starmap(fn, its)` | `fn(*args)` for each tuple |
| `accumulate(it, fn=add, *, initial=None)` | running results |
| `groupby(it, key=None)` | `(key, group)` for **adjacent** equal keys |
| `product(*its, repeat=1)` | the cartesian product |
| `permutations(it, r=None)` | ordered arrangements |
| `combinations(it, r)` | unordered selections |
| `combinations_with_replacement(it, r)` | …with repeats allowed |

The docs' "itertools recipes" section is worth reading once; several recipes graduated into the module (`pairwise`, `batched`) and the rest are copy-paste ready.

## B. Builtins that consume iterators

```python
list  tuple  set  frozenset  dict  sorted  reversed
sum  min  max  any  all  len(no!)  enumerate  zip  map  filter
next  iter  aiter  anext
str.join  math.prod  statistics.*  collections.Counter  collections.deque
```

`sorted`, `list`, `set`, and `Counter` **materialise** — everything else can stay lazy.

## C. Not deprecated, and what actually is

| Thing | Status |
|---|---|
| `yield from` (delegation) | **current.** Use it. |
| generators, generator expressions | current |
| `send` / `throw` / `close` | current, but niche — see 7.3 |
| `@asyncio.coroutine` + `yield from` for coroutines | **removed in 3.11.** Use `async def` / `await`. |
| `StopIteration` leaking out of a generator | **error since 3.7** (PEP 479) |
| `@types.coroutine` | still exists, for library authors bridging protocols |
| `loop.run_until_complete` boilerplate | superseded by `asyncio.run` |

## D. What landed when

| Version | Relevant |
|---|---|
| 2.2 | generators (`yield`) |
| 2.4 | generator expressions |
| 3.3 | `yield from` (PEP 380) |
| 3.5 | `async def`, `await`, `__aiter__`/`__anext__` |
| 3.6 | async generators, async comprehensions |
| 3.7 | PEP 479 — `StopIteration` in a generator is a `RuntimeError`; `contextlib.asynccontextmanager` |
| 3.8 | `__anext__` improvements; `@asyncio.coroutine` deprecated |
| 3.10 | `itertools.pairwise`, `contextlib.aclosing`, `anext()` / `aiter()` builtins |
| 3.11 | `@asyncio.coroutine` **removed** |
| **3.12** | **`itertools.batched`** |
| 3.13 | `itertools.batched(strict=True)` |

---

# The one thing to remember

> ## **Iteration is a pull. `next()` runs code until one value comes out — then everything stops until you pull again. `yield` is where the code decides a value has come out, and the frame freezes exactly there.**
>
> **An *iterable* hands out a fresh iterator every time and can be looped forever. An *iterator* hands out itself, so it gets one pass and then it's dry — that's `zip`, `map`, `filter`, `enumerate`, every genexp, and every generator.**
>
> **Write `__iter__` as a generator to get reuse for free. Use `yield from` to delegate — it is not deprecated, and it's the only form that forwards `send`, `throw`, `close`, and the sub-generator's return value.**

That is the whole system. Say "it's a tap, not a bucket" and the answer falls out.

And when the second loop comes back empty: **you already drank it.** Wrap the source in `list()` once, or restructure so you only need one pass.
