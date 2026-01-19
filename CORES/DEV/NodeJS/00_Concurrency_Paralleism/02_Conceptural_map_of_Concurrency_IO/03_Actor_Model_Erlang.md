# 3. Actor Model

**(Erlang/OTP, Elixir, Akka)**

---

### **Scheduler**

**How it works:**  
A VM-level scheduler preemptively allocates CPU time to each actor.

**Mechanisms:**

- Reduction-count-based preemption
- Lightweight actor processes
- Internal scheduling by VM
    

**Failure mode if mishandled:**  
Misconfigured scheduling or too many actors can cause latency spikes.

**Key idea:**  
Actors are scheduled independently and preemptively.

---

### **I/O Multiplexing**

**How it works:**  
I/O is handled by dedicated drivers; results are delivered as messages to actors.

**Mechanisms:**

- Asynchronous drivers
- Message delivery queues
- Kernel readiness signals
    

**Failure mode if mishandled:**  
Slow message delivery blocks dependent actors.

**Key idea:**  
I/O is decoupled from actor execution.

---

### **Backpressure**

**How it works:**  
Backpressure emerges naturally as slow consumers’ mailboxes fill up.

**Mechanisms:**

- Mailbox limits
- TCP-level flow control
- Actor messaging patterns
    

**Failure mode if mishandled:**  
Unbounded mailboxes lead to memory exhaustion.

**Key idea:**  
Backpressure is emergent and automatic.

---

### **Execution Unit**

**How it works:**  
Each actor processes messages sequentially in isolation.

**Mechanisms:**

- Per-actor mailbox
- Sequential message handling
- No shared memory
    

**Failure mode if mishandled:**  
Blocking inside an actor delays its own mailbox processing.

**Key idea:**  
Actors are isolated, lightweight, and sequential.

---

### **Memory Ownership & Sharing**

**How it works:**  
Actors do not share memory; all data is copied or moved.

**Mechanisms:**

- Message passing with copies
- Immutable data preferred
    

**Failure mode if mishandled:**  
Passing large data repeatedly increases memory pressure.

**Key idea:**  
No shared memory — copy or move only.

---

### **Blocking Semantics**

**How it works:**  
Blocking inside an actor only affects that actor.

**Mechanisms:**

- `receive` waits for messages
- Blocking is local
    

**Failure mode if mishandled:**  
A blocked actor cannot process its mailbox.

**Key idea:**  
Blocking is cheap and isolated.

---

### **Failure Isolation**

**How it works:**  
Actors fail individually; supervisors handle recovery.

**Mechanisms:**

- Supervision trees
- Crash and restart policies
    

**Failure mode if mishandled:**  
Poor supervision leads to cascading restarts.

**Key idea:**  
Expect failures; recover automatically.

---

### **Fairness & Starvation Prevention**

**How it works:**  
Each actor receives CPU time according to the scheduler.

**Mechanisms:**

- Preemption
- Mailbox processing fairness
    

**Failure mode if mishandled:**  
Actor starvation if scheduling is misconfigured.

**Key idea:**  
VM enforces fairness; no actor monopolizes CPU.

---

### **Ordering & Consistency Guarantees**

**How it works:**  
Messages from a single sender arrive in order; no global ordering.

**Mechanisms:**

- FIFO per sender
- No cross-actor ordering guarantees
    

**Failure mode if mishandled:**  
Assuming global message order leads to bugs.

**Key idea:**  
Ordering is per-sender; consistency is local.

---

### **Resource Bounding**

**How it works:**  
Actors and mailboxes are limited by the VM or supervisor policies.

**Mechanisms:**

- Mailbox size limits
- VM-level safeguards
    

**Failure mode if mishandled:**  
Mailbox overflows or memory exhaustion.

**Key idea:**  
Resources are bounded at the VM/actor level.

---

> **Core idea:** Isolate everything, let failures happen, recover automatically.

---

