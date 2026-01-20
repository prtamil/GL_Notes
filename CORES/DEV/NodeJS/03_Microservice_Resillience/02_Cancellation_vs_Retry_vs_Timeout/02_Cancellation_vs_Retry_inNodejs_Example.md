# A Real-World, Modular Example

## Cancellation + Timeout + Retry (Production Style)

### Scenario

**API endpoint:**

- Accepts a request to process an order
    
- Steps:
    
    1. Validate input
    2. Charge payment gateway (external, flaky)
    3. Save order to DB
    4. Emit analytics event (best effort)
        

**Requirements:**

- Client disconnect → cancel everything
- Request timeout → stop further work
- Transient payment failure → retry
- Payment retry must stop on cancellation
- Analytics must not block request
    

---

## MODULE 1 — Cancellation Utilities

### `createRequestContext`

```js
function createRequestContext(req, timeoutMs) {
  const controller = new AbortController();
  const { signal } = controller;

  // Client disconnect
  req.on('close', () => {
    controller.abort(new Error('Client disconnected'));
  });

  // Timeout policy
  const timeout = setTimeout(() => {
    controller.abort(new Error('Request timeout'));
  }, timeoutMs);

  return {
    signal,
    cleanup() {
      clearTimeout(timeout);
    }
  };
}

```

**What this module owns**

- Request lifetime
- Cancellation authority
- Deadline
    

---

## MODULE 2 — Retry Engine (Reusable Everywhere)

```js
const { setTimeout: delay } = require('timers/promises');

async function retry(operation, {
  signal,
  retries = 3,
  baseDelay = 200,
  isRetryable = () => true
}) {
  let attempt = 0;

  while (true) {
    if (signal.aborted) {
      throw signal.reason;
    }

    try {
      return await operation({ signal, attempt });
    } catch (err) {
      if (signal.aborted) {
        throw signal.reason;
      }

      attempt++;

      if (attempt > retries || !isRetryable(err)) {
        throw err;
      }

      const backoff = baseDelay * 2 ** (attempt - 1);
      console.log(`Retrying in ${backoff}ms (attempt ${attempt})`);
      await delay(backoff, { signal });
    }
  }
}

```

**What this module guarantees**

- No retries after cancellation
- Bounded retries
- Exponential backoff
- Centralized logic
    

---

## MODULE 3 — External Service (Payment Gateway)

```js
async function chargePayment(order, { signal }) {
  if (signal.aborted) throw signal.reason;

  // Simulate network delay
  await delay(300, { signal });

  // Simulate transient failure
  if (Math.random() < 0.6) {
    const err = new Error('Payment gateway timeout');
    err.transient = true;
    throw err;
  }

  return { transactionId: crypto.randomUUID() };
}

```
---

## MODULE 4 — Domain Logic

### Payment with Retry

```js
async function processPayment(order, signal) {
  return retry(
    ({ signal }) => chargePayment(order, { signal }),
    {
      signal,
      retries: 4,
      isRetryable: err => err.transient === true
    }
  );
}

```

### Database Save (No Retry Here)

```js
async function saveOrder(order, payment, { signal }) {
  if (signal.aborted) throw signal.reason;
  await delay(100, { signal });
  return { orderId: crypto.randomUUID() };
}

```

---

## MODULE 5 — Best-Effort Side Effect

```js
async function emitAnalytics(event) {
  try {
    await delay(50);
    console.log('Analytics sent');
  } catch {
    // intentionally ignored
  }
}

```

Notice:

- No signal
- No retry
- No blocking
    

This is **intentional**.

---

## MODULE 6 — Orchestration (The Important Part)

```js
async function handleOrder(req, res) {
  const { signal, cleanup } = createRequestContext(req, 3000);

  try {
    const order = { amount: 100 };

    const payment = await processPayment(order, signal);

    const saved = await saveOrder(order, payment, { signal });

    // Fire and forget
    emitAnalytics({ orderId: saved.orderId });

    res.writeHead(200);
    res.end(JSON.stringify(saved));
  } catch (err) {
    if (err.message === 'Client disconnected') {
      res.writeHead(499);
    } else if (err.message === 'Request timeout') {
      res.writeHead(504);
    } else {
      res.writeHead(500);
    }
    res.end();
  } finally {
    cleanup();
  }
}

```
---

## CONTROL FLOW — Read This Carefully

### Case 1: Payment gateway flaky

- `chargePayment` fails
- Retry kicks in
- Backoff applied
- Succeeds
- Request completes
    

✔ Retry used correctly

---

### Case 2: Client disconnects mid-retry

- `req.close` fires
- AbortController aborts
- Retry loop exits immediately
- No DB write
- No analytics
- Cleanup runs
    

✔ Cancellation wins

---

### Case 3: Request exceeds deadline

- Timeout aborts
- Any in-flight delay throws
- No retries after abort
- Controlled failure
    

✔ Timeout enforced via cancellation

---

## WHY THIS DESIGN WORKS

### Separation of Concerns

|Module|Responsibility|
|---|---|
|Request context|Lifetime + authority|
|Retry engine|Reliability|
|Domain logic|Business meaning|
|Side effects|Best effort|
|Orchestration|Ordering|

Each piece is **testable and reusable**.

---

## COMMON MISTAKES THIS AVOIDS

- ❌ Retry logic scattered everywhere
- ❌ Timeouts mixed into business logic
- ❌ Client disconnect not stopping work
- ❌ Analytics blocking main flow
    

---

## MENTAL MODEL TO KEEP

> Cancellation defines **when to stop**  
> Retry defines **whether to try again**  
> Timeout defines **how long to care**

And:

> Cancellation always wins.