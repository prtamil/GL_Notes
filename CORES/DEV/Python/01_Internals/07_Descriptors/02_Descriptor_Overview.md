Below is the same descriptor material, but reorganized so the **English is simpler while the technical depth stays senior-level**. I’ve kept the CPython terminology, lookup order, C-level details, edge cases, and interview questions.

# Python Descriptors — Complete Technical Guide

_A senior-level reference to the descriptor protocol, CPython attribute lookup, precedence rules, `__set_name__`, `__slots__`, metaclasses, functions, `property`, `classmethod`, `staticmethod`, `super`, caching, and production-style descriptors._

---

# Part I — The One Idea Everything Comes From

The most important thing to understand is this:

> **Python attribute access is a protocol, not simply a dictionary lookup.**

When you write:

```python
obj.attr
```

Python does **not** simply do:

```python
obj.__dict__["attr"]
```

Conceptually, it starts with:

```python
type(obj).__getattribute__(obj, "attr")
```

`object.__getattribute__()` then performs a carefully defined lookup.

One important part of that lookup is:

> If the attribute found on the class is a **descriptor**, Python may call the descriptor instead of simply returning the object.

That is the foundation of descriptors.

---

## What is a descriptor?

An object is a descriptor when its **type** defines at least one of:

```python
__get__
__set__
__delete__
```

For example:

```python
class Descriptor:
    def __get__(self, obj, objtype=None):
        ...

    def __set__(self, obj, value):
        ...

    def __delete__(self, obj):
        ...
```

But there is an important condition:

> The descriptor must be stored on a **class** for the descriptor protocol to participate in normal attribute lookup.

This is one of the most important rules.

---

# The Descriptor Mechanism Behind Python

Descriptors are not some isolated feature. They are underneath many things that look like special Python syntax.

|Python feature|Descriptor machinery|
|---|---|
|`obj.method`|`function.__get__`|
|`@property`|data descriptor|
|`@classmethod`|non-data descriptor|
|`@staticmethod`|non-data descriptor|
|`__slots__`|C-level `member_descriptor`|
|`super().x`|`super` + descriptor lookup|
|C extension properties|`getset_descriptor`|
|ORM fields|often descriptors|
|Lazy attributes|often descriptors|
|Validation fields|often descriptors|
|Cached attributes|often non-data descriptors|

This gives a useful interview-level statement:

> **Descriptors are one of the fundamental mechanisms Python uses to implement attribute behavior, including methods.**

---

# The Critical Placement Rule

Consider:

```python
class D:
    def __get__(self, obj, objtype=None):
        return "triggered"


class C:
    pass
```

Now:

```python
c = C()

c.d = D()
print(c.d)
```

Output:

```text
<D object ...>
```

Why?

Because `D()` was stored in:

```python
c.__dict__
```

The descriptor protocol does **not** inspect arbitrary objects inside the instance dictionary.

Now put the descriptor on the class:

```python
C.d = D()

print(C().d)
```

Now:

```text
triggered
```

Why?

Because lookup found `D()` through:

```text
type(c).__mro__
```

and therefore Python recognized it as a descriptor.

### Memorize this

> **Descriptor behavior is triggered when the descriptor is found on the type/MRO, not when it is found in the instance dictionary.**

---

# Part II — The Descriptor Protocol

A descriptor can implement:

```python
class Descriptor:

    def __set_name__(self, owner, name):
        ...

    def __get__(self, obj, objtype=None):
        ...

    def __set__(self, obj, value):
        ...

    def __delete__(self, obj):
        ...
```

These methods have different jobs.

|Method|Purpose|
|---|---|
|`__get__`|attribute read|
|`__set__`|attribute assignment|
|`__delete__`|attribute deletion|
|`__set_name__`|learn the attribute name during class creation|

---

# Data vs Non-Data Descriptors

This distinction is extremely important because it determines **precedence**.

## Data descriptor

A descriptor is a **data descriptor** when its type defines:

```python
__set__
```

or:

```python
__delete__
```

It does not matter whether the method does anything useful.

For example:

```python
class ReadOnly:
    def __get__(self, obj, objtype=None):
        return 42

    def __set__(self, obj, value):
        raise AttributeError("read-only")
```

This is still a **data descriptor**.

Why?

Because `__set__` exists on its type.

The implementation could simply be:

```python
def __set__(self, obj, value):
    raise AttributeError
```

It still makes the descriptor a data descriptor.

---

## Non-data descriptor

A descriptor that defines only:

```python
__get__
```

is a **non-data descriptor**.

Example:

```python
class NonData:
    def __get__(self, obj, objtype=None):
        return 42
```

---

# Why the Difference Matters

The key rule is:

> **Data descriptors beat the instance `__dict__`.**

But:

> **Non-data descriptors lose to the instance `__dict__`.**

So:

```text
DATA descriptor
      ↓
instance __dict__
      ↓
NON-DATA descriptor / class attribute
```

This single distinction explains a huge amount of Python behavior.

---

# `__get__` Arguments

A descriptor normally defines:

```python
def __get__(self, obj, objtype=None):
```

There are three things to understand.

### `self`

This is the **descriptor object itself**.

The descriptor object normally lives on the class and is shared by all instances.

### `obj`

This is the object on which the attribute is being accessed.

For:

```python
c.x
```

you get:

```python
obj == c
```

For:

```python
C.x
```

you get:

```python
obj is None
```

### `objtype`

This is normally the owner/type involved in the lookup.

For:

```python
c.x
```

typically:

```python
objtype is type(c)
```

For:

```python
C.x
```

typically:

```python
objtype is C
```

---

# The Standard `obj is None` Pattern

A descriptor usually does:

```python
def __get__(self, obj, objtype=None):
    if obj is None:
        return self

    ...
```

This means:

```python
C.x
```

returns the descriptor itself.

Whereas:

```python
c.x
```

performs the descriptor's instance behavior.

This is why:

```python
Person.age
```

can give you the actual descriptor object for introspection.

---

# `__set_name__`

Python 3.6 introduced `__set_name__` through PEP 487.

It solves an annoying descriptor problem:

> How does a descriptor know the name it was assigned to?

Consider:

```python
class Person:
    age = Field()
```

During class creation, Python can tell the descriptor:

```python
Field.__set_name__(Person, "age")
```

So:

```python
class Field:

    def __set_name__(self, owner, name):
        self.name = name
        self.private_name = "_" + name
```

Now the descriptor automatically knows:

```python
self.name
# "age"

self.private_name
# "_age"
```

---

## When is `__set_name__` called?

It happens during class creation.

For:

```python
class C:
    x = Field()
```

Python calls:

```python
field.__set_name__(C, "x")
```

But:

```python
C.x = Field()
```

after the class already exists does **not** automatically call `__set_name__`.

If you do that dynamically, you must call it yourself if your descriptor requires it.

---

## Same descriptor assigned twice

This is a subtle bug:

```python
field = Field()

class C:
    x = field
    y = field
```

`__set_name__` is called twice:

```python
field.__set_name__(C, "x")
field.__set_name__(C, "y")
```

If the descriptor stores:

```python
self.name = name
```

the final value will be:

```python
"y"
```

The same descriptor object is being shared by both names.

This can silently break storage logic.

---

# Part III — The Attribute Lookup Algorithm

This is the most important section for understanding descriptors deeply.

If you understand this algorithm, most descriptor behavior becomes predictable.

