Good. Now we go below the API.

We remove the “magic”.

You already know:

- `epoll_create1`
    
- `epoll_ctl`
    
- `epoll_wait`
    

Now we see what the kernel actually builds and how events flow from NIC → TCP stack → epoll → your thread.

---

# 1️⃣ First: epoll Is Just a Kernel Object

When you call:

```c
int epfd = epoll_create1(0);
```

Kernel creates an internal structure (simplified):

```
struct eventpoll {
    rb_tree   interest_tree;   // all monitored fds
    list      ready_list;      // fds currently ready
    waitqueue waiters;         // threads sleeping in epoll_wait
}
```

That’s it.

No magic.

It is just:

- A red-black tree
    
- A linked list
    
- A wait queue
    

---

# 2️⃣ What Happens During epoll_ctl(ADD)

When you call:

```c
epoll_ctl(epfd, EPOLL_CTL_ADD, fd, &ev);
```

Kernel:

1. Creates an `epitem` object:
    

```
struct epitem {
    fd
    event_mask (EPOLLIN, EPOLLOUT, etc)
    pointer to file struct
    linkage to ready list
}
```

2. Inserts it into:
    

```
eventpoll->interest_tree
```

This is O(log n) because it’s a red-black tree.

3. Registers a callback into the file’s wait queue.
    

This is critical.

---

# 3️⃣ The Most Important Concept: Callback Hooking

Every file descriptor in Linux has:

```
struct file
    -> struct file_operations
```

Sockets internally have:

```
struct socket
    -> struct sock
        -> wait_queue
```

When epoll adds a socket, it attaches itself to that socket’s wait queue.

It basically says:

> “If this socket becomes ready, call me.”

So epoll does NOT poll continuously.

It subscribes to readiness notifications.

That is the secret.

---

# 4️⃣ What Happens When Data Arrives (Deep Path)

Let’s trace packet arrival.

### Step 1 — NIC Interrupt

Network card receives packet.  
Interrupt fires.  
Kernel network driver runs.

---

### Step 2 — TCP Stack Processes Packet

Packet goes through:

```
driver → IP layer → TCP layer
```

TCP layer:

- Validates packet
    
- Appends data to socket receive buffer
    

Now socket state changes:

```
recv buffer: empty → non-empty
```

---

### Step 3 — Socket Signals Readable

Inside TCP code:

It calls something like:

```
sk->sk_data_ready(sk);
```

Which wakes the socket wait queue.

Remember earlier:

epoll registered itself on that wait queue.

So now:

Socket wake queue triggers → epoll callback runs.

---

# 5️⃣ What epoll Callback Does

The callback function:

1. Checks if fd is already in ready list
    
2. If not, adds it to:
    

```
eventpoll->ready_list
```

3. Wakes threads waiting in:
    

```
eventpoll->waiters
```

That’s it.

It does NOT wake your thread directly from TCP.

It just:

- Moves fd from interest tree
    
- To ready list
    
- Wakes epoll_wait sleepers
    

---

# 6️⃣ What epoll_wait Actually Does

When your thread calls:

```c
epoll_wait(epfd, events, max, timeout);
```

Kernel:

1. Checks ready_list
    
2. If empty:
    
    - Thread sleeps on eventpoll waitqueue
        
3. If not empty:
    
    - Copies ready fds into user buffer
        
    - Removes them (depending on mode)
        
    - Returns count
        

So epoll_wait is:

```
Sleep until ready_list not empty
```

That’s all.

---

# 7️⃣ Why This Is Efficient

Compare to poll():

poll():

```
Loop over 100k fds
Check each one
```

epoll:

```
Only touched when state changes
```

That’s why epoll scales.

It is event-driven inside kernel.

---

# 8️⃣ Level-Triggered vs Edge at Kernel Level

Kernel tracks:

- Current readiness state
    
- Previous readiness state
    

### Level-triggered

If buffer not empty:

Keep fd in ready list.

Every epoll_wait sees it.

---

### Edge-triggered

Kernel tracks state transition:

```
empty → non-empty
```

Only when transition happens:

Add to ready list.

If still non-empty:

Do NOT add again.

That’s why you must drain.

---

# 9️⃣ Where Locks Exist

epoll is NOT lock-free.

There are locks around:

- interest_tree
    
- ready_list
    
- callback path
    

When many threads share epoll:

Lock contention increases.

That’s why sharding (1 epoll per thread) scales better.

---

# 🔟 What Happens on Write Readiness

Similar mechanism.

When socket send buffer has space:

TCP layer triggers:

```
sk_write_space()
```

That wakes epoll.

epoll moves fd to ready list with EPOLLOUT.

---

# 1️⃣1️⃣ Why epoll Is Not Magic

epoll is just:

```
Subscribe to file wait queue
Move fd to ready list on state change
Wake sleeping threads
```

No polling.  
No scanning.  
No background loop.

It reacts to state change callbacks.

---

# 1️⃣2️⃣ Visual Kernel Flow

Full chain:

```
NIC interrupt
↓
Driver
↓
TCP stack
↓
Socket receive buffer updated
↓
Socket wait queue wakeup
↓
epoll callback runs
↓
fd added to ready list
↓
epoll_wait wakes up
↓
User space reads data
```

That is the full lifecycle.

---

# 1️⃣3️⃣ Why epoll Can Handle 100k Connections

Because:

- No scanning
    
- No iteration over all fds
    
- Only active fds move
    
- Everything else sits quietly in red-black tree
    

Memory cost is O(n)  
CPU cost per event is near O(1)

---

# 1️⃣4️⃣ What Feels Like Magic

The magic feeling comes from this:

You never see the callback registration.

But internally epoll hooks into:

```
file->f_op->poll()
```

Every file type implements a poll method.

epoll integrates into that generic interface.

So epoll works not only for sockets:

- pipes
    
- eventfd
    
- timerfd
    
- signalfd
    
- character devices
    

Anything implementing poll() works.

---

# 1️⃣5️⃣ Final Mental Model

epoll is:

> A subscription system inside the kernel.

It builds:

- A tree of interest
    
- A list of ready
    
- A wait queue of sleepers
    

It connects itself into each file’s readiness notification path.

That’s all.

No scanning.  
No magic.  
Just structured wakeup routing.

---

# Now Important Question For You

After this explanation:

Do you now see epoll as:

A) Polling mechanism  
B) Interrupt-to-user-space routing mechanism

If you answer correctly, the magic is gone.