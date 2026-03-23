Understanding **`mmap` internals** means understanding how **Linux virtual memory works**. When you call `mmap()`, the kernel **does NOT immediately allocate physical memory**. Instead it sets up **virtual memory mappings** and waits until you actually touch the memory.

This is one of the most elegant mechanisms inside the Linux kernel.

We will walk through it step-by-step:

1. User program calls `mmap`
    
2. CPU enters kernel via syscall
    
3. Kernel creates a **Virtual Memory Area (VMA)**
    
4. No physical memory yet
    
5. Program accesses memory
    
6. **Page fault occurs**
    
7. Kernel allocates physical page or loads file page
    
8. Page table updated
    
9. Program resumes
    

---

# 1. User Program Calls mmap

Example program:

```c
#include <stdio.h>
#include <sys/mman.h>
#include <unistd.h>

int main() {

    size_t size = 1024 * 1024 * 1024; // 1 GB

    char *p = mmap(NULL,
                   size,
                   PROT_READ | PROT_WRITE,
                   MAP_PRIVATE | MAP_ANONYMOUS,
                   -1,
                   0);

    if (p == MAP_FAILED) {
        perror("mmap");
        return 1;
    }

    printf("mmap succeeded\n");

    getchar();   // pause so we inspect memory

    p[0] = 'A';

    printf("first byte written\n");

    getchar();

    munmap(p, size);
}
```

Compile:

```
gcc mmap_demo.c
```

Run:

```
./a.out
```

Even though we requested **1GB**, the system allocates almost **no RAM yet**.

Why?

Because Linux uses **lazy allocation**.

---

# 2. The mmap System Call

User code calls:

```
mmap()
```

glibc converts it into a **syscall**.

Kernel entry:

```
sys_mmap()
   ↓
do_mmap()
```

Inside the Linux kernel (simplified):

```
sys_mmap
   → ksys_mmap_pgoff
      → vm_mmap
         → do_mmap
```

This function lives in:

```
mm/mmap.c
```

---

# 3. Kernel Creates a Virtual Memory Area (VMA)

The kernel does **NOT allocate pages yet**.

Instead it creates a structure called:

```
vm_area_struct
```

This describes a memory region.

Simplified structure:

```c
struct vm_area_struct {
    unsigned long vm_start;
    unsigned long vm_end;

    struct mm_struct *vm_mm;

    int vm_flags;

    struct file *vm_file;

    struct vm_area_struct *vm_next;
};
```

Meaning:

|Field|Meaning|
|---|---|
|vm_start|start address|
|vm_end|end address|
|vm_file|backing file|
|vm_flags|permissions|

So kernel basically records:

```
"From address A to address B,
this memory exists"
```

But **no physical RAM is attached yet**.

---

# 4. The Mapping Appears in /proc

Run:

```
cat /proc/<pid>/maps
```

Example output:

```
7f1b54000000-7f1b58000000 rw-p 00000000 00:00 0
```

This means:

```
4GB virtual memory reserved
```

But actual RAM usage may still be **0 pages**.

---

# 5. What Happens When You Access Memory

When program executes:

```c
p[0] = 'A';
```

CPU tries to translate the virtual address.

Steps:

```
virtual address
   ↓
page table lookup
```

But page table entry is **not present**.

CPU raises:

```
PAGE FAULT
```

Interrupt:

```
#PF
```

Control transfers to kernel.

---

# 6. Linux Page Fault Handler

Kernel function:

```
do_page_fault()
```

Simplified flow:

```
page_fault
   ↓
find_vma()
   ↓
handle_mm_fault()
```

Kernel checks:

1. Is the address inside a valid VMA?
    
2. What type of mapping is it?
    

---

# 7. Anonymous mmap Page Allocation

If mapping is:

```
MAP_ANONYMOUS
```

Kernel allocates a new physical page.

Simplified kernel logic:

```
alloc_page()
   ↓
zero_page()
   ↓
map_page()
```

The kernel then updates the **page table entry (PTE)**.

Now:

```
virtual address → physical page
```

Program resumes.

---

# 8. File-backed mmap Page Fault

If mapping is a **file**, the flow is different.

