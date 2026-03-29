# How a Binary Program Runs: A First-Principles Overview

---

## 1. The Moment You Press Enter

When you type `./program` in a shell, you trigger a chain of events that spans userspace, the kernel, and the hardware. The shell calls `execve(2)` — a syscall that says: *replace the current process image with this file*. From that moment, the kernel takes over.

The file you pointed to is an **ELF binary** (Executable and Linkable Format). The kernel doesn't just copy it into RAM and jump to it. It reads a structured header, maps specific parts of the file into virtual memory at specific addresses, sets up a stack, and then — only then — hands control to the program's entry point.

---

## 2. The ELF Binary Is a Map, Not a Dump

An ELF file is not a raw blob of machine code. It is a structured document describing *what to load, where to load it, and how to start*.

```
ELF File on Disk
┌─────────────────────────────┐
│  ELF Header (64 bytes)      │  ← magic number, arch, entry point VA
├─────────────────────────────┤
│  Program Headers (PHDRs)    │  ← loader uses these at runtime
│  (what the kernel reads)    │
├─────────────────────────────┤
│  .text   segment            │  ← machine code (LOAD, R+X)
│  .rodata segment            │  ← string literals, constants
├─────────────────────────────┤
│  .data   segment            │  ← initialized globals (LOAD, R+W)
│  .bss    segment            │  ← zero-initialized globals
├─────────────────────────────┤
│  Section Headers (SHDRs)    │  ← linker uses these at build time
│  .symtab, .debug_*, etc.    │  ← stripped in release builds
└─────────────────────────────┘
```

The key distinction: **Program Headers** are for the runtime loader. **Section Headers** are for the linker and debugger. A stripped binary can have no section headers and still execute perfectly.

### The ELF Header

The first 64 bytes (on x86-64) contain:

- **Magic**: `\x7fELF` — the kernel recognizes this and dispatches to the ELF loader
- **e_type**: `ET_EXEC` (static) or `ET_DYN` (PIE or shared library)
- **e_machine**: `EM_X86_64` — architecture
- **e_entry**: the virtual address where execution begins (`_start`, not `main`)
- **e_phoff**: offset to the program header table
- **e_phnum**: number of program headers

### Program Headers (the loader's instruction set)

Each PHDR says: *"take this chunk of the file, map it into virtual memory at this address, with these permissions."*

| Type | Meaning |
|---|---|
| `PT_LOAD` | Map this segment into process virtual memory |
| `PT_INTERP` | Path to the dynamic linker (`/lib64/ld-linux-x86-64.so.2`) |
| `PT_DYNAMIC` | Dynamic linking metadata (symbol table, relocations) |
| `PT_PHDR` | Location of the PHDR table itself |
| `PT_GNU_STACK` | Stack permission flags (NX bit) |
| `PT_GNU_RELRO` | Mark this region read-only after relocation |

---

## 3. How the Kernel Loads the Binary

`execve` in the kernel (Linux: `fs/binfmt_elf.c`) does the following:

### Step 1: Read and validate the ELF header

The kernel reads the first few hundred bytes. It checks the magic number, architecture, and ABI. If `e_type == ET_DYN`, the binary is position-independent — the kernel picks a load address. If `ET_EXEC`, load addresses are fixed.

### Step 2: Walk the PT_LOAD segments

For each `PT_LOAD` program header, the kernel calls `mmap()` *on the file itself*:

```
mmap(vaddr, filesz, prot, MAP_FIXED|MAP_PRIVATE, fd, offset)
```

This doesn't copy data into RAM. It establishes a **virtual memory area (VMA)** backed by the file. The pages are demand-paged — they fault in from disk the first time they're accessed.

If `memsz > filesz` (common for `.bss`), the extra pages are mapped as anonymous zero pages. This is how uninitialized globals cost no disk space.

### Step 3: Check for PT_INTERP (dynamic linker)

If the binary is dynamically linked, the kernel finds `/lib64/ld-linux-x86-64.so.2` from the `PT_INTERP` segment. It **also** loads the dynamic linker's ELF into the process's address space by the same mmap mechanism.

The kernel sets `e_entry` to the dynamic linker's entry point, not the program's. The dynamic linker runs first, resolves shared library symbols, then jumps to the real `_start`.

### Step 4: Set up the stack

The kernel allocates an anonymous region for the initial stack (typically 8 MB limit, grows down). At the top it writes the **auxiliary vector (auxv)**, then environment strings, then argument strings, then their pointers (`argv`), then `argc`. The stack pointer is set to point at `argc`.

