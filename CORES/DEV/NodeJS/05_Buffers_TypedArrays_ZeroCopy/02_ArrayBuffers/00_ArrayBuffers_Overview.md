# ArrayBuffer — The Core Memory Primitive (Clean, In-Depth Guide)

This essay explains **exactly what ArrayBuffer is**, what types exist, how zero-copy works, and how ownership & transfer behave — **without ambiguity**.

---

## 1. What ArrayBuffer Is (Precise Definition)

An **ArrayBuffer** is:

- A **fixed-length block of raw binary memory**
    
- Allocated by the JavaScript engine
    
- Managed by the garbage collector
    
- Not directly readable or writable
    

```js
const ab = new ArrayBuffer(1024);

```

This allocates **1024 bytes of memory**.  
Nothing else.

---

## 2. What ArrayBuffer Is NOT

ArrayBuffer is **not**:

- ❌ An array
    
- ❌ A list of numbers
    
- ❌ Typed
    
- ❌ Resizable
    
- ❌ Automatically shared
    
- ❌ A data structure
    

It is closest to **`malloc(size)` in C**, except GC-managed.

---

## 3. Ownership Model (Critical Concept)

A normal `ArrayBuffer` has **single ownership**.

At any moment:

- Exactly **one JS agent owns the memory**
    
- Other code can access it only via views
    

```js
ArrayBuffer (owns memory)
 ├─ Uint8Array (view)
 ├─ Float32Array (view)
 └─ DataView (view)

```

Views:

- Do NOT own memory
    
- Keep the buffer alive
    
- Cannot exist without the buffer
    

---

## 4. Fixed Size (Why It Cannot Grow)

ArrayBuffers are fixed-size by design because:

- Growing memory requires reallocation
    
- Reallocation would invalidate all views
    
- Zero-copy guarantees would break
    

So instead:

- Allocate once
    
- Reuse
    
- Or allocate a new buffer
    

This is a **systems trade-off**, not a JS limitation.

---

## 5. The Only Two Buffer Types

This is the authoritative list.

### 5.1 `ArrayBuffer` (Single-owner memory)

```js
const ab = new ArrayBuffer(1024);

```

Characteristics:

- Owned by one thread
    
- Transferable (can move ownership)
    
- Not shared
    
- Most common case
    

Used for:

- Binary parsing
    
- File formats
    
- Encoding / decoding
    
- Local processing
    

---

### 5.2 `SharedArrayBuffer` (Shared memory)

```js
const sab = new SharedArrayBuffer(1024);
const view = new Int32Array(sab);

```

Characteristics:

- Shared across threads
    
- Cannot be transferred
    
- Requires `Atomics` for safety
    

Used for:

- Worker communication
    
- Ring buffers
    
- Lock-free queues
    
- High-performance systems
    

---

## 6. Transfer Is a Usage Pattern (Not a Type)

### What “transfer” means

Transferring an ArrayBuffer means:

> **Moving ownership of the same memory from one thread to another without copying.**

It does **not** create a new buffer.

---

### How transfer works

```js
worker.postMessage(ab, [ab]);

```

What happens:

1. Ownership moves to worker
    
2. No memory copy
    
3. Original buffer becomes **detached**
    

```js
ab.byteLength === 0; // detached

```

Detached means:

- Memory is gone from this thread
    
- Access throws errors
    
- Ownership is lost permanently
    

---

### Why detaching exists

Two threads owning the same memory would cause:

- Data races
    
- Undefined behavior
    
- Security issues
    

So JS enforces **single ownership** for `ArrayBuffer`.

---

## 7. Zero-Copy — The Three Real Mechanisms

### 7.1 Zero-copy via Views (Same thread)

```js
const header = buffer.subarray(0, 16);

```

- Same ArrayBuffer
    
- New window
    
- No allocation
    

---

### 7.2 Zero-copy via Transfer (Move between threads)

```js
postMessage(buffer, [buffer]);

```

- Ownership moves
    
- No copy
    
- Original detached
    

---

### 7.3 Zero-copy via Shared Memory (Multiple threads)

```js
new SharedArrayBuffer(...)

```

- Same memory visible everywhere
    
- Requires synchronization
    

---

## 8. Moves vs Copies (Clear Comparison)

### Copy (safe, expensive)

```js
const copy = buffer.slice(0);

```

- New memory
    
- Independent lifetime
    
- Higher cost
    

---

### Move (fast, disciplined)

```js
postMessage(buffer, [buffer]);

```

- No new memory
    
- Old buffer invalid
    
- Requires careful ownership tracking
    

---

## 9. Common Lifetime Bugs (Learn These Early)

### Bug: Accidental retention

```js
const header = bigBuffer.subarray(0, 16);

```

Keeps entire buffer alive.

**Fix**

```js
const header = bigBuffer.slice(0, 16);

```

---

### Bug: Using detached buffer

```js
postMessage(ab, [ab]);
ab[0]; // ❌ TypeError

```

Ownership already moved.

---

## 10. Real-World Pipeline (How This Is Used)

### Network pipeline

```js
Socket → ArrayBuffer
        → DataView (parse header)
        → TypedArray (process payload)
        → transfer to worker

```

### Media pipeline

```js
Disk → ArrayBuffer → decode → SharedArrayBuffer → render

```

### Worker pool

```js
Main thread allocates buffers
Workers receive via transfer
Buffers move back when reused

```

---

## 11. When to Use What (No Guessing)

|Requirement|Use|
|---|---|
|Local binary memory|ArrayBuffer|
|Binary parsing|ArrayBuffer + DataView|
|Numeric processing|TypedArray|
|Move memory across threads|Transfer ArrayBuffer|
|Shared concurrent state|SharedArrayBuffer + Atomics|

---

## 12. Final Mental Model (Memorize This)

> **ArrayBuffer owns memory.  
> Views interpret memory.  
> Transfer moves ownership.  
> SharedArrayBuffer shares memory with rules.**

There are **only two buffer types**, and everything else is a **usage pattern**.