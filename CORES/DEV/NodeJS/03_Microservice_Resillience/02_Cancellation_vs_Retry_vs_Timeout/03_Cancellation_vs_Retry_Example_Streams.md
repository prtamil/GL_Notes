## Streams + Cancellation + Timeout + Retry (Correctly Designed)

### Scenario (Realistic)

An HTTP server:

- Accepts a **large streamed upload**
- Transforms data (line processing)
- Uploads to a **slow, flaky remote sink**
- Retries on transient failures
- Cancels everything if:
    
    - Client disconnects
    - Request times out
        

---

## FULL SINGLE FILE CODE

```js
/**
 * node upload.js
 */

const http = require('http');
const { Transform, Writable } = require('stream');
const { pipeline } = require('stream/promises');

/* ============================================================
 * 1. REQUEST LIFETIME + CANCELLATION
 * ============================================================
 */

function createRequestContext(req, timeoutMs) {
  const ac = new AbortController();
  const { signal } = ac;

  // Client disconnect → cancellation
  req.on('close', () => {
    ac.abort(new Error('Client disconnected'));
  });

  // Timeout policy → cancellation
  const timeout = setTimeout(() => {
    ac.abort(new Error('Request timeout'));
  }, timeoutMs);

  return {
    signal,
    cleanup() {
      clearTimeout(timeout);
    }
  };
}

/* ============================================================
 * 2. RETRY WRAPPER (PIPELINE LEVEL)
 * ============================================================
 */

async function retryPipeline(createPipeline, {
  signal,
  retries = 3,
  isRetryable = () => true
}) {
  let attempt = 0;

  while (true) {
    if (signal.aborted) {
      throw signal.reason;
    }

    try {
      return await createPipeline();
    } catch (err) {
      if (signal.aborted) {
        throw signal.reason;
      }

      attempt++;

      if (attempt > retries || !isRetryable(err)) {
        throw err;
      }

      console.log(`Retrying pipeline (attempt ${attempt})`);
    }
  }
}

/* ============================================================
 * 3. TRANSFORM STREAM (DATA PROCESSING)
 * ============================================================
 */

class LineUppercaseTransform extends Transform {
  constructor() {
    super();
    this.buffer = '';
  }

  _transform(chunk, enc, cb) {
    this.buffer += chunk.toString();
    const lines = this.buffer.split('\n');
    this.buffer = lines.pop();

    for (const line of lines) {
      this.push(line.toUpperCase() + '\n');
    }

    cb();
  }

  _flush(cb) {
    if (this.buffer) {
      this.push(this.buffer.toUpperCase());
    }
    cb();
  }
}

/* ============================================================
 * 4. WRITABLE STREAM (FLAKY REMOTE SINK)
 * ============================================================
 */

class RemoteUploadStream extends Writable {
  _write(chunk, enc, cb) {
    // Simulate slow network
    setTimeout(() => {
      // Simulate transient failure
      if (Math.random() < 0.15) {
        cb(new Error('Remote storage timeout'));
      } else {
        cb();
      }
    }, 100);
  }
}

/* ============================================================
 * 5. PIPELINE ASSEMBLY
 * ============================================================
 */

function createUploadPipeline(req, signal) {
  return pipeline(
    req,                         // Readable (HTTP body)
    new LineUppercaseTransform(),// Transform
    new RemoteUploadStream(),    // Writable
    { signal }
  );
}

/* ============================================================
 * 6. HTTP SERVER (ORCHESTRATION)
 * ============================================================
 */

http.createServer(async (req, res) => {
  if (req.method !== 'POST') {
    res.writeHead(405);
    return res.end();
  }

  const { signal, cleanup } = createRequestContext(req, 5000);

  try {
    await retryPipeline(
      () => createUploadPipeline(req, signal),
      {
        signal,
        retries: 3,
        isRetryable: err =>
          err.message.includes('timeout')
      }
    );

    res.writeHead(200);
    res.end('Upload successful');
  } catch (err) {
    if (err.message === 'Client disconnected') {
      res.writeHead(499);
      res.end('Client disconnected');
    } else if (err.message === 'Request timeout') {
      res.writeHead(504);
      res.end('Request timeout');
    } else {
      res.writeHead(500);
      res.end('Upload failed');
    }
  } finally {
    cleanup();
  }
}).listen(3000, () => {
  console.log('Server listening on port 3000');
});

```

---

# DETAILED EXPLANATION (CONCEPT BY CONCEPT)

## 1. Streams Handle **Data Flow**

- `req` is a **Readable stream**
- `Transform` processes data incrementally
- `Writable` consumes data slowly
    
- **Backpressure is automatic**
    

This ensures:

- No buffering entire uploads in memory
- No manual flow control
    

---

## 2. Backpressure (Silent but Critical)

If `RemoteUploadStream` is slow:

- `Writable` buffers fill
- `Transform` pauses
- `Readable (req)` pauses reading from socket
    

Nothing crashes.  
Nothing spins.  
This is **normal operation**, not an error.

---

## 3. Cancellation = Authority

Cancellation comes from **outside data flow**:

`AbortController`

Sources:

- Client disconnect
- Timeout
    

When aborted:

- `pipeline()` destroys **all streams**
- In-flight writes stop
- File descriptors / sockets close
- Memory is freed immediately
    

This is **not optional behavior**.

---

## 4. Timeout Is a Policy, Not a Mechanism

Timeout does **not** stop streams directly.

Instead:

`timeout → abort → pipeline destroys streams`

This keeps responsibility clean:

- Timeout decides _when_
- Abort decides _how_
- Streams decide _what to clean_
    

---

## 5. Retry Happens at the Pipeline Level

This is critical.

❌ Retrying inside `_write()`  
❌ Retrying inside `_transform()`

Those corrupt stream state.

✅ Retry **recreates the entire pipeline**

`retryPipeline(() => createUploadPipeline(...))`

Why?

- Streams are stateful
- Once broken, they must be rebuilt
- This guarantees correctness
    

---

## 6. Cancellation Always Beats Retry

Every retry loop checks:

`if (signal.aborted) throw signal.reason;`

Meaning:

- Client disconnect → no retry
- Timeout → no retry
- Shutdown → no retry
    

Retries only happen if **work is still relevant**.

---

## 7. Error Semantics (Important)

|Error Type|Meaning|
|---|---|
|AbortError|Intentional stop|
|Timeout|Policy decision|
|Stream error|Failure|
|Retryable error|Transient|

Cancellation is **not a bug**.  
It’s a **control decision**.

---

## 8. Why This Design Is Production-Grade

### Clear separation

|Layer|Responsibility|
|---|---|
|Streams|Data movement|
|Backpressure|Flow control|
|Retry|Reliability|
|AbortController|Authority|
|Timeout|Policy|

No layer leaks into another.

---

## 9. Common Bugs This Avoids

❌ Retrying after client disconnect  
❌ Retrying half-broken streams  
❌ Manual `.destroy()` chaos  
❌ Memory blowups  
❌ Hanging uploads

---

## FINAL MENTAL MODEL (LOCK THIS IN)

> **Streams move data**  
> **Backpressure regulates speed**  
> **Retry rebuilds work**  
> **Timeout decides patience**  
> **Cancellation decides relevance**

If relevance is gone, **nothing else matters**.