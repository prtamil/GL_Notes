# **Concurrency Fundamentals — Concept Overviews (Aligned to Super-Glance Index)**

---

## **A. Safety & Correctness — Overviews**

### **Critical Section**

A critical section is a part of code where shared data is accessed and **things can go wrong if two threads execute it at the same time**. It exists to protect correctness, not performance. If operations inside interleave, updates can be lost or state can become invalid. You should be able to clearly identify it and say: “only one thread may execute this at once.”

### **Mutual Exclusion**

Mutual exclusion is the **rule that enforces safety** for critical sections. It guarantees that at most one thread can enter a sensitive region at any time. This is a logical requirement, not a specific mechanism. If mutual exclusion fails, correctness breaks even if the code looks right.

### **Race Condition**

A race condition occurs when a program’s behavior depends on **timing rather than logic**. The same input may produce different results depending on thread scheduling. These bugs often disappear when logging or debugging is added, making them hard to reproduce. If timing affects correctness, you have a race.

### **Data Race**

A data race is a specific and dangerous race where multiple threads access the same memory without coordination and at least one access is a write. Many languages define this as undefined behavior. Once a data race exists, crashes, corruption, or impossible states can occur.

### **Thread Safety**

Thread safety means code **continues to behave correctly when accessed by multiple threads simultaneously**. This includes preserving invariants, visibility, and correctness—not just avoiding crashes. Thread safety is contextual: a component can be safe in one usage and unsafe in another. It is a contract between the code and its users.

### **Atomicity**

Atomicity means an operation appears to happen **all at once** from the perspective of other threads. No thread can observe intermediate states. Atomic operations simplify reasoning because partial updates effectively do not exist. Bugs appear when developers assume atomicity where it is not guaranteed.

### **Consistency**

Consistency means shared data always follows the system’s logical rules. Even under concurrency, the system must never enter an invalid or contradictory state. Many concurrency bugs violate consistency without crashing. If invariants are broken—even briefly—consistency is broken.

### **Invariant**

An invariant is a condition that must **always hold true** for the system state. Concurrency makes invariants fragile because updates can interleave. Most correctness reasoning in concurrent systems is about ensuring invariants are never observable as false. Breaking an invariant means breaking correctness.

### **Linearizability**

Linearizability means each operation appears to take effect at a single instant in time. Even when operations overlap, behavior looks as if they ran one by one in some order. This makes concurrent APIs predictable and easier to reason about. Without it, users observe surprising results.

---

## **B. Memory & Visibility — Overviews**

### **Visibility**

Visibility answers the question: “When one thread writes data, when will another thread see it?” CPUs and compilers cache aggressively, so writes are not automatically visible. Without explicit guarantees, threads may read stale values indefinitely. Many production bugs come from incorrect visibility assumptions.

### **Happens-Before**

Happens-before is the formal rule that guarantees **both ordering and visibility** between operations. If A happens-before B, then B must observe A’s effects. This relationship is the foundation for reasoning safely about concurrent code. Without it, visibility is not guaranteed.

### **Memory Ordering**

Memory ordering defines how reads and writes may be reordered by the compiler or CPU. Program order is not execution order. Strong ordering is easier to reason about but slower; weak ordering is faster but dangerous without discipline. Many low-level concurrency bugs are ordering bugs.

### **Reordering**

Reordering occurs when instructions are rearranged to improve performance while preserving single-thread correctness. This breaks assumptions in multithreaded code. Many “impossible” states are caused by reordering. Synchronization exists largely to prevent harmful reorderings.

### **Sequential Consistency**

Sequential consistency is the intuitive model where all operations appear to execute in one global order. Most programmers assume this model, but many systems do not provide it by default. Assuming sequential consistency when it isn’t guaranteed leads to rare and confusing failures.

### **Out-of-Order Execution**

Out-of-order execution allows CPUs to execute instructions as soon as their inputs are ready. This greatly improves performance but complicates visibility and ordering guarantees. Synchronization forces order only where correctness requires it. Startup and shutdown bugs often stem from this behavior.

### **Memory Model**

The memory model defines what concurrency behavior is guaranteed and what is undefined. Correct concurrent code must follow the memory model—not intuition. Many bugs exist because developers rely on behaviors the model explicitly does not promise.

### **Safe Publication**

Safe publication ensures objects are fully constructed before being accessed by other threads. Without it, threads may observe partially initialized state. Constructors alone are not enough. Many mysterious null values and crashes come from unsafe publication.

