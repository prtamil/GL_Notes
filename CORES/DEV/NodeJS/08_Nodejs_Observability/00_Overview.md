# Observability: Seeing the Event Loop in Node.js

## Why this matters (for real systems)

Node failures are rarely crashes. They are **slow deaths**:

- Requests pile up
- Latency creeps up
- GC pauses get longer
- One hot function blocks everything
- Memory grows but never drops
    

By the time users complain, the **event loop has been unhealthy for minutes**.
Observability answers **one core question**:

> _Is my event loop making forward progress?_

Everything else—CPU, memory, async context—is just a lens to answer that.

---

## Mental Model: What We’re Observing

Think of Node as a **single conveyor belt**:

- JS execution
- Promise microtasks
- I/O callbacks
- Timers
- GC pauses
    

If _anything_ blocks or starves the belt, **everything behind it suffers**.

Observability tools let you measure:

1. **Delay** (event loop lag)
2. **Pressure** (CPU & GC)
3. **Retention** (heap growth)
4. **Causality** (which async chain caused it)
    

---

# 1. Event Loop Lag (The Heartbeat)

### What it is

**Event loop lag** = how late timers fire compared to when they _should_.

If a `setTimeout(fn, 10)` fires after 80ms → the loop was blocked for ~70ms.

This is the **earliest and cheapest signal** of trouble.

---

### Practical measurement (production-safe)

```js
// eventLoopLag.js
const { monitorEventLoopDelay } = require('perf_hooks');

const h = monitorEventLoopDelay({
  resolution: 20, // ms
});

h.enable();

setInterval(() => {
  const mean = Math.round(h.mean / 1e6);
  const p99 = Math.round(h.percentile(99) / 1e6);

  console.log({
    eventLoopLagMeanMs: mean,
    eventLoopLagP99Ms: p99,
  });

  h.reset();
}, 5000);

```

#### How to interpret

- **Mean < 10ms** → healthy
- **P99 spikes** → occasional blocking (JSON parse, sync crypto, regex)
- **Mean rising steadily** → CPU saturation or GC pressure
    

📌 **Key insight**  
Lag tells you _that_ you’re blocked, not _why_. That’s when you go deeper.

---

### Real-world failure example

```js
app.get('/report', (req, res) => {
  const data = fs.readFileSync('/huge.json'); // 💥
  const parsed = JSON.parse(data);
  res.json(parsed);
});

```

Symptoms:

- Event loop lag spikes
- All endpoints slow
- CPU “looks normal”
    

Without lag metrics, this looks like “random latency.”

---

# 2. CPU Profiling (What’s Blocking the Loop)

### What CPU profiling answers

> _Which JavaScript functions consumed the event loop time?_

Node CPU profiles show:

- Hot functions
- Hidden synchronous paths
- Excessive serialization/deserialization
    

---

### Capture CPU profile safely

```js
// cpuProfile.js
const inspector = require('inspector');
const fs = require('fs');

const session = new inspector.Session();
session.connect();

session.post('Profiler.enable', () => {
  session.post('Profiler.start');

  setTimeout(() => {
    session.post('Profiler.stop', (err, { profile }) => {
      fs.writeFileSync('cpu-profile.cpuprofile', JSON.stringify(profile));
      console.log('CPU profile saved');
      process.exit(0);
    });
  }, 30000); // capture 30s under load
});

```

Load this into:

- Chrome DevTools
- `node --inspect`
    

---

### What to look for

- Long **self time** on functions
- Repeated JSON/string operations
- RegExp backtracking
- Sync crypto (`pbkdf2Sync`, `bcryptSync`)
    

📌 **Hard truth**  
If CPU is busy, **async doesn’t matter**. The loop is still blocked.

---

# 3. Heap Snapshots (Why Memory Never Comes Back)

### What heap snapshots answer

> _Why didn’t memory drop after traffic stopped?_

Common causes:

- Global caches
- Event listeners not removed
- Closures retaining large objects
- Async context leaks
    

---

### Capture heap snapshot

```js
// heapSnapshot.js
const inspector = require('inspector');
const fs = require('fs');

const session = new inspector.Session();
session.connect();

session.post('HeapProfiler.enable', () => {
  session.post('HeapProfiler.takeHeapSnapshot', null, () => {
    console.log('Heap snapshot taken');
  });
});

session.on('HeapProfiler.addHeapSnapshotChunk', (m) => {
  fs.appendFileSync('heap.heapsnapshot', m.params.chunk);
});

```

---

### How to analyze

In Chrome DevTools:

- Compare **before vs after load**
    
- Look for:
    
    - Detached DOM-like structures (in Node: objects with no GC path)
    - Large arrays/maps growing monotonically
    - Retained closures
        

📌 **Key insight**  
Memory leaks often **increase event loop lag indirectly** via longer GC pauses.

---

# 4. Async Hooks (Tracing Causality)

### Why async hooks matter

Event loop lag tells you _something is slow_.  
Async hooks tell you **which async chain caused it**.

This answers:

> _Which request / job created this runaway async work?_

---

### Basic async hook tracing

```js
// asyncTrace.js
const async_hooks = require('async_hooks');
const fs = require('fs');

const indent = new Map();

const hook = async_hooks.createHook({
  init(asyncId, type, triggerAsyncId) {
    const space = indent.get(triggerAsyncId) || '';
    indent.set(asyncId, space + '  ');
    fs.writeSync(1, `${space}${type}(${asyncId})\n`);
  },
  destroy(asyncId) {
    indent.delete(asyncId);
  }
});

hook.enable();

```

Run this under load (carefully). You’ll see async trees.

---

### Practical usage patterns

- Detect **promise storms**
- Identify **runaway recursion via microtasks**
- Correlate async work to request IDs
    

Most production systems use **AsyncLocalStorage** on top of this.

```js
const { AsyncLocalStorage } = require('async_hooks');
const als = new AsyncLocalStorage();

app.use((req, res, next) => {
  als.run({ requestId: crypto.randomUUID() }, next);
});

function log(msg) {
  const store = als.getStore();
  console.log(store?.requestId, msg);
}

```

📌 **Critical insight**  
Async hooks are not for metrics—they’re for **root cause**.

---

# Putting It All Together (Production Playbook)

|Symptom|Tool|What You Learn|
|---|---|---|
|Latency spikes|Event loop lag|Is the loop blocked?|
|High CPU|CPU profile|Which JS functions?|
|Memory grows|Heap snapshot|What’s retained?|
|Random slow requests|Async hooks|Which async chain?|

---

## A Real Incident Flow

1. Alert: P99 latency ↑
2. Check: Event loop lag → spikes
3. CPU profile → `JSON.stringify`
4. Heap snapshot → massive response buffers
5. Fix → stream response, chunk serialization
    

This is **engineering**, not guessing.

---

## Final Advice (No Sugarcoating)

If you work with Node seriously:

- **Event loop lag is mandatory**
- **Heap snapshots save weekends**
- **CPU profiles beat opinions**
- **Async hooks separate seniors from juniors**
    

Observability is how Node stops being “magic” and becomes **mechanical**.