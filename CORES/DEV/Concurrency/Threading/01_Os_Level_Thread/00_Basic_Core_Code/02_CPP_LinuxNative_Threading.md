```cpp
#define _GNU_SOURCE
#include <sched.h>
#include <unistd.h>
#include <sys/syscall.h>
#include <linux/futex.h>
#include <atomic>
#include <iostream>
#include <cstring>
#include <cstdlib>

constexpr int STACK_SIZE = 1024 * 1024;
constexpr int ITERATIONS = 100000;

/* ============================================================
   FUTEX — raw kernel primitive wrapper
   ============================================================ */
struct Futex {
    static int wait(std::atomic<int>* addr, int expected) {
        return syscall(SYS_futex, addr, FUTEX_WAIT, expected, nullptr, nullptr, 0);
    }

    static int wake(std::atomic<int>* addr) {
        return syscall(SYS_futex, addr, FUTEX_WAKE, 1, nullptr, nullptr, 0);
    }
};

/* ============================================================
   FUTEX MUTEX — our own lock abstraction
   (Equivalent to: synchronized / pthread_mutex)
   ============================================================ */
class FutexMutex {
    std::atomic<int> state{0}; // 0 = free, 1 = locked

public:
    void lock() {
        int expected;
        while (true) {
            expected = 0;

            // Fast path: try to acquire lock using CAS
            if (state.compare_exchange_strong(expected, 1))
                return;

            // Slow path: wait in kernel
            Futex::wait(&state, 1);
        }
    }

    void unlock() {
        state.store(0);
        Futex::wake(&state);
    }
};

/* ============================================================
   JOIN FLAG — our own join mechanism
   (Equivalent to pthread_join / Thread.join)
   ============================================================ */
class JoinFlag {
    std::atomic<int> done{0};

public:
    void mark_done() {
        done.store(1);
        Futex::wake(&done);
    }

    void wait_until_done() {
        while (done.load() == 0) {
            Futex::wait(&done, 0);
        }
    }
};

/* ============================================================
   SHARED COUNTER protected by our FutexMutex
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
   THREAD FUNCTION (runs inside clone-created thread)
   ============================================================ */
int thread_func(void* arg) {
    ThreadContext* ctx = static_cast<ThreadContext*>(arg);

    for (int i = 0; i < ITERATIONS; i++) {
        ctx->counter->increment();
    }

    ctx->join_flag->mark_done();
    return 0;
}

/* ============================================================
   CLONE THREAD ABSTRACTION
   (Equivalent to pthread_create)
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

    // Main thread also increments
    for (int i = 0; i < ITERATIONS; i++) {
        counter.increment();
    }

    // Our custom join
    join_flag.wait_until_done();

    std::cout << "Final counter = " << counter.get() << std::endl;
}

```