# Never Be Mystified by a Python Dunder Again

*Modern Python — 3.12 and later. Every output in this essay is real Python output.*

There is **one** mental model in this essay. Not one for operators and another for `len()`, not a special case for `with`. One.

Learn it in Part 1, then watch it explain every dunder you will ever write — `__repr__`, `__eq__`, `__add__`, `__iter__`, `__enter__`, `__get__`, `__await__`, all of them. Same model every time.

---

# Part 1 — The mental model: syntax is a rewrite

Python's syntax is a **phrasebook**. Every operator, every builtin, and most statements have a fixed translation into a method call, and the interpreter performs that translation before anything else happens.

```
   YOU WRITE               PYTHON ACTUALLY RUNS
   ─────────               ────────────────────
   len(x)             →    type(x).__len__(x)
   x + y              →    type(x).__add__(x, y)
   x[k]               →    type(x).__getitem__(x, k)
   x(1)               →    type(x).__call__(x, 1)
   print(x)           →    type(x).__str__(x)
   k in x             →    type(x).__contains__(x, k)
   for i in x: ...    →    type(x).__iter__(x),  then  __next__
   with x: ...        →    type(x).__enter__(x) … __exit__(x, …)
   if x: ...          →    type(x).__bool__(x)
   x == y             →    type(x).__eq__(x, y)
   -x                 →    type(x).__neg__(x)
   del x[k]           →    type(x).__delitem__(x, k)
```

> ## **A dunder is not magic. It is the right-hand side of a rewrite that Python was going to perform anyway.**

You never call these yourself. You never choose the name. Your only job is to **fill in the answer**, and Python's syntax starts working on your object.

## The three facts that follow

Say these out loud when a dunder confuses you:

> ## **"What does this rewrite to? Is that name on my TYPE? And what's the fallback if it isn't?"**

| Fact | Consequence |
|---|---|
| **1. The name is fixed** | You don't invent dunder names. You fill in ones Python already asks for. Inventing `__mine__` gets you nothing. |
| **2. The lookup is on the TYPE** | Not the instance. This is called *implicit special method lookup*, and it surprises everybody once. |
| **3. Missing has a defined fallback** | Sometimes another dunder, sometimes a sensible default, sometimes `TypeError`. Never a crash you can't explain. |

## Fact 2, demonstrated — because it's the one that bites

Put `__len__` in the **instance's drawer** and `len()` does not care:

```python
class Plain:
    pass

p = Plain()
p.__len__ = lambda: 5

p.__len__()             # 5      — an ordinary attribute lookup, works fine
len(p)                  # TypeError: object of type 'Plain' has no len()
```

```python
class Typed:
    def __len__(self): return 5

len(Typed())            # 5
```

Implicit dunder lookup skips the instance dictionary entirely and goes straight to the type. Two reasons, both good: **speed** (the interpreter can cache a slot on the type) and **sanity** (`1 + 1` shouldn't have to check whether this particular `int` was given a custom `__add__`).

Practically: **dunders go in the class body. Always.** Patching one onto an instance is one of those things that appears to work right up until you use it.

## What "fallback" means

Fact 3 is why so much works with so little effort. A few of the chains, so you can see the shape:

```
   bool(x)  →  __bool__     → else __len__ != 0     → else True
   str(x)   →  __str__      → else __repr__         → else <Class object at 0x…>
   iter(x)  →  __iter__     → else __getitem__ from 0 → else TypeError
   k in x   →  __contains__ → else __iter__ and scan → else __getitem__ scan → else TypeError
   x != y   →  __ne__       → else not __eq__       → else identity
   x + y    →  x.__add__(y) → else y.__radd__(x)    → else TypeError
```

Every one of those arrows is documented, deterministic, and worth knowing. The rest of this essay walks them.

That's the model. Now we just apply it.

---

# Part 2 — Showing up: `__repr__`, `__str__`, `__format__`, `__bytes__`

## 2.1 `__repr__` — the one to write first

```python
class Point:
    def __init__(self, x, y): self.x, self.y = x, y
    def __repr__(self): return f"Point(x={self.x}, y={self.y})"

p = Point(1, 2)
repr(p)                 # 'Point(x=1, y=2)'
str(p)                  # 'Point(x=1, y=2)'    ← fell back to __repr__
f"{p}"                  # 'Point(x=1, y=2)'    ← same
[p]                     # [Point(x=1, y=2)]    ← containers always use repr
```

Rewrites: `repr(x)` → `__repr__`. Also the REPL echo, the debugger, `%r`, `{!r}`, and — critically — **every element inside a container**. A list of objects with no `__repr__` is a list of hex addresses, which is why this is the single highest-value dunder in Python.

**Write it for the reader, and aim for `eval`-ability.** The convention is that `repr(x)` should look like the source that would rebuild `x`:

```python
def __repr__(self) -> str:
    return f"{type(self).__name__}(x={self.x!r}, y={self.y!r})"
```

Two habits in that one line: `type(self).__name__` so subclasses print their own name, and `!r` on the fields so strings show their quotes.

## 2.2 `__str__` — only when a human needs something different

```python
class Both:
    def __repr__(self): return "Both()"
    def __str__(self):  return "a friendly Both"

b = Both()
repr(b)         # 'Both()'
str(b)          # 'a friendly Both'
f"{b}"          # 'a friendly Both'
print(b)        # a friendly Both
[b]             # [Both()]              ← containers still use repr
f"{b!r} {b!s}"  # 'Both() a friendly Both'
```

`__str__` defaults to `__repr__`, so **skipping it is usually right.** Add it only when the debugging view and the user-facing view genuinely differ — a `Path`, a `Money`, a `Duration`.

| | `__repr__` | `__str__` |
|---|---|---|
| audience | you, debugging | your user |
| triggered by | `repr()`, REPL, containers, `!r` | `str()`, `print()`, f-strings, `!s` |
| falls back to | `<Class object at 0x…>` | `__repr__` |
| write it? | **always** | only if different |

## 2.3 `__format__` — the f-string spec after the colon

Everything after the `:` in `f"{x:spec}"` is handed to `__format__` as a string. You decide what it means.

```python
class Money:
    def __init__(self, amt): self.amt = amt
    def __repr__(self): return f"Money({self.amt})"
    def __format__(self, spec):
        if spec == "":
            return str(self.amt)
        return format(self.amt, spec)       # delegate to float's spec language

m = Money(1234.5)
f"{m}"              # '1234.5'
f"{m:,.2f}"         # '1,234.50'
f"{m:>12,.2f}"      # '    1,234.50'
format(m, ".1f")    # '1234.5'
```

Delegating to a field's own `__format__` — as above — gets you the entire mini-language for free. Only invent your own spec codes when you have something the standard ones can't express.

The default `__format__` accepts only the empty spec and calls `str()`; anything else raises `TypeError`.

## 2.4 `__bytes__`

```python
class Raw:
    def __bytes__(self): return b"raw"

bytes(Raw())        # b'raw'
```

Rare. Reach for it when your object genuinely has a wire representation.

---

# Part 3 — Being a value: `__eq__`, `__hash__`, and ordering

## 3.1 `__eq__` and the `NotImplemented` handshake

```python
class V:
    def __init__(self, n): self.n = n
    def __eq__(self, other):
        if not isinstance(other, V):
            return NotImplemented           # "not my business — ask the other one"
        return self.n == other.n

V(1) == V(1)        # True
V(1) != V(1)        # False        ← __ne__ is derived from __eq__ automatically
V(1) == 5           # False        ← both sides declined, Python fell back to identity
```

Two things to internalise:

- **`__ne__` is free.** Python derives `!=` by negating `__eq__`. Don't write `__ne__`.
- **Return `NotImplemented`, never `False`, for types you don't handle.** `NotImplemented` means *"I decline; give the other operand a turn."* Returning `False` claims authority you don't have and breaks the other type's ability to compare itself to you. (It's the singleton `NotImplemented`, not the exception `NotImplementedError` — different things, easy to typo.)

