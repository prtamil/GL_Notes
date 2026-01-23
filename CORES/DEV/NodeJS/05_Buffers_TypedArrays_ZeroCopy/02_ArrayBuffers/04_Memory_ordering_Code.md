# Memory Ordering — Simple, Complete, Correct Code

We’ll demonstrate **one invariant**:

> **If a consumer sees a flag = READY, it must see the data written before it.**

That is _memory ordering_.

---

## Mental Model (Before Code)

Think in **three phases**:

1. **Prepare data** (normal writes)
    
2. **Publish** (atomic store → ordering point)
    
3. **Consume** (atomic load → ordering point)
    

Atomics **do not move data**.  
They **order visibility**.

---

## Shared Setup (Main Thread)

```js
// main.js
const { Worker } = require("worker_threads");

const sab = new SharedArrayBuffer(1024);

// Layout
// [0]      → ready flag (Int32)
// [1..]    → payload (Int32)
const state = new Int32Array(sab, 0, 1);
const payload = new Int32Array(sab, 4);

new Worker("./producer.js", { workerData: sab });
new Worker("./consumer.js", { workerData: sab });

```

---

## Producer — Publish with Ordering

```js
// producer.js
const { workerData } = require("worker_threads");

const sab = workerData;
const state = new Int32Array(sab, 0, 1);
const payload = new Int32Array(sab, 4);

// Step 1: write normal memory (NO atomics)
payload[0] = 42;
payload[1] = 99;

// ⚠️ At this point:
// Another thread might NOT see these writes yet

// Step 2: publish using atomic store (SC fence)
Atomics.store(state, 0, 1);

// This line GUARANTEES:
// "All writes before this are visible before READY = 1"

```

### What actually happened

- `payload[...] = ...` can be reordered, buffered, cached
    
- `Atomics.store`:
    
    - Flushes prior writes
        
    - Prevents reordering past this point
        
    - Makes writes visible to other threads
        

This is a **release** (and SC) operation.

---

## Consumer — Observe with Ordering

```js
// consumer.js
const { workerData } = require("worker_threads");

const sab = workerData;
const state = new Int32Array(sab, 0, 1);
const payload = new Int32Array(sab, 4);

// Step 1: wait until published
while (Atomics.load(state, 0) === 0) {
  // spin
}

// Step 2: read normal memory
console.log(payload[0]); // ALWAYS 42
console.log(payload[1]); // ALWAYS 99

```

### Why this is guaranteed

- `Atomics.load` is **sequentially consistent**
    
- It acts as an **acquire fence**
    
- It guarantees:
    
    > “If I see READY = 1, I see everything before it”
    

No race. No reordering bug.

---

## What This Demonstrates (Very Important)

### This ordering is NOT about time

❌ “Producer ran first”  
✔ “Producer’s writes became visible first”

---

## What Happens If You Remove Atomics (Bug Example)

```js
// ❌ WRONG — no ordering guarantee
state[0] = 1;

```

Consumer may see:

```js
READY = 1
payload[0] = 0   ❌

```

This is legal behavior without Atomics.

---

## Visual Timeline (Lock This In)

```js
Producer thread:
payload write ──┐
payload write ──┼──► Atomics.store(READY=1)
                │        (visibility barrier)
                ▼

Consumer thread:
Atomics.load(READY) ──► payload reads
     (visibility barrier)

```

Atomics **connect the timelines**.

---

## Sequential Consistency (SC) — Why This Is Easy

Because JS Atomics are SC:

- There is ONE global order of atomics
    
- All threads agree on it
    
- No subtle reordering cases to reason about
    

You can think:

> “Atomics execute one-at-a-time globally”

Even though they don’t physically.

---

## A Slightly More Realistic Example (State Machine)

```js
// Producer
payload[0] = compute();
Atomics.store(state, 0, 2); // READY

// Consumer
if (Atomics.load(state, 0) === 2) {
  use(payload[0]);
}

```

This is:

- How locks work
    
- How queues work
    
- How channels work
    
- How IPC works
    

---

## What Atomics Do NOT Do

❌ They do not make normal writes atomic  
❌ They do not move memory  
❌ They do not serialize execution

✔ They **order visibility**

---

## Final Mental Model (Keep This Forever)

> **Write data → Atomic store → Atomic load → Read data**
> 
> Atomics are **visibility gates**, not data carriers.

If you understand this example deeply, you understand **memory ordering**.