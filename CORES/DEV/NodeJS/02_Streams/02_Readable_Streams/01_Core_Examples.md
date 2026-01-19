# Example 1
Let’s create a **full, raw example of a readable stream** that demonstrates:

- Reading in **flowing mode**
- Using **pause()** and **resume()**
- Handling **errors manually**
- **No piping** — raw usage
    

This will give you a clear picture of how data flows internally and how you can control it.

```js
const fs = require('fs');

// Create a readable stream from a large file
const readable = fs.createReadStream('large-file.txt', {
  encoding: 'utf8',
  highWaterMark: 16 * 1024 // 16 KB chunks
});

// Event: Data received
readable.on('data', chunk => {
  console.log(`Received chunk of size: ${chunk.length}`);

  // Simulate slow processing
  readable.pause(); // Pause the stream
  console.log('Stream paused to process chunk...');

  setTimeout(() => {
    console.log('Processing done, resuming stream...');
    readable.resume(); // Resume the stream
  }, 1000); // simulate 1-second processing delay
});

// Event: End of file
readable.on('end', () => {
  console.log('All data read. Stream ended.');
});

// Event: Error handling
readable.on('error', err => {
  console.error('Stream encountered an error:', err.message);
});

// Event: Open file descriptor
readable.on('open', fd => {
  console.log('Stream opened with file descriptor:', fd);
});

// Event: Close file descriptor
readable.on('close', () => {
  console.log('Stream closed.');
});

```

### **Explanation**

1. **HighWaterMark**: Controls how much data the stream buffers internally (here 16 KB).
2. **Flowing mode**: Adding `'data'` listener automatically puts the stream in flowing mode.
3. **Pause & Resume**:
    
    - `.pause()` stops `'data'` events.
    - `.resume()` restarts `'data'` events after processing.
    - This simulates **backpressure handling** manually.
        
4. **Error Handling**: `'error'` event ensures the process does not crash if the file is missing or unreadable.
5. **Open/Close Events**: Optional, useful for logging or resource management.
    

---

### **How it behaves**

- The stream reads **16 KB chunks** at a time.
- Each chunk is **paused** while “processing” (simulated 1-second delay).
- After processing, the stream **resumes**, fetching the next chunk.
- Errors (e.g., file not found) are caught and logged.
    

---

This is **exactly how Node handles raw readable streams internally** without `.pipe()`.

# Example 2
**fully manual Readable Stream example** using **paused mode** and `.read()`. This gives you **complete control** over how much data you consume and when, unlike flowing mode with `'data'` events.
## Readable Stream Manual Mode Example (`.read()`)

```js
const fs = require('fs');

// Create a readable stream
const readable = fs.createReadStream('large-file.txt', {
  encoding: 'utf8',
  highWaterMark: 16 * 1024 // 16 KB chunks
});

// Initially in paused mode (default if no 'data' listener)
console.log('Stream created. Listening for readable events...');

// Listen for 'readable' event
readable.on('readable', () => {
  console.log('Readable event fired. Stream has data available.');

  let chunk;
  // Read chunks manually
  while (null !== (chunk = readable.read(8 * 1024))) { // read 8KB at a time
    console.log(`Manually read chunk of size: ${chunk.length}`);

    // Simulate processing delay
    const start = Date.now();
    while (Date.now() - start < 500) {} // 0.5s processing per chunk
  }
});

// Listen for end of stream
readable.on('end', () => {
  console.log('All data read. Stream ended.');
});

// Error handling
readable.on('error', err => {
  console.error('Stream error:', err.message);
});

// Optional: open and close events
readable.on('open', fd => console.log('File opened with descriptor:', fd));
readable.on('close', () => console.log('Stream closed.'));

```

### **How This Works**

1. **Paused Mode**
    
    - No `'data'` listener means the stream **starts in paused mode**.
    - Data is buffered internally but **not emitted automatically**.
        
2. **`readable` Event**
    
    - Fires whenever **data is available in the internal buffer**.
    - You decide **how many bytes to consume** with `.read(size)`.
        
