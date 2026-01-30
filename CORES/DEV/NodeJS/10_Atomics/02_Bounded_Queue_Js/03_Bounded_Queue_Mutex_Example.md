f your goal is **“learn _all_ important Atomics concepts in JS in one example”**, then the best possible example is **a bounded producer–consumer queue**.

Why I’m confident saying this:

- It uses **every atomic primitive**
    
- It forces correct **memory ordering**
    
- It shows **wait / notify**
    
- It demonstrates **backpressure**
    
- It exposes **race conditions immediately** if wrong
    
- This is exactly how real runtimes coordinate work
    

A mutex alone is not enough.  
A counter alone is too simple.  
A queue forces everything to work together.

---

# The Best Atomics-in-JS Example: Bounded Work Queue

## Concepts you will learn in ONE program

This single program teaches:

|Concept|Used?|
|---|---|
|SharedArrayBuffer|✅|
|Atomic load / store|✅|
|Atomic add|✅|
|CAS|✅|
|wait / notify|✅|
|Memory visibility|✅|
|Backpressure|✅|
|No busy waiting|✅|
|Correctness under contention|✅|

This is **the canonical example**.

---

## Mental model before code (important)

We will build:

- A **fixed-size ring buffer**
    
- Multiple producers
    
- Multiple consumers
    
- Blocking when full / empty
    

Shared state:

```js
[ mutex | head | tail | count | buffer... ]

```

---

## Single-file, runnable example

Save as:

```js
node atomic_queue.js

```

---

## 📄 `atomic_queue.js`

```js
const { Worker, isMainThread, workerData } = require("worker_threads");

/* =========================
   CONSTANTS
   ========================= */
const QUEUE_SIZE = 8;

/* =========================
   MUTEX CLASS
   ========================= */
class Mutex {
  constructor(sharedArray, index = 0) {
    this.lockArray = sharedArray;
    this.index = index;
  }

  lock() {
    while (true) {
      if (Atomics.compareExchange(this.lockArray, this.index, 0, 1) === 0)
        return;
      Atomics.wait(this.lockArray, this.index, 1);
    }
  }

  unlock() {
    Atomics.store(this.lockArray, this.index, 0);
    Atomics.notify(this.lockArray, this.index, 1);
  }
}

/* =========================
   ATOMIC QUEUE CLASS
   ========================= */
class AtomicQueue {
  constructor(sharedArray, queueSize = QUEUE_SIZE) {
    this.shared = sharedArray;
    this.queueSize = queueSize;

    this.LOCK = 0;
    this.HEAD = 1;
    this.TAIL = 2;
    this.COUNT = 3;
    this.BUFFER = 4;

    this.mutex = new Mutex(this.shared, this.LOCK);
  }

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
}

/* =========================
   MAIN THREAD
   ========================= */
if (isMainThread) {
  const PRODUCERS = 2;
  const CONSUMERS = 2;
  const ITEMS_PER_PRODUCER = 20;

  const sab = new SharedArrayBuffer(
    Int32Array.BYTES_PER_ELEMENT * (4 + QUEUE_SIZE)
  );

  console.log("Starting atomic queue demo...");

  for (let i = 0; i < PRODUCERS; i++) {
    new Worker(__filename, {
      workerData: { sab, role: "producer", id: i, count: ITEMS_PER_PRODUCER },
    });
  }

  for (let i = 0; i < CONSUMERS; i++) {
    new Worker(__filename, {
      workerData: { sab, role: "consumer", id: i },
    });
  }

/* =========================
   WORKER THREAD
   ========================= */
} else {
  const { sab, role, id, count } = workerData;
  const queue = new AtomicQueue(new Int32Array(sab), QUEUE_SIZE);

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
}


```

---

## Why this example is perfect for learning

### 1️⃣ If you remove Atomics → it breaks

You’ll see:

- Lost items
    
- Duplicates
    
- Deadlocks
    
- Random behavior
    

### 2️⃣ If you misuse ordering → it breaks

Move writes around → consumers see garbage.

### 3️⃣ It scales naturally

- Add producers
    
- Add consumers
    
- Increase contention
    
- Everything still works
    

---

## Key lessons this teaches (important)

### Cache coherence ≠ correctness

### CAS enables exclusivity

### wait/notify prevent CPU burn

### Ordering makes data visible

### Shared memory is dangerous without rules

---

## If you master THIS example

You will:

- Understand JS Atomics deeply
    
- Understand CPU concurrency better than most
    
- Be able to read runtime / OS code
    
- Never fear race conditions again
    

This is not exaggeration.

---

## Recommended learning path from here

1. Break this code intentionally
    
2. Remove mutex → observe corruption
    
3. Replace mutex with CAS-only → observe spinning
    
4. Add fairness (ticket lock)
    
5. Remove mutex → build lock-free queue (advanced)