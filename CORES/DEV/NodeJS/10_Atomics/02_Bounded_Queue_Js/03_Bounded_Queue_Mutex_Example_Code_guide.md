### **Atomic Queue with Worker Threads in Node.js — A Deep Dive**

This code demonstrates a **multi-producer, multi-consumer concurrent queue** implemented in **Node.js** using the `worker_threads` module and **shared memory with atomics**. The design showcases **thread-safe synchronization**, **blocking coordination**, and **lock-based mutual exclusion** in a JavaScript environment, which is traditionally single-threaded.

---

#### **1. Context and Motivation**

Node.js is inherently single-threaded at the JavaScript level, but the introduction of `worker_threads` allows true **parallel execution** on multiple CPU cores. Sharing data between threads is challenging because **concurrent access** can lead to **race conditions**.

In this scenario, we want multiple producer threads to insert items into a shared queue, and multiple consumer threads to remove items concurrently, **without corrupting the queue**. The solution leverages:

- **SharedArrayBuffer** — a memory region accessible to all threads.
    
- **Atomics API** — atomic operations like `compareExchange`, `wait`, `notify`, ensuring safe updates.
    
- **Mutex abstraction** — explicit lock management to prevent concurrent modifications.
    

This is a classic **producer-consumer problem**, widely studied in operating systems and concurrent programming courses.

---

#### **2. The Mutex Class**

The `Mutex` class encapsulates a **binary lock** using an atomic integer at a fixed index of the shared array.

```js
class Mutex {
  constructor(sharedArray, index = 0) {
    this.lockArray = sharedArray;
    this.index = index;
  }

  lock() {
    while (true) {
      if (Atomics.compareExchange(this.lockArray, this.index, 0, 1) === 0)
        return; // acquired lock
      Atomics.wait(this.lockArray, this.index, 1); // sleep until released
    }
  }

  unlock() {
    Atomics.store(this.lockArray, this.index, 0); // release lock
    Atomics.notify(this.lockArray, this.index, 1); // wake one waiter
  }
}

```

**Key Points:**

- `compareExchange` ensures **atomic acquisition** of the lock.
    
- `Atomics.wait` blocks the thread **without busy-waiting**, making this CPU-efficient.
    
- `unlock` both clears the lock and wakes one waiting thread using `Atomics.notify`.
    
- Abstraction hides low-level atomic operations from the queue logic.
    

This class is crucial to ensure that **only one thread can manipulate queue indices or counts at a time**, preventing **race conditions**.

---

#### **3. The AtomicQueue Class**

`AtomicQueue` encapsulates a **ring buffer** with a fixed size, supporting `enqueue` and `dequeue` operations safely across threads. Its shared memory layout:

|Index|Purpose|
|---|---|
|0|Mutex lock|
|1|Head pointer|
|2|Tail pointer|
|3|Count|
|4+|Ring buffer|

**Enqueue (Producer) Logic:**

1. Acquire the mutex.
    
2. If the queue is full (`count === queueSize`), release the mutex and wait (`Atomics.wait`).
    
3. Insert the item at the tail index.
    
4. Increment the tail (circularly) and count.
    
5. Release the mutex and notify waiting consumers.
    

```js
enqueue(item) {
  this.mutex.lock();
  while (this.shared[this.COUNT] === this.queueSize) {
    this.mutex.unlock();
    Atomics.wait(this.shared, this.COUNT, this.queueSize);
    this.mutex.lock();
  }

  const pos = this.shared[this.TAIL];
  this.shared[this.BUFFER + pos] = item;
  this.shared[this.TAIL] = (pos + 1) % this.queueSize;
  this.shared[this.COUNT]++;

  this.mutex.unlock();
  Atomics.notify(this.shared, this.COUNT, 1);
}

```

**Dequeue (Consumer) Logic:**

1. Acquire the mutex.
    
2. If the queue is empty (`count === 0`), release the mutex and wait.
    
3. Read the item at the head index.
    
4. Increment the head (circularly) and decrement count.
    
