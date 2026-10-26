# Never Be Unsure About a Python Type Again

*Modern Python — 3.12 and later. Every old spelling you've seen on Stack Overflow is listed in the appendix so you can recognise it and never write it.*

There is **one** mental model in this essay. Not one for containers and another for generics, not a special case for `Optional`. One.

Learn it in Part 1, then watch it explain every annotation you will ever write — unions, containers, narrowing, generics, protocols, variance. Same model every time.

---

# Part 1 — The mental model: a label on a box

A variable is a **box** that holds a value. An annotation is a **label** you stick on the box.

```
   ┌─────────────────────┐
   │  label:   int       │   ← which values are ALLOWED in here
   ├─────────────────────┤
   │  value:   42        │   ← which value is ACTUALLY in here
   └─────────────────────┘
```

And the label means exactly one thing:

> ## **A type is the SET of values allowed in that slot.**

`int` is the set of all integers. `str` is the set of all strings. `None` is a set with exactly one member. `MyClass` is the set of its instances. That's not a metaphor for what types are — it *is* what they are, and every single construct in the type system is one of three moves:

| Move | What it does | Examples |
|---|---|---|
| **NAME** a set | point at a set of values | `int`, `str`, `None`, `Literal["red"]`, `User` |
| **COMBINE** sets | build a bigger or structured set | `int \| None`, `list[int]`, `dict[str, int]` |
| **SHRINK** a set | prove you're in a smaller part of it | `isinstance`, `is None`, `assert`, `match` |

Three moves. Say it out loud when you're stuck:

> ## **"What set does this slot allow? What set does my value belong to? Does mine fit inside?"**

## The rule that decides everything

```
   slot allows:   ██████████████████   (a set)
   value is in:      ██████            (a smaller set)   →  ✓ FITS

   slot allows:      ██████
   value is in:   ██████████████████                     →  ✗ TOO BIG
```

> ### **A value fits a slot when its set is a SUBSET of the slot's set.**

That single rule replaces every other rule you've been told. Subclass? A subclass's instances are a *subset* of the parent's — that's why it fits. `int` where `int | str` is asked? Subset. `list[Dog]` where `list[Animal]` is asked? **Not** a subset, and Part 5.4 shows you exactly why.

## Python does not read the labels

This is the fact that makes typing safe to learn, because **you cannot break your program by getting a type wrong.**

```python
def double(x: int) -> int:
    return "not an int at all"

double("hello")          # runs. returns 'not an int at all'. no error. ever.
```

Annotations are **not** checked at runtime. They are read by two audiences, neither of which is the interpreter:

```
                ┌──────────────────────────────────────┐
   your code ──→│  Python interpreter — ignores labels │──→ it just runs
                └──────────────────────────────────────┘
                ┌──────────────────────────────────────┐
             ──→│  type checker (mypy / pyright)       │──→ errors before you run
                └──────────────────────────────────────┘
                ┌──────────────────────────────────────┐
             ──→│  the human reading it in six months  │──→ the real payoff
                └──────────────────────────────────────┘
```

So annotations are a **contract, not a guard**. Adding them can never crash working code, and removing them can never fix a bug. If you want values checked at runtime, that's a *library's* job (`pydantic`, `attrs`) — the type system's job is to catch mistakes before the program ever runs.

Two consequences worth internalising now:

- **You can add types to one function today and nothing else.** Gradual is the intended way. There is no all-or-nothing.
- **A type error is a message, not a failure.** The program still runs. You get to decide whether the checker is right.

## Where labels go

Four places, and the syntax is the same everywhere — `name: type`.

```python
count: int = 0                          # 1. a variable

def greet(name: str, times: int = 1) -> str:      # 2. parameters   3. the return
    return f"hi {name}" * times

class User:
    id: int                             # 4. an attribute
    name: str = "anon"
```

A return of nothing is spelled `-> None`:

```python
def log(msg: str) -> None:
    print(msg)
```

`-> None` is not optional politeness — for most checkers, a function with **no** return annotation is unchecked entirely. Annotating the return is what turns the checker on for that function.

## You need a checker to get anything back

Types with no checker are just comments. Pick one and let your editor run it:

- **pyright** — what VS Code's Pylance runs. Fast, strict, immediate red squiggles. The best way to *learn*, because it answers instantly.
- **mypy** — the original, the one most CI pipelines run.
- **ty** / **pyrefly** — newer, much faster, still maturing. Fine to watch, not yet where to start.

One command to try right now in any project:

```bash
pip install mypy && mypy yourfile.py
```

And the single most useful debugging tool in the whole system:

```python
reveal_type(x)      # the checker prints what it thinks x is, right there
```

No import needed — checkers understand it specially. Use it constantly while you're learning; it turns "I think this is a `str`" into a fact.

That's the model. Now we just apply it.

---

# Part 2 — Naming a set

The atoms. Each one names a set of values, nothing more.

## 2.1 The everyday ones

```python
n: int = 3
f: float = 3.5
s: str = "hi"
b: bool = True
by: bytes = b"raw"
nothing: None = None
```

`None` is a type whose set has exactly **one** member — the value `None`. That's why `x: None` is legal and useless on its own, but `int | None` is one of the most common annotations in Python.

## 2.2 Your own classes are sets too

```python
class User: ...
class Admin(User): ...

u: User = Admin()      # ✓ every Admin IS a User — a subset fits
a: Admin = User()      # ✗ not every User is an Admin
```

Inheritance and the subset rule are the same statement. `Admin ⊂ User`.

## 2.3 Two built-in subset quirks worth knowing once

**`bool` is a subset of `int`.** Genuinely, at runtime — `True` *is* `1`.

