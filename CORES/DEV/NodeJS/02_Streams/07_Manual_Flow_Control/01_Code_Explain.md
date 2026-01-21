This snippet is **dense but extremely important**—it’s one of those patterns that separates _“I know streams”_ from _“I can safely parse binary protocols in production.”_

I’ll walk through it **line by line**, then explain **why each decision exists**, and finally give you the **mental model** you should keep.

---
# Logic
```js
WHEN stream becomes readable:
  LOOP:
    TRY to read 16 bytes as header
    IF header is not available:
      STOP (wait for more data)

    TRY to read 32 bytes as payload
    IF payload is not available:
      PUT header back into stream
      STOP (wait for more data)

    PROCESS (header, payload)

```

## The Code (for reference)

```js
stream.on("readable", () => {
  let header;
  while ((header = stream.read(16)) !== null) {
    const payload = stream.read(32);
    if (payload === null) {
      // Not enough data yet
      stream.unshift(header);
      return;
    }

    handleRecord(header, payload);
  }
});

```

---

## 1. Why `"readable"` Instead of `"data"`

### Key idea

- `"data"` → **push-based**
- `"readable"` → **pull-based**
    

This code **must control how many bytes are read**, so it _cannot_ use `"data"`.

`stream.on("readable", () => { ... });`

This event means:

> “There _might_ be data available. You decide how much to read.”

That’s crucial for fixed-size binary parsing.

---

## 2. The `while (read(n) !== null)` Pattern

```js
let header;
while ((header = stream.read(16)) !== null) {

```

### What this does

- `stream.read(16)` tries to read **exactly 16 bytes**
- If **not enough bytes are buffered**, it returns `null`
- If it returns `null`, the loop stops
    

### Why a loop?

Because **one `"readable"` event may contain multiple records**.

Node buffers data internally. If the buffer already has:

`[header][payload][header][payload]`

…then we want to process **all complete records immediately**, not wait for another event.

---

## 3. Reading the Payload

```js
const payload = stream.read(32);

```

Now we assume:

- We successfully read a full **16-byte header**
- Next we expect a **32-byte payload**
    

This matches the assumed binary format:

`[16 bytes header][32 bytes payload]`

---

## 4. Why `payload === null` Is Dangerous

```js
if (payload === null) {

```

This means:

- Header was available
- Payload was **not fully buffered yet**
    

This can happen if:

- Stream chunk boundary split the record
- Network / file I/O delivered partial data
    

### Critical danger

If we **do nothing**, the 16-byte header is now **lost**.

That would corrupt the stream.

---

## 5. Why `unshift(header)` Exists

```js
stream.unshift(header);

```

This line is the heart of the code.

### What `unshift()` does

It **puts data back** into the readable stream’s internal buffer **at the front**.

So the buffer state goes from:

`[partial payload...]`

back to:

`[header][partial payload...]`

### Why this matters

On the **next `"readable"` event**, we want to retry:

`read(16) → read(32)`

Without `unshift()`:

- The header is gone
- The payload is misaligned
- Every record after this is corrupted
    

This is **parser backtracking**.

---

## 6. Why `return`, Not `continue`

`return;`

This exits the `"readable"` handler immediately.

### Why?

Because:

- The stream currently **cannot satisfy the payload**
- More data must arrive
- Continuing the loop would only produce `null`s
    

Returning hands control back to Node’s event loop.

---

## 7. Handling a Complete Record

`handleRecord(header, payload);`

At this point:

- Header is exactly 16 bytes
- Payload is exactly 32 bytes
- Record is complete and safe to process
    

This is **deterministic parsing**—no guessing, no race conditions.

---

## 8. What Happens Over Time (Timeline)

Imagine the stream delivers data like this:

### Chunk 1

`[16-byte header][10 bytes payload]`

- `read(16)` → success
- `read(32)` → `null`
- `unshift(header)`
    
- exit
    

### Chunk 2

`[remaining 22 bytes payload]`

Buffer now contains:

`[16 header][32 payload]`

- `read(16)` → success    
- `read(32)` → success
- record handled ✔️
    

---

## 9. Why This Pattern Is Production-Grade

This code guarantees:

✔ No partial records  
✔ No data loss  
✔ Correct framing  
✔ Works across chunk boundaries  
✔ Safe for files, sockets, pipes

This is how:

- Databases parse wire protocols
- Message brokers frame messages
- Media containers parse blocks
    

---

## 10. Common Mistakes This Avoids

❌ Using `"data"` events  
❌ Assuming chunk boundaries equal record boundaries  
❌ Dropping partial headers  
❌ Parsing without rewind capability  
❌ Using `.pipe()` for structured data

---

## Final Mental Model

Think of the stream as:

> A **byte reservoir**, not a message queue.

This code:

- Pulls **exact byte counts**
- Rolls back if incomplete
- Processes only **fully formed records**
    

---

### One sentence takeaway

> This pattern turns Node streams from a byte hose into a **reliable binary parser**.