When you write:

```python
obj.x
```

the conceptual lookup performed by `object.__getattribute__()` is approximately:

```text
1. Search type(obj).__mro__ for "x"

2. If found:
       If it is a DATA descriptor:
           call descriptor.__get__(obj, type(obj))
           STOP

3. Search obj.__dict__

4. If "x" exists there:
       return obj.__dict__["x"]
       STOP

5. If "x" was found on the class:
       If it is a NON-DATA descriptor:
           call descriptor.__get__(obj, type(obj))

       Otherwise:
           return the class attribute

6. If normal lookup failed:
       call __getattr__(obj, "x") if defined

7. Otherwise:
       raise AttributeError
```

The simplified precedence chain is:

> **Data descriptor → instance `__dict__` → non-data descriptor/class attribute → `__getattr__` → `AttributeError`**

Memorize that.

---

# Why Does Python Search the Class Before the Instance Dictionary?

This initially looks strange.

You might think:

```python
obj.x
```

should first check:

```python
obj.__dict__
```

But it cannot do that.

Python first needs to determine:

> "Does the class contain a data descriptor that has the right to control this attribute?"

For example:

```python
class C:
    x = Property()
```

If:

```python
c.__dict__["x"] = 100
```

the property must still win.

Therefore Python needs to inspect the class first.

---

# Data Descriptor Beats Instance Storage

Example:

```python
class D:
    def __get__(self, obj, objtype=None):
        return "descriptor"

    def __set__(self, obj, value):
        print("setting through descriptor")


class C:
    x = D()
```

Now:

```python
c = C()

c.__dict__["x"] = "instance value"

print(c.x)
```

Result:

```text
descriptor
```

Why?

Because:

```text
C.x
```

is a data descriptor.

So the lookup stops before the instance dictionary is used.

---

# Non-Data Descriptor Loses to Instance Storage

Now remove `__set__`:

```python
class D:
    def __get__(self, obj, objtype=None):
        return "descriptor"
```

Then:

```python
class C:
    x = D()
```

Now:

```python
c = C()

print(c.x)
```

gives:

```text
descriptor
```

But:

```python
c.x = "instance value"
```

creates:

```python
c.__dict__["x"] = "instance value"
```

Now:

```python
print(c.x)
```

gives:

```text
instance value
```

The instance dictionary wins because `D` is non-data.

---

# Part III.2 — Instance Assignment

For:

```python
obj.x = value
```

`object.__setattr__()` conceptually does:

```text
1. Search type(obj).__mro__ for "x"

2. If found and it defines __set__:
       call descriptor.__set__(obj, value)
       STOP

3. Otherwise:
       store x in obj.__dict__

4. If no __dict__ exists:
       raise AttributeError
```

Notice something important:

> **Non-data descriptors do not participate in assignment.**

That is why they can be shadowed.

---

# Example: Shadowing a `classmethod`

```python
class C:

    @classmethod
    def cm(cls):
        return "class method"
```

Now:

```python
c = C()

c.cm = lambda: "shadowed"
```

`classmethod` is a non-data descriptor.

Therefore assignment goes into:

```python
c.__dict__
```

Now:

```python
c.cm()
```

returns:

```text
shadowed
```

The descriptor is bypassed.

---

# Attribute Deletion

For:

```python
del obj.x
```

the same basic idea applies.

If the class provides:

```python
__delete__
```

Python delegates deletion to the descriptor.

Otherwise, it removes the attribute from the instance storage where appropriate.

---

# Part III.3 — Class Attribute Access

Now consider:

```python
C.x
```

This is different.

A class itself is an object.

More precisely:

```text
C
↓
instance of
↓
type(C)
```

So:

```python
C.x
```

is handled by:

```python
type.__getattribute__
```

rather than the normal instance lookup of `object.__getattribute__`.

Conceptually:

```text
1. Search type(C).__mro__
   This is the METACLASS MRO.

2. If a data descriptor is found there:
       invoke it with C as the object

3. Search C.__mro__

4. If an attribute is found:
       if it is a descriptor:
           call descriptor.__get__(None, C)

       otherwise:
           return the attribute

5. Fall back to the metaclass attribute if appropriate

6. Otherwise AttributeError
```

---

# The Two-Level Model

This is worth visualizing:

```text
c.x
 │
 ▼
type(c).__getattribute__
 │
 ▼
C.__mro__
 │
 ├── data descriptor
 ├── instance __dict__
 └── non-data descriptor / class attribute
```

But:

```text
C.x
 │
 ▼
type.__getattribute__
 │
 ▼
type(C).__mro__      ← metaclass
 │
 ├── metaclass data descriptor
 │
 ▼
C.__mro__
 │
 └── descriptor with obj=None
```

This is why metaclasses and descriptors can interact in powerful ways.

---

# Dunder Lookup Is Different

There is another important exception.

Implicit special-method operations such as:

```python
len(obj)
obj + other
obj == other
with obj:
```

do not simply behave like:

```python
obj.__len__()
obj.__add__()
```

Python performs special-method lookup on the **type**, using C-level machinery such as:

```text
_PyObject_LookupSpecial
```

and often ultimately uses a type slot such as:

```text
tp_len
tp_add
tp_call
```

Therefore:

```python
class C:
    pass

c = C()

c.__len__ = lambda: 5
```

does not make:

```python
len(c)
```

work.

You may be able to do:

```python
c.__len__()
```

but:

```python
len(c)
```

still fails unless the type provides the appropriate special method.

### Important principle

> **Implicit dunder operations are type-level operations, not ordinary instance attribute lookup.**

---

# Part IV — A Simple Real Descriptor

Let's build one.

We want:

```python
class Rectangle:
    width = Positive()
    height = Positive()
```

where:

```python
r.width = 10
```

is allowed, but:

```python
r.width = -10
```

fails.

---

## Implementation

```python
class Positive:
    """Data descriptor enforcing a positive number."""

    def __set_name__(self, owner, name):
        self.name = name
        self.private = "_" + name

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self

        try:
            return obj.__dict__[self.private]
        except KeyError:
            raise AttributeError(
                f"{self.name!r} is not set"
            ) from None

    def __set__(self, obj, value):
        if (
            not isinstance(value, (int, float))
            or isinstance(value, bool)
        ):
            raise TypeError(
                f"{self.name} must be a number, "
                f"got {type(value).__name__}"
            )

        if value <= 0:
            raise ValueError(
                f"{self.name} must be positive, got {value}"
            )

        obj.__dict__[self.private] = value

    def __delete__(self, obj):
        obj.__dict__.pop(self.private, None)
```

---

## Using It

```python
class Rectangle:

    width = Positive()
    height = Positive()

    def __init__(self, width, height):
        self.width = width
        self.height = height

    @property
    def area(self):
        return self.width * self.height
```

Now:

```python
r = Rectangle(3, 4)
```

The following happens:

```python
self.width = width
```

which becomes conceptually:

```python
Rectangle.width.__set__(self, width)
```

Likewise:

```python
self.height = height
```

calls:

```python
Rectangle.height.__set__(self, height)
```

---

## Reading

```python
r.width
```

causes:

```python
Positive.__get__(r, Rectangle)
```

which retrieves:

```python
r.__dict__["_width"]
```

Therefore:

```python
vars(r)
```

looks like:

```python
{
    "_width": 3,
    "_height": 4
}
```

