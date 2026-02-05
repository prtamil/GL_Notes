# **Concurrency Bug Patterns & Failure Modes (A–F)**

---

## **A. Safety & Correctness — Bug Patterns**

### **Critical Section**

**Smell**

- State changes unexpectedly between nearby lines
    
- Fixing one bug causes another to appear close by
    
- Values look correct sometimes, wrong at other times
    

**Look for**

- Read–modify–write sequences split across functions
    
- Early returns, error paths, exceptions
    
- Helper functions called inside/outside lock inconsistently
    

**Ask**

- What exact state must be atomic?
    
- Can another thread observe this halfway?
    

---

### **Mutual Exclusion**

**Smell**

- Code “mostly works” but breaks under load
    
- Rare corruption even though locks exist
    
- Bugs vanish when everything is synchronized
    

**Look for**

- Multiple locks protecting the same data
    
- Lock taken in some paths but not others
    
- Conditional locking (“only lock sometimes”)
    

**Ask**

- Is there exactly one authority protecting this state?
    
- Can two threads enter logically exclusive paths?
    

---

### **Race Condition**

**Smell**

- Behavior changes with logging or debug prints
    
- Same input produces different outputs
    
- Bugs only appear in production
    

**Look for**

- Timing-dependent logic
    
- Assumptions about execution order
    
- Use of sleep/yield to “fix” behavior
    

**Ask**

- Does correctness depend on timing?
    
- What happens if threads run in a different order?
    

---

### **Data Race**

**Smell**

- Completely impossible states appear
    
- Crashes or corruption without clear cause
    
- Different behavior on different machines
    

**Look for**

- Shared variables accessed without synchronization
    
- Non-atomic reads/writes
    
- “It’s just a boolean / int” assumptions
    

**Ask**

- Is every access coordinated?
    
- Does the memory model allow this access?
    

---

### **Thread Safety**

**Smell**

- Works fine in isolation, fails when reused
    
- Bugs depend on usage pattern
    
- “Thread-safe” label doesn’t hold in practice
    

**Look for**

- Hidden shared state
    
- Static or global variables
    
- Objects escaping before fully initialized
    

**Ask**

- What assumptions does this code make about callers?
    
- Is safety documented or accidental?
    

---

### **Atomicity**

**Smell**

- Partial updates observed
    
- Counters drift or go negative
    
- Invariants break briefly
    

**Look for**

- Compound operations assumed atomic
    
- Multiple fields updated independently
    
- Check-then-act logic
    

**Ask**

- What must happen as one indivisible step?
    
- Can another thread observe intermediate state?
    

---

### **Consistency**

**Smell**

- State looks valid individually but wrong together
    
- Rare violations without crashes
    
- “Impossible” combinations appear
    

**Look for**

- Related fields updated separately
    
- Invariants enforced only at boundaries
    
- Missing validation under concurrency
    

**Ask**

- What rules must _always_ hold together?
    
- Can updates interleave and violate them?
    

---

### **Invariant**

**Smell**

- Debug assertions fail sporadically
    
- Invariants only broken under load
    
- Hard-to-reproduce correctness bugs
    

**Look for**

- Invariants maintained across multiple steps
    
- Invariant checks outside synchronization
    
- Partial rollback paths
    

**Ask**

- When is this invariant allowed to be false?
    
- Can another thread observe that moment?
    

---

### **Linearizability**

**Smell**

- APIs return surprising results
    
- Operations appear to “jump back in time”
    
- Users can’t reason about order
    

**Look for**

- Operations with unclear commit point
    
- State updates split across locks
    
- Visibility without atomicity
    

**Ask**

- Where is the single point of effect?
    
- Can I place each operation on a timeline?
    

---

## **B. Memory & Visibility — Bug Patterns**

### **Visibility**

**Smell**

- Threads never see updates
    
- Flags appear stuck
    
- Restart fixes the issue
    

**Look for**

- Unsynchronized shared flags
    
- Busy-wait loops
    
- Missing volatile/atomic semantics
    

**Ask**

- What guarantees visibility here?
    
- Could this value stay cached forever?
    

---

### **Happens-Before**

**Smell**

- Initialization races
    
- Reads see default values
    
- Ordering assumptions fail
    

**Look for**

- Missing synchronization edges
    
- Hand-off without barriers
    
- Unsafe publication
    

**Ask**

- What establishes ordering?
    
- Is there a happens-before edge at all?
    

---

### **Memory Ordering**

**Smell**

- Works on x86, breaks elsewhere
    
- Rare, architecture-specific bugs
    
- Reordering surprises
    

**Look for**

- Lock-free code without fences
    
- Assumptions about load/store order
    
- Weak memory platforms
    

**Ask**

- What ordering is required for correctness?
    
- Is it actually enforced?
    

---

### **Reordering**

