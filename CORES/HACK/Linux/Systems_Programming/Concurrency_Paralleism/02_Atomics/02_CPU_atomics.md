# CPU Atomic Instructions

## Introduction

Modern processors run multiple threads simultaneously across many CPU cores. These threads often share memory and may attempt to read or modify the same memory location at the same time. Without coordination, this leads to inconsistent results and data corruption.

To solve this problem, processors provide **atomic instructions**. An atomic instruction guarantees that a memory operation is performed **as a single indivisible action**. No other processor can observe or interfere with the operation while it is in progress.

Atomic instructions are therefore the **hardware foundation of concurrent programming**. Operating systems, compilers, and programming languages rely on these instructions to implement synchronization primitives such as locks, reference counters, and lock-free data structures.

Understanding CPU atomic instructions helps explain how concurrency works at the lowest level of the system.

---

# The Problem Atomic Instructions Solve

Consider a shared counter increment:

```
counter = counter + 1
```

At the CPU level, this expands into multiple steps:

```
1. Load value from memory
2. Add 1
3. Store result back to memory
```

If two threads execute this sequence simultaneously:

```
Thread A loads 5
Thread B loads 5
Thread A stores 6
Thread B stores 6
```

The final result becomes **6 instead of 7**. This situation is called a **race condition**.

Atomic instructions solve this by ensuring the **entire read–modify–write operation occurs as one indivisible step**.

---

# Categories of CPU Atomic Operations

Most processors provide a small set of atomic primitives from which all synchronization mechanisms are built.

The major atomic operations include:

```
1. Atomic Exchange
2. Compare-And-Swap
3. Fetch-And-Add
4. Atomic Increment / Decrement
5. Test-And-Set
6. Load-Linked / Store-Conditional
```

Although different CPU architectures implement them differently, the conceptual behavior is similar.

---

# 1. Atomic Exchange (XCHG)

Atomic exchange swaps the contents of a memory location with a register value.

Conceptually:

```
temp = *ptr
*ptr = new_value
return temp
```

### Example usage in C-like pseudocode

```c
int lock = 0;

int old = atomic_exchange(&lock, 1);

if (old == 0) {
    // lock acquired
}
```

### Example CPU instruction (x86)

```
xchg eax, [lock]
```

### Example assembly snippet

```
mov eax, 1
xchg eax, [lock]
```

Explanation:

```
eax = 1
swap eax with memory at lock
```

If `lock` was `0`, the thread successfully acquires the lock.

---

# 2. Compare-And-Swap (CMPXCHG)

Compare-and-swap is one of the most powerful atomic operations.

It compares the current value of memory with an expected value. If they match, it replaces the memory value with a new value.

Conceptually:

```
if (*ptr == expected)
    *ptr = new
```

### Example usage

```c
int old;

do {
    old = counter;
} while (!compare_and_swap(&counter, old, old + 1));
```

This retry loop is common in **lock-free algorithms**.

### Example CPU instruction (x86)

```
cmpxchg
```

### Example assembly snippet

```
mov eax, expected
mov ebx, new_value
lock cmpxchg [ptr], ebx
```

Explanation:

```
compare eax with memory
if equal:
    store ebx into memory
else:
    eax = memory value
```

The `lock` prefix ensures atomicity across CPU cores.

---

# 3. Fetch-And-Add (XADD)

Fetch-and-add atomically adds a value to memory and returns the old value.

Conceptually:

```
old = *ptr
*ptr = old + value
return old
```

### Example usage

```c
int id = atomic_fetch_add(&counter, 1);
```

This is commonly used for:

- generating unique IDs
    
- updating counters
    
- work queue indexing
    

### Example CPU instruction

```
xadd
```

### Example assembly snippet

```
mov eax, 1
lock xadd [counter], eax
```

Explanation:

```
eax contains increment value
memory = memory + eax
eax returns previous memory value
```

---

# 4. Atomic Increment / Decrement

Some CPUs support atomic increment or decrement instructions.

Conceptually:

```
*ptr = *ptr + 1
```

