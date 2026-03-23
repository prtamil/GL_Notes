If you want to truly understand **Linux memory**, there are a handful of classic essays and papers that systems programmers repeatedly recommend. These writings explain not just _what happens_, but _why the OS is designed that way_. Reading them alongside your experiments (`/proc`, `perf`, small C programs) will deepen your understanding quickly.

Below is a **curated reading list of ~15 essays/papers** that many kernel developers, systems engineers, and database engineers recommend.

I arranged them roughly **from easier → deeper kernel-level material**.

---

# Linux Memory Internals – 15 Essential Essays

## 1. Linux Virtual Memory Overview

📄 **Understanding the Linux Virtual Memory Manager**

- Author: Mel Gorman
    
- One of the best explanations of Linux VM internals.
    

Topics:

- page frames
    
- zones
    
- page allocation
    
- page tables
    
- page cache
    
- swap
    

This is essentially **the definitive book on Linux memory**.

---

## 2. The mmap Design Philosophy

📄 **Memory Mapping Explained**

Topics:

- why `mmap` exists
    
- file-backed pages
    
- page cache
    
- demand paging
    

Key idea:

```
Files are just memory.
```

Many high-performance systems rely on this concept.

---

## 3. What Every Programmer Should Know About Memory

📄 **What Every Programmer Should Know About Memory**

- Author: Ulrich Drepper
    

This is one of the **most famous systems essays ever written**.

Topics:

- caches
    
- memory latency
    
- NUMA
    
- page tables
    
- memory access patterns
    

Even database engineers and game engine developers read this.

---

## 4. Virtual Memory: A Simplified Explanation

📄 **Virtual Memory in the Linux Kernel**

Focus:

```
virtual address
→ page table
→ physical page
```

Clear introduction to demand paging.

---

## 5. Demand Paging and Page Faults

📄 **Demand Paging and Lazy Allocation**

Topics:

- page faults
    
- minor vs major faults
    
- loading pages from disk
    
- zero pages
    

This essay explains why:

```
mmap(1TB)
```

does not allocate 1TB RAM.

---

## 6. Copy-On-Write Explained

📄 **Copy-On-Write Fork**

Topics:

- `fork()` memory duplication
    
- page table sharing
    
- write faults
    
- page duplication
    

Without COW, `fork()` would be extremely slow.

---

## 7. Linux Page Cache Architecture

📄 **The Linux Page Cache**

Topics:

- file-backed pages
    
- page cache
    
- writeback
    
- disk IO interaction
    

Understanding this explains why:

```
mmap(file)
```

is often faster than `read()`.

---

## 8. How the Kernel Allocates Physical Memory

📄 **The Buddy Allocator in Linux**

Topics:

- physical page allocation
    
- fragmentation
    
- memory zones
    

Key concept:

```
buddy allocator
```

Used by Linux to allocate physical pages efficiently.

---

## 9. Slab Allocator

📄 **The Slab Allocator**

Topics:

- kernel object allocation
    
- cache reuse
    
- reducing fragmentation
    

This allocator is used for:

```
task_struct
inode
dentry
```

and other kernel objects.

---

## 10. Page Tables on x86-64

📄 **x86-64 Paging Explained**

Topics:

```
PML4
PDPT
PD
PT
```

This shows how the CPU translates:

```
virtual address → physical address
```

using **4-level page tables**.

---

## 11. TLB and Memory Translation

📄 **Translation Lookaside Buffer (TLB)**

Topics:

- TLB cache
    
- TLB misses
    
- page walk cost
    
- performance impact
    

Understanding this is crucial for:

- high performance systems
    
- database engines
    
- game engines
    

---

## 12. Linux Memory Overcommit

📄 **Memory Overcommit and the OOM Killer**

Topics:

- why Linux allows allocating more memory than RAM
    
- OOM killer
    
- memory heuristics
    

Explains why programs can allocate huge memory but still run.

---

## 13. Swap and Memory Pressure

📄 **Swap and Reclaim**

Topics:

- page reclaim
    
- swap-out
    
- memory pressure
    
- page eviction
    

This shows how Linux manages memory when RAM runs out.

---

## 14. NUMA Memory Systems

📄 **NUMA Memory Architecture**

Topics:

- multi-socket machines
    
- memory locality
    
- NUMA policies
    

Important for:

- databases
    
- HPC systems
    
- game servers
    

---

## 15. Observing Linux Memory

📄 **Linux Memory Debugging Interfaces**

Topics:

```
/proc/meminfo
/proc/<pid>/maps
/proc/<pid>/smaps
pmap
perf
```

Learning to observe memory behavior is extremely valuable.

---

# The Three Most Important Essays (Start Here)

If you read only **three**, start with:

1️⃣ **What Every Programmer Should Know About Memory**  
2️⃣ **Understanding the Linux Virtual Memory Manager**  
3️⃣ **x86-64 Paging Explained**

Together they explain **almost everything about memory behavior**.

---

# Best Learning Method

For each essay:

1. Read the concept
    
2. Write a small C program
    
3. Inspect with `/proc`
    
4. measure with `perf`
    

Example:

```
mmap experiment
page fault experiment
fork + COW experiment
```

This makes the learning **very concrete**.

---

# Why This Knowledge Is Rare

Most developers never learn:

- page tables
    
- TLB
    
- page faults
    
- copy-on-write
    

But these concepts power:

- databases
    
- browsers
    
- game engines
    
- operating systems
    

Which is why **systems programmers invest time here**.

---

If you'd like, I can also show you something **extremely illuminating next**:

**“The 12 experiments every systems programmer should run to understand Linux memory.”**

They are tiny C programs that reveal **how the OS memory system really behaves.**