## 3.2 Defining `__eq__` silently removes `__hash__`

This is the highest-consequence default in the whole language.

```python
class V:
    def __eq__(self, other): ...

V.__hash__          # None      ← Python set it to None for you
{V(1)}              # TypeError: cannot use 'V' as a set element (unhashable type: 'V')
```

The reason is a contract that dictionaries depend on:

> ### **If `a == b` then `hash(a) == hash(b)`. Always.**

If you redefine equality and keep the inherited identity-based hash, two equal objects get different hashes, and they land in different buckets of a dict — meaning `d[a]` can't find the value you stored under `b`. Rather than let you build that bug, Python makes the object unhashable and waits for you to decide.

Your three options:

```python
# 1. It's a value: hash the same fields you compare.
class H:
    def __init__(self, n): self.n = n
    def __eq__(self, o): return isinstance(o, H) and self.n == o.n
    def __hash__(self):   return hash(self.n)

len({H(1), H(1)})       # 1      ← correctly deduplicated

# 2. It's mutable and shouldn't be a key: leave it unhashable. This is fine.

# 3. You really want identity hashing anyway (rare, and you'd better mean it):
class Keep:
    def __eq__(self, o): return True
    __hash__ = object.__hash__
```

And a fourth, which is the one you'll actually use:

```python
@dataclass(frozen=True)     # generates __eq__ AND __hash__, correctly paired
class Point:
    x: int
    y: int
```

> **Only hash what you compare, and only hash what can't change. A mutable object used as a dict key is a bug with a delay fuse.**

## 3.3 Ordering: `__lt__`, `__le__`, `__gt__`, `__ge__`

Four independent dunders, one per operator. `a < b` tries `a.__lt__(b)`; if that returns `NotImplemented`, it tries the **reflected** operation `b.__gt__(a)`.

```python
class L:
    def __lt__(self, o): return True
class R:
    def __gt__(self, o): return "R.__gt__ ran"

L() < R()               # True                — L answered
```

```python
class OnlyGt:
    def __gt__(self, o): return "gt ran"

OnlyGt() < 5            # TypeError: '<' not supported between
                        #            instances of 'OnlyGt' and 'int'
```

The reflection pairs are `__lt__`↔`__gt__` and `__le__`↔`__ge__`. Note the asymmetry with equality: `__eq__` is its own reflection.

## 3.4 `@total_ordering` — write two, get six

```python
from functools import total_ordering

@total_ordering
class Ver:
    def __init__(self, t): self.t = t
    def __eq__(self, o): return isinstance(o, Ver) and self.t == o.t
    def __lt__(self, o): return self.t < o.t if isinstance(o, Ver) else NotImplemented
    def __repr__(self): return f"Ver{self.t}"

a, b = Ver((1, 0)), Ver((1, 2))
a < b, a <= b, a > b, a >= b, a == b, a != b        # (True, True, False, False, False, True)
sorted([b, a])                                       # [Ver(1, 0), Ver(1, 2)]
```

Define `__eq__` and any *one* of the four ordering dunders, and the decorator fills in the rest. Slightly slower than hand-writing all four; almost always worth it.

The simplest correct implementation of ordering is to **compare tuples of your fields** — Python already orders tuples lexicographically:

```python
def _key(self): return (self.major, self.minor, self.patch)
def __lt__(self, o): return self._key() < o._key() if isinstance(o, Ver) else NotImplemented
```

Or reach for `@dataclass(order=True)`, which generates all four from field order.

## 3.5 `__bool__` and `__len__`

```
   bool(x)  →  __bool__  →  else __len__() != 0  →  else True
```

```python
class NoDunders: pass
class HasLen:
    def __len__(self): return 0
class HasBool:
    def __len__(self): return 0
    def __bool__(self): return True

bool(NoDunders())       # True     ← the default. Everything is truthy.
bool(HasLen())          # False    ← len 0 means falsy, for free
bool(HasBool())         # True     ← __bool__ wins outright
```

That first line is a trap in disguise:

```python
class Empty:
    def __init__(self): self.items = []

bool(Empty())           # True     — always. Regardless of self.items.
```

**If your object can meaningfully be "empty", give it `__len__`.** You get `bool()`, `if x:`, `while x:`, `not x`, and `len(x)` from one method.

Both are strict about return types:

```python
class BadLen:
    def __len__(self): return -1
len(BadLen())           # ValueError: __len__() should return >= 0

class BadBool:
    def __bool__(self): return 1
bool(BadBool())         # TypeError: __bool__ should return bool, returned int
```

`__len__` must return a non-negative `int`; `__bool__` must return an actual `bool`.

---

# Part 4 — Being a container

Five dunders, each mapping to one piece of syntax.

```python
class Grid:
    def __init__(self):            self.cells = {}
    def __getitem__(self, key):    return self.cells[key]          # g[k]
    def __setitem__(self, key, v): self.cells[key] = v             # g[k] = v
    def __delitem__(self, key):    del self.cells[key]             # del g[k]
    def __contains__(self, key):   return key in self.cells        # k in g
    def __len__(self):             return len(self.cells)          # len(g)

g = Grid()
g[0, 0] = "a"           # the key arrives as the TUPLE (0, 0)
g["k"] = "b"
g[0, 0]                 # 'a'
len(g)                  # 2
(0, 0) in g             # True
del g[0, 0]
len(g)                  # 1
```

## 4.1 What actually arrives as `key`

Everything between the brackets, as one object. Watch:

```python
class Peek:
    def __getitem__(self, k): return f"{k!r}  ({type(k).__name__})"

pk = Peek()
pk[3]                   # '3  (int)'
pk[1:5]                 # 'slice(1, 5, None)  (slice)'
pk[1:9:2]               # 'slice(1, 9, 2)  (slice)'
pk[1, 2]                # '(1, 2)  (tuple)'
pk[...]                 # 'Ellipsis  (ellipsis)'
```

Three things fall out:

- **Slicing is not separate syntax.** `x[1:5]` is `__getitem__` with a `slice` object. If you want slicing, branch on `isinstance(key, slice)` and use `key.indices(len(self))` to normalise it.
- **Multi-dimensional indexing is just a tuple.** `arr[i, j]` is how NumPy and pandas work — there's no special support, only a tuple.
- **`x[...]` passes `Ellipsis`**, which is a real singleton object you can check for.

## 4.2 `__contains__` has two fallbacks

```
   k in x  →  __contains__  →  else __iter__ and scan  →  else __getitem__ from 0 and scan
```

```python
class NoContains:
    def __iter__(self): return iter([1, 2, 3])

2 in NoContains()       # True   — Python iterated and compared
```

So `in` works the moment you're iterable. Write `__contains__` only when you can answer **faster** than a scan (a dict or set behind the scenes) or when membership means something other than "an element equals this".

## 4.3 `__missing__` — dict subclasses only

```python
class Counter(dict):
    def __missing__(self, k): return 0

c = Counter()
c["a"] += 1             # reads a missing key → 0, then writes 1
c                       # {'a': 1}
c["zzz"]                # 0      — and NOT stored
```

`dict.__getitem__` calls `__missing__` when a key is absent. It is *only* consulted by `dict` and its subclasses — putting it on an ordinary class does nothing. This is exactly how `collections.defaultdict` works.

## 4.4 `__reversed__`

```python
class Rev:
    def __iter__(self):     return iter([1, 2, 3])
    def __reversed__(self): return iter(["c", "b", "a"])

list(reversed(Rev()))   # ['c', 'b', 'a']
```

And you often don't need it — `reversed()` works automatically on anything with both `__len__` and `__getitem__`:

```python
class RevAuto:
    def __len__(self):        return 3
    def __getitem__(self, i): return i * 10

list(reversed(RevAuto()))   # [20, 10, 0]
```

## 4.5 The shortcut you should usually take

