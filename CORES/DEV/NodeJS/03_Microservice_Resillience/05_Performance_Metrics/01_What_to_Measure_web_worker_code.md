> _“What does performance actually mean, and how do I measure it correctly?”_

Most people guess. You’re doing it right.

I’ll give you **three things**, in order:

1. **What to measure** (clear checklist you can reuse forever)
2. **Express (HTTP webapp) performance measurement code**
3. **Worker / background Node.js performance measurement code**
    

All code is **minimal, production-realistic, single-file**, and reusable.

---

# 1️⃣ What to Measure (This Is the Canonical List)

Think in **layers**, not tools.

---

## A. Latency (How fast)

|Metric|Meaning|Why it matters|
|---|---|---|
|Request latency (avg)|Typical response time|User experience|
|p95 / p99 latency|Worst-case tail|Real SLA indicator|
|Time to first byte (TTFB)|When response starts|Streaming & perceived speed|
|Event loop delay|JS is blocked|CPU overload signal|

---

## B. Throughput (How much)

|Metric|Meaning|
|---|---|
|Requests/sec|HTTP capacity|
|Jobs/sec|Worker capacity|
|Bytes/sec|IO efficiency|

---

## C. Resource Usage (How expensive)

|Metric|Meaning|
|---|---|
|RSS memory|True memory usage|
|Heap used|JS objects|
|CPU %|Saturation|
|GC pauses|Memory pressure|

---

## D. Stability / Backpressure

|Metric|Meaning|
|---|---|
|In-flight requests|Load handling|
|Queue depth|Overload signal|
|Dropped / failed jobs|System limits|
|Worker lag|CPU starvation|

---

## E. System Health (Often Ignored)

|Metric|Meaning|
|---|---|
|Event loop lag|Node responsiveness|
|Open handles|Resource leaks|
|File/socket pressure|OS bottlenecks|

---

> **If you measure these, you are doing real performance engineering.**

Now let’s **measure them properly**.

---

# 2️⃣ Express Web App Performance Measurement (HTTP)

## What This Code Measures

✔ Request latency (avg, p95)  
✔ Throughput (req/sec)  
✔ RSS + heap  
✔ Event loop delay  
✔ In-flight requests

---

## ✅ Express Performance Instrumentation (Single File)
```js
/**
 * express-perf.js
 * Run: node express-perf.js
 */

const express = require('express');
const { monitorEventLoopDelay, performance } = require('perf_hooks');

const app = express();
const port = 3000;

// =====================
// METRICS
// =====================
let requests = 0;
let inFlight = 0;
let latencies = [];

const elDelay = monitorEventLoopDelay();
elDelay.enable();

// =====================
// MIDDLEWARE
// =====================
app.use((req, res, next) => {
  const start = performance.now();
  inFlight++;

  res.on('finish', () => {
    const duration = performance.now() - start;
    latencies.push(duration);
    requests++;
    inFlight--;
  });

  next();
});

// =====================
// ROUTE
// =====================
app.get('/work', (req, res) => {
  // Simulate CPU + IO
  for (let i = 0; i < 5_000_000; i++);
  res.json({ ok: true });
});

// =====================
// REPORTER
// =====================
setInterval(() => {
  const { rss, heapUsed } = process.memoryUsage();
  const avg =
    latencies.reduce((a, b) => a + b, 0) / (latencies.length || 1);

  latencies.sort((a, b) => a - b);
  const p95 = latencies[Math.floor(latencies.length * 0.95)] || 0;

  console.log({
    reqPerSec: requests,
    avgLatencyMs: avg.toFixed(2),
    p95LatencyMs: p95.toFixed(2),
    inFlight,
    rssMB: Math.round(rss / 1024 / 1024),
    heapMB: Math.round(heapUsed / 1024 / 1024),
    eventLoopDelayMs: (elDelay.mean / 1e6).toFixed(2)
  });

  // reset counters
  requests = 0;
  latencies = [];
  elDelay.reset();
}, 1000);

// =====================
// START
// =====================
app.listen(port, () => {
  console.log(`Express app running on port ${port}`);
});

```

---

## How to Use This (Important)

Run load:

```js
autocannon -c 50 -d 30 http://localhost:3000/work

```

Watch:

- p95 latency → overload signal
- event loop delay → CPU saturation
- RSS → memory leaks
    

---

## Interview-level insight

> “Latency percentiles and event loop delay matter more than averages in Node.”

That’s correct and senior-level.

---

# 3️⃣ Worker / Background Job Performance Measurement

Now let’s measure **non-HTTP workloads** (queues, jobs, ETL, workers).

---

## What This Measures

✔ Jobs/sec  
✔ Job latency  
✔ Queue depth  
✔ CPU isolation health  
✔ Memory stability

---

## ✅ Worker Performance Harness (Single File)

```js
/**
 * worker-perf.js
 * Run: node worker-perf.js
 */

const { Worker } = require('worker_threads');
const { performance } = require('perf_hooks');

// =====================
// METRICS
// =====================
let completed = 0;
let latencies = [];
let queueDepth = 0;
let peakRSS = 0;

// =====================
// WORKER
// =====================
const worker = new Worker(`
  const { parentPort } = require('worker_threads');

  parentPort.on('message', ({ start }) => {
    // Simulate CPU-heavy job
    for (let i = 0; i < 20_000_000; i++);
    parentPort.postMessage({ start });
  });
`, { eval: true });

// =====================
// PRODUCER
// =====================
function enqueueJob() {
  queueDepth++;
  worker.postMessage({ start: performance.now() });
}

setInterval(enqueueJob, 50); // control load here

// =====================
// CONSUMER
// =====================
worker.on('message', ({ start }) => {
  const duration = performance.now() - start;
  latencies.push(duration);
  completed++;
  queueDepth--;
});

// =====================
// REPORTER
// =====================
setInterval(() => {
  const { rss, heapUsed } = process.memoryUsage();
  peakRSS = Math.max(peakRSS, rss);

  const avg =
    latencies.reduce((a, b) => a + b, 0) / (latencies.length || 1);

  latencies.sort((a, b) => a - b);
  const p95 = latencies[Math.floor(latencies.length * 0.95)] || 0;

  console.log({
    jobsPerSec: completed,
    avgLatencyMs: avg.toFixed(2),
    p95LatencyMs: p95.toFixed(2),
    queueDepth,
    rssMB: Math.round(rss / 1024 / 1024),
    heapMB: Math.round(heapUsed / 1024 / 1024),
    peakRSS_MB: Math.round(peakRSS / 1024 / 1024)
  });

  completed = 0;
  latencies = [];
}, 1000);

```

---

## How to Read Worker Metrics (Critical)

- **Queue depth growing** → overload
- **Latency increasing** → CPU saturation
- **RSS climbing** → buffering bug
- **Jobs/sec flat** → throughput ceiling
    

---

# 4️⃣ What to Say in Interviews (Memorize This)

> “For web apps, I measure latency percentiles, throughput, event loop delay, and memory.  
> For workers, I measure job latency, queue depth, throughput, and RSS stability.  
> A system is fast only if it stays predictable under load.”

That answer is **excellent**.

---

# 5️⃣ Final Mental Model (This Is the Gold)

- **Latency tells you user pain**
- **Throughput tells you capacity**
- **Memory tells you survivability**
- **Event loop delay tells you truth**