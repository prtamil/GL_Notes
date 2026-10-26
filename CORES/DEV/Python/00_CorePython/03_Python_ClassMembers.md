# Never Be Unsure Where a Python Attribute Lives Again

*Modern Python — 3.12 and later. Class attributes, instance attributes, `@staticmethod`, `@classmethod`, `@property`, `__slots__`, `_private`, and dataclasses. Every output in this essay is real Python output.*

There is **one** mental model in this essay. Not one for classes and another for instances, not a special case for `self`, not a separate story for dataclasses. One.

This essay is not about object-oriented design. It doesn't argue for inheritance or against it, and it won't tell you when to make something a class. It answers a much smaller and much more useful question, the one you actually have at 4pm on a Tuesday:

> **"Where does this name live, who can reach it, and what happens when I write to it?"**

Learn the model in Part 1, then watch it explain every member you will ever declare.

---

# Part 1 — The mental model: a drawer and a shelf

Every **object** has its own **drawer**. Every **class** has one **shelf**, standing behind all of its objects.

```python
class Counter:
    limit = 10                  # goes on the SHELF

    def __init__(self):
        self.n = 0              # goes in the DRAWER

    def tick(self):             # goes on the SHELF (a function is just a thing)
        self.n += 1

a = Counter()
b = Counter()
a.tick(); a.tick(); a.tick()
b.tick()
```

```
                   ┌─────────────────────────────────┐
                   │   THE SHELF  —  Counter         │   one of it. shared.
                   │      limit = 10                 │
                   │      tick  = <function tick>    │
                   │      __init__ = <function ...>  │
                   └─────────────────────────────────┘
                       ▲                         ▲
             behind me │                         │ behind me
       ┌───────────────┴──────┐        ┌─────────┴────────────┐
       │  MY DRAWER  —  a     │        │  MY DRAWER  —  b     │
       │      n = 3           │        │      n = 1           │
       └──────────────────────┘        └──────────────────────┘
```

You can open both and look. This is not a metaphor — these are two real dictionaries:

```python
vars(a)                 # {'n': 3}
vars(b)                 # {'n': 1}
[k for k in vars(Counter) if not k.startswith('_')]
                        # ['limit', 'tick']
```

`vars(x)` is just `x.__dict__`. **The drawer is a dict. The shelf is a dict.** That's all an object is.

## The two rules

Everything in this essay falls out of the fact that **reading and writing do not travel the same distance.**

| Move | Where it looks | Where it lands |
|---|---|---|
| **READ** — `a.limit` | my drawer first → then the shelf behind me → then the shelves behind *that* | — |
| **WRITE** — `a.limit = 99` | doesn't look anywhere | **my own drawer. Always.** |
| **DELETE** — `del a.limit` | doesn't look anywhere | **my own drawer. Always.** |

Say it out loud, every time you're confused:

> ## **"Reading walks back. Writing stays put."**

That is the entire essay. Accessibility in Python is this asymmetry, and nothing else.

## Watch it once

```python
a.limit                 # 10   — not in a's drawer, so we walk back to the shelf
a.limit = 99            # a WRITE: lands in a's drawer, shelf untouched
a.limit                 # 99   — now it IS in a's drawer, the walk stops there
b.limit                 # 10   — b's drawer is empty, b still walks back to the shelf
Counter.limit           # 10   — the shelf never changed
vars(a)                 # {'n': 3, 'limit': 99}
```

`a` didn't *change* the shared value. It put its own copy in front of it. This is called **shadowing**, and it is the single most useful thing to understand about Python attributes.

```
        SHELF:   limit = 10  ← b still sees this
                    ▲
                    ✕ blocked
        a's DRAWER: limit = 99  ← a sees this
```

Undo it by emptying your own drawer:

```python
del a.limit
a.limit                 # 10   — the shelf was there all along
del a.limit             # AttributeError: 'Counter' object has no attribute 'limit'
```

That error is worth reading carefully. `del` doesn't walk back either. There is nothing in `a`'s drawer to delete, and Python will not delete off the shelf on your behalf.

## The corollary that catches everyone

Since writing is what puts things in your drawer, and reading is what walks back — **look very carefully at which one you just did.**

> ### **`obj.x = ...` is a write. `obj.x.anything()` is a read.**

```python
class Basket:
    items = []                      # a list, on the SHELF
    def add(self, x):
        self.items.append(x)        # READ items, then mutate what you found

p = Basket()
q = Basket()
p.add("apple")

q.items                 # ['apple']   ← q sees it too
Basket.items            # ['apple']   ← because it was the shelf's list all along
vars(p)                 # {}          ← p never wrote anything
```

`self.items.append(x)` never assigns to `self.items`. It reads `items` — walking back to the shelf — and mutates the object it finds there. `p`'s drawer stays empty and every basket shares one list. This is Part 7's most famous bug, and you can already see exactly why it happens.

That's the model. Now we just apply it.

---

# Part 2 — All the moves on a drawer and a shelf

## 2.1 Putting something on the shelf

Anything in the class body, at class-body indentation, goes on the shelf:

```python
class Config:
    debug = False           # a value
    RETRIES = 3             # a constant
    def load(self): ...     # a function is a value too
```

The class body is **ordinary code that runs exactly once**, at import time, top to bottom. Whatever names exist when it finishes become the shelf.

```python
class Once:
    print("this runs at import")
    a = 1
    b = a + 1               # a is just a local name here, right now

Once.b                      # 2
```

## 2.2 Putting something in the drawer

Any assignment to `self.something`, anywhere:

```python
class Config:
    def __init__(self):
        self.path = "/etc"      # drawer
```

There is nothing special about `__init__`. It is the conventional place because it runs at birth, but a drawer accepts writes at any time, from anywhere:

```python
class Late: pass
x = Late()
x.whatever = 1              # perfectly legal
vars(x)                     # {'whatever': 1}
```

(Legal is not the same as good — see 8.6.)

## 2.3 A bare annotation puts **nothing** anywhere

This is the one that surprises people who came from typed languages.

```python
class Bare:
    x: int              # a promise. Creates NOTHING at runtime.
    y: int = 0          # a promise AND a value on the shelf.
```

```python
'x' in vars(Bare)       # False
'y' in vars(Bare)       # True
Bare.y                  # 0
Bare.x                  # AttributeError: type object 'Bare' has no attribute 'x'
Bare.__annotations__    # {'x': <class 'int'>, 'y': <class 'int'>}
```

`x: int` records a *type annotation* and puts it in a side table (`__annotations__`). It does not put `x` on the shelf. Nothing will ever read it at runtime — unless a library goes looking, which is precisely what `@dataclass` does in Part 6.

> **`x: int` describes a slot that doesn't exist yet. `x: int = 0` creates one on the shelf.**

## 2.4 Reading walks back through *whatever is behind you*

```python
class Cfg:
    debug = False

c = Cfg()
c.debug                 # False       — walked back
vars(c)                 # {}          — nothing of its own

c.debug = True          # write: c's drawer
Cfg.debug = "changed"   # write: the shelf (Cfg has no drawer of its own here — see 2.5)

c.debug                 # True        — c's own copy still wins
Cfg().debug             # 'changed'   — a fresh instance walks back and sees the new shelf
```

