# Event Loop DoS Lab (Node.js)

## Lab Setup (baseline)

Create a simple server:

```js
// server.js
const http = require('http');
const { monitorEventLoopDelay } = require('perf_hooks');

const h = monitorEventLoopDelay({ resolution: 20 });
h.enable();

setInterval(() => {
  console.log(
    'EL delay(ms):',
    (h.mean / 1e6).toFixed(2),
    'RSS(MB):',
    (process.memoryUsage().rss / 1024 / 1024).toFixed(1)
  );
}, 1000);

http.createServer((req, res) => {
  res.end('ok');
}).listen(3000);

```

Run it:

```js
node server.js

```

This is your **heartbeat monitor**.

---

## LAB 1: Sync CPU Blocking (Classic Event Loop Kill)

### Attack

Add this endpoint:

```js
if (req.url === '/cpu') {
  const end = Date.now() + 5000;
  while (Date.now() < end) {} // burn CPU
  res.end('done');
  return;
}

```

Hit it once:

```sh
curl http://localhost:3000/cpu

```

---

### What you’ll observe

- Server stops responding for ~5s
- Event loop delay spikes massively
- All other requests stall
    

---

### Why this works

The event loop is **single-threaded**.  
Any long sync work blocks _everything_.

---

### Fix pattern

- Move work to `worker_threads`
- Or chunk + yield (`setImmediate`)
    

---

## LAB 2: Microtask Starvation (Invisible DoS)

### Attack

Add this route:

```js
if (req.url === '/microtask') {
  function loop() {
    Promise.resolve().then(loop);
  }
  loop();
  res.end('started');
  return;
}

```

Call it once.

---

### What you’ll observe

- CPU goes to 100%
- Event loop delay increases
- **Timers and IO stop firing**
- Server never recovers
    

---

### Why this is dangerous

- No blocking code
- No stack trace
- Looks async and “safe”
    

Microtasks always run **before** libuv phases.

---

### Fix pattern

- Never recursively schedule promises
- Yield to macrotasks (`setImmediate`)
- Audit promise-heavy code
    

---

## LAB 3: JSON Memory Amplification

### Attack

Replace handler with:

```js
if (req.url === '/json') {
  let body = '';
  req.on('data', c => body += c);
  req.on('end', () => {
    JSON.parse(body);
    res.end('ok');
  });
  return;
}

```

Send a large payload:

```py
python - <<EOF
print("POST /json HTTP/1.1\r\nHost: localhost\r\nContent-Length: 100000000\r\n\r\n" + "a"*100000000)
EOF | nc localhost 3000

```

---

### What you’ll observe

- Memory shoots up
- GC thrashing
- Event loop delay climbs
- Process may OOM
    

---

### Why this works

- String concatenation reallocates
- JSON parsing explodes object graph
- GC can’t keep up
    

---

### Fix pattern

- Stream parsing
- Byte limits
- Reject early
    

---

## LAB 4: Backpressure Collapse (Streams)

### Attack

```js
if (req.url === '/stream') {
  req.on('data', chunk => {
    // sync work ignores backpressure
    const end = Date.now() + 50;
    while (Date.now() < end) {}
  });
  req.on('end', () => res.end('done'));
  return;
}

```

Send data continuously:

```sh
yes "AAAAAAAA" | curl -X POST --data-binary @- http://localhost:3000/stream

```

---

### What you’ll observe

- Memory grows
- Event loop delay rises
- Throughput collapses
    

---

### Why this works

- Backpressure is bypassed
- libuv delivers data
- V8 buffers it
- GC pressure feeds slowdown
    

---

### Fix pattern

- Use `pipeline()`
- Never block in `data` handlers
- Enforce chunk limits
    

---

## LAB 5: libuv Threadpool Saturation

### Attack

```js
const crypto = require('crypto');

if (req.url === '/crypto') {
  crypto.pbkdf2(
    'pw',
    'salt',
    500_000,
    64,
    'sha512',
    () => res.end('done')
  );
  return;
}

```

Hit concurrently:

```sh
ab -n 50 -c 10 http://localhost:3000/crypto

```

---

### What you’ll observe

- Requests hang
- CPU not fully used
- Event loop delay modest
- Everything feels “stuck”
    

---

### Why this works

- libuv threadpool size = 4
- Tasks queue up
- IO completion stalls
    

---

### Fix pattern

- Increase `UV_THREADPOOL_SIZE`
- Cap concurrency
- Use workers for heavy crypto
    

---

## LAB 6: Timer Flood (Scheduling Fairness Failure)

### Attack

```js
if (req.url === '/timers') {
  for (let i = 0; i < 1e6; i++) {
    setTimeout(() => {}, 0);
  }
  res.end('scheduled');
  return;
}

```

---

### What you’ll observe

- Timers delayed
- IO jitter
- Event loop delay unstable
    

---

### Why this works

libuv processes phases sequentially.  
Huge timer queues starve others.

---

### Fix pattern

- Never mass-schedule timers
- Batch work
- Use queues
    

---

## LAB 7: The “Alive but Dead” State (Worst Case)

Combine:

- JSON buffering
- Sync CPU
- Microtask recursion
    

You’ll see:

- Health checks pass
- Requests time out
- Autoscaling amplifies damage
- No crash, no recovery
    

This is **real production failure**.

---

## What You Should Learn From These Labs

### Patterns that always cause DoS

- Sync work on request path
- Unbounded buffering
- Recursive promises
- Ignoring backpressure
- Unlimited concurrency
    

---

## Core Metrics to Watch (Always)

- Event loop delay
- RSS / heap used
- Pending promises
- Active handles
- Threadpool queue depth
    

If these drift together → you’re under runtime attack.

---

## Final Mental Model

Event loop DoS is **not about traffic volume**.

It’s about **control**:

- Control of time
- Control of memory
- Control of ordering
    

Once you see these labs, real outages become obvious.