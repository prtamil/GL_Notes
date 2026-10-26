
**Python does not define an official fixed list of “types of decorators.”** A decorator is simply an object/callable used in decorator syntax that receives the decorated object and returns a replacement (or the same object). The standard syntax supports functions, methods, and classes. ([Python Enhancement Proposals (PEPs)](https://peps.python.org/pep-0318/?utm_source=chatgpt.com "PEP 318 – Decorators for Functions and Methods | peps.python.org"))

For your learning, though, I would classify modern Python 3.10+ decorators into **5 practical categories**:

| #   | Type                               | What it decorates | Typical shape                           |
| --- | ---------------------------------- | ----------------- | --------------------------------------- |
| 1   | **Function decorator**             | Function/method   | `decorator(func) → wrapper`             |
| 2   | **Decorator factory**              | Function/method   | `factory(config) → decorator → wrapper` |
| 3   | **Class decorator**                | Class             | `decorator(cls) → cls/new class`        |
| 4   | **Callable/class-based decorator** | Function/method   | `Decorator.__call__(func) → wrapper`    |
| 5   | **Class decorator factory**        | Class             | `factory(config) → decorator(cls)`      |

But there is an important distinction in your **#3/#4 confusion**.

---
## 0. How @ Expands
```py
@testdeco              → testdeco(fname)

@testdeco("test")      → testdeco("test")(fname)

@testdeco("A")("B")    → testdeco("A")("B")(fname)

@A
@B                     → A(B(fname))
```

## 1. Function decorator

The basic one you already understand:

```python
def log(func):
    def wrapper(*args, **kwargs):
        print("before")
        return func(*args, **kwargs)

    return wrapper
```

```python
@log
def hello():
    pass
```

Mental model:

```text
hello = log(hello)
```

---

## 2. Decorator factory

A decorator **with configuration**:

```python
def log(level):
    def decorator(func):
        def wrapper(*args, **kwargs):
            print(level)
            return func(*args, **kwargs)

        return wrapper

    return decorator
```

```python
@log("DEBUG")
def hello():
    pass
```

Mental model:

```text
hello = log("DEBUG")(hello)
```

This is **not a separate kind of decorator mechanism** in Python. It's a pattern where one function creates a decorator. Python's decorator syntax explicitly supports this form. ([Python Enhancement Proposals (PEPs)](https://peps.python.org/pep-0318/?utm_source=chatgpt.com "PEP 318 – Decorators for Functions and Methods | peps.python.org"))

---

# 3. Class decorator

This is what you were remembering.

A decorator can receive a **class** instead of a function:

```python
def register(cls):
    print("registering", cls.__name__)
    return cls
```

```python
@register
class User:
    pass
```

Equivalent to:

```python
User = register(User)
```

Notice:

```text
function decorator:

decorator(function)


class decorator:

decorator(class)
```

A class decorator can:

- modify the class
    
- add attributes
    
- register it somewhere
    
- return the same class
    
- return a completely different class
    

Class decorators have been part of Python since 2.6. ([Python documentation](https://docs.python.org/3.10/contents.html?utm_source=chatgpt.com "Python Documentation contents — Python 3.10.20 documentation"))

---

# 4. Class-based decorator

**This is probably the second thing you were remembering.**

Here the **decorator itself is an object created from a class**:

```python
class Log:
    def __init__(self, func):
        self.func = func

    def __call__(self, *args, **kwargs):
        print("before")
        return self.func(*args, **kwargs)
```

Usage:

```python
@Log
def hello():
    pass
```

Python does:

```python
hello = Log(hello)
```

Now `hello` is actually a **Log object**.

When you do:

```python
hello()
```

Python calls:

```python
Log.__call__(...)
```

So:

```text
@Log
   ↓
Log(original_function)
   ↓
Log object
   ↓
hello()
   ↓
__call__()
```

This is **not a class decorator**.

It is a **class-based decorator**.

That's the distinction you were thinking of.

---

# 5. Class decorator factory

You can combine the factory idea with a class decorator:

```python
def register(name):
    def decorator(cls):
        cls.name = name
        return cls

    return decorator
```

Usage:

```python
@register("User")
class User:
    pass
```

Expansion:

```python
User = register("User")(User)
```

So:



---

# The clean mental map

For your Python learning, I would remember it like this:

```text
                    DECORATORS
                        │
          ┌─────────────┴─────────────┐
          │                           │
       FUNCTION                    CLASS
          │                           │
          │                           │
     ┌────┴────┐                 class decorator
     │         │
  normal     factory
     │
     │
  function
  decorator


And the decorator itself can be:

     FUNCTION
        │
        └── function decorator

     CLASS
        │
        ├── class decorator
        │
        └── class-based decorator
             (implements __call__)
```

But don't treat these as five official Python language categories.

### For your learning roadmap, I'd use these **4 core concepts**:

1. **Function decorator**
    
2. **Decorator factory**
    
3. **Class decorator**
    
4. **Class-based decorator (`__call__`)**
    

And then understand that **#2 and factory variations can also be applied to classes**.

One more useful point: the standard library itself has many specialized decorators—`@classmethod`, `@staticmethod`, `@property`, `@functools.cache`, `@singledispatch`, etc.—but these are **applications of the decorator mechanism**, not additional fundamental decorator types. ([Python documentation](https://docs.python.org/3.10/library/functools.html?utm_source=chatgpt.com "functools — Higher-order functions and operations on callable objects — Python 3.10.20 documentation"))

So for your senior-level Python internals study, **4 concepts are enough**.