A shelf value is a **live default**, not a copy handed out at birth. Change the shelf and every un-shadowed instance sees it immediately.

## 2.5 The class is an object too

`Counter.limit = 5` looks like "writing to the shelf," and it is — because a class is itself an object, and *its* drawer is the shelf. The same two rules apply one level up, which is why Part 5's inheritance section needs no new ideas at all.

## 2.6 Delete, and the value underneath comes back

```python
a.limit = 99
del a.limit             # remove my copy
a.limit                 # 10  — the shelf is revealed again
```

Shadowing is a stack, and `del` pops your layer off.

## 2.7 Which one should hold what

| Put it on the **shelf** when | Put it in the **drawer** when |
|---|---|
| every instance agrees on it | it differs per instance |
| it's a constant: `MAX_RETRIES = 3` | it's state: `self.retries_left` |
| it's a method | it's data set at birth |
| it's a registry the class deliberately shares | anything you plan to mutate |
| it's an **immutable** default | it's a `list`, `dict`, or `set` — **always** |

That last row is not a style preference. It is the corollary at the end of Part 1, and it is Part 7.1.

---

# Part 3 — Shelf items that are functions: the four kinds of member

Here is the fact that makes `self` stop being magic:

> ### **A method is just a shelf item that happens to be a function. Taking a function off the shelf *through an instance* pre-fills its first argument.**

Watch:

```python
Counter.tick            # <function Counter.tick at 0x...>
a.tick                  # <bound method Counter.tick of <Counter object at 0x...>>

a.tick.__self__  is a               # True   — this is the pre-filled argument
a.tick.__func__  is Counter.tick    # True   — same function underneath

a.tick()                            # identical to...
Counter.tick(a)                     # ...this
```

That pre-filling is called **binding**, and it is the whole of `self`. `self` is not a keyword, not injected by the interpreter, not special. It is argument number one, and reaching a function through an instance fills it in for you.

**Proof, using nothing but the model:** put a function in the *drawer* instead, and no binding happens — because binding is something the *shelf* does.

```python
a.shout = lambda: "hi"      # a WRITE — lands in the drawer
a.shout                     # <function <lambda> at 0x...>   ← not "bound method"
a.shout()                   # 'hi'   — no self was passed
```

The four kinds of member are just four answers to "what should get pre-filled?"

```python
class Kinds:
    tag = "shelf"                                   # 0. plain value

    def inst(self, x):        return ("inst", x)    # 1. instance method
    @classmethod
    def cls_(cls, x):         return ("cls",  x)    # 2. class method
    @staticmethod
    def stat(x):              return ("stat", x)    # 3. static method
    @property
    def prop(self):           return "computed"     # 4. property
```

| Member | What sits on the shelf | `k.f(1)` gets | `Kinds.f(1)` gets | Reach for it when… |
|---|---|---|---|---|
| `def inst(self, x)` | `function` | `self=k, x=1` | `self=1` ⚠ | it needs **this object's drawer** |
| `@classmethod def cls_(cls, x)` | `classmethod` | `cls=Kinds, x=1` | `cls=Kinds, x=1` | it needs **the class**, not an instance |
| `@staticmethod def stat(x)` | `staticmethod` | `x=1` | `x=1` | it needs **neither**, but belongs here |
| `@property def prop(self)` | `property` | runs on *access*, no `()` | returns the `property` object | it's **data to the caller, work to you** |

```python
k = Kinds()
k.inst(1)               # self=k
Kinds.inst(k, 1)        # identical
k.cls_(1)               # cls is Kinds
Kinds.cls_(1)           # cls is Kinds — works with no instance at all
k.stat(1)               # ('stat', 1)
Kinds.stat(1)           # ('stat', 1)
k.prop                  # 'computed'                     ← no parentheses
Kinds.prop              # <property object at 0x...>     ← the raw shelf item
```

That last line is the model being honest with you. Reached through the *class*, you get the thing that's literally on the shelf. Reached through an *instance*, the shelf item gets a chance to transform itself first. Appendix B names that mechanism.

## 3.1 Instance method — needs the drawer

The default. If the body touches `self.anything`, this is what you want.

```python
class Cart:
    def __init__(self):
        self.lines: list[str] = []
    def add(self, item: str) -> None:
        self.lines.append(item)         # reaches into this cart's drawer
```

## 3.2 `@classmethod` — needs the class

Two real uses, and they're both about the class *itself* being the thing you need.

**Alternative constructors.** The critical property: `cls` is *the class you were called on*, so subclasses get it right for free.

```python
class Base:
    @classmethod
    def make(cls):          return cls()
    @staticmethod
    def make_static():      return Base()       # hard-coded — a bug waiting

class Sub(Base): pass

type(Sub.make())            # <class 'Sub'>     ✓
type(Sub.make_static())     # <class 'Base'>    ✗ wrong, and silently so
```

> **If a "constructor" mentions its own class by name, it should be a `@classmethod` and say `cls`.**

**Shelf-level state.** Registries, counters, caches — anything belonging to the class rather than to any one object:

```python
class Plugin:
    registry: dict[str, type["Plugin"]] = {}
    @classmethod
    def register(cls, name: str) -> None:
        cls.registry[name] = cls
```

## 3.3 `@staticmethod` — needs neither

A plain function that you have parked on the shelf for namespacing. No `self`, no `cls`, no access to any drawer.

```python
class Temperature:
    @staticmethod
    def plausible(celsius: float) -> bool:
        return -273.15 <= celsius <= 1000.0
```

Reachable as `Temperature.plausible(20)` or `t.plausible(20)` — identically, since nothing gets pre-filled either way.

**When is it right?** When the function is *conceptually* part of the class's vocabulary and would be confusing floating loose in the module. A validator for the class's own fields; a small conversion its methods keep needing.

**When is it wrong?** When you reached for it only because you didn't need `self`. A module-level function is simpler, easier to test, easier to import, and doesn't pretend to a relationship it doesn't have. `@staticmethod` is the rarest of the four for a reason.

> **`@staticmethod` is a filing decision, not a design one.**

## 3.4 `@property` — a shelf item that does work when read

A property makes a method reachable as though it were data.

```python
class Temp:
    def __init__(self, c: float):
        self._c = c
    @property
    def fahrenheit(self) -> float:
        return self._c * 9 / 5 + 32

t = Temp(100)
t.fahrenheit            # 212.0        ← no parentheses. It's a read.
vars(t)                 # {'_c': 100}  ← nothing named 'fahrenheit' in the drawer
```

Nothing is stored. Every read runs the function. The drawer holds `_c`; `fahrenheit` is a **view**.

Use it when a value is genuinely derived, and cheap. Don't use it to hide expensive work behind something that reads like a field — a caller who writes `x.total` in a loop has every right to assume it's free.

## 3.5 A property is also a **gatekeeper on writes**

