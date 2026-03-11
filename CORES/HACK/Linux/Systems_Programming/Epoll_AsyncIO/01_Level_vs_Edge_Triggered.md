## Level-Triggered vs Edge-Triggered in `epoll` (Most Important Concept)

Understanding the difference between **Level-Triggered (LT)** and **Edge-Triggered (ET)** mode is the key to truly mastering `epoll`.

Both modes control **when the kernel notifies your program** about I/O readiness. The difference is subtle but critical — and it directly affects correctness and performance.

---

# 1️⃣ The Core Idea

Imagine a socket has 100 bytes ready to read.

The question is:

> Should the kernel keep notifying you as long as data exists?  
> Or notify you only once when new data arrives?

That is the entire difference.

---

# 2️⃣ Level-Triggered (Default Mode)

### Definition

In **Level-Triggered mode**, `epoll` behaves like `poll()`.

If a file descriptor is ready:

- You will keep getting notified
    
- Until you consume all available data
    

It repeatedly reports readiness **as long as the “level” condition remains true**.

---

### Example Scenario

Socket buffer contains 100 bytes.

You read only 20 bytes.

There are still 80 bytes remaining.

Next `epoll_wait()` call:

→ You will be notified again.

Because:

```
Data still exists → condition still true → event fires again
```

---

# Level-Triggered Code Example

```c
struct epoll_event ev;

ev.events = EPOLLIN;   // No EPOLLET flag
ev.data.fd = sockfd;

epoll_ctl(epfd, EPOLL_CTL_ADD, sockfd, &ev);
```

Now event loop:

```c
while (1) {
    int n = epoll_wait(epfd, events, MAX_EVENTS, -1);

    for (int i = 0; i < n; i++) {
        int fd = events[i].data.fd;

        char buf[1024];
        int count = read(fd, buf, sizeof(buf));

        if (count <= 0) {
            close(fd);
        } else {
            printf("Read %d bytes\n", count);
        }
    }
}
```

---

### Why This Works Even If You Don't Read Everything

Because LT keeps reminding you.

Even if you forget to drain the socket, it will trigger again.

That makes LT:

- Easier
    
- Safer
    
- Harder to break
    

---

# 3️⃣ Edge-Triggered Mode

Now the important one.

### Definition

In **Edge-Triggered mode**, the kernel notifies you:

> Only when the state changes from NOT READY → READY

It does NOT keep reminding you.

It notifies once per transition.

---

### Example Scenario

Socket buffer becomes non-empty.

Kernel sends ONE notification.

You read only 20 bytes.

80 bytes remain.

Next `epoll_wait()`:

→ NO event.

Because:

```
State did not change.
It was already ready.
```

This is the most common beginner mistake.

---

# Edge-Triggered Code Example

To enable ET:

```c
ev.events = EPOLLIN | EPOLLET;
ev.data.fd = sockfd;

epoll_ctl(epfd, EPOLL_CTL_ADD, sockfd, &ev);
```

---

# ⚠️ VERY IMPORTANT RULE IN ET MODE

You MUST:

- Use non-blocking sockets
    
- Read in a loop until `EAGAIN`
    

---

### Correct ET Read Pattern

```c
while (1) {
    int n = epoll_wait(epfd, events, MAX_EVENTS, -1);

    for (int i = 0; i < n; i++) {
        int fd = events[i].data.fd;

        while (1) {
            char buf[1024];
            int count = read(fd, buf, sizeof(buf));

            if (count == -1) {
                if (errno == EAGAIN) {
                    break;  // All data consumed
                }
                perror("read");
                close(fd);
                break;
            }

            if (count == 0) {
                close(fd);
                break;
            }

            printf("Read %d bytes\n", count);
        }
    }
}
```

---

# Why Must We Read Until EAGAIN?

Because ET notifies only once.

If you leave data unread:

- You will NEVER get notified again.
    
- The connection appears "stuck".
    
- Server seems broken.
    

---

# 4️⃣ Syscall Behavior (Parameters & Return Values)

## `epoll_ctl()`

```
int epoll_ctl(int epfd, int op, int fd, struct epoll_event *event);
```

To enable ET:

```
event->events = EPOLLIN | EPOLLET;
```

Return:

- 0 → success
    
- -1 → error
    

---

## `epoll_wait()`

```
int epoll_wait(int epfd,
               struct epoll_event *events,
               int maxevents,
               int timeout);
```

Parameters:

- `epfd` → epoll instance
    
- `events` → output array
    
- `maxevents` → array size
    
- `timeout` → -1 wait forever
    

Return:

- > 0 → number of triggered fds
    
- 0 → timeout
    
- -1 → error
    

Important:  
In ET mode, if you don’t drain the fd completely, `epoll_wait()` may block forever.

---

# 5️⃣ When to Use LT vs ET

## Use Level-Triggered When:

- You want simpler code
    
- You're learning
    
- You want safer behavior
    
- You don't need extreme optimization
    

Most applications use LT.

---

## Use Edge-Triggered When:

- You need maximum performance
    
- You want fewer wakeups
    
- You understand non-blocking deeply
    
- You're building high-performance servers
    

Nginx uses ET.  
Redis uses ET.  
Netty supports ET.

---

# 6️⃣ Clear Mental Model (No Ambiguity)

Think in terms of **data presence inside the socket buffer**.

### Level-Triggered Model

Kernel logic:

```
If data is present in the buffer:
    Report the socket as ready
```

This check happens every time you call `epoll_wait()`.

So the timeline looks like this:

```
Data arrives → epoll reports ready
You read only part → data still present
Next epoll_wait → reports ready again
Next epoll_wait → reports ready again
...
Until buffer becomes empty
```

So LT means:

> "As long as there is unread data, I will keep telling you."

---

### Edge-Triggered Model

Kernel logic:

```
If buffer was empty before
AND now data has arrived:
    Report readiness ONCE
```

Timeline:

```
Buffer empty
↓
Data arrives → epoll reports ready (ONE TIME)
↓
You read only part
↓
Data still present, but no new arrival
↓
No more events
```

Next event happens only when:

```
Buffer becomes empty
↓
New data arrives again
↓
Kernel reports ready again
```

So ET means:

> "I will notify you only when new data comes into an empty buffer."

---

### One-Line Memory Rule

Level-triggered:

```
Data exists → keep notifying
```

Edge-triggered:

```
New data arrives → notify once
```

---

# 7️⃣ Performance Difference

LT:

- Slightly more wakeups
    
- Easier
    
- Very safe
    

ET:

- Fewer syscalls
    
- Less overhead
    
- Requires precise logic
    
- Harder to debug
    

---

# 8️⃣ Common ET Bug

Bad ET code:

```c
read(fd, buf, 1024);
```

Only one read.

If socket has 4096 bytes:

→ Remaining 3072 bytes stay in buffer  
→ No new event triggered  
→ Connection appears frozen

This is the classic epoll ET mistake.

---

# 9️⃣ Deep Understanding Test

You truly understand ET if you can answer:

- Why non-blocking is mandatory?
    
- Why read until EAGAIN?
    
- Why forgetting the loop causes hidden deadlocks?
    
- Why ET reduces wakeups?
    

---

# 🔥 Final Insight

Level-triggered checks:

```
Is the socket currently ready?
```

Edge-triggered checks:

```
Did the socket just become ready?
```

That single difference is everything.