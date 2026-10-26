# Never Be Confused by a Python Decorator Again

*Modern Python — 3.12 and later. Every output in this essay is real Python output.*

There is **one** mental model in this essay, and it fits on one line. Not one model for function decorators and another for class decorators, not a special case for arguments, not a separate story for `@property`. One line.

Learn it in Part 1, then watch it explain every decorator you will ever write or read.

---

# Part 1 — The mental model: `@d` is `f = d(f)`

```
   @d                          def f(...):
   def f(...):        ≡            body
       body                    f = d(f)
```

That's it. The `@` line is **syntax sugar for one assignment**, performed the moment the `def` finishes.

> ## **A decorator is a function that takes the thing you just defined and returns whatever should have that name instead.**

## Watch it once

```python
def shout(fn):
    def wrapper(*a, **k):
        return fn(*a, **k).upper()
    return wrapper

@shout
def greet(n): return f"hi {n}"
```

The `@shout` line is not doing anything mysterious. Written out by hand, it is:

```python
def greet2(n): return f"hi {n}"
greet2 = shout(greet2)

greet("ann")            # 'HI ANN'
greet2("ann")           # 'HI ANN'      — identical. There is no difference.
```

Decorators are not a feature of functions. They are a feature of **names**: `@` gives one function the chance to replace another before the name is bound.

## Three questions, always the same three

> ## **"What goes IN? What comes OUT? Which NAME gets it?"**

| | |
|---|---|
| **IN** | the object defined below the `@` — a function, or a class |
| **OUT** | whatever the decorator returns — *anything at all* |
| **NAME** | the name in the `def`/`class` line gets rebound to OUT |

## OUT really can be anything

The single most freeing fact about decorators: **nothing requires a decorator to return a function.**

```python
def to_string(fn): return "I am a string now"

@to_string
def gone(): pass

gone                    # 'I am a string now'      — the name now holds a str
```

That's a silly example, but it's the mechanism behind the ones you use daily:

| Decorator | Returns |
|---|---|
| `@property` | a `property` object |
| `@staticmethod` | a `staticmethod` object |
| `@classmethod` | a `classmethod` object |
| `@dataclass` | the same class, with methods added |
| `@functools.cache` | a wrapper function with `.cache_info()` bolted on |
| `@contextmanager` | a factory that produces context managers |

Once you stop expecting "function in, function out", `@property` stops being a special case and becomes an ordinary decorator that happens to return a descriptor.

That's the model. Now we just apply it.

---

# Part 2 — The wrapper shape

The most common decorator returns a **new function that calls the old one**. There is a standard shape, and it's worth typing from memory until it's automatic:

```python
import functools

def decorator(fn):                          # 1. take the function
    @functools.wraps(fn)                    # 4. keep its identity (Part 3)
    def wrapper(*args, **kwargs):           # 2. build a replacement
        # ...before...
        result = fn(*args, **kwargs)        # 3. call the original
        # ...after...
        return result                       # 5. RETURN THE RESULT
    return wrapper                          # 6. RETURN THE WRAPPER
```

Six lines that matter, and two of them are `return`. Those two are where nearly every bug lives.

## 2.1 `*args, **kwargs` — accept everything, pass everything

The wrapper is standing in for a function whose signature it doesn't know. Take everything, forward everything.

```python
def wrapper(*args, **kwargs):
    return fn(*args, **kwargs)
```

If your decorator only works on one specific signature, it isn't a decorator — it's a helper function with confusing syntax.

## 2.2 The two `return`s

Forget the inner one and your decorated function silently returns `None`:

```python
def broken(fn):
    @functools.wraps(fn)
    def wrapper(*a, **k):
        fn(*a, **k)                 # ← no return
    return wrapper

@broken
def add(x, y): return x + y

add(1, 2)               # None
```

Forget the outer one and the *decorator* returns `None`, so the name becomes `None` and calling it raises `TypeError: 'NoneType' object is not callable`.

**When a decorated function misbehaves, count the `return`s first.**

## 2.3 A real one

```python
import time

def timed(fn):
    @functools.wraps(fn)
    def wrapper(*a, **k):
        start = time.perf_counter()
        try:
            return fn(*a, **k)
        finally:
            wrapper.last_ms = (time.perf_counter() - start) * 1000
    wrapper.last_ms = 0.0
    return wrapper
```

Note `try/finally` — timing should record even when the function raises. And note that `wrapper.last_ms` works because a function is an object with a drawer; you can hang state on it.

---

# Part 3 — `functools.wraps`

A wrapper is a different function, and by default it says so:

