
# How the Linux Kernel Implements Atomics Using CPU Instructions

## Introduction

Modern operating systems must safely manage shared data structures across many CPUs running concurrently. The Linux kernel frequently executes on multiple cores simultaneously, and different kernel subsystems may attempt to read or modify the same data at the same time.

To prevent data corruption and race conditions, Linux relies on **atomic operations**. These operations guarantee that specific updates to shared memory occur as **indivisible steps**, meaning no other CPU can observe or interfere with the operation while it is executing.

The Linux kernel does not implement atomic behavior purely in software. Instead, it relies on **hardware atomic instructions provided by the CPU**. The kernel wraps these instructions in a portable API so that kernel code can perform atomic operations without needing to know the details of each CPU architecture.

In essence, Linux provides a **layered abstraction**:

```
CPU atomic instructions
        ↓
Architecture-specific kernel code
        ↓
Linux atomic APIs
        ↓
Kernel subsystems
```

This design allows the kernel to run on many different architectures while maintaining consistent atomic behavior.

---

# Location of Atomic Implementations in the Kernel

Atomic operations in Linux are implemented in two main layers.

### Generic API

The architecture-independent interface is defined in:

```
include/linux/atomic.h
```

This header defines types and function prototypes such as:

```
atomic_t
atomic_read
atomic_set
atomic_inc
atomic_dec
atomic_cmpxchg
```

### Architecture-specific implementation

The actual implementation is provided by each CPU architecture.

For example:

```
arch/x86/include/asm/atomic.h
arch/arm64/include/asm/atomic.h
arch/riscv/include/asm/atomic.h
```

These files use **inline assembly or compiler builtins** to map kernel atomics to CPU instructions.

---

# Atomic Data Types

The Linux kernel defines several atomic data types.

### atomic_t

Used for atomic operations on integers.

Example declaration:

```c
#include <linux/atomic.h>

atomic_t counter;
```

### atomic64_t

Used for 64-bit atomic integers.

```c
atomic64_t large_counter;
```

### Initialization

```c
atomic_set(&counter, 0);
```

---

# Core Atomic APIs

The Linux kernel provides a set of atomic functions for safely modifying shared values.

The most important operations include:

```
atomic_read
atomic_set
atomic_inc
atomic_dec
atomic_add
atomic_sub
atomic_cmpxchg
atomic_xchg
```

Each API corresponds to one or more CPU atomic instructions.

---

# atomic_read

## Purpose

Reads the value stored in an atomic variable.

### Example

```c
#include <linux/atomic.h>

atomic_t counter;

void example_read(void)
{
    int value;

    atomic_set(&counter, 10);

    value = atomic_read(&counter);

    printk("counter = %d\n", value);
}
```

### Behavior

This function retrieves the current value of the atomic variable.

Internally it may compile to a simple memory load instruction because reading alone does not require locking.

---

# atomic_set

## Purpose

Initializes or assigns a value to an atomic variable.

### Example

```c
#include <linux/atomic.h>

atomic_t counter;

void example_set(void)
{
    atomic_set(&counter, 0);

    printk("counter initialized\n");
}
```

### Implementation concept

Typically compiled as a normal memory store.

Atomicity is guaranteed by the kernel's memory ordering rules.

---

# atomic_inc

## Purpose

Atomically increments an integer.

### Example

```c
#include <linux/atomic.h>

atomic_t counter;

void increment_example(void)
{
    atomic_set(&counter, 0);

    atomic_inc(&counter);

    printk("counter = %d\n", atomic_read(&counter));
}
```

### Typical x86 implementation

Conceptually equivalent to:

```
lock inc [memory]
```

The `lock` prefix ensures the increment happens atomically across CPUs.

---

# atomic_dec

## Purpose

Atomically decrements an integer.

### Example

```c
#include <linux/atomic.h>

atomic_t counter;

void decrement_example(void)
{
    atomic_set(&counter, 5);

    atomic_dec(&counter);

    printk("counter = %d\n", atomic_read(&counter));
}
```

### Typical CPU instruction

```
lock dec [memory]
```

---

# atomic_add

## Purpose

Adds a value to an atomic variable.

### Example

```c
#include <linux/atomic.h>

atomic_t counter;

void add_example(void)
{
    atomic_set(&counter, 10);

    atomic_add(5, &counter);

    printk("counter = %d\n", atomic_read(&counter));
}
```

