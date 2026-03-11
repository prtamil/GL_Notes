## Acquire and Release Semantics: Efficient Synchronization Between CPUs

### Introduction

Modern multiprocessor systems allow CPUs to reorder memory operations internally to improve performance. Mechanisms such as store buffers, speculative execution, and out-of-order pipelines allow processors to execute instructions faster, but they also introduce situations where different CPUs observe memory operations in different orders.

To build correct concurrent systems, programmers must ensure that certain memory operations become visible in the proper order across CPUs. Memory barriers can enforce this ordering, but full barriers are often stronger than necessary and can reduce performance because they restrict many CPU optimizations.

For many synchronization patterns, only **partial ordering guarantees** are required. Instead of preventing all reordering, we only need to ensure that some operations occur before others when threads communicate.

This is where **acquire and release semantics** become useful. They provide a lightweight and structured way to enforce ordering between threads while allowing CPUs to continue performing many internal optimizations.

Acquire and release operations create a synchronization relationship that ensures memory operations performed by one thread become visible to another thread in the intended order.

In the Linux kernel, these semantics are implemented using primitives such as:

```
smp_load_acquire()
smp_store_release()
```

These primitives are widely used in lock-free algorithms, synchronization mechanisms, and communication between threads.

---

# The Core Idea Behind Acquire and Release

Acquire and release semantics establish a **happens-before relationship** between two threads.

The basic idea can be understood as a synchronization handshake between a **producer** and a **consumer**.

1. The producer prepares data.
    
2. The producer performs a **release operation** when publishing the data.
    
3. The consumer performs an **acquire operation** when checking for the signal.
    

If the acquire operation reads the value written by the release operation, then all memory operations performed before the release become visible to the consumer.

Conceptually:

```
Producer thread
----------------
write data
release store (publish)

Consumer thread
----------------
acquire load (observe signal)
read data
```

This ensures that once the consumer observes the signal, it also observes all the data that was written before the signal.

---

# Why Acquire and Release Are Needed

Consider a shared communication example.

Shared variables:

```c
int data = 0;
int ready = 0;
```

Producer thread:

```c
data = 42;
ready = 1;
```

Consumer thread:

```c
while (ready == 0)
    ;

printf("%d\n", data);
```

The intended behavior is that once the consumer observes `ready == 1`, the value of `data` should already be updated.

However, due to CPU reordering or store buffers, the following sequence might occur:

```
ready = 1 becomes visible first
data = 42 becomes visible later
```

The consumer might read:

```
ready = 1
data = 0
```

This violates the intended synchronization.

Acquire and release semantics ensure that the data write becomes visible before the signal update.

---

# Why Not Just Use Memory Barriers?

At first glance it may seem that memory barriers alone could solve this problem. For example:

Producer:

```c
data = 42;
smp_wmb();
ready = 1;
```

Consumer:

```c
while (ready == 0)
    ;

smp_rmb();
printf("%d\n", data);
```

This works, but barriers have several limitations.

### 1. Barriers Are Harder to Reason About

Memory barriers operate independently and require the programmer to correctly place barriers on **both sides** of synchronization.

If one side forgets the correct barrier, the program may break.

Acquire and release primitives encode the synchronization directly into the load and store operations, making the intent clearer.

---

### 2. Barriers Are Often Stronger Than Necessary

A full memory barrier (`smp_mb()`) prevents almost all types of reordering. This can significantly restrict CPU optimizations.

Acquire and release semantics enforce **only the ordering needed for synchronization**, allowing other operations to remain flexible.

---

### 3. Barriers Do Not Naturally Express Synchronization

Barriers simply enforce ordering but do not describe the relationship between threads.

Acquire and release operations explicitly represent:

```
publish data
observe data
```

This makes concurrent algorithms easier to understand and maintain.

---

### 4. Acquire and Release Are More Efficient

Acquire and release operations typically map to **lighter-weight instructions** on modern CPUs.

Examples:

ARM:

```
ldar   (load acquire)
stlr   (store release)
```

These instructions enforce ordering only where needed and avoid the heavy cost of full memory fences.

---

# Synchronization Pattern: Producer–Consumer

Acquire and release semantics are commonly used in the **producer–consumer communication pattern**.

Shared variables:

```c
int data;
int ready = 0;
```

Producer:

```c
void producer()
{
    data = 100;
    smp_store_release(&ready, 1);
}
```

Consumer:

```c
void consumer()
{
    while (smp_load_acquire(&ready) == 0)
        ;

    printf("%d\n", data);
}
```

Execution sequence:

1. Producer writes `data`.
    
2. Producer performs a release store on `ready`.
    
3. Consumer waits until the acquire load reads the updated value.
    
4. Consumer reads the data.
    

Because the acquire observes the value written by the release, the system guarantees:

```
data write happens-before ready update
ready update happens-before consumer reads data
```

Therefore the consumer always reads the correct value.

---

# Release Semantics

A **release operation** ensures that all memory operations before it complete before the release becomes visible to other CPUs.

Conceptually:

```
writes before release
      happen-before
release store
```

In the Linux kernel, release semantics are implemented using:

```
smp_store_release()
```

### Complete Example: Publishing Data Safely

Shared variables:

```c
int data = 0;
int ready = 0;
```

Producer thread:

```c
void producer()
{
    data = 1234;

    /* publish signal */
    smp_store_release(&ready, 1);
}
```

Explanation:

1. The producer writes the data.
    
2. The release store ensures the data write completes before `ready` becomes visible.
    
3. Other CPUs cannot observe `ready = 1` without also observing the updated data.
    

Conceptual ordering guarantee:

```
data = 1234
    happens-before
ready = 1
```

This prevents the CPU from reordering the `data` write after the signal.

---

# Acquire Semantics

An **acquire operation** ensures that no memory operations following it are allowed to move before it.

Conceptually:

```
acquire load
     happens-before
subsequent reads and writes
```

In the Linux kernel this is implemented using:

```
smp_load_acquire()
```

### Complete Example: Consuming Published Data

Shared variables:

```c
int data = 0;
int ready = 0;
```

Consumer thread:

```c
void consumer()
{
    while (smp_load_acquire(&ready) == 0)
        ;

    printf("Data = %d\n", data);
}
```

Explanation:

1. The consumer repeatedly checks the signal using an acquire load.
    
2. Once it observes the value written by the release store, the acquire ensures that all previous writes performed by the producer are visible.
    
3. The consumer safely reads the updated value of `data`.
    

Execution ordering:

```
producer writes data
producer release store
consumer acquire load
consumer reads data
```

This guarantees correct visibility of shared data.

---

# How Acquire and Release Prevent Reordering

Acquire and release semantics impose directional ordering constraints.

### Release Ordering

```
write A
release store
write B
```

The CPU cannot move `write A` after the release.

---

### Acquire Ordering

```
acquire load
read A
read B
```

The CPU cannot move `read A` or `read B` before the acquire.

---

### Combined Synchronization

When a release store and acquire load interact:

```
Producer
--------
write data
release store

Consumer
--------
acquire load
read data
```

If the acquire reads the value written by the release, then the system establishes a **happens-before relationship**.

This ensures proper synchronization between the threads.

---

# Hardware Implementation

Acquire and release semantics are typically implemented using lightweight hardware instructions.

### x86

The x86 architecture has a relatively strong memory model. Normal loads and stores already provide acquire and release behavior, so additional instructions are often unnecessary.

### ARM

ARM processors provide explicit instructions:

```
ldar   (load acquire)
stlr   (store release)
```

These instructions enforce ordering while remaining more efficient than full memory barriers.

### RISC-V

RISC-V provides acquire and release semantics through flags on atomic instructions or through `fence` instructions.

---

# Conclusion

Acquire and release semantics provide an efficient abstraction for synchronizing threads in concurrent systems. Instead of relying solely on heavy memory barriers, they enforce ordering only where it is required for communication between threads.

A **release operation** ensures that all memory writes before it become visible before the release is observed by another CPU. An **acquire operation** ensures that once a thread observes the release, it also observes all the memory updates that occurred before it.

In the Linux kernel, primitives such as `smp_store_release()` and `smp_load_acquire()` implement these semantics in a portable way across architectures such as x86, ARM, and RISC-V. By using acquire and release operations, developers can build efficient synchronization patterns that maintain correctness while allowing modern processors to continue performing aggressive performance optimizations.