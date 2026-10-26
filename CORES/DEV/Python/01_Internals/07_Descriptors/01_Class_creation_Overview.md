Absolutely. The missing layer in the previous version is the **basic object model**: before understanding descriptors, MRO, caches, and C slots, you should first know **what a class member is, what an instance member is, what a method is, and where each one is stored**.

Here is the same essay rebuilt from that foundation, with duplicates removed and the wording made more direct while keeping the CPython technical depth.

# Python Class Internals — Class Creation, Members, Storage & Attribute Access

> **Mental model first:** A Python class is an object that describes how its instances behave.  
> Class members live with the **class object**. Instance members belong to each **instance**. Methods are normally **function objects stored on the class**, which become bound methods when accessed through an instance.

---

# 1. The basic picture

Start with:

```python
class User:
    species = "human"          # class member

    def __init__(self, name):
        self.name = name        # instance member

    def hello(self):            # method
        return f"Hi {self.name}"
```

Then:

```python
u1 = User("Alice")
u2 = User("Bob")
```

Think:

```text
                         User
                    ┌──────────────┐
                    │ class object │
                    │              │
                    │ species ─────┼──► "human"
                    │ __init__ ────┼──► function
                    │ hello ───────┼──► function
                    └──────┬───────┘
                           │
                    describes instances
                 ┌─────────┴─────────┐
                 ▼                   ▼
              u1 instance         u2 instance
              ┌──────────┐        ┌──────────┐
              │ name ────┼──►Alice│ name ────┼──►Bob
              └──────────┘        └──────────┘
```

There is **one `species`**, shared through the class.

There are **two `name` values**, one per instance.

The important distinction is:

|Python concept|Where it normally lives|Example|
|---|---|---|
|Class member|class namespace|`User.species`|
|Instance member|instance state|`u1.name`|
|Method|class namespace as function object|`User.hello`|
|Bound method|temporary result of `u1.hello`|`u1.hello`|
|Static method|class namespace as descriptor|`User.utility`|
|Class method|class namespace as descriptor|`User.create`|

---

# 2. There is no separate "member memory"

Python programmers often talk about:

> class memory, instance memory, method memory

That is useful conversationally, but internally the important objects are:

```text
class object
instance object
function/descriptor objects
```

The class and instances are separate objects.

For:

```python
class User:
    species = "human"
```

the string `"human"` is referenced from the class namespace.

For:

```python
u.name = "Alice"
```

the value `"Alice"` is referenced from the instance's state.

So:

```text
CLASS STATE
    │
    └── User.__dict__
            │
            ├── species
            └── hello

INSTANCE STATE
    │
    ├── u1
    │     └── name
    │
    └── u2
          └── name
```

---

# 3. Class members

A class member is an attribute stored in the class namespace.

```python
class User:
    species = "human"
    count = 0
```

Conceptually:

```text
User
 │
 └── class namespace
       ├── species → "human"
       └── count   → 0
```

Therefore:

```python
User.species
```

works.

And:

```python
u = User()
u.species
```

also works.

Why?

Because when `u.species` is requested, Python can find `species` on `User` if it isn't found in the instance state.

So class members can be **accessed through instances**, but they are not thereby copied into each instance.

---

# 4. Instance members

Instance members are created by assigning attributes to an instance:

```python
class User:
    def __init__(self, name):
        self.name = name
```

When:

```python
u = User("Alice")
```

executes:

```python
self.name = name
```

Python stores `name` in the instance's state.

Conceptually:

```text
u
└── instance state
      └── name → "Alice"
```

If another instance is created:

```python
v = User("Bob")
```

then:

```text
u → name → "Alice"

v → name → "Bob"
```

They have independent instance state.

---

# 5. Static members: an important terminology point

Python does **not** have C++/Java-style "static data members" as a separate storage category.

If you write:

```python
class Config:
    timeout = 30
```

`timeout` is simply a **class attribute**.

It lives in the class namespace.

You can use:

```python
Config.timeout
```

