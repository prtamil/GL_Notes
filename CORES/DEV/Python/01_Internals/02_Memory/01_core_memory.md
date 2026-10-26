
## Python Memory Management — Fast Technical Revision

# Python Memory Management — Technical Essay

CPython manages memory through **multiple allocator layers**. The key idea is that Python obtains virtual memory from the OS and then manages much of that memory through its own **private heap**, rather than asking the OS for every Python object.

```text
Python objects
      ↓
Object-specific allocators
      ↓
Python object allocator
      ↓
PyMem / raw memory allocator
      ↓
Underlying general-purpose allocator
      ↓
OS Virtual Memory Manager
      ↓
RAM / swap
```

### 1. Object Allocation

When CPython creates objects such as `int`, `dict`, `list`, or `str`, their memory ultimately comes through CPython's allocator infrastructure. Object allocation is optimized because Python creates **many small, frequently allocated objects**.

The traditional small-object allocator is **`pymalloc`**.

For small allocations, `pymalloc` manages memory using:

```text
Arena
  ↓
Pool
  ↓
Block
  ↓
Python object
```

An **arena** is a relatively large memory region obtained from the lower-level allocator. An arena is divided into **pools**, and pools manage blocks belonging to particular size classes. A **block** is the actual small piece of memory used for an allocation.

This organization allows freed blocks to be reused efficiently without repeatedly requesting memory from the OS.

### 2. CPython Allocator Domains

CPython exposes several conceptual allocation domains:

- **Raw allocator** — lowest-level Python memory interface; can obtain memory from the system allocator and does not require the GIL.
    
- **`PyMem` allocator** — manages Python memory buffers.
    
- **Object allocator** — optimized for Python object memory.
    
- **Object-specific allocators** — specialized allocation strategies used by particular Python subsystems/types.
    

The important principle is:

> Higher layers divide and manage memory obtained from lower layers.

### 3. Underlying System Allocator

Eventually memory must come from the process's virtual address space. The lowest general-purpose layer may use an allocator such as C's **`malloc()`**.

Conceptually:

```text
PyObject / PyMem
       ↓
Python allocator
       ↓
malloc-family allocator
       ↓
OS virtual memory
```

The underlying allocator obtains virtual memory using platform-specific mechanisms such as **`mmap()`** and, historically/on some systems, **`brk()` / `sbrk()`**. CPython's arena implementation can use platform mechanisms such as `mmap()` on Unix or `VirtualAlloc()` on Windows.

Thus, `sbrk()` is **not "Python's allocator"**; it is an OS-level mechanism that a lower-level allocator may use.

### 4. Object Destruction vs Memory Release

When reference counting reaches zero:

```text
refcount → 0
      ↓
tp_dealloc
      ↓
object resources released
      ↓
memory returned to its allocator
      ↓
memory can be reused
```

This does **not necessarily mean the memory immediately returns to the OS**.

For example, a freed small-object block can remain inside `pymalloc` and later be reused by another object.

Therefore:

```text
Object destroyed
        ≠
Memory returned to OS
```

### 5. Important Modern CPython Note

Modern CPython also supports **mimalloc**, a general-purpose allocator. It was added as an optional allocator and is particularly relevant to newer CPython implementations, including the free-threaded build. Therefore, avoid memorizing the oversimplified statement:

> "CPython always uses pymalloc all the way down."

The stable mental model is the **allocator layers and domains**, while the exact lower-level allocator can vary by CPython build and platform.

### Interview Chain

```text
Python object
   ↓
Object allocator
   ↓
small allocation?
   ↓
pymalloc
   ↓
arena → pool → block
   ↓
object memory

Lower layer:
PyMem / Raw
   ↓
general-purpose allocator
   ↓
malloc / mmap / platform mechanism
   ↓
OS virtual memory
   ↓
RAM / swap

Object dies:
refcount = 0
   ↓
tp_dealloc
   ↓
memory returned to allocator
   ↓
usually reused rather than immediately returned to OS
```

### One-sentence memory hook

**CPython gets virtual memory from the OS through lower-level allocators, manages much of it through Python's allocator domains, and uses `pymalloc`'s arena → pool → block organization for small-object allocation; when objects die, their memory normally becomes allocator-managed reusable memory rather than automatically going back to the OS.**