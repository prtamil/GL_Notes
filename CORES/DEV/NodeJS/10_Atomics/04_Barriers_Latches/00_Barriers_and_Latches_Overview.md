# 1️⃣ Concept overview: Barrier vs Latch
## difference
### 🧱 Barrier — _symmetric coordination_

1. Everyone participates. Everyone waits. Everyone proceeds.
2. We are doing **phases**. Nobody starts the next phase alone
3. Barriers coordinate progress.
4. If it **resets**, it’s a barrier.
#### Contract

- Every participating thread **must reach the barrier**
- No thread may pass **until all have arrived**
- All threads are equal

### ⏳ Latch — _asymmetric coordination_
1. Some threads do work. Other threads wait.
2. I don’t care how you coordinate. Tell me when you’re done
3. Latches coordinate completion
4. If it **counts down to zero once**, it’s a latch.
  
#### Contract

- Workers decrement the latch
    
- Waiters block until count reaches zero
    
- Workers do _not_ wait for each other

## 🧱 Barrier — _“Wait for everyone”_

**Intention**

> _All participating threads must reach the same point before any can proceed._

### Key properties

- Group coordination
    
- Reusable (usually)
    
- Phase-based
    
- Nobody proceeds alone
    

### Mental model

```js
Phase 1 work
      ↓
 ┌───────────┐
 │  BARRIER  │ ← everyone waits here
 └───────────┘
      ↓
Phase 2 work

```

### Real-world analogies

- Game engine frame sync
    
- Simulation timesteps
    
- ML training epochs
    
- BSP (Bulk Synchronous Parallel) systems
    

---

## ⏳ Latch — _“Wait until done”_

**Intention**

> _One or more threads wait until a fixed number of events complete._

### Key properties

- One-shot (usually)
    
- Countdown-based
    
- Asymmetric (workers vs waiters)
    
- Cannot be reused
    

### Mental model

```js
Task A ─┐
Task B ─┼─▶ countdown to zero ─▶ proceed
Task C ─┘

```

### Real-world analogies

- Service startup gates
    
- Waiting for N tasks to finish
    
- Shutdown coordination
    
- “Ready” signals
    

---

## 🧠 Barrier vs Latch (quick contrast)

|Aspect|Barrier|Latch|
|---|---|---|
|Who waits|Everyone|One or more waiters|
|Trigger|All arrive|Counter reaches zero|
|Reusable|Yes|No|
|Shape|Symmetric|Asymmetric|
|Pattern|Phases|Completion|

---

# 2️⃣ Barrier — complete single-file Node.js implementation

## 🧩 Intention

> Coordinate multiple worker threads so **no phase advances until all threads finish the current phase**.

---

### ✅ `barrier.js` (single file)

```js
const { Worker, isMainThread, workerData } = require("worker_threads");

/* =========================
   CONFIG
========================= */

const WORKERS = 4;
const PHASES = 3;

/* =========================
   SHARED MEMORY LAYOUT
========================= */
// [0] arrival counter
// [1] phase (for visibility/logging)
const OFFSETS = {
  COUNT: 0,
  PHASE: 1,
};

/* =========================
   BARRIER PRIMITIVE
========================= */

class Barrier {
  constructor(shared, parties) {
    this.shared = shared;
    this.parties = parties;
    this.index = OFFSETS.COUNT;
  }

  await() {
    // Register arrival
    const arrival = Atomics.add(this.shared, this.index, 1);

    // Last thread releases all
    if (arrival === this.parties - 1) {
      Atomics.store(this.shared, this.index, 0);
      Atomics.notify(this.shared, this.index, this.parties - 1);
    } else {
      // Wait until counter resets
      Atomics.wait(this.shared, this.index, arrival + 1);
    }
  }
}

/* =========================
   MAIN THREAD
========================= */

if (isMainThread) {
  const sab = new SharedArrayBuffer(
    Int32Array.BYTES_PER_ELEMENT * 2
  );
  const shared = new Int32Array(sab);

  console.log("Barrier demo starting");

  for (let i = 0; i < WORKERS; i++) {
    new Worker(__filename, {
      workerData: { sab, id: i },
    });
  }

/* =========================
   WORKER THREAD
========================= */

} else {
  const { sab, id } = workerData;
  const shared = new Int32Array(sab);

  const barrier = new Barrier(shared, WORKERS);

  for (let phase = 1; phase <= PHASES; phase++) {
    doWork(id, phase);

    console.log(`Worker ${id} waiting at barrier (phase ${phase})`);
    barrier.await();

    // Memory publication point
    Atomics.store(shared, OFFSETS.PHASE, phase);

    console.log(`Worker ${id} passed barrier (phase ${phase})`);
  }

  console.log(`Worker ${id} finished all phases`);
}

/* =========================
   WORK SIMULATION
========================= */

function doWork(id, phase) {
  const delay = Math.random() * 400 + 100;
  Atomics.wait(new Int32Array(new SharedArrayBuffer(4)), 0, 0, delay);
}

```

