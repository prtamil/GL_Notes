# Object Mode vs Binary Mode in Streams

Node.js streams move data in **chunks**, but not all chunks are the same.  
Streams operate in **two fundamentally different modes**:

- **Binary mode** (default)
- **Object mode**
    

Understanding the difference is critical, because **mixing them incorrectly causes subtle bugs, memory issues, and broken pipelines**.

---

## 1. Binary Mode (Default)

### What it is

In binary mode, streams read and write **raw bytes**:

- `Buffer`
- `Uint8Array`
- `string` (converted to Buffer internally)
    

This is how:

- Files
- Sockets
- HTTP bodies
- Compressed or encrypted data  
    are handled.
    

### Example

```js
fs.createReadStream('data.txt')
  .on('data', chunk => {
    console.log(chunk); // Buffer
  });

```

Each `chunk`:

- Is **arbitrary-sized**
- Has **no semantic meaning**
- Might split a line, word, or JSON in half
    

### When to use binary mode

- File I/O
- Network streams
- Compression / encryption
- Media streaming
    

> Binary mode is about **bytes, not meaning**.

---

## 2. Object Mode

### What it is

In object mode, each chunk is a **JavaScript value**:

- Object
- Array
- Number
- String (as a value, not bytes)
    

The stream treats **each object as a single unit**, regardless of size.

### Example

```js
const { Readable } = require('stream');

const stream = Readable.from(
  [{ id: 1 }, { id: 2 }],
  { objectMode: true }
);

stream.on('data', obj => {
  console.log(obj); // full object
});

```

Here:

- No Buffers
- No chunk splitting
- One `push()` = one logical record
    

### When to use object mode

- Parsed JSON records
- Database rows
- Events
- Domain-level data
    

> Object mode is about **meaningful units**, not bytes.

---

## 3. Key Differences (Mental Table)

|Aspect|Binary Mode|Object Mode|
|---|---|---|
|Chunk type|Buffer / bytes|Any JS value|
|Default|Yes|No|
|Chunk size|Variable|Exactly one object|
|Backpressure unit|Bytes|Object count|
|Performance|Faster|Slower|
|Memory|Predictable|Risky if abused|

---

## 4. Backpressure Behaves Differently

### Binary mode

- Backpressure is based on **buffer size (bytes)**
- `highWaterMark` = number of bytes
    

`highWaterMark: 64 * 1024 // 64KB`

### Object mode

- Backpressure is based on **number of objects**
- `highWaterMark` = number of objects
    

`highWaterMark: 16 // 16 objects`

⚠️ One object could be **10MB** — Node doesn’t know or care.

---

## 5. Bridging Object Mode and Binary Mode (Very Important)

Most real pipelines **use both**.

### Example flow

```js
File (binary)
 → parse lines (binary → object)
 → transform objects (object)
 → stringify (object → binary)
 → write file (binary)

```
### Stringify bridge example

```js
new Transform({
  objectMode: true,
  transform(obj, _, cb) {
    cb(null, JSON.stringify(obj) + '\n');
  }
});

```

Rule:

> **Writable must accept exactly what Readable emits.**

---

## 6. Common Production Mistakes

❌ Parsing JSON in binary mode without buffering  
❌ Sending objects to a non-object writable  
❌ Forgetting `objectMode: true`  
❌ Assuming object mode controls object size  
❌ Using object mode for large binary data

---

## 7. When to Choose Which

### Use binary mode when:

- Moving data
- Preserving bytes
- Performance matters most
    

### Use object mode when:

- Meaning matters more than bytes
- Working with records, events, rows
- Transforming structured data
    

---

## Final Takeaway

**Binary mode moves bytes efficiently.  
Object mode moves meaning safely.**

Strong stream designs:

- Convert **binary → object** early
- Do logic in object mode
- Convert **object → binary** late
    

If you keep that shape in mind, your pipelines will stay fast, correct, and easy to reason about.