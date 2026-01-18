```txt
Node.js Event Loop System
│
├── 1. Call Stack (V8)
│
├── 2. Queues
│   ├── 2.1 Microtask Queues
│   │   ├── process.nextTick queue
│   │   └── Promise / queueMicrotask queue
│   │
│   └── 2.2 Phase-Bound Task Queues
│       ├── Timers queue
│       ├── Pending I/O queue
│       ├── Poll queue
│       ├── Check queue
│       └── Close queue
│
├── 3. Event Loop Phases
│   ├── Timers
│   ├── Pending I/O
│   ├── Idle / Prepare
│   ├── Poll
│   ├── Check
│   └── Close
│
├── 4. libuv Event Loop (Scheduler)
│
├── 5. OS I/O Notification (epoll/kqueue/IOCP)
│
├── 6. libuv Thread Pool
│
├── 7. Timers Subsystem
│
├── 8. EventEmitter System
│
├── 9. Microtask Checkpoints
│
└── 10. Native Bindings

```