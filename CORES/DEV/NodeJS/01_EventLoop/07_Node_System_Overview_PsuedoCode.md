The event loop is a single-threaded program that sleeps in `epoll`, wakes up with ready events, runs callbacks to completion, drains microtasks, then sleeps again.

```py
import select
import sys
from collections import deque

# ---------------- "JS" EXECUTION ----------------

def js_execute(code):
    print(f"[JS] {code}")

# ---------------- QUEUES ----------------

poll_queue = deque()        # Poll phase callbacks (I/O)
microtask_queue = deque()   # Microtasks (Promises / nextTick)

# ---------------- MICROTASK DRAIN ----------------

def run_microtasks():
    while microtask_queue:
        js_execute(microtask_queue.popleft())

# ---------------- IO HANDLER ----------------

def on_stdin():
    data = sys.stdin.readline().strip()
    if data:
        # Simulate I/O callback scheduling
        poll_queue.append("console.log('stdin data')")
        # Simulate Promise resolution
        microtask_queue.append("Promise.then()")

# ---------------- EVENT LOOP ----------------

ep = select.epoll()
ep.register(sys.stdin.fileno(), select.EPOLLIN)

print("Mini Event Loop (epoll, correct scheduler model)")
print("Type something and press Enter\n")

while True:
    print("\n[LOOP] poll phase → epoll.poll() (blocking)")

    # 1️⃣ POLL PHASE (KERNEL WAIT)
    events = ep.poll()   # blocks until fd is ready

    # 2️⃣ QUEUE POLL CALLBACKS
    for fd, event in events:
        if fd == sys.stdin.fileno():
            on_stdin()

    # 3️⃣ EXECUTE POLL CALLBACKS ONE BY ONE
    while poll_queue:
        task = poll_queue.popleft()
        js_execute(task)

        # 🔥 CRITICAL: MICROTASKS RUN AFTER EACH CALLBACK
        run_microtasks()


```


```c
#include <stdio.h>
#include <unistd.h>
#include <sys/epoll.h>
#include <stdlib.h>

#define MAX_EVENTS 10

/* ---------------- JS EXECUTION ---------------- */

void js_execute(const char* code) {
    printf("[JS] %s\n", code);
}

/* ---------------- TASK QUEUE ---------------- */

typedef struct Task {
    const char* code;
    struct Task* next;
} Task;

void enqueue(Task** q, const char* code) {
    Task* t = malloc(sizeof(Task));
    t->code = code;
    t->next = NULL;

    if (!*q) *q = t;
    else {
        Task* c = *q;
        while (c->next) c = c->next;
        c->next = t;
    }
}

Task* dequeue(Task** q) {
    if (!*q) return NULL;
    Task* t = *q;
    *q = t->next;
    return t;
}

/* ---------------- QUEUES ---------------- */

Task* poll_queue = NULL;
Task* microtask_queue = NULL;

/* ---------------- MICROTASK DRAIN ---------------- */

void run_microtasks() {
    Task* t;
    while ((t = dequeue(&microtask_queue))) {
        js_execute(t->code);
        free(t);
    }
}

/* ---------------- IO HANDLER ---------------- */

void on_stdin() {
    char buf[128];
    int n = read(STDIN_FILENO, buf, sizeof(buf));
    if (n > 0) {
        enqueue(&poll_queue, "console.log('stdin')");
        enqueue(&microtask_queue, "Promise.then()");
    }
}

/* ---------------- EVENT LOOP ---------------- */

int main() {
    int epfd = epoll_create1(0);
    struct epoll_event ev, events[MAX_EVENTS];

    ev.events = EPOLLIN;
    ev.data.fd = STDIN_FILENO;
    epoll_ctl(epfd, EPOLL_CTL_ADD, STDIN_FILENO, &ev);

    printf("Mini Event Loop (Correct Model)\n");

    while (1) {
        printf("\n[LOOP] poll phase → epoll_wait\n");

        int nfds = epoll_wait(epfd, events, MAX_EVENTS, -1);

        /* enqueue poll callbacks */
        for (int i = 0; i < nfds; i++) {
            on_stdin();
        }

        /* execute poll callbacks one by one */
        Task* task;
        while ((task = dequeue(&poll_queue))) {
            js_execute(task->code);
            free(task);

            /* 🔥 THIS IS THE CRITICAL RULE */
            run_microtasks();
        }
    }
}

```