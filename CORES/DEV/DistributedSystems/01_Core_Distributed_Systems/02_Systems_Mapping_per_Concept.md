# System Mappings per Concept

```txt
Ordering → Invariants → Resolution
   ↑                         ↓
   └── Reconciliation loop ──┘
```

---

## 1️⃣ Ordering — where agreement is created

|System|Where ordering lives|What is ordered|
|---|---|---|
|**Kafka**|Partition leader|Records within a partition|
|**Raft**|Leader log|Log entries|
|**Kubernetes**|etcd (per object)|Resource versions|
|**Databases (SQL)**|WAL / transaction log|Row mutations|
|**NoSQL (Cassandra)**|Per-partition coordinator|Writes per partition|
|**Event sourcing**|Aggregate stream|Domain events|
|**Zookeeper / KRaft**|ZNode / metadata log|Metadata updates|

**Mechanisms**

- Leader-based serialization
    
- Log append
    
- Compare-and-set
    
- Versioned writes
    

**Mental check**

> _What is the smallest scope that agrees on order?_

---

## 2️⃣ Invariants — what must never be broken

|System|Core invariants|
|---|---|
|**Kafka**|One leader per partition; committed offsets monotonic|
|**Raft**|Single leader; log matching; committed entries durable|
|**Kubernetes**|Desired state = spec; at-most-one owner|
|**Databases**|Constraints (PK, FK, UNIQUE); atomic commit|
|**Cassandra**|Tunable consistency guarantees|
|**CRDTs**|Convergence without coordination|
|**Queues**|At-most / at-least / exactly-once semantics|

**Invariant types**

- Safety properties
    
- Cardinality
    
- Monotonicity
    
- Ownership
    
- Uniqueness
    

**Mental check**

> _If everything goes wrong, what must still be true?_

---

## 3️⃣ Resolution — how violations are handled

|System|Resolution strategy|
|---|---|
|**Kafka**|Retry fetch; truncate logs; rebalance consumers|
|**Raft**|Reject stale leaders; overwrite follower logs|
|**Kubernetes**|Restart pods; reschedule; recreate resources|
|**Databases**|Abort / retry transactions|
|**Cassandra**|Read repair; hinted handoff|
|**CRDTs**|Merge functions|
|**APIs**|Idempotent retries; deduplication|

**Common tools**

- Retry with backoff
    
- Merge
    
- Abort / reject
    
- Compensating actions
    
- Fencing tokens
    

**Mental check**

> _When invariants are threatened, what safe move is allowed?_

---

## 4️⃣ Reconciliation — who keeps fixing things

|System|Reconciliation loop|
|---|---|
|**Kafka**|Controller, ISR manager, rebalance protocol|
|**Raft**|Leader heartbeats; log replication|
|**Kubernetes**|Controllers (deployment, node, scheduler)|
|**Databases**|Replication repair; background compaction|
|**Cassandra**|Anti-entropy repair|
|**CRDTs**|Gossip + merge|
|**Cloud infra**|Health checks + auto-healing|

**Patterns**

- Observe / compare / act
    
- Background workers
    
- Control loops
    
- Periodic repair
    

**Mental check**

> _What runs forever to push the system back to correctness?_

---

## 5️⃣ One-system walkthrough (Kafka example)

|Concept|Kafka mapping|
|---|---|
|Ordering|Partition leader assigns log order|
|Invariants|One leader; committed messages immutable|
|Resolution|Retry fetch; leader election; truncation|
|Reconciliation|Controller & background replication|

Ask these four questions and Kafka _stops being magical_.

---

## 6️⃣ One-system walkthrough (Kubernetes example)

|Concept|Kubernetes mapping|
|---|---|
|Ordering|etcd resource versions|
|Invariants|Spec = desired state|
|Resolution|Create / delete / reschedule|
|Reconciliation|Controllers looping forever|

This is why Kubernetes is declarative — reconciliation is the point.

---

## 7️⃣ Universal debugging checklist (use this in real life)

When a distributed system misbehaves, ask:

1. **Ordering**
    
    - What scope is ordered?
        
    - Is ordering being violated or assumed?
        
2. **Invariants**
    
    - Which invariant is broken?
        
    - Is it actually defined?
        
3. **Resolution**
    
    - What action is taken?
        
    - Is it idempotent?
        
4. **Reconciliation**
    
    - Who detects drift?
        
    - How often is repair attempted?
        

If you can’t answer one — that’s the bug.

---

## Final lock-in sentence

> **Every distributed system is a set of local orders protecting global invariants through continuous reconciliation.**