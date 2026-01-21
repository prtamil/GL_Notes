# When Async Iteration Breaks Down at Scale

## Executive Warning

> Async iteration optimizes for **correctness and clarity**, not **throughput**.

If you push it into high-volume, low-latency, multi-core workloads, it will quietly become your bottleneck.

---

## 1. Sequential Consumption Becomes the Ceiling

### The core limitation

```js
for await (const chunk of stream) {
  await process(chunk);
}

```

This is **strictly serial**.

At scale:

- One slow chunk = whole pipeline slows
- CPU cores sit idle
- Network parallelism is wasted
    

### Symptoms in production

- Low CPU utilization (<30%)
- Growing upstream queues
- Latency increasing linearly with load
    

### Why this happens

Async iteration enforces:

- One item in flight
- One promise awaited
- One execution path
    

This is _perfect backpressure_ — and terrible throughput.

---

## 2. Implicit Backpressure Turns Into Over-Throttling

Async iteration applies **absolute backpressure**.

That’s great until:

- Upstream systems expect buffering
- Network I/O could overlap
- Latency hiding is needed
    

### Example: HTTP streaming

```js
for await (const chunk of response.body) {
  await writeToDisk(chunk);
}

```

If disk is slow:

- TCP window shrinks
- Sender throttles
- Network utilization collapses
    

Streams would buffer. Async iteration **refuses to**.

At scale, this kills throughput.

---

## 3. No Built-In Parallelism Model

Async iteration gives you **zero structure for concurrency**.

Developers then do this:

```js
for await (const chunk of stream) {
  process(chunk); // fire and forget ❌
}

```

Now you have:

- Unbounded concurrency
- Memory spikes
- No backpressure
- Hard-to-debug crashes
    

Or this:

```js
await Promise.all([...]) // ❌ explodes memory

```

Async iteration **forces you to invent**:

- Concurrency limits
- Retry logic
- Ordering guarantees
    

Streams already have these primitives.

---

## 4. High-Frequency Small Chunks = Death by Await

Async iteration has **per-item await overhead**.

At scale:

- Millions of small chunks
- Each `await` = microtask + promise resolution
- Event loop becomes saturated
    

### Example failure mode

- JSON logs, 100 bytes each
- 5M logs/min
- Async iteration spends more time scheduling than processing
    

Streams batch naturally.  
Async iteration does not.

---

## 5. Object Mode Overhead Multiplies

Async generators are effectively **always object mode**.

At scale:

- More allocations
- More GC pressure
- Worse cache locality
    

Binary streams:

- Reuse buffers
- Zero-copy
- OS-optimized
    

This difference is invisible at small scale — brutal at large scale.

---

## 6. Fan-Out Pipelines Become Complex and Fragile

Async iteration is **single-consumer by design**.

Now imagine:

- Metrics
- Persistence
- Real-time alerts
- Audit logs
    

With streams:

```js
readable
  .pipe(a)
  .pipe(b)

```

With async iteration:

- You must manually tee
- Copy data
- Handle failures per branch
    

At scale, this complexity explodes.

---

## 7. Lack of Native Flow Metrics & Instrumentation

Streams expose:

- `highWaterMark`
- `bufferLength`
- `drain` events
    

Async iteration exposes:

- Nothing
    

At scale, observability matters.  
Async iteration gives you **no levers**.

You cannot:

- Inspect queue depth
- Predict memory pressure
- Tune flow behavior
    

---

## 8. GC & Memory Fragmentation at Sustained Load

Long-running async iteration pipelines:

- Create many short-lived promises
- Fragment heap
- Trigger frequent GC pauses
    

Streams reuse internal buffers and queues.  
Async iteration does not.

This shows up only under **hours or days of load**.

---

## 9. Cross-Service Backpressure Propagation Fails

Async iteration works **inside one process**.

At scale:

- Microservices
- Message brokers
- Queues
    

Backpressure must propagate **across boundaries**.

Async iteration cannot:

- Signal Kafka
- Signal SQS
- Signal upstream HTTP senders
    

Streams integrate better with:

- TCP flow control
- Kernel buffers
- OS scheduling
    

---

## 10. The “Looks Fine in Load Tests” Trap

Async iteration often:

- Passes unit tests
- Passes load tests
- Fails in real traffic
    

Why?

- Load tests are bursty
- Production is sustained
- GC and drift accumulate over time
    

This is one of the most dangerous failure modes.

---

## When Async Iteration Is Still the Right Tool

Async iteration **does not scale poorly everywhere**.

It scales well when:

- Data volume is moderate
- Logic is heavy
- I/O latency dominates
- Correctness > throughput
- Backpressure must be strict
    

Examples:

- ETL steps
- Business rules
- API request processing
- Admin pipelines
- One-off jobs
    

---

## The Correct Scalable Pattern (This Is Critical)

### Streams for I/O

### Async iteration for logic

### Controlled parallelism in between

```js
import pLimit from 'p-limit';

const limit = pLimit(16);

for await (const chunk of stream) {
  await limit(() => process(chunk));
}

```

This:

- Preserves backpressure
- Allows overlap
- Prevents overload
- Scales predictably
    

---

## Red Flags You’ve Outgrown Async Iteration

- CPU underutilized
- Latency grows with volume
- Memory spikes under load
- GC pauses increase
- Network throughput drops
- You add `Promise.all` hacks
    

When you see these, **switch models**.

---

## Final Truth (No Sugarcoating)

> Async iteration is a scalpel.  
> Streams are heavy machinery.

Use async iteration:

- For control
- For clarity
- For correctness
    

Use streams:

- For volume
- For speed
- For sustained throughput
    

If you try to make async iteration do the job of streams at scale, it won’t fail loudly — it will fail _slowly_.

That’s the most dangerous kind.