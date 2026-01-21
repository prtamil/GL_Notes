# Deep Explanation: Manual Parsing with `"readable"` and `read(n)`

### Code

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

## 1. What `"readable"` Really Means

`"readable"` is a **pull-based** event.

> It does NOT mean “a chunk arrived”.  
> It means “the stream _may_ now be readable — try pulling data”.

Node emits `"readable"` when the internal buffer transitions from:

```js
cannot make progress → can make progress

```

You are responsible for calling:

```js
stream.read()
stream.read(n)

```

---

## 2. Why `"readable"` (Not `"data"`)

This code needs:

- Exact byte counts
- Deterministic parsing
- Ability to rewind
    

`"data"` is **push-based** and unsafe for structured data.

So `"readable"` is mandatory.

---

## 3. Stream Internal Buffer (Mental Model)

Think of the stream as:

```js
[ byte ][ byte ][ byte ][ ... ]

```

The stream:

- Buffers incoming data internally
- Does NOT respect message boundaries
- Only guarantees byte order
    

---

## 4. `stream.read(16)` — Header Read

```js
header = stream.read(16)

```

### What this does internally:

- If **≥ 16 bytes** are buffered:
    
    - Remove 16 bytes from the internal buffer
    - Return them as a **new Buffer object**
        
- If **< 16 bytes** are buffered:
    
    - Return `null`
    - Do not remove anything
        

### Important guarantees:

- `header` is a **stable Buffer**
- It will NOT be reused or mutated by Node
- It is independent of future reads
    

---

## 5. Why the `while` Loop Exists

```js
while ((header = stream.read(16)) !== null) {

```

A single `"readable"` event may represent:

```js
[H][P][H][P][H][P]

```

The loop:

- Drains **all complete records**
- Avoids waiting for extra events
- Improves performance and correctness
    

---

## 6. `stream.read(32)` — Payload Read

```js
const payload = stream.read(32);

```

This attempts to read the payload corresponding to the header.

Two outcomes:

### Case A — Payload is available

- `payload` is a **new Buffer(32 bytes)**
- Independent from `header`
- Safe to process
    

### Case B — Payload is NOT available

- `payload === null`
- Header was read too early
- Stream state must be restored
    

---

## 7. Why `unshift(header)` Is Required

```js
stream.unshift(header);

```

### What `unshift()` does:

- Pushes a Buffer **back to the front** of the stream’s internal buffer
- Restores the exact byte sequence
- Does NOT copy or modify data
- Uses the **same Buffer reference**
    

### Why this is necessary:

Without `unshift()`:

- Header bytes are lost
- Stream becomes misaligned
- All future parsing is corrupted
    

This is **parser backtracking**.

---

## 8. Why `return` (Not `continue`)

```js
return;
```

This:

- Exits the `"readable"` handler
- Stops parsing **for now**
- Hands control back to Node
    

Node will emit `"readable"` again **only when more data arrives**.

This avoids:

- Busy loops
- CPU spin
- Re-reading incomplete data
    

---

## 9. Buffer Ownership and Safety

### Key facts:

- `header` and `payload` are **different Buffer objects**
- They do **not share memory**
- They remain valid until GC
- Stream will never overwrite them
    

### After `handleRecord(header, payload)`:

- Stream has already advanced
- Future reads are unaffected
    

---

## 10. Full Execution Timeline

### Incoming data

```js
Chunk 1: [16 header][10 payload]

```

### First `"readable"` event

```js
read(16) → header
read(32) → null
unshift(header)
return

```

Buffer restored:

```js
[16 header][10 payload]

```

---

### More data arrives

```js
Chunk 2: [22 payload]

```

Buffer:

```js
[16 header][32 payload]

```

---

### Second `"readable"` event

```js
read(16) → header
read(32) → payload
handleRecord()

```

✔ No data loss  
✔ No duplication  
✔ Correct framing

---

## 11. Invariant This Code Maintains

> **The stream buffer is always aligned at record boundaries**

This invariant is what makes the code correct.

---

## 12. Why This Pattern Is Production-Grade

✔ Works across chunk boundaries  
✔ Deterministic parsing  
✔ No partial records  
✔ No memory corruption  
✔ Used in real protocols and DB drivers

---

## 13. One-Line Mental Model (Put This in Notes)

> **Read → verify completeness → commit OR rewind**

---

## Final Summary

- `"readable"` gives you control
- `read(n)` gives you precision
- Each read returns a stable Buffer
- `unshift()` restores state safely
- `return` waits for more data
- `while` drains all complete records
    

This code turns a byte stream into a **correct, reliable record parser**.