```
High address
┌────────────────────────────┐
│  strings: argv[0], argv[1] │  actual bytes of arg strings
│  strings: envp[0], envp[1] │
├────────────────────────────┤
│  AT_ENTRY, AT_PHDR, ...    │  auxv: key-value pairs for ld.so
│  AT_NULL (terminator)      │
├────────────────────────────┤
│  NULL (envp terminator)    │
│  envp[n-1]                 │  pointers into env strings
│  envp[0]                   │
├────────────────────────────┤
│  NULL (argv terminator)    │
│  argv[argc-1]              │  pointers into arg strings
│  argv[0]                   │
├────────────────────────────┤
│  argc                      │  ← RSP points here at entry
└────────────────────────────┘
Low address
```

The **auxv** (auxiliary vector) is crucial: it tells the dynamic linker where the program headers are, the page size, the VDSO location, and the program's entry point — all without making syscalls.

### Step 5: Hand off

The kernel sets `RIP = entry_point`, `RSP = top_of_stack`, and returns from the syscall into userspace. Execution begins.

---

## 4. Process Virtual Memory Layout

After loading, the process address space looks like this on x86-64 Linux:

```
0xFFFFFFFFFFFFFFFF  ← canonical upper limit
│  kernel space     │  (not accessible from user mode)
0xFFFF800000000000
│                   │
│   [unmapped]      │
│                   │
0x7FFFFFFFFFFF
│  stack            │  grows downward, starts here
│  ↓                │
│  [stack guard]    │  unmapped page — catches stack overflow
│                   │
│  mmap region      │  shared libs, mmap'd files, ld.so, vdso
│  ↑                │  grows upward (kernel picks addresses)
│                   │
│  [heap]           │  grows upward via brk()/mmap()
│  ↑                │
│  .bss             │  zero-initialized (anonymous pages)
│  .data            │  initialized globals (file-backed)
│  .rodata          │  read-only data (file-backed)
│  .text            │  executable code (file-backed)
0x400000           │  (typical load address for ET_EXEC)
│                   │
│  [null guard]     │  first page unmapped (catches NULL deref)
0x0000000000000000
```

For PIE binaries (`ET_DYN`), the kernel uses ASLR to randomize the base address, so `.text` might be at `0x55a3b7c01000`. The offsets within the binary are still the same; only the base shifts.

### The Dynamic Linker's Work

Before `main` runs, `ld.so` does:

1. **Finds shared libraries** listed in the binary's `DT_NEEDED` entries (e.g., `libc.so.6`), searches `LD_LIBRARY_PATH`, `/etc/ld.so.cache`, then `mmap`s each one into the address space.
2. **Applies relocations**: patches addresses in the GOT/PLT tables. For lazy binding (default), PLT stubs initially point back into the resolver; the first call resolves and caches the symbol.
3. **Runs `.init` / constructors**: C++ global constructors, `__attribute__((constructor))` functions.
4. **Jumps to `_start`** (the real entry point).

### `_start` → `main`

`_start` is not your code. It's CRT (C Runtime) startup code, provided by `crt1.o`. It:

1. Zeroes `rbp` (marks the bottom of the call chain for stack unwinding)
2. Extracts `argc`, `argv`, `envp` from the stack
3. Calls `__libc_start_main(main, argc, argv, init, fini, rtld_fini, stack_end)`
4. `__libc_start_main` sets up the heap (`brk`), initializes `stdio`, calls `main`
5. The return value of `main` is passed to `exit()`

---

## 5. How the Process Tracks Its Resources

The kernel keeps a **process descriptor** (`struct task_struct` in Linux) for every process. This is the central ledger.

### Memory: The Virtual Memory Areas

The kernel tracks every mapped region in a data structure called the **mm_struct**, which contains a list (or red-black tree) of **vm_area_struct** nodes. Each VMA describes one contiguous region:

```
VMA: start=0x400000  end=0x401000  prot=R+X  flags=MAP_PRIVATE  file=./program  offset=0
VMA: start=0x600000  end=0x601000  prot=R+W  flags=MAP_PRIVATE  file=./program  offset=0x1000
VMA: start=0x7ffff7… end=0x7ffff8… prot=R+X  flags=MAP_PRIVATE  file=libc.so.6  ...
VMA: start=0x7ffff…  end=0x7ffff…  prot=R+W  flags=MAP_ANON     (heap)
VMA: start=0x7fffff… end=0x7fffff… prot=R+W  flags=MAP_ANON     (stack)
```

You can inspect this live: `cat /proc/<pid>/maps`.

When your program accesses a page that has a VMA but no physical page yet, the CPU raises a **page fault**. The kernel's fault handler looks up the VMA, allocates a physical page, copies data from the backing file (or zeros for anonymous), updates the page table, and resumes execution — all transparent to the program.

