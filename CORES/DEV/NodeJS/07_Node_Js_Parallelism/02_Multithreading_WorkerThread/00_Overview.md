# 0. Core Concepts (read this first)

### Node.js concurrency model (baseline)

- **Event loop** = single-threaded
- Great for **I/O**
- Terrible for **CPU-heavy work** (blocks the loop)

### What Worker Threads give you

- True OS threads
- Each worker has:
    
    - Its **own event loop**
    - Its **own JS heap**
        
- Communication via:
    
    - `postMessage` (structured clone)
    - `SharedArrayBuffer` (advanced, optional)
        

### When to use workers

✅ CPU-heavy tasks (crypto, image processing, parsing, math)  
❌ I/O-bound tasks (use async instead)

---

# 1. Minimal Worker Thread Mental Model

```js
Main Thread
 ├─ HTTP server
 ├─ Event loop
 ├─ Spawns workers
 └─ Coordinates results

Worker Thread
 ├─ Separate JS engine
 ├─ Separate event loop
 ├─ CPU-heavy logic
 └─ Sends result back

```

Think **“threads as CPU offload engines”**, not request handlers.

---

# 2. Example 1 — Simple Ping-Pong (Main ↔ Worker)

This teaches **message passing**, nothing else.

### `pingWorker.js`

```js
const { parentPort } = require("worker_threads");

parentPort.on("message", (msg) => {
  if (msg === "ping") {
    parentPort.postMessage("pong");
  }
});

```

### `main.js`

```js
const { Worker } = require("worker_threads");

const worker = new Worker("./pingWorker.js");

worker.on("message", (msg) => {
  console.log("From worker:", msg);
});

worker.postMessage("ping");

```

### What’s happening

A **worker thread** in Node.js is a real OS thread running its own full Node runtime: its own V8 isolate, heap, garbage collector, and event loop. When you create a worker, Node spins up this thread, loads the worker script, and starts its event loop immediately. Inside the worker, `parentPort` represents a **message port** that is wired to the worker’s event loop. When there is no work, the worker is not executing JavaScript—it is **blocked at the OS level** (epoll/kqueue/IOCP), consuming virtually no CPU, just like the main event loop when idle.

In the ping–pong example, `postMessage("ping")` from the main thread **does not block**. Node serializes the message and **pushes it into a thread-safe message queue** implemented in native code. This queue is protected with locks/atomics so multiple threads can safely write to it, and it is integrated with libuv so that adding a message **signals** the target thread’s event loop. When the worker wakes, the queue entry is converted into a `"message"` event, the handler runs, and `"pong"` is enqueued back to the main thread the same way. Both threads stay independent, sleeping when idle and waking only on messages—this message-queue-driven design is what makes worker threads efficient, non-blocking, and safe.
    

### Why this matters

This is the **foundation of all worker usage**.

---

# 3. Example 2 — Fibonacci in Worker (CPU-bound task)

This is the **canonical example** for workers.

### `fibWorker.js`

```js
const { parentPort, workerData } = require("worker_threads");

function fib(n) {
  if (n <= 1) return n;
  return fib(n - 1) + fib(n - 2);
}

const result = fib(workerData);

parentPort.postMessage(result);

```

### `main.js`

```js
const { Worker } = require("worker_threads");

function runFib(n) {
  return new Promise((resolve, reject) => {
    const worker = new Worker("./fibWorker.js", {
      workerData: n
    });

    worker.on("message", resolve);
    worker.on("error", reject);
    worker.on("exit", (code) => {
      if (code !== 0) reject(new Error(`Exit code ${code}`));
    });
  });
}

(async () => {
  console.log("Starting Fibonacci...");
  const result = await runFib(40);
  console.log("Fib result:", result);
})();

```

### Why this is important

- Fibonacci is **CPU-heavy**
    
- Without workers → Node freezes
    
- With workers → event loop stays responsive
    

### Key ideas

- `workerData` = input
    
- `postMessage` = output
    
- Promise wrapper = clean API
    

This pattern scales. 
In this example, the **main thread** creates a worker specifically to offload a CPU-heavy Fibonacci calculation. When `new Worker("./fibWorker.js", { workerData: n })` is called, Node starts a new OS thread with its own V8 isolate and event loop, then passes `workerData` (`n`) to the worker at startup. The worker immediately executes `fibWorker.js`, computes the recursive Fibonacci value entirely on its own thread and heap, and never blocks the main event loop. This is important because the recursive Fibonacci function is synchronous and CPU-intensive—running it on the main thread would freeze the process.

After the computation finishes, `parentPort.postMessage(result)` serializes the result and **pushes it into a thread-safe message queue** targeting the main thread. libuv signals the main event loop, which schedules the `"message"` handler and resolves the Promise in `runFib`. The main thread was never waiting in a blocking sense; it simply awaited a Promise while continuing to process other events. Once the message arrives, the Promise resolves, the result is printed, and the worker exits. This pattern cleanly separates **coordination (main thread)** from **computation (worker)** and is the canonical way to use worker threads for CPU-bound tasks in Node.js.

---

# 4. Example 3 — Web Server Using Worker Threads

Now we combine **HTTP + workers** (real-world pattern).

### Design goal

- HTTP server stays fast
    
- Heavy computation runs in workers
    

---

### `computeWorker.js`

```js
const { parentPort, workerData } = require("worker_threads");

function heavyCompute(n) {
  let sum = 0;
  for (let i = 0; i < n; i++) {
    sum += Math.sqrt(i);
  }
  return sum;
}

const result = heavyCompute(workerData);
parentPort.postMessage(result);

```

---

### `server.js`

```js
const http = require("http");
const { Worker } = require("worker_threads");

function runWorker(data) {
  return new Promise((resolve, reject) => {
    const worker = new Worker("./computeWorker.js", {
      workerData: data
    });

    worker.on("message", resolve);
    worker.on("error", reject);
    worker.on("exit", (code) => {
      if (code !== 0)
        reject(new Error(`Worker stopped with ${code}`));
    });
  });
}

const server = http.createServer(async (req, res) => {
  if (req.url === "/compute") {
    const result = await runWorker(50_000_000);
    res.end(`Result: ${result}`);
  } else {
    res.end("OK");
  }
});

server.listen(3000, () => {
  console.log("Server running on port 3000");
});

```

### What you just built

- Main thread:
    
    - Accepts HTTP requests

    - Delegates CPU work
        
- Worker:
    
    - Does expensive computation
        
    - Sends result back