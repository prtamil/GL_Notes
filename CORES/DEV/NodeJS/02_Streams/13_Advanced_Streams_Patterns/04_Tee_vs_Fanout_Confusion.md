**tee and fan-out use the same branching logic**: you take a single readable stream and create **independent branches** using `PassThrough` (or a Transform). The **difference is in intent and downstream processing**:

---

### **Conceptual Distinction**

|Aspect|Tee / Multiplexing|Fan-Out Pipelines|
|---|---|---|
|**Purpose**|Duplicate the same data to multiple consumers|Split the stream for multiple **different processing paths**|
|**Transformations**|None (raw data stays the same)|Branches often have **Transform streams** for different operations|
|**Example**|Logs + analytics|ETL: log full CSV, extract age, mask names|
|**Backpressure Handling**|Independent per branch|Independent per branch|
|**Memory Efficiency**|Each branch handles its own buffering|Same, plus transformations happen streaming|

---

### **Simplified Rule of Thumb**

> **If the branches just duplicate the data → it’s Tee/Multiplexing.  
> If the branches transform/process the data differently → it’s Fan-Out.**

---

So under the hood, **both patterns rely on the same mechanism (`PassThrough` branching)**. The **semantic difference** comes from **what happens after the branch**:

- **Tee:** everything stays the same.
    
- **Fan-Out:** each branch modifies or filters data.
---
```js
/**
 * Node.js Streams: Tee (Multiplexing) vs Fan-Out Pipelines
 *
 * Demonstrates:
 * 1. Tee / Multiplexing - duplicate the same data to multiple consumers
 * 2. Fan-Out - branch the data for different transformations / processing
 */

const { Readable, PassThrough, Transform, Writable } = require('stream');

// ------------------------------
// Step 1: Source Stream
// ------------------------------
const source = Readable.from([
  'user_login:123\n',
  'user_purchase:456\n',
  'user_logout:123\n'
]);

// ------------------------------
// Tee / Multiplexing Example
// ------------------------------

// Purpose: duplicate the exact same data to multiple consumers
const tee1 = new PassThrough(); // Branch 1
const tee2 = new PassThrough(); // Branch 2

// Consumer 1: Logging
const logSink = new Writable({
  write(chunk, encoding, callback) {
    console.log('[TEE] LOG:', chunk.toString().trim());
    callback();
  }
});

// Consumer 2: Analytics (uppercase)
const analyticsSink = new Writable({
  write(chunk, encoding, callback) {
    console.log('[TEE] ANALYTICS:', chunk.toString().trim().toUpperCase());
    callback();
  }
});

// Pipe the same source to both branches
source.pipe(tee1).pipe(logSink);
source.pipe(tee2).pipe(analyticsSink);

// ------------------------------
// Fan-Out Pipelines Example
// ------------------------------

// Simulated CSV source for fan-out
const csvSource = Readable.from([
  'John,25,Engineer\n',
  'Alice,30,Designer\n',
  'Bob,22,Intern\n'
]);

// Branch 1: Log full CSV
const logCSV = new Writable({
  write(chunk, encoding, callback) {
    console.log('[FANOUT] LOG:', chunk.toString().trim());
    callback();
  }
});

// Branch 2: Extract age only
const ageTransform = new Transform({
  transform(chunk, encoding, callback) {
    const age = chunk.toString().split(',')[1];
    callback(null, age + '\n');
  }
});
const ageSink = new Writable({
  write(chunk, encoding, callback) {
    console.log('[FANOUT] AGE:', chunk.toString().trim());
    callback();
  }
});

// Branch 3: Mask names
const maskTransform = new Transform({
  transform(chunk, encoding, callback) {
    const parts = chunk.toString().split(',');
    parts[0] = parts[0][0] + '***'; // mask first letter
    callback(null, parts.join(',') + '\n');
  }
});
const maskedSink = new Writable({
  write(chunk, encoding, callback) {
    console.log('[FANOUT] MASKED:', chunk.toString().trim());
    callback();
  }
});

// Fan-out using PassThrough streams per branch
csvSource.pipe(new PassThrough()).pipe(logCSV);                // Branch 1
csvSource.pipe(new PassThrough()).pipe(ageTransform).pipe(ageSink);    // Branch 2
csvSource.pipe(new PassThrough()).pipe(maskTransform).pipe(maskedSink); // Branch 3

```

### **What This Example Shows**

#### **Tee / Multiplexing**

- The `source` stream is **duplicated exactly** using `tee1` and `tee2`.
    
- **No transformations** happen; each consumer sees **identical data**.
    
- Use case: logging + analytics from the same raw events.
    

#### **Fan-Out Pipelines**

- The `csvSource` stream is branched into **three separate pipelines**.
    
- Each branch performs **different transformations**:
    
    - Branch 1 logs the full CSV.
        
    - Branch 2 extracts ages.
        
    - Branch 3 masks names for privacy.
        
- Use case: ETL pipelines, media processing, analytics dashboards.
    

---

### **Key Takeaways**

|Pattern|Purpose|Downstream|Example|
|---|---|---|---|
|Tee / Multiplexing|Duplicate stream to multiple consumers|Identical data|Logs + Analytics|
|Fan-Out Pipelines|Branch stream for different processing|Transformed per branch|ETL: Log full CSV, extract age, mask names|

---

✅ **Conclusion:**

Even though the **code looks similar**, the **intent and downstream transformations** distinguish **tee vs fan-out**:

- Tee = duplicate raw data.
    
- Fan-out = branch for independent transformations or processing.