```python
def f(x: int) -> None: ...
f(True)                 # ✓ legal, and occasionally surprising
```

**`int` is accepted wherever `float` is asked** (and both wherever `complex` is asked). This one is a deliberate special case in the type system, not real inheritance:

```python
def area(r: float) -> float: return 3.14 * r * r
area(2)                 # ✓ writing `float` means "int or float"
```

So `x: float` is almost always what you want for a number that could be either. **Don't write `int | float`** — it's the same set, spelled longer.

The promotion is **not** inherited by containers, though — see 9.5.

## 2.4 `Literal` — an explicitly tiny set

When only specific *values* are allowed, list them:

```python
from typing import Literal

def align(mode: Literal["left", "right", "center"]) -> None: ...

align("left")           # ✓
align("middle")         # ✗ checker: not one of the three
```

```
   str        ██████████████████████████████    every string
   Literal[…]         ███                       exactly three of them
```

This is one of the highest-value annotations in the language: it turns a runtime `ValueError` into an editor autocomplete. Use it for modes, flags, statuses, and small fixed vocabularies. (For a set of values you also want to *use* as objects, an `Enum` is the heavier, better tool — see 8.5.)

## 2.5 The three special sets

These three are where beginners lose confidence, and the set model sorts them out in one table.

| Type | Its set | Assign anything **to** it? | Do anything **with** it? |
|---|---|---|---|
| `object` | every value | ✓ yes | ✗ no — narrow first |
| `Any` | *checking is switched off* | ✓ yes | ✓ yes — anything at all |
| `Never` | nothing. the empty set | ✗ nothing fits | ✓ anything — it can't happen |

**`object`** is honest: "I hold anything, and I promise nothing."

```python
x: object = "hello"
x.upper()               # ✗ checker: `object` has no `upper` — and it's right
```

To use it, shrink it (Part 4). That's not the checker being annoying; that's it correctly pointing out you don't know what you have.

**`Any`** is the escape hatch: it doesn't mean "every value", it means **"stop checking here."**

```python
x: Any = "hello"
x.upper()               # ✓
x.flurb()               # ✓ too — no complaints, and it will crash at runtime
```

`Any` is a valid tool for genuinely dynamic code and untyped third-party libraries. But it **spreads**: anything you compute from an `Any` becomes `Any`, silently switching off checking downstream. Treat every `Any` as a small debt.

> ### **`object` = "I know nothing, so ask me nothing." `Any` = "don't ask, don't tell."**
> When you're tempted to write `Any`, try `object` first. If the checker complains, it just found a real gap in your reasoning.

**`Never`** is the empty set — the type of a value that cannot exist. You rarely write it; you use it to prove you've handled every case (4.6). A function that never returns normally is `-> Never`:

```python
from typing import Never

def die(msg: str) -> Never:
    raise RuntimeError(msg)
```

## 2.6 The whole ruler

Everything in Part 2 on one line, smallest set to biggest:

```
  Never        Literal["a"]      str            str | int         object      │  Any
  ─────────────────────────────────────────────────────────────────────────   │  ────
  nothing      one value         all strings    strings & ints    everything  │  off
  ◄──── you can do anything with it        you can do less with it ────►      │
```

Note the shape of that: **the smaller the set, the more you can do with the value.** That's the whole trade-off of typing in one line, and it's why `Any` sits outside the ruler entirely — it pretends to be at both ends at once.

---

# Part 3 — Combining sets

Four ways to build a bigger set out of smaller ones.

## 3.1 `|` — this set OR that set

```python
def parse(raw: str) -> int | None:
    return int(raw) if raw.isdigit() else None
```

```
   int | None   =   ████████████ ∪ ▪
                    all ints       None
```

`X | None` is the most common annotation in real Python — "a value, or nothing." You'll also see `Optional[X]`; it is **exactly** the same thing in older spelling (appendix). Use `|`.

Unions can hold as many members as you like, and they flatten:

```python
Scalar = int | float | str | bool | None
```

A union is a promise you'll **shrink it before using it** — which is Part 4, and the reason unions are pleasant rather than annoying.

## 3.2 Containers — a set built from another set

```python
xs: list[int]                     # a list whose items are ints
d:  dict[str, int]                # keys are str, values are int
s:  set[str]
fs: frozenset[bytes]
```

The brackets are not decoration. **`list` alone means `list[Any]`** — a list you've told the checker nothing about, which quietly disables checking on everything you pull out of it. Always parameterise.

```python
def total(xs: list) -> int: ...        # ✗ items are Any — checking is off
def total(xs: list[int]) -> int: ...   # ✓
```

Nesting works exactly as you'd expect, because it's just sets of sets:

```python
grid: list[list[int]]
index: dict[str, list[User]]
lookup: dict[str, dict[str, int | None]]
```

## 3.3 Tuples have two forms, and the difference matters

```python
point: tuple[int, int]              # EXACTLY two ints — position by position
rgb:   tuple[int, int, str]         # exactly three, of those types in that order
row:   tuple[int, ...]              # ANY number of ints — the `...` is literal syntax
empty: tuple[()]                    # the empty tuple
```

```
   tuple[int, str]      →  ( int , str )        fixed length, each slot its own type
   tuple[int, ...]      →  ( int , int , … )    any length, all the same type
```

Use the fixed form for records ("a coordinate"), the `...` form for homogeneous sequences ("however many ids"). Getting this right is what makes tuple unpacking check properly.

## 3.4 Callables — the set of functions with a given shape

```python
from collections.abc import Callable

handler: Callable[[int, str], bool]      # takes (int, str), returns bool
thunk:   Callable[[], None]              # takes nothing, returns nothing
anyf:    Callable[..., int]              # any arguments at all, returns int
```