The descriptor object itself is **not** storing `3`.

---

## Validation

```python
r.width = -1
```

causes:

```python
Positive.__set__(r, -1)
```

and raises:

```text
ValueError
```

Likewise:

```python
r.width = "big"
```

raises:

```text
TypeError
```

---

# Why Is `Positive` a Data Descriptor?

Because it defines:

```python
__set__
```

and:

```python
__delete__
```

Therefore:

```text
Positive
    ↓
data descriptor
    ↓
beats r.__dict__
```

Even if somebody manually does:

```python
r.__dict__["width"] = 999
```

the descriptor still wins because the descriptor is found first.

---

# Class-Level Introspection

When:

```python
Rectangle.width
```

is evaluated, Python calls:

```python
Positive.__get__(
    None,
    Rectangle
)
```

Therefore:

```python
if obj is None:
    return self
```

returns the descriptor.

So you can inspect:

```python
Rectangle.width.name
```

and get:

```text
width
```

This pattern is extremely common.

---

# Part V — What Descriptors Actually Implement

Now we can connect descriptors to Python's built-in machinery.

---

# 5.1 Functions Are Descriptors

This is one of the most important facts.

Consider:

```python
class Person:

    def greet(self):
        return "hello"
```

You might think:

```python
p.greet
```

simply retrieves a function.

It doesn't.

The function object implements the descriptor protocol.

Conceptually:

```python
class Function:

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self

        return MethodType(self, obj)
```

So:

```python
Person.greet
```

returns the underlying function.

But:

```python
p.greet
```

produces a **bound method**.

---

# What Is a Bound Method?

Conceptually it contains:

```text
__func__ → original function
__self__ → instance
```

For:

```python
p.greet()
```

the bound method effectively calls:

```python
greet(p)
```

This gives us a very important conclusion:

> **`self` is not a special keyword injected directly into the function by the interpreter.**

Instead, method binding is produced by descriptor behavior.

The descriptor creates the relationship:

```text
function + instance
       ↓
bound method
```

---

# CPython Optimization: `LOAD_METHOD`

There is an important performance detail.

The conceptual model says:

```python
p.greet
```

creates a bound method object.

But CPython does not necessarily create a `MethodType` object for every immediate method call.

Since Python 3.11, the specializing/adaptive interpreter can optimize patterns such as:

```python
p.greet()
```

using specialized bytecode and the `LOAD_METHOD` / call path.

The implementation can avoid creating an intermediate bound-method object in common cases.

So distinguish:

### Semantic model

```text
function.__get__()
      ↓
bound method
```

### Optimized CPython execution

```text
LOAD_METHOD / specialized path
      ↓
avoid unnecessary temporary bound-method allocation
```

The descriptor model remains the conceptual foundation.

---

# 5.2 `property`

`property` is the canonical example of a **data descriptor**.

Conceptually:

```python
class Property:

    def __init__(self, fget=None, fset=None, fdel=None, doc=None):
        self.fget = fget
        self.fset = fset
        self.fdel = fdel
        self.__doc__ = doc

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self

        if self.fget is None:
            raise AttributeError

        return self.fget(obj)

    def __set__(self, obj, value):
        if self.fset is None:
            raise AttributeError("can't set attribute")

        self.fset(obj, value)
```

The important point is:

```python
__set__
```

exists even when there is no setter.

Therefore `property` is a **data descriptor**.

That is why:

```python
@property
def x(self):
    ...
```

cannot be bypassed simply by putting:

```python
obj.__dict__["x"] = ...
```

---

# Why Does `@x.setter` Reuse the Name?

Consider:

```python
class C:

    @property
    def x(self):
        return self._x

    @x.setter
    def x(self, value):
        self._x = value
```

The setter decorator does not mutate the original property.

Conceptually it creates a **new property object** containing:

```text
old getter
+
new setter
```

Therefore the class name must be rebound:

```python
x = new_property
```

That is why the decorated setter uses the same name:

```python
def x(...)
```

---

# Property Recursion

This is wrong:

```python
class C:

    @property
    def x(self):
        return self.x
```

Why?

Because:

```python
self.x
```

again invokes the same property.

So:

```text
x getter
   ↓
self.x
   ↓
x getter
   ↓
self.x
   ↓
...
```

Use backing storage:

```python
class C:

    @property
    def x(self):
        return self._x
```

---

# 5.3 `classmethod`

Conceptually:

```python
class ClassMethod:

    def __get__(self, obj, objtype=None):
        if objtype is None:
            objtype = type(obj)

        return MethodType(self.f, objtype)
```

The important difference is:

```text
normal method:
function + instance
       ↓
bound method

classmethod:
function + class
       ↓
bound method
```

So:

```python
class C:

    @classmethod
    def create(cls):
        return cls()
```

calling:

```python
C.create()
```

binds:

```python
cls = C
```

And:

```python
class Child(C):
    pass

Child.create()
```

binds:

```python
cls = Child
```

This is why class methods are useful for **polymorphic alternative constructors**.

---

# 5.4 `staticmethod`

Conceptually:

```python
class StaticMethod:

    def __get__(self, obj, objtype=None):
        return self.f
```

There is no instance or class binding.

Therefore:

```python
class C:

    @staticmethod
    def add(a, b):
        return a + b
```

does not become:

```python
add(self, a, b)
```

or:

```python
add(cls, a, b)
```

It simply returns the underlying function.

Both:

```python
C.add(1, 2)
```

and:

```python
C().add(1, 2)
```

call the same function without automatic binding.

---

# Version Details

Two useful Python-version details:

### `staticmethod`

Since Python 3.10, `staticmethod` objects are directly callable.

### `classmethod` + `property`

Python 3.9 introduced support for chaining:

```python
@classmethod
@property
```

but that behavior was removed in Python 3.13.

The lesson is:

> Do not assume every decorator combination that happens to work in one Python version is a stable language abstraction.

---

# 5.5 `__slots__`

`__slots__` is another excellent example of descriptors implemented at the C level.

Consider:

```python
class Point:
    __slots__ = ("x", "y")
```

Conceptually Python creates descriptor objects for the slots.

For example:

```python
Point.x
```

has a type similar to:

```text
member_descriptor
```

This is a **C-level data descriptor**.

---

# Why Does `__slots__` Save Memory?

A normal object commonly has an instance dictionary:

```python
obj.__dict__
```

With:

```python
class Point:
    __slots__ = ("x", "y")
```

the object can store those attributes in predefined locations in its object layout instead of using a normal instance dictionary.

The slot descriptor knows where the value belongs.

Conceptually:

```text
Point.x
   ↓
member_descriptor
   ↓
fixed offset in object layout
```

rather than:

```text
obj.__dict__["x"]
```

---

# `__slots__` Is Still Descriptor-Based

This is an important connection:

```python
__slots__
```

is not some completely separate attribute system.

It creates C-level descriptors that participate in attribute lookup.

That is why:

```python
Point.x
```

is itself an object representing the slot.

---

# Subclass of a Slotted Class

Consider:

```python
class Base:
    __slots__ = ("x",)


class Child(Base):
    pass
```

`Child` gets a normal instance dictionary unless it also defines appropriate slots.

So:

```python
c = Child()

c.extra = 10
```

can work.

But inherited:

```python
c.x
```

is still controlled by the inherited `member_descriptor`.

Therefore:

```python
c.__dict__["x"] = 999
```

