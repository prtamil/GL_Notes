# Full Observability Toolkit (Node.js)

> **Goal:**  
> _Know when the event loop is unhealthy, why it’s unhealthy, and which work caused it — before users complain._

---

## Mental Model First (Read This Once)

Node.js observability revolves around **one truth**:

> **Everything bad eventually shows up as event loop delay.**

But delay has **causes**, not magic:

- CPU saturation
- Synchronous JS
- GC pressure
- Promise storms
- Memory retention
- Runaway async chains
    

So we build observability as **progressive zoom**:

```js
Event loop delay
   ↓
CPU / Memory / GC
   ↓
Request latency
   ↓
Async causality
   ↓
Heap & CPU forensics

```

---

# Layer 1 — Event Loop Observability (The Heartbeat)

## Question it answers

> “Is Node making forward progress?”

### Why this is mandatory

CPU can be low and Node can still be **frozen**.  
Event loop delay never lies.

---

## Code: Event Loop Lag Monitor

```js
// observability/eventLoop.js
const { monitorEventLoopDelay } = require('perf_hooks');

const histogram = monitorEventLoopDelay({ resolution: 20 });
histogram.enable();

function getEventLoopMetrics() {
  const metrics = {
    meanMs: Math.round(histogram.mean / 1e6),
    p95Ms: Math.round(histogram.percentile(95) / 1e6),
    p99Ms: Math.round(histogram.percentile(99) / 1e6),
    maxMs: Math.round(histogram.max / 1e6),
  };
  histogram.reset();
  return metrics;
}

module.exports = { getEventLoopMetrics };

```

### Usage

```js
setInterval(() => {
  console.log('event_loop', getEventLoopMetrics());
}, 5000);

```

### How to interpret

|Signal|Meaning|
|---|---|
|p99 < 20ms|Healthy|
|p99 spikes|Blocking JS|
|mean rising|Sustained pressure|
|max spikes|GC or sync I/O|

📌 **This metric alone catches 80% of Node outages.**

---

# Layer 2 — Process & Runtime Metrics

## Question it answers

> “Is the loop slow because of CPU, memory, or GC?”

---

## Code: CPU & Memory

```js
// observability/process.js
let lastCpu = process.cpuUsage();

function getProcessMetrics() {
  const cpu = process.cpuUsage(lastCpu);
  lastCpu = process.cpuUsage();

  const mem = process.memoryUsage();

  return {
    cpuUserMs: Math.round(cpu.user / 1000),
    cpuSystemMs: Math.round(cpu.system / 1000),
    rssMb: Math.round(mem.rss / 1024 / 1024),
    heapUsedMb: Math.round(mem.heapUsed / 1024 / 1024),
    heapTotalMb: Math.round(mem.heapTotal / 1024 / 1024),
  };
}

module.exports = { getProcessMetrics };

```

### Usage

```js
setInterval(() => {
  console.log('process', getProcessMetrics());
}, 5000);

```

### Patterns to learn

- CPU ↑ + loop lag ↑ → synchronous JS
- Heap ↑ + loop lag ↑ → GC pressure
- RSS ↑, heap stable → native memory leak
    

---

# Layer 3 — HTTP / Request Observability

## Question it answers

> “Which requests are slow for users?”

---

## Code: Request Timing Middleware (Express)

```js
// observability/httpMetrics.js
module.exports = function httpMetrics(req, res, next) {
  const start = process.hrtime.bigint();

  res.on('finish', () => {
    const durationMs =
      Number(process.hrtime.bigint() - start) / 1e6;

    console.log('http_request', {
      method: req.method,
      path: req.route?.path || req.path,
      status: res.statusCode,
      durationMs: Math.round(durationMs),
    });
  });

  next();
};

```

### Usage

```js
app.use(require('./observability/httpMetrics'));

```

### Why this matters

You correlate:

- **User pain** ↔ **event loop health**
- Slow endpoints ↔ blocking code paths
    

---

# Layer 4 — Async Context & Causality

## Question it answers

> “Which request caused this async work?”

This is where **most teams fail**.

---

## Code: AsyncLocalStorage Context

```js
// observability/context.js
const { AsyncLocalStorage } = require('async_hooks');
const crypto = require('crypto');

const als = new AsyncLocalStorage();

function contextMiddleware(req, res, next) {
  als.run({ requestId: crypto.randomUUID() }, next);
}

function getContext() {
  return als.getStore();
}

module.exports = { contextMiddleware, getContext };

```

