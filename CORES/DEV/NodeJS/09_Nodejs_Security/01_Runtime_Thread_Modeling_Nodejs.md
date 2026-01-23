## What we are modeling (scope)

**Asset:**

> A _healthy event loop_ with bounded memory, predictable latency, and forward progress.

**Out of scope:**

- SQL injection
- XSS
- Auth bugs
    

Those are _input correctness_ problems.  
This is about **execution safety**.

---

## The Core Question

For every runtime surface, ask:

> Can untrusted input control **time**, **memory**, or **ordering** inside the event loop?

If yes → threat exists.

---

## Runtime Attack Surfaces (Map)

```js
┌───────────────────────────────┐
│ External Input                │
│ (HTTP, streams, IPC, files)   │
└──────────────┬────────────────┘
               │
┌──────────────▼────────────────┐
│ JS Execution (V8)              │
│ - Sync code                    │
│ - Microtasks                   │
│ - Object model                 │
└──────────────┬────────────────┘
               │
┌──────────────▼────────────────┐
│ Async Runtime                  │
│ - Event loop phases            │
│ - Streams / backpressure       │
│ - Timers                       │
└──────────────┬────────────────┘
               │
┌──────────────▼────────────────┐
│ System Resources               │
│ - CPU                          │
│ - Memory                       │
│ - FDs / sockets                │
└───────────────────────────────┘

```

Threat modeling = **where can the attacker push pressure?**

---

## Threat Class 1: Time Control (CPU & Scheduling)

### Goal of attacker

Make your event loop **busy but alive**.

This is worse than a crash.

---

### Common time-control vectors

#### 1. Sync CPU bombs

```js
for (let i = 0; i < userInput; i++) {
  doWork();
}

```

Even “small” loops are fatal under concurrency.

---

#### 2. Algorithmic complexity attacks

```js
array.sort(userControlledComparator);

```

Comparator runs **O(n log n)** times → attacker controls CPU.

---

#### 3. Microtask starvation

```js
function recurse() {
  Promise.resolve().then(recurse);
}
recurse();

```

Timers, IO callbacks never run.

---

### Runtime questions to ask

- Is any sync loop bound by user input?
- Do we call crypto, compression, parsing synchronously?
- Can microtasks be recursively scheduled?
    

---

### Mitigations (runtime-focused)

- Move CPU work to workers
- Enforce per-request CPU budgets
- Yield explicitly in long loops:
    

```js
if (i % 1000 === 0) await setImmediate();

```

- Monitor event loop delay
    

---

## Threat Class 2: Memory Control

### Goal of attacker

Increase memory faster than GC can reclaim.

This leads to:

- GC thrashing
- Latency spikes
- OOM kills
    

---

### Memory control vectors

#### 1. Unbounded buffers

```js
let data = '';
req.on('data', chunk => {
  data += chunk; // ❌ copies + grows
});

```

---

#### 2. JSON amplification

Small payload → huge object graph

```js
JSON.parse('[[[[[[[...]]]]]]]');

```

---

#### 3. Stream buffering abuse

Slow consumer + fast producer = memory balloon.

---

### Runtime questions

- Do we buffer entire payloads?
- Are there max sizes on buffers, arrays, maps?
- Are streams always backpressured?
    

---

### Mitigations

- Hard size caps
- Use streams end-to-end
- Abort early on limits
- Set heap limits (`--max-old-space-size`)
    

---

## Threat Class 3: Flow Control (Ordering & Progress)

### Goal of attacker

Break assumptions about **what runs next**.

---

### Flow control vectors

#### 1. Hanging streams

```js
req.pipe(transform); // transform never ends

```

Resources leak silently.

---

#### 2. Promise leaks

```js
new Promise(() => {}); // never resolves

```

Pinned closures → memory leak.

---

#### 3. Timer floods

```js
setTimeout(() => {}, 0);

```

Large volumes degrade scheduling fairness.

---

### Runtime questions

- Can anything wait forever?
- Are there timeouts everywhere?
- Do async operations always terminate?
    

---

### Mitigations

- Global timeouts
- AbortController everywhere
- `pipeline()` for streams
- Upper bounds on concurrent promises
    

---

## Threat Class 4: Object Model Corruption

### Goal of attacker

Change **meaning** of code without changing code.

---

### Vectors

- Prototype pollution
- Monkey-patching globals
- Mutating shared config
    

```js
Object.prototype.toJSON = () => "hacked";

```

---

### Runtime questions

- Do we merge untrusted objects?
- Are shared objects mutable?
- Do libraries touch globals?
    

---

### Mitigations

- Null-prototype objects
- Freeze critical objects
- Avoid deep merges on untrusted input
- Run with `--frozen-intrinsics` (when possible)
    

---

## Threat Class 5: Resource Exhaustion (Non-Heap)

### Goal of attacker

Exhaust OS-level resources.

---

### Vectors

- File descriptors
- Sockets
- Threads
- Workers
    

```js
while (true) {
  fs.createReadStream(file);
}

```

---

### Runtime questions

- Do we cap concurrency?
- Are resources always closed?
- Are workers bounded?
    

---

### Mitigations

- Semaphores / pools
- Graceful rejection under load
- Process-level ulimits
    

---

## A Practical Threat Modeling Checklist

For **every endpoint / job / stream**, ask:

1. **Time**
    
    - Max CPU per request?
    - Any sync work?
        
2. **Memory**
    
    - Max bytes accepted?
    - Max objects created?
        
3. **Flow**
    
    - Can it hang?
    - Are timeouts enforced?
        
4. **Mutation**
    
    - Can input mutate shared state?
        
5. **Resources**
    
    - What OS resource is consumed?
    - Is there a hard cap?
        

If you can’t answer one → threat exists.

---

## Example: Threat Model an Upload Endpoint

`POST /upload`

|Surface|Threat|Mitigation|
|---|---|---|
|Stream|Infinite upload|Byte cap + timeout|
|CPU|Sync parsing|Stream parsing|
|Memory|Buffering|Pipe-only|
|Flow|Hanging stream|`pipeline()`|
|FD|Open files|Auto-close on error|

This is **runtime security in practice**.

---

## Final mental model

Runtime threat modeling is **pressure analysis**:

> Where can untrusted input push pressure on execution?

Node is fast — until pressure becomes unbounded.

Your job is not to make Node “secure”.  
Your job is to make **failure predictable**.