**Smell**

- Observing future state before past state
    
- “Impossible” read combinations
    
- Debugging changes behavior
    

**Look for**

- Writes assumed to be seen in order
    
- Missing barriers
    
- Instruction-level assumptions
    

**Ask**

- Could the compiler/CPU reorder this?
    
- What prevents it?
    

---

### **Sequential Consistency**

**Smell**

- Code matches intuition but fails
    
- Developers say “this should work”
    
- Rare and confusing bugs
    

**Look for**

- Assuming global order implicitly
    
- Missing synchronization
    
- Weak guarantees
    

**Ask**

- Is sequential consistency guaranteed here?
    
- Or just assumed?
    

---

### **Out-of-Order Execution**

**Smell**

- Startup/shutdown bugs
    
- Partial initialization observed
    
- Time-dependent failures
    

**Look for**

- Reads before writes logically
    
- Unsafe publication
    
- Missing barriers around lifecycle
    

**Ask**

- Could execution be reordered internally?
    
- Where is ordering forced?
    

---

### **Memory Model**

**Smell**

- Code “works” but isn’t legal
    
- Compiler upgrades break behavior
    
- Platform-specific bugs
    

**Look for**

- Undefined behavior
    
- Relying on undocumented guarantees
    
- Mixing models incorrectly
    

**Ask**

- What does the memory model actually promise?
    
- Is this code legal under it?
    

---

### **Safe Publication**

**Smell**

- Null fields in constructed objects
    
- Half-initialized state observed
    
- Rare startup crashes
    

**Look for**

- Objects shared without synchronization
    
- Escaping `this` in constructors
    
- Lazy initialization bugs
    

**Ask**

- How does another thread first see this object?
    
- Is publication synchronized?
    

---

## **C. Progress & Liveness — Bug Patterns**

### **Deadlock**

**Smell**

- System freezes completely
    
- Threads waiting forever
    
- Only restart helps
    

**Look for**

- Lock ordering cycles
    
- Nested locks
    
- Blocking calls under locks
    

**Ask**

- What is each thread waiting for?
    
- Is there a cycle?
    

---

### **Livelock**

**Smell**

- High CPU, no progress
    
- Constant retries
    
- System looks alive but useless
    

**Look for**

- Retry loops
    
- Backoff logic
    
- Mutual avoidance behavior
    

**Ask**

- Are threads helping or fighting each other?
    
- Is progress guaranteed?
    

---

### **Starvation**

**Smell**

- Some tasks never run
    
- Latency spikes for specific threads
    
- Priority imbalance
    

**Look for**

- Unfair locks
    
- Priority scheduling
    
- Resource hoarding
    

**Ask**

- Can this thread be postponed forever?
    
- Who dominates resources?
    

---

### **Fairness**

**Smell**

- Long-tail latency
    
- Uneven throughput
    
- Some users always slow
    

**Look for**

- Non-fair locks
    
- Greedy scheduling
    
- Work stealing imbalance
    

**Ask**

- Is fairness required here?
    
- Or is throughput more important?
    

---

### **Progress Guarantees**

**Smell**

- System stalls on single-thread failure
    
- Cascading pauses
    
- Fragile recovery
    

**Look for**

- Blocking designs
    
- Single points of progress
    
- Global locks
    

**Ask**

- What happens if one thread stops?
    
- Does the system still move forward?
    

---

### **Blocking vs Non-Blocking**

**Smell**

- Latency spikes under load
    
- Thread pile-ups
    
- Timeout storms
    

**Look for**

- Blocking I/O under locks
    
- Long critical sections
    
- Synchronous waits
    

**Ask**

- Can one thread block others?
    
- Is blocking acceptable here?
    

---

### **Lock-Freedom**

**Smell**

- System progresses but some threads starve
    
- Unpredictable fairness
    
- Hard-to-debug retries
    

**Look for**

- CAS retry loops
    
- Busy spinning
    
- Weak guarantees
    

**Ask**

- Is system-wide progress enough?
    
- Or do all threads matter?
    

---

### **Wait-Freedom**

**Smell**

- Extremely complex code
    
- High overhead
    
- Rare but strong guarantees
    

**Look for**

- Bounded retries
    
- Per-thread progress guarantees
    
- Heavy algorithmic machinery
    

**Ask**

- Is wait-freedom truly required?
    
- Or is it overkill?
    

---

## **D. Synchronization Abstractions — Bug Patterns**

### **Monitor**

**Smell**

- Code feels safe but still deadlocks
    
- Waiting threads never wake
    
- Misused wait/notify
    

**Look for**

- Waiting without loops
    
- Signaling wrong condition
    
- Holding lock while blocking
    

**Ask**

- What condition am I waiting for?
    
- Is it rechecked after wakeup?
    

---

### **Thread Confinement**

