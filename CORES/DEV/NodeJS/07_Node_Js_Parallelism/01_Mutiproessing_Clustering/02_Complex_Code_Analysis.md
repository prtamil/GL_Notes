
# Code 
```js
const cluster = require('cluster');
const net = require('net');
const http = require('http');
const os = require('os');
const crypto = require('crypto');

const CPU_COUNT = os.cpus().length;
const PORT = 3000;

/**
 * Utilities
 */
function hashIP(ip) {
  return crypto
    .createHash('md5')
    .update(ip)
    .digest('hex');
}

function getWorkerIndex(ip, workerCount) {
  const hash = parseInt(hashIP(ip).slice(0, 8), 16);
  return hash % workerCount;
}

/**
 * Primary (Load balancer / Coordinator)
 */
function startPrimary() {
  console.log(`Primary ${process.pid} running`);

  const workers = spawnWorkers();

  const server = net.createServer(
    { pauseOnConnect: true },
    (socket) => routeConnection(socket, workers)
  );

  server.listen(PORT, () => {
    console.log(`Sticky-session load balancer listening on ${PORT}`);
  });
}

function spawnWorkers() {
  const workers = [];

  for (let i = 0; i < CPU_COUNT; i++) {
    const worker = cluster.fork({ WORKER_INDEX: i });
    workers.push(worker);

    worker.on('online', () => {
      console.log(`Worker ${worker.process.pid} online`);
    });
  }

  return workers;
}

function routeConnection(socket, workers) {
  const ip = socket.remoteAddress || '';
  const index = getWorkerIndex(ip, workers.length);
  const worker = workers[index];

  // Sticky routing
  worker.send('sticky-session:connection', socket);
}

/**
 * Worker (Stateful HTTP server)
 */
function startWorker() {
  console.log(
    `Worker ${process.pid} started (index ${process.env.WORKER_INDEX})`
  );

  const sessions = new Map();

  const server = http.createServer((req, res) => {
    const sessionId = req.socket.remoteAddress;
    const count = (sessions.get(sessionId) || 0) + 1;

    sessions.set(sessionId, count);

    res.end(
      `Worker ${process.pid} session hits: ${count}\n`
    );
  });

  setupStickyConnectionHandling(server);

  // Internal-only listener
  server.listen(0);
}

function setupStickyConnectionHandling(server) {
  process.on('message', (msg, socket) => {
    if (msg === 'sticky-session:connection') {
      server.emit('connection', socket);
      socket.resume();
    }
  });
}

/**
 * Entry point
 */
function main() {
  if (cluster.isPrimary) {
    startPrimary();
  } else {
    startWorker();
  }
}

main();
```

# Deep Explanation
I’ll structure this as:

1. **Big picture (what problem this solves)**
2. **Module imports & constants**
3. **Utility functions (hashing & routing)**
4. **Primary process — deep dive**
5. **Worker process — deep dive**
6. **IPC socket handoff (critical section)**
7. **Mental model recap**
8. **Why this is done this way (and tradeoffs)**
    

Take your time — this is foundational infra knowledge.

---

# 1️⃣ Big Picture — What problem does this code solve?

### The real problem

HTTP is **stateful at the application layer**, but Node cluster workers are **separate processes**.

If:

- Request 1 → Worker A
- Request 2 → Worker B
    

Then **in-memory session state breaks**.

### Solution: Sticky Sessions

Ensure:

> The same client **always** reaches the **same worker**

This code implements a **TCP-level sticky session load balancer** using:

- `cluster` → multi-process
- `net` → raw TCP control
- IPC → socket transfer
    

This is **how PM2 sticky mode works internally**.

---

# 2️⃣ Imports & Constants (Context matters)

```js
const cluster = require('cluster');

```

👉 Enables **multiple Node processes** under one master.

Important:

- Each worker = separate memory + event loop
- No shared state unless via IPC
    

---

```js
const net = require('net');

```

👉 Raw TCP server (lower than HTTP).

Why?

- We must **accept TCP first**
- Decide _which worker_ should handle it
- Then forward the socket
    

HTTP alone can’t do this.

---

```js
const http = require('http');

```

👉 Used **inside workers** only.

Workers handle HTTP, not TCP routing.

---

```js
const os = require('os');


```

👉 Used to detect CPU cores.

---

```js
const crypto = require('crypto');

```

👉 Used for **consistent hashing** of client identity.

We hash IP → deterministic worker selection.

---

```js
const CPU_COUNT = os.cpus().length;
const PORT = 3000;

```

Intent:

- One worker per CPU core (classic Node model)
- Single public port exposed by **primary only**
    

Workers never expose public ports.

---

# 3️⃣ Utility Functions — Sticky Routing Logic

## `hashIP`

```js
function hashIP(ip) {
  return crypto
    .createHash('md5')
    .update(ip)
    .digest('hex');
}

```

### Why hash the IP?

- IP addresses are strings (`"192.168.1.10"`)
- We need a **uniform numeric distribution**
- Hashing avoids hot-spotting
    

MD5 is fine here because:

- Not for security
- Only for deterministic distribution
    

---

## `getWorkerIndex`

```js
function getWorkerIndex(ip, workerCount) {
  const hash = parseInt(hashIP(ip).slice(0, 8), 16);
  return hash % workerCount;
}

```

Let’s break this carefully:

1. `hashIP(ip)` → hex string
2. `.slice(0, 8)` → take first 32 bits
3. `parseInt(..., 16)` → convert hex → number
4. `% workerCount` → map to worker index
    