```python
def plain(fn):
    def wrapper(*a, **k): return fn(*a, **k)
    return wrapper

@plain
def alpha(x: int, y: str = "d") -> bool:
    """Alpha docs."""
    return True

alpha.__name__          # 'wrapper'                       ✗
alpha.__doc__           # None                            ✗
alpha.__qualname__      # 'plain.<locals>.wrapper'        ✗
inspect.signature(alpha)  # (*a, **k)                     ✗
```

Your function's name, docstring, and signature have all been replaced by the wrapper's. `help()` is useless, tracebacks are confusing, and any tool that reads signatures (pytest fixtures, FastAPI routing, `functools.singledispatch`) is now looking at `(*a, **k)`.

One line fixes all of it:

```python
def wrapped(fn):
    @functools.wraps(fn)
    def wrapper(*a, **k): return fn(*a, **k)
    return wrapper

@wrapped
def beta(x: int, y: str = "d") -> bool:
    """Beta docs."""
    return True

beta.__name__           # 'beta'                          ✓
beta.__doc__            # 'Beta docs.'                    ✓
beta.__qualname__       # 'beta'                          ✓
inspect.signature(beta) # (x: int, y: str = 'd') -> bool  ✓
beta.__wrapped__        # <function beta at 0x...>        ← the original
```

`@functools.wraps(fn)` is itself just a decorator applied to `wrapper`. It copies `__module__`, `__name__`, `__qualname__`, `__doc__`, the annotations, and `__type_params__`; it *updates* `__dict__`; and — the part that does the heavy lifting — it sets `__wrapped__` to the original.

That last one is why `inspect.signature` recovers the true signature: it follows the `__wrapped__` chain. (The exact tuple lives in `functools.WRAPPER_ASSIGNMENTS` and has shifted between versions — 3.12 added `__type_params__`, 3.14 swapped `__annotations__` for `__annotate__` — so read the constant rather than memorising it.)

> ### **Every decorator you write gets `@functools.wraps(fn)`. No exceptions, no judgement calls.**

For class-based decorators the equivalent is the function form: `functools.update_wrapper(self, fn)` inside `__init__` (Part 7).

---

# Part 4 — Decorators with arguments: one more layer

`@d(x)` is still just the model, applied to whatever `d(x)` evaluates to:

```
   @repeat(3)                       def ping(): ...
   def ping(): ...        ≡         ping = repeat(3)(ping)
```

So `repeat(3)` must itself return a decorator. That's three nested functions — the layer count is the whole difficulty:

```python
def repeat(n):                              # 1. takes the ARGUMENTS
    def decorator(fn):                      # 2. takes the FUNCTION
        @functools.wraps(fn)
        def wrapper(*a, **k):               # 3. takes the CALL
            return [fn(*a, **k) for _ in range(n)]
        return wrapper
    return decorator

@repeat(3)
def ping(): return "pong"

ping()                  # ['pong', 'pong', 'pong']
repeat(3)(lambda: "pong")()     # ['pong', 'pong', 'pong']   ← by hand
```

| Layer | Receives | Returns | Runs |
|---|---|---|---|
| `repeat` | the config | a decorator | once, at the `@` line |
| `decorator` | the function | the wrapper | once, at definition |
| `wrapper` | the call's args | the result | every call |

The mnemonic: **no arguments → two layers; arguments → three.** If you're one layer off, the symptom is unmistakable — `@repeat` without parentheses passes the *function* as `n`.

## 4.1 Making the parentheses optional

Sometimes you want both `@trace` and `@trace(prefix="LOUD")` to work. The trick is a keyword-only signature plus a check:

```python
def trace(fn=None, *, prefix="TRACE"):
    def decorator(f):
        @functools.wraps(f)
        def wrapper(*a, **k):
            print(f"{prefix}: {f.__name__}{a}")
            return f(*a, **k)
        return wrapper
    return decorator if fn is None else decorator(fn)

@trace
def one(x): return x

@trace(prefix="LOUD")
def two(x): return x

one(1)      # TRACE: one(1,)
two(2)      # LOUD: two(2,)
```

`@trace` passes the function as `fn`, so we decorate immediately. `@trace(prefix=...)` passes nothing positional, so `fn is None` and we return the decorator. The `*` forcing keyword-only arguments is what makes the two cases unambiguous — copy that detail.

This is how `@dataclass` and `@dataclass(frozen=True)` both work.

---

# Part 5 — Stacking: bottom-up

```
   @a                             def f(): ...
   @b                    ≡        f = a(b(f))
   def f(): ...
```

**The one nearest the `def` is applied first.** Read a decorator stack from the bottom up.

