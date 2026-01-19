# 1. Event-Driven, Non-Blocking I/O

**(Reactor Pattern — Node.js, libuv, asyncio)**

---
### **Scheduler**

**How it works:**  
A single event loop executes all user code cooperatively. Code runs only when the call stack is empty and must voluntarily yield.

**Mechanisms:**

- Single-threaded event loop
- Phase-based scheduling (timers, poll, check)
- No preemption inside user code
    

**Failure mode if mishandled:**  
Long-running handlers monopolize the loop and stall all progress.

**Key idea:**  
Scheduling is cooperative — _you must behave_.

---

### **I/O Multiplexing**

**How it works:**  
The kernel notifies the runtime when file descriptors are ready; JavaScript runs only after readiness is signaled.

**Mechanisms:**

- `epoll`, `kqueue`, IOCP
- Readiness-based polling
- libuv abstraction
    

**Failure mode if mishandled:**  
Assuming I/O completion instead of readiness leads to stalled callbacks or busy looping.

**Key idea:**  
The kernel decides _when_ work may proceed.

---

### **Backpressure**

**How it works:**  
Producers must be manually slowed when consumers fall behind.

**Mechanisms:**

- Stream pause/resume
- High-water marks
- Explicit queue management
    

**Failure mode if mishandled:**  
Unbounded buffering causes memory growth or event loop starvation.

**Key idea:**  
Backpressure is explicit and developer-owned.

---

### **Execution Unit**

**How it works:**  
Work executes as callbacks, promise jobs, or microtasks on the same thread.

**Mechanisms:**

- Callback queue
- Promise microtask queue
- `process.nextTick`
    

**Failure mode if mishandled:**  
Microtask abuse can starve I/O phases entirely.

**Key idea:**  
Execution units are cheap — but not isolated.

---

### **Memory Ownership & Sharing**

**How it works:**  
All code shares a single heap; buffers are passed by reference.

**Mechanisms:**

- Shared JS heap
- Reference-passed objects
- Closure retention
    

**Failure mode if mishandled:**  
Accidental memory retention and leaks via closures.

**Key idea:**  
Everything is shared unless you’re careful.

---

### **Blocking Semantics**

**How it works:**  
Blocking the thread blocks the entire system.

**Mechanisms:**

- Sync I/O
- CPU-heavy loops
- Native blocking calls
    

**Failure mode if mishandled:**  
Total application freeze.

**Key idea:**  
Blocking is catastrophic.

---

### **Failure Isolation**

**How it works:**  
All tasks run in the same process and thread.

**Mechanisms:**

- Single process
- Uncaught exception handling
    

**Failure mode if mishandled:**  
One crash kills all in-flight work.

**Key idea:**  
Failure isolation is minimal.

---

### **Fairness & Starvation Prevention**

**How it works:**  
Fairness depends on handlers yielding promptly.

**Mechanisms:**

- Cooperative scheduling
- Phase ordering
    

**Failure mode if mishandled:**  
One handler starves all others.

**Key idea:**  
Fairness is voluntary.

---

### **Ordering & Consistency Guarantees**

**How it works:**  
Execution order is deterministic per event loop iteration.

**Mechanisms:**

- FIFO queues
- Microtasks always run before next phase
    

**Failure mode if mishandled:**  
Misunderstanding microtask priority causes unexpected ordering.

**Key idea:**  
Order is strict — but subtle.

---

### **Resource Bounding**

**How it works:**  
The runtime provides few hard limits; developers must enforce them.

**Mechanisms:**

- Manual queue limits
- Connection caps
- Buffer sizing
    

**Failure mode if mishandled:**  
Memory exhaustion under load.

**Key idea:**  
Nothing is bounded unless you do it.

---

> **Core idea:** Maximum flexibility, maximum responsibility.

---

