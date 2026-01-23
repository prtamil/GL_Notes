# Node.js Parallelism Overview

**Cluster (Multiprocessing), Worker Threads (Multithreading), and IPC**

## 1. Why Node Needs These Primitives

Node’s main strengths:

- Single-threaded event loop
- Massive I/O concurrency
    

Node’s main weakness:

- **CPU-bound work blocks the event loop**
    

To scale across CPU cores and handle heavy computation, Node provides:

- **Cluster** → multiprocessing
- **Worker Threads** → multithreading
- **IPC** → coordination between them
    

---

## 2. Cluster: Multiprocessing Model

### What Cluster Is

- Built on top of `child_process.fork()`
- Spawns **multiple Node processes**
- Each process has:
    
    - Its own V8 instance
    - Its own event loop
    - Its own memory heap
        

This is **true OS-level parallelism**.

---

### How Cluster Works (Conceptually)

```js
Primary Process
   ├── Worker Process #1 (event loop)
   ├── Worker Process #2 (event loop)
   ├── Worker Process #3 (event loop)

```

- Primary process manages workers
- OS distributes incoming connections
- Each worker handles requests independently
    

---

### When to Use Cluster

Best for:

- HTTP servers
- API gateways
- WebSocket servers
- Stateless request handling
    

Not ideal for:

- Heavy shared-memory computation
- Fine-grained task coordination
    

---

### Key Characteristics

✅ Parallel across CPU cores  
✅ Fault isolation (one worker crash ≠ total crash)  
❌ No shared memory by default  
❌ IPC involves serialization

---

## 3. Worker Threads: Multithreading Model

### What Worker Threads Are

- Introduced for **CPU-bound JavaScript**
- Run inside the **same process**
- Each worker has:
    
    - Its own JS thread
    - Its own event loop
        

Unlike cluster:

- Memory **can be shared**
    

---

### Conceptual Model

```js
Single Node Process
   ├── Main Thread (event loop)
   ├── Worker Thread #1
   ├── Worker Thread #2

```

Workers are closer to **Java-style threads** than processes.

---

### When to Use Worker Threads

Best for:

- CPU-intensive tasks
- Image processing
- Encryption
- Parsing large data
- Scientific or numeric work
    

Not ideal for:

- Handling HTTP traffic directly
- Isolation from crashes
    

---

### Key Characteristics

✅ Low overhead vs processes  
✅ Shared memory possible  
✅ Fast communication  
❌ Crashes can affect the process  
❌ Requires synchronization (Atomics)

---

## 4. IPC: Inter-Process / Inter-Thread Communication

IPC is how Node components **coordinate work**.

Node supports **different IPC mechanisms**, depending on whether you use processes or threads.

---

## 5. IPC Between Processes (Cluster / child_process)

### Message Passing (Default)

```js
process.send()  ⇄  process.on("message")

```

- Structured clone
- Data is copied (serialized)
- Simple and safe
    

Use cases:

- Task dispatch
- Metrics
- Control signals
    

---

### OS-Level IPC (Advanced)

- Sockets
- Pipes
- UNIX domain sockets
- TCP
    

Used when:

- High throughput
- Language-agnostic IPC
- External services
    

---

### Characteristics

✅ Strong isolation  
❌ Serialization overhead  
❌ No shared memory

---

## 6. IPC Between Worker Threads

### Message Passing

```js
worker.postMessage() ⇄ parentPort.on("message")

```

- Structured clone
- Faster than process IPC
- Still copies memory by default
    

---

### Transferable Objects (Zero-Copy)

- `ArrayBuffer`
- `MessagePort`
    

Ownership transferred, not copied.

---

### Shared Memory (Advanced)

`SharedArrayBuffer + Atomics`

- True shared memory
- Lock-free or synchronized access
- Extremely fast
    

Used for:

- High-performance computing
- Streaming parsers
- Ring buffers
    

---

## 7. IPC Comparison Table

|Feature|Cluster (Process)|Worker Threads|
|---|---|---|
|Isolation|High|Low|
|Memory sharing|❌|✅|
|IPC cost|High|Low|
|Crash impact|Isolated|Whole process|
|Startup cost|High|Low|
|Best for|Servers|Computation|

---

## 8. How They Fit Together in Real Systems

A common real-world architecture:

- **Cluster** for handling traffic
- **Workers** inside each process for CPU-heavy tasks
- **IPC** to coordinate and offload work
    

```js
[Load Balancer]
      ↓
[Cluster Worker Process]
      ↓
[Worker Thread Pool]

```

This gives:

- Horizontal scalability
- CPU parallelism
- Controlled complexity
    

---

## 9. Mental Model Summary

- **Cluster** → “Many Node apps”
- **Workers** → “Many JS threads”
- **IPC** → “How they talk”
    

Or simply:

> Processes scale **traffic**, threads scale **computation**.