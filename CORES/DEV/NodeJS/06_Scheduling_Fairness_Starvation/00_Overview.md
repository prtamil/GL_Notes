# Scheduling Fairness & Starvation in Node.js

## Executive Summary

Node.js can handle **100k concurrent sockets** and still fall over because of **one badly behaved execution path**.

This is not a paradox.  
It’s a **scheduling fairness problem**.

Node is fast because it’s **single-threaded**, but that also means:

- One task can **starve** everything else
- “Async” does **not automatically mean fair**
- Microtasks can silently **block I/O**
- Long synchronous chains can **freeze the event loop**
    

This essay explains **why this happens**, **how real outages occur**, and **how to design systems that avoid starvation**.

---

## 1. What Scheduling Fairness Actually Means

### Definition

**Scheduling fairness** means:

> No class of work (timers, I/O, promises, sockets, requests) is allowed to monopolize the event loop indefinitely.

**Starvation** happens when:

- Some tasks _never get CPU time_
- Latency grows unbounded
- Health checks fail
- Requests time out even though the process is “alive”
    

---

## 2. Node’s Event Loop Is Cooperative (Not Preemptive)

This is the root of everything.

### Preemptive (OS threads)

- OS can interrupt a task
- Long-running code gets preempted
- Fairness enforced by scheduler
    

### Node.js (Single-threaded, cooperative)

- **Nothing interrupts your JS**
- Control returns to the event loop **only when your code yields**
- If you don’t yield → **everything waits**
    

> Node trusts you to behave.

---

## 3. The Event Loop Phases (Very Briefly)

Simplified order per tick:

1. Timers (`setTimeout`, `setInterval`)
2. I/O callbacks
3. `setImmediate`
4. **Microtasks** (Promises, `queueMicrotask`) — _after every phase_
5. Next tick
    

Key insight:

> **Microtasks run to completion before the loop moves on**

This is where fairness breaks.

---

## 4. Microtask Starvation (The Silent Killer)

### The Problem

Promises are often treated as “cheap async”.  
They are not.

#### Dangerous Code

```js
function loop() {
  Promise.resolve().then(loop);
}
loop();

```

### What Happens

- Each `.then()` schedules a **microtask**
- Microtasks run **before timers, I/O, sockets**
- New microtasks are added **faster than the loop can progress**
    

Result:

- Event loop never reaches I/O
- No socket reads
- No HTTP responses
- CPU at 100%
- Process looks “alive” but is dead
    

This is **microtask starvation**.

---

## 5. Why “Just Async” Is Not Enough

### Common Myth

> “If it’s async, it won’t block Node.”

False.

### Example: Async That Blocks

```js
async function processLargeArray(arr) {
  for (const item of arr) {
    await Promise.resolve(); // yields to microtask queue only
    heavyCompute(item);
  }
}

```

This:

- Never yields to timers or I/O
- Starves sockets under load
    

### Correct Yielding

```js
function yieldToEventLoop() {
  return new Promise(resolve => setImmediate(resolve));
}

async function fairProcessing(arr) {
  for (const item of arr) {
    heavyCompute(item);
    await yieldToEventLoop();
  }
}

```

Now:

- I/O callbacks get a chance
- Timers fire
- Requests stay responsive
    

---

## 6. Long Synchronous Chains (Classic Production Bug)

### Example

```js
app.get("/report", (req, res) => {
  const data = hugeArray.map(x => expensiveTransform(x));
  res.json(data);
});

```

What happens under load:

- One request blocks the event loop
- All other sockets wait
- Latency explodes
- Health checks fail
- Load balancer ejects instance
    

Even **10ms synchronous CPU** per request can kill throughput at scale.

---

## 7. Why Node “Handles 100k Sockets” But Dies Anyway

Node handles many sockets because:

- Sockets are mostly idle
- OS handles readiness
- Node reacts to events
    

But fairness collapses when:

- One request triggers a CPU-heavy path
- One promise chain never yields
- One tight loop processes unbounded data
    

Sockets don’t save you from **scheduler abuse**.

---

## 8. Real-World Outage Pattern

This pattern shows up everywhere:

1. New feature deployed
2. Adds async recursion / promise loop
3. Works in staging
4. Production traffic increases
5. Event loop starvation
6. p99 latency → seconds
7. Kubernetes restarts pods
8. Engineers chase “memory leak” (wrong cause)
    

Root cause:

> **Event loop starvation, not memory or sockets**

---

## 9. Backpressure ≠ Fairness

Streams help, but don’t solve everything.

### Backpressure protects memory
### Fairness protects time

You can:

- Respect backpressure
- Still starve timers and sockets
    

Fairness requires **intentional yielding**.

---

## 10. Detection & Instrumentation

### Event Loop Delay

```js
const { monitorEventLoopDelay } = require("perf_hooks");

const h = monitorEventLoopDelay();
h.enable();

setInterval(() => {
  console.log("p99 delay:", h.percentile(99));
}, 1000);

```

If this spikes:

- You are starving the loop
    

### Symptoms

- Requests queue but CPU is high
- Logs stop flushing
- Metrics freeze
- No crashes, just timeouts
    

---

## 11. Design Rules to Avoid Starvation

### Rule 1: Bound Work Per Tick

Never process unbounded data in one turn.

### Rule 2: Yield Explicitly

Use:

- `setImmediate`
- `setTimeout(fn, 0)` (less ideal)
- Worker threads for CPU work
    

### Rule 3: Microtasks Are Not a Yield Point

Promises **do not** yield to I/O.

### Rule 4: Separate Concerns

- I/O thread → orchestration
- Worker threads → CPU
- Streams → flow control
    

---

## 12. Worker Threads: Real Fairness for CPU Work

```js
const { Worker } = require("worker_threads");

new Worker("./cpuTask.js", { workerData });

```

This:

- Preserves responsiveness
- Prevents starvation
- Scales predictably
    

---

## 13. Mental Model to Remember (Interview Gold)

> Node.js is not slow — it is **trusting**

If you:

- Yield fairly → Node flies
- Hog the loop → Node collapses
    

---

## Final Takeaway

**Scheduling fairness is the hidden tax of Node.js.**

- Async does not guarantee fairness
- Microtasks can starve the system
- One bad loop can kill thousands of sockets
- Production stability depends on _intentional yielding_
    

If you understand this topic deeply, you’re no longer a “Node user” —  
you’re thinking like a **Node runtime engineer**.