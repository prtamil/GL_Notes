# Memory & Garbage Collection in Node.js

**(Why Node apps really crash in production)**

Most Node services don’t die because of CPU exhaustion.  
They die because **memory grows quietly until the process is killed**.

If you don’t understand _how_ V8 manages memory, you end up:

- Restarting pods
- Adding more RAM
- Blaming “Node slowness”
    

Instead of fixing the real bug.

---

## Why this matters (the real reason)

Node runs on **V8**, which uses a **managed heap** with garbage collection.

GC is:

- Automatic ✅
- **Not free** ❌
- **Stop-the-world** ❌
    

When GC pauses get longer:

- Latency spikes
- Streams stall
- Backpressure breaks
- Requests time out
    

This is why memory knowledge directly affects:

- **Throughput**
- **Tail latency**
- **Stability**
    

---

## V8 Heap Layout (mental model you must have)

Think of V8 memory like this:

```js
+-------------------+
|   Young Gen       |  (fast, small, frequent GC)
|  - Eden           |
|  - Survivor       |
+-------------------+
|   Old Gen         |  (slow, large, expensive GC)
+-------------------+
|  Large Object     |  (huge allocations)
+-------------------+
|  Code / Metadata  |
+-------------------+

```

### Young Generation

- Small objects
- Short-lived allocations
- Cleared **frequently**
- Very fast GC
    

Examples:

- Temporary objects
- Parsed JSON chunks
- Per-request objects
    

### Old Generation

- Long-lived objects
- Survived multiple GCs
- GC is **slow and blocking**
    

Examples:

- Global caches
- Leaked closures
- Retained buffers
- Long-lived Maps/Sets
    

---

## Young → Old Promotion (where bugs hide)

Objects start in **young gen**.

If they:

- Survive multiple GC cycles
- Are referenced from long-lived objects
    

➡️ They get **promoted to old gen**.

### Why promotion is dangerous

Old gen GC:

- Runs less often
- Takes much longer
- Stops the entire event loop
    

A few accidental promotions can cause:

- Latency spikes every few seconds
- “Random” freezes under load
    

---

## Stop-the-World Pauses (what you feel in prod)

During GC:

- **Event loop stops**
- No JS executes
- No I/O callbacks run
    

Symptoms:

- Requests hang briefly
- Streams stop flowing
- `drain` events arrive late
- Timeouts trigger
    

This is why:

> “Everything looks fine, but p99 latency is awful”

---

## Core Ideas You Must Internalize

### 1️⃣ Streams reduce allocation pressure

Streams matter **not just for backpressure**, but for **memory shape**.

#### Bad (loads everything into memory)

```js
const data = await fs.promises.readFile('big.csv');
process(data);

```

- Huge allocation
- Lands in old gen
- GC nightmare
    

#### Good (streaming)

```js
fs.createReadStream('big.csv')
  .pipe(csvParser())
  .on('data', processRow);

```

- Small chunks
- Short-lived objects
- Clean young-gen GC
- Stable memory
    

👉 Streams keep memory **flat**, not spiky.

---

### 2️⃣ Closures extend object lifetimes (silent leaks)

This is a **top 3 Node memory bug**.

#### Example

```js
function handler(req, res) {
  const bigObject = loadHugeData();

  setTimeout(() => {
    res.end('ok');
  }, 60000);
}

```

Even after request finishes:

- `bigObject` is still referenced
- Survives GC
- Promoted to old gen
    

Now multiply by thousands of requests.

#### Mental rule

> If a closure exists, everything it references **stays alive**

This includes:

- Request objects
- Buffers
- Parsed payloads
- ORM results
    

---

### 3️⃣ Buffers bypass the V8 heap (important nuance)

`Buffer` memory is **not stored on the V8 heap**.

It lives in:

- Native memory (outside GC)
- Referenced _by_ JS objects
    

#### Why this matters

- Large buffers don’t directly increase heap usage
- But references keep them alive
- GC can’t reclaim native memory until JS reference is gone
    

#### Example bug

```js
const cache = [];

stream.on('data', chunk => {
  cache.push(chunk); // chunk is a Buffer
});

```

Heap looks fine.  
RSS keeps growing.  
Process gets OOM-killed.

👉 This is why **RSS vs heapUsed** matters.

---

## What happens if you ignore this topic

You will:

❌ Leak memory silently  
❌ Misdiagnose GC pauses as CPU issues  
❌ Increase pod memory instead of fixing logic  
❌ Restart processes as a “solution”  
❌ Fear Node under high load

And worst of all:

> You won’t know _why_ the system is unstable

---

## What “good” looks like in real systems

Engineers who understand this:

- Use streams by default
- Watch object lifetimes, not just allocations
- Avoid retaining request-scoped data
- Design caches with explicit eviction
- Profile heap **before** production incidents
    

---

## How this connects to what you’re already learning

You’re studying:

- Streams
- Backpressure
- Partial success
- Resilience
    

Memory & GC is the **hidden layer underneath all of that**.

Streams:

- Control **flow**
- Control **memory**
- Control **GC behavior**
    

This is why I told you:

> Streams are not just an API — they are a memory strategy.