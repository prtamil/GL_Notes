# Atomics.wait and Atomics.notify — Futex-Style Coordination in JavaScript

After understanding atomic load, store, RMW, CAS, and exchange, the next step is **coordinating threads efficiently**. This is where `Atomics.wait` and `Atomics.notify` come in. They allow threads to **sleep without busy-waiting** and wake **precisely when needed**, implementing **condition-variable-like behavior** in JS.

---

## 1. Why Sleep Is Tricky

Without proper coordination:

```js
while (arr[0] === 0) {
  // spin loop
}

```

- Threads continuously check a condition
    
- Wastes CPU cycles
    
- Can cause **performance degradation** on multiple cores
    

JavaScript provides a **futex-style primitive**:

- **Sleep until a memory value changes**
    
- Wake only the relevant threads
    
- Avoid busy-waiting
    

---

## 2. Atomics.wait — Sleep Until a Condition Changes

```js
Atomics.wait(arr, index, expectedValue[, timeout]);

```

### How it works

1. Checks if `arr[index] === expectedValue`
    
2. If true, the thread **sleeps efficiently**
    
3. If false, returns immediately
    
4. Optionally, sleeps up to `timeout` milliseconds
    

**Example — Waiting for a flag:**

```js
// Worker
console.log("Waiting for flag...");
Atomics.wait(arr, 0, 0); // sleep until arr[0] != 0
console.log("Flag changed!");

```

- The thread is **parked**, not spinning
    
- CPU resources are free for other threads
    
- Scales well with many threads
    

---

## 3. Atomics.notify — Wake Sleeping Threads

```js
Atomics.notify(arr, index, count);

```

### How it works

- Wakes up `count` threads sleeping on `arr[index]`
    
- If `count = Infinity` (or `Number.MAX_SAFE_INTEGER`), wakes all
    
- Can be called by another thread after changing the value
    

**Example — Setting a flag and waking:**

```js
// Producer
arr[0] = 1;
Atomics.notify(arr, 0, 1); // wake one waiting thread

```

- Only threads that are waiting on this **specific memory location** are woken
    
- Avoids the **thundering herd problem**
    

---

## 4. Futex-Style Coordination

`Atomics.wait` + `Atomics.notify` in JS work like **futexes** in the OS world:

- Minimal CPU usage while waiting
    
- Wakeups are precise and efficient
    
- Forms the basis for **condition variables**, **barriers**, and **queues**
    

**Example — Simple condition variable pattern:**

```js
// Consumer
while (arr[0] === 0) {
  Atomics.wait(arr, 0, 0); // sleep until producer sets arr[0]
}

// Producer
arr[0] = 42;
Atomics.notify(arr, 0, 1);

```

- Consumer sleeps until the producer signals
    
- Producer signals exactly one waiting consumer
    

---

## 5. Key Takeaways

1. **Atomics.wait** = sleep efficiently while waiting for a memory condition
    
2. **Atomics.notify** = wake specific waiting threads
    
3. Together, they implement **condition-variable-style synchronization** in JS
    
4. Avoid **busy loops**, save CPU, and scale to many threads
    
5. Used for **barriers, queues, and work coordination** in multi-threaded programs
    

---

Once you understand **Atomics.wait/notify**, you can implement **high-level concurrency primitives in JavaScript**, like **barriers, latches, producer-consumer queues, and thread pools** — all without traditional mutexes.