---

### 🔍 What this demonstrates

- **Atomic arrival counting**
    
- **Last-arriver release**
    
- **Efficient blocking (`Atomics.wait`)**
    
- **Reusable cyclic barrier**
    
- **Memory visibility across phases**
    

---

# 3️⃣ Latch — complete single-file Node.js implementation

## 🧩 Intention

> Allow one or more threads to **wait until N independent tasks finish**.

---

### ✅ `latch.js` (single file)

```js
const { Worker, isMainThread, workerData } = require("worker_threads");

/* =========================
   CONFIG
========================= */

const TASKS = 4;

/* =========================
   SHARED MEMORY LAYOUT
========================= */
// [0] remaining count
const OFFSETS = {
  COUNT: 0,
};

/* =========================
   COUNTDOWN LATCH
========================= */

class CountDownLatch {
  constructor(shared, count) {
    this.shared = shared;
    Atomics.store(this.shared, OFFSETS.COUNT, count);
  }

  countDown() {
    const remaining = Atomics.sub(this.shared, OFFSETS.COUNT, 1);

    // Last completion wakes waiters
    if (remaining === 1) {
      Atomics.notify(this.shared, OFFSETS.COUNT);
    }
  }

  await() {
    while (Atomics.load(this.shared, OFFSETS.COUNT) > 0) {
      Atomics.wait(
        this.shared,
        OFFSETS.COUNT,
        Atomics.load(this.shared, OFFSETS.COUNT)
      );
    }
  }
}

/* =========================
   MAIN THREAD
========================= */

if (isMainThread) {
  const sab = new SharedArrayBuffer(
    Int32Array.BYTES_PER_ELEMENT
  );
  const shared = new Int32Array(sab);

  const latch = new CountDownLatch(shared, TASKS);

  console.log("Main thread waiting for tasks...");

  for (let i = 0; i < TASKS; i++) {
    new Worker(__filename, {
      workerData: { sab, id: i },
    });
  }

  latch.await();
  console.log("All tasks completed. Proceeding.");

/* =========================
   WORKER THREAD
========================= */

} else {
  const { sab, id } = workerData;
  const shared = new Int32Array(sab);
  const latch = new CountDownLatch(shared, 0);

  doTask(id);
  latch.countDown();
}

/* =========================
   TASK SIMULATION
========================= */

function doTask(id) {
  const delay = Math.random() * 500 + 100;
  Atomics.wait(new Int32Array(new SharedArrayBuffer(4)), 0, 0, delay);
  console.log(`Task ${id} done`);
}

```

---

### 🔍 What this demonstrates

- **Countdown semantics**
    
- **One-shot coordination**
    
- **Asymmetric roles (workers vs waiter)**
    
- **Efficient waiting**
    
- **Startup / shutdown gates**
    

---

# 🧠 Final mental model (lock this in)

- **Barrier** = _“We move together”_
    
- **Latch** = _“Wait until done”_
    

Both are built from:

- Atomic counters
    
- Predicate-based waiting
    
- Precise wakeups
    

And both are **foundational** to:

- Thread pools
    
- Schedulers
    
- Distributed systems
    
- Runtime internals