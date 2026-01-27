# Distributed Systems — Architect Study Sequence

## LEVEL 0 — The Mental Model (do this once)

**Goal:** Accept uncertainty as a first-class property.

Internalize:

- The network lies
    
- Time is relative
    
- Failure is normal
    
- Humans are part of the system
    

If you don’t accept this, everything after feels like hacks.

**Read**

- _Designing Data-Intensive Applications_ — Martin Kleppmann
    
    - Chapter 1: _Reliable, Scalable, Maintainable Applications_
        
- _The Eight Fallacies of Distributed Computing_ — Peter Deutsch (short, must-read)
    


**Outcome**  
You stop expecting certainty from distributed systems.


---

## LEVEL 1 — Time & Ordering (start here)

**Why first?**  
If you don’t understand time, _nothing else is coherent_.

Study in this order:

1. No global clock problem
    
2. Happens-before relationship
    
3. Logical clocks (Lamport)
    
4. Causal ordering
    
5. Why wall clocks fail (clock skew, drift)
    


**Read**

- _Designing Data-Intensive Applications_
    
    - Chapter 8: _The Trouble with Distributed Systems_
        
    - Chapter 9 (time-related sections)
        
- Leslie Lamport — _Time, Clocks, and the Ordering of Events in a Distributed System_
    
- _Distributed Systems_ — Maarten van Steen & Andrew Tanenbaum
    
    - Logical clocks section

**Focus**

- Happens-before
    
- Logical vs physical time
    
- Causality > timestamps
    

**Outcome**  
You can explain why “first” is often undefined.

---

## LEVEL 2 — Communication Semantics

**Why now?**  
Once time is unclear, communication becomes ambiguous.

Study:

1. Message loss, duplication, reordering
    
2. Request–response ambiguity
    
3. Delivery guarantees
    
4. Idempotency as a design primitive
    
5. Retries and retry storms
    

**Read**

- _Designing Data-Intensive Applications_
    
    - Chapter 4: _Encoding and Evolution_
        
- _Enterprise Integration Patterns_ — Hohpe & Woolf
    
    - Messaging guarantees
        
- _Distributed Systems_ — Tanenbaum
    
    - Communication failures & models
        

**Focus**

- Message loss, duplication, reordering
    
- Delivery guarantees
    
- Idempotency
    

**Outcome**  
You understand why exactly-once is mostly a lie.


---

## LEVEL 3 — Failure & Uncertainty

**Why here?**  
Failure is _observed_ through communication.

Study:

1. Partial failure model
    
2. Failure vs slowness
    
3. Timeouts and suspicion
    
4. Failure detectors
    
5. Cascading failures
    
**Read**

- _Release It!_ — Michael Nygard
    
    - Entire book (this is gold)
        
- _Designing Data-Intensive Applications_
    
    - Chapter 8 (failure sections)
        
- _Distributed Systems_ — Tanenbaum
    
    - Failure models
        

**Focus**

- Partial failure
    
- Failure detectors
    
- Timeouts & cascading failures
    

**Outcome**  
You stop asking “why did it fail?” and start asking “how did we misinterpret it?”

---

## LEVEL 4 — Identity & Naming

**Why now?**  
Failure + restart breaks identity.

Study:

1. Node vs process vs incarnation
    
2. Identity reuse problems
    
3. Epochs and generations
    
4. Fencing tokens
    
5. Correlation IDs
    

**Read**

- _Designing Data-Intensive Applications_
    
    - Sections on leader epochs, fencing
        
- _ZooKeeper: Wait-free coordination_ (paper)
    
- _The Part-Time Parliament_ — Leslie Lamport (skim concepts)
    

**Focus**

- Node vs incarnation
    
- Epochs & generations
    
- Fencing tokens
    

**Outcome**  
You understand why zombie nodes exist.

---

## LEVEL 5 — State Placement & Ownership

**Why here?**  
Now that nodes can fail and restart, **who owns data** matters.

Study:

1. Single-writer principle
    
2. Partitioned state
    
3. Replicated state
    
4. Ownership transfer
    
5. Source-of-truth decisions
    

**Read**

- _Designing Data-Intensive Applications_
    
    - Chapter 5: _Replication_
        
    - Chapter 6: _Partitioning_
        
- _Distributed Systems_ — Tanenbaum
    
    - Data placement models
        

**Focus**

- Single-writer principle
    
- Partition ownership
    
- Source of truth
    

**Outcome**  
You can explain who is allowed to mutate what—and why.

---

## LEVEL 6 — State & Consistency

**Why now?**  
Only after ownership is clear does consistency make sense.