The reading is: `Callable[[args], return]`. The inner brackets are the argument **list** — they're required even for one argument, and that's the detail people forget.

```python
def apply_twice(f: Callable[[int], int], x: int) -> int:
    return f(f(x))
```

## 3.5 The abstract containers — usually the better choice for parameters

`collections.abc` has the *shapes* rather than the concrete classes:

```python
from collections.abc import Iterable, Sequence, Mapping, Iterator

def total(xs: Iterable[int]) -> int: ...        # anything you can loop over
def first(xs: Sequence[str]) -> str: ...        # indexable and has a length
def lookup(m: Mapping[str, int]) -> int: ...    # readable dict-like
```

Which to use is Part 5, and it's the single change that most improves real codebases.

---

# Part 4 — Shrinking a set (narrowing)

You've built a union. Now you have to use it. **Narrowing** is the checker watching your control flow and shrinking the set as you rule things out.

This is where the type system stops feeling like paperwork and starts feeling like a colleague.

## 4.1 The picture

```python
def show(x: int | str | None) -> str:
    if x is None:
        ...          # here x is  None
    elif isinstance(x, int):
        ...          # here x is  int
    else:
        ...          # here x is  str
```

```
   x: int | str | None
   │
   ├── if x is None          →   None          the checker removed int and str
   ├── elif isinstance(int)  →   int
   └── else                  →   str           by elimination — nothing else is left
```

The checker does this bookkeeping for you, per branch, automatically. You don't annotate anything.

## 4.2 What narrows

| You write | Effect |
|---|---|
| `if x is None:` / `if x is not None:` | splits `None` off a union |
| `if isinstance(x, int):` | narrows to `int` (and to everything else in the `else`) |
| `if isinstance(x, (int, str)):` | narrows to `int \| str` |
| `if x == "left":` on a `Literal` | narrows to that literal |
| `match x: case int(): …` | narrows per case |
| `assert isinstance(x, int)` | narrows for the rest of the block |
| `if callable(x):` | narrows to a callable |
| `if hasattr(x, "foo"):` | narrows (pyright; support varies) |
| `if key in d:` | narrows `TypedDict` optional keys |

One asymmetry that catches people at boundaries. Narrowing **within** a `Literal` union works with plain `==` and `in`. But going the other way — taking an unchecked `str` and proving it's one of your literals — is only narrowed reliably by `match`:

```python
def parse_role(raw: str) -> Literal["admin", "editor", "viewer"]:
    if raw in ("admin", "editor", "viewer"):
        return raw                        # ✗ mypy: still just `str`
    raise ValueError(raw)

def parse_role(raw: str) -> Literal["admin", "editor", "viewer"]:
    match raw:
        case "admin" | "editor" | "viewer":
            return raw                    # ✓ narrowed to the literal
        case _:
            raise ValueError(raw)
```

Checkers differ on how clever they are here. `match` is the form all of them understand, so use it for the "validate what came in off the wire" function — and write that function once, at the edge.

## 4.3 The idiom: rule things out early and return

```python
def name_of(u: User | None) -> str:
    if u is None:
        return "anonymous"
    return u.name            # from here down, u is definitely a User
```

The early return **permanently** narrows the rest of the function. This is why guard clauses read so well in typed Python — you pay for the `None` once, at the top, and the whole body below is clean.

Compare the nested version, which is the same thing wearing more indentation:

```python
def name_of(u: User | None) -> str:
    if u is not None:
        return u.name
    return "anonymous"
```

Both check fine. The first scales; the second grows a pyramid as soon as there's a second thing to rule out.

## 4.4 The truthiness trap

This is the one narrowing mistake everyone makes:

```python
def f(n: int | None) -> int:
    if n:
        return n         # ✓ n is int here
    return 0             # ← but this branch is `int | None`, NOT `None`
```

`if n:` is false for `None` **and for `0`**. So `n = 0` silently takes the fallback path. The checker is perfectly happy — your logic isn't.

```
   n: int | None
   if n:      →  int          (0 excluded!)
   else:      →  int | None   (both None AND 0 land here)
```

Same trap with `str` (empty string), `list` (empty list), and `dict`.

> ### **When you mean "is it missing?", write `is None`. When you mean "is it empty?", write `if not xs`. Never let one stand in for the other.**

```python
if n is not None:        # ✓ says exactly what it means, and narrows exactly right
    return n
return 0
```

## 4.5 `assert` when you know something the checker doesn't

```python
row = table.get(key)              # dict[str, int].get → int | None
assert row is not None            # you know it's there; now the checker does
return row + 1
```

This is an honest tool — unlike `cast()` (9.7) it actually checks at runtime. The cost is a real `assert` statement, which is stripped under `python -O`. For anything user-facing, raise a real exception instead.

## 4.6 Proving you handled every case

The payoff for `Never`. When a union grows a new member, you want the checker to find every place that forgot about it:

```python
from typing import Literal, assert_never

Mode = Literal["r", "w", "a"]

def describe(m: Mode) -> str:
    if m == "r":
        return "read"
    if m == "w":
        return "write"
    if m == "a":
        return "append"
    assert_never(m)          # ✓ checks: here `m` is Never — nothing can reach this
```

If someone later adds `"x"` to `Mode`, the set at `assert_never` is no longer empty and **this line fails to check** — pointing straight at the function that needs updating. Do this for every closed set of cases you handle in more than one place. It is the cheapest safety net in the language.

## 4.7 Teaching the checker your own test (`TypeIs`)

Sometimes the narrowing lives in a helper function, and the checker can't see through it:

