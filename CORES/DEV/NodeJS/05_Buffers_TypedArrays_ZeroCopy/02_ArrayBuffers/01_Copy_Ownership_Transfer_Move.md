# ArrayBuffer, Ownership, Transfer, Sharing, and Atomics

## A Deep Mental Model for JavaScript Memory

JavaScript looks high-level, but underneath, modern JS engines expose **explicit memory primitives**.  
If you understand these, you can reason about **performance, correctness, and concurrency** instead of guessing.

At the center of everything is **ArrayBuffer**.

---

## 1. ArrayBuffer: The Memory Itself

### What ArrayBuffer really is

An `ArrayBuffer` is:

- A **contiguous block of bytes**
    
- Fixed-size
    
- Allocated by the JS engine
    
- Managed by the garbage collector
    
- **Not typed**
    
- **Not shared by default**
    

```js
const ab = new ArrayBuffer(1024);

```

That statement means:

> “Give me 1024 bytes of raw memory.”

No numbers, no structure, no meaning — just memory.

This is analogous to:

```c
void* p = malloc(1024);

```

…but GC-managed.

---

## 2. Ownership: The Core Rule

### Single-owner rule (normal ArrayBuffer)

A normal `ArrayBuffer` has **exactly one owner** at a time.

- One JS agent (thread / realm) owns the memory
    
- Other code can only _view_ it
    
- Ownership guarantees safety
    

This rule exists to prevent:

- Data races
    
- Undefined behavior
    
- Security bugs
    

### Views do NOT own memory

```js
const ab = new ArrayBuffer(16);
const u8 = new Uint8Array(ab);
const dv = new DataView(ab);

```

- `ab` owns memory
    
- `u8` and `dv` are **windows**
    
- Views keep the buffer alive
    
- Views die when buffer is gone
    

---

## 3. Why ArrayBuffer Is Fixed Size

Why can’t we grow it?

Because:

- Growing memory requires reallocation
    
- Reallocation would invalidate all views
    
- Zero-copy guarantees would break
    

Instead, JS chooses:

- Fixed-size memory
    
- Explicit copy or move
    
- Predictable semantics
    

This is a **systems design decision**, not a limitation.

---

## 4. Copy Semantics: Duplicate the Memory

### What a copy means

A copy means:

- New memory allocation
    
- Bytes duplicated
    
- Independent lifetime
    

```js
const ab1 = new ArrayBuffer(8);
const u8 = new Uint8Array(ab1);
u8[0] = 42;

const ab2 = ab1.slice(0); // COPY

```

Now:

- `ab1` and `ab2` are unrelated
    
- Changes don’t affect each other
    
- Memory cost doubles
    

### When copying is correct

- You need long-term ownership
    
- You need isolation
    
- You want immutability
    
- You want safety over speed
    

---

## 5. Move Semantics: Transfer Ownership (Zero-Copy)

### This is where things get serious

JS supports **move semantics** for ArrayBuffer.

This means:

> **Ownership of the same memory can be moved between threads without copying.**

---

### Transfer (move) in practice

```js
worker.postMessage(ab, [ab]);

```

What happens:

1. Ownership moves to the worker
    
2. No memory is copied
    
3. Original buffer becomes **detached**
    

```js
ab.byteLength === 0; // true

```

Detached means:

- Memory no longer exists here
    
- Access throws errors
    
- You cannot use it again
    

This is **intentional**.

---

### Why detaching exists

If two threads owned the same memory:

- Race conditions
    
- Corruption
    
- Security vulnerabilities
    

So JS enforces:

> **Move, don’t share — unless you explicitly choose shared memory.**

---

## 6. Transfer Is NOT a Type

This is crucial.

There is:

- ❌ No `TransferableArrayBuffer`
    
- ✅ Only `ArrayBuffer` used with transfer semantics
    

Transfer is:

- A **usage pattern**
    
- A **capability**
    
- Not a separate object
    

