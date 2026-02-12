# Atomics in JavaScript — From CPU Reality to Correct Programs

Modern CPUs are complicated. Each CPU core has its own cache and store buffers, and multiple cores run in parallel. Because of this, **memory writes and reads are not automatically visible or ordered across threads**. Even if one thread writes a value, another thread may temporarily see an outdated value.

JavaScript did **not invent atomics** — they already exist in the hardware to solve this problem. In JavaScript, atomics are a **safe, restricted interface** over the CPU instructions, exposed only where JS supports shared memory. You can think of it as:

> **JS Atomics = CPU Atomics with guardrails**

They allow multiple threads to access the same memory safely, without introducing subtle timing or ordering bugs.

---

## Why Shared Memory is Special in JavaScript

Normally, JavaScript avoids shared memory entirely:

- Threads communicate by **message passing**
    
- Each thread has its own memory
    
- This naturally prevents **data races and ordering bugs**
    

The **only exception** is the `SharedArrayBuffer`. It creates:

> Raw memory shared across threads

Once multiple threads can access the same memory, **all the CPU-level memory problems appear in JS**. Threads can read stale values, writes can be delayed, and ordering cannot be assumed.

---

## The Unbreakable Rule

> **Every access to a SharedArrayBuffer must go through Atomics.**

If you ignore this:

- Cache may return **stale values**
    
- Writes may be **reordered**
    
- Store buffers may **delay visibility**
    

In short, plain reads and writes have **no correctness guarantees**. Using atomics is the only way to ensure that:

1. Updates are visible across threads
    
2. Operations happen in a predictable order
    
3. Programs behave correctly, not just “eventually consistent”
    

---

This gives a **solid foundation** for understanding why JavaScript atomics exist, why shared memory is tricky, and why atomics are mandatory for correctness.