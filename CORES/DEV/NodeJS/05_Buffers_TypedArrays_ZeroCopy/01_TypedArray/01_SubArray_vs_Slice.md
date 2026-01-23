# 1. `subarray()` vs `slice()` (This Is a Big Deal)

This is one of the **most common performance misunderstandings** in JS.

## The One-Line Truth

|Method|Copies memory?|Shares memory?|
|---|---|---|
|`subarray()`|❌ No|✅ Yes|
|`slice()`|✅ Yes|❌ No|

This difference is **intentional** and **fundamental**.

---

## 1.1 `subarray()` — View on the Same Memory

### Example

```js
const buffer = new ArrayBuffer(10);
const a = new Uint8Array(buffer);
const b = a.subarray(0, 5);

```

What happened:

- `a` and `b` point to the **same ArrayBuffer**
    
- `b` is just a different window
    

```js
b[0] = 255;
console.log(a[0]); // 255

```

### Memory diagram

```js
ArrayBuffer
[ FF 00 00 00 00 00 00 00 00 00 ]
   ↑ a
   ↑ b (first 5 bytes)

```

### Why `subarray()` exists

- Zero-copy parsing
    
- Sliding windows
    
- Protocol framing
    
- Streaming chunk reuse
    

### Real-world use

- Network packet headers
    
- Audio frame windows
    
- Image tiles
    
- Streaming protocols
    

---

## 1.2 `slice()` — Copy the Bytes

### Example

```js
const c = a.slice(0, 5);

```

What happened:

- New ArrayBuffer created
    
- Bytes copied
    
- Independent lifetime
    

```js
const c = a.slice(0, 5);

```

### When to use `slice()`

- You need ownership
    
- You need to store data long-term
    
- You want immutability
    
- You must avoid retaining large buffers
    

---

## 1.3 Common Bug (Very Important)

```js
const header = bigPacket.subarray(0, 16);

```

If `bigPacket` is 10MB:

- You just kept 10MB alive
    
- Even though you only need 16 bytes
    

**Fix**

```js
const header = bigPacket.slice(0, 16);

```

---

## Rule to Remember

> **Use `subarray()` for speed. Use `slice()` for safety.**