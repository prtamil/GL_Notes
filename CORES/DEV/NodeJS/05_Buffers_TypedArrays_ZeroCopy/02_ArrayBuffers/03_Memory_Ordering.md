# Memory Ordering — A Deep, Generic Guide 

## Why Memory Ordering Exists (The Core Problem)

You naturally assume code runs like this:

```js
store A
store B
load C

```

But modern systems **do not execute memory operations in the order you write them**.

Why?

Because CPUs, runtimes, and compilers aggressively optimize for performance by:

- Reordering instructions
    
- Buffering writes
    
- Caching reads
    
- Executing speculatively
    

This breaks naïve shared-memory reasoning.

---

## The Fundamental Reality

There are **three different “orders”** in play:

1. **Program order**  
    The order in which your code is written
    
2. **Execution order**  
    The order the CPU actually executes instructions
    
3. **Visibility order**  
    The order in which _other threads_ observe memory changes
    

> **Memory ordering exists to control visibility order.**

---

## What “Memory Ordering” Actually Means

> **Memory ordering defines which memory operations must become visible to other threads, and in what relative order.**

It does **not**:

- Guarantee timing
    
- Prevent reordering inside a thread
    
- Make code faster
    

It only constrains **what other threads are allowed to see**.

---

## Why Reordering Happens (Concrete Reasons)

### 1. CPU Instruction Reordering

The CPU may execute:

```js
x = 1;
y = 1;

```

as:

```js
y = 1
x = 1

```

Because there is no dependency.

---

### 2. Store Buffers

Writes go into **per-core store buffers** first.

Another core might see:

- `y = 1`
    
- `x = 0`
    

Even though `x` was written first.

---

### 3. Cache Coherence ≠ Ordering

Cache coherence ensures **eventual consistency**, not **ordering**.

It guarantees:

- You won’t see _two_ values for the same location forever
    

It does **not** guarantee:

- When
    
- In what order
    

---

## The Classic Bug (Why Ordering Matters)

Thread A:

```js
data = 42
ready = true

```

Thread B:

```js
if (ready) read(data)

```

Thread B may legally observe:

```js
ready == true
data == 0

```

This is **not a bug in the CPU**.  
It is **a missing ordering guarantee**.

---

# Memory Barriers / Fences (Conceptual Fix)

A **memory barrier** enforces visibility constraints.

Conceptually:

> **“All memory operations before this point must be visible before any memory operations after this point.”**

Different barriers enforce different strengths.

---

# The Three Core Ordering Models (Generic)

## 1. Relaxed Ordering

- Guarantees atomicity only
    
- No visibility ordering
    
- Fastest
    
- Hard to reason about
    

Used for:

- Counters
    
- Statistics
    
- Non-synchronization data
    

---

## 2. Acquire / Release Ordering

This is the **workhorse model** of most concurrent systems.

### Release

> “All prior writes must become visible before this write.”

### Acquire

> “All subsequent reads must observe what happened before.”

Together, they form a **happens-before relationship**.

This is how:

- Mutexes
    
- Queues
    
- Channels
    
- Lock-free structures
    

are implemented.

---

## 3. Sequential Consistency (SC) — Deep Explanation

Sequential consistency is the **strongest and simplest** memory model.

### What SC Guarantees

> **All threads observe all atomic operations in the same global order.**

This means:

- There exists a single, total order of atomic operations
    
- Every thread agrees on that order
    
- The order respects program order
    

### Mental Model

You can imagine:

> “All atomic operations happen one at a time, in a single global sequence.”

Even though they don’t physically execute that way.

---

### Why SC Is Easy to Reason About

With SC, you can:

- Read code top-to-bottom
    
- Interleave threads arbitrarily
    
- Still get correct results
    

You **do not** need to think about:

- Reordering
    
- Visibility windows
    
- Partial observation
    

This is why SC is often called the **“intuitive” memory model**.

---

### Cost of Sequential Consistency

SC is expensive because:

- CPUs must insert full memory fences
    
- Optimizations are restricted
    
- Some reordering is forbidden
    

That’s why low-level systems often avoid SC unless necessary.

---

# Where JavaScript Fits In

JavaScript normally avoids all of this because:

- There is no shared memory
    
- The event loop serializes execution
    

Except here:

>**SharedArrayBuffer + Atomics**

This is **the only place memory ordering exists in JavaScript**.

---

## JavaScript Atomics Ordering Model

JavaScript Atomics are **sequentially consistent by default**.

This means:

- Every `Atomics.*` operation acts as a **full memory fence**
    
- No reordering is allowed across atomic operations
    
- All threads observe atomics in the same order
    

This is a deliberate design choice.

---

## Why JavaScript Chose SC

Because:

- JavaScript developers are not expected to reason about memory models
    
- Subtle ordering bugs would be disastrous
    
- Predictability matters more than raw speed
    

JavaScript chooses:

> **Correctness + simplicity over maximal performance**

---

## Practical Implication (Very Important)

This code is **always correct** in JS:

```js
payload[i] = 42;
Atomics.store(state, READY, 1);

```

Consumer:

```js
if (Atomics.load(state, READY) === 1) {
  console.log(payload[i]);
}

```

Because:

- The store is SC
    
- The load is SC
    
- Visibility is guaranteed
    

No extra barriers needed.

---

## What Breaks Without Atomics

```js
state[READY] = 1; // NOT atomic

```

Now:

- Write may reorder
    
- Visibility is undefined
    
- Reads may observe stale data
    

This is why **shared memory without Atomics is unsafe**.

---

# How Memory Ordering Is “Created”

Memory ordering is created by:

- Atomic instructions
    
- Memory fences
    
- Runtime guarantees
    

In JavaScript:

- `Atomics.*` injects the necessary ordering
    
- You never manually insert fences
    
- Choosing Atomics **is choosing ordering**
    

---

# How Memory Ordering Is “Used”

You use ordering by:

1. Writing data
    
2. Publishing a flag (atomic store)
    
3. Observing the flag (atomic load)
    
4. Reading the data
    

This pattern appears everywhere:

- Queues
    
- State machines
    
- Locks
    
- IPC
    
- Shared caches
    

---

## Generic Publish / Consume Pattern

Publisher:

```js
buffer[i] = value;
Atomics.store(state, READY, 1);

```

Consumer:

```js
while (Atomics.load(state, READY) === 0);
console.log(buffer[i]);

```

This is **ordering**, not locking.

---

# Common Misconceptions (Important)

❌ “Atomic means fast”  
✔ Atomic means **visible and ordered**

❌ “Cache coherence is enough”  
✔ Coherence ≠ ordering

❌ “JavaScript hides memory models”  
✔ JS exposes them **only when you opt in**

---

# Final Mental Model (Lock This In)

> **Memory ordering controls visibility, not execution**  
> **Atomics create ordering guarantees**  
> **Acquire/Release is the workhorse**  
> **Sequential Consistency is the safest mental model**  
> **JavaScript Atomics are sequentially consistent**  
> **Without Atomics, shared memory is undefined**