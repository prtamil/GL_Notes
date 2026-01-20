This will combine **everything** we’ve discussed:

- **Express endpoints**
- **Streaming pipelines** with **partial success**
- **Dead-letter queue (DLQ)**
- **Background workers**
- **Graceful + hard shutdown**
- **AbortController cancellation**
- **HTTP streaming of partial results**
    

I’ll provide a **single-file example** with **step-by-step explanation**, so you can understand exactly how a real microservice works in production.

---

# 1️⃣ Overview / Mental Model

We’re building a service with:

1. **HTTP requests** (`/orders/bulk`)
    
    - Streams data to client as each order is processed
    - Supports **partial success**
    - Failed items go to **DLQ**
        
2. **Background workers**
    
    - Long-running async jobs (ETL, periodic tasks)
    - Handle partial success
    - DLQ integration
    - Graceful shutdown
        
3. **Shutdown / Cancellation**
    
    - `SIGTERM` / `SIGINT` triggers **graceful shutdown**
    - **AbortController** propagates cancellation
    - Hard shutdown after timeout
        
4. **Streams**
    
    - `Readable` → `Transform` → `Writable` pipelines
    - Partial success = `{ ok: true/false, value/error }`
    - Backpressure handled automatically
        

---

# 2️⃣ Full Single-File Example

```js
// production-service.js
import express from "express";
import { Readable, Transform, Writable, pipeline } from "node:stream";
import { setTimeout as delay } from "node:timers/promises";

/* ============================
   GLOBAL STATE
============================ */
let shuttingDown = false;
const activeControllers = new Set(); // tracks all pipelines (HTTP + workers)

/* ============================
   UTILITY: Retry (Abort-aware)
============================ */
async function retry(fn, { retries = 1, signal } = {}) {
  let lastError;
  for (let i = 0; i <= retries; i++) {
    if (signal.aborted) throw new Error("Aborted");
    try {
      return await fn();
    } catch (err) {
      lastError = err;
    }
  }
  throw lastError;
}

/* ============================
   SIMULATED SERVICES
============================ */
async function pricing(orderId, signal) {
  await delay(100, { signal });
  return { price: 1000 + orderId };
}

async function inventory(orderId, signal) {
  await delay(150, { signal });
  if (orderId % 3 === 0) throw new Error("Inventory unavailable");
  return { inStock: true };
}

/* ============================
   STREAM PIPELINE UTILITIES
============================ */
function createOrderSource(limit = 10, signal) {
  let id = 1;
  const r = new Readable({
    objectMode: true,
    read() {
      if (signal.aborted) return this.destroy(new Error("Source aborted"));
      if (id > limit) return this.push(null);
      this.push({ orderId: id++ });
    },
  });
  return r;
}

function createEnrichmentTransform(signal) {
  return new Transform({
    objectMode: true,
    async transform(chunk, _, cb) {
      try {
        const value = await retry(
          async () => {
            const [p, i] = await Promise.all([pricing(chunk.orderId, signal), inventory(chunk.orderId, signal)]);
            return { ...chunk, pricing: p, inventory: i };
          },
          { retries: 1, signal }
        );
        cb(null, { ok: true, value });
      } catch (err) {
        if (signal.aborted) return cb(err);
        cb(null, { ok: false, orderId: chunk.orderId, error: err.message });
      }
    },
  });
}

function createRouterTransform(mainSink, dlqSink) {
  return new Transform({
    objectMode: true,
    transform(chunk, _, cb) {
      if (chunk.ok) mainSink.write(chunk.value);
      else dlqSink.write(chunk);
      cb();
    },
    final(cb) {
      mainSink.end();
      dlqSink.end();
      cb();
    },
  });
}

/* ============================
   HTTP RESPONSE SINK (Streaming)
============================ */
function createHttpResponseSink(res, signal) {
  const w = new Writable({
    objectMode: true,
    write(chunk, _, cb) {
      if (signal.aborted) return cb(new Error("Response aborted"));
      // stream JSON lines to client
      res.write(JSON.stringify(chunk) + "\n");
      cb();
    },
    final(cb) {
      res.end();
      cb();
    },
  });

  signal.addEventListener("abort", () => w.destroy(new Error("Response sink aborted")));
  return w;
}

/* ============================
   DLQ SINK
============================ */
function createDlqSink(name, signal) {
  const failures = [];
  const w = new Writable({
    objectMode: true,
    write(chunk, _, cb) {
      failures.push(chunk);
      cb();
    },
    final(cb) {
      console.log(`DLQ [${name}] processed failures:`);
      console.table(failures);
      cb();
    },
  });

  signal.addEventListener("abort", () => w.destroy(new Error(`DLQ ${name} aborted`)));
  return w;
}

/* ============================
   RUN PIPELINE
============================ */
function runPipeline({ source, enrich, mainSink, dlqSink, signal }, done) {
  pipeline(source, enrich, createRouterTransform(mainSink, dlqSink), (err) => {
    if (err && !signal.aborted) return done(err);
    done(null);
  });
}

/* ============================
   EXPRESS APP
============================ */
const app = express();

// Streaming endpoint
app.get("/orders/bulk", (req, res) => {
  if (shuttingDown) return res.status(503).json({ message: "Server shutting down" });

  const ac = new AbortController();
  activeControllers.add(ac);

  req.on("aborted", () => ac.abort());
  res.on("close", () => ac.abort());

  const source = createOrderSource(10, ac.signal);
  const enrich = createEnrichmentTransform(ac.signal);
  const mainSink = createHttpResponseSink(res, ac.signal);
  const dlqSink = createDlqSink("HTTP-DLQ", ac.signal);

  runPipeline({ source, enrich, mainSink, dlqSink, signal: ac.signal }, (err) => {
    activeControllers.delete(ac);
    if (ac.signal.aborted) return;
    if (err) console.error("Pipeline error:", err.message);
  });
});

/* ============================
   BACKGROUND WORKERS
============================ */
function startWorker(name) {
  const ac = new AbortController();
  activeControllers.add(ac);

  const source = createOrderSource(20, ac.signal); // worker jobs
  const enrich = createEnrichmentTransform(ac.signal);
  const mainSink = new Writable({
    objectMode: true,
    write(chunk, _, cb) {
      cb(); // simulate processing
    },
    final(cb) {
      console.log(`Worker ${name} completed`);
      activeControllers.delete(ac);
      cb();
    },
  });
  const dlqSink = createDlqSink(`Worker-${name}-DLQ`, ac.signal);

  runPipeline({ source, enrich, mainSink, dlqSink, signal: ac.signal }, (err) => {
    if (err && !ac.signal.aborted) console.error(`Worker ${name} pipeline error:`, err.message);
  });
}

/* ============================
   START SERVER & WORKERS
============================ */
const server = app.listen(3000, () => console.log("Server running on http://localhost:3000"));
startWorker("A");
startWorker("B");

/* ============================
   GRACEFUL SHUTDOWN
============================ */
function gracefulShutdown() {
  if (shuttingDown) return;
  shuttingDown = true;
  console.log("\nGraceful shutdown: stopping HTTP + pipelines");

  server.close(() => console.log("HTTP server closed"));

  for (const ac of activeControllers) ac.abort();

  // hard exit if grace period exceeded
  setTimeout(() => {
    console.error("Forcing shutdown");
    process.exit(1);
  }, 10000);
}

process.on("SIGTERM", gracefulShutdown);
process.on("SIGINT", gracefulShutdown);

```

