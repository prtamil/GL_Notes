

# Multithreading in Linux: What the OS Actually Provides

Modern applications create and manage many threads, but most programmers interact only with high-level APIs such as **C++ `std::thread`** or **POSIX Threads (`pthread`)**. Internally, these libraries rely on a few powerful **Linux system calls** provided by the kernel.

These system calls allow programs to create threads, allocate memory, synchronize execution, and interact with the scheduler.

Even though multithreading feels complex, the kernel provides only a **small toolkit**. Most threading libraries are simply abstractions built on top of these primitives.

---

# 1. Thread Creation

The most important system call for creating threads is:

```
clone()
```

A newer version also exists:

```
clone3()
```

Unlike traditional process creation (`fork()`), `clone()` allows a program to specify **which resources should be shared** between the parent and the new thread.

For example, threads typically share:

- Memory
    
- File descriptors
    
- Signal handlers
    

When a library like **POSIX Threads (`pthread`)** creates a new thread, it ultimately calls `clone()` with specific flags that make the new execution context behave like a thread instead of a separate process.

So the typical stack looks like this:

```
std::thread
   ↓
pthread_create()
   ↓
clone()
   ↓
Linux kernel creates thread
```

---

# 2. Memory Management

Threads share the same address space, but each thread still needs its **own stack** and sometimes other memory regions.

The kernel provides memory management through these system calls:

```
mmap()
munmap()
mprotect()
```

### mmap()

Used to allocate memory. Thread libraries commonly use it to create **thread stacks**.

Example use cases:

- thread stack allocation
    
- thread-local storage
    
- large memory allocations
    

### munmap()

Used to release memory that was previously allocated with `mmap()`.

### mprotect()

Changes memory protection (read/write/execute). Thread libraries use it to create **guard pages** that detect stack overflows.

---

# 3. Synchronization (The Most Important Primitive)

The most important syscall for synchronization is:

```
futex()
```

Futex stands for **Fast Userspace Mutex**.

It allows threads to synchronize efficiently by combining **user-space locking with kernel assistance**.

The typical workflow is:

1. Threads attempt to acquire a lock in **user space**.
    
2. If the lock is free, they proceed immediately (very fast).
    
3. If the lock is contested, the thread calls `futex()` to sleep in the kernel.
    
4. When another thread releases the lock, it wakes waiting threads using `futex()`.
    

This mechanism powers many higher-level constructs such as:

- mutexes
    
- condition variables
    
- semaphores
    

Libraries like **POSIX Threads (`pthread`)** and **C++ `std::mutex`** rely heavily on `futex()`.

---

# 4. Scheduling Control

Once threads exist, the kernel scheduler decides **which thread runs on the CPU**.

Programs can influence scheduling using several system calls:

```
sched_yield()
sched_setaffinity()
sched_getaffinity()
sched_setscheduler()
```

### sched_yield()

Allows a thread to voluntarily give up the CPU.

### sched_setaffinity()

Pins a thread to specific CPU cores. This is useful for high-performance systems.

Example:

```
run this thread only on CPU core 3
```

### sched_getaffinity()

Retrieves the CPUs a thread is allowed to run on.

### sched_setscheduler()

Changes the scheduling policy. Examples include:

- normal scheduling
    
- real-time scheduling
    
- round-robin scheduling
    

These are used in latency-sensitive systems.

---

# 5. Thread Identification

Each thread needs an identifier. The kernel provides this through:

```
gettid()
```

This returns the **Thread ID (TID)**.

Important distinction:

- **PID** → process identifier
    
- **TID** → thread identifier
    

All threads in a process share the same PID but have **different TIDs**.

---

# 6. Signals and Thread Control

Threads can send signals to each other using:

```
tgkill()
```

This allows a program to send a signal to a **specific thread** rather than the entire process.

Thread libraries use this mechanism for:

- thread cancellation
    
- debugging tools
    
- signal handling
    

---

# 7. Sleeping and Timing

Threads sometimes need to pause execution.

The kernel provides timing syscalls such as:

```
nanosleep()
clock_nanosleep()
```

These allow threads to sleep for very precise time intervals.

---

# 8. Thread Termination

When a thread finishes execution, it eventually calls:

```
exit()
```

In some cases, a process may terminate all threads using:

```
exit_group()
```

Thread libraries manage these details internally.

---

# 9. Thread-Local Storage Support

Thread-local variables require support from the CPU and kernel.

Linux provides mechanisms such as:

```
arch_prctl()
set_thread_area()
```

On x86-64 systems, `arch_prctl()` can set the **FS register**, which points to the thread’s local storage area.

This is how thread-local variables work efficiently.

---

# Summary: Core Syscalls for Multithreading

Although threading looks complex, Linux provides only a **small set of fundamental system calls**.

### Thread Creation

```
clone()
clone3()
```

### Memory Management

```
mmap()
munmap()
mprotect()
```

### Synchronization

```
futex()
```

### Scheduling

```
sched_yield()
sched_setaffinity()
sched_getaffinity()
sched_setscheduler()
```

### Thread Identification and Control

```
gettid()
tgkill()
exit()
exit_group()
```

### Timing

```
nanosleep()
clock_nanosleep()
```

### Thread-Local Storage

```
arch_prctl()
set_thread_area()
```

---

# Final Insight

One fascinating thing about Linux design is that **almost the entire threading ecosystem is built from just three key primitives**:

```
clone()
mmap()
futex()
```

With these three building blocks, libraries implement:

- threads
    
- mutexes
    
- condition variables
    
- thread pools
    
- asynchronous runtimes
    

If you enjoy studying internals and then re-implementing them yourself in **C++**, you are following the same learning path many systems engineers take. It’s a powerful way to truly understand how modern runtimes and operating systems work.