# Async I/O vs CPU Work — Why Workers Exist

## 0. The Fundamental Constraint

> **Node’s event loop is single-threaded and non-preemptive.**

This is not an implementation detail.  
This is the **core design contract**.

Everything that follows exists because of this fact.

---

## 1. Two Very Different Kinds of “Work”

Node handles two fundamentally different workloads:

```js
A) Waiting work  → I/O
B) Thinking work → CPU

```

They behave nothing alike.

---

## 2. Async I/O: Waiting Without Blocking

### 2.1 What Async I/O Really Means

Async I/O does **not** mean “runs in parallel”.

It means:

> **The kernel waits so JavaScript doesn’t have to.**

Example:

```js
fs.readFile("data.txt", cb);

```

What happens:

1. JS requests work
2. libuv asks OS / thread pool
3. JS returns immediately
4. Event loop keeps running
5. Callback queued later
    

At no point is the event loop blocked.

---

### 2.2 Why I/O Scales

I/O is mostly:

- Waiting on disk
- Waiting on network
- Waiting on kernel buffers
    

Waiting costs **zero CPU**.

This is why Node can handle:

- 100k sockets
- 10k idle HTTP connections
- Massive concurrency
    

Because **waiting is cheap**.

---

## 3. CPU Work: Thinking Blocks Everything

### 3.1 What CPU Work Is

CPU work is anything that:

- Runs JavaScript loops
- Performs calculations
- Parses large JSON
- Compresses, hashes, encrypts
- Blocks longer than ~5–10ms
    

Example:

```js
function hash(data) {
  while (heavyMath()) {}
}

```

This work:

- Does not yield
- Cannot be interrupted
- Freezes the event loop
    

---

### 3.2 What Blocking Really Means

When CPU work runs:

- Timers stop
- Poll stops
- I/O callbacks wait
- HTTP stalls
- Latency spikes globally
    

One slow request can block **every request**.

This is the single biggest Node production failure mode.

---

## 4. The Lie: “But It’s Async Code”

```js
app.get("/", async (req, res) => {
  await heavyCalculation();
  res.end("ok");
});

```

This looks safe. It is not.

Why:

- `heavyCalculation()` runs **before** the await yields
- JavaScript executes synchronously until first await
- CPU work blocks immediately
    

**Async syntax does not imply async execution.**

---

## 5. Why the Event Loop Cannot Save You

Node does **not** have:

- Preemption
- Time slicing
- Forced yielding
- Priorities
- Fair scheduling
    

The event loop **cannot interrupt you**.

If your code runs:

> It runs until it finishes or you yield voluntarily.

---

## 6. The Only Escape: Parallelism

To fix CPU blocking, Node must:

- Run work elsewhere
- Let the event loop continue
- Receive a result later
    

That requires **other threads**.

This is why workers exist.

---

## 7. Three Kinds of “Workers” in Node

### 7.1 libuv Thread Pool (Implicit Workers)

Used for:

- fs
- crypto
- zlib
- dns.lookup
    

These run on:

- A small shared pool (default: 4 threads)
- Invisible to JS
- Return results via poll
    

⚠️ Overuse can saturate the pool.

---

### 7.2 Worker Threads (Explicit Workers)

```js
new Worker("./worker.js");

```

Properties:

- Separate JS thread
- Separate event loop
- Separate call stack
- Shared memory optional
    

This is **real parallelism**.

---

### 7.3 Child Processes (Isolation Workers)

```js
fork("child.js");

```

Properties:

- Separate process
- Separate heap
- IPC communication
- Higher overhead
- Strong isolation
    

Used when:

- Crashes must not propagate
- Memory isolation matters
    

---

## 8. Why Workers Are Not “Just Faster”

Workers exist to protect:

- Latency
- Fairness
- I/O responsiveness
    

They are **correctness tools**, not optimizations.

---

## 9. The Cost Model (Critical to Understand)

|Approach|Cost|Benefit|
|---|---|---|
|Main thread|Zero overhead|Blocks everything|
|Thread pool|Cheap|Limited, shared|
|Worker threads|Moderate|True parallelism|
|Child process|Expensive|Isolation|

Workers are not free.  
But blocking is **far more expensive**.

---

## 10. When You Must Use Workers (No Exceptions)

Use workers when:

- CPU work > 10ms
- Work scales with input size
- Loop over large data
- User input controls workload
- You care about tail latency
    

If you ignore this, your system **will fail under load**.

---

## 11. When You Should NOT Use Workers

Do **not** use workers for:

- Simple glue code
- Small transformations
- I/O orchestration
- Business logic
- Request routing
    

Workers are scalpels, not hammers.

---

## 12. The One Diagram That Explains Everything

```js
Event Loop Thread:
------------------
I/O scheduling
Callbacks
Promises
Timers
HTTP routing

Worker Thread:
--------------
CPU work
Parsing
Hashing
Compression
Image processing

```

**Never mix these responsibilities.**

---

## 13. The Core Design Law

> **I/O waits should stay on the event loop.  
> CPU thinking must leave it.**

Break this rule and Node becomes slow, unfair, and fragile.

---

## 14. Final Lock-In Sentence

> **Node scales because it waits efficiently — and survives because it thinks elsewhere.**