### The Heap

The heap is an anonymous VMA managed by two mechanisms:

- **`brk()` syscall**: moves the "program break" — the top of the heap — up or down. Old and simple. `malloc` uses this for small allocations via the C library's heap allocator (ptmalloc/jemalloc/tcmalloc).
- **`mmap(MAP_ANONYMOUS)`**: for large allocations (typically > 128 KB threshold), `malloc` calls `mmap` directly, getting a new VMA that is returned to the OS with `munmap` on `free`.

The kernel only tracks the VMA boundaries. The **heap allocator** (in libc) tracks the free/used blocks within the heap — the kernel doesn't know or care about that structure.

### File Descriptors

Every process has a **file descriptor table** — an array of pointers to kernel **file objects**. A file descriptor (fd) is just an index into this table.

```
fd table (per-process):
  [0] → file object → inode (stdin)
  [1] → file object → inode (stdout)
  [2] → file object → inode (stderr)
  [3] → file object → inode (your opened file)
  [4] → file object → socket
```

The **file object** stores: the current offset (seek position), access flags (`O_RDONLY` etc.), a pointer to the inode's operations table (`read`, `write`, `mmap`, `ioctl`...).

The **inode** is the filesystem's identity of the file — it persists beyond any particular open. Multiple file objects can point to the same inode (multiple `open()` calls), and multiple fds in the same or different processes can point to the same file object (via `dup2` or inheritance across `fork`).

`fork()` duplicates the fd table — child inherits all of parent's open files. `exec()` closes fds marked `FD_CLOEXEC` (`O_CLOEXEC` flag); the rest persist across exec.

### Signal Handlers, Threads, etc.

The task_struct also tracks:

- **Signal disposition table**: per-signal handler or `SIG_DFL`/`SIG_IGN`
- **Thread group** (`tgid`): threads share mm_struct and fd table, but each has its own stack and register state
- **Namespace memberships**: mount, pid, net, user namespaces — what the process can see
- **Credentials**: uid/gid, capabilities — what the process is allowed to do
- **rlimits**: resource limits (max stack size, max open fds, max memory)

---

## 6. The Full Picture End-to-End

```
execve("./program", argv, envp)
         │
         ▼
   kernel: binfmt_elf
         │
         ├─ read ELF header, validate
         ├─ mmap PT_LOAD segments (file-backed VMAs)
         ├─ find PT_INTERP → mmap ld.so
         ├─ build stack: argc, argv, envp, auxv
         └─ set RIP=ld.so entry, RSP=stack top
                  │
                  ▼
             ld.so runs
                  │
                  ├─ read DT_NEEDED → mmap libc.so, etc.
                  ├─ apply GOT/PLT relocations
                  ├─ run .init_array constructors
                  └─ jump to _start
                           │
                           ▼
                       _start (crt1.o)
                           │
                           └─ __libc_start_main()
                                    │
                                    ├─ heap init (brk)
                                    ├─ stdio init
                                    ├─ call main(argc, argv, envp)
                                    │        │
                                    │        ▼
                                    │    your code runs
                                    │    malloc → ptmalloc → brk/mmap
                                    │    open()  → fd table entry
                                    │    read()  → file object offset
                                    │    mmap()  → new VMA
                                    │
                                    └─ exit(ret) → _exit syscall
                                              │
                                              ▼
                                    kernel cleans up:
                                    - unmap all VMAs
                                    - close all fds
                                    - notify parent (SIGCHLD)
```

---

## 7. Where to Go From Here

This overview covers the main concepts. Each node is its own deep topic:

| Layer | Go deeper with |
|---|---|
| ELF format | `man 5 elf`, `readelf -a`, `objdump -p` on real binaries |
| Kernel loading | Linux `fs/binfmt_elf.c` source |
| Virtual memory | `mmap(2)`, `brk(2)`, `/proc/pid/maps`, `/proc/pid/smaps` |
| Dynamic linking | `man ld.so`, `LD_DEBUG=all ./program` |
| Heap internals | glibc malloc source, `mallinfo()` |
| File descriptors | `man 2 open`, `lsof -p <pid>` |
| Process state | `/proc/<pid>/` — a live window into task_struct |

The key insight to carry forward: **the kernel is lazy by design**. It doesn't copy the binary into RAM upfront — it maps it. It doesn't allocate heap pages until they're touched. Everything is demand-driven, with the page fault handler as the universal backstop. The process's visible address space is largely a fiction maintained by the MMU, with the kernel filling in the blanks on demand.