Study:

1. Consistency models
    
2. CAP theorem (correctly)
    
3. Quorums
    
4. Eventual consistency mechanics
    
5. Read vs write paths
    

**Read**

- _Designing Data-Intensive Applications_
    
    - Chapter 7: _Transactions_
        
    - Chapter 9: _Consistency and Consensus_
        
- Eric Brewer — _CAP Twelve Years Later_
    
- Amazon Dynamo paper
    

**Focus**

- Consistency models
    
- Quorums
    
- Eventual consistency mechanics
    

**Outcome**  
You stop treating CAP as a slogan.

---

## LEVEL 7 — Coordination & Agreement

**Why now?**  
Agreement is expensive; use it knowingly.

Study:

1. Why agreement is hard
    
2. Leader election
    
3. Consensus guarantees
    
4. Split-brain scenarios
    
5. Configuration changes
    

**Read**

- Raft paper — _In Search of an Understandable Consensus Algorithm_
    
- _Designing Data-Intensive Applications_
    
    - Consensus sections
        
- _Distributed Systems_ — Tanenbaum
    
    - Agreement problems
        

**Focus**

- Leader election
    
- Split-brain
    
- Why consensus doesn’t scale
    

**Outcome**  
You know when _not_ to use consensus.

---

## LEVEL 8 — Progress & Liveness

**Why here?**  
Correct systems can still freeze.

Study:

1. Safety vs liveness
    
2. Deadlock & livelock
    
3. Backpressure
    
4. Load shedding
    
5. Retry collapse
    

**Read**

- _Release It!_ — failure amplification sections
    
- _Designing Data-Intensive Applications_
    
    - Liveness vs safety discussions
        
- Google SRE Book
    
    - Overload & backpressure chapters
        

**Focus**

- Deadlock vs livelock
    
- Backpressure
    
- Load shedding
    

**Outcome**  
You design systems that survive stress, not just correctness tests.


---

## LEVEL 9 — Scalability & Growth

**Why here?**  
Now you know _what_ is expensive—time to avoid it.

Study:

1. Coordination costs
    
2. Sharding strategies
    
3. Data locality
    
4. Hotspots
    
5. Growth failure modes
    

**Read**

- _Designing Data-Intensive Applications_
    
    - Partitioning & scaling chapters
        
- _Scalability Rules_ — Martin Abbott
    
- Google SRE Book
    
    - Scaling patterns
        

**Focus**

- Coordination cost
    
- Hotspots
    
- Data locality
    

**Outcome**  
Scaling becomes a consequence, not a goal.


---

## LEVEL 10 — Observability & Truth

**Why now?**  
Only complex systems need deep observability.

Study:

1. Logs vs metrics vs traces
    
2. Causality reconstruction
    
3. Distributed debugging
    
4. SLOs and error budgets
    
5. Feedback loops
    

**Read**

- Google SRE Book
    
    - Monitoring & observability
        
- _Distributed Systems Observability_ — Cindy Sridharan
    
- OpenTelemetry conceptual docs (concepts only)
    

**Focus**

- Logs vs metrics vs traces
    
- Causality reconstruction
    
- SLOs
    

**Outcome**  
You can explain _what actually happened_, not just guess.

---

## LEVEL 11 — Human & Operational Reality (last, but critical)

**Why last?**  
Humans operate what you designed.

Study:

1. Operational simplicity
    
2. Safe defaults
    
3. Rollbacks & recovery
    
4. Runbooks
    
5. Chaos & failure drills
    

**Read**

- _The Phoenix Project_ (ops mindset)
    
- Google SRE Book
    
    - Incident management
        
- _A Philosophy of Software Design_ — John Ousterhout
    

**Focus**

- Operational simplicity
    
- Safe defaults
    
- Failure drills
    

**Outcome**  
Your designs survive real humans on bad days.

---

## How the Meta Question Fits

At **every level**, ask:

> What does the system sacrifice under stress?

Write the answer down.  
If you didn’t choose, the system will choose for you.

## Cross-Cutting Lens

**Safety vs Liveness**

If you can see this tradeoff everywhere, you’re thinking like an architect.

---

## Suggested Practice Loop (don’t skip)

For each level:

1. Study the concepts
    
2. Pick a real system (Kafka, DB, payment flow)
    
3. Map it to the level’s questions
    
4. Identify the tradeoffs
    

This locks in intuition.

## Strong Recommendation (Don’t Skip)

Keep a **single notebook** (Obsidian fits you well 😉):

For every level:

- One real outage
    
- Which fundamental failed
    
- What tradeoff was accidental
    

This is how intuition compounds.