does not override the slot.

The inherited data descriptor still wins.

---

# 5.6 `super`

`super` has its own descriptor and attribute-lookup machinery.

When you write:

```python
super().x
```

Python is not simply doing:

```python
self.x
```

Instead, `super` knows:

```text
__thisclass__
__self__
```

and performs lookup in the MRO **starting after `__thisclass__`**.

For example:

```python
class A:
    def f(self):
        return "A"


class B(A):
    def f(self):
        return super().f()
```

Inside `B.f`, `super()` effectively says:

> "Start looking for `f` after `B` in the MRO, but bind the result to the original instance."

If it finds a descriptor, that descriptor is invoked appropriately.

---

# 5.7 C-Level Descriptors

CPython contains several descriptor types implemented in C.

Two important ones are:

```text
member_descriptor
getset_descriptor
```

### `member_descriptor`

Commonly associated with:

```python
__slots__
```

and fixed object-layout storage.

### `getset_descriptor`

Used for attributes implemented with C-level getter/setter functions.

Even:

```python
type(obj).__dict__
```

involves descriptor machinery.

For example, `__dict__` itself is exposed using a C-level descriptor.

This is part of why:

```python
vars(obj)
```

can access an object's dictionary.

---

# Part VI — Where Descriptor State Lives

This is one of the most common descriptor implementation mistakes.

Consider:

```python
class Field:

    def __set__(self, obj, value):
        self.value = value
```

This looks reasonable.

It is usually wrong.

Why?

Because:

```python
class Person:
    age = Field()
```

creates **one** `Field` object.

That one descriptor is shared by every `Person`.

So:

```python
a = Person()
b = Person()
```

both use:

```text
Person.age
     ↓
same Field object
```

---

# The Shared-State Bug

```python
class Broken:

    def __get__(self, obj, objtype=None):
        return self.value

    def __set__(self, obj, value):
        self.value = value


class C:
    x = Broken()
```

Now:

```python
a = C()
b = C()

a.x = 1
b.x = 2
```

Both assignments modify:

```python
C.x.value
```

Therefore:

```python
a.x
```

can return:

```text
2
```

The descriptor is shared.

---

# Correct Pattern

Store per-instance state on the instance.

For example:

```python
obj.__dict__["_x"] = value
```

The architecture becomes:

```text
Class
 │
 └── x → ONE descriptor object
             │
             ├── instance A → _x = 10
             ├── instance B → _x = 20
             └── instance C → _x = 30
```

The descriptor contains the **behavior**.

The instance contains the **state**.

This is a very useful mental model.

---

# Three Common Storage Strategies

## Option 1 — Private key in `__dict__`

Most common:

```python
obj.__dict__["_x"] = value
```

Advantages:

- simple
    
- fast
    
- GC-friendly
    
- easy to understand
    
- normally picklable
    

Disadvantage:

- requires an instance `__dict__`
    
- private backing fields appear in `vars(obj)`
    

---

# Option 2 — Same Name in Instance Dictionary

This works for **non-data descriptors**.

Example:

```python
class cached_property:
    ...
```

It can calculate:

```python
value = self.func(obj)
```

and then:

```python
obj.__dict__[self.name] = value
```

Because the descriptor is non-data, the next lookup sees:

```text
instance dictionary
```

and stops.

The descriptor is effectively removed from the hot path.

---

# Option 3 — `WeakKeyDictionary`

A descriptor can maintain external state:

```python
WeakKeyDictionary()
```

conceptually:

```text
descriptor
   │
   └── WeakKeyDictionary
          │
          ├── instance A → value
          ├── instance B → value
          └── instance C → value
```

This is useful when:

- instances have no `__dict__`
    
- you don't want to modify instance storage
    

But there are costs.

Instances generally need to be:

- hashable
    
- weak-referenceable
    

and there is additional lookup overhead.

So it is usually not the first choice.

---

# Part VII — `cached_property`: The Non-Data Descriptor Trick

`cached_property` is a beautiful demonstration of why non-data descriptors exist.

Conceptually:

```python
class cached_property:

    def __init__(self, func):
        self.func = func

    def __set_name__(self, owner, name):
        self.name = name

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self

        value = self.func(obj)

        obj.__dict__[self.name] = value

        return value
```

Suppose:

```python
class User:

    @cached_property
    def profile(self):
        print("computing...")
        return expensive_operation()
```

First:

```python
u.profile
```

causes:

```text
cached_property.__get__
       ↓
expensive_operation()
       ↓
obj.__dict__["profile"] = result
```

Now the instance dictionary contains:

```python
{
    "profile": result
}
```

---

# Why Does the Descriptor Stop Running?

Because `cached_property` is a **non-data descriptor**.

Remember:

```text
data descriptor
      >
instance dictionary
      >
non-data descriptor
```

After caching:

```text
u.profile
   ↓
instance dictionary contains "profile"
   ↓
return cached value
```

The descriptor is no longer involved.

This is extremely efficient.

---

# The Trade-Off

The same mechanism that makes `cached_property` fast also means it can be overwritten:

```python
u.profile = "something else"
```

Because the descriptor is non-data.

That is intentional.

---

# Invalidating a Cached Property

You can remove:

```python
obj.__dict__["profile"]
```

Then the descriptor becomes active again.

For example:

```python
obj.__dict__.pop("profile", None)
```

The next:

```python
obj.profile
```

recomputes the value.

This creates a useful pattern:

```text
data descriptor
      ↓
mutates object
      ↓
invalidate non-data cached_property
```

The two descriptor categories can therefore work together.

---

# Part VIII — Production-Style Descriptor System

Now let's combine the ideas into something closer to an ORM/model field system.

The system will provide:

- typed fields
    
- validation
    
- coercion
    
- change tracking
    
- defaults
    
- `__set_name__`
    
- inheritance
    
- class-level schema
    
- cached summaries
    
- metaclass descriptors
    

---

# Base `Field`

```python
class Field:

    _ANY = object()

    def __init__(
        self,
        type_=None,
        *,
        default=_ANY,
        required=True,
        doc=None,
    ):
        self.type = type_
        self.default = default
        self.required = required
        self.__doc__ = doc

    def __set_name__(self, owner, name):
        self.name = name
        self.slot = f"__field_{name}"

        owner._fields = {
            **getattr(owner, "_fields", {}),
            name: self,
        }

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self

        if self.slot in obj.__dict__:
            return obj.__dict__[self.slot]

        if self.default is not Field._ANY:
            return self.default

        raise AttributeError(
            f"{objtype.__name__}.{self.name} is unset"
        )

    def __set__(self, obj, value):
        value = self.validate(obj, value)

        old = obj.__dict__.get(self.slot, Field._ANY)

        obj.__dict__[self.slot] = value

        if old is not Field._ANY and old != value:
            obj._changes.append(
                (
                    self.name,
                    old,
                    value,
                    datetime.now(),
                )
            )

        obj.__dict__.pop("_summary", None)

    def __delete__(self, obj):
        if self.required:
            raise AttributeError(
                f"cannot delete required field {self.name!r}"
            )

        obj.__dict__.pop(self.slot, None)

    def validate(self, obj, value):
        if self.type is not None:
            if not isinstance(value, self.type):
                raise TypeError(
                    f"{self.name} expects "
                    f"{self.type.__name__}, "
                    f"got {type(value).__name__}"
                )

        return value
```

---

# Integer Field

