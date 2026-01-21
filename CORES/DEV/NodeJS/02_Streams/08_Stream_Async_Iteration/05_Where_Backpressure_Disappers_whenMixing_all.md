# Where Backpressure Disappears

### When Mixing Streams, Promises, and Async Iterators

Backpressure is **not a property of async code**.  
It is a **contract between producer and consumer**.

The moment you break that contract — even unintentionally — Node will happily buffer until memory explodes.

---

## 1. The Core Rule (Memorize This)

> **Backpressure exists only while the consumer is _blocking_ the producer.**

If the producer can keep pushing while the consumer is busy elsewhere, backpressure is gone.

---

## 2. Safe Baseline: Pure Stream Pipeline

```js
readable
  .pipe(transform)
  .pipe(writable);

```

Why this is safe:

- `writable.write()` returns `false`
- upstream pauses automatically
- kernel buffers + JS buffers cooperate
- impossible to “forget” to await
    

You can’t accidentally outpace the consumer.

---

## 3. First Leak: Promises Inside Stream Handlers

### ❌ Common Bug

```js
readable.on('data', chunk => {
  asyncProcess(chunk); // promise ignored
});

```

### What Actually Happens

- `data` keeps firing
- promises accumulate
- memory usage grows
- backpressure is bypassed
    

This **looks async**, but streams **do not await promises**.

### ✅ Correct Pattern (Transform Stream)

```js
const { Transform } = require('stream');

const transform = new Transform({
  async transform(chunk, _, cb) {
    try {
      await asyncProcess(chunk);
      cb(null, chunk);
    } catch (e) {
      cb(e);
    }
  }
});

```

Here:

- the stream waits
- backpressure is preserved
- promises are serialized
    

---

## 4. Second Leak: Async Iterators + Unawaited Work

### ❌ The Silent Killer

```js
for await (const chunk of readable) {
  doAsyncWork(chunk); // ❌ not awaited
}

```

Why this is dangerous:

- iterator keeps pulling
- stream keeps producing
- work piles up in memory
    

You’ve turned a **controlled pull loop** into a **firehose**.

### ✅ Safe Version

```js
for await (const chunk of readable) {
  await doAsyncWork(chunk);
}

```

Now:

- next chunk is not requested
- producer remains paused
- memory stays bounded
    

---

## 5. Third Leak: Hidden Parallelism

### ❌ “I’ll Just Speed This Up”

```js
for await (const chunk of readable) {
  promises.push(doAsyncWork(chunk));
}

await Promise.all(promises);

```

This defeats backpressure entirely.

- readable drains ASAP
- everything buffers
- peak memory = full stream size
    

### ✅ Bounded Parallelism

```js
const pLimit = require('p-limit');
const limit = pLimit(5);

for await (const chunk of readable) {
  await limit(() => doAsyncWork(chunk));
}

```

Backpressure is now:

- **logical**, not stream-native
- but still bounded and safe
    

---

## 6. Fourth Leak: Stream → Async Iterator → Stream

### ❌ Dangerous Bridge

```js
for await (const chunk of readable) {
  writable.write(chunk); // ❌ ignoring return value
}

```

If `write()` returns `false`, you just **ignored backpressure**.

### ✅ Correct Bridge

```js
const { once } = require('events');

for await (const chunk of readable) {
  if (!writable.write(chunk)) {
    await once(writable, 'drain');
  }
}

```

You must **manually reintroduce backpressure**.

---

## 7. Fifth Leak: Readable.from(Promise / Array)

### ❌ Subtle Footgun

```js
Readable.from(hugeArray.map(x => asyncWork(x)));

```

Why this breaks:

- array is created eagerly
- promises are scheduled immediately
- memory spike happens before streaming begins
    

### ✅ Correct Pattern

```js
async function* generator() {
  for (const x of hugeArray) {
    yield await asyncWork(x);
  }
}

Readable.from(generator());

```

Now:

- one element at a time
- backpressure respected
    

---

## 8. The “Looks Safe but Isn’t” Zone

### `pipeline()` + async iteration inside

```js
await pipeline(
  readable,
  async function* (source) {
    for await (const chunk of source) {
      doAsync(chunk); // ❌
      yield chunk;
    }
  },
  writable
);

```

This **still leaks**, because:

- async generator pulls fast
- unawaited work escapes
    

Fix:

```js
for await (const chunk of source) {
  await doAsync(chunk);
  yield chunk;
}

```

---

## 9. Mental Checklist (Use in Code Reviews)

Whenever you see:

- `async` + streams
- `for await` loops
- promises inside `data` handlers
    

Ask:

1. **Is every async operation awaited?**
2. **Is parallelism bounded?**
3. **Does write() backpressure get honored?**
4. **Is buffering happening outside the stream?**
    

If any answer is “no” — backpressure is gone.

---

## 10. Production Rule of Thumb

> **Streams enforce backpressure structurally.  
> Async/await enforces it only by discipline.**

That’s why:

- infrastructure → streams
- business logic → async iterators
- boundaries → extreme caution
    

---

## Final Takeaway (Tattoo-Worthy)

> **Backpressure doesn’t disappear loudly.  
> It leaks quietly — one un-awaited promise at a time.**