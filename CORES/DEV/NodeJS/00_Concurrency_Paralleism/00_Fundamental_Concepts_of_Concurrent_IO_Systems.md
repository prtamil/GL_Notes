## Fundamental Concepts of Concurrent I/O Systems

### 1. **Scheduler**

Decides **who runs, when, and for how long**.

- Event loop (Node)
- Goroutine scheduler (Go)
- BEAM scheduler (Erlang)
- OS scheduler (threads)
    

Without a scheduler, concurrency does not exist.

---

### 2. **I/O Multiplexing**

How a system **waits for many I/O sources efficiently**.

- `epoll`, `kqueue`, `IOCP`
- Readiness vs completion
- Polling vs callbacks
    

This determines scalability at the OS boundary.

---

### 3. **Backpressure**

Controls **how fast data is allowed to flow**.

- Explicit (Node streams)
- Implicit (blocking in Go)
- Emergent (Erlang mailboxes)
- Protocol-driven (Reactive Streams)
    

Without backpressure, systems fail under load.

---

### 4. **Execution Unit**

The smallest **independently schedulable entity**.

- Callback
- Task / Future
- Goroutine
- Actor / Process
- OS thread
    

This defines isolation and cost of concurrency.

---

### 5. **Memory Ownership & Sharing**

Who owns data and **how it is shared**.

- Shared memory + locks
- Message passing (copy or move)
- Zero-copy buffers
- Immutable data
    

Most concurrency bugs live here.

---

### 6. **Blocking Semantics**

What happens when work cannot proceed.

- Blocks thread
- Blocks task
- Yields to scheduler
- Suspends process
    

Blocking behavior defines safety and latency.

---

### 7. **Failure Isolation**

How failures are **contained and recovered**.

- Process isolation
- Supervisor trees
- Panic propagation
- Crash-only design
    

This is why Erlang feels “magical”.

---

### 8. **Fairness & Starvation Prevention**

Ensures **no task monopolizes resources**.

- Time slicing
- Priority queues
- Cooperative vs preemptive scheduling
- Yield points
    

This directly impacts tail latency.

---

### 9. **Ordering & Consistency Guarantees**

What ordering the system promises.

- In-order delivery
- Happens-before relationships
- Memory visibility
- Message ordering
    

Concurrency correctness depends on this.

---

### 10. **Resource Bounding**

Hard limits to prevent collapse.

- Buffer sizes
- Max goroutines/processes
- Connection limits
- Rate limiting
    

Backpressure without bounds still fails.

---

## One-sentence unifying truth

> **Concurrency systems exist to schedule work, move data, limit flow, and survive failure — all under finite resources.**

Everything else is surface area.