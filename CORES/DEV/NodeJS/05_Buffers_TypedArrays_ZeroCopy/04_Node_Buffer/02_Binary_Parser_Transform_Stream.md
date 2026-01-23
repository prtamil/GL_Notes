# Version 2 — Proper Transform Stream (Production-Grade)

This is what you actually ship.

---

## Why Transform Is the Correct Abstraction

A `Transform` stream:

- Accepts **binary chunks**
- Emits **parsed messages**
- Automatically respects **backpressure**
- Plugs into `pipeline()`, `pipe()`, etc.
    

Your parser becomes:

> **A framed-message decoder in a streaming pipeline**

---

## Transform Stream Parser

```js
const { Transform } = require('stream');

class BinaryProtocolParser extends Transform {
  constructor(options = {}) {
    super({
      readableObjectMode: true, // emit JS objects
      writableObjectMode: false // receive Buffers
    });

    this.buffer = Buffer.alloc(0);
    this.MAX_FRAME_SIZE = options.maxFrameSize || 1024 * 1024;
  }

  _transform(chunk, encoding, callback) {
    try {
      // Append incoming chunk
      this.buffer = Buffer.concat([this.buffer, chunk]);

      // Parse as many frames as possible
      while (true) {
        if (this.buffer.length < 4) break;

        const frameLength = this.buffer.readUInt32BE(0);

        if (frameLength > this.MAX_FRAME_SIZE) {
          throw new Error(`Frame too large: ${frameLength}`);
        }

        if (this.buffer.length < 4 + frameLength) break;

        const frame = this.buffer.slice(4, 4 + frameLength);
        this.buffer = this.buffer.slice(4 + frameLength);

        const message = this._decode(frame);

        // Push downstream (backpressure-aware)
        this.push(message);
      }

      callback();
    } catch (err) {
      callback(err);
    }
  }

  _decode(frame) {
    const type = frame.readUInt8(0);
    const payload = frame.slice(1);

    return { type, payload };
  }

  _flush(callback) {
    // Called when upstream ends
    if (this.buffer.length !== 0) {
      callback(new Error('Incomplete frame at stream end'));
    } else {
      callback();
    }
  }
}

```

---

## Using the Transform Stream with TCP

```js
const net = require('net');

net.createServer(socket => {
  const parser = new BinaryProtocolParser();

  socket
    .pipe(parser)
    .on('data', message => {
      console.log('Parsed message:', message);
    })
    .on('error', err => {
      console.error('Parser error:', err.message);
      socket.destroy();
    });

}).listen(9000);

```

---

## Why This Version Is Production-Grade

Let’s be very explicit.

### ✅ Correct framing

- Partial frames handled
- Multiple frames per chunk handled
    

### ✅ Backpressure

- `this.push()` cooperates with downstream consumers
- If downstream slows → parser naturally slows
    

### ✅ Stream composability

```js
socket
  .pipe(parser)
  .pipe(businessLogic)
  .pipe(writer);

```

This is how real Node systems are built.

---

## Key Design Choices Explained

### `readableObjectMode: true`

Why?

- Parsed messages are **objects**, not bytes
- Avoid re-encoding
- Clean API
    

---

### `_transform` Instead of `data` Events

Why?

- Centralized error handling
- Backpressure integration
- Stream lifecycle awareness
    

---

### `_flush`

Why?

- Detect truncated frames
- Prevent silent data corruption
- This catches real production bugs
    

---

## Push-Based vs Transform — When to Use Which

|Use case|Pick|
|---|---|
|Internal parsing logic|Push-based|
|Network / file pipelines|Transform|
|Needs backpressure|Transform|
|Quick experiments|Push-based|
|Production services|Transform|

---

## One Subtle but Critical Insight

The **core parsing loop is identical** in both versions.

What changes is:

- **who drives it**
- **how results flow**
- **how errors propagate**
    

This is _exactly_ how mature Node code evolves.