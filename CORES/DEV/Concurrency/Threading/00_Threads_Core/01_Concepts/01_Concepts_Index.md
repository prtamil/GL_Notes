
# **Concurrency Fundamentals — Super-Glance Index (Concepts Only)**

---

## **A. Safety & Correctness Concepts**

1. **Critical Section**
    
2. **Mutual Exclusion**
    
3. **Race Condition**
    
4. **Data Race**
    
5. **Thread Safety**
    
6. **Atomicity**
    
7. **Consistency**
    
8. **Invariant**
    
9. **Linearizability**
    


---

## **B. Memory & Visibility Concepts**

1. **Visibility**
    
2. **Happens-Before**
    
3. **Memory Ordering**
    
4. **Reordering**
    
5. **Sequential Consistency**
    
6. **Out-of-Order Execution**
    
7. **Memory Model**
    
8. **Safe Publication** 
    


---

## **C. Progress & Liveness Concepts**

1. **Deadlock**
    
2. **Livelock**
    
3. **Starvation**
    
4. **Fairness**
    
5. **Progress Guarantees** 
    
6. **Blocking vs Non-Blocking**
    
7. **Lock-Freedom**
    
8. **Wait-Freedom**
    



---

## **D. Synchronization Abstractions (Structured Coordination)**

These are **reusable abstractions that enforce intent** using primitives.

1. **Monitor**
    
2. **Thread Confinement**
    
3. **Ownership**
    
4. **Serialization**
    
5. **Resource Sharing** _(Pools, Quotas)_
    
6. **Coordination Abstractions** _(Barriers, Latches)_ 
    


---

## **E. Synchronization Intent & Rules**

These are **policies and ordering rules**, not structures.

1. **Coordination Intent** 
    
2. **Signaling Rules**
    
3. **Ordering Constraints**
    

These answer:

> _“What must happen before what?”_

---

## **F. Execution & Scheduling Concepts**

1. **Concurrency**
    
2. **Parallelism**
    
3. **Preemption**
    
4. **Context Switching**  
    
5. **Scheduling Policies**  
    
6. **Oversubscription**
    
7. **Work Stealing**
    



---

## **Ultra-Short Mental Anchor (refined)**

- **Safety** → correctness of state
    
- **Memory** → visibility & ordering
    
- **Liveness** → progress guarantees
    
- **Abstractions** → structured safety
    
- **Intent** → coordination rules
    
- **Execution** → scheduling reality