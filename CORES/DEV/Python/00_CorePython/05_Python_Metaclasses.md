# Never Be Intimidated by a Python Metaclass Again

*Modern Python — 3.12 and later. Every output in this essay is real Python output.*

There is **one** mental model in this essay, and you already know most of it.

Metaclasses have a reputation for being the deep end of Python. They aren't. They are one ordinary idea — *a class is an object, so something made it* — applied consistently. Once you see that, every metaclass feature turns out to be a feature you've already used, one storey up.

This essay also spends a lot of its length telling you **not** to write one. That isn't hedging. Knowing the four lighter tools that do 90% of the job, and being able to name the 10% they can't reach, is what actually makes you good at this.

---

# Part 1 — The mental model: a class is an object, and something made it

Start with the thing you already believe: `3` is an object, and its type is `int`.

```python
class Dog: pass
d = Dog()

type(d)                 # <class '__main__.Dog'>
type(Dog)               # <class 'type'>          ← Dog is an object too
type(type)              # <class 'type'>          ← and it stops here
type(int), type(str)    # (<class 'type'>, <class 'type'>)
isinstance(Dog, type)   # True
```

`Dog` is not special syntax that produced a special thing. It's an **object**, sitting in a variable named `Dog`, and its type is `type`.

```
     ┌──────────────────────────────────────────────────┐
     │  type          the class factory                 │   type(type) is type
     └──────────────────────────────────────────────────┘
                          │  makes
                          ▼
     ┌──────────────────────────────────────────────────┐
     │  Dog           a class                           │   type(Dog)  is type
     └──────────────────────────────────────────────────┘
                          │  makes
                          ▼
     ┌──────────────────────────────────────────────────┐
     │  d = Dog()     an instance                       │   type(d)    is Dog
     └──────────────────────────────────────────────────┘
```

> ## **A metaclass is to a class what a class is to an instance. `type` is the default one.**

And that gives you the whole essay in one sentence:

> ## **"A `class` statement is a function call. `type` is the function. A metaclass is your own function in its place."**

## `type` really is a function you can call

Two entirely different jobs, chosen by argument count:

```python
type(d)                                  # 1 arg: "what type is this?"

Cat = type("Cat", (), {"legs": 4, "speak": lambda self: "meow"})
#          name    bases   namespace

Cat                     # <class '__main__.Cat'>
Cat().speak()           # 'meow'
Cat.legs                # 4
Cat.__name__            # 'Cat'
Cat.__mro__             # (<class 'Cat'>, <class 'object'>)
```

That three-argument call is **exactly what a `class` statement does**. These two are the same thing:

```python
class Cat:
    legs = 4
    def speak(self): return "meow"

Cat = type("Cat", (), {"legs": 4, "speak": lambda self: "meow"})
```

The `class` statement is syntax sugar over a call to `type`. A metaclass is what you get when you put something else in `type`'s place.

## Everything from the previous two essays applies, one storey up

This is the part that makes metaclasses stop being scary.

**From the class-members essay:** an object has a drawer, its class has a shelf. Well — a class is an object, so a class has a drawer (`vars(Dog)`, which is the shelf its instances read from), and *its* class has a shelf too. The metaclass is one more shelf back.

```python
class WithHelper(type):
    version = "1.0"
    def describe(cls): return f"class {cls.__name__}"

class Widget(metaclass=WithHelper): pass

Widget.version          # '1.0'              ← walked back to the metaclass
Widget.describe()       # 'class Widget'     ← `cls` is Widget, bound like `self`

w = Widget()
w.version               # AttributeError: 'Widget' object has no attribute 'version'
w.describe()            # AttributeError: 'Widget' object has no attribute 'describe'
```

Read that carefully. `describe` is an *instance method of the metaclass*, so its `self` is the class. And an instance of `Widget` can't see it, because the walk goes `w → Widget → object`, never sideways into `type(Widget)`.

> **A metaclass method is a method on the class, invisible to instances. That's what "classmethod, but for real" means.**

**From the dunder essay:** every dunder is a rewrite into `type(obj).__dunder__(obj, ...)`. Substitute a class for `obj` and you get the rule for metaclass dunders:

```
   Widget(...)      →   type(Widget).__call__(Widget, ...)
   repr(Widget)     →   type(Widget).__repr__(Widget)
   len(Widget)      →   type(Widget).__len__(Widget)
   Widget[x]        →   type(Widget).__getitem__(Widget, x)
   isinstance(o, W) →   type(W).__instancecheck__(W, o)
```

So `MyClass(...)` building an instance is not special machinery — it is `__call__` on the metaclass. Part 6 shows what happens when you take it over.

## You have already used metaclasses

```python
from abc import ABC
from enum import Enum

type(ABC)               # <class 'abc.ABCMeta'>
type(Enum)              # <class 'enum.EnumType'>
```

Every `@abstractmethod` you've written, every `for colour in Colour:` — those are metaclasses doing their job. Part 10 opens both up.

That's the model. Now we just apply it.

---

# Part 2 — What a `class` statement actually does

Seven steps, in order. You can watch every one.

```python
class Meta(type):
    @classmethod
    def __prepare__(mcls, name, bases, **kw):
        print(f"1. __prepare__({name!r}, {bases}, {kw}) -> namespace")
        return {}

    def __new__(mcls, name, bases, ns, **kw):
        print(f"3. __new__  name={name!r} ns={[k for k in ns if not k.startswith('__')]} kw={kw}")
        return super().__new__(mcls, name, bases, ns)

    def __init__(cls, name, bases, ns, **kw):
        print(f"4. __init__ cls={cls.__name__}")
        super().__init__(name, bases, ns)

    def __call__(cls, *a, **k):
        print(f"5. __call__ (making an INSTANCE of {cls.__name__})")
        return super().__call__(*a, **k)


class Thing(metaclass=Meta, flavour="salt"):
    print("2. class body runs")
    x = 1
    def m(self): pass

t = Thing()
```

