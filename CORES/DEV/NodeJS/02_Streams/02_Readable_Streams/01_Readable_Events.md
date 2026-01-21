## The Core Readable Events

### 1. `"readable"` — **Pull-based, manual control**

#### What it means

> “There _may_ be data available. You decide how much to read.”

#### When it fires

- When the internal buffer transitions from **not readable → readable**
- When data arrives that allows progress
- When you call `unshift()` and restore data
    

#### What you do inside it

You explicitly call:

```js
stream.read()
stream.read(n)

```

#### Example

```js
stream.on("readable", () => {
  let chunk;
  while ((chunk = stream.read()) !== null) {
    console.log(chunk);
  }
});


```

#### Key properties

- ✔ Pull-based
- ✔ Deterministic
- ✔ Required for `read(n)`
- ❌ More code
- ❌ Easier to misuse if you don’t loop correctly
    

#### Use `"readable"` when:

- Parsing binary protocols
- Reading fixed-size records
- Doing manual flow control
- Using `read(n)`
    

---

### 2. `"data"` — **Push-based, automatic flow**

#### What it means

> “Here is a chunk. I’m pushing it to you.”

#### When it fires

- As soon as data is available
- For **every chunk**
- Continues automatically until paused or ended
    

#### Example

```js
stream.on("data", (chunk) => {
  console.log(chunk);
});

```

#### Key properties

- ✔ Simple
- ✔ High throughput
- ❌ No control over chunk size
- ❌ No rewind
- ❌ Unsafe for structured parsing
    

#### Use `"data"` when:

- Streaming files to HTTP responses
- Logging
- Compression pipelines
- You don’t care about boundaries
    

---

### ⚠️ Important Rule

> **Never mix `"data"` and `"readable"` on the same stream**

Doing so switches modes unpredictably.

---

## Lifecycle Events

### 3. `"end"` — **No more data**

#### What it means

> “All data has been consumed.”

#### When it fires

- After the internal buffer is fully drained
- Only after all `"data"` or `"readable"` reads are done
    

#### Example

```js
stream.on("end", () => {
  console.log("Stream finished");
});

```

#### Notes

- `"end"` does NOT mean stream closed
- You can still clean up resources
    

---

### 4. `"close"` — **Underlying resource closed**

#### What it means

> “The underlying resource (file, socket) is closed.”

#### When it fires

- After `.destroy()`
- After file descriptor or socket closes
- May fire **with or without** `"end"`
    

#### Example

```js
stream.on("close", () => {
  console.log("Resource closed");
});

```

#### Key distinction

|Event|Meaning|
|---|---|
|`end`|No more data|
|`close`|Resource released|

---

## Error Handling

### 5. `"error"` — **Something went wrong**

#### What it means

> “An unrecoverable error occurred.”

#### When it fires

- I/O errors
- Parsing errors (if you emit them)
- Manual `destroy(err)`
    

#### Example

```js
stream.on("error", (err) => {
  console.error("Stream error:", err);
});

```

#### Rule (critical)

> **If you don’t listen for `"error"`, Node will crash**

---

## Mode Transition Events (Advanced)

### 6. `"pause"` — Stream paused

Triggered when:

```js
stream.pause();

```

Mostly informational.

---

### 7. `"resume"` — Stream resumed

Triggered when:

```js
stream.resume();

```

Mostly informational.

---

## How These Events Relate (Big Picture)

### Flowing vs Paused Mode

|Mode|Triggered by|Events|
|---|---|---|
|Flowing|`data` / `pipe()`|`"data"`, `"end"`|
|Paused|default / `"readable"`|`"readable"`, `"end"`|

Calling:

- `on("data")` → switches to flowing mode
- `pipe()` → switches to flowing mode
- `read()` → paused mode
    

---

## Event Comparison Table (Memorize This)

|Event|Who controls flow|Chunk size|Typical use|
|---|---|---|---|
|`readable`|You|Exact (`read(n)`)|Parsing|
|`data`|Node|Arbitrary|Streaming|
|`end`|Node|N/A|Completion|
|`close`|Resource|N/A|Cleanup|
|`error`|Failure|N/A|Safety|

---

## Why `"readable"` Exists at All

Because **real systems are structured**, not byte hoses.

Examples where `"data"` fails:

- Length-prefixed messages
- CSV / JSON line parsing
- Media containers
- Database wire protocols
    

---

## Mental Model (Lock This In)

> `"data"` = firehose  
> `"readable"` = measuring cup

---

## Final Takeaway

- Use `"data"` for **transport**
- Use `"readable"` for **meaning**
- Use `"end"` to finish
- Use `"error"` to survive