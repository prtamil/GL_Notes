# 4. Thread-Per-Request / Blocking I/O

**(Classic Java, Apache prefork, traditional C/C++)**

---

### **Scheduler**

**How it works:**  
The operating system schedules each thread preemptively.

**Mechanisms:**

- OS kernel scheduler
- Thread priorities
- Context switching
    

**Failure mode if mishandled:**  
High thread counts degrade performance due to overhead.

**Key idea:**  
Scheduler is OS-managed; threads are heavy.

---

### **I/O Multiplexing**

**How it works:**  
Each thread blocks directly on I/O; no multiplexing is needed.

**Mechanisms:**

- Blocking system calls
- Dedicated thread per request
    

**Failure mode if mishandled:**  
Threads pile up under load, causing exhaustion.

**Key idea:**  
Each thread handles its own blocking.

---

### **Backpressure**

**How it works:**  
Backpressure occurs accidentally when threads or memory resources are exhausted.

**Mechanisms:**

- Implicit via thread or memory limits
- OS-enforced queues
    

**Failure mode if mishandled:**  
Uncontrolled load crashes the server.

**Key idea:**  
Backpressure is accidental, not intentional.

---

### **Execution Unit**

**How it works:**  
OS threads execute request-handling code.

**Mechanisms:**

- Kernel threads
- Dedicated stack per thread
    

**Failure mode if mishandled:**  
Expensive context switching and thread leaks.

**Key idea:**  
Threads are heavy; execution is isolated per thread.

---

### **Memory Ownership & Sharing**

**How it works:**  
Threads share the same address space.

**Mechanisms:**

- Shared heap
- Synchronization primitives (mutexes, semaphores)
    

**Failure mode if mishandled:**  
Data races and memory corruption.

**Key idea:**  
Shared memory requires explicit synchronization.

---

### **Blocking Semantics**

**How it works:**  
Blocking is the default and blocks the executing thread.

**Mechanisms:**

- Blocking I/O calls
- Synchronous locks
    

**Failure mode if mishandled:**  
Blocking threads exhaust CPU and memory.

**Key idea:**  
Blocking is normal but expensive.

---

### **Failure Isolation**

**How it works:**  
Threads run in a shared process; one thread can affect others.

**Mechanisms:**

- Shared heap
- Exceptions propagate if uncaught
    

**Failure mode if mishandled:**  
One thread corrupts global state or crashes the process.

**Key idea:**  
Isolation is weak; all threads share fate.

---

### **Fairness & Starvation Prevention**

**How it works:**  
OS scheduler attempts fairness among threads.

**Mechanisms:**

- Preemptive time slicing
- Priority-based scheduling
    

**Failure mode if mishandled:**  
Heavy contention leads to starvation.

**Key idea:**  
Fairness depends on the OS.

---

### **Ordering & Consistency Guarantees**

**How it works:**  
Execution order is governed by locks and critical sections.

**Mechanisms:**

- Mutexes, semaphores
- Condition variables
    

**Failure mode if mishandled:**  
Deadlocks or race conditions.

**Key idea:**  
Consistency requires careful synchronization.

---

### **Resource Bounding**

**How it works:**  
Threads and memory are limited by the OS.

**Mechanisms:**

- Thread count limits
- Stack size limits
- File descriptor limits
    

**Failure mode if mishandled:**  
Hitting limits collapses the system.

**Key idea:**  
Resource limits are critical.

---

> **Core idea:** Simple mental model but poor scalability.

---

