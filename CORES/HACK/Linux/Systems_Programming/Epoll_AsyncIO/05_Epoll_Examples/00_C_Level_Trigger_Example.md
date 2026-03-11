Below is a **minimal but complete single-file C example** that contains:

- A simple **epoll-based TCP server**
    
- A simple **client**
    
- Compile once, run as server or client using args
    
- Shows the full flow: socket → bind → listen → epoll → accept → read/write
    

This is meant as a **learning reference**, not production code.

---

# 🧠 Mental model before code

Think of epoll like this:

- Kernel keeps a **watch list** of file descriptors.
    
- You tell kernel:  
    “Wake me only when something interesting happens.”
    
- Kernel monitors sockets internally.
    
- When ready → kernel pushes events into a ready list.
    
- `epoll_wait()` just fetches that ready list.
    

So your program:

1. Creates epoll instance
    
2. Registers sockets
    
3. Sleeps in `epoll_wait()`
    
4. Reacts when kernel signals readiness
    

---

# 📄 Single File: epoll_server_client.c

Compile:

```
gcc epoll_server_client.c -o app
```

Run server:

```
./app server 8080
```

Run client:

```
./app client 127.0.0.1 8080
```

---

## 🔧 Full Code

```c
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <errno.h>
#include <fcntl.h>
#include <arpa/inet.h>
#include <sys/socket.h>
#include <sys/epoll.h>

#define MAX_EVENTS 64
#define BUF_SIZE 1024

/* ---------- Utility ---------- */

int set_nonblocking(int fd) {
    int flags = fcntl(fd, F_GETFL, 0);
    return fcntl(fd, F_SETFL, flags | O_NONBLOCK);
}

/* ---------- SERVER ---------- */

void run_server(int port) {
    int server_fd = socket(AF_INET, SOCK_STREAM, 0);
    if (server_fd < 0) {
        perror("socket");
        exit(1);
    }

    set_nonblocking(server_fd);

    int opt = 1;
    setsockopt(server_fd, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt));

    struct sockaddr_in addr = {0};
    addr.sin_family = AF_INET;
    addr.sin_addr.s_addr = INADDR_ANY;
    addr.sin_port = htons(port);

    if (bind(server_fd, (struct sockaddr*)&addr, sizeof(addr)) < 0) {
        perror("bind");
        exit(1);
    }

    if (listen(server_fd, 128) < 0) {
        perror("listen");
        exit(1);
    }

    int epfd = epoll_create1(0);

    struct epoll_event ev, events[MAX_EVENTS];
    ev.events = EPOLLIN;
    ev.data.fd = server_fd;

    epoll_ctl(epfd, EPOLL_CTL_ADD, server_fd, &ev);

    printf("Server listening on port %d\n", port);

    while (1) {
        int n = epoll_wait(epfd, events, MAX_EVENTS, -1);

        for (int i = 0; i < n; i++) {
            int fd = events[i].data.fd;

            if (fd == server_fd) {
                // Accept new client
                while (1) {
                    int client_fd = accept(server_fd, NULL, NULL);
                    if (client_fd < 0) {
                        if (errno == EAGAIN) break;
                        perror("accept");
                        break;
                    }

                    set_nonblocking(client_fd);

                    struct epoll_event cev;
                    cev.events = EPOLLIN | EPOLLET;
                    cev.data.fd = client_fd;

                    epoll_ctl(epfd, EPOLL_CTL_ADD, client_fd, &cev);

                    printf("Client connected: %d\n", client_fd);
                }
            } else {
                // Handle client data
                char buf[BUF_SIZE];
                int bytes = read(fd, buf, sizeof(buf));

                if (bytes <= 0) {
                    printf("Client disconnected: %d\n", fd);
                    close(fd);
                    epoll_ctl(epfd, EPOLL_CTL_DEL, fd, NULL);
                } else {
                    buf[bytes] = 0;
                    printf("Received: %s", buf);

                    // Echo back
                    write(fd, buf, bytes);
                }
            }
        }
    }
}

/* ---------- CLIENT ---------- */

void run_client(char *ip, int port) {
    int sock = socket(AF_INET, SOCK_STREAM, 0);

    struct sockaddr_in addr = {0};
    addr.sin_family = AF_INET;
    addr.sin_port = htons(port);
    inet_pton(AF_INET, ip, &addr.sin_addr);

    if (connect(sock, (struct sockaddr*)&addr, sizeof(addr)) < 0) {
        perror("connect");
        exit(1);
    }

    printf("Connected to server\n");

    char buf[BUF_SIZE];

    while (fgets(buf, sizeof(buf), stdin)) {
        write(sock, buf, strlen(buf));

        int n = read(sock, buf, sizeof(buf)-1);
        buf[n] = 0;

        printf("Echo: %s", buf);
    }

    close(sock);
}

/* ---------- MAIN ---------- */

int main(int argc, char *argv[]) {
    if (argc < 2) {
        printf("Usage:\n");
        printf("  Server: %s server <port>\n", argv[0]);
        printf("  Client: %s client <ip> <port>\n", argv[0]);
        return 0;
    }

    if (strcmp(argv[1], "server") == 0) {
        run_server(atoi(argv[2]));
    } else if (strcmp(argv[1], "client") == 0) {
        run_client(argv[2], atoi(argv[3]));
    }

    return 0;
}
```