and potentially:

```python
c = Config()
c.timeout
```

through normal attribute lookup.

Python's `@staticmethod` is something different.

---

# 6. Static method

Consider:

```python
class Math:
    @staticmethod
    def add(a, b):
        return a + b
```

The function is stored in the class namespace wrapped by a `staticmethod` descriptor.

Conceptually:

```text
Math
 │
 └── __dict__
       └── add → staticmethod object
                        │
                        └── function
```

When:

```python
Math.add(2, 3)
```

is accessed, the `staticmethod` descriptor returns the underlying function **without binding an instance or class**.

Therefore:

```python
Math.add(2, 3)
```

does not automatically receive:

```text
self
```

or:

```text
cls
```

---

# 7. Class method

Now:

```python
class User:
    @classmethod
    def create(cls, name):
        return cls(name)
```

The class dictionary contains a `classmethod` descriptor.

Conceptually:

```text
User
 │
 └── create
       │
       ▼
classmethod descriptor
       │
       ▼
function
```

When accessed through the class:

```python
User.create("Alice")
```

the descriptor binds:

```text
cls → User
```

So conceptually:

```python
User.create("Alice")
```

becomes:

```python
function(User, "Alice")
```

The important distinction:

```text
instance method
    → binds self

classmethod
    → binds cls

staticmethod
    → binds nothing
```

All three are fundamentally connected to **descriptor binding**.

---

# 8. Method vs function

This distinction is extremely important.

Inside:

```python
class User:
    def hello(self):
        ...
```

the class initially receives a **function object**:

```python
User.__dict__["hello"]
```

It is not permanently a "bound method."

When you access:

```python
User.hello
```

you get the function.

When you access:

```python
u.hello
```

the function's descriptor behavior binds `u` as `self`.

So:

```text
class namespace
       │
       ▼
function object
       │
       │ __get__(u, User)
       ▼
bound method
       │
       ├── function
       └── self = u
```

Therefore:

> **A method is not stored separately inside every instance.**

The function is stored once on the class.

---

# 9. Now: how does `class User:` actually create the class?

Consider:

```python
class User:
    species = "human"

    def hello(self):
        return "hello"
```

The class statement executes a class-construction process.

Simplified:

```text
class User
     │
     ▼
choose metaclass
     │
     ▼
metaclass.__prepare__()
     │
     ▼
create class namespace
     │
     ▼
execute class body
     │
     ▼
namespace contains:
     │
     ├── species
     └── hello
     │
     ▼
metaclass(name, bases, namespace)
     │
     ▼
type.__new__()
     │
     ▼
User class object
```

For an ordinary class, the metaclass is:

```python
type
```

---

# 10. The class body is executable code

This:

```python
class User:
    x = 10

    def hello(self):
        pass
```

is compiled into a **class-body code object**.

When executed, assignments populate the class namespace.

Conceptually:

```text
namespace
{
    "__module__": ...
    "__qualname__": "User"
    "x": 10
    "hello": <function>
}
```

This namespace is then given to the metaclass to construct the actual class object.

So the class body doesn't directly allocate the final `User` object.

It first **builds the namespace used to create it**.

---

# 11. `__prepare__`

Before executing the class body, Python asks the metaclass for the namespace:

```python
metaclass.__prepare__(name, bases, **kwargs)
```

For normal classes:

```python
type.__prepare__()
```

provides the namespace mapping.

Then Python executes the class body using that mapping.

This mechanism allows metaclasses/frameworks to customize class construction.

So:

```text
class body
    │
    ▼
namespace mapping
    │
    ▼
metaclass
    │
    ▼
class object
```

---

# 12. A class is itself an object

After construction:

```python
class User:
    pass
```

`User` is not some special entity outside the object system.

It is an object.

```python
type(User)
```

gives:

```python
<class 'type'>
```

Therefore:

```text
u
│
└── instance of User

User
│
└── instance of type
```

At the CPython level, the class object is represented by a structure based on:

```c
PyTypeObject
```

---

# 13. `PyObject`: the beginning of every object

CPython objects begin with a common header:

```c
typedef struct _object {
    Py_ssize_t ob_refcnt;
    PyTypeObject *ob_type;
} PyObject;
```

On a typical 64-bit build:

```text
┌────────────────────┐
│ ob_refcnt   8 bytes│
├────────────────────┤
│ ob_type     8 bytes│
└────────────────────┘
        16 bytes
```

So an instance contains at least:

```text
instance
├── reference count
└── pointer to its type
```

For:

```python
u = User()
```

conceptually:

```text
u
 │
 ├── ob_refcnt
 │
 └── ob_type ─────────► User
```

And:

```text
User
 │
 └── ob_type ─────────► type
```

This is the foundation of Python's object model.

---

# 14. What is inside a class object?

A class object is represented by `PyTypeObject`, which contains much more than the class namespace.

Important pieces include:

```text
PyTypeObject
│
├── tp_dict
│      class namespace
│
├── tp_mro
│      MRO
│
├── tp_bases
│      base classes
│
├── tp_basicsize
│      instance layout size
│
├── tp_dictoffset
│      instance dictionary information
│
├── tp_weaklistoffset
│      weak-reference information
│
├── tp_getattro
│      attribute lookup
│
├── tp_setattro
│      attribute assignment
│
├── tp_as_number
│      numeric protocols
│
├── tp_as_sequence
│      sequence protocols
│
├── tp_as_mapping
│      mapping protocols
│
└── version/cache information
```

This is the runtime description of the type.

---

# 15. `tp_dict`: where class members live

For:

```python
class User:
    species = "human"

    def hello(self):
        pass
```

the class namespace is exposed through:

```python
User.__dict__
```

Conceptually:

```text
User.tp_dict
│
├── "__module__"
├── "__qualname__"
├── "species" → "human"
└── "hello"   → function object
```

This is where ordinary class attributes, methods, descriptors, etc. are registered.

---

# 16. Instance storage

Now create:

```python
u = User()
```

The instance has:

```text
PyObject header
      +
instance-specific state
```

For a normal Python class, modern CPython uses optimized instance attribute storage involving **key-sharing dictionaries**.

The useful mental model is:

```text
class layout / shared keys
        │
        ├── name
        ├── age
        └── address
             │
      ┌──────┴──────┐
      ▼             ▼
     u1             u2
   values          values
   Alice            Bob
    46              30
```

The attribute names/layout metadata can be shared, while the actual values are specific to each instance.

This is the idea behind **PEP 412 key-sharing dictionaries**.

---

# 17. `__dict__` is the Python-level view

You can write:

```python
u.__dict__
```

and get:

```python
{
    "name": "Alice",
    "age": 46
}
```

That is the Python semantic model.

But don't assume the physical memory is simply:

```text
instance
└── complete PyDictObject
```

for every normal instance.

Modern CPython has optimized representations for instance attributes.

The important distinction is:

```text
Python guarantees:
    obj.__dict__ behaves like a dictionary

CPython is free to implement:
    that storage efficiently
```

---

# 18. `__slots__`: fixed instance storage

With:

```python
class Point:
    __slots__ = ("x", "y")
```

CPython can create a fixed layout.

Conceptually:

```text
Point instance

┌────────────────────┐
│ ob_refcnt          │
├────────────────────┤
│ ob_type            │
├────────────────────┤
│ x pointer          │
├────────────────────┤
│ y pointer          │
└────────────────────┘
```

The class dictionary receives descriptors for the slots:

```python
Point.__dict__["x"]
```

is a `member_descriptor`.

The descriptor knows the slot's offset.

Therefore:

```python
p.x
```

can access the known storage location directly rather than performing a normal dictionary lookup.

---

# 19. Now everything leads to `obj.x`

Suppose:

```python
class User:
    species = "human"

    def __init__(self):
        self.name = "Alice"

    def hello(self):
        return "hello"
```

