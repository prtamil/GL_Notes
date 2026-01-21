## Short correction (important)

> ❌ **Node does NOT emit `"readable"` for every chunk**  
> ✅ Node emits `"readable"` **only when the stream becomes readable again**

That distinction matters a lot.

---

## Let’s walk through your exact scenario step-by-step

### Code in question

```js
while ((header = stream.read(16)) !== null) {
  ...
}

```

### Case: header is **not complete**

#### Internal buffer state

```js
[10 bytes only]

```

#### What happens

1. `"readable"` fires (buffer transitioned from empty → has some data)
2. `stream.read(16)` → returns `null`
3. `while` condition fails immediately
4. Callback exits naturally (no `return`, no loop)
    

✔ Nothing consumed  
✔ Nothing corrupted  
✔ Waiting state entered

---

## Now the key question:

> “When more chunks arrive, does Node emit `"readable"` again and again?”

### Answer (precise)

Node emits `"readable"` **only when this condition becomes true**:

```js
previously: not readable
now: readable

```

Not “every chunk”.

---

## What does “readable” actually mean?

Internally (simplified):

```js
readable = buffer.length > 0 AND stream is not flowing

```

But `"readable"` is emitted **edge-triggered**, not level-triggered.

---

## Timeline Example (Very Concrete)

### Chunk 1 arrives

```js
Buffer: [10 bytes]

```

- Buffer was empty → now has data
- `"readable"` emitted ✅
- `read(16)` → null
- Exit handler
    

---

### Chunk 2 arrives

```js
Buffer: [10 + 4 = 14 bytes]

```

- Stream was **already readable**
- Still not enough for `read(16)`
- ❌ `"readable"` is NOT emitted again
    

This is the subtle part people miss.

---

### Chunk 3 arrives

```js
Buffer: [16 bytes]

```

Now:

- Stream transitions from “cannot satisfy read(16)” → “can”
- `"readable"` is emitted again ✅
- Handler runs
- `read(16)` succeeds
    

---

## Why Node does it this way

If `"readable"` fired on **every chunk**, your handler would:

- Wake up unnecessarily
- Spin and return
- Waste CPU
    

Node avoids that.

---

## Compare with `"data"` (important contrast)

|Event|Behavior|
|---|---|
|`"data"`|Fires for every chunk|
|`"readable"`|Fires on **readability transitions**|

That’s why `"readable"` is perfect for **exact-size parsing**.

---

## Now let’s re-evaluate your statement

> “So every chunk node emits readable event again and again”

❌ **Not correct**

Correct version:

> Node emits `"readable"` when enough buffered data exists to make progress.

---

## One more subtle but critical point

Node does **not** know you want 16 bytes.

It emits `"readable"` when:
- Data arrives
- Or when internal buffering changes state
    

But the **loop logic** ensures:

- No work happens until enough data exists
    

That’s why this pattern is safe.

---

## Mental model to lock in

> `"readable"` = _“Try reading now.”_  
> Not = _“Data arrived.”_

---

## Final clarity sentence

> The while-loop protects correctness, and the `"readable"` event protects efficiency.

---

You’re now asking **runtime-level questions**, which is exactly right.