This is the one place the second rule bends, and it bends *on purpose*.

```python
t.fahrenheit = 5
# AttributeError: property 'fahrenheit' of 'Temp' object has no setter
```

Writing did not "stay put" — it hit the shelf item and was refused. That's the point: a property is how you install a guard between callers and your drawer.

```python
class Temp2:
    def __init__(self, c: float):
        self.c = c                      # goes through the setter below

    @property
    def c(self) -> float:
        return self._c

    @c.setter
    def c(self, v: float) -> None:
        if v < -273.15:
            raise ValueError("below absolute zero")
        self._c = v

t2 = Temp2(20)
t2.c = 30
vars(t2)                # {'_c': 30}       ← the real storage, one underscore
t2.c = -300             # ValueError: below absolute zero
```

Note the shape: the **public name** `c` is the gate; the **private-ish name** `_c` is the drawer slot behind it. That naming pair is a convention worth copying, and Part 4 explains why the underscore is enough.

The full set of hooks:

```python
@property                       # read
def c(self): ...
@c.setter                       # write
def c(self, v): ...
@c.deleter                      # del
def c(self): ...
```

Read-only is the default and usually the right one. **Add a setter only when there is something to validate or something to keep in sync.** A setter that just assigns is a plain attribute with extra steps.

## 3.6 `@cached_property` — computes once, then gets out of the way

```python
from functools import cached_property

class Doc:
    def __init__(self, text: str):
        self.text = text
    @cached_property
    def words(self) -> list[str]:
        print("(computing...)")
        return self.text.split()

d = Doc("a b c")
vars(d)                 # {'text': 'a b c'}
d.words                 # (computing...)  → ['a', 'b', 'c']
d.words                 #                 → ['a', 'b', 'c']    no recompute
vars(d)                 # {'text': 'a b c', 'words': ['a', 'b', 'c']}
```

Read that last line against the model and it explains itself: **the first read wrote the answer into the drawer.** From then on the walk stops at the drawer and never reaches the shelf again. That's not an implementation detail, it's the entire mechanism.

Which gives you cache invalidation for free — just empty the slot:

```python
self.__dict__.pop("words", None)        # next read recomputes
```

And an important limitation, same reasoning: **`cached_property` needs a drawer.** It cannot work on a class with `__slots__` (3.7) or on `@dataclass(frozen=True)`, because both take the drawer away or lock it. (For a frozen dataclass, the usual answer is a `field(init=False)` computed once in `__post_init__` via `object.__setattr__`. `functools.lru_cache` on a method also works — it needs the instance to be hashable, which frozen gives you — but the cache is shared across all instances and keeps every one of them alive, so use it only for small, long-lived objects.)

Unlike `@property`, it does **not** guard writes — `d.words = [...]` simply overwrites the cached value, because a plain drawer entry is exactly what it left there.

## 3.7 `__slots__` — take the drawer away entirely

```python
class Slim:
    __slots__ = ("x", "y")
    def __init__(self, x, y):
        self.x, self.y = x, y

s = Slim(1, 2)
vars(s)             # TypeError: vars() argument must have __dict__ attribute
s.z = 3             # AttributeError: 'Slim' object has no attribute 'z'
                    #                 and no __dict__ for setting new attributes
type(vars(Slim)['x'])       # <class 'member_descriptor'>
```

`__slots__` replaces the flexible drawer with **fixed pigeonholes**, and puts a small handle for each one on the shelf. You get:

- **less memory** — no per-object dict. Real money when you have a million of something.
- **slightly faster** attribute access.
- **typo protection** — `s.nmae = 1` raises instead of silently creating a field.

You give up: `vars()`, `cached_property`, adding attributes at runtime, and some pickling conveniences.

Three rules that follow from "the shelf holds a handle for each slot":

```python
# 1. A subclass without __slots__ gets a drawer back — and all the memory with it.
class Fat(Slim): pass
f = Fat(1, 2); f.z = 3
vars(f)                 # {'z': 3}        ← the point of __slots__ is gone

# 2. So a subclass that wants to stay lean must say so, even with nothing to add.
class Lean(Slim):
    __slots__ = ()

# 3. A slot name and a class default can't share the shelf.
class Bad:
    __slots__ = ("x",)
    x = 0               # ValueError: 'x' in __slots__ conflicts with class variable
```

And multiple inheritance from two classes with non-empty slots is refused outright:

```python
class A: __slots__ = ("a",)
class B: __slots__ = ("b",)
class C(A, B): __slots__ = ()   # TypeError: multiple bases have instance lay-out conflict
```

**When to use it:** you are making a great many small objects and you have measured. Otherwise `@dataclass(slots=True)` (6.8) gives you the same thing with none of the boilerplate, and that's how you'll write it in practice.

---

# Part 4 — Accessibility: who is allowed to reach it

Now the question the whole essay is named for. Python's answer is short:

> ### **Nothing is private. Everything is reachable. Access control is a naming convention plus one mechanical trick.**

There are exactly four levels, and only one of them does anything at runtime.

| You write | Called | Enforced by | Means |
|---|---|---|---|
| `name` | public | — | part of the deal. Change it and you break callers. |
| `_name` | internal | **nobody** (and `import *`) | "I may change this. Don't build on it." |
| `__name` | mangled | the **compiler**, mechanically | "no subclass may collide with this." |
| `__name__` | dunder | the language | reserved. Use them, don't invent them. |

## 4.1 `_name` — the one you should use

One leading underscore. It is a message to a human, and that is all:

```python
class Session:
    def __init__(self, token: str):
        self._token = token         # reachable. Just don't.
        self.user = "ann"

s = Session("abc")
s._token                # 'abc'   — works fine. Nothing stops you.
```

Nothing stops you, and that's deliberate. Python's position is that the person debugging your library at 2am has a better claim on the data than your encapsulation does. The underscore is the sign on the door, not a lock.

It does have exactly one mechanical effect, and it's at module level: `from module import *` skips names starting with a single underscore.

**Use `_name` for essentially all of your "private" needs.** It is what the standard library does, what every major package does, and what your type checker and IDE will grey out for you.

## 4.2 `__name` — mangling, which is not privacy

Two leading underscores (and *at most one* trailing) triggers a compile-time rewrite. Inside `class Vault`, every `self.__secret` is literally compiled to `self._Vault__secret`.

```python
class Vault:
    def __init__(self):
        self.public = 1
        self._internal = 2
        self.__secret = 3
    def peek(self):
        return self.__secret        # compiled to self._Vault__secret

v = Vault()
vars(v)             # {'public': 1, '_internal': 2, '_Vault__secret': 3}
v.peek()            # 3
v.__secret          # AttributeError: 'Vault' object has no attribute '__secret'
v._Vault__secret    # 3            ← there it is. Not hidden. Just renamed.
```

The `AttributeError` is not access control. It's a *name mismatch* — you asked for a name that was never created, because the mangling only happens to code written inside the class body.

## 4.3 What mangling is actually for

It exists to solve exactly one problem: **a base class storing state that a subclass might unknowingly clobber.**

