## LEVEL 1 — `java.lang` (Primitive Threads & Locks)

This level gives you **raw execution + mutual exclusion**.  
No scheduling policy, no pooling, no safety nets.

Think: **“I own the thread. I own the problem.”**

---

## 1️⃣ `Thread` — The Execution Unit

**What it represents**

- A **single path of execution**
    
- Backed by **one OS thread** (platform thread)
    

**Responsibilities**

- Thread lifecycle (new → runnable → running → terminated)
    
- Naming, priority, daemon flag
    
- Interrupt signaling
    

**What it does NOT do**

- No reuse
    
- No coordination
    
- No backpressure
    
- No structured ownership
    

**Mental model**

> `Thread` is a **container for execution**, not a concurrency strategy.

---

## 2️⃣ `Runnable` — The Work

**What it is**

- A **task**, not a thread
    
- Stateless intent: “run this code”
    

**Why it exists**

- Separates **what runs** from **how it runs**
    
- Enables reuse of logic across different execution models
    

**Key insight**

> `Runnable` is **behavior**, `Thread` is **mechanism**.

Everything in higher levels (`Executor`, virtual threads, pools) still consumes `Runnable`.

---

## 3️⃣ `ThreadGroup` — Legacy Grouping (Mostly Obsolete)

**Original idea**

- Group threads for:
    
    - Bulk interrupt
        
    - Security boundaries
        
    - Hierarchical organization
        

**Reality today**

- Largely obsolete
    
- Poor isolation
    
- Weak control semantics
    

**Why it still exists**

- Backward compatibility
    
- JVM internals
    
- Some diagnostics
    

**Senior rule**

> Don’t design systems around `ThreadGroup`.

Structured concurrency replaces this idea cleanly.

---

## 4️⃣ `Object` Monitor — Intrinsic Locking

This is the **lock that started it all**.

Every Java object has:

- A **monitor**
    
- A **wait set**
    

Used via:

- `synchronized`
    
- `wait / notify / notifyAll`
    

### What the monitor provides

- **Mutual exclusion** (only one thread enters)
    
- **Happens-before guarantees**
    
- **Condition waiting**
    

### What it costs

- Blocking
    
- Context switches
    
- Risk of deadlocks
    
- Poor composability
    

### Why it still matters

- `synchronized` is **fast and optimized**
    
- Used heavily inside JDK
    
- Forms the base of higher-level locks
    

**Mental model**

> Object monitors are **coarse, safe, and blunt instruments**.

---

## How these pieces fit together

```js
Runnable  →  Thread  →  OS Thread
                │
                ▼
          Object Monitor
          (synchronized)

```

- `Runnable` defines **what**
    
- `Thread` defines **where**
    
- `Object` monitor defines **who may enter**
    

---

## What LEVEL 1 does NOT give you

❌ No pooling  
❌ No task queues  
❌ No cancellation semantics  
❌ No structured lifetimes  
❌ No scalability guarantees

That’s why **LEVEL 2 exists**.

---

## When LEVEL 1 is appropriate (realistically)

- JVM internals
    
- Teaching / learning
    
- Very small tools
    
- Understanding deadlocks, memory visibility
    
- Debugging concurrency bugs
    

**Not** for large systems.

---

## One-sentence takeaway

> LEVEL 1 gives you **threads and locks**, but no **policy** — every mistake is yours.