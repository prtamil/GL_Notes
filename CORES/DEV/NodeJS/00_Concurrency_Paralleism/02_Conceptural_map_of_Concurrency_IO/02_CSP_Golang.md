# 2. Communicating Sequential Processes (CSP)

**(Go — goroutines + channels)**

---

### **Scheduler**

**How it works:**  
The Go runtime schedules goroutines preemptively across OS threads.

**Mechanisms:**

- M:N scheduler
- Time slicing
- Work stealing
    

**Failure mode if mishandled:**  
Runaway goroutines overwhelm the scheduler.

**Key idea:**  
The runtime owns scheduling.

---

### **I/O Multiplexing**

**How it works:**  
Goroutines perform blocking I/O; the runtime parks and resumes them.

**Mechanisms:**

- Blocking syscalls
- Network poller
- Scheduler-aware I/O
    

**Failure mode if mishandled:**  
Excessive blocking goroutines increase memory pressure.

**Key idea:**  
Blocking is hidden, not eliminated.

---

### **Backpressure**

**How it works:**  
Senders block naturally when channels are full.

**Mechanisms:**

- Buffered channels
- Blocking send/receive
    

**Failure mode if mishandled:**  
Unbuffered channels cause deadlocks.

**Key idea:**  
Backpressure is implicit.

---

### **Execution Unit**

**How it works:**  
Each task runs in a goroutine.

**Mechanisms:**

- Lightweight stacks
- Runtime-managed lifecycle
    

**Failure mode if mishandled:**  
Goroutine leaks.

**Key idea:**  
Goroutines are cheap — not free.

---

### **Memory Ownership & Sharing**

**How it works:**  
Memory is shared, but best practice discourages mutation.

**Mechanisms:**

- Shared heap
- Channel-based communication
    

**Failure mode if mishandled:**  
Data races and subtle corruption.

**Key idea:**  
Share memory by communicating.

---

### **Blocking Semantics**

**How it works:**  
Blocking pauses only the goroutine.

**Mechanisms:**

- Scheduler parking
- Safe blocking points
    

**Failure mode if mishandled:**  
Deadlocks.

**Key idea:**  
Blocking is safe.

---

### **Failure Isolation**

**How it works:**  
Panics crash the process unless recovered.

**Mechanisms:**

- `panic` / `recover`
    

**Failure mode if mishandled:**  
Whole-program termination.

**Key idea:**  
Isolation is weak by default.

---

### **Fairness & Starvation Prevention**

**How it works:**  
Scheduler preempts long-running goroutines.

**Mechanisms:**

- Time slicing
- Preemption points
    

**Failure mode if mishandled:**  
Busy loops reduce fairness.

**Key idea:**  
Fairness is enforced.

---

### **Ordering & Consistency Guarantees**

**How it works:**  
Channel operations define happens-before relationships.

**Mechanisms:**

- FIFO channels
- Memory barriers
    

**Failure mode if mishandled:**  
Assuming ordering across channels.

**Key idea:**  
Channels define consistency.

---

### **Resource Bounding**

**How it works:**  
Channels and worker pools bound concurrency.

**Mechanisms:**

- Buffered channels
- Semaphore patterns
    

**Failure mode if mishandled:**  
Unbounded goroutine growth.

**Key idea:**  
Leaks are the real danger.

---

> **Core idea:** Let the runtime manage concurrency; embrace blocking.

---
---

