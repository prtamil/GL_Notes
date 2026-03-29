# Why Stack Allocation Is Fast and Heap Allocation Is Slow

---

## 1. The Core Insight

Stack allocation is fast because it is **not really allocation at all**. It is arithmetic on one register.
Heap allocation is slow because it is **resource management** — finding, tracking, and sometimes requesting memory from the OS.

To understand why, you have to trace what actually happens at each layer: the ELF loader, the kernel, and the processor.

---

## 2. Where the Stack Comes From

When the kernel loads your ELF binary (via `execve` → `binfmt_elf`), it does not read any stack information from the ELF file. The stack is not a segment in the binary. It is created fresh by the kernel for every new process, unconditionally.

The kernel calls `mmap` with `MAP_ANONYMOUS | MAP_PRIVATE` to reserve a virtual address region — typically 8 MB. It writes `argc`, `argv`, `envp`, and the auxiliary vector at the top of that region, sets the CPU's `RSP` register to point just below that data, and jumps to the entry point.

At this moment the stack VMA exists in the kernel's `mm_struct`, but most of its pages have **no physical backing yet**. The kernel set up the mapping; it did not touch the memory.

```
Kernel after execve:
  VMA [stack]: 0x7fff_f000_0000 → 0x7fff_ffff_ffff   MAP_ANON, GROWS_DOWN
  Physical pages: only the top few pages (for argc/argv) are actually mapped.
  RSP = 0x7fff_ffff_f020  (just below argv data)
```

The stack guard page (one unmapped page just below the VMA) is also set up here. If the stack grows into it, the CPU raises a segfault — that is your stack overflow.

---

## 3. Where the Heap Comes From

The heap does not exist at all when the process starts. There is no heap VMA after `execve`. It is created on first use.

When `__libc_start_main` runs (before `main`), the C runtime calls `brk(0)` to ask the kernel: *where does the heap start?* The kernel returns the address just above the last `PT_LOAD` segment of the ELF binary. This address is called the **program break**. Nothing is allocated yet — the kernel just told you where the heap would begin if you ever ask for it.

The heap VMA is created the first time `malloc` calls `brk(new_address)` or `mmap(MAP_ANONYMOUS)` to actually request pages.

---

## 4. Stack Allocation at the Processor Level

When your function is called, the processor executes a **prologue**:

```asm
push   rbp            ; save caller's frame pointer (1 store)
mov    rbp, rsp       ; set our frame pointer
sub    rsp, 0x50      ; allocate 80 bytes for locals
```

The `sub rsp, 0x50` line **is** the allocation. That is it. One instruction. The CPU decrements the stack pointer register by 80. The memory at the new `RSP` is now logically "allocated" for your local variables.

No function call. No lock. No search. No list traversal. One arithmetic instruction on one register that already lives in the CPU's register file.

**Deallocation is equally trivial:**

```asm
mov    rsp, rbp       ; restore stack pointer (discard entire frame)
pop    rbp            ; restore caller's frame pointer
ret                   ; return
```

The `mov rsp, rbp` discards every local variable in the frame instantaneously. The CPU does not zero the memory, does not update any data structure, does not notify the OS. It just moves a number in a register.

### Why Are Those Pages Already in Cache?

When you are deep in a call chain, your stack frames are clustered in a small address range — a few kilobytes. That region has been touched repeatedly and almost certainly lives in **L1 cache** (32–64 KB, ~4 cycle latency). Every local variable access is a cache hit.

The stack also has perfect **spatial locality**: variables in the same frame are adjacent bytes. A single 64-byte cache line often covers multiple locals at once. Hardware prefetchers recognize the linear access pattern and pull cache lines in automatically.

---

## 5. The Page Fault Path (Why Stack Is Still Fast on First Touch)

Even when a stack page is touched for the first time — a new cache line that has never been accessed — the path is short.

The CPU raises a **page fault** (hardware interrupt). The kernel's fault handler (`do_page_fault` → `handle_mm_fault`) looks up the VMA for that address. It finds the anonymous stack VMA, allocates a physical page, zeroes it (security requirement — you must not see another process's data), installs it in the page table, and returns. The faulting instruction is replayed.

This happens at most once per 4 KB page. After that, the page is in the page table and subsequent accesses are direct hardware memory translations — no kernel involvement.

The stack grows into new pages **sequentially and predictably** as call depth increases. The kernel even has a **stack growth heuristic**: if a fault occurs just below the current stack bottom (within a threshold), it automatically expands the stack VMA downward. You never explicitly ask for more stack; it just happens.

---

## 6. Heap Allocation at the Processor Level

`malloc(80)` does not subtract from a register. It calls into the C library's heap allocator (glibc's **ptmalloc**, or jemalloc, tcmalloc in other runtimes). Here is what that involves:

### The Free List Search

ptmalloc organizes free memory into **bins** — linked lists of free chunks grouped by size range. For a small allocation like 80 bytes, it searches the corresponding bin:

