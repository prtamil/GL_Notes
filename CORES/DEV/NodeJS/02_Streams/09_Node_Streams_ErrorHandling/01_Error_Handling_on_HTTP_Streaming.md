# Error Handling in HTTP Streaming

_How to fail safely when data is already flowing over the network_

HTTP streaming is harder than file streams because:

- Headers may already be sent
- Clients may disconnect at any time
- Errors can occur **mid-stream**
- You often cannot “retry” cleanly
    

If you don’t handle this correctly, you get:

- Hung sockets
- Partial responses without explanation
- Memory leaks
- Crashed Node processes
    

---

## 1. Why HTTP Streaming Error Handling Is Different

### Normal HTTP request (non-streaming)

```js
Request → Process → Response (once)

```

If something fails:

- Return `500`
- Send JSON error
- Done
    

---

### Streaming HTTP response

```js
Request → Headers sent → Data flowing → Error happens 💥

```

Once headers are sent:

- You **cannot change the status code**
- You **cannot send a JSON error**
    
- The only signal left is:
    
    - Connection close
    - Truncated stream
    - Protocol-level signal (if designed)
        

This changes everything.

---

## 2. Core Failure Scenarios in HTTP Streaming

You must design for these explicitly:

1. **Error before headers are sent**
2. **Error after headers are sent**
3. **Client disconnects early**
4. **Upstream stream fails (proxying)**
5. **Timeout / cancellation**
    

Each has different handling.

---

## 3. Error Before Headers Are Sent (Easy Case)

This is the _only_ case where classic HTTP error handling works.

### Example: file not found before streaming starts

```js
app.get('/download', (req, res) => {
  const fs = require('fs');

  const stream = fs.createReadStream('missing.mp4');

  stream.on('error', err => {
    // Headers not sent yet
    res.status(404).json({ error: 'File not found' });
  });

  stream.pipe(res);
});

```

### Key rule

> If `res.headersSent === false`, you can still respond normally.

---

## 4. Error After Headers Are Sent (The Hard Case)

Once streaming begins:

```js
res.writeHead(200);
res.write(chunk);

```

You **cannot** send JSON errors anymore.

### What you CAN do

- Destroy the response
- Close the socket
- Log the error
- Let the client detect truncation
    

---

### Example: error mid-stream

```js
app.get('/stream', (req, res) => {
  const fs = require('fs');

  const stream = fs.createReadStream('video.mp4');

  res.writeHead(200, {
    'Content-Type': 'video/mp4'
  });

  stream.on('error', err => {
    console.error('Stream failed:', err.message);

    // Cannot send JSON now
    res.destroy(err);
  });

  stream.pipe(res);
});

```

### Client perspective

- Video stops playing
- Download ends early
- Client may retry or fail
    

**This is expected behavior.**

---

## 5. Correct Pattern: `pipeline()` with HTTP Responses

Never manually pipe streams into HTTP responses in production.

### ✅ Production-safe streaming

```js
const { pipeline } = require('stream');

app.get('/stream', (req, res) => {
  const fs = require('fs');

  pipeline(
    fs.createReadStream('video.mp4'),
    res,
    (err) => {
      if (err) {
        console.error('Pipeline failed:', err.message);

        if (!res.headersSent) {
          res.status(500).end('Stream failed');
        } else {
          res.destroy(err);
        }
      }
    }
  );
});

```

### Why this matters

- Errors propagate correctly
- Streams are destroyed
- Socket closes cleanly
- No leaked file descriptors
    

---

## 6. Handling Client Disconnects (VERY Important)

Clients close connections all the time:

- Browser tab closed
- Mobile network drop
- Proxy timeout
    

### ❌ Common mistake

Ignoring disconnects → backend keeps streaming → wasted I/O

---

### ✅ Correct handling

```js
app.get('/stream', (req, res) => {
  const fs = require('fs');
  const stream = fs.createReadStream('big.mp4');

  req.on('aborted', () => {
    console.log('Client disconnected');
    stream.destroy();
  });

  pipeline(stream, res, err => {
    if (err) console.error(err);
  });
});

```

### Important signals

|Event|Meaning|
|---|---|
|`req.aborted`|Client closed connection|
|`res.close`|Socket closed|
|`res.finish`|Response completed normally|

---

## 7. Proxying Streams (Upstream → Downstream)

Very common in microservices:

`Client → API → Another service → File/S3`

### Example: proxy stream with error handling

```js
const http = require('http');
const { pipeline } = require('stream');

app.get('/proxy', (req, res) => {
  const upstream = http.get('http://fileservice/video');

  upstream.on('response', upstreamRes => {
    res.writeHead(upstreamRes.statusCode, upstreamRes.headers);

    pipeline(upstreamRes, res, err => {
      if (err) {
        console.error('Proxy stream failed:', err.message);
        res.destroy(err);
      }
    });
  });

  upstream.on('error', err => {
    if (!res.headersSent) {
      res.status(502).end('Upstream error');
    } else {
      res.destroy(err);
    }
  });
});

```

### Key insight

> You must handle errors on **both** upstream and downstream streams.

---

## 8. Designing Stream-Friendly Error Protocols

If truncation is not acceptable, **design your protocol**.

### Option 1: Chunked JSON framing

```js
{ "type": "data", "chunk": "..." }
{ "type": "data", "chunk": "..." }
{ "type": "error", "message": "Upstream failed" }

```

Client can interpret error mid-stream.

---

### Option 2: SSE (Server-Sent Events)

```js
res.write(`event: error\ndata: ${JSON.stringify(err)}\n\n`);

```

SSE supports explicit error events.

---

### Option 3: HTTP Range + Retry

For large files:

- Support `Range` headers
- Client retries from last byte
    

This is how video streaming survives errors.

---

## 9. Timeouts and Cancellation

### AbortController (modern Node)

```js
app.get('/stream', async (req, res) => {
  const fs = require('fs');
  const { pipeline } = require('stream/promises');
  const ac = new AbortController();

  req.on('aborted', () => ac.abort());

  try {
    await pipeline(
      fs.createReadStream('big.mp4'),
      res,
      { signal: ac.signal }
    );
  } catch (err) {
    console.error('Aborted or failed:', err.message);
  }
});

```
---

## 10. Mental Model (Burn This In)

### HTTP streaming error rules

1. **Before headers** → send HTTP error
2. **After headers** → destroy stream
3. **Client disconnect** → stop producing data
4. **Multiple streams** → use `pipeline()`
5. **Never trust the network**
    

---

## Final Advice (Hard Truth)

- You **cannot fix** mid-stream errors with HTTP status codes
- Streaming APIs must be designed with failure in mind
- `pipeline()` is not optional in production
- Client disconnects are normal, not exceptional
- If correctness matters → design resumable streams