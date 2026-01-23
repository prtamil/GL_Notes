# Security at the Runtime Level (Node.js)

## Why this matters

Most Node.js outages are **not caused by attackers stealing data**.  
They are caused by attackers (or bugs) **controlling execution flow, memory, or scheduling**.

If the event loop is blocked, starved, or forced into pathological states:

- Latency explodes
- Memory grows unbounded
- Autoscaling amplifies the problem
- The service dies _while appearing “healthy”_
    

Runtime security is about **preventing untrusted input from gaining leverage over the event loop**.

This includes:

- Prototype pollution (logic corruption)
- Untrusted streams (flow control abuse)
- Resource exhaustion (CPU, memory, file descriptors)
    

---

## 1. Prototype Pollution: Logic Corruption at Runtime

### What it actually is (not the textbook definition)

Prototype pollution is **runtime behavior mutation**.

Instead of attacking your database, the attacker attacks **JavaScript’s object model**, altering how _all_ objects behave.

This is dangerous because:

- No crash
- No exception
- Logic silently changes
    

Your program keeps running — incorrectly.

---

### How it impacts the event loop

Prototype pollution can:

- Break guards (`if (obj.isAdmin)`)
- Disable safety checks
- Change how iteration, serialization, or comparison works
- Trigger unexpected sync paths → event loop blocking
    

---

### Practical example: polluted configuration object

#### Vulnerable code

```js
function applyConfig(target, userConfig) {
  for (const key in userConfig) {
    target[key] = userConfig[key];
  }
}

const defaultConfig = { safe: true };

const payload = JSON.parse(
  '{"__proto__": {"isAdmin": true}}'
);

applyConfig(defaultConfig, payload);

console.log({}.isAdmin); // true 😨

```

Now **every object** has `isAdmin === true`.

---

### Real-world impact

Imagine:

```js
if (req.user.isAdmin) {
  processSensitiveTask(); // sync CPU work
}

```

Now _every request_ runs heavy work → **CPU exhaustion**.

This is how prototype pollution becomes a **runtime DoS**, not just a security bug.

---

### Runtime-safe patterns

#### 1. Use null-prototype objects for untrusted data

```js
const safeObj = Object.create(null);
Object.assign(safeObj, userInput);

```

No prototype → no pollution surface.

#### 2. Block dangerous keys explicitly

```js
const BLOCKED_KEYS = new Set(['__proto__', 'constructor', 'prototype']);

function safeAssign(target, source) {
  for (const key of Object.keys(source)) {
    if (BLOCKED_KEYS.has(key)) continue;
    target[key] = source[key];
  }
}

```

#### 3. Freeze trusted objects

```js
Object.freeze(config);
Object.freeze(config.defaults);

```

Prevents runtime mutation entirely.

---

## 2. Untrusted Streams: Event Loop Flow Control Attacks

### The misconception

> “Streams are safe because they’re async.”

False.

Streams can be weaponized to:

- Disable backpressure
- Stall pipelines
- Inflate buffers
- Pin memory
    

Streams are **event loop citizens**.

---

### Attack vector 1: Never-ending readable stream

```js
const { Readable } = require('stream');

const evilStream = new Readable({
  read() {
    this.push(Buffer.alloc(1024)); // infinite data
  }
});

```

If piped into:

```js
evilStream.pipe(fs.createWriteStream('file'));

```


You get:

- Unbounded disk usage
- Continuous CPU wakeups
- GC pressure
    

---

### Attack vector 2: Slow consumer (backpressure bypass)

```js
evilStream.on('data', chunk => {
  heavySyncWork(chunk); // blocks loop
});

```

Backpressure is ignored → event loop stalls.

---

### Real-world example: file upload endpoint

```js
req.pipe(processFileStream);

```

If you don’t:

- Set size limits
- Enforce timeouts
- Observe flow state
    

You’ve given attackers **direct control over runtime scheduling**.

---

### Runtime-safe stream patterns

#### 1. Always enforce byte limits

```js
let bytes = 0;
const MAX = 10 * 1024 * 1024; // 10MB

req.on('data', chunk => {
  bytes += chunk.length;
  if (bytes > MAX) {
    req.destroy(new Error('Payload too large'));
  }
});

```

---

#### 2. Use `pipeline()` (not manual piping)

```js
const { pipeline } = require('stream/promises');

await pipeline(
  req,
  limitedTransform,
  destination
);

```

`pipeline()`:

- Propagates errors
- Closes resources
- Prevents hanging streams
    

---

#### 3. Guard transform streams

```js
const { Transform } = require('stream');

class SafeTransform extends Transform {
  _transform(chunk, _, cb) {
    if (chunk.length > 1024 * 1024) {
      return cb(new Error('Chunk too large'));
    }
    cb(null, chunk);
  }
}

```

---

## 3. Resource Exhaustion: Killing the Event Loop Without Crashing

### Why this is the most dangerous class

No exploit.  
No bug.  
Just **valid input at pathological scale**.

Node.js fails when:

- Sync work runs too long
- Microtasks starve macrotasks
- Memory grows faster than GC
    

---

### CPU exhaustion example

```js
app.get('/hash', (req, res) => {
  crypto.pbkdf2Sync(
    req.query.pw,
    'salt',
    500_000, // attacker-controlled?
    64,
    'sha512'
  );
  res.send('ok');
});

```

One request → event loop blocked.

Ten concurrent requests → outage.

---

### Memory exhaustion via JSON

```js
JSON.parse(req.body); // unbounded input

```

Large nested objects cause:

- Huge allocations
- GC thrashing
- Process termination
    

---

### File descriptor exhaustion

```js
while (true) {
  fs.createReadStream('file'); // never closed
}

```

Eventually:

- `EMFILE`
- Streams stop working
- Server behaves randomly
    

---

### Runtime protection strategies

#### 1. Timeboxing CPU work

```js
const start = process.hrtime.bigint();

function guard() {
  const elapsed =
    Number(process.hrtime.bigint() - start) / 1e6;
  if (elapsed > 20) {
    throw new Error('CPU budget exceeded');
  }
}

```

Call `guard()` inside loops.

---

#### 2. Offload CPU-heavy tasks

```js
const { Worker } = require('worker_threads');

new Worker('./hash-worker.js', {
  workerData: input
});

```

Workers protect the event loop by **isolating execution**.

---

#### 3. Set hard process limits

```js
node --max-old-space-size=512 server.js

```

Fail fast > slow death.

---

#### 4. Observe event loop health

```js
const { monitorEventLoopDelay } = require('perf_hooks');

const h = monitorEventLoopDelay();
h.enable();

setInterval(() => {
  if (h.mean > 50_000_000) {
    console.error('Event loop under attack');
  }
}, 1000);

```

Detection is part of runtime security.

---

## Mental Model: Runtime Security = Control of Execution

Think in terms of **leverage**:

|Vector|Attacker gains|
|---|---|
|Prototype pollution|Logic control|
|Untrusted streams|Flow control|
|Resource exhaustion|Scheduling control|

If an attacker can:

- Extend execution
- Inflate memory
- Starve tasks
    

They control your runtime.

---

## Final takeaway

Runtime security is not about **preventing access**.  
It’s about **preserving liveness**.

Your real assets are:

- Event loop responsiveness
- Predictable scheduling
- Bounded memory
- Controlled execution paths
    

Protect those, and most attacks become irrelevant.