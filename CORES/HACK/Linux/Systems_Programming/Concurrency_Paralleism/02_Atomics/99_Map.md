```js
Concurrency Foundations  
│  
├── 1. Atomics  
│   ├── What atomic means  
│   ├── CPU atomic instructions  
│   ├── Linux kernel atomic API  
│   ├── Compare-and-Swap  
│   └── Practical kernel usage  
│  
└── 2. Memory Ordering  
    ├── CPU reordering  
    ├── Memory models  
    ├── Memory barriers  
    ├── Acquire/Release semantics  
    └── C11 memory model


```

Memory Ordering

1. Introduction to memory ordering
2. CPU memory reordering
3. Compiler reordering
4. Memory models
   - x86
   - ARM
   - RISC-V
5. Memory barriers
6. Acquire / Release semantics
7. Sequential consistency
8. C11 memory model
9. Linux kernel ordering primitives
10. Real kernel examples


### 7. Acquire / Release Semantics

Explain synchronization patterns.

smp_load_acquire()  
smp_store_release()

---

### 8. Sequential Consistency

Explain the strongest ordering guarantee.

---

### 9. C11 Memory Model

Explain:

memory_order_relaxed  
memory_order_acquire  
memory_order_release  
memory_order_seq_cst

---

### 10. Linux Kernel Ordering APIs

Explain the Linux abstraction layer.