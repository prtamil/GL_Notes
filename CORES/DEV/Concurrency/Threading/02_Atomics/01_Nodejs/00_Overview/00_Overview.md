## Why Caches Break Multithreaded Programs (and How Atomics Fix Them)

Modern CPUs are extremely fast because they **do not work directly with main memory** all the time.  
Instead, each CPU core has:

- Its **own cache** (L1 / L2)
    
- A **store buffer** (where writes wait before becoming visible)
    
- **Speculative execution** (running ahead and fixing mistakes later)
    

This design makes single-threaded programs fast — but it makes **multithreaded programs tricky**.

---

## The Core Problem: Each CPU Core Sees Its Own Version of Memory

When multiple threads run on different CPU cores, **they do not see memory at the same time**.

Each core:

- Reads from its **local cache**
    
- Writes go into a **store buffer first**
    
- Updates reach other cores **later**
    

So two cores can temporarily disagree about memory values.

---

## Cache Coherence: What It Solves (and What It Does NOT)

CPUs use **cache coherence protocols** (like MESI) to avoid total chaos.

### What cache coherence guarantees

- If one core writes a value
    
- Other cores will **eventually** see that value
    
- No one sees corrupted or half-written data
    

This is called **coherence**.

### What cache coherence does NOT guarantee

- It does **not** guarantee _when_ another core sees the update
    
- It does **not** guarantee _ordering_ between different variables
    
- It does **not** guarantee program correctness
    

This leads to the key rule:

> **Cache coherence guarantees eventual agreement, not program correctness**

---

## What “Eventual Agreement” Actually Means

“Eventual agreement” means:

- At time **t1**, a core might read an **old value**
    
- At time **t2**, all cores will finally agree on the same value
    
- But your program might already have made a **wrong decision**
    

Yes — **you can read the wrong value temporarily**, and that is allowed.

---

## 🔴 Example Problem: Producer–Consumer Bug

### What the programmer wants

One thread (producer):

```js
data = 42;
ready = 1;

```

Another thread (consumer):

```js
while (ready === 0) {}
console.log(data);

```

The programmer assumes:

> “If `ready` is 1, then `data` must already be 42.”

### What actually happens on real CPUs

- `ready = 1` becomes visible first
    
- `data = 42` is still sitting in a store buffer
    
- Consumer sees:
    
    - `ready === 1`
        
    - `data === 0` ❌
        

The program **breaks**, even though:

- Cache coherence is working
    
- No data is corrupted
    
- Everything will be correct _eventually_
    

But **eventually is too late**.

---

## Why Cache Coherence Allows This Bug

Because:

- `data` and `ready` are different memory locations
    
- Coherence only tracks **single locations**
    
- It does **not enforce ordering between them**
    

The CPU is allowed to say:

> “I’ll show `ready` now and `data` later.”

---

## 🟢 Solution: Atomics Create Ordering and Visibility

Atomics are **not just about atomicity**.

They enforce **two critical guarantees**:

1. **Visibility** – writes become visible to other cores
    
2. **Ordering** – writes happen in the correct sequence
    

---

## ✔️ Fixed Version Using Atomics

Producer:

```js
Atomics.store(shared, DATA, 42);
Atomics.store(shared, READY, 1);

```

Consumer:

```js
while (Atomics.load(shared, READY) === 0) {}
console.log(Atomics.load(shared, DATA));

```

### What atomics guarantee here

If the consumer sees:

`READY === 1`

Then the CPU guarantees:

`DATA === 42`

No guessing. No timing accidents. No “eventually”.

---

## Why Atomics Work (Intuition)

Atomics tell the CPU:

> “Do not reorder this.  
> Do not delay visibility.  
> Make this globally observable now.”

They **flush store buffers**, synchronize caches, and enforce **happens-before rules**.

---

## Mental Model to Remember

- **Cache coherence** prevents memory from becoming garbage
    
- **Atomics** make multithreaded programs correct
    
- Coherence = _agreement_
    
- Atomics = _coordination_
    

Or simply:

> Cache coherence keeps memory sane.  
> Atomics make concurrency safe.

---

## Final Takeaway

Without atomics:

- Programs _might work_
    
- Bugs appear randomly
    
- Failures are impossible to reproduce
    

With atomics:

- Visibility is guaranteed
    
- Ordering is guaranteed
    
- Correctness is enforced
    

This is why **every real concurrent system** — databases, runtimes, kernels, schedulers — is built on atomics, not hope.