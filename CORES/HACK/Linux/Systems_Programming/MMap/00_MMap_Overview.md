The Linux **`mmap`** system call is one of the most powerful primitives in Unix-like systems. Many programmers first see it as _“another way to allocate memory”_, but its real purpose is much deeper. It connects **files, devices, and virtual memory** into one unified mechanism.

To really understand why `mmap` exists, we need to answer three questions:

1. What problem does `mmap` solve?
    
2. Why can’t `malloc()` or `sbrk()` solve it?
    
3. What are the real-world use cases?
    

Let's walk through it carefully.

---

# 1. What `mmap` Actually Does

`mmap` **maps something into your process address space**.

That “something” could be:

- a file
    
- anonymous memory (RAM not backed by file)
    
- shared memory between processes
    
- hardware device memory
    

After mapping, the object appears like **normal memory**.

You just use pointers.

No `read()`, no `write()`.

---

### Basic Prototype

```c
#include <sys/mman.h>

void *mmap(
    void *addr,
    size_t length,
    int prot,
    int flags,
    int fd,
    off_t offset
);
```

Important parameters:

|Parameter|Meaning|
|---|---|
|`addr`|preferred virtual address|
|`length`|mapping size|
|`prot`|memory permissions|
|`flags`|mapping type|
|`fd`|file descriptor|
|`offset`|file offset|

Returns:

```
pointer to mapped memory
```

or

```
MAP_FAILED
```

---

# 2. Why `malloc()` Cannot Replace `mmap`

`malloc()` is a **user-space allocator**.

Internally it does two things:

- small allocations → `brk/sbrk`
    
- large allocations → `mmap`
    

So **`malloc` itself uses `mmap`**.

But `malloc` cannot do the following things.

---

## 2.1 File Mapping

`malloc` cannot map a file.

With `mmap`, a file becomes memory.

Example:

Instead of

```
read(fd, buffer)
```

you do

```
buffer[i]
```

This allows **zero-copy file IO**.

---

## 2.2 Shared Memory

`malloc` memory exists **only inside one process**.

`mmap` can create memory shared between processes.

---

## 2.3 Memory Protection

`mmap` allows:

```
PROT_READ
PROT_WRITE
PROT_EXEC
PROT_NONE
```

This enables:

- JIT compilers
    
- guard pages
    
- sandboxing
    

`malloc` cannot control memory permissions.

---

## 2.4 Memory Mapped Devices

Hardware devices are mapped into memory space.

Example:

```
GPU memory
framebuffer
NIC buffers
```

`malloc` cannot access hardware memory.

---

## 2.5 Lazy Loading

`mmap` loads pages **on demand**.

The kernel uses **page faults**.

Meaning:

A 2GB file mapping may consume only **a few KB RAM initially**.

`malloc` must allocate immediately.

---

# 3. Why `sbrk()` Cannot Replace `mmap`

`sbrk` simply **moves the program break**.

```
heap grows upward
```

Diagram:

```
Stack
 ↓

Heap (sbrk grows this)

 ↑
Data
Code
```

Problems:

### 1. Heap must remain contiguous

`sbrk` can only grow **one continuous heap**.

But modern programs need **many independent memory regions**.

---

### 2. Cannot release middle memory

If you allocate:

```
A
B
C
```

You cannot free **B** easily.

With `mmap`, each mapping is independent.

---

### 3. No file backing

`sbrk` only allocates RAM.

It cannot map files.

---

### 4. Fragmentation

Modern allocators avoid fragmentation using many `mmap` regions.

---

# 4. Simplest Example: Anonymous Memory

This behaves like `malloc`.

### Complete Program

```c
#include <stdio.h>
#include <sys/mman.h>
#include <string.h>
#include <unistd.h>

int main() {

    size_t size = 4096;

    char *memory = mmap(
        NULL,
        size,
        PROT_READ | PROT_WRITE,
        MAP_PRIVATE | MAP_ANONYMOUS,
        -1,
        0
    );

    if (memory == MAP_FAILED) {
        perror("mmap failed");
        return 1;
    }

    strcpy(memory, "Hello from mmap!");

    printf("%s\n", memory);

    munmap(memory, size);

    return 0;
}
```

Compile:

```
gcc mmap_basic.c -o mmap_basic
```

Output:

```
Hello from mmap!
```

---

# 5. File Mapping Example (Zero Copy File IO)

Instead of reading file using `read()`.

We map it directly.

### Complete Program

```c
#include <stdio.h>
#include <sys/mman.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <unistd.h>

int main() {

    int fd = open("test.txt", O_RDONLY);

    if (fd < 0) {
        perror("open");
        return 1;
    }

    struct stat st;
    fstat(fd, &st);

    size_t size = st.st_size;

    char *data = mmap(
        NULL,
        size,
        PROT_READ,
        MAP_PRIVATE,
        fd,
        0
    );

    if (data == MAP_FAILED) {
        perror("mmap");
        return 1;
    }

    write(1, data, size);

    munmap(data, size);
    close(fd);

    return 0;
}
```

