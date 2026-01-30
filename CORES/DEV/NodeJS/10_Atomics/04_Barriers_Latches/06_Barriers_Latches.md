# 🔜 LEVEL 3 — Barriers & Latches

### Why this matters

In concurrent or distributed systems, many tasks need coordination:

1. **Start together**  
    Example: N workers must all start phase 2 only after phase 1 completes.
    
2. **Finish together**  
    Example: Map-reduce tasks must all complete their part before the reduction phase.
    

Mutexes or simple queues are insufficient here because we need **all-or-nothing synchronization** — this is where **barriers** and **latches** come in.

---

### What you’ll learn

1. **Atomic counters**
    
    - Count how many threads have arrived at the barrier.
        
2. **One-time release**
    
    - Release all waiting threads exactly once when condition is met.
        
3. **Memory publication**
    
    - Ensure all threads see the latest state after barrier is passed.
        

---

### Concept

- **Latch**: one-time event; threads wait until latch is released.
    
- **Barrier**: reusable; threads wait until **all participants reach the barrier**.
    

JS `SharedArrayBuffer` + `Atomics` makes this possible with:

- `Atomics.add` → increment counter atomically
    
- `Atomics.wait` → suspend thread
    
- `Atomics.notify` → wake threads
    

---

## Single-File Example: Barrier + Worker Threads

```js
const { Worker, isMainThread, workerData } = require("worker_threads");

/* =========================
   CONFIGURATION
========================= */

const WORKERS = 4; // total threads participating in barrier
const PHASES = 3;  // number of phases to simulate

/* =========================
   MAIN THREAD
========================= */

if (isMainThread) {
  // Layout: [counter, phaseNumber]
  // 0 -> barrier counter
  // 1 -> phase number (optional, for logging)
  const sab = new SharedArrayBuffer(Int32Array.BYTES_PER_ELEMENT * 2);
  const shared = new Int32Array(sab);

  console.log("Starting Barrier & Latch demo...");

  // Spawn workers
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

  const COUNTER = 0;
  const PHASE = 1;

  function barrier(totalWorkers) {
    // Atomically increment counter and capture old value
    const arrivalIndex = Atomics.add(shared, COUNTER, 1);

    if (arrivalIndex === totalWorkers - 1) {
      // Last thread to arrive → release all
      Atomics.store(shared, COUNTER, 0); // reset for next barrier
      Atomics.notify(shared, COUNTER, totalWorkers - 1); // wake others
    } else {
      // Wait until last thread arrives
      Atomics.wait(shared, COUNTER, arrivalIndex + 1); // sleep efficiently
    }
  }

  // Simulate multiple phases
  for (let phase = 1; phase <= PHASES; phase++) {
    console.log(`Worker ${id} starting phase ${phase}...`);

    // Simulate some work
    const workTime = Math.random() * 500 + 100;
    Atomics.wait(new Int32Array(new SharedArrayBuffer(4)), 0, 0, workTime);

    console.log(`Worker ${id} finished phase ${phase}, waiting at barrier...`);

    barrier(WORKERS);

    // Memory publication: all threads see latest state
    Atomics.store(shared, PHASE, phase);

    console.log(`Worker ${id} passed barrier for phase ${phase}`);
  }

  console.log(`Worker ${id} done all phases.`);
}

```

---

## ✅ How this works

1. **Atomic counter**
    

```js
const arrivalIndex = Atomics.add(shared, COUNTER, 1);

```

- Each worker increments counter atomically
    
- Captures its “arrival index”
    
- Ensures no race in counting threads
    

2. **Last thread releases all**
    

```js
if (arrivalIndex === totalWorkers - 1) {
  Atomics.store(shared, COUNTER, 0);      // reset barrier
  Atomics.notify(shared, COUNTER, totalWorkers - 1); // wake others
}

```

- Only **last thread** wakes everyone
    
- Prevents **lost wakeups**
    

3. **Waiting threads sleep efficiently**
    

```js
Atomics.wait(shared, COUNTER, arrivalIndex + 1);

```

- Threads park until counter changes
    
- No CPU spin
    
- Waits until **barrier reached**
    

4. **Memory publication**
    

```js
Atomics.store(shared, PHASE, phase);

```

- Ensures that **all threads see the latest phase**
    
- Guarantees sequential consistency after barrier
    

5. **Reusable barrier**
    

- After release, counter resets to 0
    
- Can be used for multiple phases or iterations
    

---

### Real-world examples

1. **Worker startup synchronization**
    
    - All threads must finish initialization before starting work.
        
2. **Phase-based computation**
    
    - Like simulation steps: all threads must finish step N before step N+1.
        
3. **Map-reduce style workflows**
    
    - All map tasks finish → reduce phase starts
        

---

### Key Takeaways

- **Barriers and latches** are core synchronization primitives beyond mutexes.
    
- **CAS / atomic increment** + **wait/notify** are sufficient to implement them in JS.
    
- They ensure **all-or-nothing coordination**, memory visibility, and efficient waiting.
    
- Mastering them gives you tools to build **worker pools, phase-based computations, distributed tasks**, and **parallel algorithms**.


