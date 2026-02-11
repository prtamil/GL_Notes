# **The Five Core Responsibilities of Distributed Systems**

### _How systems stay sane when work is split across machines_

_(Authority • Ownership • Coordination • Time • Failure)_

Distributed systems are not defined by networks, servers, or APIs.  
They are defined by the **responsibilities a system must explicitly take on once work is split across independent actors**.

In a monolith, these responsibilities are implicit.  
In a distributed system, they must be **designed, enforced, and paid for**.

Everything else is machinery.

---

## I. The Five Core Responsibilities

These are **non-negotiable obligations**.  
Every distributed system must answer them explicitly, or it will fail implicitly.

Each responsibility defines:

- what the system promises
    
- where coordination is required
    
- what breaks under stress
    

---

## 1️⃣ Authority — _Who is allowed to decide?_

### Responsibility

Define who is permitted to make decisions that change system state.

### Why this responsibility exists

Without explicit authority, every change requires everyone to agree — which does not scale.

### Common authority models

- Single leader (one boss)
    
- Elected leader (democracy with rules)
    
- Lease-based authority (temporary ownership)
    
- Multi-authority (commutative state, CRDTs)
    

### Failure symptoms when unclear

- Split brain
    
- Conflicting writes
    
- Endless retries and rollbacks
    

### 🏦 Global Finance View

Who is allowed to decide:

- Can a **customer** move money directly?
    
- Can a **bank** debit an account unilaterally?
    
- Can a **clearing house** finalize settlement?
    
- Can a **central bank** reverse transactions?
    

If two banks both believe they finalized the same transfer → **double spending**.  
If _every_ bank must approve _every_ transaction → **the economy stops**.

👉 **Authority answers: “Whose decision is final?”**

---

## 2️⃣ Ownership — _Who is responsible for what?_

### Responsibility

Assign clear responsibility for subsets of state, resources, or work.

### Why this responsibility exists

Ownership bounds failure and limits coordination.  
Without it, every problem becomes global.

### Common ownership models

- Key ownership (databases)
    
- Partition ownership (logs, streams)
    
- Resource ownership (controllers)
    
- Time-based ownership (leases, epochs)
    

### Failure symptoms when unclear

- Hot spots
    
- Cascading failures
    
- Unbounded coordination
    

### 🏦 Global Finance View

Each bank owns:

- its customer accounts
    
- its internal ledger
    
- its fraud checks
    
- its risk exposure
    

A corrupted ledger in **Bank A** must **not** corrupt **Bank B**.

👉 **Ownership answers: “Who is on the hook when this breaks?”**

---

## 3️⃣ Coordination Boundaries — _Who must agree before progress is allowed?_

### Responsibility

Explicitly define the **minimum set of actors** that must coordinate for correctness.

### Why this responsibility exists

Correctness requires agreement.  
Scalability requires **minimizing** agreement.

### Common coordination patterns

- Single owner (no coordination)
    
- Quorum-based agreement
    
- Best-effort (eventual)
    
- Convergent models
    

### Failure symptoms when oversized

- Latency spikes
    
- Throughput collapse
    
- Deadlocks and convoying
    

### 🏦 Global Finance View

To move money:

- Does only the **sender’s bank** need to approve?
    
- Does the **receiver’s bank** need to confirm?
    
- Is a **clearing house** required?
    
- Is settlement delayed but guaranteed?
    

If _every_ transfer required _all_ banks to agree, global payments would halt.

👉 **Coordination boundaries answer: “Who must say yes before money moves?”**

---

## 4️⃣ Time & Ordering — _What must happen before what?_

### Responsibility

Define what ordering guarantees exist between events.

### Why this responsibility exists

There is no shared clock.  
Assuming “real time” causes subtle corruption.

### Common ordering models

- Total order (expensive)
    
- Per-key / per-partition order
    
- Causal order
    
- No order (commutative operations)
    

