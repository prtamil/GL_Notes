You already have **Express + pipelines + graceful shutdown**. The next layer is **background workers** — i.e., asynchronous jobs running **outside HTTP request scope**, which still need:

- Partial success handling
- Dead-letter queues
- Graceful shutdown
- AbortController cancellation
    

This is exactly what happens in real systems: job queues, periodic tasks, Kafka consumers, etc.

---

# 1️⃣ Mental Model

You now have **two types of work**:

|Type|Lifecycle|Cancellation|
|---|---|---|
|HTTP requests|short-lived, client-driven|abort on disconnect / SIGTERM|
|Background workers|long-running, server-driven|abort on SIGTERM, drain work|

**Key idea:** background workers are like **streams detached from requests**. They live until:

- They finish work
- Or the server shuts down gracefully
    

---

# 2️⃣ Graceful Shutdown for Workers

1. Stop fetching new jobs/tasks
2. Let in-flight jobs finish
3. Cancel slow jobs after timeout (optional)
4. Flush DLQs
5. Exit process
    

You now need **per-worker AbortController** + **global controller**.

---

# 3️⃣ Single-File Example: Shutdown-Safe Workers + Streams

```js
// background-workers.js
import { Readable, Transform, Writable, pipeline } from "node:stream";
import { setTimeout as delay } from "node:timers/promises";

/* ============================
   Global Shutdown State
============================ */
let shuttingDown = false;
const activeControllers = new Set();

/* ============================
   Simulated Job Source
============================ */
function jobSource(signal) {
  let id = 1;
  const r = new Readable({
    objectMode: true,
    read() {
      if (shuttingDown || id > 20) return this.push(null);
      this.push({ jobId: id++ });
    },
  });

  signal.addEventListener("abort", () => r.destroy(new Error("Source aborted")));

  return r;
}

/* ============================
   Worker Transform
============================ */
function workerTransform(signal) {
  return new Transform({
    objectMode: true,
    async transform(job, _, cb) {
      try {
        // simulate async processing
        await delay(100, { signal });

        // randomly fail some jobs
        if (job.jobId % 5 === 0) throw new Error("Worker failed");

        cb(null, { ok: true, job });
      } catch (err) {
        if (signal.aborted) return cb(err);
        cb(null, { ok: false, job, error: err.message });
      }
    },
  });
}

/* ============================
   Sink + Dead-Letter Queue
============================ */
function workerSink(signal) {
  const successes = [];
  const failures = [];

  const w = new Writable({
    objectMode: true,
    write(chunk, _, cb) {
      chunk.ok ? successes.push(chunk.job) : failures.push(chunk);
      cb();
    },
    final(cb) {
      console.log("\nWorker successes:", successes.map(j => j.jobId));
      console.log("Worker failures:", failures.map(f => f.jobId));
      cb();
    },
  });

  signal.addEventListener("abort", () => w.destroy(new Error("Sink aborted")));

  return w;
}

/* ============================
   Start Worker Pipeline
============================ */
function startWorker(name) {
  const ac = new AbortController();
  activeControllers.add(ac);

  console.log(`Worker ${name} started`);

  pipeline(jobSource(ac.signal), workerTransform(ac.signal), workerSink(ac.signal), (err) => {
    activeControllers.delete(ac);
    if (err) {
      if (ac.signal.aborted) {
        console.log(`Worker ${name} aborted`);
      } else {
        console.error(`Worker ${name} pipeline failed:`, err.message);
      }
    } else {
      console.log(`Worker ${name} finished normally`);
    }
  });
}

/* ============================
   Main: Start workers
============================ */
function main() {
  // start 2 workers
  startWorker("A");
  startWorker("B");

  // shutdown handler
  function gracefulShutdown() {
    if (shuttingDown) return;
    shuttingDown = true;
    console.log("\nGraceful shutdown: aborting workers...");

    for (const ac of activeControllers) {
      ac.abort();
    }

    // hard exit after timeout
    setTimeout(() => {
      console.error("Forcing shutdown");
      process.exit(1);
    }, 5000);
  }

  process.on("SIGTERM", gracefulShutdown);
  process.on("SIGINT", gracefulShutdown);
}

main();

```

---

# 4️⃣ What This Pattern Gets Right

### ✔ Workers are **shutdown-safe**

- Stop fetching new jobs on shutdown
- In-flight jobs either finish or abort
    

### ✔ Partial success + DLQ ready

- `ok: true` vs `ok: false` per job
- Can extend `workerSink` to push failures to Kafka/S3/db
    

### ✔ Backpressure respected

- Streams automatically handle flow control
- No job floods memory
    

### ✔ AbortController integrates naturally

- Works for both request-scoped and background workers
- Single signal per worker
- Can implement global + per-worker hierarchy
    

---

# 5️⃣ Real-World Usage

- Kafka consumers
    
    - Each partition = stream
    - Failures → DLQ
    - Shutdown → stop consuming partitions
        
- ETL pipelines
    
    - File ingestion → stream → transform → sink
    - Shutdown → abort remaining processing
        
- Periodic jobs / cron workers
    
    - Long-running tasks
    - Graceful exit if deployment occurs
        

---

# 6️⃣ Mental Model Update

Now you can think **like a distributed system operator**:

```js
HTTP requests  → AbortController → pipeline
Background jobs → AbortController → pipeline
Dead-letter queue → preserves partial success
SIGTERM / SIGINT → triggers graceful shutdown
Hard exit → ensures process dies if grace expires

```

Everything is **composable, safe, and observable**.