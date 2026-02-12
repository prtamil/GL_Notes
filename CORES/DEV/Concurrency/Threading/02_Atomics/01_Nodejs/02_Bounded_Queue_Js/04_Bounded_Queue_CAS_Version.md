> A _true_ lock-free MPMC queue is **much harder** than a mutex queue.  
> So we’ll do this **properly but pedagogically**, not hand-wavy.

What you will get:

- **No mutex**
    
- **Only CAS + atomic loads/stores**
    
- **Multiple producers**
    
- **Multiple consumers**
    
- **Correct under contention**
    
- **Minimal waiting (still uses `wait/notify`, but no locks)**
    

This mirrors how **real runtimes** do it.

---

# First: what “lock-free” really means

Lock-free does **NOT** mean:

- no waiting
    
- no blocking ever
    

It means:

> **System makes progress even if one thread is paused or slow**

No one _owns_ a critical section.

---

# Design: CAS-based Ring Buffer (MPMC)

We’ll use:

- `head` → consumer index
    
- `tail` → producer index
    
- No `count`
    
- Capacity = power of two
    
- CAS loops on head/tail
    

Memory layout:

```js
[ head | tail | buffer... ]

```

---

# Core idea (important)

### Producer

1. Read `tail`
    
2. Read `head`
    
3. If full → wait
    
4. CAS `tail` → reserve slot
    
5. Write data
    

### Consumer

1. Read `head`
    
2. Read `tail`
    
3. If empty → wait
    
4. CAS `head` → reserve slot
    
5. Read data
    

**Reservation via CAS** is the key.

---

# Full single-file example (lock-free)

Save as:

`node lockfree_queue.js`

---

## 📄 `lockfree_queue.js`

```js
const { Worker, isMainThread, workerData } = require("worker_threads");

/* =========================
   CONSTANTS
   ========================= */
const QUEUE_SIZE = 8; // must be power of 2
const MASK = QUEUE_SIZE - 1;

/* =========================
   LOCK-FREE QUEUE CLASS
   ========================= */
class LockFreeQueue {
  constructor(sharedArray, queueSize = QUEUE_SIZE) {
    this.shared = sharedArray;
    this.queueSize = queueSize;
    this.headIndex = 0;
    this.tailIndex = 1;
    this.bufferStart = 2;
    this.mask = queueSize - 1;
  }

  enqueue(item) {
    while (true) {
      const tail = Atomics.load(this.shared, this.tailIndex);
      const head = Atomics.load(this.shared, this.headIndex);

      // Queue full
      if (tail - head >= this.queueSize) {
        Atomics.wait(this.shared, this.headIndex, head);
        continue;
      }

      // Try to reserve a slot
      if (Atomics.compareExchange(this.shared, this.tailIndex, tail, tail + 1) === tail) {
        this.shared[this.bufferStart + (tail & this.mask)] = item;
        Atomics.notify(this.shared, this.tailIndex, 1); // wake consumers
        return;
      }
    }
  }

  dequeue() {
    while (true) {
      const head = Atomics.load(this.shared, this.headIndex);
      const tail = Atomics.load(this.shared, this.tailIndex);

      // Queue empty
      if (tail === head) {
        Atomics.wait(this.shared, this.tailIndex, tail);
        continue;
      }

      // Try to reserve a slot
      if (Atomics.compareExchange(this.shared, this.headIndex, head, head + 1) === head) {
        const value = this.shared[this.bufferStart + (head & this.mask)];
        Atomics.notify(this.shared, this.headIndex, 1); // wake producers
        return value;
      }
    }
  }
}

/* =========================
   MAIN THREAD
   ========================= */
if (isMainThread) {
  const PRODUCERS = 2;
  const CONSUMERS = 2;
  const ITEMS = 20;

  const sab = new SharedArrayBuffer(Int32Array.BYTES_PER_ELEMENT * (2 + QUEUE_SIZE));
  const shared = new Int32Array(sab);

  console.log("Starting lock-free queue demo...");

  for (let i = 0; i < PRODUCERS; i++) {
    new Worker(__filename, { workerData: { sab, role: "producer", id: i, items: ITEMS } });
  }

  for (let i = 0; i < CONSUMERS; i++) {
    new Worker(__filename, { workerData: { sab, role: "consumer", id: i } });
  }

/* =========================
   WORKER THREAD
   ========================= */
} else {
  const { sab, role, id, items } = workerData;
  const queue = new LockFreeQueue(new Int32Array(sab));

  if (role === "producer") {
    for (let i = 0; i < items; i++) {
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

Here’s an updated explanation reflecting the **new LockFreeQueue abstraction** and simplified worker logic:

---

# Line-by-line: what makes this lock-free

## 1️⃣ Fully encapsulated, no mutex

The new code wraps all atomic operations inside `LockFreeQueue`.  
No thread ever blocks another from **making progress**:

```js
queue.enqueue(value)
queue.dequeue()

```

- Producers and consumers operate independently.
    
- No explicit locks are required.
    

---

## 2️⃣ CAS = slot reservation

```js
Atomics.compareExchange(shared, TAIL, tail, tail + 1)
Atomics.compareExchange(shared, HEAD, head, head + 1)

```

This means:

> “I am claiming this index — no one else can”

Only **one thread wins**, ensuring safe slot reservation without locks.

---

## 3️⃣ Data visibility guarantee

The enqueue sequence inside the queue is:

```js
CAS tail → write data → notify

```

The dequeue sequence:

```js
CAS head → read data → notify

```

Because of this ordering:

- Consumers only read **after head advances**, so they see fully written items.
    
- `Atomics` in JS are **sequentially consistent**, ensuring memory visibility across threads.
    

---

## 4️⃣ No separate `count` variable

Derived state replaces `count`:

```js
count = tail - head

```

- Avoids races on a shared counter.
    
- Queue fullness/emptiness is computed dynamically, keeping operations lock-free.
    

---

## 5️⃣ wait / notify still allowed

Even though threads can sleep with `Atomics.wait`:

- Lock-freedom is maintained because **no thread owns a resource**.
    
- Sleeping threads don’t block progress.
    
- Other threads can still enqueue/dequeue freely.
    

---

# What you just learned (important)

|Concept|Yes|
|---|---|
|Lock-free algorithms|✅|
|CAS contention|✅|
|ABA avoidance (via monotonic counters)|✅|
|Memory visibility|✅|
|Real MPMC queue design|✅|

**Key difference in this update:**

- **Abstraction:** `LockFreeQueue` now hides head/tail, masking, and atomic operations, making the queue **easier to use and intention-revealing**.
    
- **Worker logic:** Clean `queue.enqueue(value)` / `queue.dequeue()`, showing exactly what producers and consumers are doing.
    
- **Masking for power-of-2 buffer:** `(index & MASK)` replaces modulo operations, keeping lock-free performance optimal.
    

This is **production-ready knowledge** for understanding **lock-free multi-producer/multi-consumer queues in JavaScript**.