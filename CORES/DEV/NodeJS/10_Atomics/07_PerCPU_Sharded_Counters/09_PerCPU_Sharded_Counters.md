# 🔜 LEVEL 6 — Per-CPU / Sharded Counters

## The Core Problem (Simple Truth)

> **Atomic operations are correct — but they don’t scale under heavy contention.**

When many threads update **one atomic counter**, performance collapses.

Why?  
Because **the hardware is fighting itself**.

---

## What Actually Goes Wrong

### The naïve design

```js
globalCount++

```

Implemented as:

```js
load → add → CAS → retry

```

When 1 thread runs → fast  
When 2 threads → okay  
When 16 threads → bad  
When 64 threads → terrible

Not because Atomics are slow —  
but because **cache lines bounce constantly**.

---

## Cache Lines (Very Important)

Modern CPUs move memory in **cache lines** (usually 64 bytes).

If multiple cores update:

```js
same cache line

```

The CPU must:

- invalidate other cores’ caches
    
- move the line back and forth
    
- serialize access
    

This is called **cache line contention**.

---

## False Sharing (Silent Performance Killer)

False sharing happens when:

> **Independent data lives on the same cache line.**

Example:

```js
counterA | counterB

```

Two threads update different counters —  
but still fight because they share a cache line.

Result:

- Unexpected slowdowns
    
- “Atomics are slow” myth
    

---

## The Key Insight

> **You don’t need one accurate counter at every moment.**

Most systems can tolerate:

- Slightly stale values
    
- Periodic aggregation
    
- Eventual accuracy
    

This insight unlocks scalability.

---

## The Solution: Sharded Counters

Instead of:

```js
one global counter

```

You use:

```js
many local counters

```

Each thread/core updates **its own shard**.

---

## Mental Model

```js
shard[0] → core 0
shard[1] → core 1
shard[2] → core 2
...

```

Updates:

```js
localShard++

```

Reads:

```js
sum(shards)

```

Writes scale.  
Reads cost more — and that’s okay.

---

## Why This Works

- No contention on writes
    
- No cache line bouncing
    
- CAS retries almost disappear
    
- CPU pipelines stay full
    

This is **how high-performance systems survive load**.

---

## Periodic Aggregation

Instead of summing on every read:

- Aggregate every X ms
    
- Or on demand
    
- Or when exporting metrics
    

Example pseudocode:

```js
every 1 second:
    global = sum(localCounters)
    publish(global)

```

Accuracy is:

- Slightly delayed
    
- Completely acceptable
    

---

## Real-World Mapping

### 1️⃣ Metrics Systems

Counters:

- requests/sec
    
- errors/sec
    
- bytes sent
    

They use:

- per-thread counters
    
- periodic flush
    

Accuracy ≠ per-request precision  
Accuracy = trend correctness

---

### 2️⃣ Rate Limiters

Instead of:

```js
atomic increment globalCount

```

Use:

- shard per worker
    
- approximate total
    

Limits are enforced with **slack**.

---

### 3️⃣ Telemetry & Tracing

Events are:

- counted locally
    
- batched
    
- exported
    

Exact ordering is irrelevant.  
Throughput is everything.

---

## False Sharing Prevention

Shards must be:

- Padded
    
- Cache-line separated
    
- Never adjacent
    

Conceptually:

```js
[ shard | padding | shard | padding ]

```

This avoids **invisible contention**.

---

## The Trade-Off (Be Honest)

|Benefit|Cost|
|---|---|
|Massive write scalability|Slower reads|
|Low contention|Slight inaccuracy|
|CPU-friendly|More memory|

This is a **deliberate engineering choice**.

---

## Why Node, Browsers, Kernels Use This

### Node.js

- Event loop metrics
    
- Worker pool stats
    

### Browsers

- Performance counters
    
- Telemetry pipelines
    

### OS kernels

- CPU time accounting
    
- Network packet counts
    

They do not fight the CPU.  
They **cooperate with it**.

---

## The Deeper Lesson

> **Correctness without scalability is a failure.**

Atomics guarantee correctness.  
Sharding restores performance.

Real systems balance **both**.

---

## How This Fits Into Your Journey

You now understand:

- Atomics correctness
    
- Lock contention
    
- Cache behavior
    
- Hardware-aware design
    

This is **systems-level performance thinking**.

---

## Final Takeaway (Read Twice)

> **If many threads update one atomic — you’ve already lost.**

Split the work.  
Aggregate later.  
Respect the cache.

That’s how production systems survive scale.