# Atomics: A Processor-Level Guide (Deep but Simple)

## 1. Why atomics exist (the real problem)

Modern computers do **many things at the same time**:

- Multiple CPU cores
    
- Each core has its own cache
    
- Instructions run out of order
    
- Memory is slow, CPUs are fast
    

The **core problem** is this:

> Multiple cores accessing the same memory can see **different realities** at the same time.

Without special rules:

- Updates can be lost
    
- Reads can see stale data
    
- Operations can appear reordered
    

Atomics exist to **create small islands of truth** in this chaos.

---

## 2. What “atomic” really means (no buzzwords)

An atomic operation guarantees **three things**:

1. **Indivisible**  
    The operation happens all at once — no halfway state.
    
2. **Visible**  
    Other cores will see the result.
    
3. **Ordered (when required)**  
    Certain operations cannot move before or after it.
    

That’s it.  
Everything else is built on top of these three promises.

---

## 3. Why normal reads and writes are not enough

Consider this simple code:

`x = x + 1`

At the processor level, this is **not one step**:

1. Load `x` from memory
    
2. Add 1
    
3. Store result back
    

If two cores do this at the same time:

- Both may read the same value
    
- One update gets lost
    

This is not a bug — this is how CPUs work.

---

## 4. Caches: helpful but dangerous

Each CPU core has:

- L1 / L2 cache
    
- Store buffers
    
- Speculative execution
    

Cache coherence (like MESI):

- Keeps cache lines consistent
    
- **Does NOT guarantee ordering**
    
- **Does NOT guarantee correctness**
    

Key rule:

> Cache coherence guarantees _eventual agreement_, not _program correctness_.

Atomics are what turn coherence into correctness.

---

## 5. Atomic LOAD (read)

### What it does

Reads a memory location:

- As one unit (no tearing)
    
- From a coherent cache state
    

### What it guarantees

- You get a valid value
    
- Not half old / half new
    

### What it does NOT guarantee

- That other memory locations are up to date
    
- That earlier writes from another core are visible
    

### Use cases

- Reading flags
    
- Checking state
    
- Observing progress
    

---

## 6. Atomic STORE (write)

### What it does

Writes a value:

- As one indivisible action
    
- Updates the cache line
    
- Invalidates other cores’ caches
    

### Important detail: store buffers

Stores may:

- Sit in a buffer
    
- Become visible later
    
- Be seen out of order by other cores
    

### Use cases

- Publishing a value
    
- Releasing a lock
    
- Signaling completion
    

---

## 7. Atomic ADD (read-modify-write)

### What it does

Atomically:

1. Reads a value
    
2. Modifies it
    
3. Writes it back
    

All as **one operation**.

### Why this matters

You **cannot** build this safely from load + store.

### Hardware reality

- CPU locks the cache line
    
- No other core can modify it during the operation
    

### Use cases

- Counters
    
- Reference counting
    
- Statistics
    

---

## 8. Compare-And-Swap (CAS) — the most important one

### What it does

CAS means:

> “Only update if nobody else changed it.”

Pseudocode:

```js
if (*addr == expected)
    *addr = new
return old

```

### Why CAS is powerful

With CAS, you can:

- Detect interference
    
- Retry safely
    
- Avoid locks
    

### What CAS enables

- Spinlocks
    
- Mutexes
    
- Lock-free stacks
    
- Lock-free queues
    
- State machines
    

Almost all modern concurrency is built on CAS.

---

## 9. Atomic EXCHANGE (swap)

### What it does

Replaces a value and returns the old one — atomically.

### Use cases

- Simple locks
    
- Ownership transfer
    
- Hand-off patterns
    

---

## 10. Memory ordering (the part that hurts)

CPUs and compilers reorder instructions to go faster.

So this code:

```js
write A
write B

```

May be observed as:

```js
B first, then A

```

This is legal.

### Atomics introduce ordering rules:

- Some operations prevent reordering
    
- Some create _happens-before_ relationships
    

Without ordering:

- Programs work “most of the time”
    
- Fail under pressure
    
- Fail on ARM but not x86
    

---

## 11. What atomics do NOT do

Atomics are **not magic**.

They do NOT:

- Make your whole program thread-safe
    
- Protect multiple variables automatically
    
- Replace good design
    
- Eliminate races by themselves
    

They are **sharp tools**.

---

## 12. What we can build using atomics

With just:

- atomic load
    
- atomic store
    
- atomic add
    
- CAS
    

We can build:

- Mutexes
    
- Semaphores
    
- Condition variables
    
- Thread pools
    
- Work queues
    
- Schedulers
    
- Lock-free data structures
    

Operating systems rely on these exact primitives.

---

## 13. What we’ve achieved so far (important checkpoint)

At this point, you now understand:

- Why atomics exist
    
- Why caches alone are not enough
    
- Why races happen
    
- Why reordering is real
    
- Why CAS is the foundation
    
- Why high-level locks exist
    

This is **systems-level understanding**, not application-level.

You are no longer guessing.

---

## 14. The correct mental model (keep this)

> **Atomics are small, carefully guarded moments where the CPU promises to behave predictably**

Everything else is built around those moments.