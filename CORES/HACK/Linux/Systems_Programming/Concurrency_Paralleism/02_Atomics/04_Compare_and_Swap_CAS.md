# Compare-and-Swap (CAS)

## Introduction

Concurrent systems allow multiple threads or processors to execute simultaneously and access shared memory. When multiple CPUs attempt to modify the same memory location, race conditions can occur unless special synchronization mechanisms are used.

One of the most important primitives used to build safe concurrent algorithms is **Compare-and-Swap (CAS)**.

Compare-and-Swap is an atomic operation that compares the value stored at a memory location with an expected value. If the values match, the memory location is updated with a new value. If they do not match, the update fails and the memory remains unchanged.

The key property of CAS is that **the comparison and update occur as a single atomic operation**. No other CPU can interfere between the comparison and the update.

Because of this property, CAS is widely used to build:

- lock-free algorithms
    
- spinlocks
    
- concurrent data structures
    
- reference counters
    
- kernel synchronization primitives
    

Operating systems such as Linux rely heavily on CAS to implement high-performance concurrency mechanisms.

---

# Conceptual Behavior of CAS

The logical behavior of Compare-and-Swap can be described as:

```
if (*ptr == expected)
    *ptr = new_value
```

If the comparison succeeds, the update occurs. If the comparison fails, the value is not modified.

In practice, CAS also returns the previous value so the caller can determine whether the update succeeded.

---

# Pseudocode Representation

A simplified conceptual implementation looks like this:

```
function compare_and_swap(ptr, expected, new):
    if *ptr == expected:
        *ptr = new
        return true
    else:
        return false
```

However, this pseudocode is not safe in concurrent environments. The real CAS operation must be implemented using **CPU atomic instructions**.

---

# Compare-and-Swap on x86 CPUs

On x86 processors, CAS is implemented using the **CMPXCHG instruction**.

Instruction format:

```
CMPXCHG destination, source
```

Registers involved:

```
destination → memory location
source      → new value
EAX/RAX     → expected value
```

Operation performed:

```
if (destination == EAX)
    destination = source
else
    EAX = destination
```

Meaning:

- If the memory value equals the expected value stored in `EAX`, the new value is written.
    
- If the values differ, the memory value is copied into `EAX`.
    

---

# Ensuring Atomicity with the LOCK Prefix

To guarantee atomic behavior across multiple processors, CAS is typically used with the **LOCK prefix**.

Example:

```
lock cmpxchg [memory], register
```

The `lock` prefix ensures that:

- the instruction executes atomically
    
- other CPUs cannot modify the memory location during the operation
    

---

# Example: CAS in x86 Assembly

Example program that attempts to update a value if it matches an expected value.

```
section .data
value dd 10

section .text
global cas_example

cas_example:
    mov eax, 10
    mov ebx, 20

    lock cmpxchg [value], ebx

    ret
```

Explanation:

```
EAX = expected value
EBX = new value
```

Operation:

```
if value == 10
    value becomes 20
else
    EAX becomes value
```

---

# CAS Retry Loop Example (x86)

CAS often appears inside loops because the operation may fail if another thread updates the value first.

```
section .data
counter dd 0

section .text
global increment

increment:
retry:
    mov eax, [counter]
    mov ebx, eax
    add ebx, 1

    lock cmpxchg [counter], ebx
    jne retry

    ret
```

Steps:

1. Read current counter value
    
2. Compute new value
    
3. Attempt update using CAS
    
4. Retry if another CPU changed the value
    

This pattern is the basis of **lock-free algorithms**.

---

# Compare-and-Swap in the Linux Kernel

The Linux kernel provides CAS through the function:

```
atomic_cmpxchg()
```

Prototype:

```
int atomic_cmpxchg(atomic_t *v, int old, int new);
```

Behavior:

```
if v == old
    v = new
return previous value
```

The return value allows the caller to detect whether the operation succeeded.

---

# Example: Basic CAS in Linux Kernel

```
#include <linux/atomic.h>

atomic_t value;

void cas_example(void)
{
    int prev;

    atomic_set(&value, 10);

    prev = atomic_cmpxchg(&value, 10, 20);

    printk("previous value = %d\n", prev);
    printk("current value = %d\n", atomic_read(&value));
}
```

Output:

```
previous value = 10
current value = 20
```

---

# Example: CAS Failure Case

