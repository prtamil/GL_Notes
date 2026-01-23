# Hardening a Real Production Node.js Server

## What “hardened” actually means

A hardened Node server:

- Fails **fast**, not slowly
- Degrades **gracefully**, not catastrophically
- Preserves **event loop liveness under pressure**
- Makes attacks **visible**, not silent
    

Hardening is not about preventing all failure.  
It’s about **making failure bounded and observable**.

---

## Layer 0: Process-Level Hardening (Before Code Runs)

These are **non-negotiable**.

### 1. Set hard memory limits

```js
node --max-old-space-size=512 server.js

```

Why:

- Prevents GC death spirals
- Forces early crash → faster recovery
- Avoids host-wide memory starvation
    

**Rule:** Smaller heap + faster restart > big heap + slow death.

---

### 2. Enable strict runtime flags

```js
node \
  --unhandled-rejections=strict \
  --abort-on-uncaught-exception \
  server.js

```

Why:

- Silent promise failures kill reliability
- Crashing early preserves correctness
    

Production truth:

> A crashed process is healthier than a corrupted one.

---

### 3. OS-level limits (ulimit)

```js
ulimit -n 65535

```

And cap concurrency _inside_ Node (we’ll do that later).

---

## Layer 1: Event Loop Health Protection

### 1. Monitor event loop delay (mandatory)

```js
const { monitorEventLoopDelay } = require('perf_hooks');

const h = monitorEventLoopDelay({ resolution: 20 });
h.enable();

setInterval(() => {
  const mean = h.mean / 1e6; // ms
  if (mean > 50) {
    console.error('🚨 Event loop delay:', mean.toFixed(2), 'ms');
  }
}, 1000);

```

Why:

- This is your **runtime heartbeat**
- CPU attacks, sync bugs, GC pressure all surface here
    

If you don’t measure this, you are blind.

---

### 2. Enforce per-request time budgets

```js
function withTimeBudget(ms, fn) {
  const start = process.hrtime.bigint();
  return (...args) => {
    const elapsed =
      Number(process.hrtime.bigint() - start) / 1e6;
    if (elapsed > ms) {
      throw new Error('Time budget exceeded');
    }
    return fn(...args);
  };
}

```

Use inside loops, parsers, transforms.

---

## Layer 2: Input Pressure Control (Most Outages Start Here)

### 1. Byte limits everywhere

**Never trust upstream limits.**

```js
function limitStream(stream, maxBytes) {
  let seen = 0;
  stream.on('data', chunk => {
    seen += chunk.length;
    if (seen > maxBytes) {
      stream.destroy(new Error('Payload too large'));
    }
  });
}

```

Apply to:

- HTTP requests
- File uploads
- IPC streams
    

---

### 2. Mandatory timeouts

```js
req.setTimeout(10_000, () => {
  req.destroy(new Error('Request timeout'));
});

```

No timeout = infinite resource lease.

---

### 3. Always use `pipeline()`

```js
const { pipeline } = require('stream/promises');

await pipeline(
  req,
  safeTransform,
  destination
);

```

Why:

- Proper teardown
- No zombie streams
- Backpressure preserved
    

---

## Layer 3: CPU Isolation (Protect the Event Loop)

### Rule

> The event loop must never do attacker-influenced heavy work.

### 1. Identify CPU hotspots

Red flags:

- `JSON.parse` on large payloads
- crypto sync APIs
- compression
- image processing
- regex on user input
    

---

### 2. Move heavy work to workers

```js
const { Worker } = require('worker_threads');

function runWorker(data) {
  return new Promise((res, rej) => {
    const w = new Worker('./worker.js', { workerData: data });
    w.on('message', res);
    w.on('error', rej);
  });
}

```

Workers:

- Protect the loop
- Can be rate-limited
- Can be killed
    

---

### 3. Cap worker concurrency

```js
const PQueue = require('p-queue');
const queue = new PQueue({ concurrency: 2 });

queue.add(() => runWorker(data));

```

Unbounded workers = self-DoS.

---

## Layer 4: Memory Safety

### 1. Never buffer unbounded data

❌ Bad:

```js
let body = '';
req.on('data', c => body += c);

```

✅ Good:

```js
req.pipe(parserStream).pipe(handlerStream);

```

---

### 2. Freeze shared state

```js
Object.freeze(config);
Object.freeze(config.defaults);

```

Prevents runtime mutation bugs and pollution.

---

### 3. Guard object growth

```js
if (Object.keys(obj).length > 1000) {
  throw new Error('Object too large');
}

```

This stops memory amplification attacks.

---

## Layer 5: Flow Control & Liveness

### 1. Abort everything on disconnect

```js
const ac = new AbortController();

req.on('close', () => ac.abort());

await doWork({ signal: ac.signal });

```

If the client is gone, your work should stop.

---

### 2. Promise hygiene

Never allow promises that:

- Don’t resolve
- Don’t reject
- Aren’t tracked
    

Pattern:

```js
function withTimeout(promise, ms) {
  return Promise.race([
    promise,
    new Promise((_, r) =>
      setTimeout(() => r(new Error('Timeout')), ms)
    )
  ]);
}

```

---

## Layer 6: Resource Accounting

### Track what you consume

|Resource|How to cap|
|---|---|
|Requests|Rate limiting|
|Streams|Byte + time limits|
|Workers|Pool size|
|FDs|Close on error|
|Timers|Clear aggressively|

If you can’t count it, you can’t control it.

---

## Layer 7: Graceful Degradation (This is Senior-Level)

### 1. Reject early under load

```js
if (h.mean / 1e6 > 80) {
  res.status(503).send('Server busy');
  return;
}

```

This protects _everyone else_.

---

### 2. Backpressure the client

HTTP 429 is not failure — it’s survival.

---

## Layer 8: Crash Strategy (Yes, Crash)

### You should crash when:

- Event loop delay stays high
- Memory usage keeps growing
- Internal invariants break
    

```js
process.on('uncaughtException', err => {
  console.error(err);
  process.exit(1);
});

```

Kubernetes / PM2 / systemd exists for a reason.

---

## A Realistic Production Hardening Checklist

Before shipping, you should be able to answer:

- What is the **max CPU per request**?
- What is the **max memory per request**?
- What is the **max time a request can live**?
- What happens when limits are exceeded?
- How do we know the event loop is unhealthy?
    

If any answer is “not sure” → not hardened.

---

## Final Mental Model

Hardening is **pressure management**.

Attackers don’t need exploits.  
They need **leverage**.

Your job is to:

- Bound execution
- Cap resources
- Preserve liveness
- Fail predictably
    

Do this, and Node becomes _extremely_ reliable.