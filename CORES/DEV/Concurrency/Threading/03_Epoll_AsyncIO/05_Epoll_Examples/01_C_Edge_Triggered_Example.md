Below is the **canonical C pattern** for:

- non-blocking sockets
    
- edge-triggered epoll (`EPOLLET`)
    
- read/write loops until `EAGAIN`
    
- accept loop until `EAGAIN`
    

This is the real production mental model used by nginx/redis/haproxy.

I’ll keep it small, but correct and complete.

---

# 🧠 Core Rule (burn this into memory)

With **Edge-Triggered epoll**:

> When you get an event, you MUST drain the resource completely until `EAGAIN`.

Applies to:

- `accept()`
    
- `read()`
    
- `write()`
    

---

# 📄 epoll_et_server.c (Full Example)

Single-threaded echo server using:

- nonblocking sockets
    
- EPOLLET
    
- EAGAIN loops
    

```c
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <fcntl.h>
#include <errno.h>
#include <string.h>
#include <arpa/inet.h>
#include <sys/socket.h>
#include <sys/epoll.h>

#define PORT 8080
#define MAX_EVENTS 64
#define BUFFER_SIZE 4096

int set_nonblocking(int fd) {
    int flags = fcntl(fd, F_GETFL, 0);
    return fcntl(fd, F_SETFL, flags | O_NONBLOCK);
}

int main() {
    int server_fd = socket(AF_INET, SOCK_STREAM, 0);
    set_nonblocking(server_fd);

    int opt = 1;
    setsockopt(server_fd, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt));

    struct sockaddr_in addr = {0};
    addr.sin_family = AF_INET;
    addr.sin_port = htons(PORT);
    addr.sin_addr.s_addr = INADDR_ANY;

    bind(server_fd, (struct sockaddr*)&addr, sizeof(addr));
    listen(server_fd, SOMAXCONN);

    int epfd = epoll_create1(0);

    struct epoll_event ev, events[MAX_EVENTS];

    // Register server socket (edge-triggered)
    ev.events = EPOLLIN | EPOLLET;
    ev.data.fd = server_fd;
    epoll_ctl(epfd, EPOLL_CTL_ADD, server_fd, &ev);

    printf("Listening on port %d\n", PORT);

    char buffer[BUFFER_SIZE];

    while (1) {
        int n = epoll_wait(epfd, events, MAX_EVENTS, -1);

        for (int i = 0; i < n; i++) {
            int fd = events[i].data.fd;

            // 1️⃣ Accept all pending clients
            if (fd == server_fd) {
                while (1) {
                    int client_fd = accept(server_fd, NULL, NULL);

                    if (client_fd == -1) {
                        if (errno == EAGAIN || errno == EWOULDBLOCK)
                            break;  // all clients accepted
                        perror("accept");
                        break;
                    }

                    set_nonblocking(client_fd);

                    ev.events = EPOLLIN | EPOLLET;
                    ev.data.fd = client_fd;
                    epoll_ctl(epfd, EPOLL_CTL_ADD, client_fd, &ev);

                    printf("New client %d\n", client_fd);
                }
            }

            // 2️⃣ Read all available data
            else if (events[i].events & EPOLLIN) {
                while (1) {
                    ssize_t count = read(fd, buffer, BUFFER_SIZE);

                    if (count == -1) {
                        if (errno == EAGAIN)
                            break;  // buffer drained
                        perror("read");
                        close(fd);
                        break;
                    }

                    if (count == 0) {
                        printf("Client %d disconnected\n", fd);
                        close(fd);
                        break;
                    }

                    // Echo back (write loop)
                    ssize_t written = 0;
                    while (written < count) {
                        ssize_t n = write(fd, buffer + written, count - written);

                        if (n == -1) {
                            if (errno == EAGAIN)
                                break;  // socket full
                            perror("write");
                            close(fd);
                            break;
                        }

                        written += n;
                    }
                }
            }

            // 3️⃣ Errors
            if (events[i].events & (EPOLLERR | EPOLLHUP)) {
                close(fd);
            }
        }
    }
}
```

Compile:

```
gcc epoll_et_server.c -o server
./server
```


# 📄 client.c

Simple interactive TCP client

