# Node.js Event Loop  Queues and Phases — The Complete, Precise Model

## 0. First: One Rule Above All

> **JavaScript runs only when the call stack is empty.**

Everything else exists to decide **what gets pushed next** onto that stack.

---

## 1. The Two Super-Queues (Priority Levels)

Before phases, understand this:

Node has **two priority layers**:
```js
MICROTASKS (run immediately)
-----------------------------
process.nextTick
Promise / queueMicrotask

EVENT LOOP PHASES (scheduled work)
----------------------------------
timers → poll → check → ...

```

Node **always drains microtasks completely** before moving forward.

This is why microtasks can **starve the event loop**.

---

## 2. Microtask Queues (Highest Priority)

Microtasks run:

- After the **current JS execution**
- After **every callback**
- Before **any phase transition**
    

### 2.1 process.nextTick Queue (Node-only)

**Highest priority queue in Node.**

Runs:

- Immediately after the current stack frame
- Even before Promise microtasks
    

```js
process.nextTick(() => console.log("nextTick"));
Promise.resolve().then(() => console.log("promise"));

```

Output:

```js
nextTick
promise

```

Why it exists:

- Internal cleanup
- Backward compatibility
- Dangerous if abused
    

⚠️ Infinite `process.nextTick` = **total event loop starvation**

---

### 2.2 Promise Microtask Queue

Includes:

- `Promise.then`
- `Promise.catch`
- `Promise.finally`
- `queueMicrotask`
    

Rules:

- FIFO
- Fully drained before event loop continues
    
```js
Promise.resolve()
  .then(() => console.log(1))
  .then(() => console.log(2));

```

Runs **before timers, I/O, immediates**.

---

## 3. Event Loop Phases (Macro / Task Queues)

Once microtasks are empty, Node enters the **event loop proper**.

Each iteration is called a **tick**.

### Phase Order (Fixed)

```js
1. Timers
2. Pending I/O Callbacks
3. Idle / Prepare
4. Poll
5. Check
6. Close Callbacks

```

Each phase has **its own queue**.

---

## 4. Phase-by-Phase (Deep Detail)

### 4.1 Timers Phase

#### Queue Contains

- `setTimeout`
- `setInterval`
    

#### Key Rules

- Timers are **not exact**
- A timer runs if:
    
    1. Its delay has elapsed
    2. The event loop has reached this phase
        

```js
setTimeout(() => console.log("A"), 0);
setTimeout(() => console.log("B"), 0);

```

FIFO **per timer bucket**, not globally guaranteed.

After **each timer callback**:

- `process.nextTick` drained
- Promise microtasks drained
    

---

### 4.2 Pending I/O Callbacks Phase

#### Queue Contains

- Deferred I/O callbacks
- TCP errors
- Some system-level callbacks
    

🚫 **Not**:

- File system callbacks
- HTTP data events
    

This phase exists mainly for **error handling continuity**.

---

### 4.3 Idle / Prepare Phase

- Internal libuv bookkeeping
- Ignore for application logic
    

---

### 4.4 Poll Phase (Most Important Phase)

This is where Node **earns its performance**.

#### Queue Contains

- File system callbacks
- Network I/O
- HTTP requests
- Most async results
    

#### Poll Phase Rules

##### Case 1: Poll queue has callbacks

- Execute them **one by one**
- After each:
    
    - Drain `nextTick`
    - Drain Promise microtasks
        

##### Case 2: Poll queue empty

- If `setImmediate` exists → move to **Check**
- Else:
    
    - Wait for I/O
    - Sleep efficiently
        

This waiting behavior is what allows:

- 10k+ idle connections
- Near-zero CPU usage
    

---

#### Example (Poll vs Check)

```js
fs.readFile("a.txt", () => {
  setTimeout(() => console.log("timeout"), 0);
  setImmediate(() => console.log("immediate"));
});

```

Output:

```js
immediate
timeout

```

Why:

- `setImmediate` runs in **Check**
- Timer waits for **next Timers phase**
    

---

### 4.5 Check Phase

#### Queue Contains

- `setImmediate`
    

#### Purpose

- Execute callbacks **immediately after poll**
- Before returning to timers
    

This phase exists **only** for `setImmediate`.

---

### 4.6 Close Callbacks Phase

#### Queue Contains

- `'close'` events
- Resource cleanup
    

```js
socket.on("close", () => {
  console.log("closed");
});

```

Runs after everything else in the loop iteration.

---

## 5. Phase Transition Rules (Very Important)

After **every single callback**, Node does:

```js
1. Drain process.nextTick queue
2. Drain Promise microtask queue

```

This applies:

- Between callbacks
- Between phases
- Between loop iterations
    

This is why microtasks can:

- Delay timers
- Delay I/O
- Delay immediates
    

---

## 6. Visual Timeline (One Loop Tick)

```js
Call stack empty
↓
process.nextTick
↓
Promise microtasks
↓
Timers phase
↓
nextTick → Promises
↓
Pending I/O
↓
nextTick → Promises
↓
Poll
↓
nextTick → Promises
↓
Check
↓
nextTick → Promises
↓
Close callbacks
↓
nextTick → Promises
↓
(loop repeats)

```

---

## 7. Thread Pool Interaction (Important Context)

Some callbacks originate from **libuv’s thread pool**:

- fs
- crypto
- zlib
- dns.lookup
    

Thread completes work → callback enqueued into **Poll queue**

JS still resumes **single-threadedly**.

---

## 8. Common Misconceptions (Cleared)

❌ “Node has one task queue”  
→ **False**

❌ “Promises run in the event loop”  
→ **False (microtasks bypass phases)**

❌ “setTimeout(0) runs immediately”  
→ **False**

❌ “EventEmitter is async”  
→ **False (synchronous by default)**

---

## 9. One Sentence That Locks It In

> **Phases decide _when_ callbacks may run, queues decide _what_ runs next, and microtasks always cut the line.**

If you understand that, you understand Node.