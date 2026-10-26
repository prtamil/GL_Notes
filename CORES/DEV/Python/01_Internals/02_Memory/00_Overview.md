

# Python Memory Management — Overview

```text
Python code
   ↓
Names / references
   ↓
Python objects
   ↓
Reference counting
   ↓
refcount reaches 0?
   ├── YES → immediate deallocation
   │            ↓
   │       object cleanup
   │            ↓
   │       memory available to allocator
   │
   └── NO → object remains alive
              │
              └── possible reference cycle
                       ↓
                  Cyclic GC
                       ↓
                  unreachable?
                       ↓
                  deallocation
```

Then underneath object lifetime:

```text
Python object
     ↓
CPython object header
     ↓
ob_refcnt + type pointer
     ↓
Py_INCREF / Py_DECREF
     ↓
type-specific deallocation
     ↓
Python memory allocator
     ↓
pymalloc / arenas / pools / blocks
     ↓
OS memory
```

---

# The interview chain to memorize

The interviewer can walk you through this chain:

```text
1. a = []
       ↓
2. list object is created
       ↓
3. name 'a' references the object
       ↓
4. object has a reference count
       ↓
5. b = a
       ↓
6. same object, another reference
       ↓
7. del a
       ↓
8. only the name/reference is removed
       ↓
9. reference count decreases
       ↓
10. refcount == 0?
       ↓
11. CPython deallocates the object
       ↓
12. object resources are released
       ↓
13. memory becomes available to Python's allocator
       ↓
14. memory is not necessarily returned to OS
       ↓
15. BUT cycles can keep refcount > 0
       ↓
16. cyclic garbage collector detects unreachable cycles
       ↓
17. cycle is collected
```

That's the **story** you want in your head.

---

# Full technical terms

|Concept|Technical term|
|---|---|
|Python object representation|`PyObject`|
|Reference count|`ob_refcnt`|
|Object type information|`ob_type` / type pointer|
|Increase reference count|`Py_INCREF()`|
|Decrease reference count|`Py_DECREF()`|
|Reference count reaches zero|object deallocation|
|Type-specific cleanup|`tp_dealloc`|
|Cyclic garbage collector|cyclic GC|
|Python memory allocator|`pymalloc` and related allocators|
|Small-object allocator|`pymalloc`|
|Memory regions|arenas|
|Arena subdivisions|pools|
|Pool subdivisions|blocks|
|Operating-system memory|process virtual memory / OS allocator|

The most important distinction:

```text
Reference counting ≠ cyclic GC
Object deallocation ≠ returning memory to OS
del a ≠ destroying the object
```

---

# Short crisp technical essay

## Python Object Lifetime and Deallocation

In CPython, a Python variable is a **name/reference**, while the actual data exists as a **Python object** in memory. Every object contains a CPython object header that includes information such as its **reference count (`ob_refcnt`)** and type information.

When another reference to an object is created, CPython conceptually increments its reference count using **`Py_INCREF()`**. When a reference disappears, CPython decrements the count using **`Py_DECREF()`**.

For example:

```python
a = [1, 2, 3]
b = a
del a
```

`a` and `b` refer to the **same list object**. `del a` only removes the reference named `a`; it does not destroy the list. The reference count decreases, but `b` still keeps the object alive.

When the reference count reaches **zero**, CPython knows that the object can no longer be reached through reference counting, so it performs **object deallocation**. The object's type-specific `tp_dealloc` machinery releases the object's resources and eventually makes its memory available to Python's memory allocator.

Importantly, **deallocation does not necessarily mean returning memory to the operating system**. CPython's allocator can retain freed memory and reuse it for future Python objects. For small objects, this involves mechanisms such as **`pymalloc`, arenas, pools, and blocks**.

Reference counting has one major limitation: **reference cycles**. Two or more objects can reference each other while no external reference can reach them. Their reference counts therefore remain non-zero, so reference counting alone cannot free them. CPython's **cyclic garbage collector** detects such unreachable cycles and allows them to be collected.

### One-line interview answer

> **CPython primarily manages object lifetime through reference counting; when `ob_refcnt` reaches zero, the object's `tp_dealloc` machinery releases it, while the memory is typically returned to Python's allocator for reuse rather than necessarily to the OS. Cyclic GC handles unreachable reference cycles that reference counting alone cannot reclaim.**

That paragraph is the one I'd memorize. The longer chain gives you enough depth to expand when the interviewer starts drilling down.