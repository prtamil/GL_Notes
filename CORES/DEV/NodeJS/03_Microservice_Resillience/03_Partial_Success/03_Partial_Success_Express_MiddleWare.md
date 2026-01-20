Below is a **production-grade Express middleware** conversion of the previous example, with these goals:

- ✅ **Single file**
- ✅ Clean `app.get()` handler (business logic is abstracted)
- ✅ Middleware-safe cancellation (client disconnect)
- ✅ Partial success preserved
- ✅ Timeouts + retries per dependency
- ✅ No framework magic, easy to reason about
    

---

# 🧩 Mental Model (Before Code)

In Express:

- **Cancellation source** → client disconnect (`req.aborted`, `res.close`)
- **AbortController** → shared across all downstream calls
- **Middleware responsibility**:
    
    - Create abort controller
    - Bind it to request lifecycle
    - Call orchestration logic
    - Return partial result instead of throwing
        

---

# ✅ Single-File Express Example
```js
// app.js
import express from "express";
import { setTimeout as delay } from "node:timers/promises";

/* ============================
   Utility: Timeout Wrapper
============================ */
async function withTimeout(fn, ms, parentSignal) {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), ms);

  if (parentSignal) {
    parentSignal.addEventListener("abort", () => controller.abort());
  }

  try {
    return await fn(controller.signal);
  } finally {
    clearTimeout(timeoutId);
  }
}

/* ============================
   Utility: Retry Wrapper
============================ */
async function retry(fn, { retries = 1, backoffMs = 200 } = {}) {
  let lastError;

  for (let attempt = 0; attempt <= retries; attempt++) {
    try {
      return await fn();
    } catch (err) {
      lastError = err;
      if (attempt < retries) {
        await delay(backoffMs * (attempt + 1));
      }
    }
  }

  throw lastError;
}

/* ============================
   Simulated External Services
============================ */
async function pricingService(signal) {
  await delay(300, { signal });
  return { price: 1999 };
}

async function inventoryService(signal) {
  await delay(600, { signal });
  throw new Error("Inventory DB timeout");
}

async function recommendationService(signal) {
  await delay(400, { signal });
  return ["keyboard", "mouse"];
}

/* ============================
   Partial Success Orchestrator
============================ */
async function enrichOrder(orderId, signal) {
  const result = {
    orderId,
    data: {},
    errors: {},
    isPartial: false,
  };

  const tasks = {
    pricing: () =>
      retry(() =>
        withTimeout(pricingService, 500, signal)
      ),
    inventory: () =>
      retry(() =>
        withTimeout(inventoryService, 500, signal)
      ),
    recommendations: () =>
      retry(() =>
        withTimeout(recommendationService, 500, signal)
      ),
  };

  await Promise.allSettled(
    Object.entries(tasks).map(async ([key, task]) => {
      try {
        result.data[key] = await task();
      } catch (err) {
        result.errors[key] = err.message;
        result.isPartial = true;
      }
    })
  );

  return result;
}

/* ============================
   Express Middleware
============================ */
function orderEnrichmentMiddleware(req, res, next) {
  const ac = new AbortController();

  // Cancel work if client disconnects
  req.on("aborted", () => ac.abort());
  res.on("close", () => ac.abort());

  const { orderId } = req.params;

  enrichOrder(orderId, ac.signal)
    .then((result) => {
      if (ac.signal.aborted) return;

      res.status(result.isPartial ? 206 : 200).json({
        status: result.isPartial ? "partial" : "success",
        ...result,
      });
    })
    .catch((err) => {
      if (ac.signal.aborted) return;

      next(err); // true hard failure
    });
}

/* ============================
   Express App
============================ */
const app = express();

app.get("/orders/:orderId", orderEnrichmentMiddleware);

app.use((err, req, res, _next) => {
  res.status(500).json({
    status: "error",
    message: err.message,
  });
});

app.listen(3000, () => {
  console.log("Server running on http://localhost:3000");
});

```
---

# 🔍 What Makes This Production-Correct

### 1️⃣ **Client Disconnect = Cancellation**

```js
req.on("aborted", () => ac.abort());
res.on("close", () => ac.abort());

```

- Prevents wasted CPU
- Stops retries mid-flight
- Avoids memory leaks
    

---

### 2️⃣ **Partial Success ≠ Error**

```js
res.status(result.isPartial ? 206 : 200)

```

- HTTP `206 Partial Content` is semantically correct
- Clients can distinguish degraded responses
    

---

### 3️⃣ **Retries Are Scoped**

- Retry only per dependency
- Successful calls are never repeated
- Backoff is explicit
    

---

### 4️⃣ **Timeouts Are Per Dependency**

- One slow service doesn’t block others
- Prevents tail-latency explosions
    

---

### 5️⃣ **Hard Failures Are Still Possible**

Only these cause `500`:

- Programmer bugs
- Serialization issues
- Unexpected orchestration failures
    

---

# 🧠 How This Maps to Real Systems

|Pattern|Used For|
|---|---|
|Partial success|Dashboards, search, enrichment APIs|
|Cancellation|Mobile clients, flaky networks|
|Retry|Transient infra failures|
|Timeout|SLA protection|
|206 responses|API contracts|

---

# 🚫 Common Mistake to Avoid

❌ Throwing on first failure  
❌ Retrying everything  
❌ Returning `200` without flags  
❌ Ignoring client disconnects

---

# 🏁 Final Takeaway

> **Express middleware is the boundary where chaos becomes structure.**

Partial success is **not optional** at scale — it’s how systems stay fast, honest, and resilient.