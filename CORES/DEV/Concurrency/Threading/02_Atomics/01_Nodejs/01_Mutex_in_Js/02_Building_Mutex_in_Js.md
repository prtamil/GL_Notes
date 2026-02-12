**# Building a Mutex in JavaScript (Step by Step)

## 0. What we are building (clear goal)

A **mutex** guarantees:

- Only **one worker** enters a critical section at a time
    
- Others **wait without burning CPU**
    
- Correct memory visibility when entering / leaving
    

At CPU level, a mutex is:

> CAS + ordering + sleep/wake

---

## 1. Shared memory layout (very important)

We need **one integer** to represent the lock.

```js
// shared.js
const sab = new SharedArrayBuffer(4); // 4 bytes = Int32
const lock = new Int32Array(sab);

// lock[0] meanings:
// 0 → unlocked
// 1 → locked

module.exports = { sab, lock };

```

### CPU mapping

- One aligned 32-bit memory location
    
- Perfect for atomic operations
    
- One cache line touched
    

---

## 2. First attempt: naive spinlock (CAS only)

This is the **minimal mutex**.

```js
function lockMutex(lock) {
  while (true) {
    const prev = Atomics.compareExchange(lock, 0, 0, 1);
    if (prev === 0) return; // acquired
  }
}

function unlockMutex(lock) {
  Atomics.store(lock, 0, 0);
}

```

```js
const { Worker, isMainThread, workerData } = require("worker_threads");

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
      const prev = Atomics.compareExchange(this.lockArray, this.index, 0, 1);
      if (prev === 0) return; // acquired
    }
  }

  unlock() {
    Atomics.store(this.lockArray, this.index, 0);
  }
}

/* =========================
   SHARED COUNTER CLASS
   ========================= */

class SharedCounter {
  constructor(sharedArray, counterIndex = 1) {
    this.sharedArray = sharedArray;
    this.counterIndex = counterIndex;
    this.mutex = new Mutex(sharedArray, 0); // mutex at index 0
  }

  increment() {
    this.mutex.lock();
    Atomics.add(this.sharedArray, this.counterIndex, 1);
    this.mutex.unlock();
  }

  get value() {
    return Atomics.load(this.sharedArray, this.counterIndex);
  }
}

/* =========================
   WORKER MANAGER
   ========================= */

class WorkerManager {
  constructor(file, workerCount, iterations, sharedArray) {
    this.file = file;
    this.workerCount = workerCount;
    this.iterations = iterations;
    this.sharedArray = sharedArray;
    this.workers = [];
  }

  startWorkers() {
    for (let i = 0; i < this.workerCount; i++) {
      const worker = new Worker(this.file, {
        workerData: { sab: this.sharedArray, iterations: this.iterations },
      });
      this.workers.push(worker);
    }

    return Promise.all(
      this.workers.map(
        (w) =>
          new Promise((resolve) => {
            w.on("exit", resolve);
          })
      )
    );
  }
}

/* =========================
   MAIN THREAD LOGIC
   ========================= */

if (isMainThread) {
  const WORKERS = 4;
  const ITERATIONS = 100_000;

  // Shared memory: index 0 → mutex, index 1 → counter
  const sab = new SharedArrayBuffer(Int32Array.BYTES_PER_ELEMENT * 2);
  const sharedArray = new Int32Array(sab);

  console.log("Starting workers...");

  const manager = new WorkerManager(__filename, WORKERS, ITERATIONS, sab);

  manager.startWorkers().then(() => {
    const counter = new SharedCounter(sharedArray);
    console.log("Expected:", WORKERS * ITERATIONS);
    console.log("Actual  :", counter.value);
  });

/* =========================
   WORKER THREAD LOGIC
   ========================= */

} else {
  const { sab, iterations } = workerData;
  const sharedArray = new Int32Array(sab);
  const counter = new SharedCounter(sharedArray);

  for (let i = 0; i < iterations; i++) {
    counter.increment();
  }
}


```
---

## 3. Why this works (processor mapping)

### `compareExchange`

At CPU level:

- Reads lock
    
- Compares with expected
    
- Writes new value if equal
    
- All as **one instruction**
    

This maps to:

- `LOCK CMPXCHG` (x86)
    
- `LDXR/STXR` loop (ARM)
    

### Guarantees

- Only one worker sees `0 → 1`
    
- No lost updates
    
- Atomicity ensured
    

---

## 4. Why this is NOT good enough ❌

This mutex is **correct**, but terrible:

### Problem: CPU spinning

Waiting workers:

- Loop forever
    
- Burn CPU cycles
    
- Destroy performance under contention
    

At processor level:

- Cache line ping-pong
    
- Massive coherence traffic
    

We need **sleep**, not spin.

---

## 5. Enter `Atomics.wait` (futex-style)

