Below is a **production-style reference set** to conclude your core epoll learning.  
All code uses **`select.epoll()` directly (C-style thinking)**.

You’ll get 3 files:

1. `server_lt.py` → Level-triggered high-performance echo server
    
2. `server_et.py` → Edge-triggered high-performance echo server
    
3. `client.py` → simple load/test client
    

Design goals:

- Nonblocking sockets
    
- Proper fd → state management
    
- Partial write handling
    
- Clean event modification
    
- Real echo server architecture pattern
    

These are intentionally close to how C servers are structured.

---

# 📄 server_lt.py (Production-style Level Triggered)

Level-triggered is simpler and safer. Kernel keeps reminding you if data still exists.

```python
import socket
import select

HOST = "0.0.0.0"
PORT = 8080
BUFFER = 4096
MAX_EVENTS = 1024

def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen()
    server.setblocking(False)

    epoll = select.epoll()
    epoll.register(server.fileno(), select.EPOLLIN)

    fd_to_socket = {server.fileno(): server}
    send_buffer = {}  # fd -> pending bytes

    print("Level-triggered epoll server on", PORT)

    try:
        while True:
            events = epoll.poll()

            for fd, event in events:
                sock = fd_to_socket[fd]

                # New connection
                if sock is server:
                    client, addr = server.accept()
                    client.setblocking(False)

                    fd_to_socket[client.fileno()] = client
                    send_buffer[client.fileno()] = b""

                    epoll.register(client.fileno(), select.EPOLLIN)
                    print("Connected:", addr)

                # Readable
                elif event & select.EPOLLIN:
                    data = sock.recv(BUFFER)

                    if data:
                        send_buffer[fd] += data
                        # Ask kernel to notify when writable
                        epoll.modify(fd, select.EPOLLIN | select.EPOLLOUT)
                    else:
                        cleanup(epoll, fd, fd_to_socket, send_buffer)

                # Writable
                elif event & select.EPOLLOUT:
                    if send_buffer[fd]:
                        sent = sock.send(send_buffer[fd])
                        send_buffer[fd] = send_buffer[fd][sent:]

                    # If all sent, stop watching EPOLLOUT
                    if not send_buffer[fd]:
                        epoll.modify(fd, select.EPOLLIN)

                # Error
                elif event & (select.EPOLLHUP | select.EPOLLERR):
                    cleanup(epoll, fd, fd_to_socket, send_buffer)

    finally:
        epoll.close()
        server.close()

def cleanup(epoll, fd, fd_map, send_buf):
    epoll.unregister(fd)
    fd_map[fd].close()
    del fd_map[fd]
    del send_buf[fd]

if __name__ == "__main__":
    main()
```

---

## 🧠 Important LT notes

- No loops required for `recv()`
    
- Kernel will re-notify if unread data remains
    
- Simpler mental model
    
- Slightly more wakeups than ET
    
- Used widely in real production systems
    

---

# 📄 server_et.py (Production-style Edge Triggered)

Edge-triggered = high performance + must drain buffers fully.

```python
import socket
import select

HOST = "0.0.0.0"
PORT = 8080
BUFFER = 4096

def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen()
    server.setblocking(False)

    epoll = select.epoll()
    epoll.register(server.fileno(), select.EPOLLIN | select.EPOLLET)

    fd_to_socket = {server.fileno(): server}
    send_buffer = {}

    print("Edge-triggered epoll server on", PORT)

    try:
        while True:
            events = epoll.poll()

            for fd, event in events:
                sock = fd_to_socket[fd]

                # Accept loop (drain accept queue)
                if sock is server:
                    while True:
                        try:
                            client, addr = server.accept()
                            client.setblocking(False)

                            fd_to_socket[client.fileno()] = client
                            send_buffer[client.fileno()] = b""

                            epoll.register(
                                client.fileno(),
                                select.EPOLLIN | select.EPOLLET
                            )
                            print("Connected:", addr)

                        except BlockingIOError:
                            break

                # Read loop (drain recv buffer)
                if event & select.EPOLLIN:
                    while True:
                        try:
                            data = sock.recv(BUFFER)

                            if not data:
                                cleanup(epoll, fd, fd_to_socket, send_buffer)
                                break

                            send_buffer[fd] += data
                            epoll.modify(
                                fd,
                                select.EPOLLIN | select.EPOLLOUT | select.EPOLLET
                            )

                        except BlockingIOError:
                            break

                # Write loop (drain send buffer)
                if event & select.EPOLLOUT:
                    while send_buffer[fd]:
                        try:
                            sent = sock.send(send_buffer[fd])
                            send_buffer[fd] = send_buffer[fd][sent:]

                        except BlockingIOError:
                            break

                    if not send_buffer[fd]:
                        epoll.modify(fd, select.EPOLLIN | select.EPOLLET)

                # Errors
                if event & (select.EPOLLHUP | select.EPOLLERR):
                    cleanup(epoll, fd, fd_to_socket, send_buffer)

    finally:
        epoll.close()
        server.close()

def cleanup(epoll, fd, fd_map, send_buf):
    epoll.unregister(fd)
    fd_map[fd].close()
    del fd_map[fd]
    del send_buf[fd]

if __name__ == "__main__":
    main()
```

---

## 🧠 Important ET rules (critical)

When notified:

You MUST drain:

- accept() until EAGAIN
    
- recv() until EAGAIN
    
- send() until EAGAIN
    

Otherwise:  
Connection may stall forever.

---

# 📄 client.py (Test Client)

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
            data = sock.recv(4096)
            print("Echo:", data.decode())
    finally:
        sock.close()

if __name__ == "__main__":
    main()
```

---

# 🧠 LT vs ET — Final Practical Comparison

## Level Triggered

Pros:

- Easier to write
    
- Safer
    
- Hard to get stuck
    
- Less logic
    

Cons:

- More wakeups
    
- Slightly less efficient
    

Best for:

- Most backend servers
    
- Simpler systems
    

---

## Edge Triggered

Pros:

- Fewer syscalls
    
- Less wakeups
    
- Maximum scalability
    

Cons:

- Easy to implement wrong
    
- Must drain buffers fully
    

Best for:

- High-performance systems
    
- nginx-style servers
    
- 100k+ connections
    

---

# 🧠 Final mental closure

You now understand epoll at all layers:

- Kernel internals
    
- C ET model
    
- Python LT model
    
- Python ET model
    
- EAGAIN contract
    
- Ready list behavior
    
- State transition model
    

This is the complete “basic epoll mastery” foundation.

From here, the next true production concepts would be:

- EPOLLONESHOT + thread pools
    
- EPOLLEXCLUSIVE + multi-process servers
    
- Per-CPU epoll sharding
    
- How nginx/redis event loops are structured