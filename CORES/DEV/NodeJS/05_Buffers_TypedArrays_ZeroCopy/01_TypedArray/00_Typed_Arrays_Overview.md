# Typed Arrays — Deep, Practical, In-Depth Guide

## 1. What a Typed Array _Actually_ Is (No Hand-Waving)

A **Typed Array is not memory**.

> A Typed Array is a **view** over an `ArrayBuffer`.

This distinction matters.

```js
ArrayBuffer  → owns memory
TypedArray   → interprets memory

```

### Why this design exists

- Memory allocation is expensive
    
- Interpretation can change
    
- Multiple interpretations should not copy data
    

---

## 2. ArrayBuffer — The Memory Owner

### Allocate memory

```js
const buffer = new ArrayBuffer(16);

```

That’s it.  
No reading. No writing. Just memory.

### Key properties

```js
buffer.byteLength // 16

```

- Fixed size
    
- Cannot grow
    
- Garbage collected when no references exist
    

---

## 3. Typed Arrays — Interpreting Memory

### The simplest view: bytes

```js
const bytes = new Uint8Array(buffer);

bytes[0] = 255;
bytes[1] = 128;

```

Now memory contains:

`FF 80 00 00 ...`

### Same memory, different interpretation

```js
const ints = new Uint16Array(buffer);
console.log(ints[0]); // interprets first 2 bytes as a number

```

No copy happened.  
Only interpretation changed.

---

## 4. Typed Array Families (Know These)

|Typed Array|Size|Common Use|
|---|---|---|
|`Uint8Array`|1 byte|Raw bytes, protocols|
|`Int16Array`|2 bytes|Audio|
|`Uint32Array`|4 bytes|Binary formats|
|`Float32Array`|4 bytes|Graphics, ML|
|`Float64Array`|8 bytes|Scientific|

### Rule

> **Always choose the smallest type that fits your data**

Memory layout matters.

---

## 5. Basic Use Cases (Start Here)

### Case 1: Binary data instead of JS arrays

```js
const data = new Uint8Array(1024);

```

Why better than `[]`?

- Contiguous memory
    
- No object overhead
    
- Faster iteration
    
- Predictable size
    

---

### Case 2: Encoding bytes manually

```js
const packet = new Uint8Array(4);
packet[0] = 1;   // version
packet[1] = 42;  // command

```

This is how **protocols** are built.

---

## 6. Typed Arrays + DataView (Critical)

Typed Arrays assume:

- Fixed type
    
- Platform endianness
    

### DataView exists for control

```js
const view = new DataView(buffer);
view.setUint32(0, 0xdeadbeef, false); // big-endian

```

### When to use DataView

- Network protocols
    
- File formats
    
- Cross-platform binary formats
    

Typed Arrays = speed  
DataView = correctness

---

## 7. Real-World Scenario 1: Network Protocol Parsing

### Packet format

```js
| version (1) | type (1) | length (2) | payload |

```

### Parsing without copying

```js
function parsePacket(buffer) {
  const view = new DataView(buffer);
  return {
    version: view.getUint8(0),
    type: view.getUint8(1),
    length: view.getUint16(2, false),
    payload: buffer.slice(4)
  };
}

```

This is **zero-copy parsing**.

Used in:

- Databases
    
- Game servers
    
- Message brokers
    

---

## 8. Typed Array Slicing (Views, Not Copies)

```js
const full = new Uint8Array(100);
const header = full.subarray(0, 10);

```

- `subarray()` = view
    
- No allocation
    
- Same memory
    

### Contrast

```js
full.slice(0, 10); // copies

```

Typed Arrays differ from `Buffer` here.

**Memorize this difference.**

---

## 9. Real-World Scenario 2: Audio Processing

### Audio samples

```js
const samples = new Int16Array(44100);

```

### Apply gain
```js
for (let i = 0; i < samples.length; i++) {
  samples[i] *= 0.8;
}

```

Why typed arrays?

- Exact sample format
    
- SIMD-friendly
    
- Fast math
    
- No GC pressure
    

This is how:

- DAWs
    
- Voice chat
    
- Audio codecs
    

work.

---

## 10. Typed Arrays in Graphics (WebGL)

WebGL **requires** typed arrays.

```js
const vertices = new Float32Array([
  0.0,  1.0,
 -1.0, -1.0,
  1.0, -1.0
]);

```

Why?

- GPU expects contiguous memory
    
- JS objects are useless here
    

Typed arrays are the **bridge to hardware**.

---

## 11. Real-World Scenario 3: File Formats

### Example: BMP header

```js
const header = new ArrayBuffer(54);
const view = new DataView(header);

view.setUint16(0, 0x4D42, true); // "BM"
view.setUint32(2, fileSize, true);

```

Binary formats are **typed array territory**.

---

## 12. Performance Characteristics (Very Important)

### What Typed Arrays give you

- Contiguous memory
    
- Predictable layout
    
- CPU cache friendliness
    
- Lower GC pressure
    

### What they don’t give you

- Dynamic resizing
    
- Rich methods
    
- Safety checks
    

They are **low-level tools**.

---

## 13. Common Mistakes (Avoid These)

### ❌ Treating them like normal arrays

```js
typed.push(5); // ❌

```

They are fixed-size.

---

### ❌ Copying when you don’t need to

```js
new Uint8Array(oldArray); // copy

```

Prefer views:

```js
oldArray.subarray(...)

```

---

### ❌ Wrong endianness

Network = big-endian  
Most CPUs = little-endian

Use `DataView` when in doubt.

---

## 14. Advanced: SharedArrayBuffer (Preview)

```js
const shared = new SharedArrayBuffer(1024);
const view = new Uint8Array(shared);

```

Used for:

- Workers
    
- Atomics
    
- Lock-free concurrency
    

This is how **high-performance multithreading** works in JS.

---

## 15. Mental Model Summary (Burn This In)

- `ArrayBuffer` owns memory
    
- Typed Arrays interpret memory
    
- `DataView` controls layout
    
- Views ≠ copies
    
- Memory is fixed-size
    
- Typed Arrays are for **systems work**