
# Practical Kernel Usage of Atomics

## Introduction

Atomic operations are one of the most fundamental synchronization primitives used inside the Linux kernel. Because the kernel executes concurrently on many CPU cores, different parts of the kernel may access and modify shared data structures at the same time.

Using ordinary memory operations in such situations can lead to **race conditions**, where multiple threads overwrite each other's updates or observe inconsistent state.

To avoid this, the Linux kernel provides **atomic primitives** that guarantee safe concurrent modification of shared variables. These primitives are built on top of CPU atomic instructions and allow kernel code to update shared data without using heavier synchronization mechanisms such as mutexes.

Atomic operations are widely used in the kernel for tasks such as:

- reference counting
    
- resource tracking
    
- lock implementations
    
- state flags
    
- performance counters
    
- lock-free algorithms
    

Understanding these practical uses reveals why atomics are essential for efficient kernel design.

---

# Atomic Reference Counting

One of the most common uses of atomics in the Linux kernel is **reference counting**.

Reference counting ensures that shared objects are not freed while still in use.

Each object maintains a counter representing the number of active users. When a new user obtains a reference, the counter increases. When a user releases the object, the counter decreases.

If the counter reaches zero, the object can safely be freed.

---

## Example: Kernel Object Reference Counter

```c
#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/init.h>
#include <linux/atomic.h>

struct my_object {
    atomic_t refcount;
    int data;
};

static struct my_object obj;

void object_get(struct my_object *o)
{
    atomic_inc(&o->refcount);
}

void object_put(struct my_object *o)
{
    if (atomic_dec_and_test(&o->refcount)) {
        printk("Object can now be freed\n");
    }
}

static int __init refcount_example_init(void)
{
    atomic_set(&obj.refcount, 1);
    obj.data = 100;

    printk("Initial reference count: %d\n",
           atomic_read(&obj.refcount));

    object_get(&obj);
    printk("After get: %d\n", atomic_read(&obj.refcount));

    object_put(&obj);
    object_put(&obj);

    return 0;
}

static void __exit refcount_example_exit(void)
{
    printk("Reference counter example exit\n");
}

module_init(refcount_example_init);
module_exit(refcount_example_exit);

MODULE_LICENSE("GPL");
```

### Explanation

Important atomic functions used:

```
atomic_set()
atomic_inc()
atomic_dec_and_test()
atomic_read()
```

`atomic_dec_and_test()` decreases the counter and checks whether it reached zero.

This pattern appears throughout the kernel in structures such as:

- file descriptors
    
- network sockets
    
- kernel objects
    

---

# Atomic Counters for Statistics

Another common use of atomics is maintaining **kernel statistics counters**.

Multiple CPUs may update these counters simultaneously, so atomic operations ensure correctness.

---

## Example: Packet Counter

```c
#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/init.h>
#include <linux/atomic.h>

static atomic_t packet_count;

void receive_packet(void)
{
    atomic_inc(&packet_count);
}

static int __init counter_example_init(void)
{
    atomic_set(&packet_count, 0);

    receive_packet();
    receive_packet();
    receive_packet();

    printk("Packets received: %d\n",
           atomic_read(&packet_count));

    return 0;
}

static void __exit counter_example_exit(void)
{
    printk("Counter example exit\n");
}

module_init(counter_example_init);
module_exit(counter_example_exit);

MODULE_LICENSE("GPL");
```

### Why Atomics Are Needed

Without atomics, two CPUs updating the counter could cause lost updates:

```
CPU1 reads 5
CPU2 reads 5
CPU1 writes 6
CPU2 writes 6
```

The correct result should be **7**.

Atomic increment prevents this race condition.

---

# Atomic Flags

Atomics are often used to manage **shared state flags**.

For example, a subsystem may need to track whether a task has already been scheduled or processed.

---

## Example: One-Time Initialization Flag