Instead of allocating new memory, kernel loads a page from disk.

Flow:

```
page fault
   ↓
read file page
   ↓
put page in page cache
   ↓
map page into process
```

Kernel functions:

```
filemap_fault()
```

So the file page becomes memory.

---

# 9. Example Demonstrating Lazy Allocation

Complete example:

```c
#include <stdio.h>
#include <sys/mman.h>
#include <unistd.h>

int main() {

    size_t size = 1024L * 1024 * 1024; // 1GB

    char *p = mmap(NULL,
                   size,
                   PROT_READ | PROT_WRITE,
                   MAP_PRIVATE | MAP_ANONYMOUS,
                   -1,
                   0);

    printf("mapped 1GB\n");

    getchar();

    for (size_t i = 0; i < size; i += 4096) {
        p[i] = 1;
    }

    printf("pages touched\n");

    getchar();

    munmap(p, size);
}
```

Key idea:

```
touch every 4096 bytes
```

Because:

```
page size = 4096 bytes
```

Each write triggers **one page fault**.

---

# 10. Observing Page Faults

Run program then check:

```
cat /proc/<pid>/stat
```

or

```
perf stat ./a.out
```

You will see:

```
page-faults
```

increase when memory is accessed.

---

# 11. Huge Mapping Handling

Example:

```
mmap 100GB
```

Linux does NOT allocate 100GB RAM.

It only stores:

```
VMA metadata
```

Which is very small (~200 bytes).

Memory allocated only when pages are accessed.

This allows programs like:

- databases
    
- browsers
    
- memory caches
    

to reserve huge address space.

---

# 12. Page Tables Updated

After page allocation:

Kernel sets Page Table Entry.

Simplified:

```
PTE =
{
   physical_page_address
   read/write flags
   present bit
}
```

Now CPU can translate addresses.

Future accesses **do not trigger page faults**.

---

# 13. Copy-on-Write (MAP_PRIVATE)

If mapping is:

```
MAP_PRIVATE
```

And process writes to file page:

Kernel performs **copy-on-write**.

Flow:

```
file page
   ↓
write attempt
   ↓
page fault
   ↓
duplicate page
   ↓
modify private copy
```

Used heavily in:

```
fork()
```

---

# 14. mmap and fork()

Example:

```c
#include <stdio.h>
#include <sys/mman.h>
#include <unistd.h>

int main() {

    int *p = mmap(NULL,
                  4096,
                  PROT_READ | PROT_WRITE,
                  MAP_PRIVATE | MAP_ANONYMOUS,
                  -1,
                  0);

    *p = 5;

    pid_t pid = fork();

    if (pid == 0) {
        *p = 10;
        printf("child: %d\n", *p);
    } else {
        sleep(1);
        printf("parent: %d\n", *p);
    }
}
```

Output:

```
child: 10
parent: 5
```

Because **copy-on-write duplicated the page**.

---

# 15. mmap Removal

When calling:

```
munmap()
```

Kernel does:

```
remove VMA
free page tables
release physical pages
```

Kernel function:

```
do_munmap()
```

---

# 16. Full mmap Lifecycle

Complete flow:

```
user mmap()
      ↓
syscall entry
      ↓
kernel creates VMA
      ↓
no physical memory yet
      ↓
program accesses memory
      ↓
page fault
      ↓
kernel allocates page OR loads file page
      ↓
page table updated
      ↓
program continues
```

---

# 17. Why mmap Is So Powerful

Because it enables:

• **lazy allocation**  
• **zero-copy file IO**  
• **shared memory**  
• **copy-on-write fork**  
• **memory mapped devices**

This is why **modern operating systems revolve around `mmap`**.

Even programs like:

- databases
    
- browsers
    
- virtual machines
    
- game engines
    

depend heavily on it.

---

If you'd like, the **next level of understanding (very interesting for systems programmers)** would be:

- how **page tables work (4-level paging on x86-64)**
    
- how **TLB interacts with mmap**
    
- how **fork uses copy-on-write internally**
    
- how **glibc malloc switches between brk and mmap**
    

Those reveal the **deep architecture behind modern OS memory systems.**