Result:

```
counter = 15
```

### Typical CPU instruction

Often implemented with:

```
lock xadd
```

---

# atomic_sub

## Purpose

Subtracts a value atomically.

### Example

```c
#include <linux/atomic.h>

atomic_t counter;

void subtract_example(void)
{
    atomic_set(&counter, 20);

    atomic_sub(3, &counter);

    printk("counter = %d\n", atomic_read(&counter));
}
```

Result:

```
counter = 17
```

---

# atomic_cmpxchg

## Purpose

Compare and exchange (compare-and-swap).

This operation compares a memory value with an expected value and replaces it if the comparison succeeds.

### Example

```c
#include <linux/atomic.h>

atomic_t counter;

void cmpxchg_example(void)
{
    int old;

    atomic_set(&counter, 10);

    old = atomic_cmpxchg(&counter, 10, 20);

    printk("old value = %d\n", old);
    printk("new value = %d\n", atomic_read(&counter));
}
```

Explanation:

```
if counter == 10
    counter becomes 20
```

### CPU instruction

```
lock cmpxchg
```

This is one of the most important primitives used to build lock-free algorithms.

---

# atomic_xchg

## Purpose

Atomically swaps a value in memory with a new value.

### Example

```c
#include <linux/atomic.h>

atomic_t value;

void exchange_example(void)
{
    int old;

    atomic_set(&value, 5);

    old = atomic_xchg(&value, 10);

    printk("old = %d\n", old);
    printk("new = %d\n", atomic_read(&value));
}
```

Result:

```
old = 5
new = 10
```

### CPU instruction

```
xchg
```

On x86, `xchg` with memory is automatically atomic.

---

# Real Kernel Usage Example: Reference Counting

Atomic operations are commonly used for **reference counting**.

### Example

```c
#include <linux/atomic.h>

struct object {
    atomic_t refcount;
};

void object_init(struct object *obj)
{
    atomic_set(&obj->refcount, 1);
}

void object_get(struct object *obj)
{
    atomic_inc(&obj->refcount);
}

void object_put(struct object *obj)
{
    if (atomic_dec_and_test(&obj->refcount)) {
        printk("object can be freed\n");
    }
}
```

Explanation:

```
atomic_inc       → increase reference count
atomic_dec       → decrease reference count
atomic_dec_and_test → check if it reached zero
```

This ensures safe memory management even with multiple threads.

---

# Example: Spinlock Using Atomics

Atomics can be used to implement a simple spinlock.

### Example

```c
#include <linux/atomic.h>

atomic_t lock;

void spin_lock_example(void)
{
    while (atomic_cmpxchg(&lock, 0, 1) != 0) {
        cpu_relax();
    }
}

void spin_unlock_example(void)
{
    atomic_set(&lock, 0);
}
```

Explanation:

```
0 = unlocked
1 = locked
```

Threads repeatedly attempt to change `0 → 1`.  
Only one succeeds.

---

# Why the Kernel Uses Custom Atomics Instead of C11

The Linux kernel does not rely on standard C atomics for several reasons:

1. The kernel predates the C11 standard.
    
2. The kernel requires tight control over memory ordering.
    
3. It must support many architectures consistently.
    
4. Inline assembly sometimes provides better performance.
    

Thus, Linux maintains its own atomic abstraction layer.

---

# Summary

The Linux kernel implements atomic operations by wrapping CPU atomic instructions inside a portable API. These APIs allow kernel developers to safely update shared data structures without needing to directly write architecture-specific assembly code.

Atomic types such as `atomic_t` provide operations like increment, decrement, addition, compare-and-swap, and exchange. Internally, these functions map directly to hardware instructions such as `lock inc`, `cmpxchg`, and `xadd`.

Through this abstraction, Linux ensures safe concurrency across different CPU architectures while maintaining high performance and scalability.

Atomic operations therefore form the **foundation of synchronization inside the Linux kernel**, enabling mechanisms such as reference counting, spinlocks, and lock-free data structures.

---

If you want, I can also write the **next essay that usually comes after this in systems notes**:

**“Memory Ordering in CPUs and the Linux Kernel (Barriers, Acquire/Release, and Reordering)”**

This is the **hardest but most important part** of concurrency and fits perfectly after atomics.