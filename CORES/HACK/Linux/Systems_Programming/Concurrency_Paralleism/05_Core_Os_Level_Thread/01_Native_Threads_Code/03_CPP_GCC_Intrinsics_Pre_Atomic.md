Below is your same program rewritten **without C11/C++11 atomics**.  
We replace:

- `std::atomic`
    
- `compare_exchange_strong`
    
- `.store() / .load()`
    

with **pre-C11 GCC intrinsics**:

- `__sync_bool_compare_and_swap` → CAS
    
- `__sync_lock_test_and_set` → atomic exchange
    
- `__sync_lock_release` → release store
    
- `__sync_synchronize()` → full memory barrier
    

These existed long before C11 and map directly to CPU instructions.

This is historically how Linux user-space locks were written.

# Quick Overview of `__sync` GCC Intrinsics (Pre-C11)

These are compiler-provided atomic primitives.

They provide:

- Atomic operations
    
- Full memory barriers (sequentially consistent)
    
- Cross-core visibility
    

Key ones:

### CAS (Compare-And-Swap)

```c
__sync_bool_compare_and_swap(ptr, expected, newval)

```

Atomically:

```c
if (*ptr == expected) {
    *ptr = newval;
    return true;
}
return false;

```

### Atomic exchange

```c
__sync_lock_test_and_set(ptr, value)

```

Sets and returns old value atomically.

### Release store

```c
__sync_lock_release(ptr)

```

Equivalent to:

`store + release barrier`

### Full fence

```c
__sync_synchronize()

```

Prevents any reordering across it.

---

# Your Code Rewritten (NO C11 atomics)

```cpp
#define _GNU_SOURCE
#include <sched.h>
#include <unistd.h>
#include <sys/syscall.h>
#include <linux/futex.h>
#include <iostream>
#include <cstring>
#include <cstdlib>

constexpr int STACK_SIZE = 1024 * 1024;
constexpr int ITERATIONS = 100000;

/* ============================================================
   FUTEX — raw kernel primitive wrapper
   ============================================================ */
struct Futex {
    static int wait(int* addr, int expected) {
        return syscall(SYS_futex, addr, FUTEX_WAIT, expected, nullptr, nullptr, 0);
    }

    static int wake(int* addr) {
        return syscall(SYS_futex, addr, FUTEX_WAKE, 1, nullptr, nullptr, 0);
    }
};

/* ============================================================
   FUTEX MUTEX — built using GCC CAS intrinsics
   ============================================================ */
class FutexMutex {
    volatile int state = 0; // 0 = free, 1 = locked

public:
    void lock() {
        while (true) {
            // Fast path: CAS
            if (__sync_bool_compare_and_swap(&state, 0, 1))
                return;

            // Slow path: sleep in kernel
            Futex::wait((int*)&state, 1);
        }
    }

    void unlock() {
        __sync_synchronize();   // full memory barrier
        state = 0;              // release lock
        Futex::wake((int*)&state);
    }
};

/* ============================================================
   JOIN FLAG — manual join mechanism
   ============================================================ */
class JoinFlag {
    volatile int done = 0;

public:
    void mark_done() {
        __sync_synchronize();
        done = 1;
        Futex::wake((int*)&done);
    }

    void wait_until_done() {
        while (true) {
            if (__sync_bool_compare_and_swap(&done, 1, 1))
                return;

            Futex::wait((int*)&done, 0);
        }
    }
};

/* ============================================================
   SHARED COUNTER protected by FutexMutex
   ============================================================ */
class Counter {
    int value = 0;
    FutexMutex mutex;

public:
    void increment() {
        mutex.lock();
        value++;
        mutex.unlock();
    }

    int get() const {
        return value;
    }
};

/* ============================================================
   THREAD CONTEXT
   ============================================================ */
struct ThreadContext {
    Counter* counter;
    JoinFlag* join_flag;
};

/* ============================================================
   THREAD FUNCTION
   ============================================================ */
int thread_func(void* arg) {
    ThreadContext* ctx = (ThreadContext*)arg;

    for (int i = 0; i < ITERATIONS; i++) {
        ctx->counter->increment();
    }

    ctx->join_flag->mark_done();
    return 0;
}

/* ============================================================
   CLONE THREAD ABSTRACTION
   ============================================================ */
class CloneThread {
    void* stack;

public:
    CloneThread() {
        stack = std::malloc(STACK_SIZE);
        if (!stack) {
            std::perror("malloc");
            std::exit(1);
        }
    }

    ~CloneThread() {
        std::free(stack);
    }

    void start(int (*fn)(void*), void* arg) {
        void* stack_top = (char*)stack + STACK_SIZE;

        int flags =
            CLONE_VM |
            CLONE_FS |
            CLONE_FILES |
            CLONE_SIGHAND |
            CLONE_THREAD;

        clone(fn, stack_top, flags, arg);
    }
};

/* ============================================================
   MAIN
   ============================================================ */
int main() {
    Counter counter;
    JoinFlag join_flag;

    ThreadContext ctx{&counter, &join_flag};

    CloneThread t;
    t.start(thread_func, &ctx);

    for (int i = 0; i < ITERATIONS; i++) {
        counter.increment();
    }

    join_flag.wait_until_done();

    std::cout << "Final counter = " << counter.get() << std::endl;
}

```

# What Changed Conceptually

We replaced:

|C++11 atomic|Old GCC intrinsic|
|---|---|
|compare_exchange|`__sync_bool_compare_and_swap`|
|store()|plain store + barrier|
|load()|CAS trick / volatile read|
|memory_order|implicit full fence|

Important:

`__sync_*` operations are:

- Strong
    
- Sequentially consistent
    
- Slower than modern atomics
    

But simpler.

---

# Key Mental Model

This lock now works like:

```py
lock():
  CAS(state, 0 → 1)
  if fail → futex sleep

unlock():
  barrier
  state = 0
  futex wake

```

Exactly how early pthread mutexes worked internally.

---

# Why the Barrier in unlock()

```c
__sync_synchronize();
state = 0;

```

Ensures:

All writes inside critical section become visible  
BEFORE the lock is released.

This is a manual RELEASE semantic.

---

# Why CAS is Enough

CAS is the single most important primitive in concurrency.

From it you can build:

- Mutex
    
- Spinlock
    
- Semaphore
    
- Thread-safe queues
    
- Lock-free structures
    

Everything.

---

# Historical Note

Before C11:

- Linux kernel
    
- Databases
    
- JVM
    
- Lock-free libraries
    

All used:

```c
__sync_bool_compare_and_swap

```

directly.

C11 just standardized it.

---

# Deep Insight

Your stack is now:

```c
CPU CAS instruction
    ↑
GCC __sync builtins
    ↑
Your FutexMutex
    ↑
Your Counter

```

You are only 1 abstraction layer above hardware.

This is about as "core systems" as user-space can get.