

---

# 1. Physical Memory (RAM)

At the lowest level the machine simply has **physical RAM**.

Example:

```
16 GB RAM
```

Linux divides physical RAM into **pages**.

Typical page size:

```
4 KB
```

So:

```
16 GB / 4 KB ≈ 4 million pages
```

Each page is represented inside the kernel by:

```
struct page
```

Conceptually:

```
physical RAM
 ├── page 0
 ├── page 1
 ├── page 2
 └── ...
```

This is the basic **allocation unit** used by the virtual memory manager.

---

# 2. Memory Nodes (NUMA concept)

On modern servers, memory is not always uniform. Many systems use **NUMA (Non-Uniform Memory Access)**.

In NUMA systems:

- each CPU socket has **its own local RAM**
    
- accessing local RAM is faster than remote RAM
    

Example system:

```
CPU 0 ── RAM bank A
CPU 1 ── RAM bank B
```

Linux groups each physical memory bank into a **node**.

Structure:

```
pg_data_t
```

Conceptually:

```
System memory
 ├── Node 0
 │     └── local RAM
 └── Node 1
       └── local RAM
```

Example:

```
Node 0 → 8 GB
Node 1 → 8 GB
```

The scheduler tries to allocate memory **from the node close to the CPU running the process**.

This improves cache and latency.

---

# 3. Zones (Memory Categories)

Inside each node, memory is divided into **zones**.

Zones exist mainly because **hardware limitations require different address ranges**.

Typical zones on x86 systems:

|Zone|Purpose|
|---|---|
|ZONE_DMA|memory usable by old DMA devices|
|ZONE_DMA32|memory accessible by 32-bit devices|
|ZONE_NORMAL|normal kernel memory|
|ZONE_MOVABLE|pages that can be relocated|

Conceptually:

```
Node 0
 ├── ZONE_DMA
 ├── ZONE_DMA32
 ├── ZONE_NORMAL
 └── ZONE_MOVABLE
```

Example memory layout:

```
0–16 MB       → ZONE_DMA
16 MB–4 GB    → ZONE_DMA32
4 GB+         → ZONE_NORMAL
```

Each zone contains a pool of **physical pages**.

---

# 4. Pages Inside Zones

Each zone tracks its pages using:

```
struct page
```

Example:

```
ZONE_NORMAL
 ├── page
 ├── page
 ├── page
 └── page
```

Each page descriptor contains information like:

```
flags
reference count
mapping
LRU state
```

This is how the kernel tracks every physical page.

---

# 5. The Full Memory Hierarchy

The structure looks like this:

```
System
 ├── Node 0
 │     ├── Zone DMA
 │     ├── Zone DMA32
 │     └── Zone NORMAL
 │            ├── page
 │            ├── page
 │            └── page
 │
 └── Node 1
       ├── Zone NORMAL
       └── Zone MOVABLE
```

So the hierarchy is:

```
Node
  → Zone
      → Page
```

---

# 6. How the Virtual Memory Manager Uses This

When a process needs memory (for example `malloc()`), the request eventually reaches the kernel.

Typical path:

```
malloc()
   ↓
brk() / mmap()
   ↓
Linux VM manager
   ↓
page allocator
   ↓
zone → node → page
```

The kernel selects a page using the **buddy allocator**.

Example flow:

```
process requests memory
       ↓
kernel chooses node (NUMA)
       ↓
select zone (NORMAL etc)
       ↓
buddy allocator finds free page
       ↓
returns physical page
```

---

# 7. Updating the Page Tables

Once the kernel allocates a page:

```
physical page → mapped to virtual address
```

The VM manager updates the process page table.

Example:

```
virtual address 0x7f1234000
      ↓
physical page frame 105820
```

Then:

```
page table entry updated
TLB updated
```

Now the CPU can access the memory.

---

# 8. Example: Page Fault Allocation

Suppose a program touches a new heap address.

```
virtual address access
       ↓
page fault
```

Kernel handles the fault:

```
do_page_fault()
     ↓
handle_mm_fault()
     ↓
alloc_page()
```

Allocation flow:

```
Node → Zone → Page
```

Example:

```
Node 0
  Zone NORMAL
     page #20391
```

Then the kernel:

```
updates page table
restarts instruction
```

---

# 9. Why Linux Uses Zones

Zones exist mainly for **hardware constraints**.

Example: old devices could only DMA into **low memory**.

So Linux ensures:

```
device DMA allocation → ZONE_DMA
normal kernel memory → ZONE_NORMAL
```

This keeps drivers working correctly.

---

# 10. Why Nodes Exist

Nodes improve performance on **NUMA systems**.

Example:

```
CPU 0 accesses RAM on Node 0 → fast
CPU 0 accesses RAM on Node 1 → slower
```

So Linux tries to allocate:

```
CPU → local node memory
```

This is called **NUMA locality**.

---

# 11. How It All Connects to Virtual Memory

Virtual memory manager responsibilities:

```
manage virtual address spaces
handle page faults
map virtual pages to physical pages
```

To do that it must allocate **physical pages**.

Those pages come from:

```
Node → Zone → Page
```

So the memory subsystem pipeline becomes:

```
Virtual Address
      ↓
Page Table
      ↓
Physical Page
      ↓
Node / Zone allocator
```

---

# 12. Final Mental Model

```
Virtual Memory System
        │
        ▼
Page allocator
        │
        ▼
NUMA Node
        │
        ▼
Memory Zone
        │
        ▼
Physical Page
```

This structure allows Linux to support:

- huge RAM sizes
    
- NUMA machines
    
- DMA hardware constraints
    
- efficient page allocation
    

---

✅ **Key idea:**

Virtual memory deals with **virtual → physical mapping**, but the physical memory manager organizes RAM as:

```
Nodes → Zones → Pages
```

so the kernel can efficiently allocate the pages that back virtual memory.

---

If you'd like, the next step that makes everything even clearer is understanding **the Linux buddy allocator** — the algorithm that actually finds free pages inside zones. It's one of the core algorithms in the Linux memory subsystem.