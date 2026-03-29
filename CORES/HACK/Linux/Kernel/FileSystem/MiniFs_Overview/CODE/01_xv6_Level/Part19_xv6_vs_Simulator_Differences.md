# Part 19 — xv6 vs Simulator Differences

---

## Why This Comparison Matters

The simulator is described as "xv6-faithful", but it is not identical to xv6. Understanding the differences tells you what the simulator prioritizes (clarity, observability, single-threaded correctness) and what it omits (concurrency, hardware interfaces, process isolation). This lets you read real xv6 source without being surprised.

---

## What the Simulator Implements Faithfully

These are exact algorithmic correspondences:

| Concept | xv6 | Simulator |
|---------|-----|-----------|
| Disk layout | `mkfs.c` block layout | Section 1 constants |
| Superblock fields | `struct superblock` | `Superblock` class (8 fields, 32 bytes) |
| Log protocol | `begin_op/end_op/commit` | `Log.begin_op/end_op/_commit` |
| Buffer cache semantics | `bread/bwrite/brelse/bpin` | `BufferCache.bread/bwrite/brelse/bpin` |
| Bitmap allocation | `balloc/bfree` | `_bitmap_alloc/_bitmap_free` |
| dinode format | `struct dinode` | `DINODE_FMT = "HHIII"` (16 bytes) |
| Inode cache | `struct inode` icache | `Inode` + `_icache` dict |
| `iget/iput/ialloc/iupdate` | `kernel/fs.c` | same names, same semantics |
| `bmap/itrunc` | `kernel/fs.c` | `_bmap/_itrunc` |
| `readi/writei` | `kernel/fs.c` | same names |
| `dirlookup/dirlink` | `kernel/fs.c` | same names |
| `namei/nameiparent/_namex` | `kernel/fs.c` | same names |
| `struct dirent` | `ushort inum + char[14]` | `DIRENT_FMT = "H14s"` (16 bytes) |
| Hard link contract | `nlink + ref` | `nlink + ref` |
| Deferred free | `iput` checks both | `iput` checks both |

---

## Disk Layout: Simulator vs xv6 Comment Errors

The simulator's own file header and some inline comments describe an older layout with `LOGSIZE=4`. The **actual computed values** from lines 252–257 of the code are:

```python
LOGSTART      = 2
LOGSIZE       = 8        # 8 log data blocks
INODE_START   = 11       # = LOGSTART + 1 + LOGSIZE = 2+1+8
BMAP_START    = 19       # = INODE_START + 8
DATA_START    = 20
```

Run `fs.sbdump()` or `fs.mkfs()` to see the real layout. The printed output is authoritative:
```
Log        at blocks 2–10
Inodes     at blocks 11–18  (32 inodes, 4 per block)
Bitmap     at block  19
Data       at blocks 20–255  (236 blocks)
```

---

## Differences: Concurrency and Locking

**xv6**: Every shared data structure is protected by a `spinlock` or `sleeplock`. The buffer cache uses `bcache.lock`. Each inode has its own `sleeplock`. The log has `log.lock`.

**Simulator**: Single-threaded Python. No locks. No concurrent access.

**Implication**: The simulator demonstrates the correct *sequence* of operations but not the correct *synchronization*. For studying one operation at a time, this simplification is harmless.

---

## Differences: Buffer Cache Eviction

**xv6**: Fixed-size doubly-linked LRU list of `NBUF=30` entries. When all slots are in use and a new block is needed, the LRU unpinned buffer is evicted. Hitting the limit causes `bread()` to panic.

**Simulator**: Python dict that grows without bound. `NBUF = 30` is defined but not enforced. No eviction occurs.

**Implication**: Cache miss rates in the simulator are lower than on a real bounded cache.

---

## Differences: Direct Block Pointers

**xv6 (RISC-V)**: `NDIRECT = 12` direct block pointers per inode. Max file size ≈ 269 KB with 1 KB blocks.

**Simulator**: `NDIRECT = 1`. One direct block pointer. Max file size = `(1 + 16) × 64 = 1088 bytes`.

This is a deliberate simplification — with 64-byte blocks, 12 direct pointers would only add 768 bytes over 1 pointer. The indirect mechanism is the interesting part and works identically regardless of `NDIRECT`.

---

## Differences: Log Size

**xv6**: `LOGSIZE = 30`, `MAXOPBLOCKS = 10`. Supports up to 10 blocks per transaction, 30 log data blocks total.

**Simulator**: `LOGSIZE = 8`, `MAXOPBLOCKS = 8`. Sized for the 256-block filesystem.

---

## Differences: File Descriptor Table

**xv6**: Two-level structure: global `ftable` (array of `NFILE=100 struct file`) + per-process `ofile[NOFILE]` array. `dup()` makes two fds point to the **same** `struct file` (shared offset). `fork()` duplicates the `ofile` array.

**Simulator**: Single `FDTable` dict. `dup()` creates an independent entry with its own offset (starts at 0). No `fork()` or process model. `NFILE = 20`.

---

## Differences: Physical Disk

**xv6**: Uses `virtio_disk.c` to talk to a RISC-V virtio block device. Geometry is hidden inside QEMU.

**Simulator**: Adds `PhysicalPlatter` + `DiskController` + `lba_to_chs` as an educational extension not present in xv6. This is the simulator's main *addition*, not a simplification.

---

## Differences: Path Resolution

**xv6**: `namex()` supports both absolute and relative paths (relative to current process's `cwd`).

**Simulator**: Only absolute paths. Relative paths raise `ValueError`. No process model, no `cwd`.

---

## Summary Table

| Feature | xv6 | Simulator |
|---------|-----|-----------|
| Concurrency | spinlocks + sleeplocks | none |
| Buffer eviction | LRU, NBUF=30 enforced | unbounded dict |
| NDIRECT | 12 | 1 |
| LOGSIZE | 30 | 8 |
| NFILE | 100 | 20 |
| FD sharing via fork | yes | no (no process model) |
| Relative paths | yes | no |
| Physical disk model | hidden (virtio) | exposed (CHS + iolog) |
| Block size | 1024 bytes | 64 bytes |
| Data start | varies | block 20 |
| Max file size | ~8 MB | 1088 bytes |

The simulator is faithful to the algorithm. The differences are in scale, concurrency, and process model — exactly the things that make real xv6 harder to read than the simulator.