and:

```python
u = User()
```

What happens with:

```python
u.name
```

?

Conceptually:

```text
u.name
  │
  ▼
attribute lookup
  │
  ▼
search User/MRO for "name"
  │
  ▼
descriptor?
  │
  ├── data descriptor → use descriptor
  │
  └── otherwise
        │
        ▼
   instance state
        │
        ├── found → return value
        │
        └── not found
              │
              ▼
        class attribute
              │
              ▼
        descriptor?
              │
              ▼
          __get__()
```

---

# 20. The four important lookup levels

The semantic lookup order is:

```text
1. DATA DESCRIPTOR
        ↓
2. INSTANCE STATE
        ↓
3. NON-DATA DESCRIPTOR
        ↓
4. CLASS ATTRIBUTE
        ↓
5. __getattr__ fallback
```

This is the core of Python attribute access.

---

# 21. Data descriptor

A descriptor implementing:

```python
__get__
```

and either:

```python
__set__
```

or:

```python
__delete__
```

is a **data descriptor**.

Example:

```python
class D:
    def __get__(self, obj, typ=None):
        return "descriptor"

    def __set__(self, obj, value):
        pass
```

If:

```python
class User:
    x = D()
```

then even:

```python
u.__dict__["x"] = "instance"
```

doesn't win.

```python
u.x
```

uses the data descriptor.

---

# 22. Non-data descriptor

A descriptor implementing only:

```python
__get__
```

is a **non-data descriptor**.

Python functions are non-data descriptors.

This gives the important rule:

```text
data descriptor
      >
instance state
      >
non-data descriptor
      >
class attribute
```

This one rule explains much of Python's apparently magical attribute behavior.

---

# 23. Why normal methods work

For:

```python
class User:
    def hello(self):
        return "hello"
```

the class dictionary contains:

```text
hello → function object
```

The function implements descriptor behavior.

Therefore:

```python
User.hello
```

returns the function.

But:

```python
u.hello
```

causes binding:

```text
function.__get__(u, User)
          │
          ▼
      bound method
          │
          ├── function
          └── self = u
```

So:

```python
u.hello()
```

effectively invokes:

```python
User.hello(u)
```

`self` is therefore a consequence of **descriptor binding**, not a special hidden parameter inserted by the class system.

---

# 24. `property` is the same machinery

When you write:

```python
class User:
    @property
    def name(self):
        return "Alice"
```

the class contains a `property` object.

```text
User.__dict__
     │
     └── name → property
                  │
                  ▼
              __get__()
                  │
                  ▼
              getter(self)
```

So:

```python
u.name
```

executes descriptor logic rather than simply retrieving a dictionary entry.

This is why descriptors are such a central part of Python.

---

# 25. Attribute assignment

For:

```python
u.x = 10
```

the simplified logic is:

```text
u.x = 10
   │
   ▼
Is x a data descriptor?
   │
   ├── yes → descriptor.__set__()
   │
   └── no
        │
        ▼
   store in instance state
```

Notice:

```python
u.x = 10
```

does **not** modify:

```python
User.__dict__
```

Whereas:

```python
User.x = 10
```

modifies the class.

---

# 26. MRO decides where the class lookup searches

If:

```python
class A:
    x = 10

class B(A):
    pass

class C(B):
    pass
```

then:

```python
C.__mro__
```

is conceptually:

```text
C
B
A
object
```

When looking for an attribute on the class hierarchy, Python searches this MRO.

With multiple inheritance, CPython uses **C3 linearization** to construct the MRO.

---

# 27. `super()` continues the MRO

`super()` does not simply mean:

```text
"my parent"
```

It means roughly:

> Continue attribute lookup from a particular position in the MRO.

For:

```python
class B(A):
    def hello(self):
        super().hello()
```

the `super()` proxy continues searching after `B`.

This is what makes cooperative multiple inheritance possible.

---

# 28. Special methods use type slots

There is another important path.

Consider:

```python
class X:
    def __len__(self):
        return 10
```

