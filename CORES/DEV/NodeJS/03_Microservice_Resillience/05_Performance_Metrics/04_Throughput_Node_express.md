## Throughput — Explained for Express / Node.js Apps

### What is Throughput?

**Throughput** is the amount of work your system completes **per unit time**.

For HTTP services:

- **Requests per second (RPS / QPS)**
- Sometimes **bytes per second** (for streaming APIs)
    

> Latency answers: _“How long does one request take?”_  
> Throughput answers: _“How many requests can I finish per second?”_

You need **both** to understand performance.

---

## Simple Mental Model

```js
Throughput = Completed Requests / Time

```

If your Express app handles:

- 12,000 requests in 60 seconds
    

```js
Throughput = 12,000 / 60 = 200 RPS

```

---

## Why Throughput Matters (Real Life)

### Example: API under load

- p95 latency = 200ms (looks great)
- Throughput collapses from 500 RPS → 80 RPS
    

Users will experience:

- Timeouts
- Retries
- Queue buildup
- Cascading failures
    

> **Good latency with bad throughput = fragile system**

---

## Throughput vs Latency (Critical Relationship)

They are **not independent**.

As load increases:

- Throughput rises → until a saturation point
- After saturation:
    
    - Latency spikes
    - Throughput plateaus or drops
        

This curve is **unavoidable**.

Node.js makes this very visible because:

- Single event loop
- Explicit async behavior
- Blocking code kills throughput immediately
    

---

## What Limits Throughput in Express Apps?

### 1. Event Loop Saturation

CPU-heavy work blocks the loop:

```js
app.get("/bad", (req, res) => {
  for (let i = 0; i < 1e9; i++) {} // blocks everything
  res.send("done");
});

```

Result:

- Throughput → near zero
- Latency → infinite
    

---

### 2. Slow I/O Dependencies

Examples:

- Database queries
- External APIs
- File reads
    

Even async I/O limits throughput due to:

- Connection pools
- Network limits
- Backpressure
    

---

### 3. Memory Pressure & GC

- Large buffers
- JSON over-allocation
- Holding request objects too long
    

Symptoms:

- Throughput jitter
- Periodic latency spikes
    

---

### 4. Missing Backpressure

If your app:

- Accepts requests faster than it can finish them
    

You’ll see:

- Queues growing
- Memory increasing
- Eventually OOM or crashes
    

---

## Measuring Throughput (Correctly)

### 1. Application-Level Measurement (Exact)

#### Express Middleware Counter

```js
let completed = 0;
let start = Date.now();

app.use((req, res, next) => {
  res.on("finish", () => {
    completed++;
  });
  next();
});

setInterval(() => {
  const elapsed = (Date.now() - start) / 1000;
  console.log("Throughput:", (completed / elapsed).toFixed(2), "req/sec");
}, 5000);

```

This measures **actual completed requests**, not arrivals.

---

### 2. Load Testing (Realistic)

Using `autocannon`:

`npx autocannon -c 100 -d 30 http://localhost:3000`

Key outputs:

- Requests/sec → **throughput**
- Latency percentiles
- Errors / timeouts
    

---

## Throughput vs Concurrency (Common Confusion)

- **Concurrency**: requests _in flight_
- **Throughput**: requests _completed_
    

Example:

- 100 concurrent requests
- Each takes 1 second
    

`Throughput ≈ 100 RPS`

If latency doubles:

`Throughput halves`

This is why:

> **Latency directly caps throughput**

---

## How to Increase Throughput in Express

### 1. Avoid Blocking the Event Loop

- Move CPU work to:
    
    - Worker threads
    - Separate services
        

---

### 2. Control Concurrency Explicitly

Limit in-flight work:

```js
import pLimit from "p-limit";
const limit = pLimit(10);

app.get("/api", async (req, res) => {
  await limit(() => slowOperation());
  res.send("ok");
});

```

This **protects throughput under load**.

---

### 3. Stream Instead of Buffer

Bad:

```js
const data = fs.readFileSync("big.json");
res.send(data);

```

Good:

```js
fs.createReadStream("big.json").pipe(res);

```

Streaming improves:

- Memory usage
- Sustained throughput
    

---

### 4. Horizontal Scaling (When Needed)

- Node processes (cluster / PM2)
- Containers + load balancer
    

But remember:

> Scaling hides inefficiency — it doesn’t fix it

---

## When Throughput Is the Primary Metric

- Internal APIs
- Batch systems
- Streaming services
- Message consumers
- Fan-out microservices
    

In these systems:

- **p95 latency + throughput** together tell the truth
- Average latency alone is misleading
    

---

## One-Line Takeaways (Write These Down)

- **Throughput is completed work per second**
    
- **Latency caps throughput**
    
- **Blocking kills throughput in Node**
    
- **Backpressure protects throughput**
    
- **High p95 + low throughput = overload**
    

---

## Final Truth (Important)

> **A fast request doesn’t mean a fast system.  
> A high-throughput system survives load.**