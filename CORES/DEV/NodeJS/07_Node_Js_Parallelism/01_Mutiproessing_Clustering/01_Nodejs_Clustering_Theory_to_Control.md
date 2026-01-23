# Node.js Clustering — From Theory to Control

## Why clustering exists (the real reason)

Node.js is **single-threaded at the JavaScript level**.  
You get async I/O, but **CPU-bound work blocks the event loop**.

Modern servers:

- 8, 16, 32 cores
- Node uses **one core per process**
    

**Clustering = process-level parallelism**, not threads.

> Clustering is not about “scaling Node”  
> It’s about **isolating event loops and spreading load across CPU cores**

---

## What clustering actually is

- `cluster` module forks **multiple Node processes**
- One **primary (master)** process
- Multiple **workers**
- Workers:
    
    - Have **independent event loops**
    - Can share server ports
    - Communicate via **IPC (Inter-Process Communication)**
        

Important:  
There is **NO shared memory** (unless you explicitly use `SharedArrayBuffer`, which cluster doesn’t give you by default).

---

## Mental model you must lock in

```js
┌──────────────┐
│ Primary       │
│ (no traffic)  │
│ - forks       │
│ - monitors    │
│ - routes IPC  │
└──────┬────────┘
       │ IPC
┌──────┴────────┐
│ Worker 1       │  event loop
│ HTTP server    │
└────────────────┘
┌────────────────┐
│ Worker 2       │  event loop
│ HTTP server    │
└────────────────┘

```

If you misunderstand this, clustering becomes copy-paste magic instead of control.

---

# Example 1 — **Simple Clustering**

### Goal: Understand **process model + port sharing**

> This is the minimum to stop thinking “Node is single-core”

### What this teaches

- How workers are forked
- How the OS load-balances incoming connections
- Why workers are independent
    

### Single file: `cluster_simple.js`

```js
const cluster = require('cluster');
const http = require('http');
const os = require('os');

const CPU_COUNT = os.cpus().length;

if (cluster.isPrimary) {
  console.log(`Primary ${process.pid} running`);

  for (let i = 0; i < CPU_COUNT; i++) {
    cluster.fork();
  }

  cluster.on('exit', (worker) => {
    console.log(`Worker ${worker.process.pid} died, restarting`);
    cluster.fork();
  });

} else {
  // Worker process
  http.createServer((req, res) => {
    res.end(`Handled by worker ${process.pid}\n`);
  }).listen(3000);

  console.log(`Worker ${process.pid} started`);
}

```


### Key insights

- **All workers listen on the same port**
- OS decides which worker gets the connection
- No coordination between workers
- If one worker blocks → only that worker is affected
    

> This is why clustering increases throughput but doesn’t magically fix bad code

Refactored Code Below

```js
const cluster = require('cluster');
const http = require('http');
const os = require('os');

const CPU_COUNT = os.cpus().length;
const PORT = 3000;

/**
 * Primary (Producer / Master) logic
 */
function startPrimary() {
  console.log(`Primary ${process.pid} running`);

  // Fork workers
  for (let i = 0; i < CPU_COUNT; i++) {
    forkWorker();
  }

  // Restart workers on crash
  cluster.on('exit', (worker, code, signal) => {
    console.log(
      `Worker ${worker.process.pid} died (${signal || code}). Restarting...`
    );
    forkWorker();
  });
}

function forkWorker() {
  const worker = cluster.fork();

  // Optional: observe worker lifecycle
  worker.on('online', () => {
    console.log(`Worker ${worker.process.pid} is online`);
  });
}

/**
 * Worker logic
 */
function startWorker() {
  const server = http.createServer((req, res) => {
    res.end(`Handled by worker ${process.pid}\n`);
  });

  server.listen(PORT, () => {
    console.log(`Worker ${process.pid} listening on port ${PORT}`);
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

```sh
for i in {1..10}; do curl http://localhost:3000; done

# to test it
```
---

# Example 2 — **Complex Clustering with IPC**

### Goal: Master **worker ↔ primary communication**

> This is where clustering stops being trivial and starts being powerful.

### Scenario

- Workers handle HTTP requests
- Primary keeps **global metrics**
- Workers report stats via IPC
- Primary aggregates and logs
    

This mirrors:

- Centralized rate limits
- Global metrics
- Circuit breakers
- Distributed coordination (lightweight)
    

---

### Single file: `cluster_ipc_metrics.js`

```js
const cluster = require('cluster');
const http = require('http');
const os = require('os');