```python
class Integer(Field):

    def __init__(self, *, min=None, max=None, **kw):
        super().__init__(int, **kw)

        self.min = min
        self.max = max

    def validate(self, obj, value):
        value = super().validate(obj, value)

        if isinstance(value, bool):
            raise TypeError(
                f"{self.name} must not be a bool"
            )

        if self.min is not None and value < self.min:
            raise ValueError(
                f"{self.name} must be >= {self.min}"
            )

        if self.max is not None and value > self.max:
            raise ValueError(
                f"{self.name} must be <= {self.max}"
            )

        return value
```

Notice:

```python
bool
```

is an `int` subclass:

```python
isinstance(True, int)
# True
```

Therefore explicit rejection is required if the model wants actual integers.

---

# String Field

```python
class String(Field):

    def __init__(
        self,
        *,
        maxlen=None,
        strip=True,
        **kw
    ):
        super().__init__(str, **kw)

        self.maxlen = maxlen
        self.strip = strip

    def validate(self, obj, value):
        value = super().validate(obj, value)

        if self.strip:
            value = value.strip()

        if (
            self.maxlen is not None
            and len(value) > self.maxlen
        ):
            raise ValueError(
                f"{self.name} exceeds {self.maxlen} chars"
            )

        return value
```

This demonstrates something important:

> A descriptor does not have to merely validate. It can also **coerce or transform** values.

---

# Cached Summary

```python
class cached_property:

    def __init__(self, func):
        self.func = func
        self.__doc__ = func.__doc__

    def __set_name__(self, owner, name):
        self.name = name

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self

        value = self.func(obj)

        obj.__dict__[self.name] = value

        return value
```

This is a non-data descriptor.

---

# Metaclass Descriptor

Now we want:

```python
Person.schema
```

to return schema information.

Define:

```python
class ModelMeta(type):

    @property
    def schema(cls):
        return {
            name: type(field).__name__
            for name, field in cls._fields.items()
        }
```

Here the property lives on the **metaclass**.

Therefore:

```python
Person.schema
```

works.

But:

```python
person.schema
```

does not.

Why?

Because:

```text
person
  ↓
Person.__mro__
```

does not include:

```text
ModelMeta.__mro__
```

The metaclass controls attributes of the **class object**, not ordinary instances.

---

# Base Model

```python
class Model(metaclass=ModelMeta):

    _fields = {}

    def __init_subclass__(cls, **kw):
        super().__init_subclass__(**kw)

        cls._fields = dict(cls._fields)

    def __init__(self, **kw):
        self._changes = []

        for name, field in self._fields.items():

            if name in kw:
                setattr(self, name, kw.pop(name))

            elif (
                field.required
                and field.default is Field._ANY
            ):
                raise TypeError(
                    f"missing required field {name!r}"
                )

        if kw:
            raise TypeError(
                f"unknown fields: {sorted(kw)}"
            )

    @cached_property
    def _summary(self):
        print("  [computing summary…]")

        return ", ".join(
            f"{name}={getattr(self, name)!r}"
            for name in self._fields
        )

    def __repr__(self):
        return (
            f"{type(self).__name__}"
            f"({self._summary})"
        )
```

---

# Concrete Model

```python
class Person(Model):

    name = String(
        maxlen=50,
        doc="Full name",
    )

    age = Integer(
        min=0,
        max=150,
    )

    email = String(
        required=False,
        default="",
    )
```

And:

```python
class Employee(Person):

    salary = Integer(min=0)
```

---

# What Happens During Class Creation?

This is worth following carefully.

When Python creates:

```python
class Person(Model):
    name = String(...)
    age = Integer(...)
    email = String(...)
```

the class body first creates descriptor objects.

Then the class machinery invokes:

```python
name_field.__set_name__(Person, "name")
age_field.__set_name__(Person, "age")
email_field.__set_name__(Person, "email")
```

Each descriptor registers itself in:

```python
Person._fields
```

So the class now has schema information.

---

# Creating an Instance

```python
p = Person(
    name="  Ada Lovelace  ",
    age=36,
)
```

Inside `Model.__init__`:

```python
setattr(self, "name", value)
```

causes:

```text
Person.name
     ↓
String.__set__
     ↓
String.validate
     ↓
Field.validate
     ↓
strip()
     ↓
store "__field_name"
```

So:

```python
p.name
```

returns:

```text
"Ada Lovelace"
```

rather than:

```text
"  Ada Lovelace  "
```

---

# Actual Instance Storage

The descriptor itself does not contain Ada's name.

The instance does.

Conceptually:

```python
vars(p)
```

contains something like:

```python
{
    "_changes": [],
    "__field_name": "Ada Lovelace",
    "__field_age": 36
}
```

The descriptor provides the rules for accessing that data.

---

# Defaults

For:

```python
email = String(
    required=False,
    default=""
)
```

reading:

```python
p.email
```

does not necessarily store the default.

`Field.__get__` does:

```python
if self.slot in obj.__dict__:
    return obj.__dict__[self.slot]

if self.default is not Field._ANY:
    return self.default
```

So the result can be:

```text
""
```

without:

```python
"__field_email"
```

being stored.

This is an important distinction:

> **A default value can be returned by a descriptor without becoming instance state.**

---

# Change Tracking

When:

```python
p.age = 37
```

the data descriptor receives:

```python
Integer.__set__(p, 37)
```

which validates and stores the value.

It can compare:

```text
old = 36
new = 37
```

and record:

```python
(
    "age",
    36,
    37,
    datetime(...)
)
```

The descriptor therefore becomes a natural place for:

- validation
    
- coercion
    
- auditing
    
- change tracking
    
- cache invalidation
    

---

# Cached Summary

First:

```python
repr(p)
```

calls:

```python
p._summary
```

The cached property runs:

```text
_compute summary
      ↓
store p.__dict__["_summary"]
```

Second:

```python
repr(p)
```

finds:

```python
"_summary"
```

in the instance dictionary.

Because `cached_property` is non-data:

```text
instance dict wins
```

So the descriptor is bypassed.

---

# Cache Invalidation

When:

```python
p.age = 37
```

the `Field.__set__` implementation does:

```python
obj.__dict__.pop("_summary", None)
```

Therefore the cache disappears.

The next:

```python
repr(p)
```

causes `_summary` to be calculated again.

This is a very useful design pattern:

```text
DATA DESCRIPTOR
      │
      │ mutation
      ▼
invalidate instance cache
      │
      ▼
NON-DATA cached_property
```

---

# Inheritance and MRO

For:

```python
class Employee(Person):
    salary = Integer(min=0)
```

`Employee` inherits:

```text
name
age
email
```

from `Person`.

Its MRO is conceptually:

```text
Employee
   ↓
Person
   ↓
Model
   ↓
object
```

Descriptor lookup follows this MRO.

Therefore:

```python
employee.age
```

finds the `age` descriptor defined by `Person`.

---

# Why `__init_subclass__` Copies `_fields`

If:

```python
Person._fields
```

were shared directly, modifying:

```python
Employee._fields
```

could accidentally modify the parent schema.

So:

```python
def __init_subclass__(cls, **kw):
    super().__init_subclass__(**kw)
    cls._fields = dict(cls._fields)
```

gives each subclass its own dictionary.

Thus:

```python
Employee._fields
```

contains:

```text
name
age
email
salary
```

while:

```python
Person._fields
```

