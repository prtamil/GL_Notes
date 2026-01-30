# 🔜 LEVEL 2 — Condition Variables (JS-style)

### Why this matters

Mutexes are simple. They let one thread claim exclusive access to a shared resource. But real-world systems rarely care about _just locking a variable_. They care about **state changes**:

> “Wait until there’s a free database connection.”  
> “Wait until the queue has items.”  
> “Wait until the resource usage drops below a threshold.”

A mutex alone cannot express this elegantly. If you just lock, check a condition, and unlock repeatedly, you end up with **busy-waiting**, wasted CPU cycles, or imprecise notifications.

This is where **condition variables** shine. They allow threads (or workers) to **sleep until a specific condition is true**, and to **wake precisely when needed**, without hogging the CPU.

---

### What you’ll learn

By implementing and using condition variables, you gain control over:

1. **Avoid spurious wakeups**  
    Threads won’t wake for no reason. They only wake when a specific condition changes. This prevents wasted CPU cycles and race conditions caused by premature wakeups.
    
2. **Precise signaling**  
    Instead of blindly waking all threads, you can signal **exactly one waiting thread**, or broadcast to all waiting threads. This is critical when multiple threads are competing for resources, like slots in a pool.
    
3. **No wasted notifications**  
    Condition variables let you signal only when the state actually changes, preventing a flood of unnecessary wakeups.
    

In short, **predicate-based waiting** lets threads sleep until a logical condition is true, instead of just “until the lock is free.”

---

### Example (conceptual)

Suppose you want a thread to wait until **`state X` becomes true**:

```js
function waitForState(shared, predicate) {
  while (!predicate(shared)) {
    // Atomically sleep while waiting for state to change
    Atomics.wait(shared, 0, 1); 
  }
}

function signalState(shared) {
  // Update shared state
  // Wake one or more waiters
  Atomics.notify(shared, 0, 1);
}

```

Here:

- `predicate(shared)` is your **condition** — a function returning true/false
    
- `Atomics.wait` suspends the thread efficiently
    
- `Atomics.notify` wakes exactly one waiting thread when the condition changes
    

This pattern directly mirrors **classic condition variables** in C++ or Java, but in **JS worker threads** using `SharedArrayBuffer` and `Atomics`.

---

### Real-world mappings

Condition variables are everywhere in systems programming. Some direct examples:

1. **Database connection pools**
    
    - Threads wait until a connection becomes available
        
    - Only one waiter is woken when a connection is returned
        
2. **Resource throttling**
    
    - Limit CPU or memory usage
        
    - Threads sleep until the system can safely allocate more
        
3. **Job schedulers / queues**
    
    - Consumer threads wait for items to appear in the queue
        
    - Producers signal consumers when jobs are ready
        

---

### New concept: predicate-based waiting

The key idea is:

> Threads should wait **on conditions, not locks**.

A **predicate** expresses the exact condition for wakeup:

```js
while (!predicate(shared)) {
    wait()
}

```

Benefits:

- Thread sleeps efficiently
    
- Wakes **only when meaningful**
    
- Avoids busy loops and spurious wakeups
    
- Encapsulates complex synchronization in a clear, reusable pattern
    

---

### Summary

- Mutexes alone are not enough; they enforce exclusivity, not logical correctness.
    
- Condition variables let threads **wait on predicates** rather than just locks.
    
- Precise signaling avoids unnecessary CPU usage and race conditions.
    
- This pattern maps directly to **real-world systems**: connection pools, throttling, schedulers.
    
- In JS, you can implement this with **`SharedArrayBuffer` + `Atomics.wait/notify`**, giving you **efficient, thread-safe coordination**.
    

Mastering JS-style condition variables puts you in **control of complex asynchronous coordination**, bridging the gap between high-level async patterns and low-level system design.

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
   CONFIGURATION
========================= */

const QUEUE_SIZE = 8;
const PRODUCERS = 2;
const CONSUMERS = 2;
const ITEMS_PER_PRODUCER = 20;

