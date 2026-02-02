# Read-Modify-Write (RMW) Operations in JavaScript — Updating Shared Memory Safely

After understanding **atomic load and store**, the next step is **updating shared memory safely**. This is where **Read-Modify-Write (RMW) operations** come in.

RMW operations allow a thread to **read a value, modify it, and write it back** as a **single, atomic step**. This avoids race conditions when multiple threads try to update the same memory location at the same time.

---

## 1. What are RMW Operations?

JavaScript provides several RMW operations:

```js
Atomics.add(arr, index, delta);
Atomics.sub(arr, index, delta);
Atomics.and(arr, index, mask);
Atomics.or(arr, index, mask);
Atomics.xor(arr, index, mask);

```

- **add / sub**: increment or decrement a counter
    
- **and / or / xor**: bitwise updates
    
- All of them **read the old value and write the new one atomically**
    
- Returns the **previous value** before modification
    

### Why normal code fails

```js
arr[0] = arr[0] + 1; // unsafe!

```

- Two threads can read the same value simultaneously
    
- Both compute the same result
    
- One update overwrites the other — **lost update**
    

---

## 2. How RMW Works (Conceptually)

```js
const old = Atomics.add(arr, 0, 1);

```

Step-by-step:

1. Lock the memory location (briefly)
    
2. Read the current value (`old`)
    
3. Add `1` to it
    
4. Write the new value back
    
5. Unlock the memory location
    

All of this happens as **one indivisible step** — no other thread can intervene.

---

## 3. Example — Shared Counter

```js
const sab = new SharedArrayBuffer(4);
const arr = new Int32Array(sab);

function incrementCounter() {
  const previous = Atomics.add(arr, 0, 1);
  console.log('Counter before increment:', previous);
}

incrementCounter();

```

- If multiple threads call `incrementCounter()` simultaneously:
    
    - No increments are lost
        
    - Each thread sees a **unique previous value**
        
    - The counter is always correct
        

---

## 4. Real-world Use Cases

1. **Shared counters**
    
    - Count tasks completed across threads
        
2. **Statistics collection**
    
    - Safely update totals or aggregates
        
3. **Work coordination**
    
    - Track available resources or slots
        

RMW is the **foundation for lock-free programming** because it allows threads to **update shared state without blocking**.

---

## 5. Key Takeaways

1. **RMW = read, modify, write in one atomic step**
    
2. Prevents **lost updates** in concurrent programs
    
3. Works on integers (typed arrays only)
    
4. Returns the **old value**, which is useful for coordination
    
5. Can be used to build **counters, semaphores, and queues**