---

## 7. Zero-Copy Has Three Forms (Know Them All)

### 7.1 Zero-copy via views (same thread)

```js
const payload = buffer.subarray(16);

```

- Same ArrayBuffer
    
- No allocation
    
- Just a new window
    

Used for:

- Parsing
    
- Framing
    
- Streaming
    

---

### 7.2 Zero-copy via transfer (move between threads)

```js
postMessage(buffer, [buffer]);

```
- Same memory
    
- Ownership moves
    
- Sender loses access
    

Used for:

- Worker pools
    
- Parallel processing
    
- Offloading CPU work
    

---

### 7.3 Zero-copy via shared memory

```js
new SharedArrayBuffer(...)

```

- Same memory visible everywhere
    
- No ownership transfer
    
- Requires synchronization
    

Used for:

- High-performance concurrency
    
- Real-time systems
    

---

## 8. SharedArrayBuffer: Breaking the Ownership Rule (Safely)

### What SharedArrayBuffer is

A `SharedArrayBuffer` is:

- A block of memory
    
- Shared across multiple threads
    
- Never detached
    
- Never transferred
    
- Accessed concurrently
    

```js
const sab = new SharedArrayBuffer(1024);
const view = new Int32Array(sab);

```

This **breaks single ownership**, so rules change.

---

## 9. Why Atomics Are Required

### The problem: data races

If two threads do this:

```js
view[0] += 1;
```

You can lose updates.

Because:

- Read-modify-write is not atomic
    
- CPU may reorder operations
    
- Threads interleave unpredictably
    

---

### Atomics enforce correctness

```js
Atomics.add(view, 0, 1);
```

This guarantees:

- Operation is indivisible
    
- Memory ordering is respected
    
- All threads see consistent state
    

---

## 10. Atomics Are NOT Optional with SharedArrayBuffer

This is a rule, not a suggestion.

|Operation|Safe?|
|---|---|
|Plain read/write|❌ unsafe|
|Atomics.*|✅ safe|

If you use `SharedArrayBuffer` **without Atomics**, your program is incorrect.

---

## 11. Real-World Usage Patterns

### Pattern 1: Worker pool with transfer (move)

```js
Main thread:
- allocate ArrayBuffer
- fill data
- transfer to worker

Worker:
- process
- transfer result back

```

Why this works:

- No copying
    
- Clear ownership
    
- Easy reasoning
    

---

### Pattern 2: Shared ring buffer (shared memory)

```js
SharedArrayBuffer
- producer index (atomic)
- consumer index (atomic)
- data region

```

Used in:

- Media pipelines
    
- High-frequency messaging
    
- Game engines
    

---

### Pattern 3: Hybrid (best of both)

```js
Shared control plane (SAB + Atomics)
Transferable data plane (ArrayBuffer)

```

This is how serious systems are built.

---

## 12. Lifetime Bugs You Must Watch For

### Bug: Retaining large buffers accidentally

```js
const header = bigBuffer.subarray(0, 16);

```

Keeps entire buffer alive.

Fix:

```js
const header = bigBuffer.slice(0, 16);

```

---

### Bug: Using detached buffers

```js
postMessage(ab, [ab]);
ab[0]; // 💥 error

```

Ownership already moved.

---

## 13. Final Mental Model (Lock This In)

> **ArrayBuffer owns memory**  
> **Views interpret memory**  
> **Copy duplicates memory**  
> **Transfer moves ownership**  
> **SharedArrayBuffer shares memory**  
> **Atomics make sharing safe**

This is the _complete model_. Nothing hidden.

---

## 14. When to Use What (No Guessing)

|Need|Choose|
|---|---|
|Local binary work|ArrayBuffer|
|Safe duplication|Copy (`slice`)|
|Parallel work|Transfer ArrayBuffer|
|Concurrent access|SharedArrayBuffer + Atomics|
|Structured parsing|DataView|
|Numeric processing|TypedArray|