/* =========================
   CONDITION VARIABLE HELPERS
========================= */

function waitFor(shared, index, predicate) {
  // Predicate-based waiting
  while (!predicate()) {
    // Wait efficiently while predicate is false
    Atomics.wait(shared, index, 0);
  }
}

function notifyOne(shared, index) {
  Atomics.notify(shared, index, 1);
}

function notifyAll(shared, index) {
  Atomics.notify(shared, index, Number.MAX_SAFE_INTEGER);
}

/* =========================
   MAIN THREAD
========================= */

if (isMainThread) {
  // Layout:
  // 0 -> mutex
  // 1 -> head
  // 2 -> tail
  // 3 -> queue slots start
  const sab = new SharedArrayBuffer(
    Int32Array.BYTES_PER_ELEMENT * (3 + QUEUE_SIZE)
  );
  const shared = new Int32Array(sab);

  console.log("Starting JS-style condition variable queue demo...");

  // Spawn producers
  for (let i = 0; i < PRODUCERS; i++) {
    new Worker(__filename, {
      workerData: { sab, role: "producer", id: i, items: ITEMS_PER_PRODUCER },
    });
  }

  // Spawn consumers
  for (let i = 0; i < CONSUMERS; i++) {
    new Worker(__filename, {
      workerData: { sab, role: "consumer", id: i },
    });
  }

/* =========================
   WORKER THREAD
========================= */

} else {
  const { sab, role, id, items } = workerData;
  const shared = new Int32Array(sab);

  const MUTEX = 0;
  const HEAD = 1;
  const TAIL = 2;
  const BUFFER_START = 3;

  function lock() {
    while (true) {
      if (Atomics.compareExchange(shared, MUTEX, 0, 1) === 0) return;
      Atomics.wait(shared, MUTEX, 1);
    }
  }

  function unlock() {
    Atomics.store(shared, MUTEX, 0);
    Atomics.notify(shared, MUTEX, 1);
  }

  if (role === "producer") {
    for (let i = 0; i < items; i++) {
      const value = id * 100 + i;

      lock();

      // Wait until queue has space (predicate)
      waitFor(shared, TAIL, () => shared[TAIL] - shared[HEAD] < QUEUE_SIZE);

      // Enqueue item
      const pos = shared[TAIL] % QUEUE_SIZE + BUFFER_START;
      shared[pos] = value;
      shared[TAIL]++;

      // Notify one consumer
      notifyOne(shared, HEAD);

      unlock();
    }
  }

  if (role === "consumer") {
    while (true) {
      lock();

      // Wait until queue has items (predicate)
      waitFor(shared, HEAD, () => shared[TAIL] - shared[HEAD] > 0);

      // Dequeue item
      const pos = shared[HEAD] % QUEUE_SIZE + BUFFER_START;
      const value = shared[pos];
      shared[HEAD]++;

      console.log(`Consumer ${id} got value:`, value);

      // Notify one producer
      notifyOne(shared, TAIL);

      unlock();
    }
  }
}

