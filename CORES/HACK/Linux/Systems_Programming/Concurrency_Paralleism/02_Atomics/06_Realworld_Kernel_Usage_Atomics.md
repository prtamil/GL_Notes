
# Real Linux Kernel Source Examples of Atomics

## Scheduler, Networking, and Memory Management

## Introduction

Atomic operations are not just theoretical primitives; they appear throughout the Linux kernel in performance-critical subsystems. The kernel must coordinate thousands of concurrent operations across many CPU cores, and atomics provide a fast way to update shared state without heavy locking.

Several core subsystems rely on atomic operations extensively:

- the **CPU scheduler**
    
- the **networking stack**
    
- the **memory management system**
    

In each subsystem, atomics are used to maintain shared counters, manage object lifetimes, and synchronize state between CPUs.

Understanding these real-world usages helps reveal why atomics are a fundamental building block of kernel concurrency.

---

# Atomics in the Linux Scheduler

The Linux scheduler is responsible for deciding which task runs on which CPU. Many scheduler data structures are accessed concurrently by different CPUs, so atomic operations are used to maintain consistent state.

One example is **tracking the number of running tasks**.

Inside the scheduler, the kernel maintains counters that track runnable tasks and scheduling statistics.

A simplified version of such a counter looks like this:

```c
#include <linux/atomic.h>

struct runqueue {
    atomic_t nr_running;
};
```

Whenever a task becomes runnable, the scheduler increments the counter.

### Example: Task Enters Run Queue

```c
void enqueue_task(struct runqueue *rq)
{
    atomic_inc(&rq->nr_running);
}
```

### Example: Task Leaves Run Queue

```c
void dequeue_task(struct runqueue *rq)
{
    atomic_dec(&rq->nr_running);
}
```

### Reading the Value

```c
int running_tasks(struct runqueue *rq)
{
    return atomic_read(&rq->nr_running);
}
```

### Why Atomics Are Needed

Multiple CPUs may modify the run queue simultaneously. Without atomic operations, updates could be lost due to race conditions.

Atomic increments ensure that each task addition is counted correctly.

---

# Atomics in the Networking Stack

The networking subsystem handles extremely high packet rates and must operate efficiently on multicore systems. To track packet processing statistics, the kernel uses atomic counters.

One example is **tracking received packets**.

A simplified structure used in networking drivers may look like this:

```c
#include <linux/atomic.h>

struct net_stats {
    atomic_t rx_packets;
    atomic_t tx_packets;
};
```

### Packet Receive Example

```c
void packet_received(struct net_stats *stats)
{
    atomic_inc(&stats->rx_packets);
}
```

### Packet Transmission Example

```c
void packet_sent(struct net_stats *stats)
{
    atomic_inc(&stats->tx_packets);
}
```

### Reading Statistics

```c
void print_stats(struct net_stats *stats)
{
    printk("RX packets: %d\n", atomic_read(&stats->rx_packets));
    printk("TX packets: %d\n", atomic_read(&stats->tx_packets));
}
```

### Why Atomics Are Critical

Network drivers often run on multiple CPUs simultaneously through mechanisms such as **NAPI** and **interrupt handling**.

Atomic counters allow the kernel to maintain accurate statistics without requiring locks that would slow down packet processing.

---

# Atomics in Memory Management

Memory management is another subsystem where atomics are heavily used. One important example is **reference counting for memory pages**.

Each physical memory page in the kernel maintains a reference count indicating how many users currently reference that page.

This prevents pages from being freed while still in use.

A simplified representation:

```c
#include <linux/atomic.h>

struct page {
    atomic_t refcount;
};
```

### Incrementing Page Reference

```c
void get_page(struct page *p)
{
    atomic_inc(&p->refcount);
}
```

### Releasing Page Reference

```c
void put_page(struct page *p)
{
    if (atomic_dec_and_test(&p->refcount)) {
        printk("Page can be freed\n");
    }
}
```

### Explanation

The function `atomic_dec_and_test()` performs two operations atomically:

1. Decrements the counter
    
2. Checks whether the counter reached zero
    

If the count reaches zero, the page is no longer used and can safely be reclaimed.

This pattern is critical for preventing **use-after-free memory errors**.

---

# Atomics in Kernel Object Lifetime Management

Many kernel objects use atomic reference counting to manage their lifetime.

A simplified example:

```c
#include <linux/atomic.h>

struct kobject_example {
    atomic_t refcount;
};
```

### Acquire Reference

```c
void kobj_get(struct kobject_example *obj)
{
    atomic_inc(&obj->refcount);
}
```

### Release Reference

```c
void kobj_put(struct kobject_example *obj)
{
    if (atomic_dec_and_test(&obj->refcount)) {
        printk("Object destroyed\n");
    }
}
```

This pattern appears widely in the kernel for objects such as:

- file descriptors
    
- network sockets
    
- device structures
    
- kernel modules
    

---

# Atomic Bit Operations

In addition to integer atomics, the Linux kernel provides **atomic bit operations** used for state flags.

Example structure:

```c
struct device_state {
    unsigned long flags;
};
```

### Set a Flag

```c
set_bit(0, &dev->flags);
```

### Clear a Flag

```c
clear_bit(0, &dev->flags);
```

### Test a Flag

```c
if (test_bit(0, &dev->flags))
    printk("Device active\n");
```

These operations are implemented using atomic CPU instructions to ensure safe concurrent modification of bit fields.

---

# Why the Kernel Prefers Atomics

Atomics are widely used in the kernel because they provide:

### Extremely Low Overhead

Atomic operations avoid expensive context switches.

### Scalability

Atomic primitives allow multiple CPUs to update shared state without serializing through locks.

### Lock-Free Algorithms

Many kernel components rely on lock-free or low-lock designs to maximize throughput.

---

# Limitations of Atomics

Although atomics are powerful, they cannot replace locks in all situations.

Atomics work best when:

- modifying a single variable
    
- performing simple updates
    
- maintaining counters or flags
    

Locks are still required when:

- multiple data structures must be updated together
    
- complex invariants must be preserved
    
- operations involve large critical sections
    

Thus, atomics are used as **fine-grained synchronization tools**, while locks provide **broader protection**.

---

# Conclusion

Atomic operations form a critical part of the Linux kernel’s concurrency model. They allow multiple CPUs to safely update shared variables without relying on expensive locking mechanisms.

Real kernel subsystems such as the scheduler, networking stack, and memory manager rely heavily on atomics to maintain counters, track object lifetimes, and manage system state efficiently.

By combining atomic primitives with careful design, the Linux kernel achieves both high performance and correctness in a highly parallel execution environment.

---

If you want, I can also help you create a **very clean final structure for your notes**:

**Atomics (complete learning path)**

1. What Are Atomics
    
2. CPU Atomic Instructions
    
3. Linux Kernel Atomic APIs
    
4. Compare-and-Swap
    
5. The ABA Problem
    
6. Practical Kernel Usage
    
7. Real Kernel Source Examples
    

Then your next section would naturally become:

**Memory Ordering**

1. CPU Reordering
    
2. Acquire/Release
    
3. Memory Barriers
    
4. Linux Barrier APIs
    
5. Real Kernel Barrier Usage
    

That structure is **almost identical to how kernel concurrency is taught to kernel developers**.