This:

```python
x.__len__()
```

is ordinary attribute lookup.

But:

```python
len(x)
```

doesn't simply perform:

```python
x.__len__()
```

Instead, CPython uses the type's protocol slots.

Conceptually:

```text
len(x)
  │
  ▼
type(x)
  │
  ▼
sequence protocol
  │
  ▼
sq_length
  │
  ▼
implementation
```

Similar machinery exists for:

```text
+
-
*
[]
()
iter()
next()
hash()
bool()
```

and other protocols.

---

# 29. Why instance-level dunder replacement doesn't affect operators

```python
class X:
    def __len__(self):
        return 10

x = X()

x.__len__ = lambda: 99
```

Now:

```python
x.__len__()
```

can produce:

```text
99
```

but:

```python
len(x)
```

still uses the type-level special-method machinery.

This is intentional.

```text
ordinary attribute access
        ↓
instance/class lookup

special operation
        ↓
type protocol slot
```

---

# 30. How Python dunders reach C slots

At class creation/update, CPython examines special methods and connects them to appropriate C-level slots.

Conceptually:

```text
X.__dict__["__len__"]
        │
        ▼
Python function
        │
        ▼
type slot
sq_length
        │
        ▼
C trampoline/wrapper
        │
        ▼
Python implementation
```

CPython's `update_one_slot()` machinery is involved in maintaining this connection.

This is why changing a special method on the **class** can affect:

```python
len(x)
```

while changing it only on the **instance** does not.

---

# 31. The final performance layer: 3.11+

The generic attribute algorithm looks expensive:

```text
find type
   ↓
search MRO
   ↓
inspect descriptor
   ↓
inspect instance state
   ↓
return value
```

Modern CPython avoids doing all of that from scratch every time.

Python 3.11 introduced the **specializing adaptive interpreter**.

`LOAD_ATTR` can specialize after observing repeated execution.

Conceptually:

```text
generic LOAD_ATTR
       │
       ▼
observe types/layouts
       │
       ▼
specialize
       │
       ▼
cached fast path
```

For stable objects, CPython can cache information such as:

```text
type version
keys/layout version
attribute location
descriptor/function
```

Then a repeated access can become approximately:

```text
check guard
   │
   ├── valid → fast access
   │
   └── invalid → generic lookup
```

---

# 32. Why version tags exist

Suppose CPython cached:

```python
User.x
```

Then:

```python
User.x = 100
```

changes the class.

The old cache might now be wrong.

CPython therefore maintains versioning/invalidation machinery associated with types and cached lookups.

Conceptually:

```text
cache:
    type version = 123
```

If the type changes:

```text
version changes / cache invalidated
```

The next lookup resolves the new state and can specialize again.

This is the basic pattern:

```text
CACHE
  │
  ├── guard still valid → fast path
  │
  └── changed → generic path → update cache
```

---

# 33. The complete mental model

Start from the simple Python view:

```text
                     CLASS
                       │
             ┌─────────┴─────────┐
             │                   │
       class members          methods
             │                   │
             ▼                   ▼
       class namespace       functions
             │                   │
             └─────────┬─────────┘
                       │
                       ▼
                 class object
                  PyTypeObject
                       │
                 creates/describes
                       │
            ┌──────────┴──────────┐
            ▼                     ▼
        instance 1             instance 2
            │                     │
       instance state       instance state
            │                     │
        name="A"              name="B"
```

Then attribute access:

```text
                         obj.x
                           │
                           ▼
                    class / MRO lookup
                           │
                           ▼
                  ┌─────────────────┐
                  │ data descriptor?│
                  └────────┬────────┘
                           │
                    yes ───┴─── no
                    │            │
                    ▼            ▼
                __get__     instance state
                                 │
                          found ──┴── yes
                                 │
                                 ▼
                              return
                                 │
                               no
                                 ▼
                         class attribute
                                 │
                         descriptor?
                                 │
                           yes ──┴── no
                           │          │
                           ▼          ▼
                        __get__    return value
```

