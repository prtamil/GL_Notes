Below is the **same echo server/client**, but now using **`select.epoll()` directly**, which is the closest Python equivalent to the C epoll code you saw earlier.

This is almost a 1:1 mental mapping to:

- `epoll_create1`
    
- `epoll_ctl`
    
- `epoll_wait`
    

No `selectors` abstraction.

---

# 📄 server_epoll.py (raw epoll version)

```python
import socket
import select

HOST = "0.0.0.0"
PORT = 8080
BUFFER = 1024

def main():
    # 1) Create server socket
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sock.bind((HOST, PORT))
    server_sock.listen()
    server_sock.setblocking(False)

    # 2) Create epoll object  (epoll_create1)
    epoll = select.epoll()

    # 3) Register server socket (epoll_ctl ADD)
    epoll.register(server_sock.fileno(), select.EPOLLIN)

    # Map fd -> socket object
    fd_to_socket = {server_sock.fileno(): server_sock}

    print(f"Server listening on {PORT}")

    try:
        while True:
            # 4) Wait for events (epoll_wait)
            events = epoll.poll()

            for fd, event in events:
                sock = fd_to_socket[fd]

                # New connection
                if sock is server_sock:
                    client_sock, addr = server_sock.accept()
                    print("Connected:", addr)
                    client_sock.setblocking(False)

                    fd_to_socket[client_sock.fileno()] = client_sock
                    epoll.register(client_sock.fileno(), select.EPOLLIN)

                # Data ready
                elif event & select.EPOLLIN:
                    data = sock.recv(BUFFER)

                    if data:
                        print("Received:", data.decode().strip())
                        sock.sendall(data)  # echo
                    else:
                        # Client closed
                        print("Disconnected")
                        epoll.unregister(fd)
                        sock.close()
                        del fd_to_socket[fd]

                # Error/hangup
                elif event & (select.EPOLLHUP | select.EPOLLERR):
                    epoll.unregister(fd)
                    sock.close()
                    del fd_to_socket[fd]

    finally:
        epoll.close()
        server_sock.close()

if __name__ == "__main__":
    main()
```

---

# 📄 client_epoll.py (simple client)

Client does not need epoll (usually clients are simple).

```python
import socket

HOST = "127.0.0.1"
PORT = 8080

def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((HOST, PORT))

    print("Connected. Type messages:")

    try:
        while True:
            msg = input("> ")
            if not msg:
                break

            sock.sendall(msg.encode())
            data = sock.recv(1024)

            print("Echo:", data.decode())
    finally:
        sock.close()

if __name__ == "__main__":
    main()
```

---

# 🧠 Direct mapping to C epoll

### Python

```python
epoll = select.epoll()
```

### C

```c
epoll_create1(0)
```

---

### Python

```python
epoll.register(fd, select.EPOLLIN)
```

### C

```c
epoll_ctl(epfd, EPOLL_CTL_ADD, fd, &ev)
```

---

### Python

```python
events = epoll.poll()
```

### C

```c
epoll_wait(epfd, events, max, timeout)
```

---

# 🧠 What `epoll.poll()` returns

List of tuples:

```
[(fd, event_mask), ...]
```

Example:

```
[(3, EPOLLIN), (7, EPOLLIN)]
```

Meaning:

- fd 3 → ready to read
    
- fd 7 → ready to read
    

Exactly like C.

---

# 🧠 Why we need fd_to_socket map

epoll gives:

```
fd number only
```

But Python recv needs:

```
socket object
```

So we maintain:

```
fd → socket
```

Same idea as C storing pointer in `epoll_event.data.ptr`.

---

# 🧠 Event handling logic

```
if fd == server_socket:
    accept new client
elif EPOLLIN:
    recv data
    echo back
elif HUP/ERR:
    close
```

This is the canonical epoll server.

---

# 🧠 Level-triggered by default

This Python example uses:

```
EPOLLIN
```

So it is:

```
Level-triggered
```

Just like default C epoll.

If you wanted edge-triggered:

```python
epoll.register(fd, select.EPOLLIN | select.EPOLLET)
```

Then you'd need nonblocking loops like in C.

---

# 🧠 Why this version is best for learning epoll

Because it exposes:

- fd-based thinking
    
- event masks
    
- epoll lifecycle
    
- manual connection management
    
- direct similarity to kernel API
    

Without:

- C memory complexity
    
- struct epoll_event
    
- pointer management
    

---

# 🧠 Keep-in-head minimal epoll pattern

```
create socket
set nonblocking
create epoll
register server fd

loop:
    events = epoll_wait
    for each event:
        if server:
            accept
            register client
        else:
            read/write
            if closed:
                unregister + close
```

This is the exact same pattern used by:

- nginx
    
- redis
    
- node.js
    
- uvicorn
    
- haproxy
    

---

# Next deep step (important)

Now that you saw:

- C epoll
    
- Python epoll
    

The next clarity jump is:

**Nonblocking + EAGAIN loops + Edge-triggered in Python**

That will fully connect:

Kernel readiness model → user-space draining model.

Want that next?