```python
class Parent:
    def __init__(self):    self.__id = "parent"     # → _Parent__id
    def who(self):         return self.__id

class Child(Parent):
    def __init__(self):
        super().__init__()
        self.__id = "child"                          # → _Child__id
    def who_child(self):   return self.__id

c = Child()
vars(c)             # {'_Parent__id': 'parent', '_Child__id': 'child'}
c.who()             # 'parent'    ← Parent's own state, intact
c.who_child()       # 'child'
```

Two attributes, both spelled `self.__id`, living side by side without a scratch. Had they been `self._id`, `Child` would have silently destroyed `Parent`'s bookkeeping.

> **Reach for `__name` when you are writing a base class or a mixin that will be subclassed by people you'll never meet. Everywhere else, use `_name`.**

Mangling applies to *any* name in the class body, not just attributes — shelf items and even method names:

```python
class Widget:
    __registry = {}                     # shelf key is '_Widget__registry'
    @classmethod
    def register(cls, k):
        cls.__registry[k] = True        # works: mangled the same way
```

And the trap it comes with — `getattr` receives a *string*, and strings don't get compiled:

```python
hasattr(v, '__secret')          # False
hasattr(v, '_Vault__secret')    # True
getattr(v, '__secret', 'nope')  # 'nope'
```

## 4.4 Dunders — reserved, not yours

`__name__` (leading *and* trailing) is untouched by mangling and reserved by the language. Read them, implement the documented ones (`__init__`, `__repr__`, `__eq__`, `__getattr__`), but **never invent a new one.** A future Python may claim it.

## 4.5 So how do you actually protect something?

Since nothing is private, "protection" in Python means making the *right* thing easy and the wrong thing visible:

| Goal | The Python way |
|---|---|
| "don't read this" | `_name`, and document it |
| "don't write this" | `@property` with no setter (3.5) |
| "don't write anything" | `@dataclass(frozen=True)` (6.7) |
| "don't invent new attributes" | `__slots__` (3.7) or `slots=True` |
| "a subclass must not collide" | `__name` mangling (4.3) |
| "don't export this" | `_name`, or a module `__all__` |
| "this must never be reassigned" | `typing.Final` — checker-only, no runtime effect |

Notice that the first and last are conventions, and the middle ones are mechanisms. Pick the weakest one that communicates your intent — Python programmers read `_name` fluently, and a wall of machinery around a value nobody was going to touch is just noise.

---

# Part 5 — Shelves behind shelves: inheritance

Inheritance introduces **no new rules**. It just means there is more than one shelf behind you.

```
   ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐
   │ D's shelf│ → │ B's shelf│ → │ C's shelf│ → │ A's shelf│ → object
   └──────────┘   └──────────┘   └──────────┘   └──────────┘
        ▲
   ┌────┴─────────┐
   │  MY DRAWER   │      reading walks left to right until it finds the name
   └──────────────┘
```

That row is the **MRO** — method resolution order — and you can print it:

```python
class A:
    tag = "A"
    def hello(self): return "A"
class B(A):
    def hello(self): return "B then " + super().hello()
class C(A):
    tag = "C"
    def hello(self): return "C then " + super().hello()
class D(B, C): pass

[x.__name__ for x in D.__mro__]     # ['D', 'B', 'C', 'A', 'object']
D().hello()                         # 'B then C then A'
D.tag                               # 'C'
'tag' in vars(D)                    # False   ← D's own shelf is empty; it walked
```

## 5.1 Overriding is shadowing, one floor up

`B.hello` doesn't replace `A.hello`. It sits on a *nearer* shelf, so the walk finds it first. `A.hello` is still there and still reachable — `A.hello(d)` calls it directly.

Exactly the same relationship as `a.limit = 99` shadowing `Counter.limit` in Part 1. One model, two floors.

## 5.2 `super()` — "start the walk at the shelf *after* mine"

```python
def hello(self): return "B then " + super().hello()
```

`super()` is not "my parent." It is **"resume the MRO walk from just past me."** In `D().hello()`, `B`'s `super()` finds `C` — not `A` — because `C` is next in `D`'s row. This is why `super()` is right and hard-coding `A.hello(self)` is wrong: only `super()` respects the row the *actual* object was built from.

## 5.3 A shelf value is inherited, and rebinding shadows one branch

```python
class Node:
    registry = []
class Leaf(Node): pass

Leaf.registry.append("x")           # a READ of registry, then a mutation
Node.registry                       # ['x']
Node.registry is Leaf.registry      # True   — same list. Always was.

Leaf.registry = ["own"]             # a WRITE: lands on Leaf's own shelf
Node.registry                       # ['x']
Leaf.registry                       # ['own']
```

Both lines are the same two rules you learned in Part 1, applied to classes instead of instances. Nothing new to memorise — and note how the mutable-shelf-item hazard scales up: one careless `.append()` and the entire class family shares the consequence.

## 5.4 `@override` — say what you meant (3.12)

```python
from typing import override

class Base:
    def run(self) -> str: return "base"

class Sub(Base):
    @override
    def run(self) -> str: return "sub"
```

The decorator tells a type checker: *this is meant to shadow something.* If you rename the base method, or typo the subclass one, you get an error instead of a method that silently never gets called. At runtime it does almost nothing (it sets `Sub.run.__override__ = True`), which is exactly right — this is a message to the checker and to the next reader.

---

# Part 6 — Dataclasses: a machine that writes the drawer for you

Everything so far applies to dataclasses unchanged, because a dataclass **is an ordinary class**. `@dataclass` is a function that reads your class's annotations and writes the boilerplate you were going to write anyway.

## 6.1 What it actually does

```python
from dataclasses import dataclass

@dataclass
class Point:
    x: int
    y: int = 0
```

Recall 2.3: `x: int` created nothing; `y: int = 0` put `0` on the shelf. `@dataclass` reads `__annotations__`, sees both names, and generates methods:

```python
'x' in vars(Point)      # False   ← still nothing. It's a constructor parameter now.
'y' in vars(Point)      # True
Point.y                 # 0

import inspect
inspect.signature(Point.__init__)   # (self, x: int, y: int = 0) -> None
```

And that generated `__init__` does exactly what you'd have typed:

```python
def __init__(self, x: int, y: int = 0) -> None:
    self.x = x          # a WRITE. Into the drawer.
    self.y = y
```

```python
p = Point(1, 2)
vars(p)                 # {'x': 1, 'y': 2}       ← ordinary drawer
p                       # Point(x=1, y=2)        ← generated __repr__
Point(1,2) == Point(1,2)                # True   ← generated __eq__
```

> ## **An annotated name in a dataclass body becomes a *field*: a constructor parameter that lands in the drawer. Its default, if any, sits on the shelf.**

That one sentence plus Part 1 is the entire dataclass story.

## 6.2 Mutable defaults are refused

Since a default sits on the shelf, a mutable default would be shared by every instance — Part 1's basket bug, dressed up. Dataclasses are one of the very few places Python actively stops you:

