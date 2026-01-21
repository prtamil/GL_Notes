# Tuning a Real HTTP → Transform → File Pipeline

## Scenario (Real World)

**Problem**  
Download a large HTTP response (JSONL, CSV, logs, media, etc.), apply a transformation, and write to disk **without**:

- blowing memory
- starving the CPU
- collapsing throughput
    

**Pipeline**

```js
HTTP Readable → Transform → File Writable

```

---

## 1️⃣ The Core Performance Constraints

|Stage|Risk|
|---|---|
|HTTP Read|Network bursts|
|Transform|CPU bottleneck|
|File Write|Disk backpressure|

Your goal:

> **Let the slowest stage dictate the speed — not memory growth.**

That’s exactly what backpressure + tuning does.

---

## 2️⃣ Tuned Single-File Production Example

### What this pipeline does

- Streams an HTTP download
- Uppercases data (simulating CPU work)
- Writes to a file
- Measures throughput + memory
    

---

### ✅ Full Tuned Pipeline (Single File)

```js
/**
 * Tuned HTTP → Transform → File pipeline
 * Run: node pipeline.js
 */

const http = require('http');
const fs = require('fs');
const { Transform, pipeline } = require('stream');
const { promisify } = require('util');

const pipelineAsync = promisify(pipeline);

// =====================
// CONFIG (TUNE HERE)
// =====================
const HTTP_BUFFER = 256 * 1024;   // 256 KB
const TRANSFORM_BUFFER = 64 * 1024; // 64 KB
const FILE_BUFFER = 512 * 1024;   // 512 KB

const OUTPUT_FILE = './output.data';
const URL = 'http://ipv4.download.thinkbroadband.com/100MB.zip';

// =====================
// TRANSFORM (CPU BOUND)
// =====================
class UppercaseTransform extends Transform {
  constructor() {
    super({
      highWaterMark: TRANSFORM_BUFFER
    });
  }

  _transform(chunk, enc, cb) {
    // Simulate CPU work
    const transformed = chunk.toString().toUpperCase();
    cb(null, transformed);
  }
}

// =====================
// METRICS
// =====================
let bytes = 0;
const startTime = Date.now();

function logMetrics() {
  const { rss, heapUsed } = process.memoryUsage();
  const elapsed = (Date.now() - startTime) / 1000;

  console.log({
    throughputMBps: ((bytes / elapsed) / 1024 / 1024).toFixed(2),
    rssMB: Math.round(rss / 1024 / 1024),
    heapMB: Math.round(heapUsed / 1024 / 1024)
  });
}

setInterval(logMetrics, 1000);

// =====================
// PIPELINE
// =====================
async function run() {
  const fileStream = fs.createWriteStream(OUTPUT_FILE, {
    highWaterMark: FILE_BUFFER
  });

  http.get(URL, res => {
    res.on('data', chunk => {
      bytes += chunk.length;
    });

    const transform = new UppercaseTransform();

    pipeline(
      res,
      transform,
      fileStream,
      err => {
        if (err) {
          console.error('Pipeline failed:', err);
        } else {
          console.log('Pipeline completed successfully');
          logMetrics();
          process.exit(0);
        }
      }
    );
  });
}

run();

```

---

## 3️⃣ Why These `highWaterMark` Values Work

### 🌐 HTTP Readable — 256 KB

```js
res (IncomingMessage)

```

Why:

- Network packets arrive in bursts
- Larger buffers smooth jitter
- Too large → memory spikes during slow transforms
    

**Rule**: Medium-sized chunks for network IO

---

### 🔄 Transform — 64 KB (Smallest)

```js
new Transform({ highWaterMark: 64KB })

```

Why:

- Transform is CPU-bound
- Slowest stage must **limit buffering**
- Forces upstream backpressure early
    

> **This is the most important buffer in the pipeline.**

---

### 💾 File Writable — 512 KB

```js
fs.createWriteStream({ highWaterMark: 512KB })

```

Why:

- Disk writes benefit from batching
- OS write-behind buffering works well
- Larger chunks = fewer syscalls
    

---

## 4️⃣ What Happens Under the Hood (Critical Insight)

When transform slows down:

```js
File buffer fills →
Transform write() returns false →
HTTP stream pauses →
TCP window shrinks →
Sender slows down

```

That’s **end-to-end backpressure propagation**.  
No memory growth.  
No manual throttling.

---

## 5️⃣ What Happens If You Tune It Wrong

### ❌ Huge Transform Buffer (Memory Bloat)

```js
highWaterMark: 5 * 1024 * 1024

```

Result:

- HTTP keeps pushing
- Transform queues data
- RSS climbs steadily
- GC churn
    

---

### ❌ Tiny HTTP Buffer (Starvation)

```js
highWaterMark: 8 * 1024
```

Result:

- CPU idle between reads
- Throughput collapses
- Excessive syscall overhead
    

---

## 6️⃣ Benchmarking: How to Tune Scientifically

### Step 1: Change ONE buffer at a time

Try:

- 64KB
- 128KB
- 256KB
- 512KB
    

### Step 2: Observe

- Throughput (MB/s)
- RSS stability
- CPU usage
    

### Step 3: Pick the **knee of the curve**

Where:

- Throughput stops increasing
- Memory is stable
    

---

## 7️⃣ Production Rules You Should Memorize

✔ Smallest `highWaterMark` goes to **slowest stage**  
✔ Network → medium buffers  
✔ Disk → larger buffers  
✔ Measure RSS, not just heap  
✔ Defaults are safe, not optimal

---

## Final Mental Model

> **Streams don’t give performance.  
> Backpressure + tuning does.**

Once you understand this pipeline, you understand **Node.js at scale**.