```python
def all_strings(v: Sequence[object]) -> bool:
    return all(isinstance(x, str) for x in v)

if all_strings(items):
    ...          # checker still thinks items is Sequence[object] — a plain bool tells it nothing
```

Change the return annotation and it learns:

```python
from typing import TypeIs        # Python 3.13+

def all_strings(v: Sequence[object]) -> TypeIs[Sequence[str]]:
    return all(isinstance(x, str) for x in v)

if all_strings(items):
    items[0].upper()     # ✓ Sequence[str] here
else:
    len(items)           # ✓ and Sequence[object] here — TypeIs narrows BOTH branches
```

Note the `Sequence`, not `list`. `TypeIs[X]` requires `X` to be a genuine subset of the parameter's type, and `list[str]` is **not** a subset of `list[object]` — that's variance again (5.4), and the checker will tell you so. Read-only shapes narrow; mutable containers don't.

On 3.12, the older `TypeGuard[...]` does the same job but narrows only the **true** branch. Reach for `TypeIs` when you're on 3.13+; it's the better-behaved one.

---

# Part 5 — Choosing the right-sized set

Everything checks; now make it *good*. There is one principle, and it follows from the subset rule.

> ### **Accept the widest set you can work with. Return the narrowest set you actually have.**

Wide inputs mean more callers can use you. Narrow outputs mean your callers can do more with the result.

```
   parameters  →  make the set BIGGER  →  more callers fit
   return      →  make the set SMALLER →  caller can do more without narrowing
```

## 5.1 Parameters: ask for the shape, not the class

```python
def total(xs: list[int]) -> int: ...        # ✗ refuses tuples, sets, generators, ranges
def total(xs: Iterable[int]) -> int: ...    # ✓ accepts all of them
```

The rule of thumb, in order of preference:

| If your function… | Ask for |
|---|---|
| only loops over it once | `Iterable[T]` |
| indexes it or takes `len()` | `Sequence[T]` |
| only reads keys | `Mapping[K, V]` |
| genuinely appends/mutates the caller's object | `list[T]` / `dict[K, V]` |

That last row is the point: **ask for the concrete mutable type only when you're going to mutate it** — because then it's not a needless restriction, it's documentation of a side effect.

## 5.2 Returns: be concrete

```python
def names() -> Iterable[str]: ...      # ✗ caller can't index it or take len()
def names() -> list[str]: ...          # ✓ tells the truth about what they get
```

You built a list. Say so.

## 5.3 Don't return a union you could have avoided

```python
def find(id: int) -> User | None: ...      # fine — "might not exist" is real information
def find(id: int) -> User | None | str: ...# ✗ a smell: what is the str?
```

Every union member is work you're handing to your caller. Two is normal, three deserves a second look, four usually wants a different design.

## 5.4 The variance trap — why `list[Dog]` is not a `list[Animal]`

This is the one part of typing that feels wrong until you see the reason. Here's the reason:

```python
class Animal: ...
class Dog(Animal): ...
class Cat(Animal): ...

def add_a_cat(animals: list[Animal]) -> None:
    animals.append(Cat())            # perfectly legal — a Cat is an Animal

dogs: list[Dog] = [Dog()]
add_a_cat(dogs)                      # ✗ checker refuses — and thank goodness
                                     #   otherwise `dogs` now contains a Cat
```

`Dog ⊂ Animal`, but `list[Dog]` is **not** a subset of `list[Animal]` — because a `list[Animal]` slot lets you *write* an `Animal` into it, and a `list[Dog]` can't accept every `Animal`.

Read-only containers have no such problem:

```python
def count(animals: Sequence[Animal]) -> int:
    return len(animals)              # can only read — nothing can be smuggled in

count(dogs)                          # ✓ Sequence[Dog] IS a Sequence[Animal]
```

> ### **If they can WRITE into it, the sets must match exactly. If they can only READ, a smaller set is fine.**

That one line is the whole of variance, and it also tells you the fix when you hit it: **change the parameter to `Sequence` / `Iterable` / `Mapping`.** Nine times out of ten that's not a workaround — it's what you meant.

The same logic runs backwards for callback parameters (a function that accepts *any* `Animal` can be used where one accepting `Dog`s is wanted), but you'll almost never have to think about that one consciously.

---

# Part 6 — Generics: "the same set, whichever it is"

Sometimes you don't care *which* set — you care that it's the **same one** going in and coming out.

```python
def first(xs: list[Any]) -> Any: ...       # ✗ throws the information away
```

Call that with a `list[str]` and you get back `Any`. All checking downstream, gone. What you want is a **placeholder**: "whatever set went in, that same set comes out."

## 6.1 The 3.12 syntax — square brackets on the definition

```python
def first[T](xs: list[T]) -> T:
    return xs[0]

first([1, 2, 3])          # checker knows: int
first(["a", "b"])         # checker knows: str
```

```
   def first[T](xs: list[T]) -> T
             ▲        ▲        ▲
             │        │        └── ...comes back out here
             │        └── T is bound to whatever's inside...
             └── declare the placeholder
```

`T` is not a type. It's a hole, filled in fresh at every call site. Name it `T` by convention; name it `KeyT`/`ValueT` when there are several and it isn't obvious.

This is **Python 3.12+ syntax (PEP 695)** and it is a genuine improvement — no import, no separate declaration, and the scope of `T` is obvious from where it's written.

## 6.2 Generic classes

```python
class Box[T]:
    def __init__(self, item: T) -> None:
        self.item = item

    def get(self) -> T:
        return self.item

b = Box(42)               # Box[int] — inferred, no annotation needed
b.get()                   # int
```

## 6.3 Bounds — "any set, as long as it's inside this one"

