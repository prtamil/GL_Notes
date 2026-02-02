# Atomic Load and Store in JavaScript — Reading and Writing Correctly

Once we understand that **shared memory is tricky**, the next step is learning how to **read and write it safely**. In JavaScript, this is done using **atomic operations** provided by the `Atomics` object.

---

## 1. Atomic Load — Safe Reading

```js
Atomics.load(arr, index);

```

### What it does

- Reads a single value **atomically**
    
- Returns a **coherent, up-to-date value**
    
- Prevents **partial or torn reads**
    
- Implicitly guarantees **memory ordering**
    

### Why it matters

Without atomic load:

```js
// Worker 1
arr[0] = 42; // normal write

// Worker 2
console.log(arr[0]); // Might still see 0

```

- Worker 2 might see a stale value because of CPU caches or store buffers.
    
- Reads from shared memory are **not automatically coherent**.
    

With atomic load:

```js
console.log(Atomics.load(arr, 0)); // Guaranteed to see latest value

```

- Worker 2 always observes the **most recent committed value**
    
- Any writes that happened before are also visible
    

Atomic load ensures **correct program behavior across threads**, not just eventual agreement.

---

## 2. Atomic Store — Safe Writing

```js
Atomics.store(arr, index, value);

```

### What it does

- Writes a value **atomically**
    
- Ensures **all prior writes are visible first**
    
- Guarantees that other threads see writes in the **correct order**
    

### Why it matters

Without atomic store:

```js
// Worker 1
arr[0] = 42; 
arr[1] = 1; // flag to indicate arr[0] is ready

// Worker 2
if (arr[1] === 1) console.log(arr[0]); 
// Might print 0 because arr[0] write is delayed in store buffer

```

With atomic store:

```js
Atomics.store(arr, 0, 42);
Atomics.store(arr, 1, 1); // flag

```

- Worker 2 sees **both writes in order**
    
- Prevents subtle race conditions
    
- Maintains **program correctness**
    

---

## 3. Key Takeaways

1. **Atomic load** = reading shared memory safely, no torn values.
    
2. **Atomic store** = writing safely, with correct visibility and ordering.
    
3. Together, load and store allow multiple threads to **coordinate safely without locks**.
    
4. **Plain reads and writes are unsafe** on SharedArrayBuffer. Atomics are mandatory.
    
5. These are the **building blocks** for all higher-level atomic operations, like counters, CAS, exchange, and queues.