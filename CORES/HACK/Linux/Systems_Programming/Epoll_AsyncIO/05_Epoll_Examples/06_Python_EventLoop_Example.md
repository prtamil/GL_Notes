Below is a **Node.js-style single-threaded event loop** in Python built directly on **epoll**, but **without coroutines**.

This is important because:

- Previous version → coroutine model (asyncio style)
    
- This version → callback model (Node.js style)
    
- Same core engine → epoll
    
- Different abstraction → scheduler + callbacks
    

This will help you see epoll at the lowest practical production architecture level.

---

# 🧠 Mental Model First (Before Code)

We are building 4 layers:

```
[ Application logic ]
        ↓
[ Callback scheduler ]
        ↓
[ Event loop core ]
        ↓
[ epoll syscall ]
        ↓
[ Linux kernel ]
```

This is exactly how Node.js works internally.

No threads.  
No coroutines.  
Only callbacks.

---

# Level 1 — What We Are Building

A production-style event loop that supports:

- epoll I/O notifications
    
- timer scheduling
    
- task queue
    
- non-blocking sockets
    
- high-performance echo server
    
- single thread
    

Architecture:

```
while True:
    run ready tasks
    run expired timers
    wait for epoll events
    call registered callbacks
```

---

# Level 2 — Core Design Concepts

We maintain:

1. Ready queue  
    Tasks to run immediately
    
2. Timer heap  
    Delayed execution (setTimeout)
    
3. fd → callback map  
    Who to call when fd becomes ready
    
4. epoll instance  
    Kernel notifier
    

This is almost 1:1 Node.js internals.

---

# Level 3 — Production Event Loop (No Coroutine)

## event_loop.py

```python
import socket
import select
import time
import heapq
from collections import deque

class EventLoop:
    def __init__(self):
        self.epoll = select.epoll()
        self.fd_callbacks = {}
        self.ready = deque()
        self.timers = []

    # -------------------------
    # Task Scheduling
    # -------------------------

    def call_soon(self, callback, *args):
        self.ready.append((callback, args))

    def call_later(self, delay, callback, *args):
        heapq.heappush(self.timers, (time.time() + delay, callback, args))

    # -------------------------
    # FD Registration
    # -------------------------

    def add_reader(self, sock, callback):
        fd = sock.fileno()
        self.fd_callbacks[fd] = (callback, sock)
        self.epoll.register(fd, select.EPOLLIN)

    def add_writer(self, sock, callback):
        fd = sock.fileno()
        self.fd_callbacks[fd] = (callback, sock)
        self.epoll.register(fd, select.EPOLLOUT)

    def remove_fd(self, sock):
        fd = sock.fileno()
        try:
            self.epoll.unregister(fd)
        except:
            pass
        self.fd_callbacks.pop(fd, None)

    # -------------------------
    # Core Loop
    # -------------------------

    def run_forever(self):
        while True:
            # 1) Run immediate tasks
            while self.ready:
                cb, args = self.ready.popleft()
                cb(*args)

            # 2) Run timers
            now = time.time()
            while self.timers and self.timers[0][0] <= now:
                _, cb, args = heapq.heappop(self.timers)
                cb(*args)

            # 3) Calculate epoll timeout
            timeout = 1
            if self.timers:
                timeout = max(0, self.timers[0][0] - time.time())

            # 4) Wait for kernel events
            events = self.epoll.poll(timeout)

            # 5) Dispatch events
            for fd, event in events:
                if fd in self.fd_callbacks:
                    cb, sock = self.fd_callbacks[fd]
                    cb(sock)
```

---

# Level 4 — Echo Server Using Callback Model

## echo_server.py

```python
import socket
from event_loop import EventLoop

loop = EventLoop()

def handle_client(sock):
    try:
        data = sock.recv(4096)
        if not data:
            loop.remove_fd(sock)
            sock.close()
            return
        sock.sendall(data)
    except BlockingIOError:
        pass

def accept_connection(server_sock):
    conn, _ = server_sock.accept()
    conn.setblocking(False)
    loop.add_reader(conn, handle_client)

def start_server():
    server = socket.socket()
    server.setblocking(False)
    server.bind(("0.0.0.0", 9000))
    server.listen()

    loop.add_reader(server, accept_connection)

start_server()
loop.run_forever()
```

---

# Level 5 — Client

```python
import socket

s = socket.socket()
s.connect(("127.0.0.1", 9000))

while True:
    msg = input(">> ").encode()
    s.send(msg)
    print(s.recv(4096).decode())
```

---

# Deep Explanation (Multi-Level Understanding)

---

## Level A — Kernel Level

epoll maintains:

```
interest list  → fds we care about
ready list     → fds ready right now
```

Kernel updates ready list automatically.

Your process sleeps inside:

```
epoll_wait()
```

CPU usage = near zero.

---

## Level B — Event Loop Level

Your loop does:

1. Run immediate callbacks
    
2. Run expired timers
    
3. Sleep inside epoll_wait
    
4. Wake when:
    
    - socket readable
        
    - socket writable
        
    - timer expired
        

---

## Level C — Scheduler Level

We built two schedulers:

### Immediate scheduler

```
call_soon()
```

Like:

```
process.nextTick() in Node
```

### Timer scheduler

```
call_later()
```

Like:

```
setTimeout()
```

---

## Level D — I/O Scheduling

Instead of:

```
await sock.recv()
```

We do:

```
loop.add_reader(sock, callback)
```

Meaning:

"Call this function when socket readable"

---

# Code Flow (Important Mental Model)

Connection arrives:

```
kernel → epoll → event loop → accept_connection()
```

Client sends data:

```
kernel marks fd ready
→ epoll wakes
→ event loop calls handle_client()
→ recv()
→ send()
```

No threads.  
No coroutine.  
Just callbacks.

---

# Why This Is Production Quality

This design scales because:

- O(1) epoll notifications
    
- No thread overhead
    
- No blocking
    
- No polling loops
    
- Timer heap is O(log n)
    

This is the same model used in:

- Node.js
    
- Redis
    
- Nginx
    
- libuv
    

---

# Coroutine vs Callback (Key Insight)

Coroutine model:

```
Looks synchronous
Easier to read
```

Callback model:

```
More explicit
More control
Closer to kernel
```

Both use SAME epoll underneath.

---

# The Final Deep Insight

There are only 3 real things happening:

1. Kernel detects readiness
    
2. epoll reports readiness
    
3. Event loop calls function
    

Everything else (asyncio, Node, Go) is just abstraction.

---

# Ultimate Mental Model

Think like this:

```
Kernel = sensor network
epoll  = notification inbox
Event loop = manager
Callbacks = workers
```

Manager waits.  
Sensor triggers.  
Manager assigns worker.  
Worker finishes.  
Manager waits again.

---

# If You Want Next Level

Next step to reach expert understanding:

- Add EPOLLET support
    
- Add EPOLLONESHOT
    
- Add task priority scheduler
    
- Add worker thread pool
    
- Build HTTP server on top
    

That is exactly how Node.js and Nginx evolved.