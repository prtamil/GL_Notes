
# Example Code

Perfect — let’s build a **single-file, runnable JS example** that demonstrates **condition-variable-style waiting** using **worker threads**, `SharedArrayBuffer`, and `Atomics`.

It will have:

- Multiple producers
    
- Multiple consumers
    
- Predicate-based waiting (`while (!condition) wait`)
    
- Efficient wakeups using `Atomics.notify`
    

---

## 📄 `condition_variable_queue.js`

```js
const { Worker, isMainThread, workerData } = require("worker_threads");

/* =========================
   CONFIG
========================= */

const QUEUE_SIZE = 8;
const PRODUCERS = 2;
const CONSUMERS = 2;
const ITEMS_PER_PRODUCER = 20;

/* =========================
   SHARED MEMORY LAYOUT
========================= */
// [0] mutex
// [1] head
// [2] tail
// [3..] buffer
const OFFSETS = {
  MUTEX: 0,
  HEAD: 1,
  TAIL: 2,
  BUFFER_START: 3,
};

/* =========================
   SYNCHRONIZATION PRIMITIVES
========================= */

class Mutex {
  constructor(shared) {
    this.shared = shared;
    this.index = OFFSETS.MUTEX;
  }

  lock() {
    while (true) {
      if (Atomics.compareExchange(this.shared, this.index, 0, 1) === 0) return;
      Atomics.wait(this.shared, this.index, 1);
    }
  }

  unlock() {
    Atomics.store(this.shared, this.index, 0);
    Atomics.notify(this.shared, this.index, 1);
  }
}

class Condition {
  constructor(shared, index) {
    this.shared = shared;
    this.index = index;
  }

  wait(predicate) {
    while (!predicate()) {
      Atomics.wait(this.shared, this.index, 0);
    }
  }

  notifyOne() {
    Atomics.notify(this.shared, this.index, 1);
  }
}

/* =========================
   BOUNDED QUEUE
========================= */

class BoundedQueue {
  constructor(shared, capacity) {
    this.shared = shared;
    this.capacity = capacity;

    this.mutex = new Mutex(shared);
    this.notEmpty = new Condition(shared, OFFSETS.HEAD);
    this.notFull = new Condition(shared, OFFSETS.TAIL);
  }

  size() {
    return (
      this.shared[OFFSETS.TAIL] -
      this.shared[OFFSETS.HEAD]
    );
  }

  enqueue(value) {
    this.mutex.lock();

    this.notFull.wait(() => this.size() < this.capacity);

    const pos =
      (this.shared[OFFSETS.TAIL] % this.capacity) +
      OFFSETS.BUFFER_START;

    this.shared[pos] = value;
    this.shared[OFFSETS.TAIL]++;

    this.notEmpty.notifyOne();
    this.mutex.unlock();
  }

  dequeue() {
    this.mutex.lock();

    this.notEmpty.wait(() => this.size() > 0);

    const pos =
      (this.shared[OFFSETS.HEAD] % this.capacity) +
      OFFSETS.BUFFER_START;

    const value = this.shared[pos];
    this.shared[OFFSETS.HEAD]++;

    this.notFull.notifyOne();
    this.mutex.unlock();

    return value;
  }
}

/* =========================
   MAIN THREAD
========================= */

if (isMainThread) {
  const sab = new SharedArrayBuffer(
    Int32Array.BYTES_PER_ELEMENT * (OFFSETS.BUFFER_START + QUEUE_SIZE)
  );
  const shared = new Int32Array(sab);

  console.log("Starting producer-consumer demo");

  for (let i = 0; i < PRODUCERS; i++) {
    new Worker(__filename, {
      workerData: { sab, role: "producer", id: i },
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
  const { sab, role, id } = workerData;
  const shared = new Int32Array(sab);
  const queue = new BoundedQueue(shared, QUEUE_SIZE);

  if (role === "producer") {
    for (let i = 0; i < ITEMS_PER_PRODUCER; i++) {
      const value = id * 100 + i;
      queue.enqueue(value);
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
## ✅ How this works (Refactored version)

### 1. **Mutex (Mutual Exclusion)**

- Encapsulated in the `Mutex` class
    
- Protects **shared queue state**:
    
    - `HEAD`
        
    - `TAIL`
        
    - buffer slots
        
- Guarantees **only one thread** can modify queue state at a time
    

```js
this.mutex.lock();
...
this.mutex.unlock();

```

➡️ This ensures atomicity of enqueue/dequeue operations.

---

### 2. **Condition Variables (Predicate-based waiting)**

- Encapsulated in the `Condition` class
    
- Each condition is associated with **one shared memory index**
    

|Condition|Predicate|
|---|---|
|`notFull`|`queue.size() < capacity`|
|`notEmpty`|`queue.size() > 0`|

```js
this.notFull.wait(() => this.size() < this.capacity);
this.notEmpty.wait(() => this.size() > 0);

```

➡️ Threads **sleep efficiently** until the predicate becomes true.

---

### 3. **Efficient Sleep & Wakeup (No spinning)**

- Uses `Atomics.wait` instead of busy loops
    
- Uses `Atomics.notify(…, 1)` to wake **exactly one** waiter
    

```js
this.notEmpty.notifyOne();
this.notFull.notifyOne();

```

**Benefits**

- No CPU burn
    
- No thundering herd problem
    
- Scales under contention
    

---

### 4. **Bounded Circular Buffer**

- Implemented inside `BoundedQueue`
    
- Fixed-size buffer with wraparound indexing
    

```js
pos = (index % capacity) + BUFFER_START;

```

- `HEAD` and `TAIL` grow monotonically
    
- Modulo operation maps them into the buffer
    

➡️ Simple, safe, cache-friendly design.

---

### 5. **Multiple Producers & Consumers**

- Any number of producers can call `enqueue`
    
- Any number of consumers can call `dequeue`
    
- Correctness is enforced by:
    
    - Mutex for **state safety**
        
    - Conditions for **coordination**
        

Producer logic:

```js
queue.enqueue(value);

```

Consumer logic:

```js
const value = queue.dequeue();

```

➡️ Business logic stays clean; concurrency is hidden.

---

## ⚡ Key learning points (Refined)

1. **Condition variables express _state_, not ownership.**
    
    - The predicate defines _when_ a thread may proceed.
        
    - The mutex defines _who_ may modify state.
        
2. **Waiting is always tied to shared memory.**
    
    - `Atomics.wait` sleeps on a specific index.
        
    - Notifications are scoped, precise, and cheap.
        
3. **Mutex ensures correctness; predicates ensure liveness.**
    
    - Lock prevents corruption.
        
    - Predicate prevents deadlock & busy waiting.
        
4. **This is the same pattern used everywhere.**
    
    - DB connection pools
        
    - Thread pools
        
    - Job queues
        
    - Rate limiters
        
    - Backpressure systems
        

➡️ You’re implementing a **fundamental coordination primitive**, not a toy example.