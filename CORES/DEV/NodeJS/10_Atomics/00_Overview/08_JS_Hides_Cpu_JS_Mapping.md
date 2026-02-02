# What JavaScript Hides and the CPU → JS Mapping

JavaScript provides **shared memory primitives** through `SharedArrayBuffer` and `Atomics`, but it deliberately **hides some low-level details** to make multithreaded programming safe and predictable. Understanding what is exposed — and what is hidden — helps us reason about concurrency in JS without falling into common pitfalls.

---

## 1. What JavaScript Hides on Purpose

JavaScript **does not expose** certain CPU-level memory features:

- **Relaxed atomics**  
    Operations with weak ordering semantics are **not available** in JS. Every atomic operation is **sequentially consistent**.
    
- **Weak memory ordering**  
    JS avoids letting developers reason about complex CPU-level ordering like acquire/release or memory fences.
    
- **Manual memory fences**  
    You cannot insert custom CPU barriers — JS handles memory visibility for you.
    

### Why this matters

Exposing these features would introduce:

1. **Architecture-specific bugs**  
    Code might behave differently on x86 vs ARM due to different reordering rules.
    
2. **Non-reproducible failures**  
    Subtle timing bugs would appear intermittently, making debugging nearly impossible.
    
3. **Undefined behavior**  
    Reads and writes could see inconsistent or partial values without strong guarantees.
    

> In short, JS **trades maximum performance for safety and predictability**.

---

## 2. CPU → JS Mapping — The Minimal Interface

JavaScript exposes **exactly the atomic operations needed** to build correct concurrent programs. Nothing more. Nothing less.

|CPU concept|JavaScript primitive|
|---|---|
|Atomic load|`Atomics.load`|
|Atomic store|`Atomics.store`|
|Read-Modify-Write|`Atomics.add`, `Atomics.sub`, `Atomics.and`, `Atomics.or`, `Atomics.xor`|
|Compare-And-Swap|`Atomics.compareExchange`|
|Exchange (swap)|`Atomics.exchange`|
|Futex-style wait|`Atomics.wait`|
|Futex-style wake|`Atomics.notify`|

### Key points

1. **One-to-one mapping** from CPU primitives to JS atomics
    
    - JS wraps **real CPU atomic instructions** safely.
        
2. **No relaxed modes or fences**
    
    - Sequential consistency is guaranteed for all atomics.
        
3. **Safety first**
    
    - Developers don’t have to reason about cache lines, store buffers, or memory fences.
        
    - Programs remain correct across all CPU architectures.
        

---

## 3. Putting It Together

JavaScript atomics are **designed for correctness and simplicity**:

- They **expose exactly what you need** to build locks, queues, counters, and condition variables.
    
- They **hide everything unsafe** — relaxed operations, weak ordering, manual fences.
    
- Each operation maps cleanly to a CPU-level primitive, but JS adds **guardrails** like sequential consistency.
    

> Think of it as a **safe subset of CPU atomics**: powerful enough to build multithreaded programs, but safe enough for ordinary JS developers to use without risking undefined behavior.

---

✅ **Takeaway**

JS developers don’t need to become CPU architects to write safe multithreaded code. With `Atomics`:

1. You have a **minimal, precise set of atomic operations**.
    
2. JS **handles memory ordering and visibility** for you.
    
3. You can focus on **algorithms and coordination**, not CPU-level subtleties.