```
#include <linux/atomic.h>

atomic_t value;

void cas_fail_example(void)
{
    int prev;

    atomic_set(&value, 5);

    prev = atomic_cmpxchg(&value, 10, 20);

    printk("previous value = %d\n", prev);
    printk("current value = %d\n", atomic_read(&value));
}
```

Output:

```
previous value = 5
current value = 5
```

Explanation:

The comparison fails because the expected value was incorrect.

---

# Example: Atomic Increment Using CAS

```
#include <linux/atomic.h>

atomic_t counter;

void cas_increment(void)
{
    int old;
    int new;

    do {
        old = atomic_read(&counter);
        new = old + 1;
    } while (atomic_cmpxchg(&counter, old, new) != old);
}
```

Explanation:

1. Read current value
    
2. Compute new value
    
3. Attempt CAS update
    
4. Retry if another CPU changed the value
    

---

# Example: Simple Spinlock Using CAS

```
#include <linux/atomic.h>

atomic_t lock = ATOMIC_INIT(0);

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

Lock state:

```
0 → unlocked
1 → locked
```

Only one thread can change `0 → 1`.

---

# The ABA Problem in Compare-and-Swap

Although CAS is powerful, it suffers from a subtle issue known as the **ABA problem**.

The ABA problem occurs when a memory value changes from:

```
A → B → A
```

From the perspective of CAS, the value appears unchanged because it still equals `A`. However, the value actually changed in between.

This can cause incorrect behavior in lock-free algorithms.

---

# ABA Example Scenario

Consider a lock-free stack.

Thread A reads the stack head:

```
head = A
```

While Thread A is paused:

Thread B performs:

```
pop A
push B
push A
```

The stack head is again `A`.

Thread A resumes and performs CAS:

```
CAS(head, A, next)
```

CAS succeeds because the head is still `A`.

However, the stack structure has changed, which may corrupt the data structure.

---

# Solutions to the ABA Problem

Several techniques exist to solve the ABA problem.

### Version Counters

Attach a version number to the pointer.

Example:

```
(pointer, version)
```

Each update increments the version number.

CAS checks both the pointer and version.

---

### Tagged Pointers

Combine pointer and version bits into one value.

Example:

```
struct tagged_ptr {
    void *ptr;
    int version;
};
```

CAS operates on the entire structure.

---

### Hazard Pointers

Threads mark which memory nodes they are currently accessing. This prevents nodes from being reused while another thread might still reference them.

---

# How Linux Handles ABA

The Linux kernel avoids ABA problems using multiple strategies depending on the subsystem.

Common approaches include:

### Sequence Counters

Linux often uses **sequence counters** or version fields in structures.

Example concept:

```
struct node {
    int value;
    int version;
}
```

CAS checks both the value and version.

---

### Reference Counting

Linux frequently uses **reference counters** to ensure objects are not reused prematurely.

Example:

```
atomic_inc(&obj->refcount);
```

Objects are not freed until the count reaches zero.

---

### Lock-Free Algorithms with Versioning

Some kernel structures include embedded counters to detect modifications.

These mechanisms ensure that ABA problems do not corrupt kernel data structures.

---

# Why CAS Is Important

Compare-and-Swap is one of the most fundamental operations in concurrent programming. It enables the creation of efficient synchronization mechanisms without heavy locking.

CAS is used to implement:

```
spinlocks
lock-free stacks
lock-free queues
reference counters
concurrent hash tables
memory allocators
kernel schedulers
```

Because CAS operates directly at the hardware level, it allows concurrent algorithms to scale efficiently across many CPU cores.

---

# Summary

Compare-and-Swap is a fundamental atomic primitive that allows memory to be updated only if it matches an expected value. CPUs implement CAS through instructions such as `CMPXCHG` on x86 processors, often combined with the `LOCK` prefix to ensure atomic behavior across multiple processors.

The Linux kernel exposes CAS through APIs such as `atomic_cmpxchg`, allowing kernel developers to build safe and efficient concurrent algorithms without writing architecture-specific assembly code.

Although CAS enables powerful lock-free techniques, it introduces challenges such as the ABA problem. The Linux kernel mitigates these issues through techniques like version counters, tagged pointers, and reference counting.

Through these mechanisms, CAS serves as one of the most important building blocks for modern concurrent operating systems.

---

If you'd like, I can also write a **very powerful follow-up essay** that usually comes next in systems notes:

**“Building a Lock-Free Stack Using Compare-and-Swap (with full C implementation)”**

It ties together **CAS, memory ordering, and ABA handling** in a real data structure.