### Example usage

```c
atomic_increment(&refcount);
```

This is widely used for **reference counting**.

### Example CPU instructions

```
lock inc
lock dec
```

### Example assembly snippet

```
lock inc [refcount]
```

Explanation:

```
increment memory value atomically
```

---

# 5. Test-And-Set

Test-and-set reads a value and sets it to a new value in a single atomic step.

Conceptually:

```
old = *ptr
*ptr = 1
return old
```

### Example usage (spinlock)

```c
while (test_and_set(&lock)) {
    // spin until lock becomes free
}
```

### Example assembly idea

```
mov eax, 1
xchg eax, [lock]
```

Because `xchg` is atomic on x86, it implements test-and-set.

---

# 6. Load-Linked / Store-Conditional (LL/SC)

Some architectures implement atomics using a pair of instructions:

```
Load-Linked (LL)
Store-Conditional (SC)
```

This works as follows:

1. Load-linked reads memory and marks it.
    
2. Store-conditional attempts to write.
    
3. The store succeeds only if no other processor modified the memory.
    

### Conceptual example

```
loop:
    r1 = LL(addr)
    r1 = r1 + 1
    if SC(addr, r1) fails
        goto loop
```

If another CPU changed the value between the two instructions, the store fails and the loop retries.

---

# Atomic Instructions by Architecture

Although the primitives are similar, each CPU architecture implements them differently.

---

## x86 Atomic Instructions

Common instructions:

```
XCHG
CMPXCHG
XADD
INC / DEC (with LOCK prefix)
```

Example:

```
lock xadd [counter], eax
```

The `lock` prefix ensures exclusive access across processors.

---

## ARM Atomic Instructions

ARM uses **exclusive load/store instructions**:

```
LDXR   (load exclusive)
STXR   (store exclusive)
```

Example pseudo assembly:

```
loop:
    ldxr x0, [addr]
    add x0, x0, #1
    stxr w1, x0, [addr]
    cbnz w1, loop
```

If another CPU modifies the memory, `stxr` fails and the loop retries.

---

## RISC-V Atomic Instructions

RISC-V includes atomic memory operations such as:

```
amoadd
amoswap
amoand
amoor
```

Example:

```
amoadd.w x1, x2, (x3)
```

Meaning:

```
memory[x3] = memory[x3] + x2
x1 = old value
```

RISC-V also supports:

```
lr (load reserved)
sc (store conditional)
```

---

# How CPUs Guarantee Atomicity

Processors ensure atomic behavior using hardware mechanisms such as:

**Cache coherence protocols**

CPU caches coordinate so only one core can modify a cache line during an atomic operation.

**Cache line locking**

Atomic instructions temporarily lock the memory cache line.

**Bus locking**

Older processors locked the entire memory bus during atomic operations.

These mechanisms ensure that no other CPU core can interfere with the operation while it executes.

---

# Why CPU Atomic Instructions Matter

Atomic instructions are the **lowest-level synchronization primitive** in modern systems. Everything built for concurrency relies on them.

Examples include:

```
spinlocks
mutex implementations
reference counting
lock-free data structures
kernel schedulers
memory allocators
```

Programming languages such as C, C++, Rust, and Java all rely on these instructions to implement their atomic libraries.

---

# Summary

CPU atomic instructions provide the fundamental mechanism that allows multiple processors to safely modify shared memory. These operations guarantee that critical read-modify-write sequences occur as indivisible steps that cannot be interrupted by other threads.

Although different architectures implement them differently, the essential primitives remain consistent: atomic exchange, compare-and-swap, fetch-and-add, test-and-set, and load-linked/store-conditional.

Understanding these primitives reveals how modern operating systems and programming languages implement safe and efficient concurrent systems.

---

If you'd like, I can also write the **next natural essay for your notes**:

**“How the Linux Kernel Implements Atomics Using CPU Instructions”**

That will connect:

```
CPU instructions
      ↓
Linux atomic_t API
      ↓
C11 / C++ atomics
```

which completes the **full systems view of atomics**.