# Duplex and Transform Streams in Node.js

**Two-Way Flow and In-Flight Data Processing**

## The Problem Writable or Readable Alone Cannot Solve

So far you’ve seen:

- **Readable streams** → produce data
- **Writable streams** → consume data
    

But real systems often need **both at once**, or something even more subtle:

> “As data flows through, I want to _modify it_, not just pass it along.”

Examples you already know intuitively:

- A TCP socket (read + write)
- gzip compression
- encryption / decryption
- parsing logs line-by-line
- converting formats (JSON → CSV)
    

This is where **Duplex** and **Transform** streams exist.

---

## 1. Duplex Streams — Readable + Writable Together

### What Is a Duplex Stream?

A **Duplex stream** is:

> A stream that is **both readable and writable**,  
> but where the input and output sides are **independent**.

Visually:

```js
Writable side  →  [ DUPLEX STREAM ]  →  Readable side
     (input)                          (output)

```

Important:  
**Writing does not automatically affect reading.**

---

### Classic Example: TCP Socket

```js
const net = require('net');

const socket = net.connect(3000);

socket.write('Hello server');   // writable side
socket.on('data', chunk => {    // readable side
  console.log(chunk.toString());
});

```

Here:

- Incoming data ≠ outgoing data
- Reads and writes are independent
- Backpressure applies separately to each side
    

This is _pure duplex behavior_.

---

### Duplex Stream Characteristics

- Has `_read()` **and** `_write()`
- Backpressure applies independently
- No automatic transformation
- Acts like **two streams glued together**
    

---

### Custom Duplex Stream (Minimal Example)

```js
const { Duplex } = require('stream');

class EchoDuplex extends Duplex {
  _write(chunk, enc, cb) {
    // Accept input
    this.push(chunk); // manually push to readable side
    cb();
  }

  _read(size) {
    // No-op (push happens in _write)
  }
}

```

This example **manually connects** write → read, but Node does _not_ do this for you by default.

---

## 2. Why Transform Streams Exist

Most of the time, when people _think_ they want a Duplex stream, what they really want is this:

> “Take input chunks, modify them, and emit output chunks.”

That is exactly what **Transform streams** are for.

---

## 3. Transform Streams — Duplex with a Contract

A **Transform stream** is a **specialized Duplex stream** where:

> Output is _derived from input_.

In other words:

```js
Input → [ TRANSFORM ] → Output

```

Node guarantees:

- Every write leads to zero or more reads
- Flow control is handled automatically
- Backpressure is propagated end-to-end
    

---

## 4. The Transform API (Core Idea)

You implement **one method**:

```js
_transform(chunk, encoding, callback)

```

Inside `_transform` you:

1. Receive input chunk
2. Process it
3. Push transformed data
4. Call `callback()`
    

---

## 5. Simple Transform Example — Uppercase Processor

```js
const { Transform } = require('stream');

class Uppercase extends Transform {
  _transform(chunk, encoding, callback) {
    const result = chunk.toString().toUpperCase();
    this.push(result);
    callback();
  }
}

```

Usage:

```js
process.stdin
  .pipe(new Uppercase())
  .pipe(process.stdout);

```

What Node handles for you:

- Backpressure
- Buffering
- Pause / resume
- Event loop coordination
    

You only focus on **data logic**.

---

## 6. Transform Streams as “Data Processors”

This is the key mental shift:

> Transform streams are **in-flight data processors**, not storage.

They operate on:

- **chunks**, not whole files
- **streams**, not arrays
- **flow**, not batches
    

That’s why they scale.

---

## 7. Real-World Examples

### 1️⃣ gzip Compression

```js
const zlib = require('zlib');
const fs = require('fs');

fs.createReadStream('input.txt')
  .pipe(zlib.createGzip())
  .pipe(fs.createWriteStream('input.txt.gz'));

```

Here:

- `createGzip()` is a Transform stream
- Each chunk is compressed independently
- Backpressure flows automatically
- Memory stays bounded
    

---

### 2️⃣ Encryption / Decryption

```js
const crypto = require('crypto');

const cipher = crypto.createCipheriv(alg, key, iv);

readable
  .pipe(cipher)   // Transform stream
  .pipe(writable);

```

Each chunk is encrypted **as it passes through**.

---

### 3️⃣ Line Parser (Non-Trivial Example)

Problem: Streams give chunks, **not lines**.

```js
const { Transform } = require('stream');

class LineParser extends Transform {
  constructor() {
    super();
    this.buffer = '';
  }

  _transform(chunk, enc, cb) {
    this.buffer += chunk.toString();

    const lines = this.buffer.split('\n');
    this.buffer = lines.pop(); // incomplete line

    for (const line of lines) {
      this.push(line);
    }

    cb();
  }

  _flush(cb) {
    if (this.buffer) {
      this.push(this.buffer);
    }
    cb();
  }
}


```

```js
const fs = require('fs');

const readStream = fs.createReadStream('input.txt');

readStream
  .pipe(new LineParser())
  .on('data', line => {
    console.log('LINE:', line);
  })
  .on('end', () => {
    console.log('Done reading file');
  });

```
This shows why Transform streams matter:

- Stateful processing
- Chunk boundaries don’t matter
- Still respects backpressure
    
```js
const fs = require('fs');

fs.createReadStream('input.txt')
  .pipe(new LineParser())
  .pipe(fs.createWriteStream('output.txt'));

```

```js
File (chunks)
  ↓
LineParser (lines)
  ↓
File (lines written incrementally)

```

Slow Consumer
```js
fs.createReadStream('input.txt')
  .pipe(new LineParser())
  .on('data', line => {
    // simulate slow processing
    setTimeout(() => {
      console.log(line);
    }, 100);
  });

```

What happens:

- Downstream slows
- Backpressure propagates automatically
- Read stream pauses
- Memory does NOT grow unbounded
    

You didn’t write a single line of backpressure code.  
That’s the power of Transform streams.
---

## 8. Backpressure in Transform Streams (Critical Detail)

Transform streams **automatically connect**:

- Writable backpressure ←→ Readable backpressure
    

If downstream slows down:

- `.push()` starts returning false
- `_transform` pauses
- Upstream `.write()` eventually returns false
    

You get **end-to-end flow control for free**.

This is why `.pipe()` is safe.

---

## 9. Duplex vs Transform — Clear Comparison

|Feature|Duplex|Transform|
|---|---|---|
|Read & Write|Yes|Yes|
|Output derived from input|❌ No|✅ Yes|
|Common use|Sockets, IPC|Compression, parsing|
|Needs `_read`|Yes|No|
|Needs `_write`|Yes|No|
|Needs `_transform`|No|Yes|

---

## 10. Why `.pipe()` Is So Powerful

When you write:

```js
readable
  .pipe(transform)
  .pipe(writable);

```

Node automatically wires:

- Backpressure
- Error propagation
- Pause / resume
- Drain handling
    

Manually writing this logic correctly is **hard**.  
Streams encode decades of systems knowledge.

---

## Final Mental Model (Lock This In)

- **Readable**: source of data
- **Writable**: sink of data
- **Duplex**: two independent directions
- **Transform**: data changes as it flows
    

Or simply:

> **Transform streams are Duplex streams with intent.**

If writable streams answer _“how data leaves Node safely”_,  
transform streams answer _“how data evolves safely while moving.”_