```python
def a(fn):
    def w(*ar, **k): return "a(" + fn(*ar, **k) + ")"
    return w
def b(fn):
    def w(*ar, **k): return "b(" + fn(*ar, **k) + ")"
    return w

@a
@b
def core(): return "core"

core()                  # 'a(b(core))'
```

So the **outermost decorator wraps last, and therefore runs first** at call time. If `@timed` is above `@retry`, the timer measures all the retries; the other way round, each attempt is timed separately. Neither is wrong — but you have to know which one you asked for.

```python
@timed              # measures the whole thing, retries included
@retry(times=4)
def fetch(): ...
```

---

# Part 6 — Decorating methods

A method is just a function in a class body, so nothing changes. `self` arrives in `*args` like any other argument and is forwarded untouched:

```python
class API:
    @timed
    def fetch(self, uid): ...
```

`fetch` becomes `wrapper`, which is still a plain function in the class body, so the normal binding happens and `self` lands in `args[0]`.

## 6.1 Order matters with `@property`, `@classmethod`, `@staticmethod`

These three return **descriptors**, not functions — so they must be **outermost**. Your decorator has to see a function.

```python
class Ok:
    @property                       # ✓ outermost
    @logged
    def value(self): return 1

    @classmethod                    # ✓ outermost
    @logged
    def make(cls): return cls.__name__

    @staticmethod                   # ✓ outermost
    @logged
    def util(): return "u"
```

Reverse it and you get something that looks fine and isn't:

```python
class WrongDef:
    @logged                         # ✗ wraps the property OBJECT
    @property
    def value(self): return 1

type(WrongDef.__dict__["value"])    # <class 'function'>   ← not a property at all
WrongDef().value                    # <bound method ...>   ← a method, not 1
WrongDef().value()                  # TypeError: 'property' object is not callable
```

No error at definition time; the failure surfaces somewhere else entirely. The rule is short:

> ### **`@property`, `@classmethod`, `@staticmethod`, and `@abstractmethod` go on top. Your decorator goes underneath, next to the `def`.**

(`@abstractmethod` is the one exception to "on top": it must be **innermost**, closest to the `def`, because the other descriptors need to see its marker. So `@property` then `@abstractmethod` then `def`.)

One dead end worth knowing about: `@classmethod` stacked on `@property` — a "class-level property" — worked from 3.9, was deprecated in 3.11, and **was removed in 3.13**. It now silently produces a bound method rather than a value:

```python
class C:
    @classmethod
    @property
    def x(cls): return 1

C.x                     # <bound method x of <class 'C'>>     — not 1
```

If you need a computed attribute on the class itself, put a `@property` on a **metaclass** (essay 05, Part 7). That's the only spelling that still works.

```python
class Iface(ABC):
    @property
    @abstractmethod
    def size(self): ...

    @classmethod
    @abstractmethod
    def build(cls): ...

sorted(Iface.__abstractmethods__)   # ['build', 'size']
```

---

# Part 7 — Class-based decorators

If the decorator needs **state** — a counter, a cache, configuration you want to inspect — an object with `__call__` reads better than a closure.

```python
class CountCalls:
    def __init__(self, fn):
        functools.update_wrapper(self, fn)      # the `wraps` equivalent
        self.fn = fn
        self.calls = 0

    def __call__(self, *a, **k):
        self.calls += 1
        return self.fn(*a, **k)

@CountCalls
def hello(): return "hi"

hello(); hello(); hello()
hello.calls             # 3
hello.__name__          # 'hello'
type(hello)             # <class 'CountCalls'>
```

Remember the model: `hello = CountCalls(hello)`. The name now holds an *instance*, and `hello()` is `CountCalls.__call__`.

## 7.1 The descriptor problem — and the fix

A class-based decorator breaks the moment you put it on a method, and the reason is worth understanding rather than memorising.

```python
class Bad:
    def __init__(self, fn): self.fn = fn
    def __call__(self, *a, **k): return self.fn(*a, **k)

class T:
    @Bad
    def m(self): return "ok"

T().m()
# TypeError: T.m() missing 1 required positional argument: 'self'
```

A plain function on a class is a **non-data descriptor** — reaching it through an instance binds `self`. A `Bad` instance isn't a descriptor at all, so no binding happens, and `self` never gets passed.

The fix is to *be* a descriptor:

```python
class Good(Bad):
    def __get__(self, obj, objtype=None):
        if obj is None:
            return self                              # accessed on the class
        return functools.partial(self.__call__, obj) # pre-fill self, like binding

class T:
    @Good
    def n(self): return "ok"

T().n()                 # 'ok'
```

