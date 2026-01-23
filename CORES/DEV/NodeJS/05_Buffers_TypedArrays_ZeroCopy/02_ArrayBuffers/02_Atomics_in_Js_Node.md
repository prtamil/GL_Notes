# Atomics in JavaScript (Node.js & Web) — In-Depth Guide

## 1. Why Atomics Exist (The Problem)

### JavaScript _can_ run in parallel

- Node.js: `worker_threads`
    
- Web: `Web Workers`
    

Each worker runs on a **different OS thread**.

### SharedArrayBuffer allows shared memory

```js
const sab = new SharedArrayBuffer(1024);

```

But shared memory introduces a **fundamental problem**:

> **Two threads can read/write the same memory at the same time.**

This leads to:

- Lost updates
    
- Corrupted state
    
- Impossible-to-debug bugs
    

This is called a **data race**.

---

## 2. Why Normal Reads/Writes Are Unsafe

Consider this shared counter:

```js
// shared Int32Array
counter[0] = counter[0] + 1;

```

Internally this is:

1. Load value
    
2. Add 1
    
3. Store value
    

Two threads interleaving these steps can overwrite each other.

### Result

You increment twice, but the value only increases once.

---

## 3. Atomics: The Guarantee

The `Atomics` API provides **hardware-level guarantees**:

- Operations are **indivisible**
    
- Memory ordering is respected
    
- All threads observe consistent state
    

> **Atomics turn SharedArrayBuffer from “dangerous” into “usable”.**

---

## 4. What Atomics Actually Are

`Atomics` is:

- A namespace of low-level functions
    
- That operate on **TypedArrays**
    
- Backed by **SharedArrayBuffer**
    
- Mapped to **CPU atomic instructions**
    

```js
Atomics.add(sharedView, index, value);

```

This maps closely to:

- `LOCK XADD` (x86)
    
- LL/SC loops (ARM)
    

---

## 5. What Atomics Can Operate On

Atomics only work on:

- `Int8Array`
    
- `Uint8Array`
    
- `Int16Array`
    
- `Uint16Array`
    
- `Int32Array`
    
- `Uint32Array`
    

Backed by **SharedArrayBuffer only**.

❌ Not allowed:

- Float arrays
    
- Normal ArrayBuffer
    
- Normal JS numbers
    

---

## 6. Atomics API (Node.js & Web)

### 6.1 Atomic Read / Write

```js
Atomics.load(view, index);
Atomics.store(view, index, value);

```

Use when:

- Multiple threads read/write
    
- You want visibility guarantees
    

---

### 6.2 Atomic Arithmetic

```js
Atomics.add(view, i, 1);
Atomics.sub(view, i, 1);
Atomics.and(view, i, mask);
Atomics.or(view, i, mask);
Atomics.xor(view, i, mask);

```

These:

- Modify and return old value
    
- Are atomic
    

---

### 6.3 Compare-And-Swap (CAS) — The Power Tool

```js
Atomics.compareExchange(view, i, expected, replacement);

```

This is the **foundation of lock-free algorithms**.

Mental model:

> “Only update if the value is what I expect.”

---

### 6.4 Waiting & Notification (Blocking!)

Node.js **supports blocking Atomics.wait** (web does not on main thread).

```js
Atomics.wait(view, i, expected);
Atomics.notify(view, i, count);

```

Used for:

- Queues
    
- Backpressure
    
- Thread coordination
    

This is **real blocking**, not async.

---

## 7. Memory Ordering (Important but Simple)

JS Atomics enforce **sequential consistency** by default.

That means:

- Operations appear in the same order to all threads
    
- Stronger than many low-level languages
    

This simplifies reasoning (at some performance cost).

---

# Now the Big Example: SharedArrayBuffer Ring Buffer

This is the **canonical concurrent structure**.

Used in:

- Audio pipelines
    
- Logging systems
    
- Message queues
    
- Media processing
    
- Databases
    

---

## 8. Ring Buffer Mental Model

A ring buffer is:

- Fixed-size circular array
    
- One writer (producer)
    
- One reader (consumer)
    

### Indices

- `writeIndex` → where producer writes next
    
- `readIndex` → where consumer reads next
    

Both wrap around (`mod capacity`).

---

## 9. Memory Layout (Very Important)

We’ll pack everything into **one SharedArrayBuffer**.

```js
[ writeIndex | readIndex | data data data data ... ]
   Int32        Int32        Int32 array

```

This layout matters.

---

## 10. Creating the Shared Buffer

```js
const CAPACITY = 8;
const HEADER_SIZE = 2; // writeIndex, readIndex

const sab = new SharedArrayBuffer(
  (HEADER_SIZE + CAPACITY) * Int32Array.BYTES_PER_ELEMENT
);

const header = new Int32Array(sab, 0, HEADER_SIZE);
const data = new Int32Array(
  sab,
  HEADER_SIZE * Int32Array.BYTES_PER_ELEMENT,
  CAPACITY
);

```

Now:

- `header[0]` = writeIndex
    
- `header[1]` = readIndex
    

---

## 11. Producer (Writer) Logic

```js
function push(value) {
  while (true) {
    const write = Atomics.load(header, 0);
    const read = Atomics.load(header, 1);

    const nextWrite = (write + 1) % CAPACITY;

    // Buffer full
    if (nextWrite === read) {
      Atomics.wait(header, 1, read);
      continue;
    }

    data[write] = value;

    Atomics.store(header, 0, nextWrite);
    Atomics.notify(header, 0);

    return;
  }
}

```

### What’s happening

- Atomically read indices
    
- Check if buffer is full
    
- Write data
    
- Atomically publish write index
    
- Wake consumer
    

---

## 12. Consumer (Reader) Logic

```js
function pop() {
  while (true) {
    const write = Atomics.load(header, 0);
    const read = Atomics.load(header, 1);

    // Buffer empty
    if (write === read) {
      Atomics.wait(header, 0, write);
      continue;
    }

    const value = data[read];
    const nextRead = (read + 1) % CAPACITY;

    Atomics.store(header, 1, nextRead);
    Atomics.notify(header, 1);

    return value;
  }
}

```

---

## 13. Why This Works (Mental Model)

### Key rules

- Only producer writes `writeIndex`
    
- Only consumer writes `readIndex`
    
- Atomics ensure visibility
    
- Wait/notify prevent busy spinning
    

This is **lock-free coordination**.

---

## 14. Usage Pattern (Node.js)

### Main thread

- Creates SharedArrayBuffer
    
- Spawns workers
    
- Passes SAB to workers
    

### Worker A

- Calls `push()`
    

### Worker B

- Calls `pop()`
    

No copying. No serialization. No GC pressure.

---

## 15. Where This Is Used in Real Systems

- Audio worklets
    
- Video decoding pipelines
    
- Game engines
    
- Log ingestion systems
    
- High-frequency telemetry
    
- IPC inside browsers
    

---

## 16. Common Mistakes (Learn These)

### ❌ Using normal reads/writes

```js
header[0]++; // ❌ data race
```

### ❌ Using Atomics on ArrayBuffer

```js
Atomics.add(normalArray, 0, 1); // ❌
```

### ❌ Forgetting modulo wrap

Classic ring buffer bug.

---

## 17. Final Mental Model (Lock This In)

> **SharedArrayBuffer gives shared memory**  
> **Atomics make shared memory safe**  
> **Indices coordinate access**  
> **wait/notify replace locks**  
> **Ring buffers move data without copies**

If this model is clear, you now understand **parallel memory in JavaScript**.