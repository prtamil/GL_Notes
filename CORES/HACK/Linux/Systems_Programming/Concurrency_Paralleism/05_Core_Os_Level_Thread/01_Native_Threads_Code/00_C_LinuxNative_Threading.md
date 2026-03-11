```c
#define _GNU_SOURCE
#include <sched.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/syscall.h>
#include <linux/futex.h>
#include <stdatomic.h>
#include <sys/wait.h>

#define STACK_SIZE 1024*1024
#define ITERATIONS 100000

/* -------- Shared State -------- */

atomic_int lock_var = 0;
atomic_int thread_done = 0;
int counter = 0;

/* -------- FUTEX WRAPPERS -------- */

int futex_wait(atomic_int *addr, int expected) {
    return syscall(SYS_futex, addr, FUTEX_WAIT, expected, NULL, NULL, 0);
}

int futex_wake(atomic_int *addr) {
    return syscall(SYS_futex, addr, FUTEX_WAKE, 1, NULL, NULL, 0);
}

/* -------- FUTEX LOCK -------- */

void lock() {
    int expected;
    while (1) {
        expected = 0;
        if (atomic_compare_exchange_strong(&lock_var, &expected, 1))
            return;
        futex_wait(&lock_var, 1);
    }
}

void unlock() {
    atomic_store(&lock_var, 0);
    futex_wake(&lock_var);
}

/* -------- THREAD FUNCTION -------- */

int thread_func(void *arg) {
    for (int i = 0; i < ITERATIONS; i++) {
        lock();
        counter++;
        unlock();
    }

    atomic_store(&thread_done, 1);
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

    void *stack_top = stack + STACK_SIZE;

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
    while (atomic_load(&thread_done) == 0) {
        futex_wait(&thread_done, 0);
    }

    printf("Final counter = %d\n", counter);

    free(stack);
    return 0;
}

```