contains only:

```text
name
age
email
```

---

# Part VIII — `__getattr__` vs `__getattribute__`

These two are often confused.

---

## `__getattribute__`

This is the main attribute-access interception point.

Conceptually:

```python
obj.x
```

starts through:

```python
obj.__getattribute__("x")
```

If you override:

```python
def __getattribute__(self, name):
    ...
```

you are intercepting **every attribute lookup**.

This is powerful and dangerous.

For example:

```python
class C:

    def __getattribute__(self, name):
        return self.x
```

can recurse forever.

Normally you need:

```python
super().__getattribute__(name)
```

or:

```python
object.__getattribute__(self, name)
```

to avoid recursion.

---

# `__getattr__`

`__getattr__` is different.

It is a **fallback**.

It runs only after normal lookup fails with:

```python
AttributeError
```

Example:

```python
class Proxy:

    def __getattr__(self, name):
        return getattr(self.target, name)
```

This is useful for:

- proxies
    
- delegation
    
- dynamic attributes
    
- compatibility layers
    

---

# Important Descriptor Interaction

Suppose:

```python
descriptor.__get__()
```

raises:

```python
AttributeError
```

Normal attribute lookup can then reach:

```python
__getattr__
```

This means a genuine error inside a descriptor can potentially be hidden by a fallback implementation.

For debugging:

> If an attribute unexpectedly produces a fallback value, check whether a descriptor internally raised `AttributeError`.

---

# Part IX — Descriptors on Metaclasses

Remember:

```text
object
   ↑
instance
```

and:

```text
type
   ↑
class
```

A class is itself an object:

```python
Person
```

is an instance of:

```python
ModelMeta
```

Therefore:

```python
Person.schema
```

can be controlled by a descriptor on:

```python
ModelMeta
```

This is one of the most powerful ideas in advanced Python.

---

# Metaclass Data Descriptor Precedence

Suppose a metaclass contains a data descriptor called:

```python
x
```

and the class itself contains:

```python
class C:
    x = 100
```

The metaclass data descriptor can win.

Why?

Class lookup first checks the metaclass MRO for a **data descriptor**.

So:

```text
metaclass data descriptor
        >
class dictionary
```

This is the class-level equivalent of:

```text
instance data descriptor
        >
instance dictionary
```

---

# Why Instances Don't See Metaclass Properties

If:

```python
class Meta(type):

    @property
    def schema(cls):
        ...
```

and:

```python
class Model(metaclass=Meta):
    ...
```

then:

```python
Model.schema
```

works.

But:

```python
model.schema
```

does not automatically use `Meta.schema`.

Why?

Because instance lookup searches:

```python
type(model).__mro__
```

which is something like:

```text
Model
Model's bases
object
```

It does not search:

```text
Meta
type
```

The metaclass is involved when accessing the **class object**.

---

# Part X — Other Python Features Using Descriptor Machinery

Descriptors appear in many standard-library and framework systems.

---

## ABCs

Abstract methods and properties interact with:

```python
__isabstractmethod__
```

Descriptors such as `property` propagate this information so abstract base class machinery can determine whether a class is still abstract.

---

## Dataclasses

Dataclasses support descriptor-typed fields.

There is a subtle interaction:

When processing defaults, dataclass machinery may call the descriptor through:

```python
descriptor.__get__(None, cls)
```

The result can therefore affect how the field is interpreted.

This is an advanced edge case worth knowing when combining descriptors with `dataclasses`.

---

## Enum

`Enum` uses descriptor machinery including:

```python
DynamicClassAttribute
```

This helps make member attributes such as:

```python
member.name
member.value
```

work without simply putting ordinary values into the same class-level namespace.

---

# Part XI — Performance

Descriptors are powerful, but they are not free.

---

# Python-Level Descriptor Cost

A Python-defined descriptor can require a Python-level method call:

```python
descriptor.__get__(...)
```

A raw instance dictionary access is generally cheaper.

Therefore:

```python
obj.__dict__["x"]
```

can be significantly cheaper than a Python-level:

```python
@property
def x(self):
    return self._x
```

in a very hot loop.

The exact cost depends heavily on Python version, workload, specialization, and implementation.

So don't treat "10× slower" as a universal constant.

The important architectural point is:

> **Descriptor dispatch has overhead compared with direct storage, especially for Python-level descriptors.**

---

# C-Level Descriptors Are Different

Descriptors implemented in C are generally much cheaper than Python-defined descriptor methods.

Examples include:

```text
member_descriptor
getset_descriptor
function
```

This is why:

```python
__slots__
```

can be very efficient.

---

# CPython 3.11+ Adaptive Interpreter

Modern CPython has an adaptive/specializing interpreter.

Attribute access such as:

```python
obj.x
```

starts from generic bytecode behavior.

The interpreter can observe what happens repeatedly and specialize the operation.

You may encounter specialized forms such as:

```text
LOAD_ATTR_INSTANCE_VALUE
LOAD_ATTR_SLOT
LOAD_ATTR_PROPERTY
```

The exact specialization behavior is an implementation detail and can change between Python releases.

The important concept is:

```text
generic LOAD_ATTR
       ↓
observe runtime types
       ↓
specialize
       ↓
fast path
```

---

# Type Version Tags

CPython can associate cached assumptions with a type.

Conceptually:

```text
call site
   ↓
"I usually see type C here"
   ↓
use optimized attribute path
```

But the assumption must remain valid.

If the class is mutated, relevant caches can be invalidated or deoptimized.

For example:

```python
C.x = something_else
```

can invalidate assumptions associated with attribute lookup.

Therefore:

> **Monkey-patching classes can interfere with specialization and cache effectiveness.**

Do not interpret this as "every class mutation destroys all caches globally"; the real invalidation machinery is more specific.

---

# `__slots__` Performance

If your actual requirement is simply:

> "I want compact, controlled object storage."

then descriptors may already be provided by:

```python
__slots__
```

You don't need to implement a custom descriptor.

`__slots__` gives you:

```text
fixed storage
+
C-level descriptor
+
no normal instance __dict__ by default
```

---

# `cached_property` Performance

After the first calculation:

```python
obj.cached
```

can become approximately:

```text
instance dictionary lookup
```

because the non-data descriptor has written the result into:

```python
obj.__dict__
```

This is the fundamental optimization behind the pattern.

---

# Part XII — Design Rules

Here is the practical decision framework.

---

## Use a Data Descriptor When...

You need the attribute to **always be controlled**.

Examples:

```text
validation
type enforcement
coercion
change tracking
computed storage
ORM fields
access control
cache invalidation
```

Because:

```text
data descriptor
      >
instance dictionary
```

the instance cannot simply bypass the descriptor through normal assignment.

---

# Use a Non-Data Descriptor When...

You want the instance to be able to override the behavior.

Examples:

```text
lazy computation
cached values
default behavior
method binding
```

The important property is:

```text
instance dictionary
      >
non-data descriptor
```

---

# Use `property` When...

You have one or a few attributes with custom behavior:

```python
class User:

    @property
    def age(self):
        return self._age
```

There is no reason to build a reusable descriptor abstraction for a single trivial property.

---

# Use a Custom Descriptor When...

The same behavior is repeated:

```python
class User:
    age = Integer(...)
    name = String(...)


class Product:
    price = Positive(...)
    quantity = Integer(...)
```

A descriptor lets you implement the behavior once.