```python
class Comparable[T: (int, float, str)]: ...       # T must be one of these — a "constraint"

def largest[T: float](xs: Sequence[T]) -> T:      # T must be a subset of float — a "bound"
    return max(xs)
```

`T: X` reads as "T fits inside X". Use a bound when you need to *do* something with the values (compare them, add them); use bare `T` when you're only moving them around.

## 6.4 Type aliases — the `type` statement

Also new in 3.12, and lovely:

```python
type UserId = int
type Json = None | bool | int | float | str | list[Json] | dict[str, Json]
type Pair[T] = tuple[T, T]

def load(uid: UserId) -> Json: ...
```

Three things it buys you over a plain `X = int` assignment:

1. It's unambiguous — the checker knows this is a type, not a variable holding a class.
2. It's **lazy**, so a recursive alias like `Json` above just works. (Try that with `Json = ... Json ...` and you get a `NameError`.)
3. It can take parameters, as `Pair[T]` shows.

Name your aliases for domain concepts — `type Celsius = float`, `type Handler = Callable[[Request], Response]`. A well-named alias does more for readability than any other single thing in this essay.

## 6.5 The old spelling, so you recognise it

```python
from typing import TypeVar, Generic
T = TypeVar("T")                       # pre-3.12
def first(xs: list[T]) -> T: ...
class Box(Generic[T]): ...
UserId = int                           # plain alias
```

You'll see this everywhere, including the standard library. It still works and means the same thing. **Read it fluently; write the new form.**

## 6.6 Two more you'll meet occasionally

```python
def wrap[**P, R](f: Callable[P, R]) -> Callable[P, R]:    # ParamSpec — "the same signature"
    ...                                                    # for decorators

def stack[*Ts](*args: *Ts) -> tuple[*Ts]: ...             # TypeVarTuple — "the same shape"
```

`**P` is what makes a decorator preserve its function's signature instead of collapsing it to `Callable[..., Any]`. Worth knowing exists; look it up on the day you write a decorator.

---

# Part 7 — Protocols: sets defined by shape

There are two ways to say what belongs in a set.

```
   by ANCESTRY   →  "everything that inherits from Animal"      class / ABC
   by SHAPE      →  "everything that HAS a .name and a .speak()"  Protocol
```

Python has always been a shape language — that's what duck typing is. `Protocol` is duck typing that the checker can verify.

## 7.1 The problem it solves

```python
def describe(thing: ???) -> str:
    return f"{thing.name} says {thing.speak()}"
```

There's no shared base class. You don't want one — the whole point of duck typing is that unrelated things can play along. So describe the *shape*:

```python
from typing import Protocol

class Speaker(Protocol):
    name: str
    def speak(self) -> str: ...

def describe(thing: Speaker) -> str:
    return f"{thing.name} says {thing.speak()}"
```

```python
class Dog:                          # ← does NOT inherit from Speaker. doesn't need to.
    name = "Rex"
    def speak(self) -> str:
        return "woof"

describe(Dog())                     # ✓ it has the shape, so it's in the set
```

**No registration, no inheritance, no import in `Dog`'s file.** The set `Speaker` is defined by a shape, and `Dog` is in it because of what it *is*, not who its parents were.

## 7.2 Why this is the right tool for boundaries

Protocols let you type third-party objects, test doubles, and plugin interfaces without touching them:

```python
class SupportsWrite(Protocol):
    def write(self, s: str, /) -> int: ...

def emit(out: SupportsWrite, msg: str) -> None:
    out.write(msg)

emit(sys.stdout, "hi")              # ✓
emit(open("f.txt", "w"), "hi")      # ✓
emit(io.StringIO(), "hi")           # ✓ — including your test fake
```

Your production code depends on a *shape*, and your test can hand it anything with that shape. That's dependency injection with no framework at all.

## 7.3 Protocol vs ABC

| | `Protocol` | ABC / base class |
|---|---|---|
| How you join the set | just have the shape | explicitly inherit |
| Can it cover code you don't own? | ✓ yes | ✗ no |
| Provides shared implementation? | ✗ (mostly not) | ✓ yes |
| Checked at runtime? | only with `@runtime_checkable`, and only method *names* | ✓ yes |

Rule of thumb: **`Protocol` for what you accept, base class for what you share.** Protocols at the edges of your code, inheritance in the middle.

## 7.4 The ones already written for you

You rarely need to define your own. `collections.abc` is full of protocols, and `Iterable`, `Sequence`, `Mapping`, `Iterator`, `Callable`, `Hashable`, `Sized` cover the vast majority of real parameters. `Part 5.1` was protocols the whole time.

---

# Part 8 — Typing your data

Five ways to say "a record with these fields." Pick by how the data behaves.

## 8.1 `dataclass` — the default answer

```python
from dataclasses import dataclass, field

@dataclass
class User:
    id: int
    name: str
    tags: list[str] = field(default_factory=list)     # NOT `= []` — see 9.1
    active: bool = True

u = User(1, "ann")
u.name                     # ✓ checked
u.nmae                     # ✗ caught
```

The annotations aren't decoration here — `@dataclass` reads them to build `__init__`, `__repr__`, and `__eq__`. This is the one place your types do real work at runtime.

Two options worth using by default:

```python
@dataclass(frozen=True)      # immutable, and hashable — great for keys and value objects
@dataclass(slots=True)       # smaller and faster; blocks typo'd attribute assignment
@dataclass(kw_only=True)     # forces User(id=1, name="ann") — good for wide records
```

## 8.2 `TypedDict` — when it must stay a dict

For JSON, API payloads, and anything crossing a wire, where a real class would be a lie:

