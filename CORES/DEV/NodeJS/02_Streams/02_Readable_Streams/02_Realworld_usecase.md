# Real-World Readable Stream Example: Log Processor

Imagine you have a **large log file** and you want to:

- Read it in chunks
- Process each line
- Handle slow processing gracefully
- Avoid memory overload
    

Here’s how you can do it with **Readable streams**.

---

```js
const fs = require('fs');
const readline = require('readline');

// Create a readable stream for the log file
const logStream = fs.createReadStream('server.log', {
  encoding: 'utf8',
  highWaterMark: 32 * 1024 // 32 KB chunks for faster reading
});

// Use readline to process logs line by line
const rl = readline.createInterface({
  input: logStream,
  crlfDelay: Infinity
});

// Track processing
let isProcessing = false;

// Listen for each line
rl.on('line', async (line) => {
  if (isProcessing) return; // optional: throttle if needed
  isProcessing = true;

  // Simulate async processing (e.g., storing to DB or sending to API)
  await new Promise(resolve => setTimeout(resolve, 100)); // 0.1s per line
  console.log('Processed line:', line);

  isProcessing = false;
});

// Handle end of stream
rl.on('close', () => {
  console.log('Finished processing all log lines.');
});

// Error handling
logStream.on('error', err => {
  console.error('Stream error:', err.message);
});

```

---

### **Why This Example Is Useful**

1. **Day-to-Day Use Case:** Reading logs, CSVs, or big JSON files.
2. **Memory Efficient:** Only one chunk (or one line) is processed at a time.
3. **Flow Control:** Simulates throttling via `isProcessing`.
4. **Integration Friendly:** Can send processed data to DB, API, or another stream.
5. **Backpressure Awareness:** `readline` consumes chunks line-by-line, preventing internal buffer overflow.
    

---

### **Other High-Level Usage Scenarios**

- **Reading uploaded files:** Handle user uploads without buffering the entire file in memory.
- **Streaming HTTP requests:** Consume data from clients as it arrives.
- **Streaming APIs:** Read data from external services (Twitter API, RSS feeds, stock prices) in chunks.
- **Processing CSV/JSON line-by-line:** Avoid loading huge datasets fully into memory.
- **Video/audio streaming:** Serve large media files efficiently without blocking the event loop.
    

---

This is the **typical “real-world” usage** of readable streams — **incremental, memory-efficient, and controlled**.