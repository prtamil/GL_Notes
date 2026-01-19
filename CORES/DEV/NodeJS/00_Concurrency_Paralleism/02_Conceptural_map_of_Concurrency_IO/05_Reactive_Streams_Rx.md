# 5. Dataflow / Reactive Streams

**(Reactive Streams, Rx, structured pipelines)**

---

### **Scheduler**

**How it works:**  
Framework controls execution order and concurrency.

**Mechanisms:**

- Framework-managed scheduling
- Often layered over OS threads or event loops
    

**Failure mode if mishandled:**  
Improper scheduler use blocks stages or starves consumers.

**Key idea:**  
Framework orchestrates timing.

---

### **I/O Multiplexing**

**How it works:**  
I/O is handled by the underlying runtime; streams focus on flow.

**Mechanisms:**

- Delegated to Node.js, JVM, or Go runtime
- Pull/push hybrid design
    

**Failure mode if mishandled:**  
Blocking in a stage breaks flow assumptions.

**Key idea:**  
Flow abstraction separates I/O from processing.

---

### **Backpressure**

**How it works:**  
Consumers request only what they can handle.

**Mechanisms:**

- `request(n)` signals
- Bounded buffers
- Flow control protocol
    

**Failure mode if mishandled:**  
Ignoring demand leads to overflow or high latency.

**Key idea:**  
Backpressure is built into the protocol.

---

### **Execution Unit**

**How it works:**  
Each stream stage processes data as items flow through.

**Mechanisms:**

- Operators or stages
- Declarative pipeline nodes
    

**Failure mode if mishandled:**  
Blocking or slow stages propagate delays downstream.

**Key idea:**  
Declarative, demand-driven execution units.

---

### **Memory Ownership & Sharing**

**How it works:**  
Data between stages is usually immutable.

**Mechanisms:**

- Bounded buffers
- Immutable or copy-on-write objects
    

**Failure mode if mishandled:**  
Excessive buffering increases latency and memory usage.

**Key idea:**  
Memory is controlled and predictable.

---

### **Blocking Semantics**

**How it works:**  
Most operations are non-blocking; pulling data triggers demand.

**Mechanisms:**

- Pull/push hybrid
- Reactive operators
    

**Failure mode if mishandled:**  
Blocking a stage stalls the entire pipeline.

**Key idea:**  
Blocking is avoided; flow dictates progress.

---

### **Failure Isolation**

**How it works:**  
Errors propagate along stream stages.

**Mechanisms:**

- Stream-level error handling
- Operator error propagation
    

**Failure mode if mishandled:**  
Unhandled errors terminate the stream.

**Key idea:**  
Failures are scoped to the stream graph.

---

### **Fairness & Starvation Prevention**

**How it works:**  
Slow consumers control the pace; demand-driven scheduling prevents starvation.

**Mechanisms:**

- Pull-based backpressure
- Buffering and stage coordination
    

**Failure mode if mishandled:**  
Ignoring consumer demand stalls the pipeline.

**Key idea:**  
Slow consumers dictate speed.

---

### **Ordering & Consistency Guarantees**

**How it works:**  
Data flows deterministically through each stage.

**Mechanisms:**

- Per-stage ordering
- Sequential propagation
    

**Failure mode if mishandled:**  
Assuming cross-stream ordering breaks correctness.

**Key idea:**  
Order is local to each pipeline.

---

### **Resource Bounding**

**How it works:**  
Buffers and stage limits enforce bounded memory and throughput.

**Mechanisms:**

- Backpressure-aware buffers
- Stage concurrency limits
    

**Failure mode if mishandled:**  
Ignoring bounds causes overflow or memory pressure.

**Key idea:**  
Bounding is intrinsic to the model.

---

> **Core idea:** Declare the flow and let demand control execution.
---
