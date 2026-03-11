## CPU Memory Reordering

### Introduction

Modern processors are designed to execute billions of instructions per second. To achieve such high performance, CPUs use several internal optimizations that allow instructions to execute in a different order than the one written in the program. One of the most important of these optimizations is **CPU instruction reordering**.

CPU reordering means that the processor may **execute instructions out of program order** when doing so improves performance, while still preserving the correctness of a single-threaded program. This behavior is fundamental to modern processor design, but it becomes important when multiple CPUs communicate through shared memory.

Understanding CPU reordering is essential for understanding **memory ordering**, because many concurrency bugs occur when different processors observe operations in different orders.

---

## Why CPUs Reorder Instructions

Modern CPUs are much faster than main memory. A memory access can take hundreds of CPU cycles, while an arithmetic instruction may take only one cycle. If the CPU strictly waited for each instruction to complete before executing the next one, most of the processor’s resources would remain idle.

To avoid this inefficiency, CPUs use several techniques:

- instruction pipelines
    
- out-of-order execution
    
- speculative execution
    
- memory buffers
    

These techniques allow the processor to execute independent instructions earlier rather than waiting for slower operations to complete.

For example, if one instruction is waiting for data from memory, the CPU may execute other instructions that do not depend on that data.

---

## Program Order vs Execution Order

The **program order** is the sequence of instructions written in the program.

Example:

```
1. A = 1
2. B = 1
```

The **execution order** is the order in which the CPU actually performs the operations.

A processor might internally execute them as:

```
B = 1
A = 1
```

This reordering is allowed if the CPU can prove that doing so does not affect the behavior of the program running on a single thread.

However, another CPU observing these memory updates may see them in this reordered form.

---

## Out-of-Order Execution

One of the main reasons CPUs reorder instructions is **out-of-order execution**.

In out-of-order execution, the CPU does not strictly follow program order. Instead, it executes instructions as soon as their input operands are ready.

Consider the following instructions:

```
1. load A
2. add B
3. multiply C
```

If the first instruction is waiting for memory, the CPU may execute the second or third instruction first.

This improves performance because the CPU does not waste time waiting for slow operations.

Internally, the processor uses structures such as:

- instruction reservation stations
    
- reorder buffers
    
- dependency tracking logic
    

These components ensure that results are eventually committed in a way that preserves correct program behavior.

---

## Store Buffers and Memory Reordering

Another important source of CPU memory reordering is the **store buffer**.

When a CPU writes to memory, the value is often placed into a temporary buffer before being written to the cache or main memory. This allows the CPU to continue executing instructions without waiting for the memory write to complete.

Because of this buffering, writes may become visible to other CPUs later than expected.

Example:

CPU1 executes:

```
X = 1
Y = 1
```

Due to store buffering, another CPU might observe:

```
Y = 1
X = 0
```

This does not violate the CPU’s internal execution rules, but it can produce surprising results in concurrent programs.

---

## Load Reordering

CPUs may also reorder **read operations** (loads).

Example:

```
r1 = A
r2 = B
```

The processor might execute the second load first if doing so improves performance or avoids pipeline stalls.

This behavior can cause different CPUs to observe memory operations in different orders.

---

## Common Types of CPU Reordering

Several types of memory operation reordering can occur in CPUs:

**Load → Load reordering**

A later read may execute before an earlier read.

```
r1 = A
r2 = B
```

The CPU may read `B` before `A`.

---

**Store → Store reordering**

Two writes may become visible in a different order.

```
A = 1
B = 1
```

Another CPU might observe `B` before `A`.

---

**Load → Store reordering**

A read may execute before an earlier write.

```
A = 1
r1 = B
```

The read may occur before the write completes.

---

**Store → Load reordering**

A write followed by a read may appear reordered.

```
A = 1
r1 = B
```

The read might execute before the write becomes visible.

This is the most common form of reordering on many architectures.

---

## Example of CPU Reordering Problem

Consider two threads running on different CPUs.

Thread 1:

```
X = 1
r1 = Y
```

Thread 2:

```
Y = 1
r2 = X
```

If no ordering constraints exist, the following result is possible:

```
r1 = 0
r2 = 0
```

Both threads may read the old values because the writes were delayed or reordered.

This scenario demonstrates why memory ordering mechanisms are necessary.

---

## Architecture Differences

Different CPU architectures allow different levels of reordering.

Some processors allow aggressive reordering, while others enforce stricter ordering rules.

For example:

- **x86 processors** use a relatively strong memory model and limit many types of reordering.
    
- **ARM processors** allow more aggressive reordering for better performance.
    
- **RISC-V processors** also allow flexible memory ordering depending on configuration.
    

Because of these differences, operating systems such as Linux must use **explicit memory barriers** to ensure correct behavior across architectures.

---

## Preventing CPU Reordering

To control CPU reordering, programmers and operating systems use **memory ordering primitives**, including:

Memory barriers:

```
smp_mb()
smp_rmb()
smp_wmb()
```

Acquire and release operations:

```
smp_load_acquire()
smp_store_release()
```

Atomic operations with ordering guarantees.

These mechanisms instruct the CPU and compiler to restrict certain types of reordering.

---

## Summary

CPU memory reordering is a fundamental feature of modern processors designed to improve performance. By executing instructions out of order, overlapping memory operations, and buffering writes, CPUs can keep their pipelines busy and hide memory latency.

However, these optimizations mean that the order in which operations become visible to other CPUs may differ from the order written in the program. This behavior can cause unexpected results in concurrent programs.

To maintain correctness, systems use memory ordering mechanisms such as barriers and acquire-release semantics to control when operations become visible across processors. Understanding CPU reordering is therefore essential for building reliable concurrent systems such as operating system kernels.