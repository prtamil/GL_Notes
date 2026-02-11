# LEVEL 1 — Core Java Threading (`java.lang`)

## Overview (LEVEL 1 in plain terms)

LEVEL 1 is **manual threading using `java.lang` only**.

You explicitly control:

- thread creation via `Thread`
    
- execution via `start()`
    
- coordination via `synchronized`
    
- blocking via `Object.wait()`
    
- waking via `Object.notify()` / `notifyAll()`
    
- shutdown via `Thread.interrupt()`
    

The JVM provides **mechanisms**, not **policies**.

If something breaks, it breaks **silently and legally**.

> LEVEL 1 exists so you understand what _every_ higher-level construct is built on.

---

## 1️⃣ `java.lang.Thread` — Execution Container

### What it represents

- A single **platform thread**
    
- Mapped 1:1 to an OS thread
    

### Core responsibilities (API)

- Lifecycle
    
    - `new Thread(...)`
        
    - `start()`
        
    - `run()`
        
    - termination by return from `run()`
        
- Identity & metadata
    
    - `getName()`, `setName(String)`
        
    - `getId()`
        
    - `getPriority()`, `setPriority(int)`
        
    - `setDaemon(boolean)`
        
- Coordination signals
    
    - `interrupt()`
        
    - `isInterrupted()`
        
    - `interrupted()` (static)
        
- Thread joining
    
    - `join()`
        

### What `Thread` does NOT provide

- No task reuse
    
- No scheduling policy
    
- No ownership hierarchy
    
- No failure propagation
    

> `Thread` is a **container for execution**, not a concurrency model.

---

## 2️⃣ `java.lang.Runnable` — Work Definition

### What it is

- A functional interface:
    
    - `void run()`
        

### Key properties

- Contains **behavior only**
    
- Has **no lifecycle**
    
- Has **no threading semantics**
    

### How it is used

- Passed to:
    
    - `new Thread(Runnable)`
        
- Invoked by:
    
    - `Thread.start()` → internal call to `run()`
        

### Why this separation exists

- Decouples **work** from **execution**
    
- Allows the same logic to run under:
    
    - raw threads
        
    - thread pools
        
    - virtual threads
        

> `Runnable` answers **what to do**, `Thread` answers **where it runs**.

---

## 3️⃣ `java.lang.Object` Monitor — Intrinsic Locking

Every object implicitly owns a **monitor**.

### Locking via `synchronized`

- Entry:
    
    - `synchronized (obj)`
        
    - `synchronized` instance methods
        
    - `synchronized` static methods (class monitor)
        
- Guarantees:
    
    - Mutual exclusion
        
    - Happens-before on monitor exit → entry
        

### Condition waiting (API)

- `Object.wait()`
    
- `Object.notify()`
    
- `Object.notifyAll()`
    

### Rules (non-negotiable)

- Must hold the monitor to call `wait / notify`
    
- `wait()`:
    
    - releases the monitor
        
    - places thread in wait set
        
- `notify()`:
    
    - wakes **one** waiting thread
        
- `notifyAll()`:
    
    - wakes **all** waiting threads
        

### Costs and risks

- Blocking OS threads
    
- Deadlock potential
    
- Missed notifications
    
- Poor composability
    

> Object monitors protect **shared state**, not execution order.

---

## 4️⃣ Thread Interruption — Cooperative Cancellation

### Core API

- `Thread.interrupt()`
    
- `Thread.isInterrupted()`
    
- `Thread.interrupted()` (clears flag)
    

### Behavior

- Sets an **interrupted status flag**
    
- Does **not** stop execution
    
- Certain blocking calls react:
    
    - `Object.wait()`
        
    - `Thread.sleep()`
        
    - `Thread.join()`
        

### Correct usage pattern

- Threads:
    
    - periodically check interruption
        
    - exit voluntarily
        
- Libraries:
    
    - propagate `InterruptedException`
        
    - restore interrupt status if swallowed
        

> Interruption is **polite cancellation**, not forced termination.

---

## How LEVEL 1 pieces connect

`Runnable.run()       ↓ Thread.start()       ↓ OS Thread executes       ↓ synchronized (Object monitor)       ↓ wait() / notify()`

- `Runnable` → behavior
    
- `Thread` → execution
    
- `Object` monitor → mutual exclusion + coordination
    

---

## What LEVEL 1 explicitly does NOT include

❌ `ExecutorService`  
❌ `BlockingQueue`  
❌ `Future` / `CompletableFuture`  
❌ Structured concurrency  
❌ Task cancellation semantics  
❌ Backpressure  
❌ Fair scheduling

Everything must be **hand-designed**.

---

## When LEVEL 1 is the right tool

- Learning and teaching concurrency
    
- JVM and library internals
    
- Debugging race conditions
    
- Understanding deadlocks
    
- Small, controlled experiments
    

Not suitable for large-scale systems.

---

## One-sentence takeaway

> LEVEL 1 (`java.lang`) gives you **threads, monitors, and interrupts** — but no **policy**, no **safety**, and no **forgiveness**.