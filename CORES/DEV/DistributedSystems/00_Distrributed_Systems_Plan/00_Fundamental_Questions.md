## Canonical List (Clean Version)

If I were freezing this as a _foundational charter_, it would be:

1. Time & Ordering
2. Failure & Uncertainty
3. Communication Semantics
4. State & Consistency
5. Coordination & Agreement
6. Progress & Liveness
7. Scalability & Growth
8. Observability & Truth
9. Human & Operational Reality
10. Identity & Naming
11. State Placement & Ownership
    
**Meta Question:**  
What does the system sacrifice under stress?

**Cross-cutting lens:**  
Safety vs Liveness

That’s it. This is _complete_.

# Detail
---
Below is a **concise but deep starter map** for _each_ topic — not noisy, not tool-biased.  
You can treat this as a **mental index** while studying anything in distributed systems.

I’ll keep the structure identical for every item so it’s easy to internalize.

---

## 1. Time & Ordering

**Core Question**  
How do we reason about order and causality without a shared clock?

**Sub-questions**

- What does “first” mean across machines?
- Are wall clocks trustworthy?
- Do we need total order or just causal order?
- Can two events be truly simultaneous?
    

**Leads to**

- Logical clocks (Lamport)
- Vector clocks
- Happens-before relation
- Event time vs processing time
- Ordering guarantees in logs and streams
    

---

## 2. Failure & Uncertainty

**Core Question**  
How should a system behave when some components fail or appear to fail?

**Sub-questions**

- Is a node down or just slow?
- When do we declare failure?
- What is the cost of false positives vs false negatives?
- Can the system heal itself?
    

**Leads to**

- Partial failure model
- Failure detectors
- Heartbeats
- Timeouts & suspicion levels
- Graceful degradation
    

---

## 3. Communication Semantics

**Core Question**  
What guarantees do we make about message delivery and execution?

**Sub-questions**

- Can messages be lost, duplicated, or reordered?
- Did the request execute if no response arrived?
- Who owns retries?
- Are operations idempotent?
    

**Leads to**

- At-most-once / at-least-once / exactly-once semantics
- Idempotency keys
- Retries & backoff
- Duplicate suppression
- Message acknowledgment models
    

---

## 4. State & Consistency

**Core Question**  
What does it mean for distributed state to be “correct”?

**Sub-questions**

- Is strong consistency required?
- Is stale data acceptable?
- For how long can data diverge?
- Who observes inconsistency?
    

**Leads to**

- Consistency models
- CAP theorem
- Quorums
- Eventual consistency
- Read-repair & anti-entropy
    

---

## 5. Coordination & Agreement

**Core Question**  
How do independent nodes agree on decisions?

**Sub-questions**

- Who is allowed to decide?
- How is leadership chosen?
- What happens when leaders fail?
- How do we avoid split-brain?
    

**Leads to**

- Consensus (Raft, Paxos)
- Leader election
- Distributed locks
- Term / epoch concepts
- Configuration agreement
    

---

## 6. Progress & Liveness

**Core Question**  
How do we ensure the system keeps making progress?

**Sub-questions**

- Can the system get stuck?
- Can retries cause collapse?
- Who applies backpressure?
- What happens under overload?
    

**Leads to**

- Liveness vs safety
- Deadlock & livelock
- Backpressure mechanisms
- Load shedding
- Rate limiting
    

---

## 7. Scalability & Growth

**Core Question**  
What breaks first as the system grows?

**Sub-questions**

- Where is coordination centralized?
- Does adding nodes increase contention?
- Is the bottleneck compute, network, or coordination?
- Does performance degrade gracefully?
    

**Leads to**

- Horizontal scaling
- Sharding & partitioning
- Avoiding global coordination
- Data locality
- O(1) vs O(n) coordination costs
    

---

## 8. Observability & Truth

**Core Question**  
How do we know what actually happened?

**Sub-questions**

- Can logs be incomplete or misleading?
- Can metrics lag reality?
- How do we trace causality?
- How do we debug distributed failures?
    

**Leads to**

- Logs vs metrics vs traces
- Correlation IDs
- Distributed tracing
- Event timelines
- SLOs & error budgets
    

---

## 9. Human & Operational Reality

**Core Question**  
How will humans operate and recover this system?

**Sub-questions**

- Can it be debugged at 3am?
- Can changes be rolled back safely?
- Can operators accidentally cause outages?
- Is failure understandable?
    

**Leads to**

- Simplicity bias
- Operational playbooks
- Safe defaults
- Automation vs manual control
- Chaos engineering
    

---

## 10. Identity & Naming

**Core Question**  
How do we uniquely identify entities across space and time?

**Sub-questions**

- What is a node, process, or instance?
- Can identities be reused?
- How do we distinguish old vs new incarnations?
- How do we prevent “zombie” actors?
    

**Leads to**

- UUIDs & monotonic IDs
- Epochs & generations
- Fencing tokens
- Versioned identities
- Request & entity correlation
    

---

## 11. State Placement & Ownership

**Core Question**  
Where does state live, and who is allowed to mutate it?

**Sub-questions**

- Is state centralized, partitioned, or replicated?
- Who is the source of truth?
- Can multiple writers exist?
- How does ownership move during failure?
    

**Leads to**

- Single-writer principle
- Partition leadership
- Shard ownership
- Event sourcing
- Ownership transfer protocols
    

---

## Meta Question (Always Active)

**What does the system sacrifice under stress?**

- Availability?
- Accuracy?
- Latency?
- Freshness?
    

Every distributed system answers this—intentionally or accidentally.

---

## Cross-Cutting Lens

**Safety vs Liveness**

- Safety: nothing bad ever happens
- Liveness: something good eventually happens
    

Every major design choice is a tradeoff between these two.

---

### How to use this

When studying **any system or paper**:

1. Identify which question it answers
2. Identify what it sacrifices
3. Identify where safety or liveness is favored