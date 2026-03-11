## Sequential Consistency: The Strongest Memory Ordering Model

### Introduction

In concurrent systems with multiple CPUs, memory operations such as reads and writes can be **reordered** by both the compiler and the processor to improve performance. While these optimizations make programs run faster, they also make the behavior of shared memory harder to reason about.

To manage this complexity, computer architectures and programming languages define **memory ordering models** that specify how memory operations may appear to execute across different CPUs.

Among these models, **Sequential Consistency (SC)** provides the **strongest and most intuitive ordering guarantee**.

Sequential consistency was formally defined by Leslie Lamport in 1979 as the most natural model for reasoning about concurrent programs.

Under sequential consistency, a program behaves **as if all operations from all CPUs were executed in a single global order**, and **each CPU’s operations appear in the order written in the program**.

This model eliminates most of the surprising behaviors caused by memory reordering and makes concurrent programs easier to understand.

---

# The Abstraction of Sequential Consistency

Sequential consistency provides a simple mental model:

> All threads execute their operations in **program order**, and there exists a **single global timeline** in which all memory operations appear.

Imagine a system where all memory operations are placed into a **single shared queue**. Each CPU submits operations to this queue, and the operations are executed one by one.

Conceptually:

```
Global memory order

CPU1: write A
CPU2: write B
CPU1: read B
CPU2: read A
```

Under sequential consistency, every CPU observes the **same ordering of operations**.

The important rules are:

1. **Program Order Rule**  
    Each CPU's operations occur in the order written in the program.
    
2. **Global Visibility Rule**  
    All CPUs observe memory operations in the same global order.
    

Because of these guarantees, sequential consistency eliminates many subtle concurrency bugs.

---

# Why Sequential Consistency Is Important

Without strong ordering guarantees, CPUs may reorder instructions such as:

```
store A
store B
```

into:

```
store B
store A
```

Another CPU may observe these stores in a different order than intended.

Sequential consistency prevents such surprises by enforcing strict ordering rules.

It provides a **simple programming model** where developers can reason about concurrent programs as if instructions execute one at a time in a predictable sequence.

This is especially useful for:

- debugging concurrent algorithms
    
- building synchronization primitives
    
- designing lock-free data structures
    

---

# Example: Store Buffer Reordering Problem

Consider two CPUs sharing two variables.

Shared variables:

```c
int x = 0;
int y = 0;
```

Thread 1:

```c
x = 1;
r1 = y;
```

Thread 2:

```c
y = 1;
r2 = x;
```

Without strict memory ordering, the following result is possible:

```
r1 = 0
r2 = 0
```

This occurs because each CPU may:

1. write to its store buffer
    
2. read the other variable before the store becomes visible
    

So the execution might look like:

```
CPU1: x = 1 (store buffered)
CPU2: y = 1 (store buffered)

CPU1 reads y -> 0
CPU2 reads x -> 0
```

Under **sequential consistency**, this outcome is impossible because the system must produce a **single global order** of operations.

Possible valid orders would be:

```
x=1 → y=1 → r1=1 → r2=1
```

or

```
y=1 → x=1 → r2=1 → r1=1
```

But both reads returning `0` cannot happen.

---

# Sequential Consistency in Programming Languages

Modern programming languages implement sequential consistency using **atomic operations with the strongest ordering mode**.

In **C11 atomics**, this ordering is expressed as:

```
memory_order_seq_cst
```

This mode guarantees:

- a global total order of all sequentially consistent operations
    
- consistent visibility across all threads
    

Example:

```c
#include <stdatomic.h>
#include <stdio.h>

atomic_int x = 0;
atomic_int y = 0;

void thread1()
{
    atomic_store_explicit(&x, 1, memory_order_seq_cst);
    int r1 = atomic_load_explicit(&y, memory_order_seq_cst);

    printf("Thread1 read y = %d\n", r1);
}

void thread2()
{
    atomic_store_explicit(&y, 1, memory_order_seq_cst);
    int r2 = atomic_load_explicit(&x, memory_order_seq_cst);

    printf("Thread2 read x = %d\n", r2);
}
```

Here, both loads and stores participate in the **global sequentially consistent order**.

---

# Sequential Consistency in the Linux Kernel

The Linux kernel typically prefers **weaker memory models** such as acquire and release because they allow better performance.

However, sequential consistency can be enforced using **full memory barriers**.

Example:

```
smp_mb()
```

This macro introduces a **full memory fence**.

Example:

```c
#include <linux/kernel.h>
#include <linux/module.h>

int x = 0;
int y = 0;

void thread1(void)
{
    x = 1;

    smp_mb();   // full memory barrier

    int r1 = y;

    printk("Thread1 read y = %d\n", r1);
}

void thread2(void)
{
    y = 1;

    smp_mb();   // full memory barrier

    int r2 = x;

    printk("Thread2 read x = %d\n", r2);
}
```

The `smp_mb()` ensures that:

- all previous memory operations complete
    
- before any later operations begin
    

This approximates **sequential consistency behavior**.

---

# Usage Patterns of Sequential Consistency

Sequential consistency is commonly used when:

### 1. Simplicity Is More Important Than Performance

Some algorithms are easier to reason about using strict ordering.

Examples:

- academic algorithms
    
- teaching concurrent programming
    
- debugging synchronization bugs
    

---

### 2. Building Higher-Level Synchronization

Many synchronization primitives internally rely on sequentially consistent operations.

Examples include:

- mutex locks
    
- condition variables
    
- atomic counters
    

---

### 3. Global Ordering Requirements

Some systems require a consistent ordering across all CPUs.

Examples include:

- global event logging
    
- distributed coordination
    
- consensus algorithms
    

---

# Performance Cost of Sequential Consistency

Sequential consistency is powerful but **expensive**.

It restricts many CPU optimizations:

- store buffering
    
- speculative loads
    
- instruction reordering
    

To enforce these rules, CPUs may need to insert **memory fence instructions**.

Examples:

x86:

```
mfence
```

ARM:

```
dmb ish
```

These instructions stall the CPU pipeline and reduce parallel execution opportunities.

For this reason, modern systems prefer **weaker memory ordering models** whenever possible.

---

# Relationship with Other Memory Ordering Models

Memory ordering models form a hierarchy of strength:

```
Sequential Consistency (strongest)

Acquire / Release

Relaxed Ordering (weakest)
```

Sequential consistency prevents almost all reordering.

Acquire and release allow some flexibility while still supporting synchronization.

Relaxed ordering provides minimal guarantees but offers maximum performance.

---

# Conclusion

Sequential consistency is the **strongest and most intuitive memory ordering model** used in concurrent systems. It guarantees that all memory operations appear to execute in a single global order that respects the program order of each thread.

This model greatly simplifies reasoning about concurrent programs because developers can imagine that operations occur one at a time in a predictable sequence.

However, enforcing sequential consistency requires restricting many CPU optimizations, which can reduce performance on modern processors. For this reason, systems such as the Linux kernel typically use weaker ordering models like acquire and release, reserving sequential consistency for situations where strict ordering is essential.

Understanding sequential consistency provides a solid foundation for reasoning about weaker memory models and designing correct synchronization mechanisms in high-performance concurrent systems.