```python
@dataclass
class Bad:
    items: list = []
# ValueError: mutable default <class 'list'> for field items is not allowed:
#             use default_factory
```

The fix is a factory that runs once per instance:

```python
from dataclasses import field

@dataclass
class Good:
    items: list[str] = field(default_factory=list)

g1, g2 = Good(), Good()
g1.items.append("a")
g1.items                # ['a']
g2.items                # []          ← separate lists
'items' in vars(Good)   # False       ← nothing on the shelf to share
```

> **Any mutable field default is `field(default_factory=...)`. No exceptions.**

## 6.3 `ClassVar` — "stay on the shelf"

This is the accessibility knob you came for. An annotated name becomes a field; `ClassVar` is how you say *don't*.

```python
from typing import ClassVar

@dataclass
class Account:
    owner: str
    balance: float = 0.0

    bank:    ClassVar[str] = "Acme"     # shelf. Shared. Not a parameter.
    created: ClassVar[int] = 0          # shelf. Mutable counter.

    def __post_init__(self) -> None:
        type(self).created += 1         # deliberate write to the shelf
```

```python
inspect.signature(Account)      # (owner: str, balance: float = 0.0) -> None
[f.name for f in fields(Account)]   # ['owner', 'balance']    ← bank, created absent
a1 = Account("ann"); a2 = Account("bo", 10)
a1.bank                 # 'Acme'
Account.created         # 2
vars(a1)                # {'owner': 'ann', 'balance': 0.0}
```

Note `type(self).created += 1`, not `self.created += 1`. The second would be Part 1's `+=` split — a read from the shelf, a write into the drawer, and a counter that stays at 1 forever. Part 7.2.

`ClassVar` is also the *only* way to put a mutable shared thing in a dataclass — `registry: ClassVar[dict] = {}` is fine, precisely because it is not a field and the `default_factory` rule doesn't apply.

## 6.4 The visibility knobs on `field()`

`field()` controls, per member, which generated method can see it. This is accessibility in the plainest sense.

```python
@dataclass
class Session:
    user: str
    token: str = field(repr=False)                        # exists, never printed
    scratch: dict = field(default_factory=dict,
                          compare=False)                  # exists, never compared
```

```python
s1 = Session("ann", "SECRET")
s2 = Session("ann", "SECRET")
s1.scratch["k"] = 1
s1                      # Session(user='ann', scratch={'k': 1})   ← no token
s1 == s2                # True   ← scratch ignored
asdict(s1)              # {'user': 'ann', 'token': 'SECRET', 'scratch': {'k': 1}}
```

`repr=False` on a secret is a genuinely valuable habit — it keeps credentials out of logs and tracebacks. Note that `asdict()` still sees everything: this controls *generated methods*, not access.

| `field(...)` | Effect |
|---|---|
| `default=` / `default_factory=` | the value, or a fresh one per instance |
| `init=False` | not a constructor parameter — set it in `__post_init__` |
| `repr=False` | omitted from `__repr__` |
| `compare=False` | ignored by `__eq__` (and ordering) |
| `kw_only=True` | must be passed by keyword |
| `metadata={...}` | a dict for other libraries to read; Python ignores it |

## 6.5 `field(init=False)` and `__post_init__` — computed members

```python
@dataclass
class Circle:
    radius: float
    area: float = field(init=False)

    def __post_init__(self) -> None:
        self.area = 3.14159 * self.radius ** 2
```

`__post_init__` runs at the end of the generated `__init__`. It's where anything that isn't a plain assignment goes: derived values, validation, registration.

Choosing between this and a `@property`:

| | `field(init=False)` + `__post_init__` | `@property` |
|---|---|---|
| stored in the drawer? | yes | no |
| recomputed on read? | no | yes |
| stays correct if `radius` changes? | **no** | yes |
| shows up in `repr`, `asdict`, `==`? | yes | no |

**Store it if it's expensive and the inputs don't move. Compute it if they do.**

## 6.6 `InitVar` — passes through, never lands

A value the constructor needs but the object should not keep:

```python
from dataclasses import InitVar

@dataclass
class User:
    name: str
    password: InitVar[str]
    hashed: str = field(init=False)

    def __post_init__(self, password: str) -> None:
        self.hashed = "sha:" + password[::-1]       # pretend
```

```python
inspect.signature(User)     # (name: str, password: InitVar[str]) -> None
u = User("ann", "hunter2")
vars(u)                     # {'name': 'ann', 'hashed': 'sha:2retnuh'}   ← no password
u                           # User(name='ann', hashed='sha:2retnuh')
```

`InitVar` members are handed to `__post_init__` as arguments, in declaration order, and then discarded. Exactly the tool for a secret, a config object, or a connection you only need at construction time.

The three-way distinction is worth memorising, since it's the whole accessibility question in miniature:

| Declared as | Constructor param? | Ends up in the drawer? | Shared? |
|---|---|---|---|
| `x: int` | ✓ | ✓ | ✗ |
| `x: ClassVar[int] = 0` | ✗ | ✗ (shelf) | ✓ |
| `x: InitVar[int]` | ✓ | ✗ (discarded) | ✗ |

## 6.7 `frozen=True` — turn the write rule off

```python
@dataclass(frozen=True)
class Frozen:
    x: int

f = Frozen(1)
f.x = 2         # FrozenInstanceError: cannot assign to field 'x'
```

`frozen=True` generates a `__setattr__` that refuses everything (and a `__delattr__` to match). Since the object can't change, dataclasses also gives you `__hash__`, so it works as a dict key or set member:

```python
hash(Frozen(1)) == hash(Frozen(1))      # True
{Frozen(1), Frozen(1)}                  # one element
```

To "change" one, build a new one:

```python
from dataclasses import replace
replace(f, x=9)             # Frozen(x=9)     — f is untouched
```

**Default to frozen for anything that represents a value** — a coordinate, a config, a message, a row read from somewhere. It makes a whole category of aliasing bug impossible, and it costs nothing. Reserve mutability for things that model a changing entity.

(Inside `__post_init__` of a frozen class, `self.x = ...` is also refused. Use `object.__setattr__(self, "x", v)` when you truly must — sparingly, and with a comment.)

## 6.8 `slots=True` and `kw_only=True`

```python
@dataclass(frozen=True, slots=True, kw_only=True)
class Conf:
    host: str
    port: int = 8080

Conf(host="h")          # Conf(host='h', port=8080)
Conf("h")               # TypeError: takes 1 positional argument but 2 were given
vars(Conf(host="h"))    # TypeError: vars() argument must have __dict__ attribute
```

- **`slots=True`** (3.10) — generates `__slots__` for you. Everything in 3.7 applies: smaller, faster, typo-proof, no `cached_property`. One quirk: with slots the defaults live in the generated `__init__` rather than on the shelf, so `Conf.port` gives you a `member_descriptor`, not `8080`.
- **`kw_only=True`** (3.10) — every field must be passed by name. For anything with more than about three fields this is a straight upgrade: call sites become self-documenting, and adding a field can never silently reorder someone's arguments. It also dissolves the inheritance headache in 7.8.

