
## 1. The Big Picture (Bird’s-Eye View)

**Node.js =**

- Single JS thread
- - Event Loop (scheduler)
- - OS / libuv thread pool
- - Queues (tasks & microtasks)
        

Think of Node as:

> **“One JS worker executing tiny jobs, while other workers do the heavy lifting and report back.”**

The **event loop** decides:

- _What runs next_
- _When callbacks fire_
- _Why `setTimeout` isn’t exact_
- _Why `Promise.then` runs before `setTimeout`_
    

---

## 2. Core Components (List You Must Know)

### A. JavaScript Call Stack

- Where **synchronous code** runs
- Runs **to completion**
- Blocks everything else
    

`console.log("A"); console.log("B");`

👉 Nothing async happens until stack is empty.

---

### B. Event Loop (The Scheduler)

- Lives outside JS engine
    
- Repeatedly checks:
    
    1. Is call stack empty?
    2. Any microtasks?
    3. Any tasks in current phase?
        

It **does NOT execute JS**, it **decides what JS executes next**.

---

### C. Queues (Critical Concept)

Node has **two main categories**:

### 1️⃣ Microtask Queue (Highest Priority)

Runs **immediately after current JS finishes**

Contains:

- `Promise.then / catch / finally`
- `queueMicrotask`
- `process.nextTick` (**Node-only, even higher priority**)
    

```js
setTimeout(() => console.log("timeout"));
Promise.resolve().then(() => console.log("promise"));

```

👉 Output:

`promise`
`timeout`

---

### 2️⃣ Task Queues (Macrotasks)

Scheduled by the event loop phases.

Examples:

- `setTimeout`
- `setInterval`
- `setImmediate`
- I/O callbacks
- Network events
    

---

## 3. Node.js Event Loop Phases (VERY IMPORTANT)

This is **Node-specific** (browser is simpler).

### Order of phases (simplified):

1. **Timers**
    
    - `setTimeout`
    - `setInterval`
        
2. **I/O callbacks**
    
    - Some system/network callbacks
        
3. **Idle / prepare**
    
    - Internal (ignore for now)
        
4. **Poll**
    
    - Incoming I/O (fs, net, http)
    - If empty → may wait here
        
5. **Check**
    
    - `setImmediate`
        
6. **Close callbacks**
    
    - `socket.on('close')`, cleanup
        

👉 After **each phase**, Node drains **microtasks**.

---

## 4. Special Case: `process.nextTick`

This one trips everyone.

- Runs **before Promises
- Can starve the event loop if abused
    

Priority order:

```js
Call stack
→ process.nextTick
→ Promise microtasks
→ Event loop phase tasks

```

```js
process.nextTick(() => console.log("tick"));
Promise.resolve().then(() => console.log("promise"));

```

Output:

`tick `
`promise`

---

## 5. libuv Thread Pool (Hidden Workers)

Node is single-threaded **for JS**, but not for work.

Thread pool handles:

- `fs` (most)
- `crypto`
- `zlib`
- `dns.lookup`
    

Default size: **4 threads**

`fs.readFile("big.txt", cb);`

👉 JS thread is free while OS threads work.

---

## 6. Timers Are NOT Timers

Important truth:

`setTimeout(fn, 0);`

Means:

> “Run **after at least** 0ms, when the event loop reaches timers phase”

NOT:

> “Run immediately”

Delays happen if:

- Call stack is busy
- Microtasks keep running
- Poll phase waits for I/O
    

---

## 7. setImmediate vs setTimeout(0)

Common interview trap.

- `setImmediate` → **Check phase**
- `setTimeout(0)` → **Timers phase**
    

Inside I/O:

```js
fs.readFile("x", () => {
  setTimeout(() => console.log("timeout"));
  setImmediate(() => console.log("immediate"));
});

```

👉 Output:

```txt
immediate
timeout

```

Outside I/O → order is not guaranteed.

---

## 8. Events (`EventEmitter`)

Events are **just callbacks**, not magic.

`emitter.on("data", handler);`

When event fires:

- Handler is **queued**
    
- Runs when event loop reaches it
    
- Still subject to stack + microtasks rules
    

---

## 9. Mental Model You Should Lock In

### Node runs in this rhythm:

1. Run sync JS
2. Drain `process.nextTick`
3. Drain Promise microtasks
4. Pick next event loop phase
5. Run one task
6. Repeat
    

---

## 10. Minimal Checklist (Memorize This)

If you remember only this, you’re solid:

- ✅ JS runs to completion
- ✅ Event loop schedules, doesn’t execute
- ✅ Microtasks run before tasks
- ✅ `process.nextTick` > Promise
- ✅ Timers are minimum delays
- ✅ Node has multiple loop phases
- ✅ Heavy work runs in thread pool