Now the file content appears as:

```
data[i]
```

No `read()` loop needed.

---

# 6. Shared Memory Between Processes

Two processes can share memory using `MAP_SHARED`.

### Writer Program

```c
#include <stdio.h>
#include <sys/mman.h>
#include <fcntl.h>
#include <unistd.h>
#include <string.h>

int main() {

    int fd = open("shared.bin", O_CREAT | O_RDWR, 0666);
    ftruncate(fd, 4096);

    char *mem = mmap(NULL, 4096,
        PROT_READ | PROT_WRITE,
        MAP_SHARED,
        fd,
        0);

    strcpy(mem, "Hello from process 1");

    printf("written message\n");

    sleep(20);

    munmap(mem, 4096);
    close(fd);

    return 0;
}
```

---

### Reader Program

```c
#include <stdio.h>
#include <sys/mman.h>
#include <fcntl.h>
#include <unistd.h>

int main() {

    int fd = open("shared.bin", O_RDONLY);

    char *mem = mmap(NULL, 4096,
        PROT_READ,
        MAP_SHARED,
        fd,
        0);

    printf("message: %s\n", mem);

    munmap(mem, 4096);
    close(fd);

    return 0;
}
```

Two processes now share memory **without pipes or sockets**.

---

# 7. Huge File Processing (Major Real World Use)

Example: searching large file.

### Without mmap

```
read()
copy to user buffer
scan
repeat
```

Many copies.

---

### With mmap

File is memory.

### Complete Example

```c
#include <stdio.h>
#include <sys/mman.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <unistd.h>

int main() {

    int fd = open("bigfile.txt", O_RDONLY);

    struct stat st;
    fstat(fd, &st);

    size_t size = st.st_size;

    char *data = mmap(NULL, size,
        PROT_READ,
        MAP_PRIVATE,
        fd,
        0);

    size_t count = 0;

    for (size_t i = 0; i < size; i++) {
        if (data[i] == '\n')
            count++;
    }

    printf("lines: %zu\n", count);

    munmap(data, size);
    close(fd);

    return 0;
}
```

Tools like:

```
ripgrep
sqlite
chromium
databases
```

use this technique.

---

# 8. Guard Pages (Stack Overflow Detection)

You can create a **page that crashes when accessed**.

```c
#include <stdio.h>
#include <sys/mman.h>

int main() {

    void *p = mmap(NULL, 4096,
        PROT_NONE,
        MAP_PRIVATE | MAP_ANONYMOUS,
        -1,
        0);

    printf("accessing...\n");

    char *x = (char*)p;

    x[0] = 1;

    return 0;
}
```

Result:

```
Segmentation fault
```

Used in:

- stack overflow detection
    
- debugging tools
    
- sanitizers
    

---

# 9. Memory Allocator Implementation

Modern allocators (glibc, jemalloc, tcmalloc) use `mmap`.

Large allocations:

```
malloc(1MB)
```

internally becomes:

```
mmap()
```

Why?

Because it can be **returned directly to OS using `munmap`**.

---

# 10. JIT Compilers

JIT compilers allocate executable memory.

Example:

```c
mmap(
 NULL,
 4096,
 PROT_READ | PROT_WRITE | PROT_EXEC,
 MAP_PRIVATE | MAP_ANONYMOUS,
 -1,
 0
)
```

Then:

```
write machine code
execute it
```

Used in:

- Java JVM
    
- V8
    
- LuaJIT
    
- WebAssembly engines
    

---

# 11. How OS Actually Implements mmap

Kernel creates **Virtual Memory Area (VMA)**.

Mapping stored in process memory map:

```
/proc/<pid>/maps
```

Example:

```
7f8a4a000000-7f8a4a021000 rw-p
```

Pages are loaded **only when accessed**.

Mechanism:

```
page fault
 → kernel loads file page
 → maps into process
```

This is called:

```
demand paging
```

---

# 12. Real Software That Relies on mmap

`mmap` is used heavily in:

|Software|Reason|
|---|---|
|SQLite|database pages|
|Chromium|fast file IO|
|Redis|persistence|
|Git|packfile reading|
|PostgreSQL|shared buffers|
|JVM|class loading|

---

# 13. Simple Mental Model

Think of `mmap` like this:

```
file  ----\
           \
device ----- >  mapped into virtual memory
           /
RAM   ----/
```

Everything becomes **memory**.

Once mapped:

```
data[i]
```

is enough.

---

# 14. Key Takeaway

`mmap` is not just memory allocation.

It is a **unified interface between files, devices, and virtual memory**.

`malloc` = convenient heap allocator  
`sbrk` = primitive heap growth  
`mmap` = **general virtual memory mapping system**

That’s why modern systems rely heavily on it.

---

If you'd like, I can also show a **very interesting deep topic for systems programmers**:

- **How `mmap` enables zero-copy networking**
    
- **How databases like SQLite use mmap internally**
    
- **How the kernel handles page faults for mmap**
    

Those reveal some of the **most beautiful parts of OS design.**