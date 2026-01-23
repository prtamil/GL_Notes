# Version 1 — Push-Based Binary Parser (Baseline, Still Useful)

This version is **not wrong**. It’s often used internally or when you want full manual control.

## Protocol Recap

```js
[4 bytes] length (uint32 BE) → bytes of (type + payload)
[1 byte ] type
[N bytes] payload

```

---

## BinaryParser (Non-Stream Version)

```js
class BinaryParser {
  constructor() {
    this.buffer = Buffer.alloc(0);
    this.MAX_FRAME_SIZE = 1024 * 1024; // 1MB safety limit
  }

  push(chunk) {
    // Append incoming data
    this.buffer = Buffer.concat([this.buffer, chunk]);
    return this._parse();
  }

  _parse() {
    const messages = [];

    while (true) {
      // 1️⃣ Need at least 4 bytes for length
      if (this.buffer.length < 4) break;

      const frameLength = this.buffer.readUInt32BE(0);

      // 2️⃣ Defensive check (production requirement)
      if (frameLength > this.MAX_FRAME_SIZE) {
        throw new Error(`Frame too large: ${frameLength}`);
      }

      // 3️⃣ Need full frame
      if (this.buffer.length < 4 + frameLength) break;

      // 4️⃣ Extract frame (zero-copy)
      const frame = this.buffer.slice(4, 4 + frameLength);

      // 5️⃣ Consume bytes
      this.buffer = this.buffer.slice(4 + frameLength);

      // 6️⃣ Decode frame
      messages.push(this._decode(frame));
    }

    return messages;
  }

  _decode(frame) {
    const type = frame.readUInt8(0);
    const payload = frame.slice(1);

    return {
      type,
      payload
    };
  }
}

```

---

## Using It with TCP

```js
const net = require('net');

const parser = new BinaryParser();

net.createServer(socket => {
  socket.on('data', chunk => {
    const messages = parser.push(chunk);

    for (const msg of messages) {
      console.log('Message:', msg);
    }
  });
}).listen(9000);

```

---

## Why This Version Still Matters

✅ Simple  
✅ Explicit control  
✅ Easy to debug  
❌ Not composable  
❌ No built-in backpressure  
❌ Manual wiring everywhere

This is your **conceptual foundation**.

Now we do it _the Node way_.