---

## **C. Progress & Liveness — Overviews**

### **Deadlock**

Deadlock occurs when threads wait on each other in a cycle and none can proceed. The system becomes permanently stuck unless externally interrupted. Logic may be correct, but progress halts completely. Deadlocks often appear only under specific timing conditions.

### **Livelock**

Livelock happens when threads remain active but make no progress. They continuously react to each other and retry. Unlike deadlock, CPU usage is high. The system is busy but ineffective.

### **Starvation**

Starvation occurs when a thread never gets the resources it needs to run. Other threads may continue progressing while one is indefinitely delayed. This often results from unfair scheduling or priority imbalance.

### **Fairness**

Fairness determines whether all threads eventually get a chance to run. Without fairness, some work may never execute even though the system is alive. Fairness trades throughput for predictability.

### **Progress Guarantees**

Progress guarantees describe whether the system continues moving forward under contention. Blocking designs can halt if a thread stalls. Non-blocking designs ensure progress even when some threads fail or pause.

### **Blocking vs Non-Blocking**

Blocking means one thread can prevent others from making progress. Non-blocking designs ensure system-wide progress regardless of individual thread delays. This distinction is critical for latency-sensitive and fault-tolerant systems.

### **Lock-Freedom**

Lock-free systems guarantee that **some thread** always makes progress. Individual threads may starve, but the system continues moving forward. This improves robustness under failure.

### **Wait-Freedom**

Wait-free systems guarantee that **every thread** completes its operation in a bounded number of steps. This is the strongest progress guarantee and the most difficult to implement.

---

## **D. Synchronization Abstractions (Structured Coordination) — Overviews**

These are **reusable abstractions that enforce intent using primitives**.

### **Monitor**

A monitor combines mutual exclusion and signaling around shared state. It represents structured intent rather than a low-level mechanism. Many languages embed monitors directly to reduce misuse.

### **Thread Confinement**

Thread confinement restricts data access to a single thread. This avoids synchronization entirely. Bugs occur when confined data unintentionally escapes to other threads.

### **Ownership**

Ownership defines which thread or component is allowed to modify a piece of state. Clear ownership simplifies reasoning. Shared ownership dramatically increases complexity and bug risk.

### **Serialization**

Serialization forces operations to occur in a specific order. This simplifies correctness but limits concurrency. Many systems deliberately serialize access to maintain safety.

### **Resource Sharing**

Resource sharing manages access to limited resources such as connections or memory. Without limits, resources are exhausted. Over-restriction reduces throughput and scalability.

### **Coordination Abstractions**

Barriers and latches allow threads to wait for each other at defined points. They express collective coordination intent and prevent ad-hoc waiting logic.

---

## **E. Synchronization Intent & Rules — Overviews**

These are **policies and ordering rules**, not structures.

### **Coordination Intent**

Coordination intent defines how threads are expected to work together. Threads may need to wait, synchronize phases, or combine results. Bugs arise when these assumptions are violated.

### **Signaling Rules**

Signaling allows one thread to notify another about state changes. Correct signaling requires rechecking conditions and avoiding missed signals. Mistakes lead to hangs and lost work.

### **Ordering Constraints**

Ordering constraints ensure certain actions occur before others. Initialization before use is the classic example. Many concurrency bugs come from violated ordering assumptions.

---

## **F. Execution & Scheduling — Overviews**

### **Concurrency**

Concurrency means multiple tasks are in progress at the same time, even if not executing simultaneously. It introduces nondeterminism. Many bugs only appear once concurrency is enabled.

### **Parallelism**

Parallelism means tasks execute simultaneously on multiple cores. It can improve performance but increases contention. Poor parallel design can make systems slower.

### **Preemption**

Preemption allows the OS to interrupt a thread at almost any point. Code must assume it can be paused anywhere. This makes reasoning about shared state harder.

### **Context Switching**

A context switch occurs when the CPU switches from one thread to another. Excessive context switching causes performance collapse. Blocking designs increase context switch frequency.

### **Scheduling Policies**

Scheduling policies determine how CPU time is allocated. Small changes can cause starvation or latency spikes. Schedulers strongly influence concurrency behavior.

### **Oversubscription**

Oversubscription happens when runnable threads exceed available CPU cores. This increases contention and context switching. Throughput often drops sharply.

### **Work Stealing**

Work stealing allows idle threads to take tasks from busy ones. It improves load balance but complicates debugging. Many modern runtimes rely on it internally.