const CPU_COUNT = os.cpus().length;

if (cluster.isPrimary) {
  console.log(`Primary ${process.pid} started`);

  let totalRequests = 0;

  for (let i = 0; i < CPU_COUNT; i++) {
    const worker = cluster.fork();

    worker.on('message', (msg) => {
      if (msg.type === 'request') {
        totalRequests += 1;
      }
    });
  }

  setInterval(() => {
    console.log(`Total requests handled: ${totalRequests}`);
  }, 3000);

} else {
  let workerRequests = 0;

  http.createServer((req, res) => {
    workerRequests++;

    // Send IPC message to primary
    process.send({
      type: 'request',
      pid: process.pid
    });

    res.end(
      `Worker ${process.pid} handled ${workerRequests} requests\n`
    );
  }).listen(3000);

  console.log(`Worker ${process.pid} listening`);
}

```


---

### Critical concepts learned here

#### 1. IPC is async and serialized

- Messages are copied (not shared memory)
- Large payloads are expensive
    

#### 2. Primary becomes a coordination point

- Good for **light control**
- Dangerous for **high-frequency messaging**
    

#### 3. Workers should stay dumb

- Let workers focus on handling requests
- Let primary focus on orchestration
    

> If your primary becomes CPU-bound, you’ve built a bottleneck.

###  Refactored: `cluster_ipc_metrics.js`
```js
const cluster = require('cluster');
const http = require('http');
const os = require('os');

const CPU_COUNT = os.cpus().length;
const PORT = 3000;

/**
 * Primary (Producer / Master) logic
 */
function startPrimary() {
  console.log(`Primary ${process.pid} started`);

  let totalRequests = 0;

  // Fork workers
  for (let i = 0; i < CPU_COUNT; i++) {
    const worker = forkWorker();

    // IPC: listen to worker messages
    worker.on('message', (msg) => {
      if (msg?.type === 'request') {
        totalRequests += 1;
      }
    });
  }

  // Periodic reporting
  setInterval(() => {
    console.log(`Total requests handled: ${totalRequests}`);
  }, 3000);
}

function forkWorker() {
  const worker = cluster.fork();

  worker.on('online', () => {
    console.log(`Worker ${worker.process.pid} online`);
  });

  return worker;
}

/**
 * Worker logic
 */