---

# 3️⃣ Detailed Explanation

### 1️⃣ **Streams + Partial Success**

- `Readable` → generates jobs/orders
- `Transform` → enriches orders, wraps errors as `{ ok: false }`
- `RouterTransform` → splits successful vs failed items
- `Writable` → sinks handle results and DLQs
    

### 2️⃣ **Dead-Letter Queue (DLQ)**

- DLQs are **separate sinks** for failed items
- Can be extended to **Kafka, S3, database**
- Keeps main pipeline clean and fast
    

### 3️⃣ **HTTP Streaming**

- `Writable` sink writes JSON lines (`res.write`)
- Client sees **partial results immediately**
- Uses **backpressure naturally**
    

### 4️⃣ **Background Workers**

- Same pipeline logic as HTTP, **detached**
- Simulates long-running jobs
- Graceful shutdown + DLQ works identically
    

### 5️⃣ **Graceful Shutdown**

- `shuttingDown = true` → blocks new requests
- `AbortController.abort()` → cancels all pipelines
- `server.close()` → stops accepting HTTP connections
- Timeout → forces hard exit if some pipelines are stuck
    

### 6️⃣ **AbortController Integration**

- Single signal per pipeline
    
- Propagates to:
    
    - Sources (`Readable`)
    - Transforms (`Transform`)
    - Sinks (`Writable`)
        
- Allows **cooperative cancellation**
    

### 7️⃣ **Backpressure & Memory Safety**

- Streams pause automatically if sinks are slow
- No extra queues needed
- Partial success + DLQ **does not block main pipeline**
    

---

# 4️⃣ Mental Model (Full Microservice)

```js
HTTP Request → Readable → Transform → Router → Writable → Client
                               └→ DLQ (failed chunks)

Background Worker → Readable → Transform → Router → Writable → Processing
                                     └→ DLQ (failed chunks)

SIGTERM/SIGINT → AbortController → abort all pipelines → close server → exit
Hard shutdown if timeout → process.exit(1)

```
---

✅ This template demonstrates **everything you need for a real Node.js microservice**:

- Request + background pipelines
- Partial success handling
- DLQ for failed jobs
- Streaming to client
- Graceful + hard shutdown
- Backpressure handling