😄 I actually had the same reaction during the interview.

I thought:

> "This person clearly has years of architecture experience. Let's see where the edges are."

Then the `dict` question immediately revealed one.

This is **exactly** why companies like Meta, Google, Microsoft, Amazon, OpenAI, Stripe, etc., ask these questions. They want to distinguish between:

- **Uses Python every day**
    
- **Understands why Python behaves the way it does**
    

---

# Here are the "shock questions" for Python

These are questions where **95% of experienced Python developers stumble**.

---

# Tier 1 (Must Know)

## 1. Dictionary Internals ⭐⭐⭐⭐⭐

I already shocked you 😄

Questions

- Why is dict O(1)?
    
- How is hash computed?
    
- Why are strings immutable?
    
- How are collisions handled?
    
- Why does Python resize dictionaries?
    
- What is load factor?
    
- Why are dictionaries ordered now?
    

---

## 2. Memory Management ⭐⭐⭐⭐⭐

This is a favorite.

Questions

```
What happens after

a = []

Explain every step.
```

Then

```
a=[1,2,3]
b=a
del a

Why does b still exist?
```

Then

```
What is reference counting?

Why is Python using it?
```

Then

```
What is cyclic garbage?

Why reference counting cannot free it?
```

---

## 3. GIL ⭐⭐⭐⭐⭐

Not just

"What is GIL?"

Interviewers ask

```
Why was GIL introduced?

Could Python remove it?

Why does Java not need GIL?

Why does Go not need GIL?

What changed in newer CPython versions?
```

---

## 4. List Internals ⭐⭐⭐⭐⭐

Questions

```
Why append() is O(1)?

How list grows?

Why insert(0,x) is O(n)?

Difference between

append

extend

+=
```

---

## 5. Tuple ⭐⭐⭐⭐

Questions

```
Why tuple faster?

Why tuple hashable?

Can tuple contain mutable objects?

Why tuple is preferred for dictionary key?
```

---

## 6. Set ⭐⭐⭐⭐

Questions

```
How set works?

Difference between

dict

set

Why lookup O(1)?
```

---

# Tier 2 (Interview Favorites)

---

## 7. Decorators

Questions

```
How decorator works internally?

Functions are objects?

Closure?

Wrapper?

functools.wraps?
```

---

## 8. Generators

One of my favorite.

Questions

```
yield vs return

How generator saves state?

Why memory efficient?

How next() works?

What is StopIteration?
```

---

## 9. Iterator Protocol

Interviewers LOVE this.

Questions

```
What makes object iterable?

Difference

Iterable

Iterator

Generator

Explain

__iter__()

__next__()
```

---

## 10. Context Manager

Questions

```
with open()

How does it work?

Explain

__enter__

__exit__

Why use context manager?
```

---

## 11. Asyncio

Questions

```
How event loop works?

Coroutine?

Future?

Task?

await?

Why asyncio faster for IO?
```

---

## 12. Multiprocessing

Questions

```
fork

spawn

pickle

IPC

shared memory

Queue

Pipe
```

---

# Tier 3 (Senior Engineer)

---

## 13. Object Model

Questions

```
Everything is object?

What is class?

How instance created?

__new__

__init__

Method Resolution Order

MRO

super()

Diamond inheritance
```

---

## 14. Descriptors ⭐⭐⭐⭐⭐

Almost nobody knows.

Questions

```
@property

staticmethod

classmethod

How implemented?

What is descriptor?
```

---

## 15. Metaclasses ⭐⭐⭐⭐⭐

Scary interview topic.

Questions

```
What is metaclass?

Why class is object?

Who creates class?

type()

When use metaclass?
```

---

## 16. Slots

Questions

```
Why __slots__ faster?

Memory reduction?

Tradeoffs?
```

---

## 17. Copy

Questions

```
copy()

deepcopy()

Assignment

Mutable

Immutable
```

---

## 18. Serialization

Questions

```
pickle

json

marshal

Protocol Buffers

Which one?
```

---

## 19. Import System

Questions

```
Why module executes only once?

What is sys.modules?

Circular imports?

PYTHONPATH?

Import cache?
```

---

## 20. CPython Memory

This is where Staff Engineers start shining.

Questions

```
PyObject

Reference Count

Memory Arena

Pools

Blocks

Small object allocator (pymalloc)

Why int objects reused?

Why string interning?
```

---

# Tier 4 (Very Hard)

These separate Staff Engineers.

---

### Explain this

```python
a=256
b=256

a is b
```

Why?

---

### Why

```python
257 is 257
```

may behave differently?

---

### Explain

```python
[] == []
```

vs

```python
[] is []
```

---

### Why

```python
def f(x=[]):
    x.append(1)
    return x
```

returns

```
[1]
[1,2]
[1,2,3]
```

---

### Explain

```python
lambda
```

internally.

---

### Explain

```python
@property
```

internally.

---

### Explain

```python
@classmethod
```

internally.

---

### Explain

```python
@staticmethod
```

internally.

---

### Explain

```python
type()
```

---

### Explain

```python
object
```

---

### Explain

```python
class Foo:
    pass
```

What actually happens?

---

# The "Python Internals Roadmap"

If I were preparing you specifically for **Senior Backend / Staff Engineer** interviews, I'd prioritize these topics in order:

1. **Memory management** (reference counting, garbage collection, object lifecycle)
    
2. **`dict`, `set`, and `list` internals**
    
3. **Object model** (`object`, `type`, classes, instances, MRO)
    
4. **Concurrency** (GIL, threading, multiprocessing, `asyncio`)
    
5. **Functions** (closures, decorators, generators, iterators)
    
6. **Descriptors and `property`**
    
7. **Imports and modules**
    
8. **CPython implementation details** (pymalloc, string interning, integer caching)
    

---

## Here's what I propose

I think we can make this fun.

I'll become a **Python Core Developer interviewer**.

Not "What is a list?"

Instead:

> **"When you write `a = [1, 2, 3]`, tell me everything CPython does—from parsing the code to creating the list object in memory and binding the name `a`."**

Or:

> **"Explain why `dict` lookups are O(1), and convince me they can become O(n). Then tell me how CPython minimizes that risk."**

We'll go layer by layer until you develop a solid mental model of how Python works under the hood. I think you'll enjoy it, because it's the same first-principles approach you've been using to understand watches and system architecture.