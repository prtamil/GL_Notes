# Why Caches Break Multithreaded Programs (and How Atomics Fix Them)
# 1️⃣ The Problem: Cores + Caches

Modern CPUs are **not** like this:

```js
Core → RAM

```

They are like this:

```js
Core 1 → L1/L2 → RAM
Core 2 → L1/L2 → RAM
Core 3 → L1/L2 → RAM

```

Each core has:

- Its **own cache**
    
- Its **own store buffer**
    
- It can **delay and reorder** memory operations for speed
    

This is where trouble starts.

---

## What the CPU is optimizing for

- Speed
    
- Throughput
    
- Speculation
    

❌ **Not** correctness of your multithreaded program.

---

# 2️⃣ Cache Coherence: What It Solves (and What It Doesn’t)

### What cache coherence guarantees

If two cores touch the **same memory location**:

```js
X = 1

```

Then:

- Only one core writes at a time
    
- Other cores will **eventually** see the same value
    
- No “impossible” values appear
    

This is usually implemented via **MESI** or similar protocols.

✅ This solves **data corruption**  
❌ This does **not** solve **coordination**

---

## Key limitation

> Cache coherence tracks **values**, not **meaning**.

It does **not know**:

- That one write depends on another
    
- That “ready” means “data is valid”
    
- That order matters
    

---

# 3️⃣ The Actual Bug: “Eventual Agreement”

Let’s see the classic failure.

### Shared variables (in RAM)

```js
data = 0;
ready = 0;

```

---

### Thread / Core 1 (Producer)

```js
data = 42;
ready = 1;

```

### Thread / Core 2 (Consumer)

```js
while (ready === 0) {}
print(data);

```

---

## What you expect

```js
ready == 1 → data == 42

```

---

## What actually happens (timeline)

### Core 1

```js
t1: data = 42   → stays in store buffer
t2: ready = 1  → flushed early to cache

```

### Core 2

```js
t3: sees ready = 1
t4: reads data = 0   ❌

```

### Later…

```js
t5: data = 42 becomes visible

```

---

## Why cache coherence allows this

- `ready` and `data` are **different cache lines**
    
- Coherence does **not order writes across addresses**
    
- Visibility timing is **independent**
    

> Cache coherence guarantees **eventual agreement**  
> not **correct timing**

By the time things “agree”, the program is already wrong.

---

# 4️⃣ Why This Breaks Programs

Programs rely on **meaningful ordering**, like:

> “If you see READY, DATA must already be valid”

Cache coherence cannot express that rule.

So you get:

- Heisenbugs
    
- Rare failures
    
- “Works on my machine”
    
- Nightmares in prod
    

---

# 5️⃣ How Atomics Fix This

Atomics do **two critical things**:

---

## ✅ 1. They force **visibility**

Atomic writes **must** become visible before proceeding.

---

## ✅ 2. They enforce **ordering**

They create **happens-before** relationships.

> “This write must be seen before that read”

---

# 6️⃣ Same Example — Fixed with Atomics

### Producer

```js
Atomics.store(shared, DATA, 42);
Atomics.store(shared, READY, 1);

```

### Consumer

```js
while (Atomics.load(shared, READY) === 0) {}
print(Atomics.load(shared, DATA));

```

---

## What Atomics guarantee here

- `DATA = 42` **happens before** `READY = 1`
    
- Any thread that sees `READY = 1`  
    → **must see** `DATA = 42`
    

This is **not optional**  
This is **mandatory correctness**

---

# 7️⃣ Mental Model (keep this)

### Without atomics

```js
Values propagate whenever
Order is optional
Correctness is accidental

```

### With atomics

```js
Writes have meaning
Order is enforced
Correctness is guaranteed

```

---

# 8️⃣ One-Line Summary (lock it in)

> **Cache coherence keeps values consistent.  
> Atomics make programs correct.**