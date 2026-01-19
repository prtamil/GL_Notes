# Readable Streams Deep Dive

Readable streams are **the foundation of Node.js streaming I/O**. They represent **sources of data** that Node can read incrementally, such as files, network sockets, or generated content. Understanding how they **flow** and how to **control that flow** is essential for building efficient, non-blocking applications.

---

## 1. How Data Flows From Sources to Node

Readable streams have an **internal buffer**. When data arrives from a source:

1. The source pushes chunks into the stream’s buffer.
2. Node decides when JavaScript can access these chunks.
3. Depending on the stream mode, data is either:
    
    - Automatically emitted to `'data'` events (**flowing mode**)
    - Held in the internal buffer until explicitly read (**paused mode**)
        

This allows Node to handle **large or slow data sources** without blocking the event loop.

---

## 2. Stream Modes: Paused vs. Flowing

### **Flowing Mode**

- Data is automatically read from the buffer and emitted via `'data'` events.
    
- Starts when you:
    
    - Add a `'data'` listener
    - Call `.resume()`
    - Pipe to a writable stream using `.pipe()`
        

**Example: Flowing Mode**

```js
const fs = require('fs');
const readable = fs.createReadStream('large-file.txt', { encoding: 'utf8' });

readable.on('data', chunk => {
  console.log('Received chunk:', chunk.length, 'characters');
});

readable.on('end', () => {
  console.log('Finished reading');
});

```

### **Paused Mode**

- Data stays in the internal buffer until you call `.read()`.
- Gives you **manual control** over when and how much data to read.
    

**Example: Paused Mode**

```js
const fs = require('fs');
const readable = fs.createReadStream('large-file.txt', { encoding: 'utf8' });

// Initially paused; must call read()
let chunk;
while ((chunk = readable.read(1024)) !== null) {
  console.log('Manually read chunk:', chunk.length);
}

// Listen for more data
readable.on('readable', () => {
  let chunk;
  while ((chunk = readable.read(1024)) !== null) {
    console.log('Readable event chunk:', chunk.length);
  }
});

```
---

## 3. Reading Data

### `.read([size])`

- Pulls data from the internal buffer.
- If you call `.read()` and there isn’t enough data, it returns `null`.
- Useful in **paused mode** for controlled processing.
    

### `'data'` Event

- Automatically pushes chunks to JavaScript.
- Always flowing mode.
- Convenient for simple use cases.
    

### `.pipe(destination)`

- Connects a readable stream to a writable stream.
- Handles backpressure automatically.
- Simplifies building pipelines.
    

**Pipe Example**

```js
const fs = require('fs');
const readable = fs.createReadStream('input.txt');
const writable = fs.createWriteStream('output.txt');

readable.pipe(writable); // Streams file content efficiently

```

---

## 4. Controlling Flow

### Pausing and Resuming

```js
const readable = fs.createReadStream('large-file.txt');

readable.on('data', chunk => {
  console.log('Got chunk:', chunk.length);
  readable.pause(); // Temporarily stop emitting
  setTimeout(() => readable.resume(), 1000); // Resume after 1 second
});

```

- **pause()** → stops flowing mode
- **resume()** → resumes flowing mode
    

This is useful when processing is slower than the source, allowing **backpressure management** manually.

### Listening to `'readable'`

- Instead of `'data'`, you can listen to `'readable'` in paused mode.
- Gives control over **how many bytes to consume** at a time.
    

**Readable Event Example**

```js
const readable = fs.createReadStream('large-file.txt', { highWaterMark: 32 * 1024 });

readable.on('readable', () => {
  let chunk;
  while ((chunk = readable.read(16 * 1024)) !== null) {
    console.log('Read 16KB chunk');
  }
});

```
---

## 5. Creating a Custom Readable Stream

Sometimes you need to **generate data on the fly**, like producing random numbers or streaming database results.

```js
const { Readable } = require('stream');

class NumberStream extends Readable {
  constructor(max) {
    super();
    this.current = 1;
    this.max = max;
  }

  _read(size) {
    const i = this.current++;
    if (i > this.max) {
      this.push(null); // End of stream
    } else {
      this.push(String(i)); // Push next number as string
    }
  }
}

// Consume the stream
const numbers = new NumberStream(5);
numbers.on('data', chunk => console.log('Number:', chunk.toString()));
numbers.on('end', () => console.log('All numbers read'));

```

**Output:**

```js
Number: 1
Number: 2
Number: 3
Number: 4
Number: 5
All numbers read

```

This example shows how **Readable streams can produce data dynamically**, not just from files or sockets.

---

## 6. Debugging Readable Streams

1. **Check flow mode:**
    
```js
console.log(readable.readableFlowing); // null / true / false

```
    
2. **Use `'readable'` event for precise control.**
    
3. **Always handle `'error'`:**  
    Streams can fail (file missing, network error).
    
4. **Backpressure awareness:**  
    When piping to a slow writable stream, the readable stream will **pause automatically** if needed.
    

---

## ✅ Conclusion

Readable streams are **the data sources in Node.js**. Key takeaways:

- **Flowing mode** → automatic `'data'` events, easy for simple pipelines.
- **Paused mode** → manual `.read()` calls, precise control.
- **Piping** → efficiently connects readable and writable streams.
- **Custom Readable** → dynamically generate data on the fly.
    

By mastering readable streams, you can **process large files, network streams, and dynamic data** efficiently without blocking the event loop.