`@dataclass(frozen=True, slots=True, kw_only=True)` is a very good default for value objects.

## 6.9 It's still a class

Methods, classmethods, staticmethods, and properties all work exactly as in Part 3 — they're shelf items, and `@dataclass` only cares about annotated names.

```python
@dataclass
class Rect:
    w: float
    h: float

    @property
    def area(self) -> float:            return self.w * self.h
    @classmethod
    def square(cls, s: float) -> "Rect": return cls(s, s)
    @staticmethod
    def valid(v: float) -> bool:         return v > 0

Rect.square(3)                  # Rect(w=3, h=3)
Rect.square(3).area             # 9
[f.name for f in fields(Rect)]  # ['w', 'h']       ← area is not a field
```

## 6.10 Choosing the container

| You have | Reach for |
|---|---|
| an object with named data and behaviour | `@dataclass` |
| a value that should never change | `@dataclass(frozen=True, slots=True)` |
| data that must stay a real `dict` (JSON on the wire) | `TypedDict` |
| something that must behave like a tuple | `NamedTuple` |
| a fixed set of named constants | `Enum` / `StrEnum` |
| data arriving from outside that must be *validated* | `pydantic` / `attrs` |
| pure behaviour, no data | a module of functions |

`@dataclass` is the default answer, and the bar for the others is "I need the thing only it does."

---

# Part 7 — The traps

Every one of these is the two rules, misapplied. Each entry names which rule.

## 7.1 The mutable class attribute

*(Read walks back; `.append()` is a read.)*

```python
class Basket:
    items = []                      # ✗ one list, forever, for everybody
    def add(self, x): self.items.append(x)
```

```python
class Basket:
    def __init__(self):
        self.items: list[str] = []  # ✓ a fresh list per instance
    def add(self, x): self.items.append(x)
```

Or, better, let a dataclass enforce it:

```python
@dataclass
class Basket:
    items: list[str] = field(default_factory=list)
```

## 7.2 `self.x += 1` on a shelf value

*(A `+=` is a read **and** a write, and they go to different places.)*

```python
class Reg:
    count = 0
    def bump(self): self.count += 1     # reads the shelf, writes the drawer

r, s = Reg(), Reg()
r.bump(); r.bump()
r.count         # 2
s.count         # 0
Reg.count       # 0       ← never moved
vars(r)         # {'count': 2}
```

You wanted a shared counter and got a per-instance one, silently. The fix names the shelf explicitly:

```python
def bump(self):
    type(self).count += 1       # ✓ shared, and subclass-aware
    # Reg.count += 1            # also works; pins it to Reg even for subclasses
```

Pick `type(self)` when subclasses should count separately, `Reg` when they shouldn't. Both are better than the accident.

## 7.3 The bare annotation that creates nothing

*(2.3.)*

```python
class Config:
    debug: bool             # NOT a default. Nothing exists.

Config().debug              # AttributeError: 'Config' object has no attribute 'debug'
```

Write `debug: bool = False`, or make it a dataclass field.

## 7.4 The mutable default argument

*(Same shape, different room — the default is evaluated once, when `def` runs.)*

```python
def add(item, bucket=[]):       # ✗ one list for every call, forever
    bucket.append(item)
    return bucket

def add(item, bucket=None):     # ✓
    bucket = [] if bucket is None else bucket
    bucket.append(item)
    return bucket
```

## 7.5 Shadowing a method by accident

*(Writing stays put — including on top of a name that used to reach a method.)*

```python
class Duck:
    def quack(self): return "QUACK"

d = Duck()
d.quack = "not callable"    # a WRITE into the drawer, blocking the shelf
d.quack()                   # TypeError: 'str' object is not callable
Duck.quack(d)               # 'QUACK'   — the method never went anywhere
```

The usual real-world version: a field and a method with the same name. `__slots__` or a `@dataclass(frozen=True)` both make it impossible.

## 7.6 Attributes invented outside `__init__`