3. **Manual `.read(size)`**
    
    - Returns `null` if there isn’t enough data.
    - You can read in **smaller chunks than highWaterMark** for fine-grained control.
    - Pauses automatically if you stop calling `.read()`.
        
4. **Simulated Processing**
    
    - In the example, we block for 0.5s per chunk to simulate heavy computation.
    - Notice the event loop **doesn’t get overwhelmed**, because we only process small chunks at a time.
        
5. **Error Handling**
    
    - `'error'` ensures you don’t crash the process if the file is missing or unreadable.
        
6. **Open & Close**
    
    - Useful for logging or managing resources (like closing file descriptors).
        

---

### **Key Takeaways**

- **Flowing mode** (`'data'`) = automatic, simple, less control.
- **Paused mode** (`.read()`) = manual, precise, better for **throttling or processing intensive tasks**.
- **HighWaterMark vs read(size)** = highWaterMark controls internal buffering, `read(size)` controls how much JS consumes at a time.

# Example 3
Let’s build a **full, realistic Readable Stream example** that combines:

- **Manual `.read()`** (paused mode)
- **Pause & resume control**
- **Error handling**
- **Chunked processing with simulated delays**
    

Think of this as a **mini Node-style file processor** — exactly how you’d handle large files or streams in real apps.

---

## Full Readable Stream Example: Manual Read + Pause/Resume + Error Handling

```js
const fs = require('fs');

// Create a readable stream for a large file
const readable = fs.createReadStream('large-file.txt', {
  encoding: 'utf8',
  highWaterMark: 16 * 1024 // 16 KB chunks buffered internally
});

// Track processing state
let isProcessing = false;

// Handle 'readable' event - triggered when data is available in the buffer
readable.on('readable', () => {
  // If already processing a chunk, skip until resume
  if (isProcessing) return;

  let chunk;
  while ((chunk = readable.read(8 * 1024)) !== null) { // read 8KB manually
    isProcessing = true; // mark as processing
    console.log(`Read chunk of size: ${chunk.length}`);

    // Pause stream while processing chunk
    readable.pause();
    console.log('Stream paused for processing...');

    // Simulate async processing with setTimeout
    setTimeout(() => {
      console.log('Processing chunk done. Resuming stream...');
      isProcessing = false;
      readable.resume(); // Resume stream for next chunk
    }, 1000); // simulate 1 second processing per chunk

    // Break the loop to wait for processing to finish
    break;
  }
});

// Stream ended
readable.on('end', () => {
  console.log('All data read. Stream ended.');
});

// Error handling
readable.on('error', err => {
  console.error('Stream error:', err.message);
});

// Optional: open/close logging
readable.on('open', fd => console.log('File opened, fd:', fd));
readable.on('close', () => console.log('Stream closed.'));

```

---

### **How This Works**

1. **Paused Mode**
    
    - No `'data'` listener keeps the stream in paused mode.
    - We control exactly when data is consumed with `.read(size)`.
        
2. **Manual `.read(size)`**
    
    - Reads **8 KB chunks** from the internal buffer at a time.
    - Returns `null` if there isn’t enough data, waiting for `'readable'` event.
        
3. **Pause & Resume**
    
    - Each chunk is processed individually.
    - `.pause()` stops new `'readable'` events while processing.
    - `.resume()` allows the next chunk to be read.
        
4. **Simulated Processing Delay**
    
    - `setTimeout` simulates heavy computation or slow I/O.
    - Shows how backpressure can be handled **manually** without blocking the event loop.
        
5. **Error Handling**
    
    - `'error'` catches file-not-found or other stream errors.
        
6. **Open & Close Events**
    
    - Useful for logging file descriptors or resource management.
        

---

### **Why This Is Useful**

- Full control over **how many bytes you read** at a time.
- You can implement **throttling**, **rate-limiting**, or **CPU-heavy processing** per chunk.
- Demonstrates **manual backpressure handling** without using `.pipe()`.
- Perfect mental model for **how Node handles streams internally**.