**Smell**

- Random crashes after refactor
    
- “It was safe before”
    
- Data suddenly shared
    

**Look for**

- References escaping
    
- Callbacks crossing threads
    
- Shared caches
    

**Ask**

- Is this data truly confined?
    
- Where did it escape?
    

---

### **Ownership**

**Smell**

- Nobody knows who updates state
    
- Defensive locking everywhere
    
- Over-synchronization
    

**Look for**

- Multiple writers
    
- No clear owner
    
- Shared mutable state
    

**Ask**

- Who owns this data?
    
- Who is allowed to mutate it?
    

---

### **Serialization**

**Smell**

- System is correct but slow
    
- Throughput collapses under load
    
- Long queues
    

**Look for**

- Single-thread executors
    
- Global locks
    
- Serialized pipelines
    

**Ask**

- Is serialization intentional?
    
- Can it be relaxed safely?
    

---

### **Resource Sharing**

**Smell**

- Resource exhaustion
    
- Throttling bugs
    
- Cascading failures
    

**Look for**

- Unbounded pools
    
- Missing quotas
    
- Leaked resources
    

**Ask**

- What limits resource usage?
    
- What happens under exhaustion?
    

---

### **Coordination Abstractions**

**Smell**

- Threads wait forever
    
- Barrier never trips
    
- Startup hangs
    

**Look for**

- Wrong participant counts
    
- Missed arrivals
    
- Reused one-shot primitives
    

**Ask**

- Who is expected to arrive?
    
- Can arrival be missed?
    

---

## **E. Synchronization Intent & Rules — Bug Patterns**

### **Coordination Intent**

**Smell**

- Threads disagree on protocol
    
- Partial execution
    
- Phase mismatches
    

**Look for**

- Implicit assumptions
    
- Undocumented protocols
    
- Ad-hoc coordination
    

**Ask**

- What is the coordination contract?
    
- Is it enforced or assumed?
    

---

### **Signaling Rules**

**Smell**

- Missed wakeups
    
- Spurious hangs
    
- Notifications ignored
    

**Look for**

- Signal-before-wait
    
- Missing condition loops
    
- Incorrect predicates
    

**Ask**

- What exactly does this signal mean?
    
- Is the condition rechecked?
    

---

### **Ordering Constraints**

**Smell**

- Use-before-init crashes
    
- Startup races
    
- Shutdown corruption
    

**Look for**

- Missing barriers
    
- Initialization split across threads
    
- Weak lifecycle control
    

**Ask**

- What must happen first?
    
- How is that enforced?
    

---

## **F. Execution & Scheduling — Bug Patterns**

### **Concurrency**

**Smell**

- Bugs disappear when single-threaded
    
- Nondeterministic failures
    
- Heisenbugs
    

**Look for**

- Shared mutable state
    
- Implicit assumptions
    
- Missing synchronization
    

**Ask**

- What changes when concurrency is enabled?
    
- Is state truly independent?
    

---

### **Parallelism**

**Smell**

- Performance worse with more cores
    
- Lock contention
    
- Cache thrashing
    

**Look for**

- False sharing
    
- Over-parallelization
    
- Contended locks
    

**Ask**

- Is this actually parallelizable?
    
- Where is contention?
    

---

### **Preemption**

**Smell**

- Rare mid-operation failures
    
- Interrupted assumptions
    
- Timing sensitivity
    

**Look for**

- Non-atomic sequences
    
- Blocking calls
    
- Unsafe interruption
    

**Ask**

- What if this thread is paused here?
    
- Is state still valid?
    

---

### **Context Switching**

**Smell**

- High CPU, low throughput
    
- Latency spikes
    
- Scheduler overhead
    

**Look for**

- Excessive threads
    
- Blocking synchronization
    
- Fine-grained locks
    

**Ask**

- How often do threads block?
    
- Can work be batched?
    

---

### **Scheduling Policies**

**Smell**

- Priority inversion
    
- Starvation
    
- Unpredictable latency
    

**Look for**

- Priority misuse
    
- OS vs runtime mismatch
    
- Scheduler assumptions
    

**Ask**

- What policy is actually in effect?
    
- Does it match expectations?
    

---

### **Oversubscription**

**Smell**

- System slows under load
    
- Thrashing
    
- Queue buildup
    

**Look for**

- Too many threads
    
- Blocking workloads
    
- CPU saturation
    

**Ask**

- How many threads should exist?
    
- Are they mostly runnable or blocked?
    

---

### **Work Stealing**

**Smell**

- Uneven performance
    
- Hard-to-reproduce bugs
    
- Task migration surprises
    

**Look for**

- Shared mutable task state
    
- Assumptions about thread locality
    
- Hidden parallelism
    

**Ask**

- Can tasks safely move threads?
    
- Is state thread-affine?