# **11 Natural Forces of Distributed Systems**

### _(The realities you cannot escape once systems are split)_

Distributed systems don’t fail because engineers are bad.  
They fail because **these forces exist whether you like them or not**.

You don’t “choose” them.  
You **design around them**.

---

## 1️⃣ Time & Ordering

**Force:** There is no single clock, and events don’t arrive in order.

**In simple words**  
Different machines don’t agree on _when_ something happened.

**Why this matters**  
If you assume time is shared, your system slowly corrupts itself.

**Banking example 🏦**

- Bank A sends money at 10:01
    
- Bank B receives it at 10:05
    
- Clearing system settles at midnight
    

Which happened “first”?  
➡️ Banks rely on **process order**, not wall clocks.

---

## 2️⃣ Failure & Uncertainty

**Force:** You can’t tell if something is dead or just slow.

**In simple words**  
Silence does not mean failure.

**Why this matters**  
Wrong assumptions cause retries, duplicates, or split-brain.

**Banking example 🏦**

- Did the transfer fail?
    
- Or did the confirmation message get delayed?
    

➡️ Banks **assume uncertainty** and design retries + reconciliation.

---

## 3️⃣ Communication Semantics

**Force:** Messages can be lost, duplicated, or reordered.

**In simple words**  
Talking is unreliable.

**Why this matters**  
“Did it happen once or twice?” becomes a real question.

**Banking example 🏦**

- Payment instruction sent twice
    
- Bank must not debit twice
    

➡️ Transactions are **idempotent** and have unique IDs.

---

## 4️⃣ State & Consistency

**Force:** Copies of data diverge.

**In simple words**  
Not everyone sees the same truth at the same time.

**Why this matters**  
You must decide what “correct” means.

**Banking example 🏦**

- Your app shows ₹10,000
    
- Bank backend shows ₹9,500 (pending debit)
    

➡️ Temporary inconsistency is allowed, **eventual correctness is mandatory**.

---

## 5️⃣ Coordination & Agreement

**Force:** Agreement is slow and expensive.

**In simple words**  
The more people who must agree, the slower things get.

**Why this matters**  
Unlimited agreement kills scale.

**Banking example 🏦**

- Local transfer: only your bank decides
    
- International transfer: sender bank + receiver bank + clearing house
    

➡️ Coordination scope is **kept minimal on purpose**.

---

## 6️⃣ Progress & Liveness

**Force:** Systems can stop making progress even if nothing is “broken”.

**In simple words**  
Everyone waits, nothing moves.

**Why this matters**  
Safety alone can freeze the system.

**Banking example 🏦**

- Fraud check too strict
    
- All payments blocked “just in case”
    

➡️ Banks balance **risk vs forward movement**.

---

## 7️⃣ Scalability & Growth

**Force:** What works for 10 nodes breaks at 10,000.

**In simple words**  
Growth exposes hidden bottlenecks.

**Why this matters**  
Central decisions don’t scale.

**Banking example 🏦**

- One bank manager approving every transaction ❌
    
- Automated rules + limits ✅
    

➡️ Authority is **pushed outward**, not centralized.

---

## 8️⃣ Observability & Truth

**Force:** You never see the full picture.

**In simple words**  
Dashboards lie by omission.

**Why this matters**  
Debugging becomes archaeology.

**Banking example 🏦**

- Ledger says settled
    
- Customer says failed
    
- Clearing house says pending
    

➡️ Truth is reconstructed **after the fact**.

---

## 9️⃣ Human & Operational Reality

**Force:** Humans make mistakes under pressure.

**In simple words**  
People are part of the system.

**Why this matters**  
Perfect systems fail when humans touch them.

**Banking example 🏦**

- Operator runs wrong reconciliation job
    
- Millions temporarily mismatched
    

➡️ Systems must be **operable, reversible, and boring**.

---

## 🔟 Identity & Naming

**Force:** Things don’t stay unique forever.

**In simple words**  
Names get reused, machines restart, people change.

**Why this matters**  
Old messages can affect new actors.

**Banking example 🏦**

- Account number reused after closure
    
- Old transaction arrives late
    

➡️ Banks use **epochs, IDs, and versioning**.

---

## 1️⃣1️⃣ State Placement & Ownership

**Force:** Someone must own the truth.

**In simple words**  
Shared ownership creates chaos.

**Why this matters**  
Without ownership, everyone argues.

**Banking example 🏦**

- Your bank owns your balance
    
- Clearing house owns settlement
    
- Central bank owns final authority
    

➡️ Single owner per responsibility.

---

# 🧠 Meta Question (Always Ask)

**What does the system sacrifice under stress?**

- Availability?
    
- Accuracy?
    
- Speed?
    
- Freshness?
    

Banks often sacrifice **speed** to preserve **correctness**.

---

# ⚖️ Cross-Cutting Lens: Safety vs Liveness

- **Safety:** No money created or lost
    
- **Liveness:** Payments eventually complete
    

Every banking system chooses a balance.  
Every distributed system does the same.

---

## How to Use This Mental Model

When you see **any system** (Kafka, MongoDB, Kubernetes, Payments):

1. Identify which forces dominate
    
2. See how responsibilities counter them
    
3. Observe what is sacrificed under stress
    

If you can do that, **you understand the system**.