If your class is genuinely a sequence or a mapping, inherit the abstract base and implement the two or three required methods. You get a dozen more for free, all correct:

```python
from collections.abc import Sequence, MutableMapping

class Deck(Sequence):                   # implement __len__ + __getitem__
    def __init__(self, cards): self._cards = list(cards)
    def __len__(self):         return len(self._cards)
    def __getitem__(self, i):  return self._cards[i]

d = Deck("abcde")
d[1], d[1:3], len(d), "c" in d, list(reversed(d)), d.index("c"), d.count("a")
# ('b', ['b', 'c'], 5, True, ['e','d','c','b','a'], 2, 1)
```

`__contains__`, `__iter__`, `__reversed__`, `index`, and `count` all arrived free. `MutableSequence`, `Mapping`, `MutableMapping`, and `Set` do the same for their protocols.

---

# Part 5 — Being iterable: `__iter__` and `__next__`

Two separate roles, and mixing them up is the classic mistake.

| Role | Dunder | Contract |
|---|---|---|
| **iterable** | `__iter__` | returns a *fresh* iterator each time |
| **iterator** | `__next__` (+ `__iter__` returning `self`) | returns the next item, or raises `StopIteration` |

## 5.1 The easy way: `__iter__` as a generator

```python
class Countdown:
    def __init__(self, n): self.n = n
    def __iter__(self):
        cur = self.n
        while cur > 0:
            yield cur
            cur -= 1

list(Countdown(3))      # [3, 2, 1]
list(Countdown(3))      # [3, 2, 1]      ← reusable, because each call is a new generator
```

Because `__iter__` contains `yield`, calling it returns a brand-new generator — which is already a perfectly good iterator. **This is how you should write iteration 95% of the time.**

## 5.2 The manual way, and why it burns you

```python
class Manual:
    def __init__(self, n): self.n = n
    def __iter__(self):  return self             # ← I am my own iterator
    def __next__(self):
        if self.n <= 0: raise StopIteration
        self.n -= 1
        return self.n + 1

m = Manual(3)
list(m)                 # [3, 2, 1]
list(m)                 # []              ← exhausted. Forever.
```

An object that returns `self` from `__iter__` is **one-shot**. Sometimes that's exactly right (a file, a socket, a stream). It is almost never right for a collection, and it produces a beautifully confusing bug where a `for` loop over your object works and the *second* one silently does nothing.

> **`__iter__` should return `self` only if your object genuinely IS a cursor over a stream. Otherwise return a fresh generator.**

## 5.3 The ancient fallback

Before `__iter__` existed, `for` used `__getitem__` with 0, 1, 2, … until `IndexError`. That path still works:

```python
class OldStyle:
    def __getitem__(self, i):
        if i > 2: raise IndexError
        return i * 10

list(OldStyle())        # [0, 10, 20]
20 in OldStyle()        # True
```

Worth recognising in old code. Don't write new code that relies on it.

## 5.4 `__iter__` must return an *iterator*

```python
class BadIter:
    def __iter__(self): return [1, 2, 3]

list(BadIter())         # TypeError: iter() returned non-iterator of type 'list'
```

A list is iterable but is *not* an iterator (no `__next__`). Return `iter([1,2,3])`, or use `yield`.

---

# Part 6 — Doing arithmetic

## 6.1 The three-way family

Every binary operator has **three** dunders, and each answers a different question.

| Dunder | Question | Triggered by |
|---|---|---|
| `__add__` | "can I handle `me + other`?" | `a + b`, tried first |
| `__radd__` | "can I handle `other + me`?" | `a + b` when `a.__add__` declined |
| `__iadd__` | "can I absorb `other` into myself?" | `a += b` |

```python
class Vec:
    def __init__(self, x, y): self.x, self.y = x, y
    def __repr__(self): return f"Vec({self.x}, {self.y})"

    def __add__(self, o):
        if isinstance(o, Vec): return Vec(self.x + o.x, self.y + o.y)
        return NotImplemented

    def __mul__(self, k):
        if isinstance(k, (int, float)): return Vec(self.x * k, self.y * k)
        return NotImplemented
    __rmul__ = __mul__                   # scalar * vec == vec * scalar

    def __neg__(self): return Vec(-self.x, -self.y)
    def __abs__(self): return (self.x**2 + self.y**2) ** 0.5

v = Vec(1, 2)
v + Vec(3, 4)           # Vec(4, 6)
v * 3                   # Vec(3, 6)
3 * v                   # Vec(3, 6)     ← __rmul__ did this
-v                      # Vec(-1, -2)
abs(Vec(3, 4))          # 5.0
v + 1                   # TypeError: unsupported operand type(s) for +: 'Vec' and 'int'
```

That `TypeError` message is Python reporting that **both** operands declined. It is the correct outcome and it comes for free — as long as you return `NotImplemented`.

## 6.2 `NotImplemented` is the whole protocol

```python
class Left:
    def __add__(self, o): return NotImplemented
class Right:
    def __radd__(self, o): return "Right.__radd__ ran"

Left() + Right()        # 'Right.__radd__ ran'
```

The rule Python follows for `a + b`:

```
   1. try  type(a).__add__(a, b)
   2. NotImplemented?  try  type(b).__radd__(b, a)
   3. still NotImplemented?  raise TypeError
```

With one refinement: **if `type(b)` is a subclass of `type(a)` and overrides the reflected method, `b` goes first.** The subclass is presumed to know more.

```python
class Base:
    def __add__(self, o):  return "Base.__add__"
    def __radd__(self, o): return "Base.__radd__"
class Sub(Base):
    def __radd__(self, o): return "Sub.__radd__ (subclass wins)"

Base() + Sub()          # 'Sub.__radd__ (subclass wins)'
```

## 6.3 In-place: `__iadd__` and the `+=` you thought you understood

```python
class Bag:
    def __init__(self, items): self.items = list(items)
    def __repr__(self): return f"Bag({self.items})"
    def __iadd__(self, o):
        self.items.extend(o)
        return self                      # ← you MUST return something

b = Bag([1]); before = id(b)
b += [2, 3]
b                       # Bag([1, 2, 3])
id(b) == before         # True     — same object, mutated in place
```

`a += b` compiles to `a = type(a).__iadd__(a, b)` — **the rebinding happens either way.** That's why `__iadd__` must return `self`; forget, and `a` becomes `None`.

Without `__iadd__`, `+=` falls back to `__add__` and rebinds to a new object:

```python
class NoIadd:
    def __init__(self, n): self.n = n
    def __add__(self, o): return NoIadd(self.n + o.n)
    def __repr__(self): return f"NoIadd({self.n})"

n = NoIadd(1); orig = id(n)
n += NoIadd(2)
n                       # NoIadd(3)
id(n) == orig           # False    — a new object; the fallback did its job
```

> **Define `__iadd__` only for mutable types, and only when in-place mutation is genuinely cheaper. For immutable values, let it fall back — that's the correct behaviour, not a gap.**

## 6.4 The complete operator table

Every row is the same three-way family: `__op__`, `__rop__`, `__iop__`.

| Syntax | Dunder | Reflected | In-place |
|---|---|---|---|
| `a + b` | `__add__` | `__radd__` | `__iadd__` |
| `a - b` | `__sub__` | `__rsub__` | `__isub__` |
| `a * b` | `__mul__` | `__rmul__` | `__imul__` |
| `a / b` | `__truediv__` | `__rtruediv__` | `__itruediv__` |
| `a // b` | `__floordiv__` | `__rfloordiv__` | `__ifloordiv__` |
| `a % b` | `__mod__` | `__rmod__` | `__imod__` |
| `a ** b` | `__pow__` | `__rpow__` | `__ipow__` |
| `a @ b` | `__matmul__` | `__rmatmul__` | `__imatmul__` |
| `a << b` | `__lshift__` | `__rlshift__` | `__ilshift__` |
| `a >> b` | `__rshift__` | `__rrshift__` | `__irshift__` |
| `a & b` | `__and__` | `__rand__` | `__iand__` |
| `a \| b` | `__or__` | `__ror__` | `__ior__` |
| `a ^ b` | `__xor__` | `__rxor__` | `__ixor__` |
| `divmod(a,b)` | `__divmod__` | `__rdivmod__` | — |