---

# 🔍 Flow Explained Step-by-Step

## 1) Server startup

```
socket()
bind()
listen()
```

Creates TCP listening socket.

---

## 2) Create epoll

```
epoll_create1()
```

Kernel creates:

- interest list
    
- ready list
    

---

## 3) Register server socket

```
epoll_ctl(ADD, server_fd)
```

Kernel now watches:

> "Wake me when new connections arrive"

---

## 4) Event loop

```
epoll_wait()
```

Thread sleeps inside kernel.

---

## 5) Client connects

Kernel detects:

```
server_fd becomes readable
```

Why readable?

Because `accept()` will not block.

Kernel pushes event → ready list.

---

## 6) Accept loop

We use:

```
while (accept() until EAGAIN)
```

This is **edge-triggered best practice**.

---

## 7) Add client fd to epoll

Now kernel watches:

> "Wake me when client sends data"

---

## 8) Client sends data

Kernel:

- data arrives in socket buffer
    
- marks fd readable
    
- adds to epoll ready list
    

---

## 9) epoll_wait returns

You call:

```
read(fd)
```

---

## 10) Echo back

```
write(fd)
```

---

# 🧠 Important Deep Concepts Hidden Here

### Why non-blocking?

If blocking:

- One slow client freezes server
    

---

### Why EPOLLET (edge-triggered)?

Kernel notifies only when state changes.

So you must:

```
read until EAGAIN
```

---

### What epoll is doing internally

Kernel tracks:

```
struct eventpoll {
   interest RB-tree
   ready linked-list
}
```

When data arrives:

```
sock_def_readable()
  → ep_poll_callback()
    → add fd to ready list
```

---

# 🧪 What to Observe While Running

Open 3 terminals:

Terminal 1:

```
./app server 8080
```

Terminal 2:

```
./app client 127.0.0.1 8080
```

Terminal 3:

```
./app client 127.0.0.1 8080
```

Type messages → see echo.

---

# 🧠 Mental Model Summary

epoll is NOT magic.

It is:

```
Kernel maintains ready-list
Your thread sleeps
Kernel wakes you only when needed
```

So instead of:

```
check 10k sockets repeatedly
```

You do:

```
sleep until kernel says "work exists"
```

---

# Want next deeper step?

I can next show:

1. epoll + EPOLLONESHOT real production pattern
    
2. multithreaded epoll design
    
3. how Nginx uses epoll internally
    
4. kernel source walkthrough of ep_poll()
    

Which level do you want?