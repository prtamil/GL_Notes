## Modern C11 Atomics: Language-Level Abstraction Over CPU Atomics

### Introduction

Earlier we explored how **CPUs implement atomic instructions** and how the Linux kernel exposes them through primitives such as `atomic_t`, `cmpxchg`, and memory barriers. While these mechanisms are powerful, they are **hardware-specific** and difficult to use directly in portable applications.

To solve this problem, the C language introduced a standardized concurrency model in **C11** through the header:

```
<stdatomic.h>
```

C11 atomics provide a **portable abstraction over hardware atomic instructions and memory ordering rules**. Instead of writing architecture-specific assembly or kernel primitives, programmers can use standardized atomic types and operations that map internally to the appropriate CPU instructions and memory fences.

Conceptually, C11 atomics sit between the **language and the hardware**.

```
C Program
   ↓
C11 Atomic API
   ↓
Compiler mapping
   ↓
CPU atomic instructions
   ↓
Hardware memory model
```

For example:

```
atomic_fetch_add()
```

may compile to:

```
LOCK XADD   (x86)
LDXR/STXR   (ARM)
AMOADD      (RISC-V)
```

This design allows concurrent programs to remain **portable while still achieving lock-free performance**.

---

# Atomic Types in C11

C11 introduces atomic versions of normal C types. These ensure that operations on the variable are performed **atomically**.

Common atomic types:

```
atomic_bool
atomic_char
atomic_int
atomic_long
atomic_uint
atomic_uint64_t
atomic_size_t
```

Example:

```c
#include <stdio.h>
#include <stdatomic.h>

atomic_int counter = 0;

int main() {

    atomic_store(&counter, 10);

    int value = atomic_load(&counter);

    printf("counter = %d\n", value);

    return 0;
}
```

Here:

```
atomic_store()
atomic_load()
```

guarantee **atomic access** even when multiple threads access the variable simultaneously.

---

# Atomic Initialization

Atomic variables can be initialized using:

```
atomic_init()
```

Example:

```c
#include <stdio.h>
#include <stdatomic.h>

int main() {

    atomic_int counter;

    atomic_init(&counter, 5);

    printf("counter = %d\n", atomic_load(&counter));

    return 0;
}
```

This ensures the variable begins with a **well-defined atomic state**.

---

# Atomic Load and Store

The most basic atomic operations are **load** and **store**.

### API

```
atomic_load()
atomic_store()
```

These operations read or write values atomically.

Example:

```c
#include <stdio.h>
#include <stdatomic.h>
#include <pthread.h>

atomic_int shared_value = 0;

void* writer(void* arg) {

    atomic_store(&shared_value, 100);

    return NULL;
}

void* reader(void* arg) {

    int value = atomic_load(&shared_value);

    printf("Read value: %d\n", value);

    return NULL;
}

int main() {

    pthread_t t1, t2;

    pthread_create(&t1, NULL, writer, NULL);
    pthread_create(&t2, NULL, reader, NULL);

    pthread_join(t1, NULL);
    pthread_join(t2, NULL);

    return 0;
}
```

This ensures that concurrent reads and writes occur safely.

---

# Atomic Read-Modify-Write Operations

Many synchronization algorithms require operations that **read and modify a value atomically**.

C11 provides several **read-modify-write (RMW)** operations.

Common ones:

```
atomic_fetch_add()
atomic_fetch_sub()
atomic_fetch_or()
atomic_fetch_and()
atomic_fetch_xor()
atomic_exchange()
```

These operations guarantee that the read and update occur **as a single indivisible operation**.

---

## Example: Atomic Counter

```c
#include <stdio.h>
#include <stdatomic.h>
#include <pthread.h>

atomic_int counter = 0;

void* increment(void* arg) {

    for (int i = 0; i < 100000; i++) {

        atomic_fetch_add(&counter, 1);

    }

    return NULL;
}

int main() {

    pthread_t t1, t2;

    pthread_create(&t1, NULL, increment, NULL);
    pthread_create(&t2, NULL, increment, NULL);

    pthread_join(t1, NULL);
    pthread_join(t2, NULL);

    printf("Final counter: %d\n", atomic_load(&counter));

    return 0;
}
```

Without atomic operations, this program would suffer from **race conditions** and produce incorrect results.

---

# Atomic Exchange

The `atomic_exchange()` operation replaces a value atomically and returns the previous value.

API:

```
atomic_exchange()
```

Example:

```c
#include <stdio.h>
#include <stdatomic.h>

int main() {

    atomic_int lock = 0;

    int old = atomic_exchange(&lock, 1);

    printf("Old value = %d\n", old);
    printf("New value = %d\n", atomic_load(&lock));

    return 0;
}
```