Unary and the odd ones out:

| Syntax | Dunder |
|---|---|
| `-a` | `__neg__` |
| `+a` | `__pos__` |
| `~a` | `__invert__` |
| `abs(a)` | `__abs__` |
| `pow(a, b, m)` | `__pow__(self, b, mod=None)` — the third argument is optional |

```python
class D:
    def __divmod__(self, o):        return ("q", "r")
    def __pow__(self, o, mod=None): return f"pow(mod={mod})"

divmod(D(), 3)          # ('q', 'r')
D() ** 2                # 'pow(mod=None)'
pow(D(), 2, 7)          # 'pow(mod=7)'
```

`@` (matmul) has no meaning for built-in types at all — it exists purely so numeric libraries can spell matrix multiplication. `|` on your own class is how `X | Y` type unions and `dict | dict` merging are spelled.

## 6.5 Conversions

| Syntax | Dunder | Must return | Note |
|---|---|---|---|
| `int(x)` | `__int__` | `int` | explicit conversion only |
| `float(x)` | `__float__` | `float` | |
| `complex(x)` | `__complex__` | `complex` | |
| `x` as an **index** | `__index__` | `int` | **lossless** — used by `list[x]`, `range`, `hex`, `bin`, slicing |
| `round(x, n)` | `__round__(self, nd=None)` | anything | |
| `math.trunc(x)` | `__trunc__` | `int` | |
| `math.floor(x)` | `__floor__` | `int` | |
| `math.ceil(x)` | `__ceil__` | `int` | |

```python
class Idx:
    def __index__(self):        return 2
    def __int__(self):          return 99
    def __float__(self):        return 1.5
    def __round__(self, nd=None): return "rounded"

i = Idx()
[10, 20, 30][i]         # 30       ← __index__, not __int__
hex(i)                  # '0x2'    ← __index__
list(range(10))[i:]     # [2, 3, 4, 5, 6, 7, 8, 9]
int(i)                  # 99       ← __int__, only for the explicit call
float(i)                # 1.5
round(i)                # 'rounded'
```

**`__index__` is the one that matters.** It means "I am *exactly* an integer, losslessly" and is what any interpreter operation needing a real index will use. `__int__` means "I can be converted, possibly lossily" and is only used when someone writes `int(x)`. Give a whole-number type `__index__`; give a float-like type `__int__`.

---

# Part 7 — Being called: `__call__`

```python
class Adder:
    def __init__(self, n): self.n = n
    def __call__(self, x): return x + self.n

add5 = Adder(5)
add5(10)                # 15
callable(add5)          # True
```

`x(...)` → `type(x).__call__(x, ...)`. That's it.

**Use it when** you have a function with configuration: a parameterised validator, a retry policy, a decorator with arguments, a stateful accumulator. The alternative — a closure — is often simpler; reach for `__call__` when the object also needs a `repr`, other methods, or to be pickled.

And one to file away: `__call__` on a **metaclass** is what makes `MyClass(...)` build an instance. Same dunder, one storey up — essay 05.

---

# Part 8 — Attribute access

Four dunders, and a very sharp difference between two of them.

| Syntax | Dunder | When it fires |
|---|---|---|
| `x.name` | `__getattribute__` | **every** read |
| `x.name` | `__getattr__` | only when the normal lookup **failed** |
| `x.name = v` | `__setattr__` | **every** write |
| `del x.name` | `__delattr__` | every delete |
| `dir(x)` | `__dir__` | `dir()` |

## 8.1 `__getattr__` — the safe one

```python
class Loose:
    known = 1
    def __init__(self): self.own = 2
    def __getattr__(self, name):
        return f"<no {name}>"

l = Loose()
l.known, l.own, l.anything      # (1, 2, '<no anything>')
```

It is the **last resort** in the lookup chain, so it never fires for attributes that exist. That makes it cheap and hard to break — good for proxies, lazy loading, and dynamic APIs.

## 8.2 `__setattr__` — the dangerous one

It intercepts **every** write, including the ones inside your own `__init__`. Which means `self.x = 1` inside `__setattr__` is infinite recursion. You must go around yourself:

```python
class Locked:
    def __init__(self, x):
        object.__setattr__(self, "x", x)         # the only way in
    def __setattr__(self, name, value):
        raise AttributeError(f"{type(self).__name__} is read-only")

lk = Locked(5)
lk.x                    # 5
lk.x = 6                # AttributeError: Locked is read-only
```

This is exactly how `@dataclass(frozen=True)` is implemented.

## 8.3 A proxy, using both

```python
class Proxy:
    def __init__(self, target):
        object.__setattr__(self, "_t", target)
    def __getattr__(self, name):
        return getattr(self._t, name)
    def __setattr__(self, name, v):
        setattr(self._t, name, v)
    def __dir__(self):
        return dir(self._t)
```

Note `object.__setattr__` in `__init__` again — without it, storing `_t` would call our own `__setattr__`, which needs `_t`, which doesn't exist yet.

## 8.4 `__getattribute__` — almost always wrong

```python
class Watch:
    def __init__(self): self.x = 1
    def __getattribute__(self, name):
        print(f"read {name!r}")
        return object.__getattribute__(self, name)
```

It fires on every successful read too, which makes it slow and trivially recursive. If you find yourself reaching for it, you almost certainly want `__getattr__` or a descriptor (Part 9).

---

# Part 9 — Being a descriptor: `__get__`, `__set__`, `__delete__`, `__set_name__`

A **descriptor** is an object that, when found on a class, intercepts attribute access on instances of that class. It's the machinery behind `property`, `classmethod`, `staticmethod`, `functools.cached_property`, `__slots__` members, and every plain method's `self` binding.

| Dunder | Fires on | Signature |
|---|---|---|
| `__get__` | `obj.attr` | `(self, obj, objtype=None)` |
| `__set__` | `obj.attr = v` | `(self, obj, value)` |
| `__delete__` | `del obj.attr` | `(self, obj)` |
| `__set_name__` | class creation | `(self, owner, name)` |

Having `__set__` (or `__delete__`) makes it a **data descriptor**, which outranks the instance dictionary. Having only `__get__` makes it a **non-data descriptor**, which loses to the instance dictionary — that asymmetry is exactly why `cached_property` can cache into the instance and then get out of the way.

## 9.1 `__set_name__` — how a descriptor learns its own name

```python
class Field:
    def __set_name__(self, owner, name):
        print(f"__set_name__: I am {name!r} on {owner.__name__}")
        self.name = name
    def __get__(self, obj, objtype=None):
        if obj is None: return self          # accessed on the class
        return obj.__dict__.get(self.name)
    def __set__(self, obj, v):
        obj.__dict__[self.name] = v

class Model:
    title = Field()
    body = Field()
# __set_name__: I am 'title' on Model
# __set_name__: I am 'body' on Model

m = Model(); m.title = "hi"
m.title                 # 'hi'
vars(m)                 # {'title': 'hi'}       ← stored in the instance
type(Model.title)       # <class 'Field'>       ← the `obj is None` branch
```

Python calls `__set_name__` on every descriptor in the class body, automatically, at class creation. Before it existed you had to write `title = Field("title")` and keep the two in sync.

That `if obj is None: return self` line is standard boilerplate: it makes `Model.title` return the descriptor itself rather than exploding, which is what `help()`, IDEs, and introspection expect.

## 9.2 A validating descriptor — the real payoff

