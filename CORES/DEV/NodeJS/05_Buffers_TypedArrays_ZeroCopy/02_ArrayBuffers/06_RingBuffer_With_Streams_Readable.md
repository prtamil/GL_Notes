# Integrating SharedArrayBuffer Ring Buffer with Node Streams

## What We’re Actually Doing

Node streams already solve:

- Backpressure
    
- Composition (`pipe`)
    
- Interop with fs / net / crypto
    

But **Node streams are single-threaded**.

We want:

- **Real parallelism (workers)**
    
- **Bounded memory**
    
- **Hard backpressure**
    
- **Still use streams**
    

So the architecture becomes:

```js
Readable Stream (main thread)
        │
        ▼
SharedArrayBuffer Ring Buffer
        │
        ▼
Worker (consumer / processor)

```

The stream **does not store data**.  
The ring buffer **does**.

---

# Key Design Insight (Very Important)

> **Streams signal backpressure with `.push()` / `.write()` returning false**  
> **Shared memory enforces backpressure with `Atomics.wait()`**

We must **bridge these two worlds**.

---

# Strategy

1. Wrap the **producer side** of the ring buffer in a `Readable`
    
2. Only call `push()` when space is available
    
3. Let the ring buffer block, not the stream
    
4. Use **objectMode or binary mode**, depending on use case
    

We’ll implement a **Readable stream backed by SharedArrayBuffer**.

---

# Memory Assumptions (Simplified)

- Ring buffer stores `Int32` values (easy to reason about)
    
- One producer (stream)
    
- One consumer (worker)
    

---

# File 1 — `sab-stream.js` (Readable Stream Wrapper)

```js
const { Readable } = require("stream");

class SABReadable extends Readable {
  constructor({ header, data, capacity }) {
    super({ objectMode: true });

    this.header = header;
    this.data = data;
    this.capacity = capacity;
  }

  _read() {
    while (true) {
      const write = Atomics.load(this.header, 0);
      const read = Atomics.load(this.header, 1);

      if (write === read) {
        // Buffer empty → stream naturally pauses
        Atomics.wait(this.header, 0, write);
        continue;
      }

      const value = this.data[read];
      const next = (read + 1) % this.capacity;

      Atomics.store(this.header, 1, next);
      Atomics.add(this.header, 3, 1); // consumedCount
      Atomics.notify(this.header, 1);

      // Push into Node stream
      const canContinue = this.push(value);

      if (!canContinue) {
        // Node stream backpressure kicks in
        return;
      }
    }
  }
}

module.exports = { SABReadable };

```

---

# Why This Works

- `_read()` is called **only when downstream is ready**
    
- `push(false)` stops reading
    
- Shared buffer blocks producer independently
    
- Two layers of backpressure:
    
    - Ring buffer (hard)
        
    - Stream (soft, compositional)
        

---

# File 2 — `main.js` (Producer + Stream Consumer)

```js
const { Worker } = require("worker_threads");
const { SABReadable } = require("./sab-stream");

const CAPACITY = 8;
const HEADER_FIELDS = 6;
const I32 = Int32Array.BYTES_PER_ELEMENT;

main();

function main() {
  const sab = new SharedArrayBuffer((HEADER_FIELDS + CAPACITY) * I32);

  const header = new Int32Array(sab, 0, HEADER_FIELDS);
  const data = new Int32Array(sab, HEADER_FIELDS * I32, CAPACITY);

  new Worker("./worker.js", { workerData: sab });

  const stream = new SABReadable({ header, data, capacity: CAPACITY });

  stream
    .map(x => x * 2)
    .on("data", (val) => {
      console.log("Stream consumed:", val);
    });
}

```

> Yes — streams can consume **shared-memory–backed data** safely.

---

# File 3 — `worker.js` (Producer into Ring Buffer)

```js
const { workerData } = require("worker_threads");

const CAPACITY = 8;
const HEADER_FIELDS = 6;
const I32 = Int32Array.BYTES_PER_ELEMENT;

const header = new Int32Array(workerData, 0, HEADER_FIELDS);
const data = new Int32Array(workerData, HEADER_FIELDS * I32, CAPACITY);

let value = 1;

setInterval(() => {
  while (true) {
    const write = Atomics.load(header, 0);
    const read = Atomics.load(header, 1);
    const next = (write + 1) % CAPACITY;

    if (next === read) {
      Atomics.add(header, 4, 1); // producerWaits
      Atomics.wait(header, 1, read);
      continue;
    }

    data[write] = value++;
    Atomics.store(header, 0, next);
    Atomics.add(header, 2, 1); // producedCount
    Atomics.notify(header, 0);
    break;
  }
}, 10);

```

---

# Backpressure: End-to-End View

```js
Worker produces →
  Ring buffer full →
    Worker blocks (Atomics.wait)

Stream downstream slow →
  push() returns false →
    _read pauses →
      No reads →
        Ring buffer fills →
          Worker blocks

```

This is **full pipeline backpressure**, across threads.

---

# Why This Is Powerful

- Zero-copy
    
- Bounded memory
    
- Stream composition
    
- Parallel CPU usage
    
- Deterministic behavior
    

You now have **a real multi-threaded stream pipeline**.

---

# What This Is NOT

❌ This is not async iteration  
❌ This is not message passing  
❌ This is not event-loop backpressure  
❌ This is not “just streams”

This is **shared-memory streaming**.

---

# When You Should Use This Pattern

Use this when:

- CPU-heavy transforms
    
- Media pipelines
    
- Binary protocols
    
- High-throughput ingestion
    
- Predictable latency matters
    

Avoid when:

- Simplicity matters more than determinism
    
- Workload is light
    
- One thread is enough
    

---

# Final Mental Model (Lock It In)

> **Streams control flow**  
> **Ring buffers control memory**  
> **Atomics control correctness**  
> **Workers give parallelism**

This is how **real streaming systems** are built.