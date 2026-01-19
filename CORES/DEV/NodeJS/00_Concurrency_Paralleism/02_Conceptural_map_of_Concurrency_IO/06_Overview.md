- 🟢 **Developer**
    
- 🔵 **Runtime / Scheduler**
    
- 🟡 **VM / Actor system**
    
- 🟠 **OS / Kernel**
    
- 🟣 **Protocol / Framework**
    

---

|Concept|Node.js / Event Loop|Go / CSP|Actor Model|Thread-per-Request|Reactive Streams|
|---|---|---|---|---|---|
|**Scheduler**|🟢 Developer (cooperative)|🔵 Runtime|🟡 VM|🟠 OS|🔵 Framework|
|**I/O Multiplexing**|🟠 OS signals readiness|🔵 Runtime hides blocking|🟡 VM drivers|🟠 OS blocks|🔵 Framework delegates|
|**Backpressure**|🟢 Manual|🔵 Channels block implicitly|🟡 Mailboxes / TCP flow|🟠 Accidental via thread/memory|🟣 Demand protocol|
|**Execution Unit**|🟢 Callback / microtask|🔵 Goroutine|🟡 Actor|🟠 OS thread|🔵 Stream stage|
|**Memory Ownership & Sharing**|🟢 Shared heap|🟢 Shared, communicate by convention|🟡 Copy/move only|🟢 Shared, locks|🟣 Immutable / bounded|
|**Blocking Semantics**|🟢 Catastrophic|🔵 Goroutine-local|🟡 Actor-local|🟠 Thread blocks|🟣 Pull/push hybrid|
|**Failure Isolation**|🟠 Process-level|🔵 Weak, panic|🟡 Strong, supervision trees|🟢 Weak|🟣 Stream-level|
|**Fairness & Starvation**|🟢 Cooperative|🔵 Scheduler|🟡 VM|🟠 OS|🟣 Slow consumers control flow|
|**Ordering & Consistency**|🟢 Event-loop deterministic|🔵 Channels FIFO|🟡 Sender FIFO|🟢 Locks / synchronization|🟣 Stream-local deterministic|
|**Resource Bounding**|🟢 Manual (buffers, queues)|🔵 Channels / pools|🟡 Mailbox / VM|🟠 Threads, stack, FDs|🟣 Built-in via flow limits|

---

### Visual takeaway:

- **Developer-heavy responsibility:** Node.js, Threads
- **Runtime-managed:** Go, Reactive Streams
- **VM-enforced isolation:** Actor Model
- **OS-level enforcement:** Threads, Node.js I/O readiness
- **Protocol-driven flow:** Reactive Streams