```python
class Positive:
    def __set_name__(self, owner, name):
        self._n = "_" + name
    def __get__(self, obj, objtype=None):
        if obj is None: return self
        return getattr(obj, self._n)
    def __set__(self, obj, v):
        if v <= 0:
            raise ValueError(f"{self._n[1:]} must be positive")
        setattr(obj, self._n, v)
    def __delete__(self, obj):
        delattr(obj, self._n)

class Box:
    w = Positive()
    h = Positive()
    def __init__(self, w, h): self.w, self.h = w, h

bx = Box(2, 3)
bx.w                    # 2
vars(bx)                # {'_w': 2, '_h': 3}
bx.w = -1               # ValueError: w must be positive
```

Two properties would do this too — but they'd be two nearly identical eight-line blocks. **A descriptor is a property you can reuse.** That is the entire reason to write one: the same validation, unit conversion, or type coercion applied to many attributes across many classes.

---

# Part 10 — Lifecycle: `__new__`, `__init__`, `__del__`, `__init_subclass__`

## 10.1 `__new__` makes it; `__init__` fills it in

```python
class Loud:
    def __new__(cls, *a, **k):
        print("__new__ (making the object)", a)
        return super().__new__(cls)
    def __init__(self, x):
        print("__init__ (filling it in)", x)
        self.x = x

Loud(5)
# __new__ (making the object) (5,)
# __init__ (filling it in) 5
```

`Cls(5)` runs `Cls.__new__(Cls, 5)`, then — **only if the result is an instance of `Cls`** — `result.__init__(5)`.

```python
class Weird:
    def __new__(cls): return "not an instance"
    def __init__(self): print("never runs")

Weird()                 # 'not an instance'      — and __init__ was skipped
```

`__new__` is an implicit `staticmethod` taking `cls` first. You rarely need it. The three cases where you genuinely do:

**Subclassing an immutable type** — by the time `__init__` runs, the value is already fixed:

```python
class Upper(str):
    def __new__(cls, v): return super().__new__(cls, v.upper())

Upper("hi")             # 'HI'
type(Upper("hi"))       # <class 'Upper'>
```

**Controlling identity** — caching, interning, singletons:

```python
class Singleton:
    _me = None
    def __new__(cls):
        if cls._me is None:
            cls._me = super().__new__(cls)
        return cls._me

Singleton() is Singleton()      # True
```

Note the wrinkle: `__init__` still runs *every* time here, on the same object. If that matters, guard it — or put the logic in a metaclass's `__call__` (essay 05), which is the cleaner place for it.

**Returning a different subclass** — a factory that dispatches on its arguments.

## 10.2 `__del__` — not a destructor

```python
class Res:
    def __init__(self, n): self.n = n
    def __del__(self): print(f"__del__ {self.n}")

r = Res("a"); del r     # __del__ a
```

`del r` removes a *name*, and `__del__` runs when the last reference goes. Which means: it may run late, it may run at interpreter shutdown when globals are already `None`, it may never run at all (reference cycles, `os._exit`), and exceptions inside it are printed and swallowed.

> **Never use `__del__` to release a resource. Use `__enter__`/`__exit__`, or `contextlib.closing`, or an explicit `close()`.** `__del__` is a last-ditch safety net at best.

## 10.3 `__init_subclass__` — a hook that fires for your children

```python
class Base:
    registry = {}
    def __init_subclass__(cls, /, key=None, **kw):
        super().__init_subclass__(**kw)
        Base.registry[key or cls.__name__] = cls

class A(Base, key="a"): pass
class B(Base): pass

Base.registry           # {'a': <class 'A'>, 'B': <class 'B'>}
```

It runs once per subclass, at class-creation time, and can accept keyword arguments written in the `class` line. It is implicitly a `classmethod`; always call `super().__init_subclass__(**kw)` so cooperative hooks upstream still fire.

**This is the tool that replaced 90% of metaclasses.** Registration, validation of required methods, injecting defaults, plugin discovery — all of it. Essay 05 makes the full comparison, but the short version: if `__init_subclass__` can do it, don't write a metaclass.

```python
class Validating:
    def __init_subclass__(cls, **kw):
        super().__init_subclass__(**kw)
        if not hasattr(cls, "handle"):
            raise TypeError(f"{cls.__name__} must define handle()")

class Missing(Validating): pass
# TypeError: Missing must define handle()      ← at import time, not at call time
```

---

# Part 11 — Context managers: `__enter__` and `__exit__`

```python
class Tx:
    def __enter__(self):
        print("BEGIN")
        return self                          # ← this is what `as x` binds
    def __exit__(self, exc_type, exc, tb):
        if exc_type is ValueError:
            print("swallowed")
            return True                      # ← truthy SUPPRESSES the exception
        print("COMMIT/ROLLBACK")
        return False
```

```python
with Tx() as t:
    pass
# BEGIN
# COMMIT/ROLLBACK

with Tx():
    raise ValueError("oops")
# BEGIN
# swallowed
                                            # ...and execution continues

with Tx():
    raise KeyError("k")
# BEGIN
# COMMIT/ROLLBACK
# KeyError: 'k'                             — propagated
```

The rewrite:

```
   with EXPR as name:          mgr = EXPR
       BODY              →     name = type(mgr).__enter__(mgr)
                               try:     BODY
                               finally: type(mgr).__exit__(mgr, *sys.exc_info())
```

Three things to get right:

- **`__enter__` returns what `as` binds.** Usually `self`, but it can be anything — a cursor, a file handle, a temp directory path.
- **`__exit__` receives three arguments**, all `None` when the body completed normally.
- **Return `False` (or nothing) unless you deliberately mean to swallow.** A bare `return True` is a black hole:

```python
class Oops:
    def __enter__(self): return self
    def __exit__(self, *a): return True     # swallows EVERYTHING

with Oops():
    raise RuntimeError("this vanishes")
# ...and we get here. Silently.
```

## 11.1 The shortcut

For anything without other methods, `@contextmanager` is shorter and harder to get wrong:

```python
from contextlib import contextmanager

@contextmanager
def tx():
    print("BEGIN")
    try:
        yield "handle"
    finally:
        print("END")

with tx() as h:
    print("body:", h)
# BEGIN
# body: handle
# END
```

The code before `yield` is `__enter__`, the value yielded is what `as` binds, and the `finally` is `__exit__`. To suppress an exception here you catch it around the `yield` and don't re-raise.

---

# Part 12 — Async: the five `a`-dunders

Each one is the async twin of a synchronous dunder.

| Syntax | Dunder | Sync twin |
|---|---|---|
| `await x` | `__await__` | — |
| `async with x` | `__aenter__` / `__aexit__` | `__enter__` / `__exit__` |
| `async for i in x` | `__aiter__` / `__anext__` | `__iter__` / `__next__` |

```python
import asyncio

class AsyncPool:
    async def __aenter__(self):
        print("__aenter__"); return self
    async def __aexit__(self, et, e, tb):
        print("__aexit__", et.__name__ if et else None); return False

class Ticker:
    def __init__(self, n): self.n = n
    def __aiter__(self): return self             # note: NOT async
    async def __anext__(self):                   # note: async
        if self.n <= 0: raise StopAsyncIteration
        self.n -= 1
        return self.n

async def main():
    async with AsyncPool():
        async for i in Ticker(3):
            print("tick", i)

asyncio.run(main())
# __aenter__
# tick 2
# tick 1
# tick 0
# __aexit__ None
```

Two details worth pinning down:

- **`__aiter__` is a plain method**, not `async`. It returns the async iterator directly. Only `__anext__` is `async`.
- **The sentinel is `StopAsyncIteration`**, not `StopIteration`.

`__await__` is the lowest-level one: it must return an *iterator*, and you will essentially never write it by hand — an `async def` function already produces an awaitable. Implement it only when you're bridging some other object into `await`.

An async generator makes `__aiter__`/`__anext__` unnecessary, the same way a generator does for the sync pair:

```python
class Ticker:
    def __init__(self, n): self.n = n
    async def __aiter__(self):          # an async generator
        for i in range(self.n, 0, -1):
            yield i
```

