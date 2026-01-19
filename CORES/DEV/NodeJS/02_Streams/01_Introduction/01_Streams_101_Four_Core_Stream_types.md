# Streams 101: Understanding the Four Core Stream Types

Node.js streams are not just an API; they are a **pattern for handling data efficiently**. Before you start coding, you need to understand the **four core types**, how they differ, and when to use each.

---

## 1. Readable Streams

### **How They Work**

A **readable stream** represents a source of data that you can **read from**. Examples include:

- Files (`fs.createReadStream`)
- HTTP request bodies (`req` in `http.createServer`)
- Sockets
    

Readable streams **emit data in chunks**, allowing you to process large data sets without buffering everything in memory.

### **Key Methods and Events**

- `.read([size])` → Pulls chunks from the internal buffer.
- `.pipe(destination)` → Automatically sends data to a writable stream.
- `.on('data', chunk)` → Event-driven mode.
- `.on('end')` → Signals no more data.
- `.on('error', err)` → Handles errors in the stream.
    

### **When to Use**

- Reading large files
- Receiving network data
- Processing logs or live feeds
    

### **Debugging Tips**

- Check if `'end'` is emitted — if not, the stream might be paused or stuck.
- Use `stream.readableFlowing` to see if it’s in flowing or paused mode.
- Wrap with `stream.pipeline()` to catch errors automatically.
    

---

## 2. Writable Streams

### **How They Work**

A **writable stream** represents a destination you can **write data to**, chunk by chunk. Examples:

- Files (`fs.createWriteStream`)
- HTTP responses (`res` in `http.createServer`)
- TCP sockets
    

Writable streams **handle backpressure** automatically — if the destination is slow, `.write()` returns `false`, signaling you to wait for the `'drain'` event.

### **Key Methods and Events**

- `.write(chunk)` → Write a chunk to the stream.
- `.end([chunk])` → Finish writing and close the stream.
- `.on('drain')` → Signals you can resume writing.
- `.on('finish')` → Indicates all data has been written.
- `.on('error', err)` → Catches errors.
    

### **When to Use**

- Sending files over HTTP
- Logging to files or consoles
- Writing to database streams or network sockets
    

### **Debugging Tips**

- If `.write()` returns `false` and `'drain'` never fires, the stream may be blocked.
- Always handle `'error'` — ignoring it can crash your process.
- Use `stream.finished(stream, callback)` to detect when the stream is done safely.
    

---

## 3. Duplex Streams

### **How They Work**

A **duplex stream** is both **readable and writable**. You can **read from it and write to it simultaneously**. Examples:

- TCP sockets (`net.Socket`)
- `zlib` streams (e.g., gzip compression/decompression streams)
- WebSocket wrappers
    

Duplex streams are essential when the source and destination are both active — like bidirectional communication channels.

### **Key Methods and Events**

- Combines readable and writable stream methods: `.read()`, `.write()`, `.pipe()`, `.on('data')`
- Backpressure is handled independently for reading and writing
    

### **When to Use**

- Networking protocols
- Pipes that modify data in place
- Bidirectional streams like SSH, WebSocket, or database connections
    

### **Debugging Tips**

- Ensure both sides are consuming data; unconsumed readable chunks can block writing.
- Watch `'data'` events to verify reading is active.
- Use `.unpipe()` if multiple pipelines may interfere.
    

---

## 4. Transform Streams

### **How They Work**

A **transform stream** is a special kind of duplex stream that **modifies data as it passes through**. Think of it as a “filter” or “processor.”

- Example transformations: compression, encryption, data parsing, formatting
    

The key difference: **input data is transformed before output**, unlike a plain duplex stream where read and write are independent.

### **Key Methods**

- `_transform(chunk, encoding, callback)` → Define how to transform data
- Can be piped into other streams
    

### **When to Use**

- Compressing or decompressing files (`zlib.createGzip()`)
- Parsing CSV, JSON, or logs in a streaming fashion
- Encrypting/decrypting data on the fly
    

### **Debugging Tips**

- If output is missing or delayed, ensure `_transform` calls the callback.
- Watch for errors in the pipeline; transform streams propagate errors to all connected streams.
- Use `stream.pipeline()` for safer composition.
    

---

## 5. How They Differ — Quick Comparison

|Stream Type|Read|Write|Modify Data|Examples|
|---|---|---|---|---|
|Readable|✅|❌|❌|fs.createReadStream, HTTP request|
|Writable|❌|✅|❌|fs.createWriteStream, HTTP response|
|Duplex|✅|✅|❌|net.Socket, zlib streams|
|Transform|✅|✅|✅|gzip, crypto, CSV parsers|

**Summary:**

- **Readable** = source of data
- **Writable** = destination for data
- **Duplex** = bidirectional stream
- **Transform** = process data while passing through
    

---

## 6. Debugging Streams in General

1. **Check Flowing Mode**
    
    - `readableFlowing` tells if data is automatically emitted.
        
2. **Always Handle Errors**
    
    - Streams without error handling can crash your process.
        
3. **Use `stream.pipeline()`**
    
    - Safely connects multiple streams with automatic error handling.
        
4. **Inspect Backpressure**
    
    - `.write()` return value and `'drain'` event are critical for writable streams.
        
5. **Log Events**
    
    - `'data'`, `'end'`, `'finish'`, `'drain'`, `'error'` — watching these gives insight into where the stream is stuck.
        

---

## ✅ Conclusion

Understanding **readable, writable, duplex, and transform streams** is the first step toward mastering Node.js streams.

- **Readable** = pull data from somewhere
- **Writable** = push data somewhere
- **Duplex** = both at the same time
- **Transform** = process data on the fly
    

Debugging streams revolves around **flow control, backpressure, and error events**. Once you are comfortable with these four types and their behaviors, you can start **building pipelines, chaining streams, and handling large-scale I/O efficiently**.