```
malloc(80):
  1. round up to next chunk size (96 bytes with header)
  2. look in the fastbin for size 96
  3. if empty, look in the smallbin for size 96
  4. if empty, carve from the top chunk (wilderness)
  5. if top chunk too small, call brk() or mmap() → kernel
  6. write chunk header (size, flags) at the start of the returned block
  7. return pointer past the header
```

Steps 2–4 involve pointer chasing through linked lists — memory accesses that are likely **cache misses** because the allocator's metadata is scattered across the heap, not co-located with your hot code.

### The Chunk Header

Every `malloc`'d block has a hidden header (8–16 bytes) just before the pointer you receive. It stores the chunk size and status bits. `free()` reads this header to know how large the block is and whether adjacent chunks can be coalesced (merged). This metadata is invisible to your code but costs memory and causes cache pressure.

### Thread Contention

ptmalloc uses **arenas** — per-thread heap regions with a mutex. In a multithreaded program, two threads calling `malloc` simultaneously must serialize on that mutex. The stack has no such contention: each thread has its own stack, and `RSP` is a per-CPU register. No synchronization, ever.

---

## 7. When malloc Calls the Kernel (The Slow Path)

When the allocator has no free chunk that fits, it must ask the OS for more memory. It calls either:

- **`brk(new_break)`**: extends the heap VMA upward by moving the program break. The kernel validates the new address, extends the VMA in `mm_struct`, and returns. New pages are not allocated yet — they will fault in on first access.
- **`mmap(MAP_ANONYMOUS)`**: for large allocations (> ~128 KB in glibc), creates a brand new anonymous VMA. This is an entirely separate region from the heap, returned directly to the OS via `munmap` when `free`'d.

Either path crosses the **user/kernel boundary** — a context switch, privilege level change (ring 3 → ring 0), TLB interaction, and return. Even a fast syscall (`syscall` instruction) costs hundreds of nanoseconds. Most `malloc` calls avoid this via the free list, but every program eventually hits it.

---

## 8. The TLB Dimension

The CPU's **TLB** (Translation Lookaside Buffer) caches virtual→physical page mappings so the hardware page table walker is not invoked on every memory access. A typical L1 TLB holds 64 entries — 64 × 4 KB = 256 KB of address space with fast translation.

The stack wins here too:
- Stack frames cluster in a tight address range. A handful of TLB entries cover the entire active stack.
- Those entries stay hot across function calls because the same pages are reused repeatedly.

The heap loses:
- Long-lived programs accumulate fragmented allocations across many pages scattered through the heap address range.
- Accessing an old allocation after working elsewhere may cause a **TLB miss**, requiring a page table walk (several memory accesses across potentially cache-cold page table pages).

---

## 9. Lifetime and Discipline

There is a non-hardware reason the stack is fast: **its discipline makes it predictable**.

Stack memory has a rigid LIFO lifetime. A frame is allocated when a function is called and freed when it returns. The compiler knows this statically — it computes the exact frame size at compile time and emits a single `sub rsp, N` instruction. No runtime decision is made.

Heap memory has **arbitrary lifetime**. The caller decides when to `free`, and that decision may happen in a different function, thread, or module. The allocator cannot predict it. It must track every live allocation, maintain metadata, and handle `free` in any order — which is exactly the work that makes it expensive.

The stack's discipline is its performance contract.

---

## 10. Summary: The Cost Model

| Operation | Stack | Heap |
|---|---|---|
| Allocate | 1 instruction (`sub rsp, N`) | ~10–100s of instructions (free list search) |
| Free | 1 instruction (`mov rsp, rbp`) | ~10–100s of instructions (coalesce, relink) |
| Kernel involvement | Once per 4 KB page (page fault, amortized) | Occasionally (`brk`/`mmap` on exhaustion) |
| Cache behavior | Hot — tight address range, high reuse | Cold — scattered, metadata thrash |
| TLB pressure | Minimal — few active pages | Higher — many scattered pages |
| Thread safety | Free — per-CPU register | Costs — mutex or per-thread arena |
| Metadata overhead | None | 8–16 bytes per allocation |
| Lifetime tracking | None — compiler handles it statically | Full — allocator tracks every live block |

The stack is fast because the compiler does all the work at compile time and the CPU does the rest in a single instruction. The heap is slower because the runtime must do real work — search, track, synchronize, and occasionally ask the kernel — every single time.

---

## 11. The Practical Takeaway

Use the stack for anything with a known, bounded size and a lexical lifetime. Use the heap when you need:
- Size unknown at compile time
- Lifetime that outlives the creating function
- Data shared across threads or modules

The performance difference matters most in hot loops. A `malloc` in a tight loop is a red flag — each call may miss cache, acquire locks, and periodically block on a syscall. A stack variable in the same loop is free after the first page fault.

Understanding this distinction at the instruction and kernel level gives you the intuition to read a hot path and immediately see where memory pressure comes from — before you even profile it.
