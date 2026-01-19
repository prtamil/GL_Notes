## **Use Case 1: Processing CSV Line-by-Line**

Here we’ll read a **large CSV file** and process it **row by row** without loading the entire file into memory. We’ll use **`readline`** with a readable stream.

```js
const fs = require('fs');
const readline = require('readline');

// Create a readable stream from CSV
const csvStream = fs.createReadStream('data.csv', {
  encoding: 'utf8',
  highWaterMark: 32 * 1024 // 32 KB chunks
});

// Use readline to process one line at a time
const rl = readline.createInterface({
  input: csvStream,
  crlfDelay: Infinity
});

// Process each row
rl.on('line', (line) => {
  // Split CSV columns
  const columns = line.split(',');
  console.log('Processed row:', columns);
});

// End of file
rl.on('close', () => {
  console.log('Finished processing CSV file.');
});

// Error handling
csvStream.on('error', (err) => {
  console.error('Stream error:', err.message);
});

```

**Key Points:**

- Reads CSV **incrementally**, line by line.
- **Memory efficient** even for huge files.
- Can integrate with **database inserts** or **analytics pipelines**.

## **Use Case 2: Video/Audio Streaming to Clients**

Here we’ll stream a **video file** to an HTTP client in **chunks** using a readable stream. This prevents loading the entire video into memory.

```js
const fs = require('fs');
const http = require('http');

const server = http.createServer((req, res) => {
  const filePath = 'video.mp4';
  const stat = fs.statSync(filePath);
  const fileSize = stat.size;

  // Set headers
  res.writeHead(200, {
    'Content-Type': 'video/mp4',
    'Content-Length': fileSize
  });

  // Create readable stream for video
  const videoStream = fs.createReadStream(filePath, {
    highWaterMark: 64 * 1024 // 64 KB chunks
  });

  // Stream video to client
  videoStream.on('data', (chunk) => {
    res.write(chunk);
  });

  videoStream.on('end', () => {
    res.end(); // finish response
    console.log('Video streaming complete.');
  });

  videoStream.on('error', (err) => {
    console.error('Stream error:', err.message);
    res.statusCode = 500;
    res.end('Server error');
  });
});

server.listen(8000, () => console.log('Server running on port 8000'));

```

**Key Points:**

- Streams video in **chunks**, keeping memory usage low.
- Handles **large files** efficiently.
- Can be enhanced with **range requests** for seeking.

## **Use Case3 : Reading Uploaded Files**

We’ll use **Node.js built-in `http` module** and handle an uploaded file in chunks with a **readable stream**. This is raw, no external libraries like `multer`—so you see exactly how streams work.

```js
const http = require('http');
const fs = require('fs');
const path = require('path');

const server = http.createServer((req, res) => {
  if (req.method === 'POST' && req.url === '/upload') {
    // Create a unique file path to save uploaded file
    const filePath = path.join(__dirname, 'uploads', `upload-${Date.now()}.bin`);
    const writable = fs.createWriteStream(filePath);

    console.log('Receiving file upload...');

    // req is a readable stream (incoming HTTP body)
    req.on('data', (chunk) => {
      console.log('Received chunk of size:', chunk.length);
      writable.write(chunk); // write chunk to file
    });

    req.on('end', () => {
      writable.end();
      console.log('File upload complete:', filePath);
      res.writeHead(200, { 'Content-Type': 'text/plain' });
      res.end('Upload successful');
    });

    req.on('error', (err) => {
      console.error('Error reading upload:', err.message);
      res.writeHead(500, { 'Content-Type': 'text/plain' });
      res.end('Upload failed');
    });

    writable.on('error', (err) => {
      console.error('Error writing file:', err.message);
      res.writeHead(500, { 'Content-Type': 'text/plain' });
      res.end('Upload failed');
    });
  } else {
    // Simple form for testing upload
    res.writeHead(200, { 'Content-Type': 'text/html' });
    res.end(`
      <form method="POST" action="/upload" enctype="multipart/form-data">
        <input type="file" name="file" />
        <button>Upload</button>
      </form>
    `);
  }
});

server.listen(8000, () => console.log('Server running at http://localhost:8000'));

```

---

### **Explanation**

1. **`req` as Readable Stream**
    
    - The incoming HTTP body is a readable stream.
    - Data arrives in **chunks** (`'data'` events), so you don’t buffer the whole file in memory.
        
2. **Writable Stream**
    
    - Each chunk is written to a file using `fs.createWriteStream`.
    - Backpressure is **automatically handled**; if the file system is slow, Node buffers internally and signals when ready.
        
3. **Error Handling**
    
    - Both the readable (`req`) and writable streams handle `'error'` events.
        
4. **End of Stream**
    
    - `'end'` signals that all chunks have been received.
    - The writable stream is closed with `.end()`.
        
5. **Real-World Usage**
    
    - Large file uploads (images, videos, CSVs)
    - Memory-safe processing of user uploads
    - Can integrate a **transform stream** for processing while uploading (e.g., resizing images or compressing files)
        

---

### **Optional Enhancement: Processing While Uploading**

You can insert a **transform stream** between `req` and `writable` to process the file on the fly:

```js
const { Transform } = require('stream');

const upperCaseTransform = new Transform({
  transform(chunk, encoding, callback) {
    // Just an example: convert upload content to uppercase
    callback(null, chunk.toString().toUpperCase());
  }
});

req.pipe(upperCaseTransform).pipe(writable);

```

This is **exactly how Node pipelines large uploads in production**, with **memory-efficient streaming** and optional real-time processing.