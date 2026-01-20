```js
function write() {
  while (i < 1_000_000) {
    const chunk = `Line ${i}\n`;
    const canContinue = stream.write(chunk);

    i++;

    if (!canContinue) {
      // Internal buffer is full — STOP writing
      stream.once('drain', write);
      return;
    }
  }

  stream.end();
}

```

## 1. What the `drain` Event _Really_ Means (No Hand-Waving)

### The internal reality

A writable stream has **two layers**:

`JavaScript writes  →  Stream internal buffer  →  OS / kernel / disk / socket`

- `.write(chunk)` **does not write to disk immediately**
- It pushes data into the **internal buffer**
- Node then asynchronously pushes that buffer to the OS
    

### When `.write()` returns `false`

This means:

> “The internal buffer is now **at or above `highWaterMark`**.  
> If you keep writing, memory will grow.”

**Nothing is broken. Nothing failed.**  
It’s simply **flow control**.

### What `drain` means

`drain` is emitted when:

> “Enough data has been flushed from the internal buffer  
> that it is now safe to resume writing.”

So:

- `false` → **producer must stop**
- `drain` → **producer may continue**
    

That’s it. No magic.

---

## 2. Why `drain` Is an _Event_, Not a Callback

Node cannot tell you _when_ the OS will accept more data:

- Disk speed varies
- Kernel buffers vary
- Network congestion varies
    

So Node does this:

- You **pause voluntarily**
- Node **notifies you asynchronously**
- You **resume exactly once**
    

This keeps JavaScript **non-blocking** and **memory-safe**.

---

## 3. Writable Stream Events (The Ones That Matter)

Here are the **important writable stream events**, with blunt meanings:

### `drain` ⭐ (Most important)

`stream.on('drain', () => {})`

- Internal buffer dropped below `highWaterMark`
- Safe to resume `.write()`
- Only emitted **after `.write()` returned false**
    

---

### `finish`

`stream.on('finish', () => {})`

- `.end()` was called
- All buffered data has been flushed
- JavaScript side is completely done
    

⚠️ **Not** the same as “file closed”

---

### `close`

`stream.on('close', () => {})`

- Underlying resource (file descriptor, socket) is closed
- May happen **after** `finish`
- Or without `finish` if stream is destroyed
    

---

### `error`

`stream.on('error', err => {})`

- Disk failure
- Permission issue
- Broken pipe
- Stream is no longer usable
    

Always handle this in real code.

---

### `pipe` / `unpipe`

Used mostly when streams are connected together. Less relevant here.

---

## 4. Now Let’s Explain _Your Code_ Line by Line

### The Code Again

```js
function write() {
  while (i < 1_000_000) {
    const chunk = `Line ${i}\n`;
    const canContinue = stream.write(chunk);

    i++;

    if (!canContinue) {
      // Internal buffer is full — STOP writing
      stream.once('drain', write);
      return;
    }
  }

  stream.end();
}

```

---

## 5. Step-By-Step Execution (What Actually Happens)

### Step 1: First call to `write()`

- `while` loop starts
- Chunks are generated fast (pure JS)
- `.write(chunk)` pushes data into stream buffer
    

So far:

- JS is faster than disk
- Buffer starts filling
    

---

### Step 2: Buffer hits `highWaterMark`

At some iteration:

`const canContinue = stream.write(chunk); // returns false`

This means:

- Buffer is “full enough”
- Disk is behind
- Node is protecting memory
    

---

### Step 3: Producer pauses itself

```js
if (!canContinue) {
  stream.once('drain', write);
  return;
}

```

Key things happening here:

- **We stop the loop immediately**
- We **do not write more data**
- We register a **one-time listener** for `drain`
- We **return control to the event loop**
    

⚠️ This `return` is critical  
Without it, you would keep writing and defeat backpressure.

---

## 6. What Happens While We’re Paused?

While JavaScript is idle:

- Node pushes buffered data to disk (async)
- libuv + kernel do the slow work
- Internal buffer shrinks
    

Eventually:

- Buffer drops below `highWaterMark`
- Node emits `drain`
    

---

## 7. `drain` Fires → Writing Resumes

When `drain` fires:

`write(); // called again`

But note:

- `i` was preserved
- We continue exactly where we left off
- No duplicate writes
- No lost data
    

This creates a **cooperative loop** between JS and the OS.

---

## 8. Why `once('drain')` (Not `on`)?

Using `once` ensures:

- The handler runs **exactly one time**
- No accidental multiple resumes
- No memory leaks
    

Each pause → one resume → clean lifecycle.

---

## 9. Final Phase: Ending the Stream

Once `i` reaches 1,000,000:

`stream.end();`

This:

- Signals “no more data”
- Flushes remaining buffer
- Eventually emits `finish`
    

At this point:

- JS writing is done
- Disk may still be flushing bytes
    

---

## 10. Mental Model to Lock This In

Think of writable streams like this:

> `.write()` asks: “Can I keep going?”  
> `false` says: “Wait.”  
> `drain` says: “Continue.”

That’s the entire contract.

---

## 11. The One Rule You Must Remember

> **If you ignore `write()`’s return value,  
> you are writing broken Node.js code.**

This pattern is not optional, not advanced, not edge-case.

It is **the core of how Node safely handles output**.