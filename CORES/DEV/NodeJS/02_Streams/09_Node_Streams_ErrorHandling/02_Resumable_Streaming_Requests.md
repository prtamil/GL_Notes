# Resumable HTTP Streaming (Range Requests)

_How downloads survive network failures, retries, and partial reads_

Large downloads **will fail**:

- Mobile network drops
- Wi-Fi changes
- Proxy timeouts
- Browser refreshes
    

The only reason video streaming and large downloads work reliably is **HTTP Range Requests**.

---

## 1. What Is a Range Request?

A client asks the server:

> “Give me bytes **X to Y** of this resource.”

### Example request

`GET /video.mp4 HTTP/1.1 Range: bytes=1000000-1999999`

Meaning:

- Start at byte `1,000,000`
- End at byte `1,999,999`
    

---

### Server response (partial content)

```js
HTTP/1.1 206 Partial Content
Content-Range: bytes 1000000-1999999/734003200
Content-Length: 1000000
Accept-Ranges: bytes

```

This is the **foundation of resumable streaming**.

---

## 2. Why Range Requests Matter (Real Systems)

Range requests enable:

|Feature|Without Range|With Range|
|---|---|---|
|Video streaming|❌ Restarts|✅ Resume|
|Large downloads|❌ Restart|✅ Resume|
|CDN caching|❌ Poor|✅ Excellent|
|Retries|❌ Wasteful|✅ Efficient|

---

## 3. Server Responsibilities (Non-Optional)

If you support resumable streaming, your server **must**:

1. Advertise support:
    
    `Accept-Ranges: bytes`
    
1. Handle `Range` header correctly
2. Return `206 Partial Content`
3. Return correct `Content-Range`
4. Stream only requested bytes
5. Handle invalid ranges safely
    

---

## 4. Minimal Production-Grade Node.js Range Server

### Single-file example (clean and realistic)

```js
import fs from 'fs';
import path from 'path';
import express from 'express';

const app = express();
const VIDEO_PATH = path.resolve('./video.mp4');

app.get('/video', (req, res) => {
  const stat = fs.statSync(VIDEO_PATH);
  const fileSize = stat.size;
  const range = req.headers.range;

  if (!range) {
    // Full file (not resumable)
    res.writeHead(200, {
      'Content-Length': fileSize,
      'Content-Type': 'video/mp4',
      'Accept-Ranges': 'bytes'
    });

    fs.createReadStream(VIDEO_PATH).pipe(res);
    return;
  }

  // Example: "bytes=1000-"
  const [startStr, endStr] = range.replace(/bytes=/, '').split('-');
  const start = parseInt(startStr, 10);
  const end = endStr ? parseInt(endStr, 10) : fileSize - 1;

  // Validate range
  if (start >= fileSize || end >= fileSize || start > end) {
    res.writeHead(416, {
      'Content-Range': `bytes */${fileSize}`
    });
    return res.end();
  }

  const chunkSize = end - start + 1;

  res.writeHead(206, {
    'Content-Range': `bytes ${start}-${end}/${fileSize}`,
    'Accept-Ranges': 'bytes',
    'Content-Length': chunkSize,
    'Content-Type': 'video/mp4'
  });

  fs.createReadStream(VIDEO_PATH, { start, end }).pipe(res);
});

app.listen(3000, () => {
  console.log('Range server running on port 3000');
});

```

---

## 5. What Happens During Resume (Step-by-Step)

1. Client downloads bytes `0 → 5MB`
2. Network fails
3. Client retries with:
    `Range: bytes=5242880-`
    
4. Server:
    - Reads from byte `5MB`
    - Sends `206 Partial Content`
        
5. Client appends data
6. Download completes
    

**No restart. No waste.**

---

## 6. Client-Side Resume Logic (Browser Example)

Browsers handle this automatically for:

- `<video>`
- `<audio>`
- Download manager
    

Manual fetch example:

```js
async function resumeDownload(url, start) {
  const res = await fetch(url, {
    headers: {
      Range: `bytes=${start}-`
    }
  });

  if (res.status !== 206) {
    throw new Error('Server does not support resume');
  }

  return res.body;
}

```

---

## 7. Handling Errors Mid-Stream

### Key reality

Once streaming starts:

- You cannot send JSON errors
- The only signal is **connection close**
    

### Best practice

- Let the connection drop
- Client retries with `Range`
    

**This is not a bug. It’s the design.**

---

## 8. Invalid Ranges (Very Important)

If client asks:

`Range: bytes=999999999-`

But file is smaller → must respond:

```js
HTTP/1.1 416 Range Not Satisfiable
Content-Range: bytes */734003200

```

This tells the client:

> “Your resume offset is invalid. Start over.”

---

## 9. Range Requests + Pipelines (Correct Cleanup)

```js
import { pipeline } from 'stream';

pipeline(
  fs.createReadStream(VIDEO_PATH, { start, end }),
  res,
  err => {
    if (err) {
      console.error('Stream failed:', err.message);
      res.destroy();
    }
  }
);

```

Always use `pipeline()` in production.

---

## 10. Range Requests in Microservices

### Common architecture

```js
Client → API Gateway → File Service → S3

```

### Gateway must:

- Forward `Range` header
- Forward `206` status
- Forward `Content-Range`
- Not buffer entire response
    

### ❌ Wrong

```js
await fetch(upstream).then(r => r.buffer());

```

### ✅ Correct

```js
pipeline(upstream.body, res);

```

---

## 11. Security & Performance Notes

### Prevent abuse

- Limit max chunk size
- Validate ranges
- Rate-limit resume attempts
    

### Use OS optimizations

- `fs.createReadStream` uses zero-copy where possible
- Avoid buffering
    

---

## 12. Mental Model (Memorize This)

```js
Errors are normal.
Truncation is a signal.
Resume is the recovery.

```

Range requests turn **network failure** into **retryable state**.

---

## Final Advice (Straight, Practical)

- If file > 10MB → support Range
- If video/audio → support Range
- If clients are mobile → support Range
- If reliability matters → Range is mandatory