```txt
┌───────────────────────────────────────────────────────────────┐
│ LEVEL 3 — PROJECT LOOM (Virtual / Structured Concurrency)     │
│                                                               │
│   Thread (Virtual)                                            │
│   Executors                                                   │
│   StructuredTaskScope                                         │
│   ScopedValue                                                 │
│                                                               │
└───────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌───────────────────────────────────────────────────────────────┐
│ LEVEL 2 — java.util.concurrent (High-level Concurrency)       │
│                                                               │
│  Task Execution                                               │
│   Executor                                                    │
│   ExecutorService                                             │
│   ScheduledExecutorService                                    │
│   ForkJoinPool                                                │
│                                                               │
│  Async / Futures                                              │
│   Future                                                      │
│   CompletableFuture                                           │
│                                                               │
│  Synchronizers                                                │
│   CountDownLatch                                              │
│   CyclicBarrier                                               │
│   Semaphore                                                   │
│   Phaser                                                      │
│   Exchanger                                                   │
│                                                               │
│  Concurrent Collections                                      │
│   ConcurrentHashMap                                           │
│   ConcurrentLinkedQueue                                       │
│   CopyOnWriteArrayList                                        │
│   BlockingQueue                                               │
│                                                               │
│  Atomics (Lock-free)                                          │
│   AtomicInteger                                               │
│   AtomicLong                                                  │
│   AtomicReference                                             │
│   LongAdder                                                   │
│   LongAccumulator                                             │
│   VarHandle                                                   │
│                                                               │
└───────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌───────────────────────────────────────────────────────────────┐
│ LEVEL 1 — java.lang (Primitive Threads & Locks)               │
│                                                               │
│   Thread                                                      │
│   Runnable                                                    │
│   ThreadGroup                                                 │
│                                                               │
│   Object (monitor / intrinsic lock)                           │
│                                                               │
└───────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌───────────────────────────────────────────────────────────────┐
│ LEVEL 0 — OPERATING SYSTEM                                   │
│                                                               │
│   Native OS Thread                                            │
│   Kernel Scheduler                                            │
│                                                               │
└───────────────────────────────────────────────────────────────┘

```