Four lines, and they replicate exactly what a function's own `__get__` does.

> **A closure-based decorator has none of this problem — it returns a plain function, which is already a descriptor. That is the strongest reason to prefer closures unless you genuinely need the state.**

---

# Part 8 — Decorating classes

The model is unchanged: `cls = d(cls)`.

```python
REGISTRY: dict[str, type] = {}

def register(name):
    def decorate(cls):
        REGISTRY[name] = cls
        cls.registered_as = name
        return cls                          # ← return the class!
    return decorate

@register("users")
class UserAPI: pass

REGISTRY                    # {'users': <class 'UserAPI'>}
UserAPI.registered_as       # 'users'
```

Three things a class decorator does well:

- **Register** the class somewhere.
- **Add** attributes or methods to it.
- **Return a different class** entirely (rare, and confusing — `@dataclass(slots=True)` does it, which is why the decorated class isn't the same object).

And the reason to reach for one at all, from the metaclass essay: **a class decorator is the lightest of the four levers.** It touches one class, doesn't infect the hierarchy, and can't cause a metaclass conflict. Prefer it, then `__init_subclass__`, and only then a metaclass.

```python
def add_repr(cls):
    def __repr__(self):
        fields = ", ".join(f"{k}={v!r}" for k, v in vars(self).items())
        return f"{type(self).__name__}({fields})"
    cls.__repr__ = __repr__
    return cls

@add_repr
class Pt:
    def __init__(self, x, y): self.x, self.y = x, y

Pt(1, 2)                # Pt(x=1, y=2)
```

That is `@dataclass` in miniature — which is exactly why `@dataclass` is a decorator and not a metaclass.

---

# Part 9 — The ones Python gives you

You will read these far more often than you'll write your own. Grouped by what they're for.

## 9.1 Access and binding

| Decorator | Returns | Does |
|---|---|---|
| `@property` | `property` | method reachable as data |
| `@x.setter` / `@x.deleter` | `property` | add a write / delete gate |
| `@staticmethod` | `staticmethod` | no `self`, no `cls` |
| `@classmethod` | `classmethod` | `cls` instead of `self` |
| `@functools.cached_property` | descriptor | compute once, store in the instance |

Since 3.10, a `staticmethod` object is directly callable, which used to be a genuine annoyance:

```python
class S:
    @staticmethod
    def f(): return "static"

S.__dict__["f"]()       # 'static'      — works since 3.10
```

## 9.2 Caching

```python
@functools.cache                    # unbounded; 3.9+. This is lru_cache(maxsize=None)
def fib(n): return n if n < 2 else fib(n-1) + fib(n-2)

fib(30)                 # 832040
fib.cache_info()        # CacheInfo(hits=28, misses=31, maxsize=None, currsize=31)
fib.cache_clear()

@functools.lru_cache(maxsize=2)     # bounded, evicts least-recently-used
def sq(n): return n * n
```

Both require **hashable arguments** and are only correct for **pure functions**. And `@cache` on a method keeps every `self` alive forever — a memory leak with a polite name. For per-instance caching use `@cached_property`; for per-call caching on a method, make sure the instances are short-lived or the class is frozen and small.

## 9.3 Writing decorators

| Tool | Use |
|---|---|
| `@functools.wraps(fn)` | on every wrapper you write |
| `functools.update_wrapper(obj, fn)` | the same, for class-based decorators |
| `functools.partial(fn, *a)` | pre-fill arguments (not a decorator, but always nearby) |
| `functools.partialmethod` | the same, in a class body |

## 9.4 Generating code

| Decorator | Generates |
|---|---|
| `@dataclasses.dataclass` | `__init__`, `__repr__`, `__eq__`, `__match_args__`, and more |
| `@functools.total_ordering` | the three ordering dunders you didn't write |
| `@enum.unique` | rejects duplicate values |
| `@enum.verify(UNIQUE / CONTINUOUS / NAMED_FLAGS)` | validates the member set (3.11+) |
| `@enum.member` / `@enum.nonmember` | force a class-body name in or out of the members (3.11+) |

```python
from enum import Enum, unique, verify, CONTINUOUS

@unique
class Bad(Enum):
    A = 1
    B = 1
# ValueError: duplicate values found in <enum 'Bad'>: B -> A

@verify(CONTINUOUS)
class Gappy(Enum):
    A = 1
    C = 3
# ValueError: invalid enum 'Gappy': missing values 2
```

## 9.5 Dispatch

`@singledispatch` turns one function into several, chosen by the first argument's type:

```python
@functools.singledispatch
def describe(x): return f"something: {x!r}"

@describe.register
def _(x: int): return f"int: {x}"

@describe.register
def _(x: list): return f"list of {len(x)}"

@describe.register(str)             # explicit form, when there's no annotation
def _(x): return f"str: {x!r}"

describe(1)             # 'int: 1'
describe([1, 2])        # 'list of 2'
describe("hi")          # "str: 'hi'"
describe(1.5)           # "something: 1.5"       ← the base case
```

`@singledispatchmethod` is the same thing inside a class, dispatching on the argument after `self`. Both are the Pythonic answer to a chain of `isinstance` checks in a function you don't own — a third party can register a new type without touching your code.

## 9.6 Contexts

```python
from contextlib import contextmanager, asynccontextmanager

@contextmanager
def scope(n):
    print(f"enter {n}")
    yield n
    print(f"exit {n}")

with scope("a") as v:
    print("body", v)
# enter a / body a / exit a
```

A `@contextmanager` result is *also* usable as a decorator, which is a genuinely useful and little-known trick:

```python
@scope("as-decorator")
def work(): print("working")

work()
# enter as-decorator / working / exit as-decorator
```

## 9.7 Contracts for the type checker

These mostly do nothing at runtime. That's the point — they're messages to `mypy`/`pyright` and to the next reader.

| Decorator | Says |
|---|---|
| `@abc.abstractmethod` | subclasses must implement this (enforced by `ABCMeta`) |
| `@typing.overload` | this name has several typed signatures |
| `@typing.final` | do not subclass / do not override |
| `@typing.override` (3.12) | this is meant to override a base method |
| `@typing.runtime_checkable` | allow `isinstance` against this `Protocol` |
| `@typing.no_type_check` | skip this one |
| `@typing.dataclass_transform` | "my decorator behaves like `@dataclass`" — teaches the checker about your library |
| `@warnings.deprecated` (3.13) | emit a `DeprecationWarning` *and* tell the checker |

```python
from typing import overload, final, override

@overload
def parse(x: int) -> int: ...
@overload
def parse(x: str) -> str: ...
def parse(x): return x              # ← the only one that exists at runtime

typing.get_overloads(parse)         # the two stubs, if you need them

class Sub(Base):
    @override
    def run(self): return "sub"

Sub.run.__override__                # True     — a runtime marker, nothing more
```

`@deprecated` is the newest and the most immediately useful:

```python
from warnings import deprecated       # 3.13+; typing_extensions before that

@deprecated("use new_api instead")
def old_api(): return 1

old_api()       # DeprecationWarning: use new_api instead
```

## 9.8 One more

`@atexit.register` runs a function at interpreter shutdown. It's the clearest example in the standard library of a decorator used purely for its **side effect** — it returns the function unchanged, and the point is entirely that it got registered.

---

# Part 10 — Async and typed decorators

## 10.1 Decorating a coroutine function

A wrapper around an `async def` must itself be `async def`, and must `await`:

```python
def timed_async(fn):
    @functools.wraps(fn)
    async def wrapper(*a, **k):                 # ← async
        start = time.perf_counter()
        try:
            return await fn(*a, **k)            # ← await
        finally:
            wrapper.last_ms = (time.perf_counter() - start) * 1000
    return wrapper
```

Wrap an `async def` in a *sync* wrapper and you get no error — you get a coroutine object handed back unawaited, and a `RuntimeWarning` much later. If your decorator must handle both, branch on `inspect.iscoroutinefunction(fn)` and return one of two wrappers.

## 10.2 Typing a decorator: `ParamSpec`

Without help, a type checker sees your wrapper as `(*args: Any, **kwargs: Any) -> Any` and every decorated function loses its types. `ParamSpec` (3.10) fixes that:

```python
from collections.abc import Callable
from typing import ParamSpec, TypeVar

P = ParamSpec("P")
R = TypeVar("R")

def timed(fn: Callable[P, R]) -> Callable[P, R]:
    @functools.wraps(fn)
    def wrapper(*a: P.args, **k: P.kwargs) -> R:
        return fn(*a, **k)
    return wrapper
```

`P` captures "whatever parameters the original had" and `R` its return type, so the decorated function keeps its full signature at the call site. This is the difference between a decorator that helps and one that quietly turns off type checking for everything it touches.

In 3.12 you can also write the PEP 695 form:

```python
def timed[**P, R](fn: Callable[P, R]) -> Callable[P, R]: ...
```

If the decorator *changes* the signature — adds a parameter, changes the return type — say so honestly (`Callable[P, list[R]]` for `@repeat`). Don't reach for `Any`.

---

# Part 11 — The traps

## 11.1 Forgetting a `return`

*(2.2.)* Inner `return` missing → the function returns `None`. Outer `return` missing → the *name* becomes `None`. Count them first.

## 11.2 Forgetting `@functools.wraps`

*(Part 3.)* Costs you the name, the docstring, and the signature — and breaks every tool that reads them.

## 11.3 Wrong number of layers

*(Part 4.)* `@repeat` without parentheses passes the function in as `n`. `@repeat(3)` on a two-layer decorator passes `3` where a function was expected. The error message names whichever argument got the wrong thing.

## 11.4 Decorator order with `@property` / `@classmethod`

*(6.1.)* They must be outermost. `@abstractmethod` must be innermost.

## 11.5 The decorator runs at import time

`@` executes when the module is imported, not when the function is called. A decorator that opens a file, hits the network, or reads config does it at import. Keep the decorator body cheap; put the work in the wrapper.

## 11.6 Class-based decorators on methods

*(7.1.)* No `__get__`, no `self`. Add the four-line descriptor, or use a closure.

## 11.7 Mutable state shared across all calls

A closure variable or an attribute on the wrapper is **one copy, for the whole program**. That's correct for a counter or a cache, and a bug for anything per-call or per-instance.

## 11.8 `@cache` on a method leaks

*(9.2.)* The cache key includes `self`, so every instance ever passed is kept alive forever. Use `@cached_property`, or cache a module-level function that takes plain values.

## 11.9 Losing the exception context

Swallowing exceptions in a wrapper, or re-raising without `from`, destroys the traceback. Use `raise NewError(...) from exc`, and prefer `try/finally` over `try/except` when you only need cleanup.

## 11.10 A decorator that can't be turned off

Anything doing logging, retries, or timing should be configurable — a module-level flag, an argument, or an environment check. A decorator baked into a hot path with no off switch is a performance problem you can't remove without editing every call site.

---

# Part 12 — The whole thing on one page

## The rewrites

```python
@d                  →   f = d(f)
def f(): ...

@d(x)               →   f = d(x)(f)
def f(): ...

@a                  →   f = a(b(f))          # bottom-up
@b
def f(): ...

@d                  →   C = d(C)             # classes are identical
class C: ...
```

## The shapes

```python
# no arguments — two layers
def deco(fn):
    @functools.wraps(fn)
    def wrapper(*a, **k):
        return fn(*a, **k)
    return wrapper

# with arguments — three layers
def deco(cfg):
    def decorate(fn):
        @functools.wraps(fn)
        def wrapper(*a, **k):
            return fn(*a, **k)
        return wrapper
    return decorate

# optional arguments
def deco(fn=None, *, cfg=1):
    def decorate(f): ...
    return decorate if fn is None else decorate(fn)

# class-based, safe on methods
class Deco:
    def __init__(self, fn):
        functools.update_wrapper(self, fn); self.fn = fn
    def __call__(self, *a, **k):
        return self.fn(*a, **k)
    def __get__(self, obj, objtype=None):
        return self if obj is None else functools.partial(self.__call__, obj)

# class decorator
def deco(cls):
    cls.extra = 1
    return cls

# typed, signature-preserving
def deco[**P, R](fn: Callable[P, R]) -> Callable[P, R]:
    @functools.wraps(fn)
    def wrapper(*a: P.args, **k: P.kwargs) -> R:
        return fn(*a, **k)
    return wrapper
```

## The stdlib set

| Group | Decorators |
|---|---|
| **access** | `@property`, `@x.setter`, `@x.deleter`, `@staticmethod`, `@classmethod` |
| **caching** | `@functools.cache`, `@lru_cache(maxsize=…)`, `@cached_property` |
| **authoring** | `@functools.wraps`, `functools.update_wrapper`, `functools.partial(method)` |
| **generating** | `@dataclass`, `@total_ordering`, `@enum.unique`, `@enum.verify`, `@enum.member`/`nonmember` |
| **dispatch** | `@functools.singledispatch`, `@singledispatchmethod` |
| **contexts** | `@contextlib.contextmanager`, `@asynccontextmanager` |
| **contracts** | `@abstractmethod`, `@overload`, `@final`, `@override`, `@runtime_checkable`, `@no_type_check`, `@dataclass_transform`, `@warnings.deprecated` |
| **side effects** | `@atexit.register` |

## Ordering rules

| Rule | Because |
|---|---|
| bottom decorator applies first | `@a @b def f` is `a(b(f))` |
| outermost runs first at call time | it wrapped last |
| `@property`/`@classmethod`/`@staticmethod` outermost | they return descriptors, not functions |
| `@abstractmethod` innermost | the descriptor above it must see the marker |

---

# Part 13 — When it surprises you, ask three questions

1. **"What is the name actually bound to now?"** Print it. `print(f, type(f))`. If it says `<class 'NoneType'>` you forgot a `return`; if it says `function wrapper` you forgot `@wraps`; if it's a `property` object where you wanted a function, your stack is upside down.

2. **"How many layers do I have, and how many do I need?"** Arguments → three. No arguments → two. Then check whether the `@` line has parentheses. Nearly every "decorator doesn't work" question is this mismatch.

3. **"When does this run — import time or call time?"** Everything outside the innermost `def` runs once, at import. Everything inside runs per call. Put the work in the right place.

And the universal move: **write out `f = d(f)` by hand.** The sugar is what's confusing; the assignment never is.

---

# Part 14 — Real code, using all of it

```python
import functools
import inspect
import time
from collections.abc import Callable
from typing import Any, ParamSpec, TypeVar, get_type_hints

P = ParamSpec("P")
R = TypeVar("R")

REGISTRY: dict[str, type] = {}


# --- a class decorator: the lightest lever there is ---
def register(name: str) -> Callable[[type], type]:
    def decorate(cls: type) -> type:
        REGISTRY[name] = cls
        cls.registered_as = name
        return cls
    return decorate


# --- no arguments: two layers, signature preserved ---
def timed(fn: Callable[P, R]) -> Callable[P, R]:
    @functools.wraps(fn)
    def wrapper(*a: P.args, **k: P.kwargs) -> R:
        start = time.perf_counter()
        try:
            return fn(*a, **k)
        finally:
            wrapper.last_ms = (time.perf_counter() - start) * 1000
    wrapper.last_ms = 0.0
    return wrapper


# --- arguments: three layers ---
def retry(times: int = 3, on: tuple[type[BaseException], ...] = (Exception,)):
    def decorate(fn: Callable[P, R]) -> Callable[P, R]:
        @functools.wraps(fn)
        def wrapper(*a: P.args, **k: P.kwargs) -> R:
            last: BaseException | None = None
            for attempt in range(1, times + 1):
                try:
                    return fn(*a, **k)
                except on as exc:
                    last = exc
                    print(f"attempt {attempt} failed: {exc}")
            raise RuntimeError(f"{fn.__name__} failed after {times} attempts") from last
        return wrapper
    return decorate


# --- reads the annotations the function already declares ---
def validate(fn: Callable[P, R]) -> Callable[P, R]:
    sig = inspect.signature(fn)
    hints = get_type_hints(fn)              # resolves string annotations

    @functools.wraps(fn)
    def wrapper(*a: P.args, **k: P.kwargs) -> R:
        bound = sig.bind(*a, **k)
        bound.apply_defaults()
        for name, value in bound.arguments.items():
            want = hints.get(name)
            if isinstance(want, type) and not isinstance(value, want):
                raise TypeError(
                    f"{name} must be {want.__name__}, got {type(value).__name__}"
                )
        return fn(*a, **k)
    return wrapper


# --- class-based, because it holds state; __get__ so it works on a method ---
class CallCounter:
    def __init__(self, fn: Callable[..., Any]):
        functools.update_wrapper(self, fn)
        self.fn = fn
        self.calls = 0

    def __call__(self, *a: Any, **k: Any) -> Any:
        self.calls += 1
        return self.fn(*a, **k)

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        return functools.partial(self.__call__, obj)

    def __repr__(self) -> str:
        return f"<CallCounter {self.__name__} calls={self.calls}>"


@register("users")
class UserAPI:
    def __init__(self) -> None:
        self._fail_left = 2

    @timed                                  # measures ALL the retries
    @retry(times=4, on=(ConnectionError,))
    def fetch(self, uid: int) -> str:
        if self._fail_left:
            self._fail_left -= 1
            raise ConnectionError("network blip")
        return f"user-{uid}"

    @validate
    def rename(self, uid: int, name: str) -> str:
        return f"{uid} -> {name}"

    @CallCounter
    def ping(self) -> str:
        return "pong"

    @functools.cached_property
    def config(self) -> dict[str, int]:
        print("building config once")
        return {"timeout": 30}

    @staticmethod                           # outermost
    def normalise(name: str) -> str:
        return name.strip().lower()

    @classmethod                            # outermost
    def create(cls) -> "UserAPI":
        return cls()
```

Running it:

```python
api = UserAPI.create()

REGISTRY                                # {'users': <class 'UserAPI'>}
UserAPI.registered_as                   # 'users'

api.fetch(7)
# attempt 1 failed: network blip
# attempt 2 failed: network blip
# 'user-7'

api.fetch.__name__                      # 'fetch'                      ← wraps
inspect.signature(UserAPI.fetch)        # (self, uid: int) -> str      ← wraps

api.rename(1, "Ann")                    # '1 -> Ann'
api.rename("nope", "Ann")               # TypeError: uid must be int, got str

api.ping(); api.ping()
UserAPI.__dict__["ping"]                # <CallCounter ping calls=2>

api.config; api.config
# building config once                  ← exactly once

UserAPI.normalise("  ANN ")             # 'ann'
```

Read the stack on `fetch` bottom-up: `retry` wraps the real method, `timed` wraps that. So the timer covers every attempt. Swap the two lines and each attempt gets timed separately — same decorators, different measurement, and the only thing that changed is which one is nearer the `def`.

And notice what none of them do: none inspect their caller, none use `__getattribute__`, none need a metaclass. Every one is `f = d(f)` with a wrapper in between.

---

# Appendix

## A. Third-party decorators you'll meet

Not stdlib, but ubiquitous enough that recognising the shape helps:

| Decorator | Shape |
|---|---|
| `@pytest.fixture`, `@pytest.mark.parametrize` | registration + argument injection |
| `@unittest.mock.patch("mod.name")` | wraps the test, injects a mock argument |
| `@app.route("/path")` (Flask) / `@app.get(...)` (FastAPI) | registration; returns the function unchanged |
| `@click.command()`, `@click.option(...)` | stacked registration building a CLI spec |
| `@pydantic.validate_call` | runtime validation from annotations — Part 14's `validate`, done properly |
| `@celery.task`, `@functools.singledispatch`-style plugin hooks | registration |

Notice how many of them are *registration* decorators that return the function untouched. When you see one, the interesting thing happened as a side effect.

## B. Introspecting a decorated function

```python
f.__wrapped__               # the original, if @wraps was used
inspect.signature(f)        # follows __wrapped__ automatically
inspect.unwrap(f)           # walk the whole __wrapped__ chain
f.__name__, f.__doc__       # correct only if @wraps was used
type(f)                     # is it a function, or a class-based decorator instance?
vars(SomeClass)["method"]   # the raw shelf item — property? classmethod? your object?
```

`inspect.signature(f)` following `__wrapped__` is the reason `@wraps` matters beyond cosmetics: pytest, FastAPI, and `singledispatch` all read signatures.

## C. When *not* to write one

| Situation | Do instead |
|---|---|
| the behaviour differs per call site | a parameter |
| it's used exactly once | inline the code |
| it needs to see or change the caller's locals | rethink |
| it silently changes the return type | rename it so the surprise is visible |
| you only want it in tests | a fixture or a context manager |
| it's adding methods to many classes | a base class or `__init_subclass__` |

A decorator is invisible at the call site. That's its power and its cost — anything a reader would be surprised by shouldn't hide there.

## D. What landed when

| Version | Relevant |
|---|---|
| 2.4 | function decorators |
| 2.6 | class decorators |
| 3.2 | `@functools.lru_cache` |
| 3.4 | `@functools.singledispatch`, `@abc.abstractmethod` becomes the only spelling |
| 3.8 | `@functools.cached_property`, `@singledispatchmethod`, `@typing.final` |
| 3.9 | `@functools.cache`; `@classmethod` + `@property` chaining (deprecated 3.11, **removed 3.13**) |
| 3.10 | `ParamSpec`, `staticmethod` objects become directly callable |
| 3.11 | `@enum.verify`, `@enum.member`/`@enum.nonmember`, `@typing.dataclass_transform` |
| **3.12** | **`@typing.override`; PEP 695 `def deco[**P, R]`** |
| 3.13 | `@warnings.deprecated` |

---

# The one thing to remember

> ## **`@d` above a `def` or a `class` means exactly one thing: `f = d(f)`. The decorator takes what you defined and returns whatever should have that name instead — and it may return anything at all.**
>
> **No arguments means two layers; arguments means three. Stacks apply bottom-up, so the outermost one runs first. `@property`, `@classmethod`, and `@staticmethod` go on top because they return descriptors; `@abstractmethod` goes on the bottom. And every wrapper you write gets `@functools.wraps(fn)`.**

That sentence is the entire feature. Write `f = d(f)` out by hand and the confusion goes with the sugar.

And when a decorated function does something inexplicable: **print `f` and `type(f)`.** The name is holding something, and it will tell you what.