```python
from typing import TypedDict, NotRequired

class UserDict(TypedDict):
    id: int
    name: str
    nickname: NotRequired[str]         # may be absent entirely

u: UserDict = {"id": 1, "name": "ann"}
u["name"]                              # ✓ str
u["nmae"]                              # ✗ caught — unknown key
```

It's a plain `dict` at runtime, with zero overhead. `NotRequired` (3.11+) marks optional keys; `total=False` on the class makes them *all* optional; `ReadOnly` (3.13+) marks ones callers mustn't change.

> **`TypedDict` when the thing genuinely is a dict. `dataclass` when it's an object you happened to load from a dict.** Converting at the boundary is usually the right move.

## 8.3 `NamedTuple` — a tuple with names

```python
from typing import NamedTuple

class Point(NamedTuple):
    x: int
    y: int

p = Point(1, 2)
p.x                        # ✓ 1
x, y = p                   # ✓ still unpacks — it IS a tuple
```

Immutable, unpackable, comparable, and light. Use it for small values that are naturally positional (coordinates, ranges, small return bundles). For anything with more than about three fields, a frozen dataclass reads better.

## 8.4 Multiple returns without a tuple

```python
def stats(xs: Sequence[float]) -> tuple[float, float]:      # ✗ which one is which?
def stats(xs: Sequence[float]) -> Stats:                    # ✓ named fields
```

The moment a returned tuple has two elements of the same type, name them. A `NamedTuple` or small dataclass costs three lines and removes an entire category of bug.

## 8.5 `Enum` — a fixed set you can also carry around

```python
from enum import Enum, StrEnum, auto

class Colour(StrEnum):
    RED = "red"
    GREEN = "green"

def paint(c: Colour) -> None: ...
paint(Colour.RED)          # ✓
paint("red")               # ✗ with Enum; ✓ with StrEnum (it IS a str)
```

`Literal` vs `Enum`: **`Literal` for values passing through** (a mode you receive and immediately branch on), **`Enum` for a concept you own** (something with a name, methods, or a canonical list you iterate). `StrEnum` (3.11+) is the friendly middle when the values also have to be strings on the wire.

## 8.6 `Final` and `ClassVar` — labels about the slot, not the value

```python
from typing import Final, ClassVar

MAX_RETRIES: Final = 3              # nobody may rebind this
MAX_SIZE: Final[int] = 1024

class Conn:
    pool: ClassVar[dict[str, str]] = {}   # shared by the class, not per-instance
    host: str                             # per-instance
```

`ClassVar` matters inside dataclasses: it tells `@dataclass` "this is *not* a field", so it stays off `__init__`. Without it, a shared mutable class attribute is a bug waiting to happen.

## 8.7 `Self` and `@override`

```python
from typing import Self, override

class Builder:
    def add(self, x: int) -> Self:      # ✓ subclasses return THEIR type, not Builder
        return self

class Base:
    def run(self) -> None: ...

class Child(Base):
    @override                            # 3.12+ — checker verifies this really overrides
    def run(self) -> None: ...
    @override
    def ran(self) -> None: ...           # ✗ caught: typo, overrides nothing
```

`@override` (3.12) is a small decorator that catches a genuinely nasty class of bug: a renamed or misspelled method that silently stops overriding anything. If you write class hierarchies, use it everywhere.

---

# Part 9 — The traps

## 9.1 Mutable defaults

```python
def add(x: int, into: list[int] = []) -> list[int]:      # ✗ ONE list, shared by every call
```

Not a typing bug — a Python bug the annotation makes more visible. The fixes:

```python
def add(x: int, into: list[int] | None = None) -> list[int]:
    into = [] if into is None else into

@dataclass
class C:
    xs: list[int] = field(default_factory=list)          # the dataclass version
```

## 9.2 Nothing is checked at runtime

Worth repeating because people are surprised twice — once when they learn it, once when they forget:

```python
def f(x: int) -> int: ...
f("hello")                  # runs. no error. the checker complains; Python doesn't.
```

**Never rely on annotations to validate input.** For data crossing a boundary — a request body, a config file, a CSV — use `pydantic` or explicit checks. Annotations describe intent; they don't enforce it.

## 9.3 `Any` spreads silently

```python
import untyped_lib                       # everything from it is Any

data = untyped_lib.load()                # Any
name = data["user"]["name"]              # Any
name.upper().flurb()                     # ✓ no complaints. crashes at runtime.
```

Pin it down as soon as it enters your code:

```python
data: dict[str, UserDict] = untyped_lib.load()
```

One annotation at the boundary restores checking for everything downstream. **Type the doorway, not every room.**

## 9.4 Bare containers

```python
def f(xs: list) -> dict: ...             # ✗ = list[Any], dict[Any, Any]
def f(xs: list[str]) -> dict[str, int]: ...   # ✓
```

Silent, and it switches off exactly the checking you thought you'd turned on. Most checkers have a strict flag (`--disallow-any-generics`) that catches these; turn it on once you're comfortable.

## 9.5 `float` promotion does not reach inside containers

```python
def f(x: float) -> None: ...
f(3)                                     # ✓ int is accepted for float

def g(xs: list[float]) -> None: ...
nums: list[int] = [1, 2, 3]
g(nums)                                  # ✗ list[int] is not list[float]
g([1, 2, 3])                             # ✓ — see below
```

Genuinely inconsistent-feeling, and it's variance again (5.4): `g` could append a `1.5` to your list of ints. The fix is `xs: Sequence[float]` — read-only, so it's allowed.

That last line is why this trap ambushes people. A **literal** written at the call site has no type of its own yet, so the checker infers it as `list[float]` to fit the slot and waves it through. The error only appears once the list has a name — which is usually the day after you wrote the function.