### Failure symptoms when wrong

- Lost updates
    
- Stale reads
    
- Inconsistent views across clients
    

### 🏦 Global Finance View

In banking:

- Authorization happens before settlement
    
- Settlement happens before reconciliation
    
- Reversals happen after posting
    

But across banks:

- messages arrive late
    
- settlements batch overnight
    
- reconciliation lags reality
    

👉 **Time & ordering answer: “Which sequence actually matters for correctness?”**

---

## 5️⃣ Failure Model — _What can go wrong, and what cannot?_

### Responsibility

Explicitly state which failures are expected and handled.

### Why this responsibility exists

Systems that assume the wrong failure model fail catastrophically.

### Common failure assumptions

- Crash-stop
    
- Network partitions
    
- Partial failures
    
- Byzantine (rare, costly)
    

### Failure symptoms when mismatched

- Silent corruption
    
- Data loss
    
- Global outages
    

### 🏦 Global Finance View

Banks **expect**:

- network outages
    
- delayed settlements
    
- retry storms
    
- partial system downtime
    

Banks **do not accept**:

- silent money creation
    
- disappearing transactions
    
- ledger corruption
    

👉 **Failure model answers: “What disasters are survivable vs unacceptable?”**

---

## II. The 15 Fundamental Questions (Universal Decoder)

_When you encounter **any** distributed system, ask these — in order._

### A. Authority & Ownership

1. Who has authority to mutate state?
    
2. Is authority exclusive or shared?
    
3. What exactly is owned (keys, time, resources, tasks)?
    
4. How is ownership assigned, transferred, and revoked?
    

### B. Coordination & Scale

5. Who must agree for a change to be valid?
    
6. Is coordination synchronous or asynchronous?
    
7. Which operations avoid coordination entirely?
    

### C. Time & Consistency

8. What ordering guarantees exist?
    
9. What happens when messages are delayed or reordered?
    
10. What consistency model is exposed to users?
    

### D. Failure & Recovery

11. What failures are assumed possible?
    
12. How is authority recovered after failure?
    
13. How does the system prevent split brain?
    

### E. Boundaries & Costs

14. Which operations are intentionally expensive or forbidden?
    
15. Where is complexity pushed — user or system?
    

If you can answer these fifteen, you understand the system.

---

## III. Apply Once — Kafka

|Responsibility|Kafka|
|---|---|
|Authority|Partition leader|
|Ownership|Partition|
|Coordination boundary|ISR quorum|
|Ordering|Per-partition|
|Failure model|Crash-stop|

Kafka scales because **coordination never crosses partitions**.

🏦 _Banking view:_  
Each account ledger has one authoritative writer; accounts don’t coordinate.

---

## IV. Apply Once — Kubernetes

|Responsibility|Kubernetes|
|---|---|
|Authority|Controller leader|
|Ownership|Resource kind / namespace|
|Coordination|etcd transactions|
|Ordering|Per-resource|
|Failure model|Node & network failure|

🏦 _Banking view:_  
Policy is centralized; execution is local; failures are routine.

---

## V. The Unifying Law

**Distributed systems scale by converting global problems into many local ones.**

They do this by:

- assigning authority
    
- partitioning ownership
    
- shrinking coordination boundaries
    
- relaxing ordering guarantees
    
- choosing a realistic failure model
    

---

## VI. Mental One-Liners

- Authority decides.
    
- Ownership contains blast radius.
    
- Coordination limits scale.
    
- Ordering defines correctness.
    
- Failure defines reality.
    

Everything else is implementation.

---

## Final Takeaway

Authority, ownership, and coordination boundaries are the **core responsibilities**.  
Time/ordering and failure model make them **work in the real world**.

With these five responsibilities and fifteen questions, you now have a **systems-level lens**.

You won’t memorize tools anymore.  
You’ll **recognize architectures** — the same way you understand how the global financial system actually works.