---

# 34. Where each Python feature fits

Now the various features you are learning become much easier to place:

```text
                    PYTHON CLASS
                         │
          ┌──────────────┼──────────────┐
          │              │              │
          ▼              ▼              ▼
    Class members   Instance members   Methods
          │              │              │
      class dict      instance state   function
                                         │
                                         ▼
                                    descriptor
                                         │
                              ┌──────────┼──────────┐
                              │          │          │
                              ▼          ▼          ▼
                         instance     class      static
                          method      method     method
                              │          │          │
                             self       cls       nothing


                         ATTRIBUTE SYSTEM
                                │
                  ┌─────────────┼─────────────┐
                  ▼             ▼             ▼
             descriptors      MRO       instance state
                  │
          ┌───────┴────────┐
          ▼                ▼
     data descriptor   non-data descriptor
          │                │
       property        function/method
       slots           classmethod
                       staticmethod
```

---

# 35. The senior-level summary

A Python class has two distinct responsibilities:

1. **It is an object itself.**
    
2. **It describes/controls the behavior and layout of its instances.**
    

When:

```python
class User:
    species = "human"

    def hello(self):
        ...
```

executes, Python builds a class namespace containing objects such as:

```text
species → value
hello   → function
```

The metaclass, normally `type`, uses that namespace to construct a `PyTypeObject`.

The class object contains:

```text
class namespace
MRO
base classes
instance-layout information
C protocol slots
attribute access machinery
version/cache information
```

When:

```python
u = User()
```

runs, CPython creates an instance whose `PyObject` header points to `User`, plus storage for instance-specific state.

So the fundamental storage model is:

```text
CLASS
 └── class namespace
       ├── class attributes
       ├── functions
       ├── descriptors
       └── other class-level objects

INSTANCE
 └── instance state
       ├── attribute values
       └── possibly fixed __slots__ storage
```

A method is normally **not stored in the instance**:

```text
User.__dict__["hello"]
        │
        ▼
    function
        │
        │ __get__(u, User)
        ▼
   bound method
        │
        └── self = u
```

And `@staticmethod` / `@classmethod` are descriptor-based variations:

```text
normal method  → binds self
classmethod    → binds cls
staticmethod   → binds nothing
```

For:

```python
obj.x
```

the fundamental attribute precedence is:

```text
1. data descriptor
2. instance state
3. non-data descriptor
4. class attribute
5. __getattr__
```

For:

```python
obj.x = value
```

the important path is:

```text
1. data descriptor.__set__()
2. instance state
```

Special methods such as:

```python
len(obj)
obj + other
obj[key]
```

use **type-level C protocol slots**, not ordinary instance attribute lookup.

Finally, CPython 3.11+ adds **adaptive specialization and inline caches** on top of these mechanisms so that stable attribute accesses can bypass much of the generic lookup process.

---

## The one mental model to keep

```text
             class statement
                    │
                    ▼
             execute class body
                    │
                    ▼
              class namespace
                    │
                    ▼
            metaclass / type
                    │
                    ▼
             PyTypeObject
                    │
        ┌───────────┼────────────┐
        │           │            │
        ▼           ▼            ▼
    class dict     MRO       type slots
        │
        ├── class attributes
        ├── functions
        └── descriptors
                    │
                    ▼
              creates instances
                    │
              ┌─────┴─────┐
              ▼           ▼
             obj1        obj2
              │           │
        instance state  instance state
              │           │
              └─────┬─────┘
                    │
                    ▼
                 obj.x
                    │
                    ▼
          descriptor → instance
             → descriptor → class
                    │
                    ▼
             optimized by
          inline caches / specialization
```

**That is the foundation.** Once this is clear, descriptors, `property`, `classmethod`, `staticmethod`, `__slots__`, MRO, metaclasses, special methods, and `LOAD_ATTR` stop looking like separate Python features. They become different pieces of the **same object/class/attribute machinery**.