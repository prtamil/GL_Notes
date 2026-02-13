## Introduction to `epoll` in Linux: Why It Exists and How It Works

Modern network servers must handle thousands or even hundreds of thousands of simultaneous connections. A web server, chat server, or database cannot afford to block on a single client while others are waiting. The operating system must provide a way for programs to efficiently monitor many file descriptors (sockets, pipes, etc.) and act only when something interesting happens. This is the problem that `epoll` was designed to solve.

### Why `epoll` Is Needed

Before `epoll`, Linux programs used `select()` and later `poll()` to monitor multiple file descriptors. These mechanisms work, but they have a major limitation: they repeatedly scan all file descriptors to check which ones are ready for input/output. This becomes slow as the number of connections grows.

For example:

- With 10 connections, scanning is fast.
    
- With 10,000 connections, scanning becomes expensive.
    
- With 100,000 connections, performance drops significantly.
    

The core issue is that `select()` and `poll()` are O(n), meaning their cost grows linearly with the number of file descriptors. Even if only one connection has data, the kernel still checks all of them.

`epoll` was introduced to solve this scaling problem. Instead of repeatedly asking, “Which file descriptors are ready?”, a program tells the kernel:

> “Here are the file descriptors I care about. Notify me only when one of them becomes ready.”

The kernel then keeps track of readiness internally and wakes the program only when needed. This makes `epoll` highly efficient and scalable, which is why it is used by high-performance systems such as Nginx, Redis, Node.js (via libuv), and Java Netty.

### The Event-Driven Model

`epoll` enables an event-driven programming model. Instead of looping through connections and checking each one, the program sleeps while the kernel monitors activity. When data arrives, a socket becomes writable, or a new client connects, the kernel notifies the application.

This allows a single-threaded program to handle thousands of connections efficiently.

### The Core `epoll` System Calls

There are three main system calls used in `epoll`. Together, they create an event monitoring mechanism inside the kernel.

#### 1) `epoll_create1()`

**Purpose:** Create an epoll instance.

**Prototype:**

```c
int epoll_create1(int flags);

```

**Parameters:**

- `flags`: Usually set to `0`. One optional flag is `EPOLL_CLOEXEC`, which ensures the epoll file descriptor is closed during an `exec()` call.
    

**Return value:**

- On success: returns a file descriptor representing the epoll instance.
    
- On failure: returns `-1` and sets `errno`.
    

Conceptually, this creates a kernel object that contains:

- An “interest list” (file descriptors you want to monitor)
    
- A “ready list” (file descriptors currently ready for I/O)
    

#### 2) `epoll_ctl()`

**Purpose:** Add, modify, or remove file descriptors from the interest list.

**Prototype:**

```c
int epoll_ctl(int epfd, int op, int fd, struct epoll_event *event);

```

**Parameters:**

- `epfd`: The epoll instance file descriptor returned by `epoll_create1()`.
    
- `op`: Operation to perform:
    
    - `EPOLL_CTL_ADD` → Add a file descriptor.
        
    - `EPOLL_CTL_MOD` → Modify an existing entry.
        
    - `EPOLL_CTL_DEL` → Remove a file descriptor.
        
- `fd`: The file descriptor to monitor (socket, pipe, etc.).
    
- `event`: Pointer to a structure describing what events to watch for.
    

The `struct epoll_event` typically contains:

- `events`: Bitmask of events (e.g., `EPOLLIN` for read-ready, `EPOLLOUT` for write-ready).
    
- `data`: User-defined data, often used to store the file descriptor itself.
    

**Return value:**

- `0` on success.
    
- `-1` on failure, with `errno` set.
    

This call tells the kernel: “Watch this file descriptor and notify me when specific events happen.”

#### 3) `epoll_wait()`

**Purpose:** Wait for events to occur on monitored file descriptors.

**Prototype:**

```c
int epoll_wait(int epfd, struct epoll_event *events, int maxevents, int timeout);

```

**Parameters:**

- `epfd`: The epoll instance.
    
- `events`: Array where the kernel will store triggered events.
    
- `maxevents`: Maximum number of events to return.
    
- `timeout`:
    
    - `-1` → Wait forever.
        
    - `0` → Return immediately.
        
    - Positive value → Wait up to that many milliseconds.
        

**Return value:**

- A positive number: count of ready file descriptors.
    
- `0`: Timeout occurred, no events.
    
- `-1`: Error occurred.
    

This is the call where the program usually blocks. The kernel puts the process to sleep and wakes it only when one or more monitored file descriptors become ready.

### Basic Usage Flow

A typical `epoll` program follows this sequence:

1. Create an epoll instance using `epoll_create1()`.
    
2. Open sockets or other file descriptors.
    
3. Register them using `epoll_ctl(EPOLL_CTL_ADD)`.
    
4. Enter a loop:
    
    - Call `epoll_wait()` to get ready events.
        
    - For each returned event:
        
        - Read data, write data, or accept new connections.
            
5. Repeat.
    

In practice, sockets are usually set to non-blocking mode. This ensures that when an event is triggered, the program can process it without getting stuck waiting on a slow client.

### Level-Triggered vs Edge-Triggered (Conceptual Note)

`epoll` supports two notification styles:

- **Level-triggered (default):** As long as data is available, the event keeps triggering.
    
- **Edge-triggered:** You are notified only when new data arrives. You must read everything at once or risk missing future notifications.
    

Level-triggered is easier to use. Edge-triggered can be more efficient but requires careful handling.

### Why `epoll` Scales Better

The key advantage of `epoll` is that the kernel does the work of tracking readiness. Instead of scanning thousands of file descriptors repeatedly, it maintains an internal structure and gives the application only the descriptors that are ready.

This leads to:

- Less CPU usage
    
- Fewer system calls
    
- Better performance with large numbers of connections
    

In technical terms:

- `select()` / `poll()` → O(n) scanning
    
- `epoll` → O(1) event delivery (in practical workloads)
    

### Conclusion

`epoll` is a fundamental Linux mechanism for building scalable, high-performance I/O systems. It allows applications to efficiently monitor many file descriptors and react only when necessary. By shifting the responsibility of tracking readiness into the kernel, it eliminates the inefficiencies of earlier approaches and enables modern event-driven server architectures.

Understanding `epoll` is an important step toward mastering Linux systems programming, network servers, and high-concurrency design.