```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <arpa/inet.h>

#define PORT 8080
#define BUFFER_SIZE 4096

int main() {
    int sock = socket(AF_INET, SOCK_STREAM, 0);

    struct sockaddr_in server_addr = {0};
    server_addr.sin_family = AF_INET;
    server_addr.sin_port = htons(PORT);
    inet_pton(AF_INET, "127.0.0.1", &server_addr.sin_addr);

    if (connect(sock, (struct sockaddr*)&server_addr, sizeof(server_addr)) < 0) {
        perror("connect");
        return 1;
    }

    printf("Connected to server. Type messages:\n");

    char buffer[BUFFER_SIZE];

    while (1) {
        printf("> ");
        fflush(stdout);

        if (!fgets(buffer, BUFFER_SIZE, stdin))
            break;

        size_t len = strlen(buffer);

        if (write(sock, buffer, len) < 0) {
            perror("write");
            break;
        }

        ssize_t n = read(sock, buffer, BUFFER_SIZE);
        if (n <= 0) {
            printf("Server closed connection\n");
            break;
        }

        printf("Echo: %.*s", (int)n, buffer);
    }

    close(sock);
    return 0;
}

```

Compile & run:

`gcc client.c -o client ./client`

---
You now have:

- Real epoll ET server
    
- Multiple concurrent clients
    
- Nonblocking I/O
    
- EAGAIN draining
    
- Kernel-accurate behavior
---

# 🧠 What’s happening internally (step-by-step)

## Step 1 — Nonblocking socket

```
fcntl(fd, F_SETFL, O_NONBLOCK)
```

Now:

- `read()` returns `-1 + EAGAIN` if no data
    
- `accept()` returns `-1 + EAGAIN` if no clients
    
- `write()` returns `-1 + EAGAIN` if send buffer full
    

This is the foundation of async I/O.

---

## Step 2 — Register EPOLLET

```
EPOLLIN | EPOLLET
```

Meaning:

```
Notify me only when state changes.
Not continuously.
```

---

## Step 3 — Accept loop (critical)

```
while (accept() != EAGAIN)
```

Why?

Because kernel may say:

```
"Connections arrived"
```

But there could be:

- 1 client
    
- 50 clients
    

Edge-trigger gives only ONE wakeup.

So you must drain all pending accepts.

---

## Step 4 — Read loop (MOST IMPORTANT)

```
while (read() != EAGAIN)
```

This drains the kernel recv buffer.

If you read only once:

You might leave data behind.

Then:

Kernel will NOT notify you again.

Connection appears stuck.

---

## Step 5 — Write loop

```
while (write() != EAGAIN)
```

Because:

- TCP send buffer might fill
    
- write() might write partial data
    

You must continue until:

- all data sent
    
- OR socket full
    

---

# 🧠 Visual mental model (ET mode)

Timeline:

```
Buffer empty
Client sends 8KB
Buffer now has data
Kernel fires EPOLLIN ONCE
```

Your job:

```
read()
read()
read()
until EAGAIN
```

Now:

```
Buffer empty again
```

Later:

```
Client sends more data
Kernel fires EPOLLIN again
```

---

# 🧠 The Big Rule

Edge-triggered = state transition based

Kernel notifies only when:

```
empty → non-empty
```

So you must:

```
consume until empty
```

---

# 🧠 Common beginner mistake

WRONG:

```
read(fd, buf, 1024);
```

RIGHT:

```
while (read() != EAGAIN)
```

---

# 🧠 Difference vs Level-triggered

Level-triggered:

```
If data still present → epoll keeps waking you
```

Edge-triggered:

```
If data still present → kernel stays silent
```

---

# 🧠 Why ET is faster

Level-triggered:

- repeated wakeups
    
- more syscalls
    

Edge-triggered:

- fewer wakeups
    
- fewer context switches
    
- better scalability
    

---

# 🧠 Where EAGAIN comes from (kernel level)

Kernel recv buffer:

```
data available → read() returns bytes
no data → read() returns EAGAIN
```

This is how kernel says:

```
"You have drained everything."
```

---

# 🧠 Final deep understanding checkpoint

ET mode is basically:

> "Interrupt-like behavior for sockets"

Kernel says once:

```
"Something changed"
```

Then responsibility shifts to you:

```
Drain completely
```

---

# Want the final mastery layer?

Next concepts that complete epoll knowledge:

- EPOLLONESHOT internal logic
    
- EPOLLEXCLUSIVE and thundering herd fix
    
- Multi-threaded epoll architecture
    
- How nginx structures worker loops
    

Which one should we go into next?