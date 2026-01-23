# libuv Threadpool (The Hidden Workers)

## Why this matters

> **Not all async is I/O.**

Many Node developers believe:

> “If it’s async, it won’t block.”

That belief is **dangerously incomplete**.

Node.js has **two execution worlds**:

1. **Event Loop (single-threaded JS)**
2. **libuv Threadpool (hidden worker threads)**
    

If you don’t understand the threadpool:

- You’ll see **CPU spikes with “async” code**
- Your app will **stall under load**
- Latency will explode even though nothing “blocks” JS
    

---

## Big Picture: Where libuv fits

```js
┌───────────────┐
│ JavaScript    │  (single thread)
│ Event Loop    │
└───────┬───────┘
        │ offloads work
        ▼
┌───────────────────┐
│ libuv Threadpool  │  (default: 4 threads)
│                   │
│  fs / crypto      │
│  dns / zlib       │
└───────────────────┘

```

The event loop **delegates work** it cannot do efficiently:

- Blocking syscalls
- CPU-heavy native operations
    

But the pool is **finite**.

---

## What uses the libuv threadpool?

These APIs look async, but **run on worker threads**:

### 1. File system (`fs`)

```js
fs.readFile()
fs.writeFile()
fs.stat()

```

### 2. Crypto

```js
crypto.pbkdf2()
crypto.scrypt()
crypto.randomBytes()

```

### 3. DNS (not all)

```js
dns.lookup()   // uses threadpool
dns.resolve() // uses OS async resolver (no pool)

```

### 4. Compression

```js
zlib.gzip()
zlib.inflate()

```

⚠️ **Important:**  
These do **real CPU work**. They do **not magically disappear**.

---

## Why only 4 threads by default?

### Historical reason

- libuv optimized for **low memory**
- Cross-platform consistency
- Most servers were not CPU-heavy
    

### Reality today

- 4 threads is **too small** for modern workloads
- Especially for:
    
    - password hashing
    - compression
    - file-heavy services
        

---

## Core rule (burn this into memory)

> **Async does not mean parallel at scale**

Async means:

- JS is not blocked
    

It does **not** mean:

- Unlimited concurrency
- No CPU contention
- No throughput collapse
    

---

## Demonstration: Crypto blocking throughput

### Example: password hashing

```js
const crypto = require('crypto');

function hashPassword(id) {
  crypto.pbkdf2('password', 'salt', 100_000, 64, 'sha512', () => {
    console.log(`done ${id}`);
  });
}

for (let i = 0; i < 8; i++) {
  hashPassword(i);
}

```

### What happens?

- Only **4 tasks run at a time**
- Remaining tasks **queue**
- Completion order comes in **waves**
    

```js
done 0
done 1
done 2
done 3
(done pause)
done 4
done 5
done 6
done 7

```

This is **throughput bottleneck**, not blocking.

---

## Real-world failure: API slowdown

Imagine an API that:

- hashes passwords
- compresses responses
- reads files
    

Under load:

- Threadpool saturates
- Requests wait for workers
- Latency skyrockets
- CPU spikes even though JS is idle
    

---

## Visualizing threadpool saturation

### Simulate heavy fs usage

```js
const fs = require('fs');

for (let i = 0; i < 10; i++) {
  fs.readFile(__filename, () => {
    console.log(`read ${i}`);
  });
}

```

Even on SSD:

- Only **4 reads at once**
- Others wait
    

This is why:

> “My async fs code is slow under load”

---

## Event loop is free — workers are not

This explains a common mystery:

> “CPU is high but event loop lag is low”

Why?

- Work is happening in **libuv threads**
- JS loop is idle
- Monitoring only event loop misses it
    

---

## DNS gotcha (very common)

```js
const dns = require('dns');

dns.lookup('example.com', () => {
  console.log('lookup done');
});

```

`dns.lookup()`:

- Uses **threadpool**
- Can block throughput under load
    

Better for high-scale systems:

```js
dns.resolve('example.com', cb);

```

---

## zlib: silent CPU eater

```js
const zlib = require('zlib');

zlib.gzip(largeBuffer, () => {
  console.log('compressed');
});

```

Compression:

- CPU-heavy
- Uses threadpool
- Can stall unrelated async work
    

This is why:

- Large response compression under load hurts APIs
    

---

## Increasing threadpool size (with caution)

```js
UV_THREADPOOL_SIZE=16 node server.js

```

### Rules:

- Max: **128**
- Must be set **before Node starts**
- More threads ≠ free performance
    

### Tradeoffs:

- Context switching
- Memory usage
- Can hurt if CPU cores are limited
    

---

## Mental model: queue + workers

```js
Incoming async tasks
        │
        ▼
┌───────────────────┐
│ Threadpool queue  │  ← backlog grows here
└───────┬───────────┘
        ▼
┌───────────────────┐
│ Worker threads    │  ← fixed count
└───────────────────┘

```

Latency = queue time + execution time

---

## When “async” still blocks throughput

**Async blocks throughput when:**

1. Task is CPU-heavy
2. Uses libuv threadpool
3. Concurrency > thread count
    

This is **the most common Node performance trap**.

---

## Production patterns to survive

### 1. Limit concurrency manually

```js
import pLimit from 'p-limit';

const limit = pLimit(2);

limit(() => crypto.pbkdf2(...));

```

### 2. Move heavy work off Node

- Dedicated worker service
- Job queues (BullMQ, SQS)
- Native services (Rust/Go)
    

### 3. Use worker_threads for CPU-heavy JS

Threadpool is **not configurable per task**.

---

## Final takeaway

> **Node is single-threaded by design, multi-threaded by necessity**

libuv threadpool:

- Saves Node from blocking
- Introduces hidden contention
- Explains mysterious CPU spikes
- Determines real scalability limits
    

If you understand this:

- You stop blaming the event loop
- You design APIs that survive load
- You debug performance like a senior engineer