### Result:

Same IP → **always same worker**
That’s _session affinity_.

---

# 4️⃣ Primary Process — Line by Line

## Entry decision

```js
function main() {
  if (cluster.isPrimary) {
    startPrimary();
  } else {
    startWorker();
  }
}

```

### Why this matters

- Same file runs as **primary OR worker**
- `cluster.fork()` re-executes this file
    

This is the standard cluster pattern.

---

## `startPrimary`

```js
function startPrimary() {
  console.log(`Primary ${process.pid} running`);

```

Primary responsibilities:

- Spawn workers
- Accept TCP connections
- Route sockets
- Never handle HTTP
    

---

### Spawning workers

```js
const workers = spawnWorkers();

```

Primary holds references to workers so it can:

- Send sockets
- Monitor lifecycle
    

---

### TCP server creation

```js
const server = net.createServer(
  { pauseOnConnect: true },
  (socket) => routeConnection(socket, workers)
);

```

This line is **extremely important**.

#### `pauseOnConnect: true`

- TCP socket starts **paused**
- No data is read yet
- Prevents losing data during transfer
    

Without this → race condition → broken requests.

---

### Listening

```js
server.listen(PORT, () => {
  console.log(`Sticky-session load balancer listening on ${PORT}`);
});

```

Only **primary** listens on public port.

Workers listen on **random internal ports**.

---

## Worker spawning

```js
function spawnWorkers() {
  const workers = [];

```

Workers stored in an array for hashing.

---

```js
for (let i = 0; i < CPU_COUNT; i++) {
  const worker = cluster.fork({ WORKER_INDEX: i });

```

- One worker per CPU
- `WORKER_INDEX` is optional metadata
- Useful for logging/debugging
    

---

```js
workers.push(worker);

```

Workers are indexed — this matters for hashing.

---

```js
worker.on('online', () => {
  console.log(`Worker ${worker.process.pid} online`);
});

```

Lifecycle visibility.  
In production, you’d also handle:

- exit
- restart
- draining
    

---

## Routing connections (core logic)

```js
function routeConnection(socket, workers) {

```

This function **decides ownership** of the client.

---

```js
const ip = socket.remoteAddress || '';

```

- Client identity
- Weak but common (better: cookie/session id)
    

---

```js
const index = getWorkerIndex(ip, workers.length);

```

Deterministic mapping.

---

```js
const worker = workers[index];

```

Select target worker.

---

```js
worker.send('sticky-session:connection', socket);

```

🔥 **Critical moment**

- Socket is transferred via IPC
- Ownership moves from primary → worker
- Primary never touches it again
    

---

# 5️⃣ Worker Process — Line by Line

## Worker start

```js
function startWorker() {
  console.log(
    `Worker ${process.pid} started (index ${process.env.WORKER_INDEX})`
  );

```

Workers:

- Handle HTTP
- Hold session state
- Never route
    

---

## Session store

```js
const sessions = new Map();

```

This is:

- **In-memory**
- **Per-worker**
- **Stateful**
    

Sticky sessions exist **only because this exists**.

---

## HTTP server

```js
const server = http.createServer((req, res) => {

```

This is standard Node HTTP.

---

```js
const sessionId = req.socket.remoteAddress;

```

Using IP as session key (simplified).

---

```js
const count = (sessions.get(sessionId) || 0) + 1;
sessions.set(sessionId, count);

```

State mutation:

- Each worker maintains its own counter
- Different worker → different memory
    

---

```js
res.end(
  `Worker ${process.pid} session hits: ${count}\n`
);

```

Proof that stickiness works:

- Refresh → count increases
- Hit different worker → count resets
    

---

## Sticky socket handoff

```js
setupStickyConnectionHandling(server);

```

Separates concerns:

- HTTP logic vs IPC wiring
    

---

```js
server.listen(0);

```

Important:

- `0` → random internal port
- Not publicly accessible
- Only receives sockets from primary
    

---

## IPC socket receiving

```js
function setupStickyConnectionHandling(server) {
  process.on('message', (msg, socket) => {

```

Workers listen for IPC messages.

---

```js
if (msg === 'sticky-session:connection') {

```

Protocol message.  
In real systems, this is a full message object.

---

```js
server.emit('connection', socket);


```

🔥 **Key trick**

- Manually inject socket into HTTP server
- HTTP server thinks it accepted it itself
    

This is undocumented magic — but widely used.

---

```js
socket.resume();

```

Resume reading data.  
Remember: socket was paused in primary.

---

# 6️⃣ Critical Insight — Why TCP + IPC?

Why not just use HTTP and round-robin?

Because:

- HTTP load balancers can’t preserve **in-memory state**
- Workers don’t share memory
- Sticky routing must happen **before HTTP parsing**
    

That’s why:

- TCP first
- Routing second
- HTTP last
    

---

# 7️⃣ Mental Model (Burn this in)

```js
Client
  ↓
Primary (TCP router)
  ↓ (socket transfer)
Worker (HTTP + session memory)

```

Workers:

- Are isolated
- Can crash independently
- Own state
    

Primary:

- Never blocks
- Never handles HTTP
- Only routes
    

---

# 8️⃣ Tradeoffs & Reality Check

### Pros

✅ Simple  
✅ Fast  
✅ No external store  
✅ Great for demos / small systems

### Cons

❌ Worker crash = session loss  
❌ No horizontal scaling across machines  
❌ IP-based stickiness is weak  
❌ Kubernetes hates this

That’s why **Redis-backed sessions** exist.