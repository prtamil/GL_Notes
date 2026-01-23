```js
const cluster = require('cluster');
const net = require('net');
const http = require('http');

if (cluster.isPrimary) {
  const worker = cluster.fork();

  const server = net.createServer({ pauseOnConnect: true }, (socket) => {
    // Transfer TCP socket to worker
    worker.send('socket', socket);
  });

  server.listen(3000, () => {
    console.log('Primary listening on 3000');
  });

} else {
  const server = http.createServer((req, res) => {
    res.end(`Handled by worker ${process.pid}\n`);
  });

  process.on('message', (msg, socket) => {
    if (msg === 'socket') {
      server.emit('connection', socket);
      socket.resume();
    }
  });

  server.listen(0); // internal only
}

```
## 1. `process` — what it is, what it points to, and why it works in both primary and worker

### What `process` actually is

`process` is a **global object injected by the Node.js runtime**.  
It represents **the current OS process** in which this JavaScript code is executing.

There is **no separate “primary process object” or “worker process object”** in your code.

Instead:

- The **same file** runs in **multiple OS processes**
- Each OS process has its **own `process` object**
- `process` always refers to **“me”**, not “the cluster”
    

### Why it points correctly in both roles

When you call:

`cluster.fork()`

Node:

- creates a **new OS process**
- re-executes the same JS file
- sets internal flags (`cluster.isPrimary`)
    
- wires up IPC
    

So:

- In the primary process  
    `process` = primary OS process
    
- In a worker process  
    `process` = that worker’s OS process
    

This is why:

- `process.pid` is different in each worker
- `process.on('message')` exists only in forked processes
- No import or wiring is needed
    

### Intent

`process` is Node’s **bridge to the OS process model**.  
It lets your JavaScript code:

- know _which_ process it is
- communicate with its parent
- receive sockets, signals, and messages
    

### Key meaning (no ambiguity)

> `process` does not represent the cluster.  
> It represents **the currently running OS process**, whether that is primary or worker.

---

## 2. TCP socket handoff → HTTP handling

### (pauseOnConnect, socket transfer, and connection bridging)

### Context: why this exists at all

Node cluster workers:

- do not share memory
- cannot safely share HTTP sessions
    

If you want:

> “This client must always hit the same worker”

You must decide **before HTTP exists**.

HTTP comes _after_ TCP.

So routing must happen at the **TCP layer**.

---

### What the primary is doing (intent)

The primary process acts as a **TCP connection router**.

It:

1. accepts raw TCP connections
2. does _not_ parse HTTP
3. decides ownership
4. hands the socket to a worker
5. exits the picture
    

The primary is **not a web server**.

---

### Why `pauseOnConnect` matters

When a TCP connection is accepted:

- data may start flowing immediately
    

If data flows before the socket is transferred:

- it may be read by the wrong process
- HTTP parsing breaks
    

So:

- primary accepts the socket
- immediately pauses it
- transfers ownership
- worker resumes it
    

This guarantees **no data loss**.

---

### What “pushing the socket to the worker” really means

At the OS level:

- a TCP socket is a file descriptor
    

Node allows:

- file descriptors to be passed over IPC
    

So when primary does:

`worker.send('socket', socket)`

It is **transferring ownership** of that TCP connection to the worker process.

After this:

- primary must never touch the socket again
- the worker owns it fully
    

---

### Why the worker “creates HTTP on top of it”

The worker:

- already has an HTTP server
- that server expects sockets via a `'connection'` event
    

By doing:

`server.emit('connection', socket)`

The worker is saying:

> “Treat this socket exactly as if you accepted it yourself.”

From the HTTP server’s point of view:

- there is **no difference**
- it parses HTTP normally
- request handling is unchanged
    

This is not a hack — it is **explicitly how Node’s HTTP server is built**.

---

### Why `server.listen(0)` exists

The worker:

- must activate its HTTP server
- must _not_ expose a public port
    

Port `0` means:

- “bind internally”
- “do not accept external connections”
    

All traffic flows **only** through the primary.

---

### Intent, meaning, and mental model (clean)

**Intent**

- Keep workers stateful
- Keep routing centralized
- Avoid external session storage
    

**Meaning**

- Primary = TCP router
- Worker = HTTP execution context
    

**Mental model**

> The worker does not “create” the connection.  
> It **inherits ownership** of a paused TCP socket and layers HTTP on top of it.

---

## Final unambiguous takeaway

1. `process` always refers to **the current OS process**, not the cluster.
2. The primary accepts TCP **only to decide ownership**, not to serve requests.
3. Sockets are paused, transferred, then resumed to guarantee correctness.
4. Workers do not accept connections — they **receive them**.
5. HTTP is layered **after routing**, not before.
    

This pattern feels awkward because it exposes **OS-level truth** directly.  
That discomfort is a sign you’re understanding it correctly.