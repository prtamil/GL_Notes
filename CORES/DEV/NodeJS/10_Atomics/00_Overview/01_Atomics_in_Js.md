# Atomics in JavaScript — Mapping from CPU to JS

## 1. Big picture (important reset)

JavaScript **did not invent atomics**.

JS Atomics are:

- A **thin, safe wrapper**
    
- Over **real CPU atomic instructions**
    
- Exposed only where JS truly has shared memory
    

So think:

> **JS Atomics = CPU Atomics with training wheels**

---

## 2. Where shared memory exists in JS

JS normally:

- Has no shared memory
    
- Uses message passing
    

The exception:

```js
SharedArrayBuffer
```

This is literally:

> A block of raw shared memory

Exactly like:

- `malloc` in C
    
- A shared memory page in an OS
    

---

## 3. Critical rule (burn this in)

> **If memory is backed by `SharedArrayBuffer`, you MUST use Atomics**

Plain reads/writes on shared memory:

- Are data races
    
- Have no ordering guarantees
    
- Are undefined behavior conceptually
    

---

## 4. Atomic LOAD (CPU → JS)

### CPU concept

Atomic read with visibility guarantees.

### JS mapping

```js
Atomics.load(typedArray, index);

```

### Guarantees

- Reads one coherent value
    
- No tearing
    
- Sequentially consistent ordering
    

### What JS hides

- Acquire semantics are implicit
    
- Compiler + CPU barriers handled for you
    

---

## 5. Atomic STORE (CPU → JS)

### CPU concept

Atomic write + visibility + ordering.

### JS mapping

```js
Atomics.store(typedArray, index, value);

```

### Guarantees

- Atomic write
    
- Prior writes become visible before this
    
- Other threads see it in order
    

### Why JS is strict

JS always uses **strong ordering** to avoid foot-guns.

---

## 6. Atomic ADD / RMW

### CPU concept

Read–modify–write as one indivisible operation.

### JS mapping

```js
Atomics.add(arr, index, delta);
Atomics.sub(arr, index, delta);
Atomics.and(arr, index, mask);
Atomics.or(arr, index, mask);
Atomics.xor(arr, index, mask);

```

### Guarantees

- No lost updates
    
- Total order per memory location
    

### Real-world JS use

- Shared counters
    
- Statistics
    
- Work coordination
    

---

## 7. Compare-And-Swap (CAS)

### CPU concept

Foundation of lock-free programming.

### JS mapping

```js
Atomics.compareExchange(arr, index, expected, replacement);

```

### Behavior

- Returns old value
    
- Update happens only if expected matches
    

### Why this matters

With this single function, you can:

- Build locks
    
- Build queues
    
- Build state machines
    

---

## 8. Atomic EXCHANGE (swap)

### CPU concept

Replace value and get old one.

### JS mapping

```js
Atomics.exchange(arr, index, value);

```

### Typical use

- Simple spinlocks
    
- Ownership handoff
    

---

## 9. Memory ordering in JS (important design choice)

JS Atomics are:

> **Sequentially consistent**

That means:

- No relaxed mode
    
- No acquire/release choices
    
- No reordering surprises
    

Why JS chose this:

- Most JS developers are not systems programmers
    
- Safety over performance
    
- Predictable behavior across platforms
    

This is why JS atomics feel “heavy” — but safe.

---

## 10. What JS does NOT expose (on purpose)

JS hides:

- Memory fences
    
- Weak ordering
    
- Relaxed atomics
    
- Custom barriers
    

This prevents:

- Heisenbugs
    
- Architecture-specific failures
    
- Undefined behavior
    

---

## 11. Atomic WAIT / NOTIFY (this is special)

### CPU + OS concept

- Atomic check
    
- Sleep if unchanged
    
- Wake when modified
    

### JS mapping

```js
Atomics.wait(arr, index, expected);
Atomics.notify(arr, index, count);

```

### What this really is

A **futex-style primitive**:

- No busy looping
    
- OS-assisted sleep
    
- Scales well
    

### Critical rule

❌ Cannot be used on the main JS thread  
(Blocking the event loop would freeze everything)

---

## 12. One-to-one mapping table

|CPU concept|JavaScript|
|---|---|
|atomic load|`Atomics.load`|
|atomic store|`Atomics.store`|
|atomic add|`Atomics.add`|
|CAS|`Atomics.compareExchange`|
|swap|`Atomics.exchange`|
|futex wait|`Atomics.wait`|
|futex wake|`Atomics.notify`|

Nothing extra. Nothing missing.

---

## 13. What you can build in JS using Atomics

With just these:

- Mutex
    
- Semaphore
    
- Barrier
    
- Work queue
    
- Thread pool coordination
    
- Backpressure mechanisms
    

Exactly like C/C++, just slower and safer.

---

## 14. Why JS Atomics feel “weird” at first

Because JS developers are used to:

- Event loop
    
- Promises
    
- Message passing
    

Atomics are:

- Low-level
    
- Synchronous
    
- CPU-minded
    

But now that you understand processors:  
👉 **They should feel natural**

---

## 15. The correct JS mental model (keep this)

> **`SharedArrayBuffer` is raw shared RAM**  
> **`Atomics` are the only legal way to touch it**

Everything else is undefined behavior.

---

## 16. Where people go wrong in JS Atomics

- Mixing atomic and non-atomic access
    
- Using Atomics when message passing is enough
    
- Expecting performance miracles
    
- Blocking the main thread