This operation is often used to implement **spinlocks**.

---

# Compare-and-Swap in C11

The most important primitive in lock-free programming is **Compare-and-Swap (CAS)**.

C11 provides:

```
atomic_compare_exchange_strong()
atomic_compare_exchange_weak()
```

CAS compares a variable with an expected value and replaces it if the values match.

---

## Complete Example: CAS Loop

```c
#include <stdio.h>
#include <stdatomic.h>

int main() {

    atomic_int value = 10;

    int expected = 10;
    int desired = 20;

    if (atomic_compare_exchange_strong(&value, &expected, desired)) {

        printf("CAS succeeded\n");

    } else {

        printf("CAS failed\n");

    }

    printf("Final value = %d\n", atomic_load(&value));

    return 0;
}
```

Behavior:

```
if value == expected
    value = desired
else
    expected = actual_value
```

CAS is the **foundation of lock-free data structures**.

---

# Memory Ordering in C11 Atomics

C11 atomics also allow programmers to control **memory ordering behavior**.

Memory ordering specifies how operations appear to execute across threads.

C11 defines several ordering modes.

```
memory_order_relaxed
memory_order_acquire
memory_order_release
memory_order_acq_rel
memory_order_seq_cst
```

These correspond closely to the ordering models we previously studied.

---

# Example: Acquire and Release

Producer-consumer synchronization can be implemented using acquire and release ordering.

```c
#include <stdio.h>
#include <stdatomic.h>
#include <pthread.h>

atomic_int ready = 0;
int data = 0;

void* producer(void* arg) {

    data = 123;

    atomic_store_explicit(&ready, 1, memory_order_release);

    return NULL;
}

void* consumer(void* arg) {

    while (atomic_load_explicit(&ready, memory_order_acquire) == 0)
        ;

    printf("Data = %d\n", data);

    return NULL;
}

int main() {

    pthread_t p, c;

    pthread_create(&p, NULL, producer, NULL);
    pthread_create(&c, NULL, consumer, NULL);

    pthread_join(p, NULL);
    pthread_join(c, NULL);

    return 0;
}
```

Guarantee:

```
producer writes data
      ↓
release store
      ↓
acquire load
      ↓
consumer reads data
```

This establishes a **happens-before relationship**.

---

# Sequential Consistency in C11

The strongest ordering mode is:

```
memory_order_seq_cst
```

Example:

```c
#include <stdio.h>
#include <stdatomic.h>

atomic_int x = 0;

int main() {

    atomic_store_explicit(&x, 1, memory_order_seq_cst);

    int value = atomic_load_explicit(&x, memory_order_seq_cst);

    printf("Value = %d\n", value);

    return 0;
}
```

This enforces **global ordering of all sequentially consistent operations**.

---

# Relationship to CPU Instructions

C11 atomic operations are compiled into hardware instructions depending on the architecture.

Examples:

|C11 Operation|x86|ARM|RISC-V|
|---|---|---|---|
|atomic_fetch_add|LOCK XADD|LDAXR/STXR|AMOADD|
|atomic_exchange|XCHG|SWP|AMOSWAP|
|CAS|CMPXCHG|LDAXR/STXR loop|AMOCAS|
|acquire load|normal load|LDAR|acquire load|
|release store|normal store|STLR|release store|

The compiler selects the correct implementation based on the **target architecture and memory model**.

---

# Lock-Free Guarantee

C11 provides a way to check whether an atomic type is **lock-free**.

API:

```
atomic_is_lock_free()
```

Example:

```c
#include <stdio.h>
#include <stdatomic.h>

int main() {

    atomic_int x;

    if (atomic_is_lock_free(&x)) {

        printf("Atomic operations are lock-free\n");

    } else {

        printf("Atomic operations use locks internally\n");

    }

    return 0;
}
```

Most modern CPUs provide lock-free atomics for basic types.

---

# Conclusion

C11 atomics provide a standardized way to write concurrent programs using atomic operations and well-defined memory ordering semantics. They abstract the complexity of CPU instructions and memory models while still allowing developers to build high-performance lock-free algorithms.

Using `<stdatomic.h>`, programmers can safely perform atomic loads, stores, read-modify-write operations, and compare-and-swap without relying on architecture-specific assembly or kernel primitives. At the same time, memory ordering options such as relaxed, acquire, release, and sequential consistency allow developers to precisely control how memory operations become visible across threads.

By combining atomic operations with explicit memory ordering rules, C11 provides a powerful foundation for building portable and efficient concurrent systems.