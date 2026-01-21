# Interview Traps Around `objectMode` in Node.js Streams

---

## Trap 1: “What is objectMode?”

### ❌ Weak answer

> “It allows streams to pass objects instead of buffers.”

### ✅ Strong answer

> “`objectMode` changes the stream’s unit of backpressure and buffering from **bytes** to **discrete JavaScript values**. Each `push()` is treated as one logical record, regardless of its size.”

**Why this matters**  
Interviewers want to hear **backpressure implications**, not just data type.

---

## Trap 2: “Does objectMode control object size?”

### ❌ Wrong assumption

> “Yes, it prevents large objects.”

### ✅ Correct answer

> “No. `objectMode` only counts **number of objects**, not their memory size. A single object can be arbitrarily large and still count as `1` toward `highWaterMark`.”

**Follow-up they love**

> “That’s why object mode can be dangerous for memory if objects are large.”

---

## Trap 3: “What does `highWaterMark` mean in objectMode?”

### ❌ Weak answer

> “It’s the buffer size.”

### ✅ Strong answer

> “In object mode, `highWaterMark` is the **maximum number of objects** buffered, not bytes. In binary mode it’s bytes.”

```js
// object mode
highWaterMark: 16 // 16 objects

// binary mode
highWaterMark: 64 * 1024 // 64KB

```

**Signal**  
You understand **flow control**, not just syntax.

---

## Trap 4: “Can I pipe an objectMode stream into a normal writable?”

### ❌ Common mistake

> “Yes, pipe handles it.”

### ✅ Correct answer

> “No. A non-object writable expects `Buffer` or `string`. You must serialize objects first.”

```js
// Bridge required
objectStream
  .pipe(stringifyTransform)
  .pipe(fs.createWriteStream('out.txt'));

```

**Rule to say out loud**

> “Readable output type must match writable input type.”

---

## Trap 5: “Why not use objectMode everywhere?”

### ❌ Naive answer

> “It’s easier to work with.”

### ✅ Strong answer

> “Object mode has higher overhead, weaker memory guarantees, and disables many optimizations. It’s best used only for semantic processing, not byte transport.”

**Extra credit**

> “I convert to object mode early, do logic, then return to binary mode.”

---

## Trap 6: “Is `chunk.length` meaningful in objectMode?”

### ❌ Wrong

> “Yes, it tells size.”

### ✅ Correct

> “No. In object mode, `chunk.length` has no defined meaning unless the object itself defines it.”

**Interview gotcha**  
Some candidates rely on `.length` for flow logic — instant red flag.

---

## Trap 7: “How does backpressure differ in objectMode?”

### ❌ Surface answer

> “It still works.”

### ✅ Deep answer

> “Backpressure triggers after `highWaterMark` objects are buffered. But object size is unknown, so memory pressure can still grow unexpectedly.”

**Key phrase**

> “Backpressure is about _count_, not _memory_.”

---

## Trap 8: “Does objectMode affect performance?”

### ❌ Weak

> “It’s fine.”

### ✅ Strong

> “Yes. Object mode disables fast Buffer paths, adds JS overhead, and reduces throughput. That’s acceptable for record processing, not raw I/O.”

---

## Trap 9: “What happens if I forget `objectMode: true`?”

### ❌ Hand-wavy

> “It breaks.”

### ✅ Correct

> “Node will try to treat objects as Buffers and throw or corrupt data. The failure may occur at runtime, not compile time.”

**Example failure**

`TypeError: Invalid non-string/buffer chunk`

---

## Trap 10: “When is objectMode the right choice?”

### ❌ Generic

> “When working with JSON.”

### ✅ Interview-grade

> “When the pipeline operates on **logical records**—events, rows, messages—where chunk boundaries must align with semantics.”

---

## One-Sentence Interview Summary (Gold)

If you remember nothing else, say this:

> **“Binary mode moves bytes efficiently. Object mode moves semantic records safely—but shifts backpressure from bytes to object count, which impacts memory and performance.”**