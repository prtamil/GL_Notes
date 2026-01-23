# User-Controllable Surfaces at the libuv Level (Node.js)

## Big Picture

libuv manages:

- Event loop phases
- Threadpool
- IO watchers
- Timers
- OS handles (FDs, sockets)
    

Node APIs **project user input into libuv queues**.

If user input can reach one of these projections unbounded → libuv is under attacker control.

---

## 1. libuv Threadpool (High-Risk Surface)

### What goes through the threadpool

|Node API|Uses libuv pool|
|---|---|
|`fs.*` (most async)|Yes|
|`crypto.pbkdf2`, `scrypt`|Yes|
|`zlib`|Yes|
|`dns.lookup()`|Yes|

Default pool size = **4 threads**

---

### How users control it

Any request that triggers these APIs queues work into the pool.

Example:

```js
app.get('/hash', (req, res) => {
  crypto.pbkdf2(
    req.query.pw,  // user input
    'salt',
    500_000,
    64,
    'sha512',
    () => res.end('ok')
  );
});

```

One user → 1 threadpool task  
10 concurrent users → **threadpool saturation**

---

### Failure mode

- Threadpool queue grows
- Completion callbacks stall
- Requests hang
- Event loop looks idle
    

This is _classic production outage behavior_.

---

### Hardening

- Limit concurrency explicitly
- Move heavy work to `worker_threads`
- Cap iterations / input size
- Increase `UV_THREADPOOL_SIZE` cautiously
    

---

## 2. Timers Phase (User-Driven Scheduling)

### Node APIs → libuv timers

- `setTimeout`
- `setInterval`
- `setImmediate` (check phase)
    

---

### User control vector

Any user action that causes scheduling:

```js
app.get('/ping', () => {
  setTimeout(() => {}, 0);
});

```

At scale:

```js
Requests → timers → libuv timer heap

```

---

### Failure mode

- Huge timer queues
- Timer phase dominates
- IO callbacks delayed
- Scheduling fairness collapses
    

---

### Why this is dangerous

Timers are:

- Cheap individually
- Expensive at scale
- Hard to observe
    

---

### Hardening

- Avoid per-request timers
- Reuse timers
- Batch work
- Cap outstanding timers
    

---

## 3. IO Watchers (Sockets & Streams)

### What libuv manages

- Socket readability/writability
- Backpressure signaling
- Polling
    

---

### How users control it

By opening connections or streaming data:

```js
req.on('data', chunk => { /* slow work */ });

```

Users control:

- Rate of arrival
- Chunk sizes
- Connection lifetime
    

---

### Failure mode

- Backpressure collapse
- JS buffering grows
- Memory spikes
- Event loop delay increases
    

libuv keeps delivering data; JS can’t keep up.

---

### Hardening

- Enforce byte limits
- Enforce timeouts
- Use `pipeline()`
- Abort on slow consumers
    

---

## 4. File Descriptors (FD Pressure)

### libuv responsibility

- Open files
- Network sockets
- Pipes
    

---

### User control vector

Anything that opens FDs per request:

```js
fs.createReadStream(userPath);

```

If not closed properly → FD leak.

---

### Failure mode

- `EMFILE`
- Random IO failures
- libuv unable to register watchers
    

---

### Hardening

- Always close streams
- Track open handles
- Enforce per-request limits
    

---

## 5. DNS Resolution (Surprising One)

### Node API

```js
dns.lookup()

```

Uses libuv threadpool.

---

### User control vector

```js
app.get('/resolve', async (req, res) => {
  dns.lookup(req.query.host, () => res.end());
});

```

Attackers can:

- Trigger DNS storms
- Block threadpool
- Stall unrelated fs/crypto work
    

---

### Hardening

- Cache aggressively
- Limit DNS lookups
- Use OS caching carefully
    

---

## 6. Signal Handling & Process Events (Low-frequency, High Impact)

While users can’t send OS signals directly in most cases, container environments or misconfigurations can expose:

- `SIGTERM`
- `SIGUSR1`
    

Poor handling can:

- Interrupt libuv loop
- Leave resources dangling
    

---

## 7. `process.nextTick` (Not libuv, but worse)

This is **above libuv**, but it **preempts libuv entirely**.

```js
process.nextTick(() => {
  process.nextTick(() => { /* starve loop */ });
});

```

User input that triggers this is catastrophic.

---

## Summary Table (Important)

|Surface|User Influence|Failure|
|---|---|---|
|Threadpool|High|Requests hang|
|Timers|Medium–High|IO starvation|
|Streams|High|Memory blowup|
|FDs|Medium|EMFILE|
|DNS|Medium|Hidden stalls|
|nextTick|Very High|Total starvation|

---

## Core Insight (This matters)

> Users don’t “control libuv”.  
> They control **pressure vectors that libuv faithfully executes**.

libuv assumes:

- Fair use
- Bounded queues
- Cooperative producers
    

Production traffic violates all three.

---

## Hardening Rule of Thumb

If user input can cause:

- Work to be queued
- A handle to be created
- A timer to be scheduled
- A threadpool task to start
    

…then that input **controls libuv**.

---

## Final Takeaway

Node.js gives users _indirect write access_ to libuv’s scheduling queues.

Security at this level means:

- Bounding
- Accounting
- Rejecting early
    

Not fixing bugs.