```
1. __prepare__('Thing', (), {'flavour': 'salt'}) -> namespace
2. class body runs
3. __new__  name='Thing' ns=['x', 'm'] kw={'flavour': 'salt'}
4. __init__ cls=Thing
5. __call__ (making an INSTANCE of Thing)
```

The full sequence, including the parts `type.__new__` does for you:

| # | Step | What happens |
|---|---|---|
| 1 | **Evaluate bases** | the base classes in the parentheses are evaluated. If one isn't a class, its `__mro_entries__` is consulted. |
| 2 | **Determine the metaclass** | explicit `metaclass=` if given, else the most derived metaclass among the bases, else `type`. |
| 3 | **`__prepare__`** | asks the metaclass for an empty namespace object to run the body in. Defaults to `{}`. |
| 4 | **Run the class body** | ordinary code, top to bottom, with that namespace as its local scope. |
| 5 | **`metacls(name, bases, ns, **kwds)`** | which is `__new__` then `__init__`. The class object now exists. |
| 6 | **Inside `type.__new__`:** `__set_name__` | called on every descriptor found in the namespace. |
| 7 | **Inside `type.__new__`:** `__init_subclass__` | called on the *nearest parent*, with the new class. |
| 8 | **Decorators** | applied last, outermost last, to the finished class. |

Steps 6–8 in real output:

```python
order = []

class TraceMeta(type):
    def __new__(mcls, n, b, ns, **kw):
        order.append("metaclass.__new__")
        return super().__new__(mcls, n, b, ns)

def deco(cls):
    order.append("decorator"); return cls

class TBase(metaclass=TraceMeta):
    def __init_subclass__(cls, **kw):
        order.append("__init_subclass__"); super().__init_subclass__(**kw)

class Desc:
    def __set_name__(self, owner, name): order.append("__set_name__")

@deco
class Final(TBase):
    f = Desc()

order
# ['metaclass.__new__',            ← creating TBase
#  'metaclass.__new__',            ← creating Final (logged before super().__new__)
#  '__set_name__',                 ← inside type.__new__
#  '__init_subclass__',            ← inside type.__new__
#  'decorator']                    ← last of all
```

**Two things to take from this table.** First, `__new__` is the *only* hook that runs before the class exists — everything after it can only modify a finished class. Second, `__init_subclass__` and `__set_name__` are free: no metaclass required, and they cover most of what people write metaclasses for.

---

# Part 3 — The four levers

Four ways to customise class creation, ordered from lightest to heaviest. **Use the lightest one that does the job.** That's not style advice; each step up costs you composability, and the last one costs you the ability to combine with other libraries.

Here is the same task — a registry of subclasses — done all three ways that can do it:

```python
# LEVER 1 — a class decorator.  Explicit, local, zero inheritance.
registry1 = {}
def register(cls):
    registry1[cls.__name__] = cls
    return cls

@register
class Alpha: pass
registry1               # {'Alpha': <class 'Alpha'>}


# LEVER 2 — __init_subclass__.  Automatic for every subclass, no metaclass.
class Base2:
    registry = {}
    def __init_subclass__(cls, **kw):
        super().__init_subclass__(**kw)
        cls.registry[cls.__name__] = cls

class Beta(Base2): pass
Base2.registry          # {'Beta': <class 'Beta'>}


# LEVER 4 — a metaclass.  Works, but you didn't need it here.
class RegMeta(type):
    registry = {}
    def __new__(mcls, name, bases, ns, **kw):
        cls = super().__new__(mcls, name, bases, ns)
        if bases: mcls.registry[name] = cls
        return cls

class Base3(metaclass=RegMeta): pass
class Gamma(Base3): pass
RegMeta.registry        # {'Gamma': <class 'Gamma'>}
```

## 3.1 The decision table

| Lever | Reaches | Costs | Use for |
|---|---|---|---|
| **1. class decorator** | one class, after it exists | must be applied by hand each time | `@dataclass`, `@register`, `@final`, adding methods |
| **2. `__init_subclass__`** | every subclass, automatically | requires a common base | registration, validating required methods, injecting defaults, plugin discovery |
| **3. `__set_name__`** | one descriptor, learns its own name | only descriptors | fields, validators, ORM columns |
| **4. metaclass** | the class *before* it exists, plus the class object's own behaviour | infects the whole hierarchy; conflicts with other metaclasses | see 3.3 |

## 3.2 `__init_subclass__` in full

