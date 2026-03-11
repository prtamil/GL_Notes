## Compiler Reordering: Why Memory Operations May Change Before Reaching the CPU

### Introduction

When discussing memory ordering, it is common to focus on CPU behavior such as store buffers, caches, and out-of-order execution. However, memory operations may already be reordered **before the CPU even executes the program**. This happens during compilation.

Modern compilers perform aggressive optimizations to improve performance. These optimizations include reordering instructions, eliminating redundant memory accesses, and keeping variables in registers. While these transformations preserve the behavior of **single-threaded programs**, they can create problems in concurrent programs where multiple threads communicate through shared memory.

This phenomenon is known as **compiler reordering**. It refers to the compiler changing the order or existence of memory operations while generating machine code, as long as the transformation does not change the observable behavior of a single thread.

Because compilers are unaware of external threads unless explicitly instructed, these optimizations can break synchronization assumptions in concurrent code. Therefore, special mechanisms are needed to prevent unwanted compiler optimizations when accessing shared variables.

---

## Why Compilers Reorder Instructions

Compilers aim to generate efficient machine code. To achieve this, they analyze programs and apply transformations that reduce memory accesses, improve pipeline usage, and eliminate unnecessary operations.

The compiler assumes the program runs in isolation unless synchronization primitives indicate otherwise. As a result, it may freely reorder instructions or eliminate memory operations that appear redundant from the perspective of a single thread.

Several common compiler optimizations can affect memory ordering.

---

## Instruction Scheduling

**Instruction scheduling** rearranges instructions to better utilize CPU pipelines and avoid stalls.

For example, consider the following code:

```c
x = 1;
y = 1;
```

The compiler may generate machine code where the order is reversed:

```c
y = 1;
x = 1;
```

Because both assignments are independent, this reordering does not change the result in a single-threaded program. However, in a concurrent program another thread may observe the writes in a different order than intended.

Instruction scheduling is therefore one source of compiler-level reordering.

---

## Register Optimization

Compilers often keep frequently accessed variables in **CPU registers** instead of repeatedly loading them from memory.

Consider this example:

```c
while (flag == 0) {
}
```

A compiler might transform this into:

```c
int tmp = flag;
while (tmp == 0) {
}
```

Because the compiler assumes that `flag` cannot change without the program itself modifying it, the value may be cached in a register. This means the loop never reloads `flag` from memory.

In a multithreaded program, another thread may set `flag = 1`, but the loop continues forever because the compiler removed the repeated memory load.

---

## Load and Store Elimination

Compilers also remove memory operations that appear unnecessary.

Example:

```c
x = 1;
x = 1;
```

The compiler may eliminate the first store because the second store overwrites it.

Similarly, repeated loads may be merged:

```c
int a = x;
int b = x;
```

This could become:

```c
int a = x;
int b = a;
```

In concurrent programs, however, another thread may update `x` between the two reads. Eliminating the second load removes the possibility of observing that change.

---

## Preventing Compiler Reordering

To safely access shared variables in concurrent programs, programmers must explicitly prevent certain compiler optimizations.

The Linux kernel provides several mechanisms for this purpose.

---

## Compiler Barrier

The simplest mechanism is a **compiler barrier**.

```
barrier();
```

A compiler barrier tells the compiler:

- do not reorder memory operations across this point
    
- do not cache values in registers across this boundary
    

Conceptually:

```
operation A
barrier()
operation B
```

The compiler must generate code where `operation A` appears before `operation B`.

However, a compiler barrier does **not affect CPU execution**. It only prevents the compiler from moving instructions.

---

## READ_ONCE()

The Linux kernel provides the `READ_ONCE()` macro to safely read shared variables.

Example:

```c
value = READ_ONCE(shared_var);
```

This macro ensures:

- the variable is read exactly once
    
- the compiler cannot merge or eliminate the load
    
- the value is not cached in a register across operations
    

This prevents the compiler from performing optimizations that would hide changes made by other threads.

---

## WRITE_ONCE()

Similarly, `WRITE_ONCE()` ensures that a variable is written exactly once.

Example:

```c
WRITE_ONCE(shared_var, 10);
```

This prevents the compiler from:

- eliminating the write
    
- splitting the write into multiple operations
    
- merging writes with other instructions
    

It guarantees that the memory store occurs exactly as written.

---

## Example of Safe Shared Variable Access

Consider two threads communicating through a flag.

Producer thread:

```c
data = 100;
WRITE_ONCE(flag, 1);
```

Consumer thread:

```c
while (READ_ONCE(flag) == 0)
    ;

printf("%d\n", data);
```

Using `READ_ONCE()` and `WRITE_ONCE()` ensures the compiler does not remove or reorder the memory accesses that are necessary for communication between threads.

However, these macros **do not guarantee CPU ordering**. They only prevent compiler optimizations. For full correctness across CPUs, memory barriers or acquire/release semantics may also be required.

---

## Compiler Reordering vs CPU Reordering

It is important to distinguish the two sources of reordering.

|Type|Where it Happens|Cause|
|---|---|---|
|Compiler reordering|During compilation|Code optimization|
|CPU reordering|During execution|Hardware performance optimizations|

Compiler barriers prevent the first type, while memory barriers control the second.

Concurrent programs must often handle **both kinds of reordering**.

---

## Conclusion

Compiler reordering occurs because modern compilers aggressively optimize programs by rearranging instructions, eliminating redundant memory operations, and keeping variables in registers. These transformations are safe in single-threaded programs but can break synchronization assumptions in concurrent systems.

To prevent such issues, the Linux kernel provides mechanisms such as `barrier()`, `READ_ONCE()`, and `WRITE_ONCE()` that restrict compiler optimizations when accessing shared variables. These primitives ensure that memory operations appear exactly as written in the program, allowing threads to observe changes made by others.

Understanding compiler reordering is essential for concurrent programming because it highlights that memory ordering issues can arise even before instructions reach the CPU.