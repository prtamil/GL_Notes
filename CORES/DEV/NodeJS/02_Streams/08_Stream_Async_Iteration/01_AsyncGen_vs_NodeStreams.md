\# Async Generators vs Node Streams

## Executive Summary (If You Read Only This)

- **Async generators** are about _control, clarity, and composition_
- **Node streams** are about _performance, interoperability, and backpressure at scale_
- Async generators model **async sequences**
- Node streams model **flow-controlled I/O pipelines**
    

They overlap—but they are **not substitutes**.

---

## 1. Mental Model (This Is the Real Difference)

### Async Generators

```js
async function* source() {
  yield 1;
  yield 2;
}

```


Mental model:

> “I will yield the next value **when the consumer asks**.”

This is:

- Pull-based
- Consumer-driven
- Sequential by default
    

You control _when_ values are produced.

---

### Node Streams

```js
readable.pipe(transform).pipe(writable);

```

Mental model:

> “I will push data forward **as fast as the system allows**, slowing down only when backpressure applies.”

This is:

- Push-based
- Producer-driven
- Buffer-managed
    

The stream controls _how fast_ data flows.

---

### Key Insight

|Aspect|Async Generator|Node Stream|
|---|---|---|
|Control|Consumer|Runtime|
|Direction|Pull|Push with brakes|
|Default speed|One item at a time|Buffered|
|Flow tuning|Explicit `await`|HighWaterMark|

This difference shapes **everything else**.

---

## 2. Backpressure: Explicit vs Implicit

### Async Generators

Backpressure is **implicit and absolute**.

```js
for await (const item of gen()) {
  await slowTask(item);
}

```

Nothing advances until `slowTask` finishes.  
No buffers.  
No leaks.

Backpressure is **perfect**, but throughput is limited.

---

### Node Streams

Backpressure is **buffer-based**.

```js
stream.write(chunk); // returns false

```

- Data can accumulate in memory
- Flow continues until buffers fill
- Optimized for throughput
    

This is **necessary for I/O**, but harder to reason about.

---

### Production Implication

- Async generators → _safe by default_
- Streams → _fast by default_
    

---

## 3. Error Propagation (Huge Difference)

### Async Generators

Errors behave like normal `async/await`.

```js
try {
  for await (const x of gen()) {
    ...
  }
} catch (e) {
  // clean, predictable
}

```

- Single error channel
- Stack traces preserved
- No event juggling
    

---

### Node Streams

Errors are **out-of-band**.

```js
stream.on('error', ...)

```

- Errors can happen anytime
- Must be wired everywhere
- Easy to miss in pipelines
    

Node has improved this (`stream.pipeline()`), but generators are still cleaner.

---

## 4. Composition & Testability

### Async Generators (Functional Composition)

```js
async function* filter(src) {
  for await (const x of src) {
    if (x > 10) yield x;
  }
}

```

- Pure functions
- No framework dependency
- Easy to test with arrays
- Deterministic behavior
    

This feels like **async functional programming**.

---

### Node Streams (System Composition)

```js
readable
  .pipe(transformA)
  .pipe(transformB)

```

- Stateful objects
- Framework-heavy
- Harder to unit test
- Designed for I/O boundaries
    

This feels like **infrastructure plumbing**.

---

## 5. Performance & Memory

### Async Generators

Pros:

- Zero buffering
- Minimal memory
- Simple scheduling
    

Cons:

- Sequential by default
- Lower throughput
- Not ideal for binary data
    

They shine in:

- Business logic
- APIs
- ETL logic
- Control-heavy pipelines
    

---

### Node Streams

Pros:

- Native buffering
- Zero-copy for Buffers
- OS-level optimizations
    

Cons:

- Complex internals
- Harder reasoning
- Event-driven edge cases
    

They shine in:

- Files
- Sockets
- HTTP
- Compression
- Large binary data
    

---

## 6. Object Mode vs Async Generators

Async generators are **always object mode**.

Streams have:

- Binary mode (Buffers)
- Object mode (with overhead)
    

If you’re streaming **objects**, generators often win on clarity.

If you’re streaming **bytes**, streams win on performance.

---

## 7. Interoperability (Reality Check)

### Streams integrate with:

- fs
- http
- zlib
- crypto
- child_process
- ecosystem tools
    

### Async generators integrate with:

- `for await`
- `Readable.from()`
- `Readable.toWeb()`
    

You can convert:

`Readable.from(asyncGenerator)`

But generators **cannot replace streams at system edges**.

---

## 8. Cancellation & Shutdown

### Async Generators

- Natural via `return()`
- Abortable with `AbortController`
- No dangling resources
    

### Streams

- Must `.destroy()`
- Must propagate errors
- Easy to leak if mishandled
    

Generators are safer for **graceful shutdown logic**.

---

## 9. Real Production Pattern (Best of Both)

This is the pattern you should actually use:

```js
const stream = fs.createReadStream('data.log');

async function* parse(src) {
  for await (const chunk of src) {
    yield chunk.toString().trim();
  }
}

for await (const line of parse(stream)) {
  await processLine(line);
}

```

**Streams handle I/O.  
Generators handle logic.**

This separation is clean, scalable, and maintainable.

---

## 10. When to Choose What (Hard Rules)

### Choose Async Generators when:

- Logic is async-heavy
- Control > throughput
- Errors must be clean
- Code must be readable
- You’re inside the service layer
    

### Choose Node Streams when:

- Handling raw I/O
- Dealing with large files
- Working with buffers
- Using native Node modules
- Performance is critical
    

### Never:

- Implement custom buffering with generators
- Reimplement streams for I/O
- Use streams for pure business logic
    

---

## Final Mental Lock-In

> **Streams move data efficiently.  
> Async generators move logic cleanly.**

Streams are **infrastructure**.  
Async generators are **language-level control flow**.

If you internalize this distinction, your Node.js designs will stop being accidental and start being intentional.