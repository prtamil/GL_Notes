# libuv Internals: epoll, kqueue, IOCP — What the Event Loop Actually Waits On

## 0. The Core Question This Essay Answers

> **What is the event loop actually doing when it “waits”?**

Not metaphorically.  
Not conceptually.  
**Literally.**

The answer is:  
**libuv blocks on the operating system’s I/O multiplexing primitive.**

---

## 1. The Stack, From JavaScript to Silicon

When Node “waits for I/O”, the call stack looks like this:

```js
JavaScript
↓
Node.js C++ bindings
↓
libuv
↓
OS I/O API (epoll / kqueue / IOCP)
↓
Kernel
↓
Hardware

```

The event loop is not magic.  
It is a **thin, disciplined wrapper** over OS facilities.

---

## 2. The Universal Problem: “Wait for Many Things”

Every OS must solve the same problem:

> **Wait until _any_ of many file descriptors becomes ready.**

Examples:

- Socket has data
- File read completed
- Timer expired
- Pipe writable
- Signal delivered
    

Busy-waiting is unacceptable.  
Spawning a thread per socket does not scale.

The solution is **I/O multiplexing**.

---

## 3. The Three Big APIs

|OS|API|
|---|---|
|Linux|`epoll`|
|BSD / macOS|`kqueue`|
|Windows|`IOCP`|

libuv abstracts these so Node behaves consistently everywhere.

---

## 4. epoll (Linux)

### 4.1 What epoll Is

`epoll` is a kernel object that:

- Tracks many file descriptors
- Sleeps efficiently
- Wakes when any becomes ready
    

Key calls:

```js
epoll_create()
epoll_ctl()
epoll_wait()

```

---

### 4.2 The epoll Lifecycle

1. Node registers sockets with epoll
2. Kernel monitors them
3. Event loop calls:
    

```js
epoll_wait(epfd, events, MAX_EVENTS, timeout);

```

4. Kernel blocks the thread
5. Hardware interrupt arrives
6. Kernel wakes epoll
7. Ready descriptors returned
    

**Zero polling. Zero spinning.**

---

### 4.3 Why epoll Scales

epoll is:

- O(1) for readiness
- Edge-triggered capable
- Does not rescan descriptors
    

This is why Node on Linux can handle:

- Tens of thousands of sockets
- Idle connections with near-zero CPU
    

---

## 5. kqueue (BSD / macOS)

### 5.1 Conceptual Difference

`kqueue` is **event-based**, not FD-based.

You register:

- Read readiness
- Write readiness
- Signals
- Timers
- Filesystem changes
    

All in **one unified queue**.

---

### 5.2 kqueue Model

```js
kevent(kq, changelist, nchanges, eventlist, nevents, timeout);

```

This:

- Applies registrations
- Blocks
- Returns events
    

macOS Node performance comes largely from this design.

---

### 5.3 Why kqueue Is Powerful

kqueue can:

- Track timers natively
- Track signals
- Track process lifecycle
    

libuv uses this to unify:

- Timers
- I/O
- Signals
    

Into a **single wait point**.

---

## 6. IOCP (Windows)

### 6.1 Different Philosophy Entirely

IOCP is not readiness-based.

It is **completion-based**.

You don’t ask:

> “Is this socket readable?”

You ask:

> “Tell me when this operation finishes.”

---

### 6.2 How IOCP Works

1. Submit async operation
2. Kernel performs work
3. Completion packet queued
4. Event loop dequeues completion
    

This is true async I/O — not readiness emulation.

---

### 6.3 Why Windows Is Harder

IOCP:

- Requires overlapped I/O
- Requires different mental model
- Cannot rely on readiness semantics
    

libuv translates this into Node’s callback model.

This is **non-trivial engineering**.

---

## 7. The Poll Phase Is Just “Wait Here”

Now revisit the Poll phase:

```js
Poll:
  if callbacks available:
    run them
  else:
    wait for I/O

```

That “wait” is literally:

- `epoll_wait`
- `kevent`
- `GetQueuedCompletionStatus`
    

There is no JS magic here.

---

## 8. Why CPU Usage Drops to Near Zero

When Node is idle:

- Event loop thread is **blocked in kernel**
- No spinning
- No polling
- No wakeups
    

This is why Node servers appear “idle” even with 50k connections.

---

## 9. Timers and Sleep Accuracy

Timers are not precise because:

- Kernel wakeups are coarse
- epoll_wait timeout interacts with poll
- Timers are checked **between waits**
    

Node trades precision for scalability.

---

## 10. Thread Pool Integration

Some operations:

- fs
- crypto
- zlib
    

Cannot use epoll/kqueue directly.

They run in **libuv’s thread pool**.

Completion still returns via:

- Poll phase
- OS notification
- Callback enqueue
    

Even threads feed back into the same loop.

---

## 11. Why Node Can’t “Just Use Threads”

Threads solve CPU parallelism.

They **do not solve I/O waiting efficiently**.

Using epoll/kqueue:

- One thread
- Thousands of sockets
- Minimal context switching
    

This is why the event loop exists at all.

---

## 12. The Design Tradeoff (Explicit)

Node chooses:

- Fewer threads
- Explicit yielding
- OS-driven wakeups
    

Over:

- Preemptive scheduling
- Fairness guarantees
- CPU isolation
    

This is a conscious tradeoff.

---

## 13. One Diagram That Matters

```js
Event Loop Thread
↓
libuv wait
↓
OS multiplexing API
↓
Kernel sleep
↓
Interrupt
↓
Ready events
↓
Callbacks queued
↓
JS executes

```

Nothing else is happening.

---

## 14. Final Lock-In Sentence

> **The Node event loop doesn’t spin — it sleeps inside the kernel and wakes only when the OS tells it to.**