This is where descriptors become an architectural abstraction rather than just a Python trick.

---

# Use `__slots__` When...

Your main requirement is:

```text
controlled storage
+
lower memory overhead
+
fixed attributes
```

rather than sophisticated validation or business logic.

---

# Use `__getattr__` When...

Your requirement is:

```text
"If normal lookup fails, dynamically provide/delegate the attribute."
```

Good for:

```text
proxies
delegation
dynamic APIs
compatibility layers
```

---

# Use `__getattribute__` When...

You genuinely need to intercept **all attribute access**.

This is powerful but easy to get wrong.

It is much lower-level than most application code needs.

---

# Use `__init_subclass__` When...

You need to customize subclass creation without requiring a full metaclass.

It is often the simpler solution for:

```text
registration
validation
configuration
plugin discovery
schema collection
```

---

# Use a Metaclass When...

You specifically need to control **class creation or class behavior itself**.

Do not reach for a metaclass just because descriptors are involved.

Often:

```python
__init_subclass__
```

or a descriptor is enough.

---

# Part XIII — The Mental Model

The easiest way to understand the whole system is to separate:

## Behavior

Stored on the class:

```text
C.x
 ↓
descriptor
 ↓
__get__
__set__
__delete__
```

## State

Stored on the instance:

```text
obj
 ↓
__dict__
 ↓
_x = 10
```

So:

```text
             CLASS
               │
               ▼
        ┌──────────────┐
        │ Descriptor   │
        │              │
        │ __get__       │
        │ __set__       │
        │ __delete__    │
        └──────┬───────┘
               │
               │ controls
               ▼
          ┌───────────┐
          │ INSTANCE  │
          │           │
          │ __dict__  │
          │ _x = 10   │
          └───────────┘
```

The descriptor is usually the **rule**.

The instance dictionary is usually the **data**.

---

# Part XIV — The Complete Precedence Picture

For:

```python
obj.x
```

remember:

```text
                obj.x
                  │
                  ▼
       type(obj).__mro__
                  │
                  ▼
       Is x a DATA descriptor?
             /          \
           YES           NO
            │             │
            ▼             ▼
      descriptor      obj.__dict__
        __get__           │
            │          found?
            │          /    \
            │        YES     NO
            │         │       │
            │         ▼       ▼
            │      return   class x
            │                │
            │                ▼
            │        NON-DATA descriptor?
            │             /       \
            │           YES        NO
            │            │          │
            │            ▼          ▼
            │       descriptor    return
            │         __get__     class value
            │
            ▼
          result
```

And if normal lookup fails:

```text
AttributeError
      ↓
__getattr__
```

---

# Part XV — Hard Interview Questions

These are the questions I would expect a senior Python engineer to answer precisely.

---

## 1. What makes an object a descriptor?

Its **type** defines one or more of:

```python
__get__
__set__
__delete__
```

At the CPython C level, this corresponds to descriptor-related type slots such as:

```text
tp_descr_get
tp_descr_set
```

The important point is:

> Python checks the descriptor behavior on the **type of the attribute object**, not by simply looking for methods on the descriptor instance.

---

## 2. What is the difference between a data and non-data descriptor?

A data descriptor defines:

```python
__set__
```

or:

```python
__delete__
```

and therefore outranks the instance dictionary.

A non-data descriptor defines only:

```python
__get__
```

and therefore loses to the instance dictionary.

---

## 3. Does a `__set__` that only raises still make it a data descriptor?

Yes.

For example:

```python
def __set__(self, obj, value):
    raise AttributeError
```

still makes the descriptor a data descriptor.

The **presence** of the descriptor's `__set__` implementation matters.

---

## 4. What is the descriptor precedence chain?

For ordinary instance reads:

```text
data descriptor
    >
instance __dict__
    >
non-data descriptor / class attribute
    >
__getattr__
    >
AttributeError
```

---

## 5. Why doesn't a descriptor inside an instance dictionary execute?

Because descriptor lookup is triggered by attributes found through the **type/MRO**.

Values retrieved from:

```python
obj.__dict__
```

are returned as ordinary values.

Python does not recursively ask:

> "Is this instance-dictionary value itself a descriptor?"

---

## 6. What does `object.__setattr__` do?

Conceptually:

```text
search class MRO
       ↓
find __set__?
   /       \
 YES        NO
  │          │
  ▼          ▼
call       obj.__dict__
__set__    assignment
```

If there is no instance dictionary, assignment can fail.

---

## 7. Why can a non-data descriptor be shadowed?

Because it has no:

```python
__set__
```

So:

```python
obj.x = value
```

normally creates:

```python
obj.__dict__["x"] = value
```

and instance storage has higher precedence than the non-data descriptor.

---

## 8. What is `obj` inside `__get__` when accessing through the class?

For:

```python
C.x
```

the descriptor receives:

```python
obj = None
objtype = C
```

That is why descriptors commonly implement:

```python
if obj is None:
    return self
```

---

## 9. Why does `C.method` differ from `c.method`?

Because `function` is a descriptor.

Conceptually:

```text
C.method
    ↓
function.__get__(None, C)
    ↓
function
```

but:

```text
c.method
    ↓
function.__get__(c, C)
    ↓
bound method
```

---

## 10. How does class attribute lookup differ from instance lookup?

Instance lookup is performed through the object's type.

Class lookup is performed through the class object's type — the **metaclass**.

So:

```text
obj.x
```

and:

```text
C.x
```

use related but different lookup paths.

---

## 11. Can a metaclass data descriptor beat an attribute in the class?

Yes.

A metaclass data descriptor is considered before the class's own attribute in class-level lookup.

Conceptually:

```text
metaclass data descriptor
        >
class attribute
```

---

## 12. Why doesn't an instance see a metaclass property?

Because:

```python
instance
```

searches:

```python
type(instance).__mro__
```

not the metaclass MRO.

Metaclass attributes control the **class object**.

---

## 13. How is `self` actually passed to a method?

Conceptually, `function.__get__` binds the function to the instance and produces a bound method containing:

```text
__func__
__self__
```

Calling the bound method supplies the instance as the first argument.

The specializing interpreter may optimize away temporary method-object creation for common calls, but the descriptor/binding model remains the semantic foundation.

---

## 14. Why is `function` a non-data descriptor?

Because it defines `__get__` but not `__set__`.

This allows:

```python
obj.method = replacement
```

to shadow the class-level method for that particular instance.

It also fits Python's method-binding model.

---

## 15. What does `__slots__` create?

C-level slot descriptors, commonly:

```text
member_descriptor
```

These are data descriptors that access storage associated with a fixed position in the object layout.

---

## 16. What happens when a slotted subclass does not define `__slots__`?

The subclass can regain an instance:

```python
__dict__
```

but inherited slot descriptors remain data descriptors.

Therefore an instance-dictionary entry with the same slot name does not override the inherited slot descriptor through normal lookup.

---

## 17. How does `@x.setter` work?

It returns a **new `property` object** containing the existing getter and the new setter.

Therefore:

```python
@property
def x(...):
    ...

@x.setter
def x(...):
    ...
```

rebinds the name `x` to the new property.

---

## 18. What is `cached_property`'s trick?

It is a **non-data descriptor**.

On first access:

```text
descriptor.__get__
       ↓
compute
       ↓
obj.__dict__["name"] = result
```

Later:

```text
obj.__dict__["name"]
```