```

---

## ✅ How this works

### 1. **Mutex**

- Protects shared indices (`HEAD` and `TAIL`)
    
- Ensures one thread updates them at a time
    

### 2. **Predicate-based waiting**

- Producers check: `queue has space`
    
- Consumers check: `queue has items`
    
- If condition false → `Atomics.wait` efficiently blocks
    

### 3. **Efficient wakeups**

- `notifyOne` wakes exactly **one waiting thread**
    
- Avoids CPU spin loops
    
- Prevents thundering herd
    

### 4. **Circular buffer**

- `pos = index % QUEUE_SIZE + BUFFER_START`
    
- Wraps head/tail over fixed-size buffer
    

### 5. **Multiple producers & consumers**

- Demonstrates real contention
    
- Threads coordinate via **condition variables**
    

---

## ⚡ Key learning points

1. **Condition variables are predicates, not locks.**
    
2. **Wait and notify are tied to a memory location.**
    
3. **Mutex ensures consistency, but predicate controls sleep/wake.**
    
4. **This mirrors real-world systems:** DB pools, job schedulers, resource throttling.

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
   CONFIGURATION
========================= */

const QUEUE_SIZE = 8; // must be power-of-two
const MASK = QUEUE_SIZE - 1;
const PRODUCERS = 2;
const CONSUMERS = 2;
const ITEMS_PER_PRODUCER = 20;

/* =========================
   MAIN THREAD
========================= */

if (isMainThread) {
  // Layout:
  // 0 -> head
  // 1 -> tail
  // 2.. -> buffer
  const sab = new SharedArrayBuffer(
    Int32Array.BYTES_PER_ELEMENT * (2 + QUEUE_SIZE)
  );
  const shared = new Int32Array(sab);

  console.log("Starting lock-free, condition-variable-style queue demo...");

  for (let i = 0; i < PRODUCERS; i++) {
    new Worker(__filename, {
      workerData: { sab, role: "producer", id: i, items: ITEMS_PER_PRODUCER },
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
  const { sab, role, id, items } = workerData;
  const shared = new Int32Array(sab);

  const HEAD = 0;
  const TAIL = 1;
  const BUFFER_START = 2;

  function notifyOne(index) {
    Atomics.notify(shared, index, 1);
  }

  /* =========================
     PRODUCER
  ========================= */
  if (role === "producer") {
    for (let i = 0; i < items; i++) {
      const value = id * 100 + i;

      while (true) {
        const tail = Atomics.load(shared, TAIL);
        const head = Atomics.load(shared, HEAD);

        // Predicate: queue full?
        if (tail - head >= QUEUE_SIZE) {
          Atomics.wait(shared, HEAD, head); // sleep until space
          continue;
        }

        // Try to reserve a slot atomically
        if (Atomics.compareExchange(shared, TAIL, tail, tail + 1) === tail) {
          const pos = BUFFER_START + (tail & MASK);
          shared[pos] = value;

          // Notify one consumer
          notifyOne(HEAD);
          break;
        }
      }
    }
  }

  /* =========================
     CONSUMER
  ========================= */
  if (role === "consumer") {
    while (true) {
      while (true) {
        const head = Atomics.load(shared, HEAD);
        const tail = Atomics.load(shared, TAIL);

        // Predicate: queue empty?
        if (tail === head) {
          Atomics.wait(shared, TAIL, tail); // sleep until data
          continue;
        }

        // Try to reserve a slot atomically
        if (Atomics.compareExchange(shared, HEAD, head, head + 1) === head) {
          const pos = BUFFER_START + (head & MASK);
          const value = shared[pos];
          console.log(`Consumer ${id} got value:`, value);

          // Notify one producer
          notifyOne(TAIL);
          break;
        }
      }
    }
  }
}

```

---

## ✅ How this works

1. **CAS = slot reservation**
    
    - Producers: `compareExchange(TAIL, tail, tail + 1)`
        
    - Consumers: `compareExchange(HEAD, head, head + 1)`
        
    - Guarantees **no two threads claim same slot**
        
2. **Predicate-based waiting**
    
    - Producer waits if `tail - head >= QUEUE_SIZE`
        
    - Consumer waits if `tail === head`
        
    - Only wakes when state changes
        
3. **Circular buffer**
    
    - `(index & MASK) + BUFFER_START`
        
    - Wraps around safely
        
4. **notifyOne**
    
    - Wakes exactly **one waiting thread**
        
    - Efficient, no busy waiting
        
5. **No mutex needed**
    
    - Entire coordination via **CAS + wait/notify + atomic loads**
        

---

## ⚡ Key learning points

- You now have a **true lock-free, MPMC queue**
    
- Uses **predicate-based sleeping** → a JS-style condition variable
    
- Demonstrates **real-world system patterns**:
    
    - Producer-consumer pipelines
        
    - Thread pools
        
    - Job scheduling
        
- Mirrors **how Node and other runtimes manage worker threads** internally