---

# Part 13 — Copying and pickling

| Syntax | Dunder |
|---|---|
| `copy.copy(x)` | `__copy__` |
| `copy.deepcopy(x)` | `__deepcopy__(self, memo)` |
| `pickle.dumps(x)` | `__getstate__`, then `__reduce__`/`__reduce_ex__` |
| `pickle.loads(...)` | `__setstate__` |

```python
import copy

class Node:
    def __init__(self, v): self.v = v; self.cache = {"big": 1}
    def __repr__(self): return f"Node({self.v})"
    def __copy__(self):
        return Node(self.v)                          # drop the cache
    def __deepcopy__(self, memo):
        return Node(copy.deepcopy(self.v, memo))     # pass memo along!

copy.copy(Node([1, 2]))         # Node([1, 2])
copy.deepcopy(Node([1, 2]))     # Node([1, 2])
```

That `memo` dict is how `deepcopy` handles cycles. **Always thread it through** to nested `deepcopy` calls, or a self-referential structure will recurse forever.

`__getstate__`/`__setstate__` are the pair you'll actually use — for objects holding something unpicklable:

```python
class Conn:
    def __init__(self, host):
        self.host = host
        self.socket = open_socket()
    def __getstate__(self):
        s = self.__dict__.copy()
        del s["socket"]                  # sockets don't pickle
        return s
    def __setstate__(self, state):
        self.__dict__.update(state)
        self.socket = open_socket()      # reopen on the far side

import pickle
c = pickle.loads(pickle.dumps(Conn("h")))
c.host                  # 'h'
c.socket                # a fresh socket
```

Note that `__setstate__` receives the state directly — `__init__` is **not** called during unpickling.

`__reduce__` is the general escape hatch when even that isn't enough. It's rarely the right answer; prefer `__getstate__`/`__setstate__`.

---

# Part 14 — Talking to the type system

## 14.1 `__match_args__` — structural pattern matching

`case Cls(a, b)` needs to know which attributes the *positional* patterns refer to. `__match_args__` says.

```python
@dataclass
class Pt:
    x: int
    y: int

Pt.__match_args__       # ('x', 'y')     ← dataclass generates it

def where(p):
    match p:
        case Pt(0, 0):        return "origin"
        case Pt(x, 0):        return f"on x at {x}"
        case Pt(x=0, y=y):    return f"on y at {y}"
        case Pt():            return "somewhere"

where(Pt(0,0)), where(Pt(5,0)), where(Pt(0,7)), where(Pt(1,1))
# ('origin', 'on x at 5', 'on y at 7', 'somewhere')
```

By hand it's a plain class attribute — a tuple of attribute names:

```python
class Manual:
    __match_args__ = ("a", "b")
    def __init__(self, a, b): self.a, self.b = a, b

match Manual(1, 2):
    case Manual(p, q): ...      # p=1, q=2
```

**Keyword patterns (`case Pt(x=0)`) work without it** — they just look up attributes. `__match_args__` is only needed for positional patterns. `@dataclass` and `NamedTuple` generate it for free, which is one more reason to use them.

## 14.2 `__class_getitem__` — making `MyClass[int]` legal

```python
class Stack:
    def __class_getitem__(cls, item):
        return f"Stack of {item}"

Stack[int]              # 'Stack of <class 'int'>'
```

This is what makes `list[int]` work. In your own code you almost never write it — `class Stack[T]:` (PEP 695, 3.12) generates a correct one for you. Recognise it, don't hand-roll it.

## 14.3 `__instancecheck__` and `__subclasshook__`

`isinstance(x, C)` → `type(C).__instancecheck__(C, x)`. Note the `type(C)` — customising it means writing a **metaclass**, which is essay 05's subject.

The one you can use without a metaclass is `__subclasshook__` on an ABC, which makes `issubclass` structural:

```python
from abc import ABC

class Quacky(ABC):
    @classmethod
    def __subclasshook__(cls, C):
        if cls is Quacky:
            return any("quack" in B.__dict__ for B in C.__mro__)
        return NotImplemented

class Duck:
    def quack(self): pass
class Dog: pass

issubclass(Duck, Quacky)        # True    — never declared any relationship
issubclass(Dog, Quacky)         # False
isinstance(Duck(), Quacky)      # True
```

This is exactly how `isinstance(x, collections.abc.Iterable)` works. For type-checker-visible structural typing, `typing.Protocol` is the modern answer; `__subclasshook__` is the runtime one.

---

# Part 15 — The traps

## 15.1 Patching a dunder onto an instance

*(Fact 2.)* `x.__len__ = ...` does nothing for `len(x)`. Dunders live on the class.

## 15.2 Defining `__eq__` and forgetting `__hash__`

*(3.2.)* Your object silently becomes unhashable. Use `@dataclass(frozen=True)`, or write both.

## 15.3 Returning `False` instead of `NotImplemented`

*(3.1, 6.2.)* You've told Python "definitively not equal / can't be added", when what you meant was "not my type". The other operand never gets its turn.

```python
def __eq__(self, o):
    if not isinstance(o, V): return False            # ✗ blocks the other side
    if not isinstance(o, V): return NotImplemented   # ✓
```

## 15.4 `__iter__` returning `self` on a reusable collection

*(5.2.)* The second `for` loop silently iterates nothing.

## 15.5 `__exit__` returning a truthy value

*(Part 11.)* You've built an exception black hole. Return `False`, or nothing at all.

## 15.6 Forgetting to return `self` from `__iadd__`

`a += b` rebinds `a` to whatever `__iadd__` returned. Return `None` and your variable becomes `None`.

## 15.7 Infinite recursion in `__setattr__` / `__getattribute__`

*(8.2.)* Inside them, use `object.__setattr__(self, ...)` / `object.__getattribute__(self, ...)`, never `self.x = ...`.

## 15.8 Using `__del__` for cleanup

*(10.2.)* Non-deterministic, skippable, and it swallows exceptions. Use a context manager.

## 15.9 Expecting `bool()` to notice your empty container

*(3.5.)* Without `__len__` or `__bool__`, every instance is truthy forever.

## 15.10 `__missing__` on a non-dict

*(4.3.)* Only `dict` subclasses consult it. On a plain class it is dead code.

## 15.11 `NotImplemented` vs `NotImplementedError`

The first is a value you *return* from a binary dunder. The second is an exception you *raise* from an unfinished method. Returning `NotImplementedError` (the class) is truthy and will quietly poison a comparison.

## 15.12 Writing `__str__` but not `__repr__`

Backwards. `__repr__` falls back nowhere useful; `__str__` falls back to `__repr__`. Write `__repr__` first, and `__str__` only if it differs.

---

# Part 16 — The whole thing on one page

## Every dunder, by what it makes possible

**Showing up**

| Syntax | Dunder |
|---|---|
| `repr(x)`, REPL, containers, `!r` | `__repr__` |
| `str(x)`, `print(x)`, f-string, `!s` | `__str__` → `__repr__` |
| `f"{x:spec}"`, `format(x, spec)` | `__format__` |
| `bytes(x)` | `__bytes__` |

**Being a value**

| Syntax | Dunder |
|---|---|
| `x == y` | `__eq__` |
| `x != y` | `__ne__` → `not __eq__` |
| `hash(x)`, dict key, set member | `__hash__` (set to `None` if you define `__eq__`) |
| `x < y`, `<=`, `>`, `>=` | `__lt__`, `__le__`, `__gt__`, `__ge__` |
| `bool(x)`, `if x`, `not x` | `__bool__` → `__len__ != 0` → `True` |

**Being a container**

| Syntax | Dunder |
|---|---|
| `len(x)` | `__len__` |
| `x[k]` (incl. slices and tuples) | `__getitem__` |
| `x[k] = v` | `__setitem__` |
| `del x[k]` | `__delitem__` |
| `k in x` | `__contains__` → iterate → `__getitem__` scan |
| `reversed(x)` | `__reversed__` → `__len__` + `__getitem__` |
| missing dict key | `__missing__` (`dict` subclasses only) |