## 9.6 Forward references

Referring to a name defined later — or to the class you're inside:

```python
class Node:
    def sibling(self) -> "Node": ...      # quotes: the classic fix, works everywhere
```

On **3.14+** annotations are evaluated lazily (PEP 649) and the quotes are no longer needed. On 3.12–3.13, either quote it, or put `from __future__ import annotations` at the top of the file and forget about it.

For imports that only exist for typing — including ones that would be circular at runtime:

```python
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from myapp.models import User        # never imported at runtime

def save(u: "User") -> None: ...
```

## 9.7 `cast` lies, and it's silent

```python
from typing import cast
x = cast(list[str], something)           # "trust me" — zero runtime effect
```

`cast` does nothing at runtime and disables checking at that point. It's occasionally necessary at the edge of untyped code. Prefer `assert isinstance(...)` (4.5), which actually verifies. Every `cast` should feel like it needs a comment.

## 9.8 Silencing the checker

```python
x = weird()  # type: ignore[assignment]      # mypy — name the code, don't blanket-ignore
y = odd()    # pyright: ignore[reportGeneralTypeIssues]
```

Always include the specific error code. A bare `# type: ignore` hides the next three bugs on that line too.

## 9.9 Over-annotating

```python
name: str = "ann"                        # ✗ noise — the checker already knows
count: int = len(xs)                     # ✗ noise
result: dict[str, list[int]] = {}        # ✓ genuinely useful, can't be inferred
```

**Annotate boundaries, not the inside.** Function signatures, class attributes, and empty containers earn their annotations. Ordinary locals with obvious values do not — the checker infers them perfectly, and the label is just something else to keep in sync.

> ### **If deleting the annotation loses no information, delete it.**

---

# Part 10 — The whole thing on one page

## Naming sets

| You write | The set |
|---|---|
| `int`, `str`, `bytes`, `bool`, `float` | the obvious ones |
| `None` | exactly one value |
| `User` | instances of `User` and its subclasses |
| `Literal["a", "b"]` | exactly those values |
| `object` | every value — but you can't use it without narrowing |
| `Any` | checking off |
| `Never` | empty — nothing can be here |

## Combining sets

| You write | Means |
|---|---|
| `int \| None` | an int, or nothing |
| `list[int]` | list of ints |
| `dict[str, int]` | str keys, int values |
| `set[str]`, `frozenset[int]` | as expected |
| `tuple[int, str]` | exactly two, in that order |
| `tuple[int, ...]` | any number of ints |
| `Callable[[int], bool]` | function: takes an int, returns a bool |
| `Callable[..., None]` | any arguments, returns nothing |
| `Iterable[T]` / `Sequence[T]` / `Mapping[K, V]` | the shape, not the class |
| `type UserId = int` | a named alias (3.12+) |

## Shrinking sets

| You write | Effect |
|---|---|
| `if x is None: return` | everything below is non-None |
| `if isinstance(x, C):` | narrows to `C`; the `else` gets the rest |
| `assert x is not None` | narrows, and checks at runtime |
| `match x: case int():` | narrows per case |
| `assert_never(x)` | ✓ only if every case is handled — your exhaustiveness alarm |
| `-> TypeIs[C]` (3.13+) | teach the checker your own test |

## Defining things

| You write | Use it for |
|---|---|
| `def f[T](x: T) -> T` | same set in, same set out (3.12+) |
| `class Box[T]:` | a generic container (3.12+) |
| `def f[T: float](…)` | generic, bounded |
| `class P(Protocol):` | a set defined by shape, not ancestry |
| `@dataclass class C:` | a record — the default choice |
| `class D(TypedDict):` | a record that must stay a dict |
| `class P(NamedTuple):` | a small immutable positional record |
| `Final`, `ClassVar` | facts about the slot, not the value |
| `Self`, `@override` | correct types in class hierarchies (3.11 / 3.12) |

## Choosing well

| Situation | Do this |
|---|---|
| a parameter you only loop over | `Iterable[T]` |
| a parameter you index | `Sequence[T]` |
| a parameter you read keys from | `Mapping[K, V]` |
| a parameter you mutate | `list[T]` / `dict[K, V]` — and mean it |
| any return value | the concrete type |
| "`list[Dog]` isn't a `list[Animal]`" | change the parameter to `Sequence` |
| a fixed set of string modes | `Literal[...]` |
| you reached for `Any` | try `object` first |

---

# Part 11 — When it surprises you, ask three questions

1. **"What set does the slot allow, what set is my value in, and does mine fit?"** Say it with the real names. Most checker messages are literally telling you these two sets — read them as sets and the message stops being noise.
2. **Getting "`X | None` has no attribute …"?** You forgot to shrink. Add the `is None` guard at the top and return early. This is the single most common message in typed Python, and it is nearly always the checker finding a real crash.
3. **Getting "`list[Dog]` is incompatible with `list[Animal]`"?** It's variance (5.4). Ask whether that parameter really mutates the list. If not — and it usually doesn't — change it to `Sequence`.

And the universal move: **`reveal_type(x)` on the line before the error.** Stop guessing what the checker thinks; ask it.

---

# Part 12 — Real code, using all of it