```c
#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/init.h>
#include <linux/atomic.h>

static atomic_t init_flag = ATOMIC_INIT(0);

void initialize_resource(void)
{
    if (atomic_cmpxchg(&init_flag, 0, 1) == 0) {
        printk("Resource initialized\n");
    } else {
        printk("Resource already initialized\n");
    }
}

static int __init flag_example_init(void)
{
    initialize_resource();
    initialize_resource();

    return 0;
}

static void __exit flag_example_exit(void)
{
    printk("Flag example exit\n");
}

module_init(flag_example_init);
module_exit(flag_example_exit);

MODULE_LICENSE("GPL");
```

### Explanation

`atomic_cmpxchg()` ensures that initialization happens only once.

Operation:

```
if init_flag == 0
    set to 1
else
    do nothing
```

This prevents multiple CPUs from initializing the same resource simultaneously.

---

# Atomic Spinlocks

Although the kernel provides dedicated spinlock primitives, the underlying concept can be implemented using atomic operations.

---

## Example: Simple Spinlock Using Atomics

```c
#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/init.h>
#include <linux/atomic.h>

static atomic_t lock = ATOMIC_INIT(0);

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

static int __init spinlock_example_init(void)
{
    spin_lock_example();

    printk("Critical section entered\n");

    spin_unlock_example();

    return 0;
}

static void __exit spinlock_example_exit(void)
{
    printk("Spinlock example exit\n");
}

module_init(spinlock_example_init);
module_exit(spinlock_example_exit);

MODULE_LICENSE("GPL");
```

### Lock State

```
0 → unlocked
1 → locked
```

Only one CPU can change the value from `0` to `1`.

---

# Atomic Resource Allocation

Atomics are also useful for **generating unique identifiers**.

---

## Example: Unique ID Generator

```c
#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/init.h>
#include <linux/atomic.h>

static atomic_t next_id;

int allocate_id(void)
{
    return atomic_fetch_add(1, &next_id);
}

static int __init id_example_init(void)
{
    atomic_set(&next_id, 0);

    printk("ID1: %d\n", allocate_id());
    printk("ID2: %d\n", allocate_id());
    printk("ID3: %d\n", allocate_id());

    return 0;
}

static void __exit id_example_exit(void)
{
    printk("ID example exit\n");
}

module_init(id_example_init);
module_exit(id_example_exit);

MODULE_LICENSE("GPL");
```

Each call returns a unique identifier even when multiple CPUs allocate IDs simultaneously.

---

# When the Kernel Uses Atomics Instead of Locks

Atomics are preferred when:

```
the shared data is small
the operation is simple
performance is critical
contention is low
```

Locks are preferred when:

```
multiple variables must be updated together
the critical section is large
complex invariants must be maintained
```

Thus, atomics provide **fine-grained synchronization**, while locks provide **coarse-grained synchronization**.

---

# Performance Benefits

Atomic operations are significantly faster than kernel locks.

Approximate cost:

```
atomic instruction     ~ 10–50 CPU cycles
spinlock acquisition   ~ 100+ cycles
mutex lock             ~ 1000+ cycles
context switch         ~ 10,000+ cycles
```

Because of this, atomics are heavily used in performance-critical kernel paths.

---

# Summary

Atomic operations are a fundamental building block for concurrency in the Linux kernel. They allow shared variables to be safely updated across multiple CPUs without requiring heavyweight synchronization mechanisms.

In practice, atomics are used for reference counting, statistics counters, state flags, spinlocks, and resource allocation. These operations rely on CPU atomic instructions but are exposed through kernel APIs such as `atomic_inc`, `atomic_dec`, `atomic_cmpxchg`, and `atomic_fetch_add`.

By combining atomic operations with careful design, the Linux kernel achieves both **correctness and high performance** in highly concurrent environments.

---

If you'd like, I can also write one more **very interesting section for your notes**:

**“Real Linux Kernel Source Examples of Atomics (scheduler, networking, and memory management)”**

That shows **actual snippets from the kernel source tree**, which is extremely helpful when studying kernel internals.