5. Release the mutex and notify waiting producers.
    

```js
dequeue() {
  this.mutex.lock();
  while (this.shared[this.COUNT] === 0) {
    this.mutex.unlock();
    Atomics.wait(this.shared, this.COUNT, 0);
    this.mutex.lock();
  }

  const pos = this.shared[this.HEAD];
  const item = this.shared[this.BUFFER + pos];
  this.shared[this.HEAD] = (pos + 1) % this.queueSize;
  this.shared[this.COUNT]--;

  this.mutex.unlock();
  Atomics.notify(this.shared, this.COUNT, 1);

  return item;
}

```

**Intention & Design Considerations:**

- Uses **blocking waits** to avoid CPU spinning when the queue is full or empty.
    
- Circular buffer ensures **constant-time enqueue/dequeue** operations.
    
- The mutex guarantees **mutual exclusion** while manipulating shared indices and count.
    
- `Atomics.notify` wakes up a waiting producer or consumer whenever the queue state changes.
    

---

#### **4. Main Thread Logic**

The main thread initializes the shared memory buffer and spawns multiple workers:

```js
const PRODUCERS = 2;
const CONSUMERS = 2;
const ITEMS_PER_PRODUCER = 20;

const sab = new SharedArrayBuffer(Int32Array.BYTES_PER_ELEMENT * (4 + QUEUE_SIZE));

```

- `PRODUCERS` produce items, `CONSUMERS` consume them.
    
- Each producer adds `ITEMS_PER_PRODUCER` items.
    
- Shared memory layout matches `AtomicQueue` structure.
    
- Workers are started with `workerData` specifying their role and ID.
    

This setup **simulates a real-world concurrent system**, where multiple tasks produce and consume data in parallel.

---

#### **5. Worker Thread Logic**

Each worker interprets its role:

- **Producers:** loop `count` times, generate unique items (`id * 100 + i`), and enqueue them.
    
- **Consumers:** run indefinitely, dequeuing items and logging them.
    

```js
if (role === "producer") {
  for (let i = 0; i < count; i++) {
    const value = id * 100 + i;
    queue.enqueue(value);
    console.log(`Producer ${id} added`, value);
  }
}

if (role === "consumer") {
  while (true) {
    const value = queue.dequeue();
    console.log(`Consumer ${id} got`, value);
  }
}

```

**Key Insights:**

- `AtomicQueue` abstracts away low-level locking and buffer logic, letting the worker logic read like **“enqueue this item”** or **“consume this item”**.
    
- Consumers loop infinitely — in real applications, a termination condition or sentinel value is usually added.
    
- Using `worker_threads` allows producers and consumers to run **truly in parallel** on separate cores.
    

---

#### **6. Overall Intention**

This code is an educational and practical demonstration of:

1. **Shared memory concurrency** in Node.js.
    
2. **Mutex-based synchronization** using Atomics.
    
3. **Blocking producer-consumer patterns** without busy-waiting.
    
4. **Clean abstraction** for queue operations.
    

It can be extended to:

- Support **multiple queues**.
    
- Implement **graceful shutdowns**.
    
- Use **timeouts** for blocking waits.
    
- Measure performance for high-concurrency environments.
    

---

#### **7. Why This Matters**

In high-performance applications, such as:

- Real-time data pipelines
    
- Event processing systems
    
- Multi-threaded caching
    

…you often need **atomic shared structures**. This code provides a **foundation** to understand:

- How to coordinate multiple threads safely.
    
- How to leverage atomics to implement **classic OS data structures** in JavaScript.
    
- How to design abstractions (`Mutex`, `AtomicQueue`) that separate **concurrency control** from **business logic**.
    

---

**Conclusion:**

This implementation elegantly demonstrates **multi-producer, multi-consumer synchronization in Node.js** using `worker_threads` and **atomic shared memory**. It balances **safety, performance, and readability**. The abstractions (`Mutex`, `AtomicQueue`) make complex concurrency concepts approachable and reusable, showing how low-level operating system concepts translate directly to JavaScript.