function startWorker() {
  let workerRequests = 0;

  const server = http.createServer((req, res) => {
    workerRequests++;

    // IPC → primary
    process.send({
      type: 'request',
      pid: process.pid,
    });

    res.end(
      `Worker ${process.pid} handled ${workerRequests} requests\n`
    );
  });

  server.listen(PORT, () => {
    console.log(`Worker ${process.pid} listening on port ${PORT}`);
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

###  another Example : `cluster_ipc_fibonacci_progress.js`


```js
const cluster = require('cluster');

const TASKS = [
  { id: 1, n: 40 },
  { id: 2, n: 42 }
];

/**
 * Fibonacci with progress reporting
 * (iterative so we can report progress)
 */
function fibonacciWithProgress(n, onProgress) {
  let a = 0, b = 1;

  for (let i = 0; i <= n; i++) {
    if (i === 0) {
      a = 0;
    } else if (i === 1) {
      b = 1;
    } else {
      const next = a + b;
      a = b;
      b = next;
    }

    // Report progress every 5%
    const percent = Math.floor((i / n) * 100);
    if (percent % 5 === 0) {
      onProgress(percent);
    }
  }

  return n === 0 ? 0 : b;
}

/**
 * Primary (Coordinator)
 */
function startPrimary() {
  console.log(`Primary ${process.pid} started\n`);

  const results = new Map();
  const progress = new Map();
  const workers = [];

  // Spawn workers
  for (let i = 0; i < TASKS.length; i++) {
    const worker = cluster.fork();
    workers.push(worker);

    worker.on('message', (msg) => {
      switch (msg.type) {
        case 'progress':
          progress.set(msg.taskId, msg.percent);
          printProgress(progress);
          break;

        case 'result':
          results.set(msg.taskId, msg.result);
          console.log(
            `\nResult received for task ${msg.taskId} from worker ${msg.pid}`
          );

          if (results.size === TASKS.length) {
            printFinalResults(results);
            process.exit(0);
          }
          break;
      }
    });
  }

  // Assign tasks
  workers.forEach((worker, index) => {
    const task = TASKS[index];
    worker.send({
      type: 'task',
      taskId: task.id,
      n: task.n
    });
  });
}

/**
 * Worker (Compute node)
 */
function startWorker() {
  console.log(`Worker ${process.pid} started`);

  process.on('message', (msg) => {
    if (msg.type === 'task') {
      const { taskId, n } = msg;

      const result = fibonacciWithProgress(n, (percent) => {
        process.send({
          type: 'progress',
          taskId,
          percent,
          pid: process.pid
        });
      });

      process.send({
        type: 'result',
        taskId,
        result,
        pid: process.pid
      });
    }
  });
}

/**
 * Pretty printing helpers
 */
function printProgress(progressMap) {
  let output = '\nProgress:\n';
  for (const [taskId, percent] of progressMap.entries()) {
    output += `  Task ${taskId}: ${percent}%\n`;
  }
  process.stdout.write(output);
}

function printFinalResults(results) {
  console.log('\n=== FINAL RESULTS ===');
  for (const task of TASKS) {
    console.log(
      `fib(${task.n}) = ${results.get(task.id)}`
    );
  }
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
---

# Example 3 — **Most Complex: Sticky Sessions + Stateful IPC**

### Goal: Understand **real-world clustering problems**

This example simulates:

- Sticky sessions (same client → same worker)
- Session state per worker
- Primary routing connections manually
- IPC-based routing decisions
    

This is **how Socket.IO, WebSockets, and stateful APIs work under cluster**.

---

## Why sticky sessions matter

Without stickiness:

- User A → worker 1
- Next request → worker 3
- Session cache breaks
- Auth breaks
- WebSocket breaks
    

---

### How it works here

- Primary creates TCP server
- Hashes client IP
- Routes connection to specific worker
- Workers handle HTTP on internal port
    

---

### Single file: `cluster_sticky_sessions.js`

```js
const cluster = require('cluster');
const net = require('net');
const http = require('http');
const os = require('os');
const crypto = require('crypto');

const CPU_COUNT = os.cpus().length;
const workers = [];

function hashIP(ip) {
  return crypto.createHash('md5').update(ip).digest('hex');
}

if (cluster.isPrimary) {
  console.log(`Primary ${process.pid} running`);

  for (let i = 0; i < CPU_COUNT; i++) {
    const worker = cluster.fork({ WORKER_INDEX: i });
    workers.push(worker);
  }

  const server = net.createServer({ pauseOnConnect: true }, (socket) => {
    const ip = socket.remoteAddress || '';
    const hash = parseInt(hashIP(ip).slice(0, 8), 16);
    const workerIndex = hash % workers.length;
    const worker = workers[workerIndex];

    worker.send('sticky-session:connection', socket);
  });

  server.listen(3000);

} else {
  const sessions = new Map(); // stateful per worker

  const server = http.createServer((req, res) => {
    const sessionId = req.socket.remoteAddress;

    const count = (sessions.get(sessionId) || 0) + 1;
    sessions.set(sessionId, count);

    res.end(
      `Worker ${process.pid} session hits: ${count}\n`
    );
  });

  process.on('message', (msg, socket) => {
    if (msg === 'sticky-session:connection') {
      server.emit('connection', socket);
      socket.resume();
    }
  });

  server.listen(0); // internal only
}

```


---

## Why this example matters

You just learned:

### ✔ Manual connection routing

- Primary controls **which worker gets what**
    

### ✔ Sticky session hashing

- Deterministic routing
- Stateless primary logic
    

### ✔ Worker-local state

- Fast
- No shared cache
- Predictable behavior
    

### ✔ Real-world relevance

This is how you build:

- WebSocket servers
- Stateful APIs
    
- High-throughput gateways

### Refactored Code 
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

### Client 
```sh
for i in {1..5}; do
  curl --keepalive-time 60 http://localhost:3000
done

```
 This reinforces that:

- Same socket
- Same IP
- Same worker

```sh
curl --interface 127.0.0.2 http://localhost:3000
curl --interface 127.0.0.3 http://localhost:3000
curl --interface 127.0.0.4 http://localhost:3000

```
---

# Hard truths (expert advice)

### 1. Clustering does NOT fix:

- Blocking CPU code
- Memory leaks
- Poor async design
    

### 2. IPC is a tax

- Use it sparingly
- Never send hot-path data
    

### 3. Prefer this order:

1. Fix event loop blocking
2. Use async I/O properly
3. Add clustering
4. Add sticky sessions only if required
    

---

