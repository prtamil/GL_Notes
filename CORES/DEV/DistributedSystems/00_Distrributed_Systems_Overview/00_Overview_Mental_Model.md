# Distributed Systems — A Zero-Level Mental Model

_(Why they exist, what we lose, the forces of reality, and how we survive)_

---

## 1️⃣ Why Distributed Systems Are Needed

### _(Why we leave the monolith)_

**Big idea**  
A monolith is like **one big kitchen with one chef**.

At first:

- food is fast
    
- everything is coordinated
    
- life is easy
    

Then:

- too many orders
    
- chef gets tired
    
- if chef faints → restaurant closed ❌
    

So we build **many kitchens**.

**Why we distribute**

- One machine can’t handle infinite load
    
- One failure shouldn’t kill everything
    
- Users are far away (latency)
    
- Teams grow and need independence
    

👉 **Distributed systems exist because the real world demands scale, availability, and reach.**

---

## 2️⃣ What We Gain and What We Lose

### _(The hidden cost: loss of implicit guarantees)_

### What we gain (the good stuff)

- More machines → more power
    
- Failures don’t kill everything
    
- Faster access via geography
    

Now the **dangerous part** 👇

---

## Implicit Guarantees (What Monoliths Give for Free)

In a monolith, many things “just work” **without you thinking**.

When you distribute, these disappear.

Think of it like **living alone vs living in 10 houses**.

---

### 🧠 Implicit Guarantees — Explained Like You’re 5

1️⃣ **Single Clock**  
⏰ _Everyone agrees what time it is._  
In one house, there’s one wall clock.

➡️ In distributed systems:  
Everyone has their own watch — all wrong in different ways.

---

2️⃣ **Shared Memory**  
🧠 _Everyone sees the same notebook._  
You write something, everyone sees it instantly.

➡️ Distributed:  
Everyone has their own notebook — pages don’t sync.

---

3️⃣ **Single Authority**  
👑 _One parent decides bedtime._  
No arguments.

➡️ Distributed:  
Multiple parents shout different rules.

---

4️⃣ **Single Failure Domain**  
💡 _Lights on or lights off — same for everyone._

➡️ Distributed:  
Some rooms have light, some are dark.

---

5️⃣ **Deterministic Order**  
📜 _Things happen one after another, clearly._

➡️ Distributed:  
Events overlap, arrive late, or arrive twice.

---

6️⃣ **Reliable Communication**  
📢 _If you shout, people hear you._

➡️ Distributed:  
Your message might vanish into the void.

---

👉 **Distributed systems are hard because these guarantees vanish silently.**  
Nothing breaks loudly — things just become _uncertain_.

---

## 3️⃣ Nature / Forces of Distributed Systems

### _(Reality after guarantees are gone)_

Once implicit guarantees disappear, **forces appear**.

These forces are like **weather** 🌧️  
They don’t care about your design.

---

### The 11 Forces (Simple + Funny)

1️⃣ **No Shared Time**  
⏰ _Everyone’s watch lies differently._

2️⃣ **Failure Uncertainty**  
😴 _Is your friend asleep or dead? No one knows._

3️⃣ **Unreliable Messages**  
📮 _Letters get lost, duplicated, or delayed._

4️⃣ **State Drift**  
📒 _Everyone updates their own copy — they disagree._

5️⃣ **Coordination Is Expensive**  
🧑‍🤝‍🧑 _More people = longer meetings._

6️⃣ **Progress Can Stop**  
🛑 _Everyone waits forever. Nothing moves._

7️⃣ **Scaling Pressure**  
🐘 _Too many elephants on one bridge._

8️⃣ **Partial Visibility**  
🕶️ _You see only part of the truth._

9️⃣ **Humans Interfere**  
🧑‍🔧 _Someone panics and restarts things._

🔟 **Identity Confusion**  
🎭 _Same name, different person._

1️⃣1️⃣ **State Ownership Confusion**  
📦 _Who owns this box right now?_

---

👉 **These forces explain why distributed bugs feel random and evil.**  
They are not random — they are **unmanaged forces**.

---

## 4️⃣ Responsibilities of Distributed Systems

### _(How we survive reality)_

Responsibilities are **jobs we assign** so the system doesn’t collapse.

If forces are weather, responsibilities are **city jobs**.

---

### The 5 Responsibilities (Dog-Level Simple)

---

### 1️⃣ Authority

👑 _Who is the boss?_

**Like:** One referee in a match  
Without it → chaos.

Purpose:

- resolve conflicts
    
- decide final truth
    
- avoid split-brain
    

---

### 2️⃣ Ownership

🏠 _Who owns which house?_

**Like:** One kid owns one toy  
Others ask before touching.

Purpose:

- limit responsibility
    
- enable scaling
    
- define source of truth
    

---

### 3️⃣ Coordination

🤝 _Who must agree with whom?_

**Like:** Only roommates vote on house rules  
Not the entire city.

Purpose:

- enforce agreement only where needed
    
- avoid global slowdown
    

---

### 4️⃣ Communication Discipline

📞 _How do we talk safely?_

**Like:** “Say it again, I didn’t hear you.”  
And not getting angry if it repeats.

Purpose:

- survive lost messages
    
- avoid double actions
    
- handle retries
    

---

### 5️⃣ Recovery & Continuity

🚑 _What happens when someone falls?_

**Like:** Ambulance + hospital  
Failure is normal, not shocking.

Purpose:

- heal the system
    
- recover ownership
    
- survive human mistakes
    

---

👉 **Every distributed system has these jobs — even broken ones.**

---

## 5️⃣ Components

### _(How responsibilities become real things)_

Components are **tools that perform responsibilities**.

Same jobs, different uniforms.

### Common Components Everywhere

- **Leader / Primary** → Authority
    
- **Shard / Partition** → Ownership
    
- **Scheduler / Coordinator** → Coordination
    
- **Queue / Log** → Communication discipline
    
- **Worker** → Execution
    
- **Controller / Reconciler** → Recovery
    
- **Metadata store** → Memory of authority & ownership
    

👉 **Names change. Responsibilities don’t.**

---

## The Full Mental Map (Glue It All Together)

```txt
 Why we distribute         ↓
 What we gain & what we lose (implicit guarantees)         ↓ 
 Forces of reality         ↓ 
 Responsibilities we assign         ↓ 
 Components that implement them`
```

This is the **entire subject** at level-0.

---

## One Sentence to Remember Forever 🧠

> **Distributed systems exist because one machine isn’t enough, are hard because implicit guarantees disappear, and work only when responsibilities are clearly assigned to survive unavoidable forces.**

If this sentence feels _obvious_ now — you truly get it.