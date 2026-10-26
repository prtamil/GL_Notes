Great. Let's trace **one tiny class from class creation all the way to `u.hello()`**. This is the best way to make the object model concrete.

We will use only this:

```python
class User:
    species = "human"

    def hello(self):
        print("Hello")

u = User()
u.hello()
```

# 1. Before `class User` exists

There is no `User` class yet.

Python is about to execute the class statement:

```text
class User:
    ...
```

The first question is:

> **Which metaclass should create `User`?**

For a normal class:

```text
metaclass = type
```

So:

```text
type
 │
 │ will create
 ▼
User
```

---

# 2. `__prepare__()` creates the class namespace

Python asks the metaclass to prepare a namespace:

```text
type.__prepare__("User", ())
```

Conceptually we get:

```text
namespace
   │
   ├── __module__
   └── __qualname__
```

Think of this as a temporary dictionary where Python will execute the class body.

---

# 3. Python executes the class body

Now Python executes:

```python
species = "human"

def hello(self):
    print("Hello")
```

### First statement

```python
species = "human"
```

creates:

```text
namespace
   │
   └── species ─────► "human"
```

### Second statement

```python
def hello(self):
    print("Hello")
```

creates a **function object**.

Then Python stores it:

```text
namespace
   │
   ├── species ─────► "human"
   │
   └── hello ───────► function object
```

At this point:

> `hello` is a function object. It is **not yet a bound method**.

This distinction is extremely important.

---

# 4. The completed class namespace

Conceptually:

```text
namespace
│
├── "__module__"  ──► "__main__"
│
├── "__qualname__" ─► "User"
│
├── "species"     ──► "human"
│
└── "hello"       ──► function object
```

Now Python has all the information required to create the class.

It has:

```text
name      = "User"

bases     = ()

namespace = {...}
```

---

# 5. Give it to the metaclass

Python now invokes the metaclass.

Conceptually:

```python
type("User", (), namespace)
```

At a lower conceptual level:

```text
type.__call__()
```

is involved.

Simplified:

```text
type.__call__()
      │
      ├── type.__new__()
      │
      └── type.__init__()
```

---

# 6. `type.__new__()` creates `User`

This is the key moment.

`type.__new__()` creates the actual **class object**.

We now have:

```text
                    type
                     │
                     │ creates
                     ▼
                   User
```

And:

```python
type(User)
```

returns:

```text
<class 'type'>
```

So `User` is itself an object.

---

# 7. What does the new `User` object contain?

Conceptually:

```text
User  ← class object
│
├── class dictionary
│
├── base classes
│
├── MRO
│
└── other type metadata
```

Its class dictionary contains:

```text
User.__dict__
│
├── species ──► "human"
│
└── hello   ──► function object
```

So now we have:

```text
                     type
                      │
                      │ instance of
                      ▼
                    User
                      │
                      │ contains
                      ▼
                class dictionary
                   │       │
                   ▼       ▼
                species   hello
                   │       │
                   ▼       ▼
                "human"  function
```

---

# 8. Now execute `u = User()`

The class already exists.

Now:

```python
u = User()
```

is a **different process**.

We are no longer creating a class.

We are creating an **instance**.

The call:

```python
User()
```

goes through the class object's call machinery.

Conceptually:

```text
User()
  │
  ▼
User.__call__()
  │
  ├── User.__new__()
  │
  └── User.__init__()
  │
  ▼
u
```

The resulting object is:

```text
u
```

and:

```python
type(u)
```

is:

```text
User
```

So now:

```text
                  type
                    │
                    │ creates
                    ▼
                  User
                    │
                    │ creates
                    ▼
                    u
```

---

# 9. What does `u` contain?

Assume we haven't assigned any instance attributes.

Then:

```python
u.__dict__
```

is approximately:

```python
{}
```

So we have:

```text
User
│
├── class dictionary
│     │
│     ├── species ──► "human"
│     └── hello   ──► function
│
│
u
│
└── instance dictionary
      │
      └── {}
```

Notice:

> `species` is not copied into `u.__dict__`.

The instance accesses it through the class.

---

# 10. Now `u.hello`

This is where the **descriptor protocol** becomes important.

We write:

```python
u.hello
```

Python performs attribute lookup.

Conceptually, it searches the instance and its class.

It eventually finds:

```text
User.__dict__["hello"]
```

which is the function object.

But Python functions implement the **descriptor protocol**.

So Python effectively uses:

```python
function.__get__(u, User)
```

Conceptually:

```text
u.hello
   │
   ▼
attribute lookup
   │
   ▼
User.__dict__["hello"]
   │
   ▼
function descriptor
   │
   ▼
function.__get__(u, User)
   │
   ▼
bound method
```

---

# 11. What is the bound method?

The result of:

```python
u.hello
```

is conceptually a bound method containing:

```text
bound method
│
├── __self__ ──► u
│
└── __func__ ─► User.hello function
```

So:

```text
                 User
                  │
                  │ class dictionary
                  ▼
               hello
                  │
                  │ function
                  ▼
             function object
                  ▲
                  │
               __func__
                  │
            bound method
                  │
               __self__
                  │
                  ▼
                  u
```

This is why:

```python
u.hello()
```

automatically supplies `u` as `self`.

---

# 12. What actually happens during `u.hello()`?

Think of:

```python
u.hello()
```

as conceptually producing:

```python
bound_method = u.hello
bound_method()
```

The bound method already remembers:

```text
self = u
```

So the function:

```python
def hello(self):
    print("Hello")
```

effectively receives:

```text
self ──► u
```

Therefore:

```python
u.hello()
```

behaves conceptually like:

```python
User.hello(u)
```

The syntax is different, but the important binding relationship is the same.

---

# 13. Now compare `User.hello`

There is an important difference:

```python
User.hello
```

versus:

```python
u.hello
```

### `User.hello`

Attribute access through the class gives access to the function without an instance being supplied.

Conceptually:

```text
User.hello
    │
    ▼
function
```

### `u.hello`

Attribute access through an instance supplies the instance to the descriptor:

```text
u.hello
   │
   ▼
function.__get__(u, User)
   │
   ▼
bound method
```

This is the heart of Python method binding.

---

# 14. Where `self` actually comes from

This is a common interview question.

Python does **not** have a special `self` keyword.

`self` is simply the first parameter of the function:

```python
def hello(self):
```

The descriptor-based method binding supplies the instance as that argument.

Conceptually:

```text
u.hello()
   │
   ▼
bound method
   │
   └── self = u
```

So `self` is a normal parameter.

The special behavior comes from **method binding**, not from the name `self`.

This also means:

```python
def hello(x):
    print(x)
```

works:

```python
u.hello()
```

Here `x` receives the instance.

Python does not care that you called the parameter `x` instead of `self`.

---

# 15. Now add an instance attribute

Suppose:

```python
u.name = "Tamil"
```

Now:

```python
u.__dict__
```

contains:

```python
{
    "name": "Tamil"
}
```

So the object layout is conceptually:

```text
                     User
                      │
              class dictionary
                      │
             ┌────────┴────────┐
             │                 │
          species            hello
             │                 │
          "human"          function
                                │
                                │ descriptor
                                ▼
                           method binding


                     u
                     │
              instance dictionary
                     │
                     ▼
                  name
                     │
                  "Tamil"
```

The instance stores its own state.

The class stores shared class-level objects.

---

# 16. The complete picture

Put everything together:

```text
                         type
                          │
                          │ metaclass
                          │ creates
                          ▼
                    ┌─────────────┐
                    │    User     │
                    │ class object│
                    └──────┬──────┘
                           │
                    User.__dict__
                           │
              ┌────────────┴────────────┐
              │                         │
              ▼                         ▼
          species                    hello
              │                         │
              ▼                         ▼
          "human"                 function object
                                        │
                                   descriptor
                                        │
                                        │ __get__
                                        ▼
                              bound method
                                        │
                                        │ __self__
                                        ▼
                                        u
                                        │
                                instance dictionary
                                        │
                                        ▼
                                      name
                                        │
                                     "Tamil"
```

---

# 17. The entire lifecycle in one diagram

This is the diagram I recommend remembering:

```text
CLASS CREATION
───────────────

class User:
    ...
        │
        ▼
Choose metaclass
        │
        ▼
type.__prepare__()
        │
        ▼
class namespace
        │
        ▼
execute class body
        │
        ├── species → "human"
        │
        └── hello → function
        │
        ▼
type(...)
        │
        ▼
type.__call__()
        │
        ├── type.__new__()
        │       │
        │       ▼
        │     User class object
        │
        └── type.__init__()


INSTANCE CREATION
──────────────────

User()
  │
  ▼
User.__call__()
  │
  ├── User.__new__()
  │       │
  │       ▼
  │       u
  │
  └── User.__init__()


ATTRIBUTE ACCESS
────────────────

u.hello
   │
   ▼
attribute lookup
   │
   ▼
User.__dict__["hello"]
   │
   ▼
function descriptor
   │
   ▼
function.__get__(u, User)
   │
   ▼
bound method
   │
   ├── __self__ → u
   └── __func__ → hello
```

# 18. The four things to keep separate

If these four things are clear, most of Python's object model becomes much easier:

|Thing|Meaning|
|---|---|
|**Class namespace**|Names defined while executing the `class` body|
|**Class object**|The object created by the metaclass|
|**Instance namespace**|Per-instance state, commonly `u.__dict__`|
|**Descriptor**|Object that controls attribute access through `__get__`, `__set__`, etc.|

And the key chain is:

```text
class body
    ↓
class namespace
    ↓
metaclass
    ↓
class object
    ↓
class dictionary
    ↓
descriptor
    ↓
attribute lookup
    ↓
bound method
    ↓
instance
```

**This is the bridge between the topics you've been studying.** `classmethod`, `staticmethod`, `property`, normal methods, and custom descriptors all become much easier once this chain is clear.