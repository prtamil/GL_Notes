# How V8 + libuv Fail Under Pressure

## Mental model (keep this in mind)

Node is two systems glued together:

```js
┌──────────────┐
│   V8         │  → JS execution, GC, microtasks
└───────┬──────┘
        │
┌───────▼──────┐
│   libuv      │  → IO, timers, threadpool
└──────────────┘

```

Most outages happen **at the seam**, not inside one box.

---

## Failure Mode 1: GC Thrashing (V8 under memory pressure)

### What triggers it

- Rapid allocation of short-lived objects
- Large buffers created faster than GC can reclaim
- Heap near its max size
    

Common causes:

- JSON parsing
- Buffer concatenation
- Large arrays/maps
- Stream buffering bugs
    

---

### What actually happens

1. V8 increases GC frequency
2. GC pauses become longer
3. Event loop stops making forward progress
4. Latency spikes, but CPU looks “busy”
5. Process may never crash — just crawl
    

This is the **slow death**.

---

### Why it’s deceptive

- No errors
- No stack traces
- CPU looks normal
- Memory plateaus just below limit
    

Your service looks “up” but unusable.

---

### Observable symptoms

- Event loop delay steadily increasing
- P99 latency exploding
- Throughput collapsing
- GC logs full of `Scavenge` and `Mark-sweep`
    

---

### Practical example

```js
req.on('data', chunk => {
  body += chunk; // creates new string each time
});

```

Each `+=` allocates → GC storm.

---

### Mitigations

- Avoid string concatenation
- Stream data
- Cap heap aggressively
- Fail early
    

---

## Failure Mode 2: Microtask Starvation (V8 scheduling failure)

### Trigger

- Recursive promises
- Promise-heavy libraries
- Unbounded `then()` chains
    

---

### What happens

Microtasks run **before** timers and IO.

If microtasks keep scheduling themselves:

- Timers never fire
- IO callbacks never execute
- libuv appears “stuck”
    

---

### Example

```js
function loop() {
  Promise.resolve().then(loop);
}
loop();

```

Event loop is alive but **nothing else runs**.

---

### Symptoms

- 0% IO throughput
- No timer callbacks
- CPU pegged
- No obvious blocking code
    

This looks like a libuv bug — it’s not.

---

### Mitigation

- Yield explicitly (`setImmediate`)
- Avoid recursive promise chains
- Audit promise-heavy code
    

---

## Failure Mode 3: Threadpool Saturation (libuv under CPU pressure)

### Trigger

libuv threadpool (default size = 4) handles:

- `fs`
- `crypto`
- `zlib`
- DNS
    

---

### What happens

1. Threadpool fills
2. New tasks queue up
3. IO latency increases
4. Event loop looks idle but nothing completes
    

---

### Example

```js
for (let i = 0; i < 100; i++) {
  crypto.pbkdf2('pw', 'salt', 500000, 64, 'sha512', cb);
}

```

Threadpool saturated → all crypto stalls.

---

### Symptoms

- CPU not maxed
- Requests hanging
- FS/crypto slow or timing out
    

---

### Mitigations

- Increase pool size carefully
    

`UV_THREADPOOL_SIZE=8`

- Move heavy work to workers
- Limit concurrency
    

---

## Failure Mode 4: Event Loop Phase Starvation (libuv fairness)

### Trigger

- Massive timers
- Immediate floods
- Excessive callbacks per tick
    

---

### What happens

libuv processes phases sequentially.

One overloaded phase delays others.

Example:

- Timer queue huge → IO delayed
- Check phase flooded → starvation
    

---

### Example

```js
for (let i = 0; i < 1e6; i++) {
  setImmediate(() => {});
}

```

---

### Symptoms

- IO jitter
- Inconsistent latency
- Timers firing late
    

---

### Mitigation

- Cap timers
- Batch scheduling
- Avoid 0ms floods
    

---

## Failure Mode 5: Backpressure Collapse (V8 + libuv interaction)

### Trigger

- Fast producer
- Slow consumer
- Backpressure ignored
    

---

### What happens

1. libuv delivers data
2. JS buffers it
3. V8 allocates memory
4. GC pressure increases
5. Loop slows → even more buffering
    

Positive feedback loop.

---

### Example

```js
stream.on('data', chunk => {
  heavySyncWork(chunk);
});

```

Backpressure bypassed.

---

### Mitigation

- Respect `highWaterMark`
- Use `pipeline()`
- Never do sync work in `data` handlers
    

---

## Failure Mode 6: FD & Handle Leaks (libuv resource exhaustion)

### Trigger

- Streams not closed
- Timers not cleared
- Workers not terminated
    

---

### What happens

- libuv handle table grows
- OS limits reached
- Random operations start failing
    

---

### Symptoms

- `EMFILE`
- Strange IO failures
- Process doesn’t recover
    

---

### Mitigation

- Track resources
- Close aggressively
- Fail fast
    

---

## Failure Mode 7: The “Alive but Dead” State (Worst Case)

### Combined pressure scenario

- Memory near limit
- GC thrashing
- Threadpool saturated
- Microtask starvation
    

---

### What it looks like

- Health checks pass
- Process responds slowly
- Restart doesn’t happen
- Autoscaling amplifies damage
    

This is the **most dangerous state**.

---

## Why Node Fails This Way (Design Reality)

Node optimizes for:

- Throughput
- Low overhead
- Developer velocity
    

Not for:

- Hard isolation
- Fair scheduling
- Resource accounting
    

These are _your_ responsibility.

---

## The Core Insight (Important)

> V8 and libuv do not “break”.  
> They do exactly what they’re designed to do.

They assume **cooperative code**.

Under adversarial or pathological load:

- Fairness disappears
- Liveness degrades
- Failure becomes nonlinear
    

---

## Practical Defensive Strategy

If you remember only this:

1. **Bound everything**
2. **Measure event loop delay**
3. **Isolate CPU**
4. **Fail early**
5. **Restart aggressively**
    

Node is powerful — but unforgiving.