wins over the non-data descriptor.

---

## 19. How do you invalidate a cached property?

Remove the cached value:

```python
obj.__dict__.pop("name", None)
```

The next lookup reaches the descriptor again.

---

## 20. How does `super().x` work?

`super` performs MRO lookup beginning **after the class represented by `__thisclass__`**.

It uses the original object for binding.

If it finds a descriptor, the descriptor is invoked according to the appropriate binding rules.

---

## 21. What does `__set_name__` solve?

It lets a descriptor learn:

```text
owner class
+
attribute name
```

during class creation.

It removes the need for:

```python
Field("age")
```

when the descriptor can infer:

```python
age = Field()
```

---

## 22. When is `__set_name__` not called?

When you attach the descriptor after class creation:

```python
C.x = Field()
```

The class creation machinery is no longer processing the assignment.

You need to arrange any initialization manually.

---

## 23. What happens if one descriptor object is assigned to two names?

`__set_name__` runs twice.

If the descriptor stores the name internally, the second call can overwrite the first.

This can corrupt per-name storage.

---

## 24. Why should a descriptor raise `AttributeError` for missing attributes?

Because Python's attribute machinery recognizes:

```python
AttributeError
```

as the standard "attribute does not exist" signal.

It is important for:

```python
getattr(obj, name, default)
```

and:

```python
hasattr(obj, name)
```

and for triggering:

```python
__getattr__
```

A `KeyError` does not have the same meaning.

---

## 25. How can a descriptor bug be accidentally hidden?

Suppose:

```python
descriptor.__get__()
```

raises:

```python
AttributeError
```

Normal lookup can then invoke:

```python
__getattr__
```

A poorly designed fallback might return another value.

The original bug can therefore appear as:

> "The attribute works, but gives a strange result."

---

## 26. Why is storing state on the descriptor dangerous?

Because:

```python
class C:
    x = Descriptor()
```

creates one descriptor object shared by all instances.

Therefore:

```python
a.x = 1
b.x = 2
```

can overwrite the same descriptor state.

Per-instance data should normally live on:

```python
obj
```

not:

```python
descriptor
```

---

## 27. When might you use `WeakKeyDictionary`?

When you need external per-instance state and:

- instances have no `__dict__`, or
    
- you don't want to pollute the instance dictionary.
    

The trade-offs include:

- extra indirection
    
- weak-reference requirements
    
- hashability requirements
    

---

## 28. Why doesn't `c.__len__ = f` make `len(c)` work?

Because implicit special-method lookup bypasses ordinary instance attribute lookup.

CPython uses special lookup machinery and type slots such as:

```text
tp_len
```

Therefore:

```python
c.__len__()
```

and:

```python
len(c)
```

are not equivalent lookup operations.

---

## 29. `__getattr__` vs `__getattribute__`?

```text
__getattribute__
    ↓
every attribute access
```

while:

```text
__getattr__
    ↓
fallback after AttributeError
```

Use `__getattribute__` carefully because it can easily recurse.

---

## 30. Why does `self.x` inside property `x` recurse?

Because:

```python
self.x
```

starts another attribute lookup.

That lookup finds:

```python
x property
```

which calls the getter again.

So:

```text
x getter
 ↓
self.x
 ↓
x getter
 ↓
self.x
 ↓
...
```

Use:

```python
self._x
```

for backing storage.

---

## 31. What is the performance cost of a property?

A Python-level property normally introduces descriptor dispatch and a Python-level getter call.

Therefore it can be more expensive than direct instance storage.

However, modern CPython has specialization and inline caching, so exact performance depends on:

- Python version
    
- access pattern
    
- descriptor type
    
- hotness of the code
    
- interpreter specialization
    

Do not use a fixed "property is exactly X times slower" rule without benchmarking the actual workload.

---

## 32. How does CPython reduce attribute-access overhead?

Modern CPython uses an adaptive interpreter and specialized attribute-access paths.

Examples include specialized forms such as:

```text
LOAD_ATTR_INSTANCE_VALUE
LOAD_ATTR_SLOT
LOAD_ATTR_PROPERTY
```

These allow repeated attribute access to use optimized paths when runtime assumptions remain valid.

---

## 33. What can invalidate specialization assumptions?

Mutating the relevant class/type can invalidate assumptions used by inline caches.

For example:

```python
C.x = something
```

can affect optimized attribute access involving `C`.

The exact cache invalidation mechanism is an implementation detail of CPython and can evolve between releases.

---

## 34. When are descriptors the right abstraction?

Use descriptors when the **same attribute behavior is needed repeatedly**.

Good examples:

```text
validation
coercion
ORM fields
lazy loading
change tracking
computed attributes
access control
unit conversion
cache management
```

If it is just one simple attribute:

```python
@property
```

is usually clearer.

If the problem is only memory-efficient fixed storage:

```python
__slots__
```

may be better.

---

# Part XVI — The 80/20 You Should Actually Remember

If you don't want to memorize the entire implementation, remember these **seven facts**.

### 1. Attribute access is a protocol

```python
obj.x
```

is not simply:

```python
obj.__dict__["x"]
```

---

### 2. A descriptor must be found on the type/MRO

```text
instance dictionary → ordinary object
class/MRO → descriptor machinery can activate
```

---

### 3. Data descriptors beat instance dictionaries

```text
data descriptor
      >
obj.__dict__
```

---

### 4. Non-data descriptors lose to instance dictionaries

```text
obj.__dict__
      >
non-data descriptor
```

This explains:

```text
methods
cached_property
classmethod
staticmethod
```

---

### 5. Functions are descriptors

This explains:

```python
C.method
```

versus:

```python
c.method
```

and ultimately explains where method binding comes from.

---

### 6. Descriptor behavior lives on the class; instance state normally lives on the instance

```text
class
 ↓
descriptor = behavior

instance
 ↓
__dict__ / slots = state
```

---

### 7. `__slots__`, `property`, methods, `super`, ORM fields, and cached attributes are all connected by descriptor machinery

Once you understand descriptors, a large part of Python's object model stops looking like unrelated magic.

---

# Final Mental Model

When you see:

```python
obj.x
```

ask these questions in this order:

```text
1. What is type(obj)?

2. Search its MRO.

3. Did we find x?

4. Is x a DATA descriptor?
       │
       ├── YES → call __get__
       │
       └── NO

5. Does obj.__dict__ contain x?
       │
       ├── YES → return it
       │
       └── NO

6. Is the class attribute a NON-DATA descriptor?
       │
       ├── YES → call __get__
       │
       └── NO → return ordinary class value

7. If lookup raises AttributeError:
       call __getattr__ if available
```

For assignment:

```python
obj.x = value
```

think:

```text
Search MRO
    ↓
Does x have __set__?
    │
 ┌──┴──┐
YES    NO
 │      │
 ▼      ▼
__set__ obj.__dict__["x"] = value
```

And for class access:

```python
C.x
```

remember:

```text
C is itself an object
       ↓
its type is the metaclass
       ↓
metaclass lookup participates
       ↓
class MRO is searched
       ↓
descriptor receives obj=None
```

That is the core of Python descriptors.

Once this lookup model is solid, **`property`, bound methods, `classmethod`, `staticmethod`, `__slots__`, `cached_property`, `super()`, ORM fields, metaclass properties, and many framework abstractions become variations of the same underlying mechanism rather than separate pieces of Python magic.**