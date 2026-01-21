# Custom Stream Implementations in Node.js

Node.js streams are powerful because they let you **process data incrementally** instead of loading everything into memory. While built-in streams (fs, http, zlib) cover many cases, real systems often need **custom behavior**:

- Reading from a database cursor
- Writing to an API with rate limits
- Transforming data (encryption, validation, enrichment)
- Integrating legacy or non-stream APIs
    

This is where **custom Readable, Writable, and Transform streams** shine.

---

## Why Write Your Own Streams?

Before jumping into code, understand the _problem they solve_.

### Without streams (bad for large data)

```js
const data = await fs.promises.readFile('big.csv', 'utf8');
process(data);

```

❌ High memory usage  
❌ No backpressure  
❌ No partial progress

### With custom streams (production-friendly)

- Data flows chunk by chunk
- Backpressure is automatic
- You can pause, resume, retry, or abort cleanly
    

---

## 1. Custom Readable Streams

### When to write one

Use a custom **Readable** when:

- Data source is _push-based_ (DB cursor, message queue)
- Data is generated dynamically
- You want full control over chunk size and timing
    

---

### The `_read(size)` hook

```js
_read(size) {
  // push data with this.push(chunk)
  // push(null) when done
}

```

**Key rules**

- `_read` is called when consumer wants more data
- Never push endlessly — respect demand
- `this.push(null)` signals end of stream
    

---

### Practical Example: Reading from a Database Cursor

```js
const { Readable } = require('stream');

class UserCursorStream extends Readable {
  constructor(cursor, options = {}) {
    super({ objectMode: true, ...options });
    this.cursor = cursor;
  }

  async _read() {
    try {
      const user = await this.cursor.next();

      if (!user) {
        this.push(null); // end of stream
        return;
      }

      this.push(user);
    } catch (err) {
      this.destroy(err);
    }
  }
}

```

### Usage

```js
for await (const user of new UserCursorStream(dbCursor)) {
  console.log(user.email);
}

```

### Why this works well

- Pull-based (consumer controls pace)
- Natural backpressure
- Errors propagate correctly
    

---

## 2. Custom Writable Streams

### When to write one

Use a **Writable** when:

- Destination is slow (API, DB, socket)
- Writes need batching, retries, or rate limits
- You must know _when_ data is flushed
    

---

### The `_write(chunk, encoding, callback)` hook

```js
_write(chunk, encoding, callback) {
  // perform async write
  // call callback(err?) when finished
}

```

**Golden rule**

> Never forget to call `callback` — or the stream will stall forever.

---

### Practical Example: Writing to a Rate-Limited API

```js
const { Writable } = require('stream');

class ApiWriter extends Writable {
  constructor(apiClient, options = {}) {
    super({ objectMode: true, ...options });
    this.apiClient = apiClient;
  }

  async _write(record, encoding, callback) {
    try {
      await this.apiClient.send(record);
      callback();
    } catch (err) {
      callback(err);
    }
  }
}

```

### Usage

```js
readableStream
  .pipe(new ApiWriter(apiClient))
  .on('error', console.error)
  .on('finish', () => console.log('All sent'));

```

### Backpressure behavior

If the API is slow:

- `_write` resolves slowly
- Writable buffer fills
- Readable automatically pauses
    

No extra code required.

---

## 3. Custom Transform Streams

### When to write one

Use a **Transform** when:

- You modify data (parse, encrypt, compress)
- Input ≠ Output
- You want streaming pipelines
    

---

### The `_transform(chunk, encoding, callback)` hook

```js
_transform(chunk, encoding, callback) {
  // process input
  // this.push(transformed)
  // callback(err?)
}

```

---

### Practical Example: JSON Validation + Enrichment

```js
const { Transform } = require('stream');

class EnrichUserStream extends Transform {
  constructor() {
    super({ objectMode: true });
  }

  async _transform(chunk, encoding, callback) {
    try {
      if (!chunk.email) {
        throw new Error('Invalid user');
      }

      const enriched = {
        ...chunk,
        processedAt: new Date().toISOString(),
      };

      this.push(enriched);
      callback();
    } catch (err) {
      callback(err);
    }
  }
}

```

### Usage

```js
readableUsers
  .pipe(new EnrichUserStream())
  .pipe(apiWriter);

```

### Why Transform is powerful

- Keeps logic composable
- Easy to test
- Works cleanly with `pipeline()`
    

---

## Understanding the Hooks (Mental Model)

|Stream Type|Hook|Responsibility|
|---|---|---|
|Readable|`_read(size)`|Produce data|
|Writable|`_write(chunk, enc, cb)`|Consume data|
|Transform|`_transform(chunk, enc, cb)`|Modify data|

Think in terms of **contracts**:

- Readable promises to _push_
- Writable promises to _acknowledge_
- Transform promises to _do both_
    

---

## Error Handling (Critical)

### Correct pattern

```js
try {
  // async logic
  callback();
} catch (err) {
  callback(err);
}

```

or

```js
this.destroy(err);

```

### Production-safe pipeline

```js
const { pipeline } = require('stream/promises');

await pipeline(
  source,
  transform,
  destination
);

```

✔ Automatic cleanup  
✔ Error propagation  
✔ No leaked file descriptors

---

## Debugging Custom Streams (Real Tips)

### 1. Enable stream debugging

```js
NODE_DEBUG=stream node app.js

```

You’ll see:

- `_read` calls
- buffer states
- backpressure behavior
    

---

### 2. Log lifecycle events

```js
stream.on('close', () => console.log('closed'));
stream.on('end', () => console.log('ended'));
stream.on('finish', () => console.log('finished'));
stream.on('error', console.error);

```

---

### 3. Most common bugs (and fixes)

|Bug|Symptom|Fix|
|---|---|---|
|Forgot callback|Pipeline freezes|Always call `callback()`|
|Never push null|Stream never ends|`this.push(null)`|
|Pushing in constructor|Early data loss|Push only in `_read`|
|Ignoring backpressure|High memory|Respect write callbacks|

---

## When NOT to Write Custom Streams

Be honest here — don’t over-engineer.

Avoid custom streams when:

- Simple async loop is enough
- Data fits comfortably in memory
- No backpressure needed
    

Streams are **power tools**, not default tools.

---

## Final Takeaway

Custom streams let you:

- Model real-world data flow
- Handle large data safely
- Build resilient pipelines
    

But they demand **discipline**:

- Respect backpressure
- Handle errors explicitly
- Understand lifecycle events
    

If you’re already studying **backpressure, async iteration, and pipelines**, custom streams are the _next level_ — and mastering them means you truly understand Node.js internals.