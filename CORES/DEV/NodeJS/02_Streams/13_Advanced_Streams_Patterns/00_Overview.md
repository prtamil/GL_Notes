# **Advanced Patterns: Multiplexing, Tee-ing, and Broadcasting Streams**

Streams in Node.js are powerful because they allow processing of large amounts of data efficiently, without loading everything into memory. While the basic `.pipe()` method works for single-source-to-single-sink scenarios, real-world applications often need **multiple consumers** or **fan-out pipelines**, where a single readable stream feeds data into several sinks. This is where advanced patterns like **multiplexing**, **tee-ing**, and **broadcasting** come in.

---

## **1. Sending One Readable Source to Multiple Consumers**

A common scenario is a stream that produces data—say, a log file, a live sensor feed, or an HTTP request body—that multiple modules need to consume simultaneously.

### **The Problem**

A standard readable stream can only be consumed once in flowing mode. If you try to `.pipe()` it to two writable streams, only the first will get the data. To solve this, we can **duplicate the stream**—a process called **tee-ing**.

### **Practical Example: Logging and Analytics**

```js
const { Readable, Writable, PassThrough } = require('stream');

// Simulated data source
const source = Readable.from(['metric1\n', 'metric2\n', 'metric3\n']);

// Two sinks
const logSink = new Writable({
  write(chunk, encoding, callback) {
    console.log('Log Sink:', chunk.toString().trim());
    callback();
  }
});

const analyticsSink = new Writable({
  write(chunk, encoding, callback) {
    console.log('Analytics Sink:', chunk.toString().trim().toUpperCase());
    callback();
  }
});

// Tee-ing using PassThrough streams
const tee1 = new PassThrough();
const tee2 = new PassThrough();

source.pipe(tee1);
source.pipe(tee2);

tee1.pipe(logSink);
tee2.pipe(analyticsSink);

```

**Output:**

```js
Log Sink: metric1
Analytics Sink: METRIC1
Log Sink: metric2
Analytics Sink: METRIC2
Log Sink: metric3
Analytics Sink: METRIC3

```
**Explanation:**

- `PassThrough` streams act as clones of the source.
    
- Each `PassThrough` can independently handle backpressure with its respective sink.
    
- This pattern avoids consuming the original source multiple times, which would fail in normal `.pipe()` usage.
    

---

## **2. Implementing Fan-Out Pipelines**

Fan-out pipelines allow one stream to branch into multiple transformations before reaching sinks. This is common in ETL (Extract-Transform-Load) systems, log processing, or real-time notifications.

### **Example: Transforming a CSV Stream for Multiple Outputs**

```js
const { Transform } = require('stream');

// Transform to uppercase
const upperCaseTransform = new Transform({
  transform(chunk, encoding, callback) {
    callback(null, chunk.toString().toUpperCase());
  }
});

// Transform to reverse string
const reverseTransform = new Transform({
  transform(chunk, encoding, callback) {
    callback(null, chunk.toString().split('').reverse().join(''));
  }
});

// Fan-out
source.pipe(new PassThrough()).pipe(upperCaseTransform).pipe(logSink);
source.pipe(new PassThrough()).pipe(reverseTransform).pipe(analyticsSink);

```

**Explanation:**

- Each branch gets a separate `PassThrough` from the source.
    
- The transforms run independently, and backpressure is handled per branch.
    
- This allows creating multiple pipelines from a single source without blocking each other.
    

---

## **3. Handling Backpressure Across Multiple Sinks**

When one sink is slow, it can cause the whole pipeline to stall. Handling this efficiently is critical in production systems.

### **Concepts**

- Each branch should **propagate its own backpressure** independently.
    
- Use `PassThrough` streams to **buffer data per consumer**, preventing a slow consumer from affecting others.
    
- Avoid writing custom fan-out loops with `source.on('data')` for large streams, as this can exhaust memory.
    

### **Practical Strategy: Independent Buffers**

```js
const fs = require('fs');

const fileSource = fs.createReadStream('large-file.txt');
const sink1 = fs.createWriteStream('copy1.txt');
const sink2 = fs.createWriteStream('copy2.txt');

const branch1 = new PassThrough();
const branch2 = new PassThrough();

fileSource.pipe(branch1).pipe(sink1);
fileSource.pipe(branch2).pipe(sink2);

// Each sink handles its own drain
sink1.on('drain', () => console.log('Sink1 ready for more'));
sink2.on('drain', () => console.log('Sink2 ready for more'));

```

**Key Takeaways:**

- Slow sinks automatically signal `drain` events.
    
- `PassThrough` streams prevent the slowest sink from blocking the source.
    
- Node.js streams’ internal buffering works per branch.
    

---

## **4. When to Use These Patterns**

- **Multiplexing / Tee-ing:** Multiple consumers need the exact same data simultaneously (logs, analytics, caching).
    
- **Fan-out Pipelines:** Different transformations or processing steps branch from the same source (ETL, real-time monitoring).
    
- **Broadcasting Streams:** When broadcasting events to multiple endpoints (WebSockets, notifications).
    

---

## **5. Pitfalls to Avoid**

- **Memory Blow-Up:** Avoid buffering too much data if sinks are slow; use small buffer sizes or streams in object mode.
    
- **Single Consumer Mistake:** Remember, readable streams can’t be `.pipe()`-ed multiple times without `PassThrough` or cloning.
    
- **Ignoring Backpressure:** Always handle `drain` events to prevent data loss or crashes.
    

---

## **Conclusion**

Multiplexing, tee-ing, and broadcasting are advanced patterns that make Node.js streams powerful for real-world applications. By splitting streams with `PassThrough` and handling backpressure per branch, you can efficiently feed multiple consumers from a single source without blocking or memory issues. These patterns unlock high-performance pipelines for logging, analytics, ETL, and real-time streaming systems.