**Being iterable**

| Syntax | Dunder |
|---|---|
| `for i in x`, `iter(x)`, unpacking, `list(x)` | `__iter__` → `__getitem__` from 0 |
| `next(it)` | `__next__` (raise `StopIteration` to finish) |

**Operators** — each has `__op__`, `__rop__`, `__iop__`

| | |
|---|---|
| `+ - * / // % ** @` | `add sub mul truediv floordiv mod pow matmul` |
| `<< >> & \| ^` | `lshift rshift and or xor` |
| `- + ~ abs()` | `__neg__ __pos__ __invert__ __abs__` |
| `divmod()`, `pow(a,b,m)` | `__divmod__`, `__pow__(self, b, mod=None)` |

**Conversion**

| Syntax | Dunder |
|---|---|
| `int(x)` / `float(x)` / `complex(x)` | `__int__` / `__float__` / `__complex__` |
| index, slice, `hex`, `range` | `__index__` (lossless int) |
| `round`, `trunc`, `floor`, `ceil` | `__round__`, `__trunc__`, `__floor__`, `__ceil__` |

**Calling and attributes**

| Syntax | Dunder |
|---|---|
| `x(...)` | `__call__` |
| `x.name` (failed lookup only) | `__getattr__` |
| `x.name` (every read) | `__getattribute__` |
| `x.name = v` | `__setattr__` |
| `del x.name` | `__delattr__` |
| `dir(x)` | `__dir__` |

**Descriptors**

| Fires on | Dunder |
|---|---|
| `obj.attr` where attr is on the class | `__get__(self, obj, objtype)` |
| `obj.attr = v` | `__set__(self, obj, value)` |
| `del obj.attr` | `__delete__(self, obj)` |
| class creation | `__set_name__(self, owner, name)` |

**Lifecycle**

