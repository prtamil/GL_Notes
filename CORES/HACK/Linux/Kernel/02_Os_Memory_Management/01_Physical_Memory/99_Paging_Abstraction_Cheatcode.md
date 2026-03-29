### x86-64 4-Level Paging and the Nested Dictionary Analogy

In x86-64, virtual memory uses **4-level page tables** to map virtual addresses (VAs) to physical addresses. Conceptually, we can think of each page table as a **nested dictionary**: the VA is split into indices, which serve as keys to traverse these dictionaries.

A **48-bit canonical VA** is divided as follows:
```txt
+---------+---------+---------+---------+---------+
|  PML4   |  PDPT   |   PD    |   PT    | Offset  |
| 9 bits  | 9 bits  | 9 bits  | 9 bits  | 12 bits |
+---------+---------+---------+---------+---------+

```

Each 9-bit index selects one of 512 entries in its respective table. The tables conceptually look like this:

```txt
PML4_table[PML4_idx] -> PDPT_table
PDPT_table[PDPT_idx] -> PD_table
PD_table[PD_idx]       -> PT_table
PT_table[PT_idx]       -> Physical_Frame_Base
Physical_Frame_Base + Offset -> Final Physical Address

```

Each entry is **more than just a pointer**: it contains **permission flags** along with the address of the next level or physical page. Common flags include:

- **P (Present)** – is the entry valid?
    
- **RW (Read/Write)** – is writing allowed?
    
- **US (User/Supervisor)** – is access allowed from user mode?
    
- **NX (No Execute)** – is execution prohibited?
    
- **A/D (Accessed/Dirty)** – set automatically by the CPU
    

The **CPU performs a page table walk** for each memory access:

1. Look up `PML4_idx` in PML4 table → check flags.
    
2. Look up `PDPT_idx` in PDPT table → check flags.
    
3. Look up `PD_idx` in PD table → check flags.
    
4. Look up `PT_idx` in PT table → check flags and get physical frame.
    
5. Add the **Offset** to reach the exact physical address.
    

At any level, if a **flag check fails**, a page fault occurs. The OS is responsible for setting up these tables and handling faults.

This nested dictionary analogy helps visualize the VA-to-physical mapping while retaining the **hierarchical structure and permission checks** of actual x86-64 paging.


```txt

x86-64 4-Level Paging: Nested Dicts + Flags + CPU Walk

Virtual Address (VA):
+-----------+-----------+-----------+-----------+-----------+
|  PML4     |  PDPT     |   PD      |   PT      |  Offset   |
| 9 bits    | 9 bits    | 9 bits    | 9 bits    | 12 bits   |
+-----------+-----------+-----------+-----------+-----------+

Nested Tables ("Dicts"):

PML4_table
+-------------------------------+
| PML4_idx -> (PDPT_table, P,RW,US,...) |
+-------------------------------+
        |
        v
PDPT_table
+-------------------------------+
| PDPT_idx -> (PD_table, P,RW,US,...)  |
+-------------------------------+
        |
        v
PD_table
+-------------------------------+
| PD_idx -> (PT_table, P,RW,US,...)   |
+-------------------------------+
        |
        v
PT_table
+------------------------------------------+
| PT_idx -> (Physical_Frame_Base, P,RW,US,NX,...) |
+------------------------------------------+
        |
        v
Physical_Frame_Base + Offset
        |
        v
Final Physical Address

CPU Walk & Permission Checks:

1. PML4: Present? (P=1)  → else #PF  
          User/Priv? (US)  
          Writable? (RW)  

2. PDPT: Present? (P=1)  → else #PF  
          User/Priv? (US)  
          Writable? (RW)  

3. PD:   Present? (P=1)  → else #PF  
          User/Priv? (US)  
          Writable? (RW)  

4. PT:   Present? (P=1)  → else #PF  
          User/Priv? (US)  
          Writable? (RW)  
          Execute? (NX)  

Offset added to Physical_Frame_Base → final physical address.

Legend:
- P   = Present
- RW  = Read/Write
- US  = User/Supervisor
- NX  = No Execute
- #PF = Page Fault

```


```txt
VA[47:0] -> [PML4_idx | PDPT_idx | PD_idx | PT_idx | Offset]

CPU Page Table Walk:

VA
 |
 v
PML4_table[PML4_idx] (P,RW,US)
 |
 v
PDPT_table[PDPT_idx] (P,RW,US)
 |
 v
PD_table[PD_idx] (P,RW,US)
 |
 v
PT_table[PT_idx] (P,RW,US,NX)
 |
 v
Physical_Frame_Base + Offset
 |
 v
Final Physical Address

Checks at each level:
- P = Present? else #PF
- RW = Write allowed?
- US = User/Supervisor access?
- NX = No Execute (PT only)

```


💡 **Legend**

- 🏗️ VA — Virtual Address (split into indices + offset)
- 🗂️ — Page table (dict)
- 📦 — Physical Frame base address
- 🧩 — Offset within 4 KB page
- 🧠 — Final physical address
- 💥 #PF — Page Fault
    
- Flags → control access (Present, Read/Write, User/Supervisor, No Execute)
    

Perfect for quick mental recall in Obsidian.

```txt
🏗️ VA → 🗂️ PML4[PML4_idx] → 🗂️ PDPT[PDPT_idx] → 🗂️ PD[PD_idx] → 🗂️ PT[PT_idx] → 📦 PF_Base + 🧩 Offset → 🧠 Physical Addr
🔍 Flags: P✅ RW✏️ US👤 NX🚫exec → any violation → 💥 #PF

```