# Compare-And-Swap (CAS) and Exchange in JavaScript — Foundations of Lock-Free Programming

After understanding **atomic load, store, and RMW operations**, the most powerful primitives in JavaScript are **Compare-And-Swap (CAS)** and **Exchange**. These allow threads to coordinate safely without locks and are the building blocks of **lock-free algorithms**.

---

## 1. Compare-And-Swap (CAS)

```js
Atomics.compareExchange(arr, index, expected, replacement);

```

### What it does

CAS is a conditional atomic operation:

1. Reads the current value at `arr[index]`
    
2. Compares it to `expected`
    
3. If the current value equals `expected`, writes `replacement`
    
4. Returns the **old value**, whether or not the swap happened
    

> The key: the **read, compare, and write happen as a single atomic step**.

---

### Why CAS matters

Without CAS:

```js
if (state === FREE) {
  state = BUSY;
}

```

- Two threads could read `FREE` at the same time
    
- Both write `BUSY` → race condition
    
- The program state becomes inconsistent
    

With CAS:

```js
const old = Atomics.compareExchange(lock, 0, 0, 1);
if (old === 0) {
  // successfully acquired lock
}

```

- Only **one thread succeeds**
    
- Others retry until successful
    
- Guarantees correctness without using a mutex
    

---

### How CAS Works (CPU-level intuition)

1. Lock the memory location briefly
    
2. Compare the current value with `expected`
    
3. Write the new value only if it matches
    
4. Unlock the location
    

- No other core can intervene during this operation
    
- Prevents **lost updates** or races
    
- Forms the basis of **lock-free data structures** like queues and counters
    

---

## 2. Atomic Exchange

```js
Atomics.exchange(arr, index, value);

```

### What it does

- Swaps the current value with a new value **atomically**
    
- Returns the **old value**
    
- Does **not check a condition**, unlike CAS
    

---

### Why Exchange exists

Exchange is simpler than CAS and is often used for:

- Ownership handoff (e.g., spinlocks)
    
- Simple atomic replacement
    
- Implementing queues or flags
    

**Example — Simple spinlock:**

```js
while (Atomics.exchange(lock, 0, 1) === 1) {
  // another thread owns the lock
}
// lock acquired

```

- Only one thread acquires the lock
    
- Others keep retrying
    
- No data corruption occurs
    

---

### CAS vs Exchange — Quick Comparison

|Feature|CAS|Exchange|
|---|---|---|
|Conditional update|✅ only if expected matches|❌ unconditional swap|
|Returns old value|✅|✅|
|Typical use|Lock-free algorithms, state machines|Simple locks, ownership handoff|
|Complexity|Slightly more complex|Simpler|

---

## 3. Key Takeaways

1. **CAS and Exchange are atomic building blocks** for coordination without locks
    
2. CAS allows **conditional updates**, crucial for lock-free queues and counters
    
3. Exchange allows **unconditional handoff**, useful for locks and flags
    
4. Both return the **previous value**, allowing threads to detect success or failure
    
5. Mastering these primitives enables building **mutexes, semaphores, queues, barriers, and thread pools** entirely with atomics
    

---

Once you understand **CAS and Exchange**, you can implement **lock-free, highly concurrent data structures** in JavaScript — a major step toward **parallel and multithreaded programming**.