```python
from collections.abc import Callable, Iterable, Sequence
from dataclasses import dataclass
from typing import Literal, Protocol, Self, TypedDict, assert_never

# --- domain aliases: names do more for readers than any other annotation ---
type UserId = int
type Role = Literal["admin", "editor", "viewer"]


# --- the wire format: it really is a dict, so TypedDict ---
class UserPayload(TypedDict):
    id: int
    name: str
    role: str                             # a str on the wire — it hasn't been checked yet


# --- the boundary: turn an unchecked str into a Role, or refuse ---
def parse_role(raw: str) -> Role:
    match raw:
        case "admin" | "editor" | "viewer":
            return raw                    # narrowed by `match` — see 4.2
        case _:
            raise ValueError(f"unknown role: {raw}")


# --- the domain object: it's an object, so dataclass ---
@dataclass(frozen=True, slots=True)
class User:
    id: UserId
    name: str
    role: Role                            # inside the program it's never a bare str again
    tags: tuple[str, ...] = ()

    @classmethod
    def from_payload(cls, p: UserPayload) -> Self:
        return cls(id=p["id"], name=p["name"], role=parse_role(p["role"]))


# --- a boundary described by shape, not by class ---
class Store(Protocol):
    def get(self, uid: UserId) -> User | None: ...
    def all(self) -> Sequence[User]: ...


# --- accept wide, return narrow ---
def names_of(users: Iterable[User]) -> list[str]:
    return [u.name for u in users]


def find_admins(store: Store) -> list[User]:
    return [u for u in store.all() if u.role == "admin"]


# --- narrowing: rule out None once, at the top ---
def greet(store: Store, uid: UserId) -> str:
    user = store.get(uid)
    if user is None:
        return "hello, stranger"
    return f"hello, {user.name}"          # user is a User for the whole rest of the body


# --- exhaustiveness: adding a Role breaks this on purpose ---
def permissions(role: Role) -> frozenset[str]:
    match role:
        case "admin":
            return frozenset({"read", "write", "delete"})
        case "editor":
            return frozenset({"read", "write"})
        case "viewer":
            return frozenset({"read"})
        case _:
            assert_never(role)


# --- generics: whatever went in comes back out ---
def first[T](xs: Sequence[T], default: T) -> T:
    return xs[0] if xs else default


def group_by[T, K](items: Iterable[T], key: Callable[[T], K]) -> dict[K, list[T]]:
    out: dict[K, list[T]] = {}            # ← an empty container genuinely needs its label
    for item in items:
        out.setdefault(key(item), []).append(item)
    return out
```

Read that top to bottom and notice how little of it is ceremony. The aliases name concepts, the `Protocol` describes a seam, the narrowing removes a crash, and `assert_never` guarantees the next person who adds a role can't forget this function.

---

# Appendix

## A. The old spellings — recognise them, don't write them

| You'll see (old) | Write instead | Since |
|---|---|---|
| `List[int]`, `Dict[str, int]`, `Set[str]`, `Tuple[int, ...]` | `list[int]`, `dict[str, int]`, `set[str]`, `tuple[int, ...]` | 3.9 |
| `typing.Callable`, `typing.Iterable`, `typing.Sequence` | import from `collections.abc` | 3.9 |
| `Union[int, str]` | `int \| str` | 3.10 |
| `Optional[int]` | `int \| None` | 3.10 |
| `T = TypeVar("T")` + `Generic[T]` | `def f[T]()`, `class C[T]` | 3.12 |
| `Alias = int` | `type Alias = int` | 3.12 |
| `NoReturn` (for "can't happen" values) | `Never` | 3.11 |
| `-> "MyClass"` in a method | `-> Self` | 3.11 |
| `TypeGuard[X]` | `TypeIs[X]` (narrows both branches) | 3.13 |
| `def f(x: int = None)` | `def f(x: int \| None = None)` | always was |

That last row was once allowed ("implicit Optional") and is now an error by default. If old code trips on it, the fix is always to write the `| None` you meant.

## B. What landed when

| Version | Highlights |
|---|---|
| 3.9 | `list[int]` builtins |
| 3.10 | `X \| Y`, `TypeGuard`, `ParamSpec`, pattern matching |
| 3.11 | `Self`, `Never`, `assert_never`, `LiteralString`, `Required`/`NotRequired`, `StrEnum` |
| **3.12** | **`def f[T]`, `class C[T]`, `type X = …` (PEP 695), `@override`, `Unpack[**kwargs]`** |
| 3.13 | `TypeIs`, `ReadOnly` for TypedDict, type-parameter defaults |
| 3.14 | lazy annotations (PEP 649) — forward references need no quotes |

## C. Turning the dial up

Types are a dial, not a switch. A sane progression:

1. Annotate **new** functions only. Nothing else.
2. Turn the checker on in your editor and fix what's red in files you're already touching.
3. Add it to CI, allowing failures at first.
4. Enable `--strict` on one package. Then another.
5. Add `--disallow-any-generics` (catches bare `list`) and `--warn-return-any`.

Never do a big-bang annotation sweep. The value of types is concentrated in the code you're actively changing, and a thousand-line typing PR gets rubber-stamped, which teaches you nothing.

## D. Where types do run at runtime

Three real cases, so you know the exceptions to "Python ignores labels":

- **`@dataclass`** reads annotations to generate `__init__` and friends.
- **`pydantic` / `attrs`** read them to build actual validators — this is how you check data at a boundary.
- **`typing.get_type_hints(obj)`** lets any library read them; frameworks like FastAPI use this for routing and serialisation.

The annotation itself still never checks anything. Something has to go and read it.

---

# The one thing to remember

> ## **A type is the SET of values allowed in that slot. A value fits when its set is a subset of the slot's set.**
>
> **Every construct is naming a set, combining sets, or shrinking one. Accept the widest set you can work with; return the narrowest set you actually have. And Python never reads the labels — the checker and the next human do.**

That sentence is the entire system. Say it out loud with your real types and the error message stops being noise.

And on the days a signature makes you squint: **`reveal_type(x)`, then read the checker's two sets and ask which one is too big.**
