
# 1. Normal Memory Access (No Page Fault)

When a process runs, the CPU register **CR3** points to that process’s **page table root**.

Conceptually:

```
CR3 → PML4 → PDPT → PD → PT → physical page
```

Flow of a normal memory access:

```
CPU instruction
      │
      ▼
virtual address generated
      │
      ▼
TLB lookup
```

### Case 1 — TLB hit

If the translation is already cached:

```
virtual → physical address found instantly
```

CPU directly accesses RAM.

Fast path:

```
CPU
 │
 ▼
TLB
 │
 ▼
RAM
```

---

### Case 2 — TLB miss

The MMU walks the page tables in memory.

```
CPU
 │
 ▼
TLB miss
 │
 ▼
hardware page-table walk
 │
 ▼
PML4 → PDPT → PD → PT
 │
 ▼
physical page found
 │
 ▼
update TLB
 │
 ▼
access RAM
```

Still **no kernel involvement**.

---

# 2. When a Page Fault Happens

A **page fault occurs when the page table entry says the page is not present**.

Typical causes:

```
page not loaded in RAM
demand paging
copy-on-write
stack growth
invalid memory access
```

Then this happens.

---

# 3. CPU Raises a Page Fault Exception

The MMU detects:

```
PTE.present = 0
```

The CPU triggers the **page fault exception**.

On x86‑64 architecture this is:

```
#PF (Page Fault)
```

CPU automatically:

1. saves instruction state
    
2. switches to kernel mode
    
3. jumps to the kernel page fault handler
    

Inside the Linux Kernel this eventually reaches:

```
do_page_fault()
```

---

# 4. Linux Virtual Memory Manager Handles It

The kernel’s **virtual memory subsystem** now determines what kind of fault this is.

It checks the process memory map:

```
vm_area_struct
```

This describes regions like:

```
code
heap
stack
mmap files
shared libraries
```

Example:

```
0x400000–0x401000  → program code
0x7fff0000–...     → stack
```

The kernel decides:

```
Is the access valid?
```

---

# 5. If the Page Is Valid (Demand Paging)

Example: accessing memory mapped by `mmap()` or the heap.

Linux allocates a physical page:

```
allocate_page()
```

Then:

```
update page table entry
set present bit
set permissions
```

Example PTE change:

```
before:
present = 0

after:
present = 1
physical_page = 0x12345000
```

---

# 6. If File-Backed (Very Important Case)

For memory mapped files or executable code:

Linux reads the page from disk.

Example pipeline:

```
page fault
    │
    ▼
VFS
    │
    ▼
filesystem (like :contentReference[oaicite:4]{index=4})
    │
    ▼
block layer
    │
    ▼
disk
```

Then the page is placed into the **page cache**.

---

# 7. Updating the Page Tables

Once the page is ready:

```
page table entry updated
```

Now the virtual address is valid.

Example:

```
virtual page 0x7fff1234
      │
      ▼
physical page 0x45678000
```

---

# 8. Restarting the Faulting Instruction

Now the CPU resumes the instruction that caused the fault.

Important detail:

**The instruction is restarted automatically.**

The process never notices.

Now the translation works.

```
CPU
 │
 ▼
TLB lookup
 │
 ▼
page table
 │
 ▼
physical memory
```

The new translation is inserted into the **TLB**.

---

# 9. Final Execution Flow

Full lifecycle:

```
CPU instruction
     │
     ▼
virtual address generated
     │
     ▼
TLB lookup
     │
     ├── hit → access RAM
     │
     └── miss
          │
          ▼
          hardware page-table walk
          │
          ├── present → update TLB → RAM
          │
          └── not present
                 │
                 ▼
             page fault (#PF)
                 │
                 ▼
          kernel page fault handler
                 │
                 ▼
          memory manager allocates page
                 │
                 ▼
          update page table
                 │
                 ▼
          restart instruction
```

---

# 10. The Important Insight

You summarized it well, but the key distinction is:

### Hardware responsibilities

```
TLB lookup
page-table walk
fault detection
```

### Kernel responsibilities

```
allocate pages
load from disk
manage memory regions
update page tables
```

So the CPU **detects the fault**, but the **kernel resolves it**.

---

💡 One deeper insight that ties everything together:

When a page fault loads data from disk, it **does not go directly to process memory**.

Instead it goes to the **page cache**, which is shared by:

- normal file reads
    
- mmap
    
- executables
    
- shared libraries
    

That’s why **Linux filesystem performance is mostly memory performance**.

---

If you'd like, I can also explain a very interesting piece of engineering:

**“How mmap connects the virtual memory manager and the filesystem page cache.”**

That mechanism is one of the most elegant designs in the entire kernel.