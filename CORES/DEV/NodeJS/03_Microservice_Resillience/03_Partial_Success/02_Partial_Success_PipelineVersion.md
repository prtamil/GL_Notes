# Partial Success with Streams **+ Cancellation**

Good — this is the most correct mental model for partial success in Node.js.

**Streams + pipelines let you model partial success as data, not exceptions — and AbortController lets you stop the flow safely when the outside world says “enough”.**

I’ll keep the same structure and add cancellation where it belongs.

---

## 1️⃣ Why Streams Are the Right Abstraction

Exceptions are binary:

- success ❌
- failure ❌
    

Streams are continuous:

- some chunks succeed
- some chunks fail
- pipeline keeps flowing
    

> Partial success is not a _control-flow problem_  
> It’s a **data-flow classification problem**

Streams let you:

- Keep good data flowing
- Side-channel failures
- Apply backpressure naturally
- **Cancel safely and globally**
    

This is why:

- Kafka
- Log processors
- ETL systems
- Search pipelines
    

are all **stream-based**, not promise-based.

---

## 2️⃣ Partial Success in a Pipeline (Mental Model)

Instead of throwing, each chunk becomes **data**:

```js
{
  ok: true,
  value: ...
}

// or

{
  ok: false,
  error: ...
}

```

Errors are **values**, not fatal signals.

Fatal errors are reserved for:

- Corrupt streams
- Programmer bugs
- Broken invariants
    

This distinction is what allows **partial success + cancellation** to coexist.

---

## 3️⃣ Production-Grade Streaming Pipeline

### (with AbortController + pipeline cancellation)

### 📌 Scenario (Very Real)

**Bulk order enrichment**

- Input stream of order IDs
- Enrich each order
- Some services fail
- Pipeline must continue
- **User / system may cancel mid-way**
- Final output separates success & failures
    

---

## ✅ Full Single-File Example (Cancellation Included)

```js
// stream-partial-success-with-cancel.js
import { Readable, Transform, Writable, pipeline } from "node:stream";
import { setTimeout as delay } from "node:timers/promises";

/* ============================
   Utility: Retry (Abort-aware)
============================ */
async function retry(fn, { retries = 1, signal } = {}) {
  let lastError;

  for (let i = 0; i <= retries; i++) {
    if (signal?.aborted) {
      throw new Error("Operation aborted");
    }

    try {
      return await fn();
    } catch (err) {
      lastError = err;
    }
  }

  throw lastError;
}

/* ============================
   Simulated Services (Abort-aware)
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
   Readable: Order Source
============================ */
function orderSource(signal) {
  let id = 1;

  const src = new Readable({
    objectMode: true,
    read() {
      if (id > 10) return this.push(null);
      this.push({ orderId: id++ });
    },
  });

  signal.addEventListener("abort", () => {
    src.destroy(new Error("Source aborted"));
  });

  return src;
}

/* ============================
   Transform: Enrichment
============================ */
function enrichmentTransform(signal) {
  return new Transform({
    objectMode: true,

    async transform(chunk, _enc, cb) {
      if (signal.aborted) {
        return cb(new Error("Transform aborted"));
      }

      const { orderId } = chunk;

      try {
        const result = await retry(
          async () => {
            const [p, i] = await Promise.all([
              pricing(orderId, signal),
              inventory(orderId, signal),
            ]);

            return {
              orderId,
              pricing: p,
              inventory: i,
            };
          },
          { retries: 1, signal }
        );

        cb(null, { ok: true, value: result });
      } catch (err) {
        if (signal.aborted) return cb(err);

        cb(null, {
          ok: false,
          orderId,
          error: err.message,
        });
      }
    },
  });
}

/* ============================
   Writable: Result Sink
============================ */
function resultSink(signal) {
  const successes = [];
  const failures = [];

  const sink = new Writable({
    objectMode: true,

    write(chunk, _enc, cb) {
      if (chunk.ok) {
        successes.push(chunk.value);
      } else {
        failures.push({
          orderId: chunk.orderId,
          error: chunk.error,
        });
      }
      cb();
    },

    final(cb) {
      console.log("\nSUCCESSFUL ORDERS:");
      console.table(successes);

      console.log("\nFAILED ORDERS:");
      console.table(failures);

      cb();
    },
  });

  signal.addEventListener("abort", () => {
    sink.destroy(new Error("Sink aborted"));
  });

  return sink;
}

/* ============================
   Main (Clean + Cancellable)
============================ */
function main() {
  const ac = new AbortController();

  // Simulate external cancellation (HTTP client disconnect, SLA timeout)
  setTimeout(() => {
    console.log("\n⚠ Cancelling pipeline...");
    ac.abort();
  }, 700);

  pipeline(
    orderSource(ac.signal),
    enrichmentTransform(ac.signal),
    resultSink(ac.signal),
    (err) => {
      if (err) {
        console.error("\nPipeline stopped:", err.message);
      } else {
        console.log("\nPipeline completed with partial success");
      }
    }
  );
}

main();

```

---

## 4️⃣ What This Pipeline Gets Right (Now Complete)

### ✔ Partial success is explicit

```js
{ ok: true, value }
{ ok: false, error }

```

No ambiguity.

---

### ✔ Failures don’t stop the pipeline

- Inventory fails for some orders
- Other orders continue normally
    

This is the **core property** you want.

---

### ✔ Backpressure is automatic

- Slow enrichment ⇒ source pauses
- Memory stays flat
- No queues, no manual throttling
    

---

### ✔ Retry is per-item

- One bad order ≠ global retry
- Matches real ETL / ingestion systems
    

---

### ✔ Cancellation is **global and correct**

- AbortController propagates intent
- `pipeline()` shuts everything down
- Streams clean up resources
- No orphan promises
    

> **Destroy the stream, not individual promises**

---

## 5️⃣ Cancellation & Timeouts (Properly Explained)

### AbortController is for:

- Client disconnects
- SLA expiration
- System shutdown
- Manual operator stop
    

### Pipeline cancellation works because:

- `stream.destroy()` is authoritative
- Backpressure unwinds
- `pipeline()` guarantees cleanup
    

This is **far safer** than canceling promises manually.

---

## 6️⃣ How This Maps to Real Systems

|System|Mapping|
|---|---|
|Kafka consumer|Readable|
|Enrichment workers|Transform|
|DB / API writes|Writable|
|Dead-letter queue|`{ ok:false }` chunks|
|Metrics|Count `ok:false`|
|Shutdown / rebalance|AbortController|

---

## 7️⃣ When NOT to Use This Model

Don’t use streaming partial success when:

- Transactional guarantees required
- All-or-nothing semantics matter
- Side effects must be atomic
    

In those cases:

- Use sagas
- Use strict transactions
- Use compensation workflows
    

---

## 🧠 Final Mental Model (Completed)

> **Promises fail fast**  
> **Streams fail slow**  
> **AbortController decides _when to stop_**

Partial success requires **failing slow**  
Cancellation requires **stopping clean**

Together, this is how **real systems survive reality**.