This is the **game changer**.

Instead of spinning:

- Try CAS once
    
- If failed → sleep
    
- Wake only when value changes
    

---

## 6. Improved mutex (real one)

```js
function lockMutex(lock) {
  while (true) {
    // Fast path: try to acquire
    if (Atomics.compareExchange(lock, 0, 0, 1) === 0) {
      return;
    }

    // Slow path: sleep while locked
    Atomics.wait(lock, 0, 1);
  }
}

function unlockMutex(lock) {
  Atomics.store(lock, 0, 0);
  Atomics.notify(lock, 0, 1);
}

```

This is a **proper mutex**.

```js
const { Worker, isMainThread, workerData } = require("worker_threads");

/* =========================
   MUTEX (WAIT / NOTIFY)
   ========================= */

function lockMutex(lock) {
  while (true) {
    // Fast path: try to acquire
    if (Atomics.compareExchange(lock, 0, 0, 1) === 0) {
      return;
    }

    // Slow path: sleep while locked
    Atomics.wait(lock, 0, 1);
  }
}

function unlockMutex(lock) {
  Atomics.store(lock, 0, 0);
  Atomics.notify(lock, 0, 1);
}

/* =========================
   MAIN THREAD
   ========================= */

if (isMainThread) {
  const WORKERS = 4;
  const ITERATIONS = 100_000;

  // Shared layout:
  // index 0 → mutex
  // index 1 → shared counter
  const sab = new SharedArrayBuffer(Int32Array.BYTES_PER_ELEMENT * 2);
  const shared = new Int32Array(sab);

  console.log("Starting workers with blocking mutex...");

  const workers = [];
  for (let i = 0; i < WORKERS; i++) {
    workers.push(
      new Worker(__filename, {
        workerData: {
          sab,
          iterations: ITERATIONS,
        },
      })
    );
  }

  Promise.all(
    workers.map(
      (w) =>
        new Promise((resolve) => {
          w.on("exit", resolve);
        })
    )
  ).then(() => {
    console.log("Expected:", WORKERS * ITERATIONS);
    console.log("Actual  :", Atomics.load(shared, 1));
  });

/* =========================
   WORKER THREAD
   ========================= */

} else {
  const { sab, iterations } = workerData;
  const shared = new Int32Array(sab);

  const lock = shared;      // lock lives at index 0
  const counterIndex = 1;  // shared counter

  for (let i = 0; i < iterations; i++) {
    lockMutex(lock);

    // ---- critical section ----
    shared[counterIndex]++;
    // --------------------------

    unlockMutex(lock);
  }
}

```
---

## 7. Line-by-line CPU explanation (important)

### `compareExchange(lock, 0, 0, 1)`

- Atomic RMW
    
- Only one worker wins
    
- Cache line locked briefly
    

---

### `Atomics.wait(lock, 0, 1)`

Meaning:

> “If value is still 1, put this thread to sleep”

What happens under the hood:

- Atomic check
    
- Kernel futex sleep
    
- Thread descheduled
    
- Zero CPU burn
    

---

### `Atomics.store(lock, 0, 0)`

- Atomic release of lock
    
- Updates cache line
    
- Makes prior writes visible
    

---

### `Atomics.notify(lock, 0, 1)`

- Wakes one sleeping thread
    
- Kernel wakes exactly one waiter
    
- Prevents thundering herd
    

---

## 8. Memory ordering (why this mutex is correct)

JS Atomics are **sequentially consistent**, so:

### On lock acquire

- You see **all writes** from previous owner
    

### On unlock

- All your writes are visible before lock is released
    

This gives correct **happens-before** semantics.

---

## 9. What this mutex guarantees

✅ Mutual exclusion  
✅ No busy spinning  
✅ Correct memory visibility  
✅ Portable across architectures  
✅ Maps directly to CPU primitives

This is **OS-quality synchronization**, written in JS.

---

## 10. What this mutex does NOT guarantee (important)

❌ Fairness (no FIFO order)  
❌ Priority inheritance  
❌ Reentrancy  
❌ Deadlock prevention

This is a **minimal mutex**, just like in C.

---

## 11. Why JS forbids this on main thread

`Atomics.wait`:

- Blocks the thread
    
- Would freeze the event loop
    

So:

- Only usable in **worker threads**
    
- Same rule as OS kernels
    

---

## 12. Mental model checkpoint (you should feel this)

At this point, you should clearly see:

- CAS → exclusivity
    
- wait → sleep
    
- notify → wake
    
- store → release + visibility
    

Nothing is magic anymore.

---

## 13. What we’ve built so far

Using **only processor-level ideas**, we built:

- A real mutex
    
- With proper blocking
    
- With correct memory ordering
    

This is exactly how:

- Linux futex mutexes work
    
- JVM monitors work
    
- libc pthread mutexes start**