It is a classmethod (implicitly — don't write the decorator), it runs at class-creation time, and it can take keyword arguments written in the `class` line.

```python
class Validating:
    def __init_subclass__(cls, /, plugin_name=None, **kw):
        super().__init_subclass__(**kw)
        if not hasattr(cls, "handle"):
            raise TypeError(f"{cls.__name__} must define handle()")
        cls.plugin_name = plugin_name or cls.__name__.lower()

class Missing(Validating): pass
# TypeError: Missing must define handle()      ← at IMPORT time, not at call time

class Csv(Validating, plugin_name="csv"):
    def handle(self): ...

Csv.plugin_name         # 'csv'
```

Note `super().__init_subclass__(**kw)` — always call it. It's how cooperative hooks further up the MRO still get their turn, and how unexpected keyword arguments produce a proper error.

> **`__init_subclass__` is the single most under-used feature in Python. It replaced most metaclasses in 2016 and a lot of code hasn't caught up.**

## 3.3 What only a metaclass can do

Be honest about this list — it's short, and it's the whole justification.

**1. Change the namespace before the class exists.** `__init_subclass__` receives a finished class. Only `__new__` on a metaclass can rewrite, add to, or reject the namespace *first*.

```python
class UpperMeta(type):
    def __new__(mcls, name, bases, ns, **kw):
        ns = {(k.upper() if not k.startswith("__") else k): v for k, v in ns.items()}
        return super().__new__(mcls, name, bases, ns)

class Shouty(metaclass=UpperMeta):
    quiet = 1

Shouty.QUIET            # 1
hasattr(Shouty, "quiet")  # False
```

**2. Set things that must exist at creation time.** `__slots__` is the canonical example — by the time `__init_subclass__` runs, the object layout is already fixed:

```python
class TooLate:
    def __init_subclass__(cls, **kw):
        super().__init_subclass__(**kw)
        cls.__slots__ = ("x",)          # sets an attribute. Does nothing else.

class S(TooLate): pass
s = S(); s.anything = 1
S.__slots__             # ('x',)      ← the attribute is there
hasattr(s, "__dict__")  # True        ← but the class still has a drawer. It did nothing.
```

The metaclass version works, because it happens first:

```python
class AutoSlots(type):
    def __new__(mcls, name, bases, ns, **kw):
        ann = annotations_of(ns)                        # see the note below
        if ann and "__slots__" not in ns:
            ns["__slots__"] = tuple(ann)
            for k in ann: ns.pop(k, None)
        return super().__new__(mcls, name, bases, ns)

class Slim(metaclass=AutoSlots):
    x: int
    y: int
    def __init__(self, x, y): self.x, self.y = x, y

Slim.__slots__          # ('x', 'y')
hasattr(Slim(1,2), "__dict__")      # False
```

```python
def annotations_of(ns):
    """Reading class-body annotations, portably across the 3.14 PEP 649 change."""
    if "__annotations__" in ns:
        return ns["__annotations__"]        # 3.13 and earlier
    fn = ns.get("__annotate_func__")
    return fn(1) if fn is not None else {}  # 3.14+: annotations are lazy
```

**3. Give the class object its own behaviour.** `len(MyClass)`, `for x in MyClass`, `MyClass[k]`, a custom `repr(MyClass)` — these are dunders on the metaclass, and there is no other way to write them (Part 7).

**4. Control instantiation itself.** `MyClass(...)` is `type(MyClass).__call__` (Part 6).

**5. Customise `isinstance` / `issubclass`.** `__instancecheck__` and `__subclasscheck__` live on the metaclass.

**6. Detect duplicate or ordered definitions in the body.** Needs `__prepare__` (Part 5).

If your reason isn't on that list, you want lever 1, 2, or 3.

---

# Part 4 — Writing one: `__new__` vs `__init__`

A metaclass is a class that inherits from `type`. Its instances are classes.

```python
class Meta(type):
    def __new__(mcls, name, bases, ns, **kwargs):
        # mcls  = the metaclass itself       (like `cls` in a normal __new__)
        # name  = 'Thing'
        # bases = (Base1, Base2)
        # ns    = the namespace dict from the class body
        # kwargs = extra keywords from the class line
        cls = super().__new__(mcls, name, bases, ns)
        return cls

    def __init__(cls, name, bases, ns, **kwargs):
        # cls = the finished class          (like `self` in a normal __init__)
        super().__init__(name, bases, ns)
```

The naming convention is worth adopting: **`mcls` in `__new__`** (the argument is the metaclass), **`cls` in `__init__` and every other method** (the argument is the class). It makes the storey you're on obvious at a glance.

| | `__new__` | `__init__` |
|---|---|---|
| when | before the class exists | after |
| first arg | the metaclass | the finished class |
| can change the namespace? | **yes** | no — only set attributes on `cls` |
| can change bases? | yes | no |
| can return a different object? | yes | no |
| use it when | you must affect creation | you only need to record or register |

```python
class NewMeta(type):
    def __new__(mcls, n, b, ns, **kw):
        ns["added_in_new"] = True               # can still edit the namespace
        return super().__new__(mcls, n, b, ns)

class InitMeta(type):
    def __init__(cls, n, b, ns, **kw):
        super().__init__(n, b, ns)
        cls.added_in_init = True                # class exists; just mutate it
```

**Default to `__init__`.** It's harder to break and the signature is less fiddly. Move to `__new__` only when you genuinely need the namespace before the class is built.

## 4.1 Keyword arguments in the class line

Extra keywords in `class Foo(Base, x=1)` flow to all three metaclass hooks:

```python
class KwMeta(type):
    @classmethod
    def __prepare__(mcls, n, b, **kw):  return {}
    def __new__(mcls, n, b, ns, **kw):
        cls = super().__new__(mcls, n, b, ns); cls.opts = kw; return cls
    def __init__(cls, n, b, ns, **kw):  super().__init__(n, b, ns)

class Tuned(metaclass=KwMeta, cache=True, ttl=30): pass
Tuned.opts              # {'cache': True, 'ttl': 30}
```

Note that `__new__` must **not** pass `**kw` on to `type.__new__` (it doesn't accept them), and `__init__` likewise. Swallow them in your own signature.

The same keywords reach `__init_subclass__` if you're using that instead — which is the lighter way to get the same effect:

```python
class KwInit:
    def __init_subclass__(cls, /, plugin_name=None, **kw):
        super().__init_subclass__(**kw)
        cls.plugin_name = plugin_name

class P(KwInit, plugin_name="csv"): pass
P.plugin_name           # 'csv'
```

---

# Part 5 — `__prepare__`: choosing the namespace

`__prepare__` is asked for the object the class body will be executed *into*. Return anything dict-like.

```python
class Meta(type):
    @classmethod
    def __prepare__(mcls, name, bases, **kwargs):
        return {}                       # the default
```

**First, the honest caveat:** its original headline use — preserving declaration order — has been unnecessary since 3.6, because the default class namespace is an ordered `dict`:

```python
class Ordered:
    z = 1
    a = 2
    m = 3

[k for k in vars(Ordered) if not k.startswith("_")]     # ['z', 'a', 'm']
```

So don't write `__prepare__` for ordering. Two real uses remain.

## 5.1 Observing definitions as they happen

```python
class NoDup(dict):
    def __setitem__(self, k, v):
        if k in self:
            raise TypeError(f"duplicate member {k!r}")
        super().__setitem__(k, v)

class NoDupMeta(type):
    @classmethod
    def __prepare__(mcls, n, b, **kw): return NoDup()

class Bad(metaclass=NoDupMeta):
    def f(self): pass
    def f(self): pass
# TypeError: duplicate member 'f'
```

Silently shadowing a method by redefining it is a real bug that nothing else catches. `Enum` uses exactly this technique to reject duplicate member *names* while allowing duplicate values as aliases.

## 5.2 Making names available inside the body

A namespace with a `__missing__` can inject values that the class body can reference as bare names — how `enum.auto()`-style DSLs and some ORMs work. Powerful, and the fastest way to make your class bodies unreadable. Use sparingly.

## 5.3 Recording metadata about the body

```python
class Ordered(dict):
    def __init__(self): super().__init__(); self.order = []
    def __setitem__(self, k, v):
        if not k.startswith("__"): self.order.append(k)
        super().__setitem__(k, v)

class OrderMeta(type):
    @classmethod
    def __prepare__(mcls, name, bases, **kw): return Ordered()
    def __new__(mcls, name, bases, ns, **kw):
        cls = super().__new__(mcls, name, bases, dict(ns))
        cls._declared = ns.order
        return cls

class Form(metaclass=OrderMeta):
    email = "e"
    name = "n"
    age = "a"

Form._declared          # ['email', 'name', 'age']
```

Note `dict(ns)` when calling `super().__new__` — `type.__new__` copies the namespace into a real dict anyway, so hand it one.

---

# Part 6 — `__call__`: controlling instantiation

`MyClass(...)` is `type(MyClass).__call__(MyClass, ...)`. Override it and you own what happens when someone instantiates.

The default `type.__call__` is essentially:

```python
def __call__(cls, *args, **kwargs):
    obj = cls.__new__(cls, *args, **kwargs)
    if isinstance(obj, cls):
        cls.__init__(obj, *args, **kwargs)
    return obj
```

## 6.1 Singleton — done properly

```python
class SingletonMeta(type):
    _cache = {}
    def __call__(cls, *a, **k):
        if cls not in cls._cache:
            cls._cache[cls] = super().__call__(*a, **k)
        return cls._cache[cls]

class Config(metaclass=SingletonMeta):
    def __init__(self): print("Config.__init__ ran once")

Config() is Config()    # True
# Config.__init__ ran once
```

Compare with the `__new__` version from the dunder essay: there, `__init__` re-ran on every call, because `__new__` returning an existing instance doesn't stop `__init__`. Here it can't happen — `super().__call__` is only reached once. **`__call__` is the correct place for identity control**, `__new__` is the correct place for allocation.

## 6.2 Instance caching / interning

```python
class CacheMeta(type):
    def __call__(cls, *a, **k):
        key = (cls, a, tuple(sorted(k.items())))
        cache = cls.__dict__.get("_cache")
        if cache is None:
            cache = {}; setattr(cls, "_cache", cache)
        if key not in cache:
            cache[key] = super().__call__(*a, **k)
        return cache[key]

class Colour(metaclass=CacheMeta):
    def __init__(self, name): self.name = name
    def __repr__(self): return f"Colour({self.name!r})"

Colour("red") is Colour("red")      # True
Colour("red") is Colour("blue")     # False
```

`cls.__dict__.get("_cache")` rather than `cls._cache` — otherwise a subclass would read (and share) its parent's cache. That's the drawer-and-shelf rule again: reading walks back, and here you don't want it to.

## 6.3 Blocking instantiation

```python
class Abstract(type):
    def __call__(cls, *a, **k):
        if getattr(cls, "_abstract", False):
            raise TypeError(f"{cls.__name__} is abstract")
        return super().__call__(*a, **k)
```

Which is a hand-rolled and worse version of `abc.ABCMeta`. Use the real one.

---

# Part 7 — Dunders on the metaclass: giving the class itself behaviour

Everything from the dunder essay, applied to the class object.

```python
class NiceMeta(type):
    def __repr__(cls):          return f"<the {cls.__name__} class>"
    def __len__(cls):           return len(cls.members)
    def __iter__(cls):          return iter(cls.members)
    def __getitem__(cls, k):    return cls.members[k]
    def __getattr__(cls, name): return f"<dynamic {name}>"

class Team(metaclass=NiceMeta):
    members = ["ann", "bo"]

Team                    # <the Team class>
len(Team)               # 2
list(Team)              # ['ann', 'bo']
Team[0]                 # 'ann'
Team.anything           # '<dynamic anything>'
```

**This is the reason metaclasses survive.** There is genuinely no other way to make `len(MyClass)` or `for x in MyClass` work — a classmethod can't, a decorator can't, `__init_subclass__` can't. If you have ever wondered how `list(Colour)` iterates an `Enum`'s members, this is the answer.

## 7.1 `__instancecheck__` and `__subclasscheck__`

```python
class EvenMeta(type):
    def __instancecheck__(cls, obj):  return isinstance(obj, int) and obj % 2 == 0
    def __subclasscheck__(cls, sub):  return sub is int

class Even(metaclass=EvenMeta): pass

isinstance(4, Even)     # True
isinstance(5, Even)     # False
issubclass(int, Even)   # True
```

Cute, and almost always the wrong tool — lying about `isinstance` breaks every reader's expectations and confuses type checkers. The legitimate version of this is `abc.ABCMeta`, which uses it for virtual subclass registration (Part 10.1).

## 7.2 The full list of class-level dunders worth knowing

| On the metaclass | Makes possible |
|---|---|
| `__call__` | control `MyClass(...)` |
| `__repr__` | how the class prints |
| `__len__`, `__iter__`, `__contains__`, `__getitem__` | treat the class as a collection |
| `__getattr__` | dynamic class attributes |
| `__instancecheck__`, `__subclasscheck__` | customise `isinstance` / `issubclass` |
| `__prepare__` | choose the class-body namespace |
| `__new__`, `__init__` | class creation |
| `__or__` | `MyClass \| Other` (this is how `int \| str` works) |

---

# Part 8 — Inheritance and conflicts

## 8.1 A metaclass is inherited

```python
class M1(type): pass
class A(metaclass=M1): pass
class B(A): pass

type(B)                 # <class 'M1'>      ← no metaclass= needed
```

This is why a metaclass "infects" a hierarchy. Every descendant gets it, forever. That is the real cost of lever 4 and the main reason to prefer the lighter ones.

## 8.2 Python picks the most derived metaclass

```python
class MSub(M1): pass
class WithSub(A, metaclass=MSub): pass

type(WithSub)           # <class 'MSub'>    ← MSub is a subclass of M1, so it's allowed
```

The rule: the chosen metaclass must be a **(non-strict) subclass of every base's metaclass**. Python picks the most derived candidate automatically.

## 8.3 The conflict, and the fix

```python
class M2(type): pass
class C(metaclass=M2): pass

class Clash(A, C): pass
# TypeError: metaclass conflict: the metaclass of a derived class must be a
#            (non-strict) subclass of the metaclasses of all its bases
```

`A`'s metaclass is `M1`, `C`'s is `M2`, and neither is a subclass of the other. The fix is to build one that is:

```python
class M3(M1, M2): pass
class Fixed(A, C, metaclass=M3): pass

type(Fixed)             # <class 'M3'>
```

**In practice this is where metaclasses hurt.** The moment you want your class to inherit from something in another library that has its own metaclass, you're writing a combined metaclass and hoping the two don't fight. The most common real instance is combining with `ABCMeta`:

```python
from abc import ABCMeta, abstractmethod

class RegMeta(ABCMeta):                     # ← inherit from ABCMeta, not type
    registry = {}
    def __new__(mcls, n, b, ns, **kw):
        cls = super().__new__(mcls, n, b, ns, **kw)
        if b: mcls.registry[n] = cls
        return cls

class Plugin(metaclass=RegMeta):
    @abstractmethod
    def run(self): ...

class Csv(Plugin):
    def run(self): return "csv"

RegMeta.registry        # {'Csv': <class 'Csv'>}

class Broken(Plugin): pass
Broken()
# TypeError: Can't instantiate abstract class Broken without an implementation
#            for abstract method 'run'
```

Both behaviours survive: the registry from `RegMeta`, and abstract enforcement from `ABCMeta`.

Inheriting from `ABCMeta` rather than `type` is the standard move, and it's why library metaclasses so often do.

## 8.4 You cannot change it afterwards

```python
class A: pass
A.__class__ = M1
# TypeError: __class__ assignment only supported for mutable types
#            or ModuleType subclasses
```

The metaclass is fixed at creation. Decide up front.

---

# Part 9 — The variants: a catalogue

Every pattern people reach for metaclasses to do, with the lighter alternative named honestly.

| # | Pattern | Metaclass hook | Lighter alternative |
|---|---|---|---|
| 1 | **Registry** of subclasses | `__new__`/`__init__` | **`__init_subclass__`** ✓ |
| 2 | **Validate** required methods | `__new__` | **`__init_subclass__`** ✓ |
| 3 | **Inject** default attributes | `__init__` | **`__init_subclass__`** ✓ |
| 4 | **Name** descriptors | `__new__` scanning the ns | **`__set_name__`** ✓ |
| 5 | **Add generated methods** | `__new__` | **class decorator** ✓ (this is `@dataclass`) |
| 6 | **Abstract enforcement** | `__call__` | **`abc.ABCMeta`** ✓ (already written) |
| 7 | **Singleton / caching** | `__call__` | module-level instance, or `@functools.cache` on a factory |
| 8 | **Set `__slots__` automatically** | `__new__` | *none* — needs a metaclass |
| 9 | **Class-level `len`/`iter`/`repr`** | metaclass dunders | *none* — needs a metaclass |
| 10 | **Reject duplicate members** | `__prepare__` | *none* — needs a metaclass |
| 11 | **Rewrite the namespace** | `__new__` | *none* — needs a metaclass |
| 12 | **Custom `isinstance`** | `__instancecheck__` | `Protocol` (for checkers), `ABC.register` (for runtime) |

## 9.1 Rows 1–3: use `__init_subclass__`

Already shown in 3.2. If you're writing a metaclass for any of these, stop.

## 9.2 Row 5: use a class decorator

Adding `__init__`, `__repr__`, `__eq__` to a class is a decorator's job — that is literally what `@dataclass` is, and it deliberately isn't a metaclass so it composes with anything.

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

**A decorator that doesn't touch the hierarchy is always safer than a metaclass that does.**

## 9.3 Row 7: singleton, and whether you want one

The metaclass version is Part 6.1. But before you write it, consider that in Python the module is already a singleton:

```python
# config.py
settings = Settings()       # imported once, shared everywhere
```

That is simpler, testable, and doesn't surprise anyone. Reach for the metaclass version when the singleton-ness must be enforced against callers who'd otherwise construct their own.

## 9.4 Rows 8–11: the genuine cases

Shown in 3.3, Part 5.1, and Part 7. These are why the feature exists.

---

# Part 10 — The metaclasses already in your code

## 10.1 `abc.ABCMeta`

```python
from abc import ABC, abstractmethod

class Shape(ABC):
    @abstractmethod
    def area(self) -> float: ...

type(Shape)                     # <class 'abc.ABCMeta'>
Shape.__abstractmethods__       # frozenset({'area'})

Shape()
# TypeError: Can't instantiate abstract class Shape without an implementation
#            for abstract method 'area'

class Square(Shape):
    def __init__(self, s): self.s = s
    def area(self): return self.s ** 2

Square(3).area()                # 9
```

What it does with the levers: `__new__` collects every name marked `__isabstractmethod__` into `__abstractmethods__`, and `__call__` refuses if that set is non-empty. Plus `__instancecheck__`/`__subclasscheck__` for virtual subclasses:

```python
class Drawable(ABC): pass
class Circle: pass

Drawable.register(Circle)               # no inheritance involved

isinstance(Circle(), Drawable)          # True
issubclass(Circle, Drawable)            # True
[c.__name__ for c in Circle.__mro__]    # ['Circle', 'object']   ← MRO untouched
```

`register` is how `collections.abc` claims that `list` is a `MutableSequence` without `list` ever hearing about it.

## 10.2 `enum.EnumType`

```python
from enum import Enum, StrEnum, auto

class Colour(Enum):
    RED = auto()
    GREEN = auto()

type(Colour)            # <class 'enum.EnumType'>
list(Colour)            # [<Colour.RED: 1>, <Colour.GREEN: 2>]
len(Colour)             # 2
Colour["RED"]           # <Colour.RED: 1>       ← __getitem__ on the metaclass
Colour(1)               # <Colour.RED: 1>       ← __call__ on the metaclass
Colour.RED in Colour    # True

class Dup(Enum):
    A = 1
    A = 2
# TypeError: 'A' already defined as 1           ← __prepare__ caught it
```

`Enum` is the best worked example of a metaclass in the standard library, because it uses nearly every hook for a reason you can see:

| Hook | What Enum does with it |
|---|---|
| `__prepare__` | a namespace that rejects duplicate names and supports `auto()` |
| `__new__` | turn each plain value into a member instance, build the lookup maps |
| `__call__` | `Colour(1)` looks up by value instead of constructing |
| `__getitem__` | `Colour["RED"]` looks up by name |
| `__iter__`, `__len__`, `__contains__` | the class behaves as a collection of members |
| `__repr__`, `__dir__` | nicer introspection |

Try to build that with `__init_subclass__` and you get stuck at the second row.

## 10.3 Others you'll meet

- **`typing.Protocol`** uses `_ProtocolMeta` (an `ABCMeta` subclass) to make `@runtime_checkable` work.
- **Django models, SQLAlchemy declarative, pydantic v1** all use metaclasses to turn class-body declarations into schema. Pydantic v2 kept the metaclass but moved most work into a Rust core.
- **`type` itself** is the one you use in every single line of Python you've ever written.

---

# Part 11 — The traps

## 11.1 Writing one at all

If `__init_subclass__`, `__set_name__`, or a decorator can do it, they should. The cost of a metaclass is paid by everyone who ever subclasses your class.

## 11.2 The metaclass conflict

*(8.3.)* Two libraries, two metaclasses, and now your class can't inherit from both. Mitigate by inheriting from `ABCMeta` rather than `type`, and by keeping your metaclass minimal.

## 11.3 Passing class keywords through to `type.__new__`

```python
class Meta(type):
    def __new__(mcls, n, b, ns, **kw):
        return super().__new__(mcls, n, b, ns, **kw)     # ✗ TypeError if kw is non-empty
        return super().__new__(mcls, n, b, ns)           # ✓ swallow them
```

`type.__new__` accepts exactly three arguments. (`ABCMeta.__new__` does forward `**kw`, which is why 8.3's example passes them on — match whatever your base metaclass expects.)

## 11.4 Forgetting `super().__init_subclass__(**kw)`

Breaks cooperative multiple inheritance and hides argument typos.

## 11.5 Confusing `mcls`, `cls`, and `self`

Three storeys, three names. In a metaclass method, the first argument is **a class**. Writing `self` there is legal and will confuse you in a month.

## 11.6 `cls.x` vs `cls.__dict__["x"]` inside a metaclass

*(6.2.)* Reading `cls.something` walks back to base classes. If you're storing per-class state — a cache, a registry, a counter — you almost always want `cls.__dict__.get(...)` so subclasses don't silently share their parent's.

## 11.7 Expecting `__init_subclass__` to see the class first

*(3.3.)* It receives a fully built class. `__slots__`, base classes, and object layout are already decided.

## 11.8 Metaclass attributes are invisible to instances

*(Part 1.)* `Widget.version` works, `Widget().version` raises. If instances need it, put it on the class, not the metaclass.

## 11.9 Debugging without printing the storey

When a metaclass misbehaves, print all three at once:

```python
print(type(obj), type(type(obj)), type(obj).__mro__, type(type(obj)).__mro__)
```

Half the confusion is being one level off from where you think you are.

## 11.10 Type checkers don't follow metaclass magic

Anything a metaclass injects into a class is invisible to mypy and pyright. That's a real cost: you trade static checking for dynamism. `__init_subclass__` and decorators fare better (`@dataclass` has explicit checker support precisely because it isn't a metaclass).

---

# Part 12 — The whole thing on one page

## The three storeys

```python
type(instance)          # the class
type(cls)               # the metaclass
type(type)              # type          — it's turtles, but only two deep
isinstance(cls, type)   # True for every class
cls.__bases__           # its parents
cls.__mro__             # the lookup row
type(cls).__mro__       # the metaclass's lookup row
```

## What a class statement runs

| # | Step |
|---|---|
| 1 | evaluate bases (`__mro_entries__` if one isn't a class) |
| 2 | determine the metaclass (explicit, else most-derived base's, else `type`) |
| 3 | `metacls.__prepare__(name, bases, **kw)` → namespace |
| 4 | execute the class body into that namespace |
| 5 | `metacls(name, bases, ns, **kw)` → `__new__`, then `__init__` |
| 6 | `__set_name__` on every descriptor (inside `type.__new__`) |
| 7 | `__init_subclass__` on the nearest parent (inside `type.__new__`) |
| 8 | apply decorators, innermost first |

## The four levers

| Lever | Signature | Reaches |
|---|---|---|
| class decorator | `def d(cls) -> cls` | one finished class |
| `__init_subclass__` | `(cls, /, **kw)`, implicit classmethod | every subclass, finished |
| `__set_name__` | `(self, owner, name)` on a descriptor | that descriptor |
| metaclass | `class M(type)` | creation itself + the class object's behaviour |

## Metaclass hooks

| Hook | Signature | When |
|---|---|---|
| `__prepare__` | `(mcls, name, bases, **kw)` — classmethod | before the body runs |
| `__new__` | `(mcls, name, bases, ns, **kw)` | building the class |
| `__init__` | `(cls, name, bases, ns, **kw)` | after it's built |
| `__call__` | `(cls, *a, **k)` | someone writes `Cls(...)` |
| `__repr__`, `__len__`, `__iter__`, `__getitem__`, `__contains__`, `__getattr__` | `(cls, …)` | that syntax, applied to the class |
| `__instancecheck__`, `__subclasscheck__` | `(cls, obj/sub)` | `isinstance` / `issubclass` |

## Build a class by hand

```python
C = type("C", (Base,), {"x": 1, "m": lambda self: 2})

import types
C = types.new_class("C", (Base,), {}, lambda ns: ns.update(x=1))   # metaclass-aware
mcls, ns, kwds = types.prepare_class("C", (Base,))                 # the low-level pieces
```

## Choosing

> **Decorator → `__init_subclass__` → `__set_name__` → metaclass. Stop at the first one that works.**

Reach for a metaclass only for: rewriting the namespace, setting `__slots__`, giving the class object its own dunders, controlling instantiation, `__prepare__` tricks, or customising `isinstance`.

---

# Part 13 — When it surprises you, ask three questions

1. **"Which storey am I on?"** Print `type(x)` and `type(type(x))`. Almost every metaclass bug is code written one level away from where it needs to be — a method on the class when it should be on the metaclass, or vice versa.

2. **"Has the class been built yet?"** `__prepare__` and metaclass `__new__` run **before**; `__init__`, `__set_name__`, `__init_subclass__`, and decorators run **after**. If your change isn't taking effect, you're probably too late (`__slots__` is the classic).

3. **"Do I actually need this lever?"** Walk down the list in Part 12. Nine times out of ten `__init_subclass__` does the job, composes with everything, and needs no explanation in the code review.

And the universal move: **`type(Cls).__mro__`.** When two libraries fight, that line tells you which metaclasses are in play and in what order.

---

# Part 14 — Real code, using all of it

A small declarative model layer. It is the honest use case: a `Field` descriptor, ordered declaration, inherited fields, a registry, and — the part that genuinely requires a metaclass — a class object that behaves like a collection of its own fields.

```python
class Field:
    """A descriptor. __set_name__ means it learns its own name for free."""

    def __init__(self, kind: type, default=None):
        self.kind, self.default = kind, default

    def __set_name__(self, owner, name):
        self.name = name
        self.slot = "_" + name

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self                              # accessed on the class
        return getattr(obj, self.slot, self.default)

    def __set__(self, obj, value):
        if not isinstance(value, self.kind):
            raise TypeError(
                f"{self.name} must be {self.kind.__name__}, "
                f"got {type(value).__name__}"
            )
        setattr(obj, self.slot, value)

    def __repr__(self):
        return f"Field({self.kind.__name__})"


class ModelMeta(type):
    registry: dict[str, type] = {}

    def __new__(mcls, name, bases, ns, *, table=None, **kw):
        cls = super().__new__(mcls, name, bases, ns, **kw)

        # collect inherited fields first, then this body's — base-first order
        fields = {}
        for base in reversed(cls.__mro__[1:]):
            fields.update(getattr(base, "_fields", {}))
        fields.update({k: v for k, v in ns.items() if isinstance(v, Field)})
        cls._fields = fields

        if bases:                                    # skip the abstract root
            cls._table = table or name.lower()
            mcls.registry[cls._table] = cls
        return cls

    # --- the part only a metaclass can do: the CLASS behaves like a collection ---
    def __repr__(cls):            return f"<Model {cls.__name__}({', '.join(cls._fields)})>"
    def __len__(cls):             return len(cls._fields)
    def __iter__(cls):            return iter(cls._fields.items())
    def __getitem__(cls, name):   return cls._fields[name]


class Model(metaclass=ModelMeta):
    def __init__(self, **kw):
        for k, v in kw.items():
            if k not in self._fields:
                raise TypeError(f"unknown field {k!r}")
            setattr(self, k, v)                      # goes through Field.__set__

    def __repr__(self):
        inner = ", ".join(f"{k}={getattr(self, k)!r}" for k in self._fields)
        return f"{type(self).__name__}({inner})"


class User(Model, table="users"):
    name = Field(str)
    age = Field(int, default=0)


class Admin(User, table="admins"):
    level = Field(int, default=1)
```

Using it:

```python
User                    # <Model User(name, age)>
Admin                   # <Model Admin(name, age, level)>        ← inherited fields
len(Admin)              # 3
Admin["age"]            # Field(int)
[k for k, _ in Admin]   # ['name', 'age', 'level']
ModelMeta.registry      # {'users': <Model User(...)>, 'admins': <Model Admin(...)>}

u = User(name="ann", age=30)
u                       # User(name='ann', age=30)
vars(u)                 # {'_name': 'ann', '_age': 30}

User(name=5)            # TypeError: name must be str, got int
User(nope=1)            # TypeError: unknown field 'nope'
User(name="bo").age     # 0                                       ← the default
```

## What each piece is actually earning

| Piece | Lever | Could it be lighter? |
|---|---|---|
| `Field.__set_name__` | 3 | no — this *is* the light tool |
| field collection + registry | 4 (`__new__`) | **yes** — `__init_subclass__` does this |
| `table=` keyword | 4 | **yes** — `__init_subclass__` takes keywords too |
| `repr(User)`, `len(Admin)`, `Admin["age"]`, iteration | 4 | **no** — nothing else can do this |

So the honest version of this design, if you don't need the class-as-collection behaviour, is smaller and composes better:

```python
class Model2:
    registry: dict[str, type] = {}
    _fields: dict[str, Field] = {}

    def __init_subclass__(cls, /, table=None, **kw):
        super().__init_subclass__(**kw)
        fields = {}
        for base in reversed(cls.__mro__[1:]):
            fields.update(getattr(base, "_fields", {}))
        fields.update({k: v for k, v in vars(cls).items() if isinstance(v, Field)})
        cls._fields = fields
        cls._table = table or cls.__name__.lower()
        Model2.registry[cls._table] = cls


class User2(Model2, table="users"):
    name = Field(str)

Model2.registry         # {'users': <class 'User2'>}
User2._fields           # {'name': Field(str)}

repr(User2)             # "<class '__main__.User2'>"     ← plain. No custom class repr.
len(User2)              # TypeError: object of type 'type' has no len()
```

Everything works except the two lines at the bottom. **That gap is exactly the size of the justification for a metaclass** — and if you don't need those two lines, you don't need the metaclass.

---

# Appendix

## A. Building classes without the `class` statement

```python
# the raw call — ignores any metaclass the bases might have
C = type("C", (Base,), {"x": 1})

# the correct general form — resolves the metaclass, calls __prepare__
import types
def body(ns):
    ns["x"] = 1
    ns["m"] = lambda self: 2
C = types.new_class("C", (Base,), {}, body)

# the pieces, if you want them separately
mcls, ns, kwds = types.prepare_class("C", (Base,))
```

Use `types.new_class` whenever the bases might have a metaclass — the bare `type(...)` call skips metaclass resolution and will silently build the wrong kind of class.

## B. `__mro_entries__` — a non-class in the bases list

```python
class Real: pass

class Stand:
    def __mro_entries__(self, bases):
        return (Real,)                  # substitute me with this

stand = Stand()
class Uses(stand): pass

Uses.__bases__          # (<class 'Real'>,)
Uses.__orig_bases__     # (<__main__.Stand object at 0x...>,)   ← what you wrote
```

Step 1 of the class statement. This is how `class Foo(Generic[T])` and `class Foo(Protocol)` work when the thing in parentheses isn't really a class. `__orig_bases__` preserves what you actually typed, which is how `typing` recovers the type arguments.

## C. Metaclass vs. the alternatives, at a glance

| You want | Reach for |
|---|---|
| add generated methods to one class | class decorator |
| the same for every subclass | `__init_subclass__` |
| a reusable validated attribute | a descriptor + `__set_name__` |
| enforce "must implement X" | `abc.ABC` + `@abstractmethod` |
| structural typing for a checker | `typing.Protocol` |
| structural typing at runtime | `@runtime_checkable`, or `__subclasshook__` |
| a fixed set of named constants | `Enum` |
| data-holding classes | `@dataclass` |
| one shared instance | a module-level object |
| the class itself to be iterable / sized / custom-repr'd | **a metaclass** |
| the namespace rewritten before the class exists | **a metaclass** |

## D. What landed when

| Version | Relevant |
|---|---|
| 3.0 | `metaclass=` keyword syntax (replacing `__metaclass__`) |
| 3.3 | `__qualname__`; `__prepare__` becomes generally useful |
| **3.6** | **`__init_subclass__`, `__set_name__`** — the change that made most metaclasses unnecessary; class-body namespace becomes ordered by default |
| 3.7 | `__class_getitem__` (a lighter alternative to a metaclass `__getitem__`) |
| 3.7 | `__mro_entries__` (PEP 560) — `Generic` stops needing a metaclass |
| 3.11 | `enum.EnumMeta` renamed `enum.EnumType` (old name kept as an alias) |
| 3.12 | PEP 695 `class C[T]` — generics with no metaclass involvement at all |

Notice the direction of travel: nearly every release since 3.6 has moved something *out* of metaclass territory. Writing one in 2026 should feel like reaching for a power tool, not a default.

## E. Reading a metaclass you didn't write

In order:

1. `type(TheClass)` — which metaclass is it?
2. `type(TheClass).__mro__` — is it stacked on `ABCMeta` or another library's?
3. Look for `__new__` first — it's where the namespace gets rewritten, and therefore where attributes appear from nowhere.
4. Look for `__call__` — it's where instantiation stops behaving normally.
5. `vars(TheClass)` vs. what the source says — the difference is what the metaclass added.

---

# The one thing to remember

> ## **A class is an object. Something made it, and that something is its metaclass. `type` is the default; a metaclass is your own factory in its place.**
>
> **A metaclass is to a class what a class is to an instance — so every dunder you know works one storey up: `__call__` on the metaclass runs when someone writes `MyClass(...)`, `__len__` runs on `len(MyClass)`, `__repr__` decides how the class prints.**
>
> **And there are four levers, not one. Class decorator, `__init_subclass__`, `__set_name__`, metaclass — in that order of preference. Stop at the first one that works. The only jobs that genuinely need the last one are: rewriting the namespace before the class exists, setting `__slots__`, giving the class object its own dunders, taking over instantiation, and customising `isinstance`.**

That is the whole system. When it surprises you, print `type(x)` and `type(type(x))` and find out which storey you're standing on.

And on the days you're about to write one: **try `__init_subclass__` first. It usually just works, and nobody has to read an essay to understand it.**
