
# Memory Ordering in CPUs and the Linux Kernel

## Barriers, Acquire/Release, and Reordering

## Introduction

Atomic operations ensure that a particular memory update happens as an indivisible step. However, atomicity alone does not guarantee that different CPUs will observe memory operations in the same order. Modern processors aggressively reorder instructions and memory accesses to improve performance. As a result, even when operations are atomic, other processors may observe them in an unexpected order.

This problem is addressed through **memory ordering rules** and **memory barriers**.

Memory ordering defines **when changes made by one CPU become visible to other CPUs and in what order they appear**. Without proper ordering guarantees, concurrent programs may behave incorrectly even when atomic operations are used.

The Linux kernel therefore provides mechanisms that control how memory operations are ordered and observed across processors. These mechanisms include **memory barriers** and **acquire/release semantics**, which enforce visibility constraints between threads.

Understanding memory ordering is essential for writing correct concurrent code in operating systems, lock-free data structures, and low-level synchronization mechanisms.

---

# Why CPUs Reorder Instructions

Modern CPUs are designed to maximize performance. To keep their execution pipelines full, processors may reorder instructions internally as long as the final single-threaded result remains correct.

For example, consider two memory writes:

```
A = 1
B = 1
```

A CPU may execute them in the opposite order:

```
B = 1
A = 1
```

For a single-threaded program this does not change the final outcome. However, when multiple CPUs observe the memory operations, they may see different orders.

Consider two processors:

CPU 1:

```
data = 42
flag = 1
```

CPU 2:

```
if (flag == 1)
    print(data)
```

Without ordering guarantees, CPU 2 might observe:

```
flag = 1
data = 0
```

Even though CPU 1 wrote `data` first.

This occurs because:

1. CPUs reorder memory operations.
    
2. CPU caches delay when writes become visible to other processors.
    

This phenomenon is known as **memory reordering**.

---

# Memory Models

Different CPU architectures define different **memory models**, which specify the allowed reorderings of memory operations.

### Strong memory model

Some architectures provide stronger guarantees.

Example:

```
x86 (Total Store Order - TSO)
```

On x86 processors:

- loads are mostly ordered
    
- stores appear in program order
    

Reordering still happens internally, but the architecture hides many effects.

---

### Weak memory model

Many modern architectures use weaker models.

Examples:

```
ARM
RISC-V
PowerPC
```

These architectures allow more aggressive reordering, meaning programmers must explicitly enforce ordering when needed.

This is why portable operating systems like Linux provide explicit memory barrier primitives.

---

# Memory Barriers

A **memory barrier** (also called a memory fence) is an instruction that prevents certain types of reordering.

Barriers ensure that specific memory operations complete before others begin.

Linux provides several barrier primitives.

---

# Full Memory Barrier

A full memory barrier prevents both loads and stores from being reordered across it.

Linux primitive:

```
smp_mb()
```

Meaning:

```
All memory operations before the barrier
must complete before operations after it begin.
```

Example:

```
CPU1

data = 42
smp_mb()
flag = 1
```

```
CPU2

if (flag == 1) {
    smp_mb()
    print(data)
}
```

This guarantees that if CPU2 sees `flag = 1`, it will also see `data = 42`.

---

# Read Memory Barrier

A read barrier prevents loads from being reordered.

Linux primitive:

```
smp_rmb()
```

Example:

```
value1 = data1
smp_rmb()
value2 = data2
```

This ensures the CPU reads `data1` before reading `data2`.

---

# Write Memory Barrier

A write barrier prevents stores from being reordered.

Linux primitive:

```
smp_wmb()
```

Example:

```
data = 42
smp_wmb()
flag = 1
```

This ensures `data` becomes visible before `flag`.

---

# Acquire and Release Semantics

Modern concurrency models often use **acquire and release semantics** rather than explicit barriers.

These semantics provide a structured way to enforce ordering.

---

# Release Semantics

A **release operation** ensures that all previous memory writes become visible before the release occurs.

Example:

```
store_release(flag, 1)
```

Meaning:

```
All previous writes must complete
before flag is updated.
```

Producer example:

```
data = 42
store_release(flag, 1)
```

---

# Acquire Semantics

An **acquire operation** ensures that all subsequent reads happen after the acquire.

Example:

```
load_acquire(flag)
```

Consumer example:

```
if (load_acquire(flag)) {
    print(data)
}
```

This ensures that if the consumer observes `flag = 1`, it also sees the correct `data`.

---

# Example: Producer–Consumer with Ordering

Producer thread:

```
data = 100
store_release(flag, 1)
```

Consumer thread:

```
if (load_acquire(flag)) {
    use(data)
}
```

Guarantee:

```
consumer sees data = 100
```

Acquire and release operations therefore synchronize memory visibility between threads.

---

# Linux Kernel Barrier APIs

The Linux kernel provides several barrier functions.

Important ones include:

```
smp_mb()      full barrier
smp_rmb()     read barrier
smp_wmb()     write barrier
```

Additional variants exist for specific contexts.

Example usage:

```c
int data;
int flag;

void producer(void)
{
    data = 42;
    smp_wmb();
    flag = 1;
}

void consumer(void)
{
    if (flag) {
        smp_rmb();
        printk("%d\n", data);
    }
}
```

This ensures the consumer reads `data` only after the producer writes it.

---

# Interaction with Atomic Operations

Atomic operations do not always guarantee memory ordering by themselves.

Some atomic operations include ordering semantics, but others do not.

For example:

```
atomic_read()
atomic_set()
```

These may not impose strong ordering.

Therefore kernel code often combines atomics with barriers.

Example:

```
atomic_set(&flag, 1);
smp_mb();
```

This ensures that prior writes become visible before the flag is updated.

---

# CPU Instructions for Memory Barriers

At the hardware level, barriers correspond to specific instructions.

Examples:

x86:

```
mfence
lfence
sfence
```

ARM:

```
dmb
dsb
isb
```

RISC-V:

```
fence
```

These instructions enforce ordering constraints within the CPU pipeline and cache system.

---

# Why Memory Ordering Matters

Memory ordering is critical for implementing:

```
spinlocks
mutexes
reference counters
lock-free queues
kernel schedulers
device drivers
```

Without proper ordering guarantees, concurrent programs may appear correct during testing but fail unpredictably on different CPUs or under heavy concurrency.

This is why understanding memory ordering is essential for systems programming.

---

# Summary

Atomic operations guarantee that individual memory updates occur without interruption. However, they do not fully control how memory operations are ordered or when they become visible to other processors.

Modern CPUs reorder instructions and delay memory visibility for performance reasons. To ensure correct behavior in concurrent programs, developers must use memory barriers and acquire/release semantics to enforce ordering constraints.

The Linux kernel provides a set of barrier primitives such as `smp_mb`, `smp_rmb`, and `smp_wmb`, which map to architecture-specific instructions that control memory ordering at the hardware level.

Together with atomic operations, these mechanisms provide the foundation for safe and efficient synchronization in multi-core systems.

