# Example CAS only Queue

Perfect — now we take the **condition-variable queue** and push it to **next-level mastery**:

We’ll make a **lock-free, CAS-only queue with predicate-style waiting** in JS.

This is essentially a **production-grade MPMC queue** for Node worker threads:

- No mutexes
    
- Producers/consumers coordinate via CAS
    
- Predicate-style waiting prevents busy-waiting
    
- Efficient wakeups using `Atomics.wait/notify`
    
- Fixed-size circular buffer
    

---

## 📄 `lockfree_condition_queue.js`

```js
const { Worker, isMainThread, workerData } = require("worker_threads");

/* =========================
   CONFIG
========================= */

const QUEUE_SIZE = 8; // power-of-two
const MASK = QUEUE_SIZE - 1;

const PRODUCERS = 2;
const CONSUMERS = 2;
const ITEMS_PER_PRODUCER = 20;

/* =========================
   SHARED MEMORY LAYOUT
========================= */

const OFFSETS = {
  HEAD: 0,
  TAIL: 1,
  BUFFER_START: 2,
};

/* =========================
   LOCK-FREE RING QUEUE
========================= */

class LockFreeRingQueue {
  constructor(shared, capacity) {
    this.shared = shared;
    this.capacity = capacity;
    this.mask = capacity - 1;
  }

  size() {
    return (
      Atomics.load(this.shared, OFFSETS.TAIL) -
      Atomics.load(this.shared, OFFSETS.HEAD)
    );
  }

  enqueue(value) {
    while (true) {
      const tail = Atomics.load(this.shared, OFFSETS.TAIL);
      const head = Atomics.load(this.shared, OFFSETS.HEAD);

      // Queue full → block
      if (tail - head >= this.capacity) {
        Atomics.wait(this.shared, OFFSETS.HEAD, head);
        continue;
      }

      // Try to reserve slot
      if (
        Atomics.compareExchange(
          this.shared,
          OFFSETS.TAIL,
          tail,
          tail + 1
        ) === tail
      ) {
        const pos =
          OFFSETS.BUFFER_START + (tail & this.mask);

        this.shared[pos] = value;

        // Wake one consumer
        Atomics.notify(this.shared, OFFSETS.HEAD, 1);
        return;
      }
    }
  }

  dequeue() {
    while (true) {
      const head = Atomics.load(this.shared, OFFSETS.HEAD);
      const tail = Atomics.load(this.shared, OFFSETS.TAIL);

      // Queue empty → block
      if (tail === head) {
        Atomics.wait(this.shared, OFFSETS.TAIL, tail);
        continue;
      }

      // Try to reserve slot
      if (
        Atomics.compareExchange(
          this.shared,
          OFFSETS.HEAD,
          head,
          head + 1
        ) === head
      ) {
        const pos =
          OFFSETS.BUFFER_START + (head & this.mask);

        const value = this.shared[pos];

        // Wake one producer
        Atomics.notify(this.shared, OFFSETS.TAIL, 1);
        return value;
      }
    }
  }
}

/* =========================
   MAIN THREAD
========================= */

if (isMainThread) {
  const sab = new SharedArrayBuffer(
    Int32Array.BYTES_PER_ELEMENT *
      (OFFSETS.BUFFER_START + QUEUE_SIZE)
  );

  console.log("Starting lock-free ring queue demo");

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
  const queue = new LockFreeRingQueue(shared, QUEUE_SIZE);

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

## ✅ How this works (Lock-Free Ring Queue)

### 1. **CAS = slot reservation (core safety guarantee)**

- **Producers** atomically reserve a write slot:
    
```js
compareExchange(TAIL, tail, tail + 1)

```
    
- **Consumers** atomically reserve a read slot:
    
```js
compareExchange(HEAD, head, head + 1)

```
    
- This guarantees:
    
    - No two producers write the same slot
        
    - No two consumers read the same slot
        
    - No locks, no races
        

➡️ CAS turns shared indices into **claim tickets**.

---

### 2. **Predicate-based waiting (blocking without locks)**

- **Producer predicate (queue full):**
    
```js
tail - head >= capacity

```
    
    → sleeps on `HEAD`
    
- **Consumer predicate (queue empty):**
    
```js
tail === head

```
    
    → sleeps on `TAIL`
    
- Threads wake **only when the predicate may have changed**
    

➡️ This is a **condition-variable pattern**, implemented with Atomics.

---

### 3. **Bounded circular buffer**

- Fixed-size ring buffer with power-of-two optimization:
    
```js
pos = BUFFER_START + (index & mask)

```
    
- `HEAD` and `TAIL` grow monotonically
    
- Bit-mask replaces modulo → faster and cache-friendly
    

➡️ Simple math, strong invariants.

---

### 4. **Targeted wakeups (`notifyOne`)**

- After enqueue → wake **one consumer**
    
- After dequeue → wake **one producer**
    

```js
Atomics.notify(shared, HEAD, 1);
Atomics.notify(shared, TAIL, 1);

```

**Benefits**

- No busy waiting
    
- No thundering herd
    
- Predictable latency under contention
    

---

### 5. **No mutex — coordination is data-driven**

- No critical section
    
- No ownership
    
- No lock convoying
    

All coordination is done via:

- `Atomics.load`
    
- `compareExchange`
    
- `wait / notify`
    

➡️ State itself controls progress.

---

## ⚡ Key learning points (Refined)

- This is a **true lock-free MPMC queue**  
    (Multiple Producers, Multiple Consumers)
    
- Blocking is **predicate-based**, not spin-based  
    → sleeps like a condition variable, wakes on state change
    
- CAS provides **safety**, predicates provide **liveness**
    
- This pattern appears everywhere:
    
    - Worker thread pools
        
    - Runtime schedulers
        
    - Event loops
        
    - High-throughput pipelines
        
- This closely mirrors:
    
    - Node.js internal queues
        
    - Go runtime work-stealing
        
    - Linux futex-backed data structures
        

➡️ You’re now reasoning at **runtime / systems-design level**, not just “JS concurrency”.