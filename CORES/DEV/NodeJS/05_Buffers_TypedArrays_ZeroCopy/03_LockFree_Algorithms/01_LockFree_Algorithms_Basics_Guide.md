# Lock-Free Algorithms in Node.js — Full Guide

## 1️⃣ Core Concepts

Before code, a few key points:

1. **Lock-free** ≠ no synchronization
    
    - You still **coordinate** between threads, but **without blocking mutexes**.
    - JS Atomics act as **synchronization primitives**.
        
2. **Compare-And-Swap (CAS)**
    
    - `Atomics.compareExchange(array, index, expected, newValue)`
    - Core of most lock-free structures
    - “Set newValue **only if** current value is expected”
    - Atomic, sequentially consistent
        
3. **Single-producer / single-consumer (SPSC)**
    
    - One writer, one reader
    - Easy to reason about, often just a ring buffer
        
4. **Multi-producer / multi-consumer (MPMC)**
    
    - Multiple writers and readers
    - Requires CAS to ensure correctness
        

---

## 2️⃣ Atomic Counter (Simplest Lock-Free)

```js
const sab = new SharedArrayBuffer(Int32Array.BYTES_PER_ELEMENT);
const counter = new Int32Array(sab);

console.log("Initial:", counter[0]);

// Increment atomically
Atomics.add(counter, 0, 1);
console.log("After +1:", Atomics.load(counter, 0));

// Compare and swap
const old = Atomics.compareExchange(counter, 0, 1, 42);
console.log("Old value:", old, "New value:", Atomics.load(counter, 0));

```

✅ **Key points**

- `Atomics.add` = atomic increment, safe for multiple threads
- `compareExchange` = conditional update, used for lock-free structures
    

---

## 3️⃣ Lock-Free Stack (SPSC)

A stack with **one producer, one consumer**. Uses **shared memory and CAS**.

```js
const CAPACITY = 8;
const HEADER = 1;

const sab = new SharedArrayBuffer((HEADER + CAPACITY) * Int32Array.BYTES_PER_ELEMENT);
const stack = new Int32Array(sab);

function push(value) {
  while (true) {
    const top = Atomics.load(stack, 0);
    if (top >= CAPACITY) return false; // stack full
    stack[1 + top] = value;
    if (Atomics.compareExchange(stack, 0, top, top + 1) === top) return true;
  }
}

function pop() {
  while (true) {
    const top = Atomics.load(stack, 0);
    if (top === 0) return null; // stack empty
    const value = stack[top];
    if (Atomics.compareExchange(stack, 0, top, top - 1) === top) return value;
  }
}

// Usage
push(10);
push(20);
console.log(pop()); // 20
console.log(pop()); // 10

```

✅ **Key points**

- Top index is atomic
- CAS ensures only one thread updates top at a time
- Safe SPSC lock-free stack
    

---

## 4️⃣ Single-Producer / Single-Consumer Ring Buffer

This is essentially what you built before, but now framed as **classic lock-free queue**.

```js
const CAP = 8;
const sab = new SharedArrayBuffer((2 + CAP) * Int32Array.BYTES_PER_ELEMENT);
const header = new Int32Array(sab, 0, 2); // [writeIndex, readIndex]
const data = new Int32Array(sab, 2 * Int32Array.BYTES_PER_ELEMENT, CAP);

// Producer
function enqueue(val) {
  const write = header[0];
  const next = (write + 1) % CAP;
  if (next === header[1]) return false; // full
  data[write] = val;
  header[0] = next;
  return true;
}

// Consumer
function dequeue() {
  const read = header[1];
  if (read === header[0]) return null; // empty
  const val = data[read];
  header[1] = (read + 1) % CAP;
  return val;
}

```

✅ **Key points**

- SPSC simplifies concurrency
- No CAS needed for indices (single writer / single reader)
- Deterministic backpressure
    

---

## 5️⃣ Multi-Producer / Multi-Consumer Queue (MPMC)

Here we **need CAS** to prevent multiple threads overwriting each other.

```js
const CAP = 8;
const sab = new SharedArrayBuffer((2 + CAP) * Int32Array.BYTES_PER_ELEMENT);
const header = new Int32Array(sab, 0, 2); // [writeIndex, readIndex]
const data = new Int32Array(sab, 2 * Int32Array.BYTES_PER_ELEMENT, CAP);

// Producer
function mpmcEnqueue(val) {
  while (true) {
    const write = Atomics.load(header, 0);
    const next = (write + 1) % CAP;
    if (next === Atomics.load(header, 1)) return false; // full
    data[write] = val;
    if (Atomics.compareExchange(header, 0, write, next) === write) return true;
  }
}

// Consumer
function mpmcDequeue() {
  while (true) {
    const read = Atomics.load(header, 1);
    if (read === Atomics.load(header, 0)) return null; // empty
    const val = data[read];
    const next = (read + 1) % CAP;
    if (Atomics.compareExchange(header, 1, read, next) === read) return val;
  }
}

```

✅ **Key points**

- Both producers and consumers may race
- CAS ensures only **one thread updates index at a time**
- This is **true lock-free MPMC queue**
    

---

## 6️⃣ Node.js / Worker Integration Example

You can now plug this into **worker threads**:

- Producers = multiple workers pushing into queue
- Consumers = multiple workers popping from queue
    

```js
// worker_producer.js
while(true) {
  mpmcEnqueue(Math.random() * 100);
}

// worker_consumer.js
while(true) {
  const val = mpmcDequeue();
  if (val !== null) console.log(val);
}

```

- **Backpressure:** You can combine with `Atomics.wait` to block when full / empty
- **Streams:** You can wrap MPMC queue in Readable / Writable streams (like you did before)
    

---

## 7️⃣ Mental Model for Lock-Free

1. Identify **shared state**
2. Use **atomic indices / flags / counters**
3. Write **data first, then update index with CAS / Atomics.store**
4. Consumers **read index first, then data**
5. Always ensure **happens-before via Atomics**
    

> Key difference from locks: threads never block each other arbitrarily — only when you explicitly use `Atomics.wait`.

---

## ✅ Summary

- Atomic primitives + CAS = foundation of lock-free algorithms
- SPSC is easy, MPMC requires CAS
- SharedArrayBuffer + Atomics in Node = safe lock-free memory
- Integration with **backpressure and streams** = full multi-threaded pipelines