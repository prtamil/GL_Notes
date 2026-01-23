# Introduction — What We Are Building and Why

Modern systems fail **not because they are slow**, but because they **cannot handle pressure**.

Backpressure answers one question:

> _What happens when the producer is faster than the consumer?_

In this guide, we will build **two real systems** that answer that question differently:

1. **SharedArrayBuffer + Atomics ring buffer**
    
2. **postMessage + transferable ArrayBuffer**
    

Both are:

- Zero-copy
    
- Cross-thread
    
- Real Node.js worker communication
    

But they differ **fundamentally** in:

- Memory ownership
    
- Blocking behavior
    
- Predictability
    
- Observability
    

Our goal is to:

- Make backpressure **observable**
    
- Measure **where pressure accumulates**
    
- Compare **hard vs soft backpressure**
    
- Understand **when each model breaks**
    

---

# What You Will Achieve by the End

After this guide, you will be able to:

- Explain **what backpressure actually is** (not abstractly)
    
- Measure backpressure with **real metrics**
    
- Build a **bounded, deterministic pipeline**
    
- Understand why **zero-copy alone is not enough**
    
- Choose correctly between **shared memory** and **message passing**
    

This is **systems-level Node.js**, not app-level patterns.

---

# PART 1 — Backpressure Metrics (Why They Exist)

Backpressure is **observable pressure** in the system, not theory.

We measure:

|Metric|Meaning|
|---|---|
|`producedCount`|Total items produced|
|`consumedCount`|Total items consumed|
|`producerWaits`|Producer blocked (buffer full)|
|`consumerWaits`|Consumer blocked (buffer empty)|
|`queueDepth`|Current pressure|
|`throughput/sec`|System capacity|

These metrics answer:

- Who is slower?
    
- Where contention happens?
    
- Whether buffer capacity is correct?
    
- Whether zero-copy helps _in practice_?
    

---

# PART 2 — SharedArrayBuffer Ring Buffer (Hard Backpressure)

## System Architecture (Bird’s-Eye View)

```js
Main Thread (Producer)
  └─ writes data
  └─ blocks when full

Worker Thread (Consumer)
  └─ reads data
  └─ blocks when empty

SharedArrayBuffer
  ├─ indices
  ├─ metrics
  └─ data (ring buffer)

```

This system has **bounded memory** and **deterministic behavior**.

---

## Memory Layout (Shared)

```js
[ writeIndex,
  readIndex,
  producedCount,
  consumedCount,
  producerWaits,
  consumerWaits,
  data... ]

```

All metrics live **inside shared memory** → zero-copy observability.

---

## producer.js — With a Clear “Main Flow”

```js
// producer.js
const { Worker, isMainThread } = require("worker_threads");

const CAPACITY = 8;
const HEADER_FIELDS = 6;
const I32 = Int32Array.BYTES_PER_ELEMENT;

if (isMainThread) {
  main();
}

function main() {
  const sab = createSharedMemory();
  spawnConsumer(sab);

  const { header, data } = mapViews(sab);

  startProducerLoop(header, data);
  startMetricsReporter(header);
}

function createSharedMemory() {
  return new SharedArrayBuffer((HEADER_FIELDS + CAPACITY) * I32);
}

function spawnConsumer(sab) {
  new Worker("./consumer.js", { workerData: sab });
}

function mapViews(sab) {
  return {
    header: new Int32Array(sab, 0, HEADER_FIELDS),
    data: new Int32Array(sab, HEADER_FIELDS * I32, CAPACITY),
  };
}

function startProducerLoop(header, data) {
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
  }, 5);
}

function startMetricsReporter(header) {
  setInterval(() => {
    const produced = Atomics.load(header, 2);
    const consumed = Atomics.load(header, 3);

    console.log({
      produced,
      consumed,
      producerWaits: Atomics.load(header, 4),
      consumerWaits: Atomics.load(header, 5),
      queueDepth: (produced - consumed + CAPACITY) % CAPACITY,
    });
  }, 1000);
}

```

---

## consumer.js — Clear Consumption Loop

```js
// consumer.js
const { workerData } = require("worker_threads");

const CAPACITY = 8;
const HEADER_FIELDS = 6;
const I32 = Int32Array.BYTES_PER_ELEMENT;

main(workerData);

function main(sab) {
  const header = new Int32Array(sab, 0, HEADER_FIELDS);
  const data = new Int32Array(sab, HEADER_FIELDS * I32, CAPACITY);

  while (true) consume(header, data);
}

function consume(header, data) {
  while (true) {
    const write = Atomics.load(header, 0);
    const read = Atomics.load(header, 1);

    if (write === read) {
      Atomics.add(header, 5, 1); // consumerWaits
      Atomics.wait(header, 0, write);
      continue;
    }

    const next = (read + 1) % CAPACITY;
    Atomics.store(header, 1, next);
    Atomics.add(header, 3, 1); // consumedCount
    Atomics.notify(header, 1);
    break;
  }
}

```

---

## How to Interpret Results

- `producerWaits ↑` → consumer is the bottleneck
    
- `consumerWaits ↑` → producer is the bottleneck
    
- `queueDepth ≈ capacity` → sustained pressure
    
- `produced ≈ consumed` → healthy pipeline
    

This is **real backpressure** — the producer _physically cannot outrun_ the consumer.

---

# PART 3 — postMessage + Transfer (Soft Backpressure)

## System Architecture

```js
Producer Thread
  └─ allocates buffer
  └─ sends message

Consumer Thread
  └─ receives message
  └─ event-loop driven

```

No shared state. No blocking. No bounds.

---

## producer_transfer.js (Main Flow)

```js
const { Worker } = require("worker_threads");

main();

function main() {
  const worker = new Worker("./consumer_transfer.js");

  let produced = 0;
  let blocked = 0;

  setInterval(() => {
    const buf = new ArrayBuffer(4);
    new Int32Array(buf)[0] = ++produced;

    if (!worker.postMessage(buf, [buf])) {
      blocked++;
    }
  }, 5);

  setInterval(() => {
    console.log({ produced, blocked });
  }, 1000);
}

```

---

## consumer_transfer.js

```js
const { parentPort } = require("worker_threads");

let consumed = 0;

parentPort.on("message", () => {
  consumed++;
});

setInterval(() => {
  console.log({ consumed });
}, 1000);

```

---

## What You Observe Here

- Producer never blocks
    
- Queue can grow indefinitely
    
- Memory usage can spike
    
- Latency becomes unpredictable
    

This is **soft backpressure** — pressure is absorbed by memory.

---

# Final Mental Model (Memorize This)

> **SharedArrayBuffer = shared state + hard limits**  
> **postMessage = message passing + elastic memory**  
> **Atomics enforce correctness**  
> **wait/notify enforce pressure**  
> **Ring buffers enforce bounds**

---

## Bottom Line

- Zero-copy ≠ safe
    
- Throughput ≠ stability
    
- Bounded systems beat fast systems
    
- Backpressure must be **designed**, not hoped for