*(Legal, per 2.2 — but it means no reader can know an object's shape.)*

```python
class Job:
    def start(self):    self.started = True
    def finish(self):   self.result = compute()    # exists only sometimes
```

Now `job.result` raises or not depending on history, and no type checker can help. **Declare every attribute in `__init__` (or as a dataclass field), even if the value is `None` at first.**

## 7.7 A comprehension in the class body can't see the shelf

*(A class body is not an enclosing scope for the functions defined inside it — and a comprehension is a function.)*

```python
class Grid:
    n = 3
    xs = [1, 2, 3]
    doubled = [x * 2 for x in xs]       # ✓ works
    scaled  = [x * n for x in xs]       # ✗ NameError: name 'n' is not defined
```

The outermost iterable (`xs`) is evaluated in the class body, so it's fine. Everything *inside* the comprehension runs in its own scope, which skips class scope entirely. Same reason a method must say `self.n` and not just `n`.

Fix: compute it outside the class, or in `__init__`, or inline the value.

## 7.8 Dataclass inheritance and default ordering

*(Fields are collected base-first, and Python won't allow a non-default after a default.)*

```python
@dataclass
class Animal:
    name: str
    legs: int = 4

@dataclass
class Bird(Animal):
    can_fly: bool           # TypeError: non-default argument 'can_fly'
                            #            follows default argument 'legs'
```

`kw_only=True` on both makes the problem vanish, because keyword arguments have no order to violate. That's the recommended fix.

## 7.9 A `@property` over a dataclass field name

*(The property object becomes the field's default, and nothing warns you.)*

```python
@dataclass
class Trap:
    x: int = 0
    @property
    def x(self): return self._x
    @x.setter
    def x(self, v): self._x = v

Trap()          # Trap(x=<property object at 0x...>)      ← the default is the property!
Trap(5)         # Trap(x=5)                               ← works by accident
```

The `@property` assignment lands on the shelf under the name `x`, so `@dataclass` reads it as `x`'s default. Don't cross the streams: give the field a private-ish name and the property a public one, or drop the dataclass field entirely.

## 7.10 `getattr` doesn't mangle

*(4.3.)* `getattr(obj, "__x")` fails; the real name is `_Cls__x`.

## 7.11 `__slots__` quietly doing nothing

*(3.7, rule 1.)* A subclass without its own `__slots__` restores the drawer and every byte you saved. Add `__slots__ = ()`.

---

# Part 8 — The whole thing on one page

## Where a name lives

| You write | Lands | Shared? | Reached by |
|---|---|---|---|
| `x = 1` in the class body | shelf | ✓ | `Cls.x`, `obj.x` |
| `x: int` in the class body | **nowhere** (annotation only) | — | nothing |
| `x: int = 1` in the class body | shelf | ✓ | `Cls.x`, `obj.x` |
| `self.x = 1` anywhere | that object's drawer | ✗ | `obj.x` |
| `obj.x = 1` from outside | that object's drawer | ✗ | `obj.x` |
| `Cls.x = 1` from outside | shelf | ✓ | `Cls.x`, `obj.x` |
| `x: int` in a **dataclass** body | drawer, via generated `__init__` | ✗ | `obj.x` |
| `x: ClassVar[int] = 1` in a dataclass | shelf | ✓ | `Cls.x`, `obj.x` |
| `x: InitVar[int]` in a dataclass | **nowhere** (discarded after init) | — | `__post_init__` only |
| a name in `__slots__` | a fixed pigeonhole, no drawer | ✗ | `obj.x` |

## The four kinds of member

| Written | Gets | Use when |
|---|---|---|
| `def f(self)` | this object | it needs the drawer |
| `@classmethod def f(cls)` | this class | alternative constructor, shelf state |
| `@staticmethod def f()` | nothing | it belongs here by name only |
| `@property def f(self)` | this object, on read | derived data, or a write guard |
| `@cached_property def f(self)` | this object, once | expensive + inputs don't change |

## Accessibility

| Spelling | Runtime effect | Meaning |
|---|---|---|
| `name` | none | public API |
| `_name` | skipped by `import *` | internal, don't rely on it |
| `__name` | **compiled to `_Cls__name`** | subclasses can't collide |
| `__name__` | reserved | language-owned |
| `@property` no setter | write refuses | read-only |
| `frozen=True` | all writes refuse | immutable |
| `__slots__` | new names refuse | fixed shape |
| `Final` | checker only | never reassign |

## Dataclass knobs

| On `@dataclass(...)` | Does |
|---|---|
| `frozen=True` | writes refuse; adds `__hash__` |
| `slots=True` | no drawer; smaller, faster |
| `kw_only=True` | all fields keyword-only; fixes inheritance ordering |
| `order=True` | adds `<`, `<=`, `>`, `>=` |
| `eq=False` | keep identity comparison |

| On `field(...)` | Does |
|---|---|
| `default_factory=list` | fresh mutable per instance — **mandatory** for mutables |
| `init=False` | not a parameter; set in `__post_init__` |
| `repr=False` | hidden from `__repr__` (use for secrets) |
| `compare=False` | ignored by `__eq__` |
| `kw_only=True` | this field only |

## Looking at what's really there

```python
vars(obj)                   # the drawer   (== obj.__dict__)
vars(Cls)                   # the shelf
dir(obj)                    # every name reachable — drawer + all shelves
type(obj).__mro__           # the row of shelves, in walk order
getattr(obj, "x", default)  # read by name, no exception
hasattr(obj, "x")           # is it reachable at all?
setattr(obj, "x", v)        # write by name
dataclasses.fields(Cls)     # the declared fields, with their metadata
inspect.signature(Cls)      # the generated __init__, spelled out
```

---

# Part 9 — When it surprises you, ask three questions

1. **"Which one is it actually in?"** Run `vars(obj)` and `vars(type(obj))` side by side. Nine times out of ten the answer is on screen before you finish reading. If the name is in neither, walk `type(obj).__mro__`.

2. **"Did I read something shared and write something private?"** Any `+=`, `-=`, `|=` on `self.x` where `x` came from the class is this bug. So is every `self.xs.append(...)` where `xs` is a class attribute — remember that `.append()` is a **read**.

3. **"Is there a gatekeeper in the way?"** If a write did something you didn't expect — refused, validated, transformed, or landed somewhere else — look on the shelf for a `property`, a slot descriptor, `frozen=True`, or a custom `__setattr__`. Those are the only four things that can bend rule two.

And the universal move: **print `vars()`.** Stop reasoning about where a value lives; open the drawer.

---

# Part 10 — Real code, using all of it

```python
from dataclasses import dataclass, field, fields, InitVar, replace
from functools import cached_property
from typing import ClassVar, Self

ABSOLUTE_ZERO = -273.15


# --- a value: frozen + slots. No drawer, no writes, hashable, cheap. ---
@dataclass(frozen=True, slots=True)
class Reading:
    sensor: str
    celsius: float
    at: int

    @property                                   # derived, cheap, always correct
    def fahrenheit(self) -> float:
        return self.celsius * 9 / 5 + 32


# --- a mixin: __name mangling, because subclasses must not collide ---
class Auditable:
    def __init__(self) -> None:
        self.__log: list[str] = []              # really _Auditable__log

    def audit(self, event: str) -> None:
        self.__log.append(event)

    @property                                   # read-only view; the list stays ours
    def history(self) -> tuple[str, ...]:
        return tuple(self.__log)


# --- an entity: mutable, with shared class-level state ---
@dataclass
class Sensor(Auditable):
    # fields — one copy per sensor, in its own drawer
    name: str
    readings: list[Reading] = field(default_factory=list)   # never a bare []
    offset: float = field(default=0.0, repr=False)          # noise, keep it out of logs
    calibrate_with: InitVar[float | None] = None            # used at birth, then gone

    # ClassVar — stays on the shelf, shared, never a constructor argument
    MAX_READINGS: ClassVar[int] = 3
    registry: ClassVar[dict[str, "Sensor"]] = {}

    def __post_init__(self, calibrate_with: float | None) -> None:
        Auditable.__init__(self)
        if calibrate_with is not None:
            self.offset = calibrate_with
        type(self).registry[self.name] = self   # a deliberate write to the shelf
        self.audit(f"created {self.name}")

    # needs the class, and honours subclasses
    @classmethod
    def get(cls, name: str) -> Self | None:
        found = cls.registry.get(name)
        return found if isinstance(found, cls) else None

    # needs neither self nor cls, but belongs to this vocabulary
    @staticmethod
    def plausible(celsius: float) -> bool:
        return ABSOLUTE_ZERO <= celsius <= 1000.0

    # needs this sensor's drawer
    def record(self, celsius: float, at: int) -> Reading:
        if not self.plausible(celsius):
            raise ValueError(f"{celsius} is not a temperature")
        r = Reading(self.name, celsius + self.offset, at)
        self.readings.append(r)
        del self.readings[: -self.MAX_READINGS]     # keep the last N
        self.__dict__.pop("average", None)          # empty the cache slot
        self.audit(f"recorded {celsius}")
        return r

    @property                                       # cheap: compute every time
    def latest(self) -> Reading | None:
        return self.readings[-1] if self.readings else None

    @cached_property                                # not cheap: store in the drawer
    def average(self) -> float:
        return sum(r.celsius for r in self.readings) / len(self.readings)


class Thermocouple(Sensor):
    MAX_READINGS: ClassVar[int] = 5     # a nearer shelf, for this branch only
```

Running it:

```python
s = Sensor("kitchen", calibrate_with=0.5)
for i, c in enumerate([20.0, 21.0, 22.0, 23.0]):
    s.record(c, at=i)

len(s.readings)             # 3                    ← MAX_READINGS trimmed it
s.latest                    # Reading(sensor='kitchen', celsius=23.5, at=3)
s.latest.fahrenheit         # 74.3
s.average                   # 22.5                 ← computed, then cached
s.average                   # 22.5                 ← drawer hit, no recompute
s.record(30.0, at=9)
s.average                   # 25.5                 ← cache slot was emptied

t = Thermocouple("furnace")
t.MAX_READINGS              # 5        ← Thermocouple's shelf
s.MAX_READINGS              # 3        ← Sensor's shelf
sorted(Sensor.registry)     # ['furnace', 'kitchen']       ← one shared dict
Sensor.get("furnace").name  # 'furnace'
Thermocouple.get("kitchen") # None     ← cls-aware: a Sensor is not a Thermocouple

sorted(vars(s))             # ['_Auditable__log', 'average', 'name', 'offset', 'readings']

Reading("x", 1.0, 0).celsius = 2.0
# FrozenInstanceError: cannot assign to field 'celsius'
```

That `sorted(vars(s))` line is the essay in one output. The mangled log, the cached average that became a plain drawer entry, the three fields — and conspicuously absent, `MAX_READINGS`, `registry`, and `calibrate_with`, because two of them live on the shelf and one was never kept at all.

Read the class top to bottom and notice how little of it is ceremony. Each decorator answers one question — *does this need the drawer, the class, or neither?* — and each `field()` answers one more: *should anyone be able to see this?*

---

# Appendix

## A. The honest lookup order

Part 1's "drawer, then shelf" is true in every case you'll write. Here is the full sequence `obj.x` actually performs, which explains the two exceptions:

```
   1.  Walk type(obj).__mro__ looking for 'x'.
       Found one with BOTH __get__ and __set__ (a "data descriptor")?
           → it wins outright. Stop. The drawer is never consulted.
              ▸ @property, @x.setter, __slots__ members

   2.  Is 'x' in obj.__dict__ (the drawer)?
           → return it. Stop.

   3.  Back to the MRO result from step 1.
       Has __get__ only (a "non-data descriptor")?  → call it.
              ▸ plain functions (this is binding), @classmethod,
                @staticmethod, @cached_property
       Otherwise                                    → return it as-is.

   4.  Nothing found → call type(obj).__getattr__(obj, 'x') if it exists,
       else raise AttributeError.
```

Step 1 is why a `@property` can refuse a write and why `__slots__` works. Step 3 is why `@cached_property` gets out of the way after the first read. You can watch both:

```python
class P:
    @property
    def v(self): return "from the shelf"

p = P()
p.__dict__['v'] = "smuggled into the drawer"    # bypass the property
vars(p)                 # {'v': 'smuggled into the drawer'}
p.v                     # 'from the shelf'      ← step 1 wins

class Q:
    @cached_property
    def v(self): return "computed"

q = Q()
q.__dict__['v'] = "drawer wins"
q.v                     # 'drawer wins'         ← step 2 wins
```

## B. Descriptors, in one paragraph

A **descriptor** is any object with a `__get__` method, sitting on a shelf. When you reach for it through an instance, Python calls `__get__` instead of handing it over — that's the hook the whole system hangs on. `property`, `classmethod`, `staticmethod`, `cached_property`, `functools.partialmethod`, and the members that `__slots__` creates are all descriptors, and so is every ordinary function (its `__get__` returns a bound method, which is 100% of the magic behind `self`). If it also has `__set__`, it's a **data descriptor** and it outranks the drawer per Appendix A. You will rarely write one by hand — the four decorators cover almost everything — but knowing the word turns four unrelated features into one.

```python
type(vars(Kinds)['inst'])       # <class 'function'>
type(vars(Kinds)['cls_'])       # <class 'classmethod'>
type(vars(Kinds)['stat'])       # <class 'staticmethod'>
type(vars(Kinds)['prop'])       # <class 'property'>
type(vars(Slim)['x'])           # <class 'member_descriptor'>
```

## C. `__getattr__` and `__setattr__` — the last resort

```python
class Loose:
    known = 1
    def __init__(self):   self.own = 2
    def __getattr__(self, name):        # called ONLY when the normal walk fails
        return f"<no {name}>"

l = Loose()
l.known, l.own, l.anything      # (1, 2, '<no anything>')
```

`__getattr__` is the step-4 fallback. It never fires for names that exist, which makes it cheap and mostly safe — good for proxies and lazy loading.

`__setattr__`, by contrast, intercepts **every single write**, including the ones in your own `__init__`. That's how `frozen=True` works, and it's why you need `object.__setattr__` to get past it:

```python
class Locked:
    def __init__(self, x):
        object.__setattr__(self, "x", x)        # the only way in
    def __setattr__(self, name, value):
        raise AttributeError(f"{type(self).__name__} is read-only")
```

There is also `__getattribute__`, which intercepts every *read* — including successful ones. It is easy to make infinitely recursive and almost always the wrong tool. Prefer `__getattr__`.

## D. What landed when

| Version | Relevant to this essay |
|---|---|
| 3.7 | `@dataclass`, `field()`, `InitVar`, `__post_init__` |
| 3.8 | `functools.cached_property`, `Final`, positional-only params |
| 3.10 | `@dataclass(slots=True, kw_only=True)`, `field(kw_only=True)` |
| 3.11 | `Self`, `StrEnum`, `dataclasses` speedups |
| **3.12** | **`@override`, `type X = ...`, `class C[T]` (PEP 695)** |
| 3.13 | `@dataclass` field defaults for `__replace__`, `ReadOnly` for TypedDict |
| 3.14 | lazy annotations (PEP 649) — class annotations are computed on demand |

That last one is worth a note if you introspect: on 3.14 the raw shelf holds `__annotate_func__` rather than `__annotations__`, though `Cls.__annotations__` still works exactly as before. Read annotations through `typing.get_type_hints()` or `dataclasses.fields()` rather than poking at `vars(Cls)` and you'll never notice.

## E. Where annotations actually run

Part 2.3 said nothing reads `x: int` at runtime. Three things go and read it deliberately:

- **`@dataclass`** — reads `__annotations__` to decide what the fields are. This whole essay's Part 6.
- **`pydantic` / `attrs`** — read them to build real runtime validators. What you want at a boundary where data arrives from outside.
- **`typing.get_type_hints(obj)`** — the general door, used by FastAPI, serialisers, and DI frameworks.

The annotation still checks nothing by itself. Something has to come and look.

---

# The one thing to remember

> ## **Every object has its own drawer. Every class has one shelf behind it. Reading walks back — drawer, then shelf, then the shelves behind that. Writing stays put — it lands in your own drawer, always.**
>
> **A method is just a shelf item that happens to be a function, and reaching it through an instance pre-fills `self`. `@classmethod` pre-fills the class instead; `@staticmethod` pre-fills nothing; `@property` and `__slots__` are gatekeepers that get first refusal on the walk. A dataclass field is an annotated name that the generated `__init__` writes into the drawer — and `ClassVar` is how you say "no, leave this on the shelf."**
>
> **And nothing is private. `_name` is a message, `__name` is a rename, and the only real locks are a property with no setter, `frozen=True`, and `__slots__`.**

That is the whole system. Say it out loud with your real class and the answer falls out.

And on the days a value appears in the wrong place: **print `vars(obj)` and `vars(type(obj))`, and ask which one you wrote to.**