### Usage

```js
app.use(contextMiddleware);

function log(msg) {
  const ctx = getContext();
  console.log(ctx?.requestId, msg);
}

```

### Why this is powerful

Now:

- Logs
- Metrics
- Errors
    

…can all be tied to **one request**.

---

# Layer 5 — Event Loop Blocking Detection

## Question it answers

> “What blocked the loop just now?”

---

## Code: Manual Lag Probe

```js
// observability/lagProbe.js
let last = process.hrtime.bigint();

setInterval(() => {
  const now = process.hrtime.bigint();
  const delayMs = Number(now - last) / 1e6 - 100;
  last = now;

  if (delayMs > 50) {
    console.warn('event_loop_blocked', { delayMs });
  }
}, 100);

```

### Why this exists

This catches **short freezes** that averages hide.

---

# Layer 6 — CPU Profiling (Forensics)

## Question it answers

> “Which JS function burned the CPU?”

---

## Code: On-Demand CPU Profile

```js
// observability/cpuProfile.js
const inspector = require('inspector');
const fs = require('fs');

function startCpuProfile(durationMs = 30000) {
  const session = new inspector.Session();
  session.connect();

  session.post('Profiler.enable', () => {
    session.post('Profiler.start');

    setTimeout(() => {
      session.post('Profiler.stop', (_, { profile }) => {
        fs.writeFileSync(
          `cpu-${Date.now()}.cpuprofile`,
          JSON.stringify(profile)
        );
        process.exit(0);
      });
    }, durationMs);
  });
}

module.exports = { startCpuProfile };

```

### Usage

```js
if (process.env.CPU_PROFILE === '1') {
  require('./observability/cpuProfile').startCpuProfile();
}

```

Open `.cpuprofile` in Chrome DevTools.

---

# Layer 7 — Heap Snapshots (Memory Leaks)

## Question it answers

> “Why didn’t memory go down?”

---

## Code: Heap Snapshot

```js
// observability/heapSnapshot.js
const inspector = require('inspector');
const fs = require('fs');

function takeHeapSnapshot() {
  const session = new inspector.Session();
  session.connect();

  session.post('HeapProfiler.enable');
  session.on('HeapProfiler.addHeapSnapshotChunk', m => {
    fs.appendFileSync('heap.heapsnapshot', m.params.chunk);
  });

  session.post('HeapProfiler.takeHeapSnapshot');
}

module.exports = { takeHeapSnapshot };

```

### Usage

Take:

- One snapshot at idle
- One after load  
    Compare retained objects.
    

---

# Layer 8 — Unified Health Endpoint

## Why

Humans need **one glance**.

---

## Code

```js
// observability/health.js
const { getEventLoopMetrics } = require('./eventLoop');
const { getProcessMetrics } = require('./process');

function healthSnapshot() {
  return {
    timestamp: Date.now(),
    eventLoop: getEventLoopMetrics(),
    process: getProcessMetrics(),
  };
}

module.exports = { healthSnapshot };

```

### Usage

```js
app.get('/internal/health', (req, res) => {
  res.json(healthSnapshot());
});

```

This endpoint alone catches most incidents.

---

# Libraries You Can Use (When You Don’t Want to Build Everything)

### Metrics

- **prom-client** – Prometheus metrics
- **statsd-client**
- **opentelemetry-metrics**
    

### Tracing

- **@opentelemetry/sdk-node**
- **@opentelemetry/instrumentation-http**
- **@opentelemetry/instrumentation-express**
    

### Logging

- **pino** (fastest)
- **winston**
- **bunyan**
    

### APM (Tradeoffs)

- Datadog
- New Relic
- Elastic APM
    

📌 **Rule:** APMs help you _see_, not _understand_.  
Build fundamentals first.

---

# What You Now Control

You can now answer:

- Is Node blocked?
- Why?
- Which code path?
- Which request?
- Is it CPU, memory, GC, or async storm?
    

That’s **real observability**.

---

## Straight Advice (No Sugarcoating)

If you can explain:

- Event loop lag
- AsyncLocalStorage
- CPU profiles
- Heap snapshots
    

…you’re operating at **senior-engineer level** in Node.js.