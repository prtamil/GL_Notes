This example intentionally covers:

- backpressure
- stalled pipelines
- memory leak detection
- logging + metrics
- safe shutdown
- error propagation
    

---

# ✅ **Production-Grade Stream Debugging Example (Single File)**

### **Scenario**

We process a **large log file**, transform each line, and write it to an output file.

Problems we guard against:

- input faster than output
- transform errors
- silent stalls
- memory growth over time
    

---

## **📄 `debug-streams-prod.js`**

```js
'use strict';

const fs = require('fs');
const readline = require('readline');
const { Transform, pipeline } = require('stream');

/* ----------------------------------------
   CONFIG
----------------------------------------- */

const INPUT_FILE = './input.log';
const OUTPUT_FILE = './output.log';
const LOG_INTERVAL_MS = 5000;

/* ----------------------------------------
   METRICS & INSTRUMENTATION
----------------------------------------- */

const metrics = {
  linesRead: 0,
  linesWritten: 0,
  startTime: Date.now(),
};

function logMetrics() {
  const mem = process.memoryUsage();
  const elapsed = ((Date.now() - metrics.startTime) / 1000).toFixed(1);

  console.log('[METRICS]', {
    elapsedSeconds: elapsed,
    linesRead: metrics.linesRead,
    linesWritten: metrics.linesWritten,
    rssMB: (mem.rss / 1024 / 1024).toFixed(1),
    heapUsedMB: (mem.heapUsed / 1024 / 1024).toFixed(1),
  });
}

const metricsTimer = setInterval(logMetrics, LOG_INTERVAL_MS);

/* ----------------------------------------
   TRANSFORM STREAM (BUSINESS LOGIC)
----------------------------------------- */

class LineTransform extends Transform {
  constructor() {
    super({ objectMode: true });
  }

  _transform(line, _, callback) {
    try {
      metrics.linesRead++;

      // simulate occasional bad data
      if (line.includes('ERROR')) {
        throw new Error('Bad log line detected');
      }

      const transformed = `[PROCESSED] ${line}\n`;
      metrics.linesWritten++;

      callback(null, transformed);
    } catch (err) {
      callback(err); // IMPORTANT: propagate error
    }
  }
}

/* ----------------------------------------
   STREAM SETUP
----------------------------------------- */

// Readable (line-by-line, avoids loading entire file)
const fileStream = fs.createReadStream(INPUT_FILE);

fileStream.on('error', (err) => {
  console.error('[READ STREAM ERROR]', err);
});

// Convert stream into line reader
const rl = readline.createInterface({
  input: fileStream,
  crlfDelay: Infinity,
});

// Writable stream with backpressure awareness
const outputStream = fs.createWriteStream(OUTPUT_FILE);

outputStream.on('drain', () => {
  console.log('[BACKPRESSURE] Output drained, resuming...');
});

outputStream.on('error', (err) => {
  console.error('[WRITE STREAM ERROR]', err);
});

/* ----------------------------------------
   PIPELINE (SAFE STREAM COMPOSITION)
----------------------------------------- */

pipeline(
  rl,                 // Readable (lines)
  new LineTransform(),// Transform
  outputStream,       // Writable
  (err) => {
    clearInterval(metricsTimer);

    if (err) {
      console.error('[PIPELINE FAILED]', err.message);
    } else {
      console.log('[PIPELINE SUCCESS] Processing complete');
    }

    logMetrics();
  }
);

/* ----------------------------------------
   PROCESS-LEVEL SAFETY NETS
----------------------------------------- */

process.on('SIGINT', () => {
  console.log('\n[SHUTDOWN] Gracefully shutting down...');
  clearInterval(metricsTimer);
  outputStream.end(() => process.exit(0));
});

process.on('uncaughtException', (err) => {
  console.error('[UNCAUGHT EXCEPTION]', err);
  process.exit(1);
});

process.on('unhandledRejection', (reason) => {
  console.error('[UNHANDLED REJECTION]', reason);
  process.exit(1);
});

```

---

# 🧠 **DETAILED EXPLANATION (Important Part)**

---

## **1️⃣ Why `readline` instead of `fs.createReadStream` directly?**

```js
const rl = readline.createInterface({ input: fileStream });

```

### Problem avoided

- Reading raw chunks gives you **partial lines**
- Parsing line-based logs becomes error-prone
    

### Benefit

- One line at a time
- Natural backpressure support
- Constant memory usage
    

✅ **This is production-safe for large files**

---

## **2️⃣ Object Mode Transform (Critical Concept)**

```js
class LineTransform extends Transform {
  constructor() {
    super({ objectMode: true });
  }
}

```

### Why objectMode?

- We process **strings (lines)**, not Buffers
- Prevents accidental buffer growth
- Easier debugging
    

### Production rule

> If your data is logical units (lines, JSON, objects), use `objectMode`.

---

## **3️⃣ Error Propagation (Most Common Production Bug)**

```js
callback(err);

```

### Why this matters

- If you `throw` inside a stream → **pipeline stalls**
- If you swallow errors → **silent failure**
    

`pipeline()` ensures:

- all streams are destroyed
- callback is invoked
- resources are released
    

🚫 **Never manually `.pipe()` in production for complex flows**

---

## **4️⃣ Backpressure Visibility**

```js
outputStream.on('drain', () => {
  console.log('[BACKPRESSURE] Output drained');
});

```

### What this tells you

- Downstream is slow
- Buffer filled up
- Writes were paused
    

If you **never** see `drain`:

- output is fast
- or you’re leaking memory upstream
    

---

## **5️⃣ Memory Leak Detection (REAL Production Debugging)**

```js
process.memoryUsage()

```

You’re watching:

- `rss` → actual memory used by process
- `heapUsed` → JS heap
    

### Red flags

- heapUsed increases continuously
- rss never stabilizes
    

This usually means:

- ignoring backpressure
- retaining references to chunks
- listeners added repeatedly
    

---

## **6️⃣ Why Periodic Metrics Logging Matters**

```js
setInterval(logMetrics, 5000);

```

This answers:

- Is the pipeline making progress?
- Is it stalled?
- Is memory climbing?
- Is throughput stable?
    

📌 **Without this, production stream bugs are invisible**

---

## **7️⃣ Safe Shutdown (Often Forgotten)**

```js
process.on('SIGINT', ...)

```

Why this matters:

- prevents corrupted files
- flushes buffers
- avoids partial writes
    

Production streams **must close cleanly**.

---

## **8️⃣ Why `pipeline()` Is Non-Negotiable**

```js
pipeline(a, b, c, callback);

```

### It guarantees:

- error propagation
- stream destruction
- no hanging processes
- no leaked file descriptors
    

> `.pipe()` is fine for demos  
> `pipeline()` is for production

---

# 🧪 **How to Debug This in Real Production**

1. **Pipeline stuck?**
    
    - Check metrics logs
    - Is `linesRead` increasing?
    - Is `linesWritten` frozen?
        
2. **Memory climbing?**
    
    - Look at `heapUsedMB`
    - Look for missing backpressure handling
        
3. **Random crashes?**
    
    - Errors in transform not propagated
    - Missing `pipeline()` callback
        
4. **Slow performance?**
    
    - CPU flamegraph (`clinic flame`)
    - Chunk size too small / too large
        

---

# ✅ **Mental Model You Should Keep**

> Streams don’t fail loudly.  
> They fail **silently unless you instrument them**.