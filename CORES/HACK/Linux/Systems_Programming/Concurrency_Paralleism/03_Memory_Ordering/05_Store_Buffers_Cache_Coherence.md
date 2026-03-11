## Store Buffers, Cache Coherence, and Why Memory Reordering Actually Happens

### Introduction

When programmers first learn about memory ordering, they often assume that memory behaves like a single shared object where every write immediately becomes visible to every CPU. However, modern multiprocessor systems do not work this way. In reality, each CPU core has its own caches and internal buffers, and writes may not become visible to other CPUs immediately.

To achieve high performance, processors use mechanisms such as **store buffers, private caches, and cache coherence protocols**. These mechanisms significantly improve execution speed but also introduce situations where memory operations appear to occur out of order when observed from different CPUs.

Understanding **store buffers** and **cache coherence** explains the real hardware reasons behind memory reordering. These mechanisms form the foundation for why memory barriers and synchronization primitives are necessary in concurrent programming.

---

## The Problem: Memory Visibility Between CPUs

Consider a system with two CPU cores executing concurrently. Both cores access shared variables in memory.

Thread running on CPU0:

```c
X = 1;
```

Thread running on CPU1:

```c
if (X == 1) {
    printf("X updated\n");
}
```

A programmer might expect that once CPU0 executes `X = 1`, CPU1 will immediately see that change. However, modern processors do not update main memory directly for every write. Instead, they use intermediate hardware structures to optimize performance.

As a result, CPU1 may temporarily observe the old value of `X` even after CPU0 has executed the write instruction.

---

## Store Buffers

### What Is a Store Buffer?

A **store buffer** is a small hardware queue inside a CPU core that temporarily holds write operations before they are committed to the cache or main memory.

Instead of waiting for a write to propagate through the entire memory system, the CPU places the write into the store buffer and continues executing subsequent instructions immediately.

This improves performance because writing to memory can take many cycles due to cache and bus latency.

Conceptually:

```
Program instruction
        ↓
Store buffer
        ↓
CPU cache
        ↓
Main memory
```

The CPU treats the write as complete once it enters the store buffer, even though other CPUs may not yet see the update.

---

### Example of Store Buffer Behavior

Consider two shared variables:

```c
int X = 0;
int Y = 0;
```

Two CPUs execute the following code.

CPU0:

```c
X = 1;
r1 = Y;
```

CPU1:

```c
Y = 1;
r2 = X;
```

At first glance, it seems impossible for both `r1` and `r2` to become `0`. But due to store buffers, the following sequence may occur:

1. CPU0 writes `X = 1` into its store buffer.
    
2. CPU1 writes `Y = 1` into its store buffer.
    
3. CPU0 reads `Y` before CPU1’s store buffer flushes.
    
4. CPU1 reads `X` before CPU0’s store buffer flushes.
    

Final results:

```
r1 = 0
r2 = 0
```

Both CPUs observe stale values because the writes have not yet propagated from the store buffers to shared memory.

This phenomenon is a fundamental example of **memory reordering caused by hardware buffering**.

---

## CPU Caches and Private Memory Views

Modern processors use multiple levels of cache to reduce memory access latency.

Typical structure:

```
CPU Core
   ↓
L1 Cache
   ↓
L2 Cache
   ↓
L3 Cache (shared)
   ↓
Main Memory
```

Each CPU core typically has its own **private L1 and L2 caches**. Because of this, each CPU can temporarily hold different versions of the same memory location.

For example:

```
CPU0 cache: X = 1
CPU1 cache: X = 0
```

Until the caches synchronize, the two CPUs observe different values.

This is where **cache coherence protocols** become essential.

---

## Cache Coherence

### What Is Cache Coherence?

Cache coherence ensures that all CPUs eventually agree on the value of shared memory locations.

When one CPU modifies a memory location, the coherence protocol ensures that other CPUs update or invalidate their cached copies.

Most modern processors implement some variation of the **MESI protocol**.

MESI stands for:

```
Modified
Exclusive
Shared
Invalid
```

These states describe the status of a cache line in each CPU’s cache.

---

### MESI Protocol Overview

1. **Modified**  
    The cache line has been changed by the CPU and differs from main memory.
    
2. **Exclusive**  
    The cache line exists only in one CPU’s cache and matches main memory.
    
3. **Shared**  
    Multiple CPUs hold identical copies of the cache line.
    
4. **Invalid**  
    The cache line is not valid and must be fetched again.
    

---

### Example of Cache Coherence in Action

Suppose both CPUs initially read the variable `X`.

```
CPU0 cache: X = 0
CPU1 cache: X = 0
State: Shared
```

Now CPU0 updates `X`.

```c
X = 1;
```

The coherence protocol performs these actions:

1. CPU0 changes its cache line state to **Modified**.
    
2. CPU1's cached copy is **invalidated**.
    
3. If CPU1 later reads `X`, it must fetch the updated value.
    

This mechanism ensures that eventually all CPUs observe consistent memory values.

---

## Why Memory Reordering Happens

Even though cache coherence ensures eventual consistency, CPUs still allow temporary inconsistencies for performance reasons.

Three main mechanisms contribute to memory reordering.

### 1. Store Buffers

Writes are delayed before becoming visible to other CPUs.

### 2. Load Speculation

CPUs may execute loads before earlier instructions complete.

### 3. Out-of-Order Execution

CPUs may execute instructions in a different order internally while preserving single-threaded correctness.

Because of these mechanisms, memory operations may appear in different orders across CPUs.

---

## Example Demonstrating Memory Reordering

Consider again the earlier example.

Initial state:

```
X = 0
Y = 0
```

Two CPUs execute:

CPU0:

```c
X = 1;
r1 = Y;
```

CPU1:

```c
Y = 1;
r2 = X;
```

Possible outcome:

```
r1 = 0
r2 = 0
```

Explanation:

```
CPU0 store buffer: X = 1
CPU1 store buffer: Y = 1
```

The writes remain buffered and invisible to the other CPU when the reads occur.

This example demonstrates how hardware optimizations produce memory behaviors that differ from the program order.

---

## Why Memory Barriers Are Needed

Because store buffers and caches delay the visibility of writes, concurrent programs require mechanisms to enforce ordering.

Memory barriers force the CPU to complete certain memory operations before continuing execution.

For example, a full memory barrier ensures:

```
all previous reads and writes complete
before any later operations begin
```

In operating systems like Linux, developers use primitives such as:

```
smp_mb()
smp_rmb()
smp_wmb()
```

These ensure that memory operations become visible in a predictable order across CPUs.

---

## Conclusion

Memory reordering is not an arbitrary behavior introduced by compilers or operating systems. It is a direct consequence of the hardware optimizations used in modern processors.

Store buffers allow CPUs to continue executing without waiting for slow memory writes. Private caches reduce memory access latency but allow CPUs to temporarily hold different views of memory. Cache coherence protocols ensure that these views eventually become consistent across processors.

While these mechanisms significantly improve system performance, they also introduce situations where memory operations appear out of order to other CPUs. Because of this, concurrent programs must use synchronization mechanisms such as memory barriers and atomic operations to enforce correct ordering.

Understanding store buffers, cache coherence, and the resulting memory behaviors provides the hardware-level foundation for reasoning about memory ordering and synchronization in modern multiprocessor systems.