# 2. `DataView` — Why It Exists and When You Need It

Typed Arrays are fast, but they assume **structure**.

What if your data:

- Mixes types?
    
- Has headers?
    
- Needs endianness control?
    

That’s where `DataView` comes in.

---

## 2.1 What `DataView` Is

A `DataView` is:

- A low-level view over an `ArrayBuffer`
    
- Allows reading/writing at **any offset**
    
- Allows explicit **endianness control**
    

```js
const buffer = new ArrayBuffer(8);
const view = new DataView(buffer);

```

---

## 2.2 Typed Arrays vs DataView

|Feature|TypedArray|DataView|
|---|---|---|
|Speed|Fast|Slower|
|Fixed layout|Yes|No|
|Mixed types|No|Yes|
|Endianness control|No|Yes|

### Rule

- Structured numeric arrays → TypedArray
    
- Binary formats / protocols → DataView
    

---

## 2.3 Endianness (This Is Why DataView Exists)

### Problem

Network protocols are **big-endian**  
Most CPUs are **little-endian**

Typed arrays **hide this**.

### DataView makes it explicit

```js
view.setUint32(0, 0xdeadbeef, false); // big-endian

```

Without DataView, your protocol breaks on some platforms.

---

## 2.4 Real-World Usage Pattern: Protocol Parsing

### Packet layout

```js
| version (1) | flags (1) | length (2) | timestamp (4) |

```

### Parsing

```js
function parsePacket(buffer) {
  const view = new DataView(buffer);
  return {
    version: view.getUint8(0),
    flags: view.getUint8(1),
    length: view.getUint16(2, false),
    timestamp: view.getUint32(4, false)
  };
}

```

This pattern appears in:

- HTTP/2
    
- TLS
    
- Database protocols
    
- Media containers
    

---

## 2.5 Writing Binary Data (Encoding)

```js
const buffer = new ArrayBuffer(8);
const view = new DataView(buffer);

view.setUint16(0, 0xABCD, false);
view.setUint32(2, Date.now() >>> 0, false);

```

This is how **file formats are generated**.