# Writable Stream → SharedArrayBuffer

(**Hard backpressure, zero-copy, cross-thread**)

## What We’re Solving

Previously, we did:

> **SharedArrayBuffer → Readable stream**

Now we want the inverse:

> **Writable stream → SharedArrayBuffer**

This lets you do things like:

```js
fs.createReadStream()
  .pipe(transform)
  .pipe(sharedMemorySink)

```

Where:

- The **stream pipeline stays idiomatic**
    
- The **actual storage is bounded shared memory**
    
- The **producer blocks when memory is full**
    
- A worker consumes data in parallel
    

This is how you turn **Node streams into real multi-threaded pipelines**.

---

# High-Level Architecture

```js
Writable Stream (main thread)
        │
        ▼
SharedArrayBuffer Ring Buffer
        │
        ▼
Worker Thread (consumer)

```

Key rule:

> **Writable._write() must block when the ring buffer is full**

That’s how we bridge:

- Stream backpressure
    
- Atomics-based backpressure
    

---

# Critical Design Insight (Do Not Skip)

Node writable streams signal backpressure by:

- Delaying the `_write` callback
    

Shared memory signals backpressure by:

- Blocking with `Atomics.wait`
    

So our job is simple but strict:

> **Call `callback()` only after data is safely written into the ring buffer**

If the buffer is full:

- We **do not call callback**
    
- We **block**
    
- The upstream stream naturally pauses
    

---

# Assumptions (To Keep It Focused)

- Binary data: `Int32`
    
- One producer (stream)
    
- One consumer (worker)
    
- Same ring buffer layout as before
    

---

# Memory Layout (Same as Before)

```js
[ writeIndex,
  readIndex,
  producedCount,
  consumedCount,
  producerWaits,
  consumerWaits,
  data... ]

```

---

# File 1 — `sab-writable.js`

This is the **core abstraction**.

```js
const { Writable } = require("stream");

class SABWritable extends Writable {
  constructor({ header, data, capacity }) {
    super({ objectMode: true });

    this.header = header;
    this.data = data;
    this.capacity = capacity;
  }

  _write(chunk, _enc, callback) {
    // chunk is a value (Int32 in our case)
    while (true) {
      const write = Atomics.load(this.header, 0);
      const read = Atomics.load(this.header, 1);
      const next = (write + 1) % this.capacity;

      if (next === read) {
        // Ring buffer full → hard backpressure
        Atomics.add(this.header, 4, 1); // producerWaits
        Atomics.wait(this.header, 1, read);
        continue;
      }

      // Write into shared memory
      this.data[write] = chunk;

      Atomics.store(this.header, 0, next);
      Atomics.add(this.header, 2, 1); // producedCount
      Atomics.notify(this.header, 0);

      // Signal stream that write completed
      callback();
      return;
    }
  }
}

module.exports = { SABWritable };

```

---

# Why This Is Correct

- `_write` **does not return until space exists**
    
- The stream **automatically pauses upstream**
    
- No buffering inside the stream
    
- Memory is **strictly bounded**
    
- Zero-copy (shared memory)
    

This is **hard backpressure**, not advisory.

---

# File 2 — `main.js` (Stream Producer)

This simulates a normal Node stream pipeline.

```js
const { Worker } = require("worker_threads");
const { Readable } = require("stream");
const { SABWritable } = require("./sab-writable");

const CAPACITY = 8;
const HEADER_FIELDS = 6;
const I32 = Int32Array.BYTES_PER_ELEMENT;

main();

function main() {
  const sab = new SharedArrayBuffer((HEADER_FIELDS + CAPACITY) * I32);

  const header = new Int32Array(sab, 0, HEADER_FIELDS);
  const data = new Int32Array(sab, HEADER_FIELDS * I32, CAPACITY);

  // Start consumer
  new Worker("./worker.js", { workerData: sab });

  const writable = new SABWritable({ header, data, capacity: CAPACITY });

  // Normal Node readable stream
  const readable = Readable.from(generateNumbers(), { objectMode: true });

  readable.pipe(writable);
}

function* generateNumbers() {
  let i = 1;
  while (true) {
    yield i++;
  }
}

```

This is **100% idiomatic Node streams**.

No worker logic leaks into stream code.

---

# File 3 — `worker.js` (Consumer)

```js
const { workerData } = require("worker_threads");

const CAPACITY = 8;
const HEADER_FIELDS = 6;
const I32 = Int32Array.BYTES_PER_ELEMENT;

const header = new Int32Array(workerData, 0, HEADER_FIELDS);
const data = new Int32Array(workerData, HEADER_FIELDS * I32, CAPACITY);

main();

function main() {
  while (true) {
    consume();
  }
}

function consume() {
  while (true) {
    const write = Atomics.load(header, 0);
    const read = Atomics.load(header, 1);

    if (write === read) {
      Atomics.add(header, 5, 1); // consumerWaits
      Atomics.wait(header, 0, write);
      continue;
    }

    const value = data[read];
    const next = (read + 1) % CAPACITY;

    // Simulate work
    busyWork();

    Atomics.store(header, 1, next);
    Atomics.add(header, 3, 1); // consumedCount
    Atomics.notify(header, 1);

    break;
  }
}

function busyWork() {
  const end = Date.now() + 20;
  while (Date.now() < end);
}

```

---

# End-to-End Backpressure Flow

```js
Readable stream fast →
  Writable._write blocks →
    upstream pauses →

Ring buffer full →
  Atomics.wait →
    producer sleeps →

Consumer slow →
  queueDepth rises →
    producerWaits increase

```

Nothing grows unbounded. Ever.

---

# Why This Pattern Is Powerful

You now have:

- Node stream ergonomics
    
- Worker parallelism
    
- Shared memory speed
    
- Deterministic memory usage
    
- Real backpressure across threads
    

This is **not common Node.js code** — this is **systems code**.

---

# What This Enables in Real Life

- `fs.createReadStream()` → CPU worker
    
- Network ingestion with bounded memory
    
- Media pipelines (audio/video frames)
    
- Telemetry ingestion
    
- Binary protocol decoding
    

All **without copies** and **without queues exploding**.

---

# Final Mental Model (Lock This In)

> **Writable streams control upstream flow**  
> **SharedArrayBuffer controls memory bounds**  
> **Atomics enforce correctness**  
> **Workers consume in parallel**

You’ve now completed the **full duplex bridge** between:

- Node streams
    
- Shared memory
    
- Hard backpressure