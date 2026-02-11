We replace:

- `atomic_int` → `volatile int`
    
- `atomic_compare_exchange_strong` → `__sync_bool_compare_and_swap`
    
- `atomic_store` → `__sync_lock_release` or barrier + store
    
- `atomic_load` → safe volatile read or CAS trick
    
- Memory ordering → implicit full fences from `__sync_*`
    

These intrinsics are **sequentially consistent** and were widely used before C11.

```c
#define _GNU_SOURCE
#include <sched.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/syscall.h>
#include <linux/futex.h>
#include <sys/wait.h>

#define STACK_SIZE 1024*1024
#define ITERATIONS 100000

/* -------- Shared State -------- */

volatile int lock_var = 0;
volatile int thread_done = 0;
int counter = 0;

/* -------- FUTEX WRAPPERS -------- */

int futex_wait(volatile int *addr, int expected) {
    return syscall(SYS_futex, addr, FUTEX_WAIT, expected, NULL, NULL, 0);
}

int futex_wake(volatile int *addr) {
    return syscall(SYS_futex, addr, FUTEX_WAKE, 1, NULL, NULL, 0);
}

/* -------- FUTEX LOCK (CAS using GCC intrinsic) -------- */

void lock() {
    while (1) {
        // Try to acquire lock: CAS 0 -> 1
        if (__sync_bool_compare_and_swap(&lock_var, 0, 1))
            return;

        // Failed, sleep in kernel
        futex_wait(&lock_var, 1);
    }
}

void unlock() {
    __sync_synchronize();  // full memory barrier (release semantics)
    lock_var = 0;
    futex_wake(&lock_var);
}

/* -------- THREAD FUNCTION -------- */

int thread_func(void *arg) {
    for (int i = 0; i < ITERATIONS; i++) {
        lock();
        counter++;
        unlock();
    }

    // Mark thread as done
    __sync_synchronize();   // ensure counter updates visible
    thread_done = 1;
    futex_wake(&thread_done);

    return 0;
}

/* -------- MAIN -------- */

int main() {
    void *stack = malloc(STACK_SIZE);
    if (!stack) {
        perror("malloc");
        exit(1);
    }

    void *stack_top = (char*)stack + STACK_SIZE;

    // Create thread using clone()
    int flags = CLONE_VM | CLONE_FS | CLONE_FILES | CLONE_SIGHAND | CLONE_THREAD;

    clone(thread_func, stack_top, flags, NULL);

    // Main thread also increments
    for (int i = 0; i < ITERATIONS; i++) {
        lock();
        counter++;
        unlock();
    }

    // JOIN: wait until thread_done becomes 1
    while (1) {
        if (__sync_bool_compare_and_swap(&thread_done, 1, 1))
            break;

        futex_wait(&thread_done, 0);
    }

    printf("Final counter = %d\n", counter);

    free(stack);
    return 0;
}


```

# What Each Replacement Means (Mental Mapping)

### 1) CAS replacement

Old C11:

```c
atomic_compare_exchange_strong(&lock_var, &expected, 1)

```

Now:

```c
__sync_bool_compare_and_swap(&lock_var, 0, 1)

```

This is a direct hardware CAS.

---

### 2) atomic_store replacement

Old:

```js
atomic_store(&lock_var, 0)

```

Now:

```js
__sync_synchronize();
lock_var = 0;

```

Barrier ensures:

All writes inside critical section are visible before unlock.

This mimics **release semantics**.

---

### 3) atomic_load replacement

Old:

```c
atomic_load(&thread_done)

```

Now:

```c
__sync_bool_compare_and_swap(&thread_done, 1, 1)

```

Why this trick?

Because:

- CAS acts as an atomic read + full fence
    
- It does NOT change value
    
- But guarantees visibility
    

Equivalent to a safe atomic read.

---

# Why `volatile int` is used

Not for atomicity.

Only to prevent compiler from:

- Removing reads
    
- Caching variable in register
    

Real atomicity comes from:

```c
__sync_* operations

```

---

# Memory Model of `__sync_*`

All `__sync` intrinsics provide:

- Full memory fence
    
- Sequential consistency
    
- Strong ordering
    

So they are simpler but slower than C11 atomics.

---

# What is Happening Internally

Your lock:

```c
lock():
  CAS(lock_var, 0→1)
  if fail → futex_wait()

unlock():
  barrier
  lock_var = 0
  futex_wake()

```

Your join:

```js
worker:
  thread_done = 1
  futex_wake()

main:
  while(thread_done != 1)
      futex_wait()

```

This is exactly how:

- pthread_mutex
    
- pthread_join
    

were implemented historically.

---

# Historical Reality

Before 2011:

People wrote production systems using:

- `__sync_bool_compare_and_swap`
    
- `__sync_fetch_and_add`
    
- `__sync_synchronize`
    

Including:

- JVM internals
    
- Database engines
    
- Lock-free queues
    
- Kernel-adjacent code
    

C11 atomics only standardized this.

---

# Deep Insight

You now have 3 layers visible:

```js
CPU CAS instruction
     ↑
GCC __sync builtin
     ↑
Your futex lock
     ↑
Your counter

```

That is nearly raw hardware-level concurrency.