| Moment | Dunder |
|---|---|
| allocate | `__new__(cls, ...)` |
| initialise | `__init__(self, ...)` |
| last reference gone | `__del__` (don't rely on it) |
| a subclass is created | `__init_subclass__(cls, **kw)` |
| the class body is being run | `__prepare__` (metaclass — essay 05) |

**Context and async**

| Syntax | Dunder |
|---|---|
| `with x` | `__enter__`, `__exit__(et, e, tb)` |
| `async with x` | `__aenter__`, `__aexit__` |
| `async for i in x` | `__aiter__`, `__anext__` (`StopAsyncIteration`) |
| `await x` | `__await__` |

**Serialising**

| Syntax | Dunder |
|---|---|
| `copy.copy` | `__copy__` |
| `copy.deepcopy` | `__deepcopy__(self, memo)` |
| pickling | `__getstate__`, `__setstate__`, `__reduce__` |

**Type system**

| Syntax | Dunder |
|---|---|
| `case Cls(a, b)` | `__match_args__` (a tuple, not a method) |
| `Cls[int]` | `__class_getitem__` |
| `isinstance(x, C)` | `__instancecheck__` (on the metaclass) |
| `issubclass(S, C)` | `__subclasscheck__`, `__subclasshook__` |

## The fallback chains, collected

```
   bool(x)      →  __bool__  →  __len__() != 0  →  True
   str(x)       →  __str__   →  __repr__        →  <Cls object at 0x…>
   format(x,"") →  __format__ →  __str__
   iter(x)      →  __iter__  →  __getitem__(0,1,2…) until IndexError  →  TypeError
   k in x       →  __contains__ →  iterate and compare  →  TypeError
   x != y       →  __ne__    →  not __eq__      →  identity
   reversed(x)  →  __reversed__ → __len__ + __getitem__ →  TypeError
   a + b        →  a.__add__ →  b.__radd__      →  TypeError
   a += b       →  a.__iadd__ →  a = a + b
   a < b        →  a.__lt__  →  b.__gt__        →  TypeError
```

## Which ones to write, in order of value

1. **`__repr__`** — always. Nothing else pays back as fast.
2. **`__eq__` + `__hash__`** — the moment your object is a value. Or just `@dataclass(frozen=True)`.
3. **`__len__`** — the moment it can be empty. `bool()` comes free.
4. **`__iter__`** — the moment it holds several things.
5. **`__getitem__`** — the moment lookup by key or position makes sense.
6. **`__enter__`/`__exit__`** — the moment it owns something that must be released.
7. Everything else — when the syntax genuinely reads better than a method call.

> **The bar for the rest: would `a + b` be clearer than `a.combine(b)` to someone who has never seen this class? If not, write the method.**

---

# Part 17 — When it surprises you, ask three questions

1. **"What does this syntax rewrite to?"** Look it up in Part 16 and say the rewritten form out loud. `len(x)` is `type(x).__len__(x)` — half the confusion evaporates at that step.

2. **"Is it on the TYPE?"** Check `hasattr(type(x), '__the_dunder__')`, not `hasattr(x, ...)`. And check the whole MRO — a parent may have set `__hash__ = None` for you.

3. **"Which fallback did I land in?"** A dunder you didn't write is not absent — it has a default. `bool()` defaults to `True`, `__str__` defaults to `__repr__`, `in` defaults to a linear scan. The surprising behaviour is usually a fallback working exactly as documented.

And the universal move: **`type(x).__mro__` and `vars(type(x))`.** Stop guessing which dunder is in play; look at the class.

---

# Part 18 — Real code, using all of it

A small immutable money type and a mutable ledger — between them they use most of what's above, and nothing is there for decoration.

```python
from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass, field
from functools import total_ordering


@total_ordering
@dataclass(frozen=True, slots=True)
class Money:
    """A value. Frozen gives __eq__ + __hash__; total_ordering gives the rest."""
    cents: int
    currency: str = "USD"

    # --- showing up ---
    def __repr__(self) -> str:
        return f"Money({self.cents}, {self.currency!r})"

    def __str__(self) -> str:
        return f"{self.cents / 100:,.2f} {self.currency}"

    def __format__(self, spec: str) -> str:
        return str(self) if spec == "" else format(self.cents / 100, spec)

    # --- ordering (frozen dataclass already wrote __eq__ and __hash__) ---
    def __lt__(self, other: object) -> bool:
        if not isinstance(other, Money) or other.currency != self.currency:
            return NotImplemented
        return self.cents < other.cents

    # --- arithmetic ---
    def __add__(self, other: object) -> Money:
        if not isinstance(other, Money) or other.currency != self.currency:
            return NotImplemented
        return Money(self.cents + other.cents, self.currency)

    def __sub__(self, other: object) -> Money:
        if not isinstance(other, Money) or other.currency != self.currency:
            return NotImplemented
        return Money(self.cents - other.cents, self.currency)

    def __mul__(self, k: int | float) -> Money:
        if not isinstance(k, (int, float)):
            return NotImplemented
        return Money(round(self.cents * k), self.currency)

    __rmul__ = __mul__                       # 3 * money reads fine too

    def __neg__(self) -> Money:              return Money(-self.cents, self.currency)
    def __abs__(self) -> Money:              return Money(abs(self.cents), self.currency)
    def __bool__(self) -> bool:              return self.cents != 0
    def __round__(self, nd: int = 0) -> Money:
        step = 10 ** (2 - nd)
        return Money(round(self.cents / step) * step, self.currency)


@dataclass
class Ledger:
    """A mutable collection. Container + iteration + context management."""
    currency: str = "USD"
    _entries: list[tuple[str, Money]] = field(default_factory=list, repr=False)

    # --- container ---
    def __len__(self) -> int:                       return len(self._entries)
    def __getitem__(self, i: int | slice):          return self._entries[i]
    def __iter__(self) -> Iterator[tuple[str, Money]]:
        return iter(self._entries)                  # fresh iterator every time
    def __contains__(self, label: object) -> bool:
        return any(lbl == label for lbl, _ in self._entries)
    def __reversed__(self):                         return reversed(self._entries)

    # --- accumulate ---
    def __iadd__(self, entry: tuple[str, Money]) -> "Ledger":
        label, amount = entry
        if amount.currency != self.currency:
            raise ValueError(f"expected {self.currency}, got {amount.currency}")
        self._entries.append((label, amount))
        return self                                 # ← required

    # --- read as data ---
    @property
    def total(self) -> Money:
        out = Money(0, self.currency)
        for _, amount in self._entries:
            out += amount
        return out

    def __repr__(self) -> str:
        return f"Ledger({self.currency!r}, {len(self)} entries, total={self.total})"

    # --- transaction scope ---
    def __enter__(self) -> "Ledger":
        self._checkpoint = len(self._entries)
        return self

    def __exit__(self, exc_type, exc, tb) -> bool:
        if exc_type is not None:
            del self._entries[self._checkpoint:]    # roll back
        return False                                # never swallow
```

Using it:

```python
a, b = Money(1050), Money(299)

repr(a)                 # "Money(1050, 'USD')"
str(a)                  # '10.50 USD'
f"{a}"                  # '10.50 USD'
f"{a:>10,.2f}"          # '     10.50'
a + b                   # Money(1349, 'USD')
a - b                   # Money(751, 'USD')
2 * b                   # Money(598, 'USD')
-a                      # Money(-1050, 'USD')
a > b                   # True
sorted([a, b])          # [Money(299, 'USD'), Money(1050, 'USD')]
bool(Money(0))          # False
{a, Money(1050)}        # {Money(1050, 'USD')}      — deduplicated by value
a + Money(1, "EUR")     # TypeError: unsupported operand type(s) for +: 'Money' and 'Money'

led = Ledger()
led += ("coffee", Money(450))
led += ("book", Money(1899))
len(led)                # 2
"coffee" in led         # True
led.total               # Money(2349, 'USD')
led                     # Ledger('USD', 2 entries, total=23.49 USD)
[lbl for lbl, _ in led] # ['coffee', 'book']

try:
    with led:
        led += ("lunch", Money(1200))
        raise RuntimeError("card declined")
except RuntimeError:
    pass
len(led)                # 2       ← rolled back
```

Read it and notice what isn't there. No `__getattr__`, no `__new__`, no metaclass, no `__del__`. Each dunder present is answering a piece of syntax that genuinely reads better than a method would — `a + b` beats `a.plus(b)`, `"coffee" in led` beats `led.has_label("coffee")`, and `with led:` beats a try/except pair the caller has to remember.

That last line of `Money.__add__` is the essay in miniature: the cross-currency `TypeError` was never written by hand. Returning `NotImplemented` let Python produce it, with the right message, for free.

---

# Appendix

## A. The complete list, alphabetically

Grouped by section above; here as a checklist you can scan.

```
__abs__          __add__          __aenter__       __aexit__        __aiter__
__and__          __anext__        __await__        __bool__         __bytes__
__call__         __ceil__         __class_getitem__ __complex__     __contains__
__copy__         __deepcopy__     __del__          __delattr__      __delete__
__delitem__      __dir__          __divmod__       __enter__        __eq__
__exit__         __float__        __floor__        __floordiv__     __format__
__ge__           __get__          __getattr__      __getattribute__ __getitem__
__getstate__     __gt__           __hash__         __iadd__         __iand__
__ifloordiv__    __ilshift__      __imatmul__      __imod__         __imul__
__index__        __init__         __init_subclass__ __instancecheck__
__int__          __invert__       __ior__          __ipow__         __irshift__
__isub__         __iter__         __itruediv__     __ixor__         __le__
__len__          __lshift__       __lt__           __matmul__       __missing__
__mod__          __mro_entries__  __mul__          __ne__           __neg__
__new__          __next__         __or__           __pos__          __pow__
__prepare__      __radd__         __rand__         __rdivmod__      __reduce__
__repr__         __reversed__     __rfloordiv__    __rlshift__      __rmatmul__
__rmod__         __rmul__         __ror__          __round__        __rpow__
__rrshift__      __rshift__       __rsub__         __rtruediv__     __rxor__
__set__          __set_name__     __setattr__      __setitem__      __setstate__
__sizeof__       __str__          __sub__          __subclasscheck__
__subclasshook__ __truediv__      __trunc__        __xor__
```

Plus the *attributes* that are dunders but not methods: `__dict__`, `__slots__`, `__class__`, `__bases__`, `__mro__`, `__name__`, `__qualname__`, `__module__`, `__doc__`, `__annotations__`, `__match_args__`, `__abstractmethods__`, `__all__` (module level).

## B. Ones you should almost never write

| Dunder | Why not | Instead |
|---|---|---|
| `__getattribute__` | fires on every read; trivially recursive | `__getattr__`, or a descriptor |
| `__del__` | non-deterministic, swallows exceptions | `__enter__`/`__exit__` |
| `__reduce__` | very easy to get subtly wrong | `__getstate__`/`__setstate__` |
| `__await__` | hand-writing the coroutine protocol | `async def` |
| `__ne__` | derived from `__eq__` already | nothing |
| `__class_getitem__` | PEP 695 generates it | `class C[T]:` |
| `__prepare__`, `__instancecheck__` | needs a metaclass | see essay 05 |

## C. Where dunders come from for free

You often don't need to write these at all:

| Give it | And you get |
|---|---|
| `@dataclass` | `__init__`, `__repr__`, `__eq__`, `__match_args__` |
| `@dataclass(frozen=True)` | …plus `__hash__`, `__setattr__`, `__delattr__` |
| `@dataclass(order=True)` | …plus `__lt__ __le__ __gt__ __ge__` |
| `@dataclass(slots=True)` | `__slots__` and its member descriptors |
| `@total_ordering` | the other three ordering dunders |
| `NamedTuple` | the whole tuple protocol, `__match_args__` |
| `Enum` | `__iter__`, `__len__`, `__contains__`, `__getitem__` on the class |
| `Sequence` / `Mapping` ABCs | `__contains__`, `__iter__`, `__reversed__`, `index`, `count`, `keys`, `items`, `get`, … |
| `@contextmanager` | `__enter__`, `__exit__` |
| `@functools.cache` | memoisation without touching `__hash__` |

**Reach for these before writing dunders by hand.** Every one of them is more correct than the version you'd type at 5pm.

## D. What landed when

| Version | Dunders |
|---|---|
| 3.5 | `__matmul__`, `__await__`, `__aiter__`, `__anext__`, `__aenter__`, `__aexit__` |
| 3.6 | `__set_name__`, `__init_subclass__`, `__fspath__` |
| 3.7 | `__class_getitem__`, module-level `__getattr__`/`__dir__` |
| 3.8 | `__index__` required for `__len__`-like slots; `functools.cached_property` |
| 3.10 | `__match_args__` (structural pattern matching) |
| 3.11 | `__getstate__` gains a useful default on `object` |
| **3.12** | **PEP 695 generates `__class_getitem__`; `@override`** |

---

# The one thing to remember

> ## **Every operator, builtin, and statement is a rewrite into `type(obj).__name__(obj, …)`. A dunder is you writing the right-hand side.**
>
> **The name is fixed — you fill it in, you never invent it. The lookup is on the TYPE, never the instance. And a dunder you didn't write isn't missing: it has a documented fallback, and that fallback is usually what surprised you.**
>
> **Return `NotImplemented`, not `False`, when a binary operation isn't yours to answer. Write `__repr__` first, always. And check whether `@dataclass`, an ABC, or `@contextmanager` has already written the ones you were about to.**

That sentence is the entire system. Say the rewrite out loud with your real class and the answer falls out.

And on the days a dunder does nothing at all: **you put it on the instance. Move it to the class.**
