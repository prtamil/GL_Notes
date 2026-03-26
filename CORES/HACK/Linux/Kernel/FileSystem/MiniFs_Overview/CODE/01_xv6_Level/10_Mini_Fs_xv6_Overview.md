# Understanding a Complete xv6-Faithful UNIX Filesystem

### A Deep Technical Essay on `mini_unix_fs_xv6.py`

---

> _"The best way to understand a system is to build one. The best way to build one is to study one that already works."_ — The xv6 philosophy

---

## Table of Contents

1. [What Is xv6, and Why Does It Matter?](https://claude.ai/chat/9064ec55-8826-41d5-8ca1-c6c8917f51a5#1-what-is-xv6-and-why-does-it-matter)
2. [The Complete Stack in One Diagram](https://claude.ai/chat/9064ec55-8826-41d5-8ca1-c6c8917f51a5#2-the-complete-stack-in-one-diagram)
3. [Disk Layout — How Every Byte Is Organised](https://claude.ai/chat/9064ec55-8826-41d5-8ca1-c6c8917f51a5#3-disk-layout--how-every-byte-is-organised)
4. [Section 0 — Physical Hardware (Platter, Controller, LBA)](https://claude.ai/chat/9064ec55-8826-41d5-8ca1-c6c8917f51a5#4-section-0--physical-hardware)
5. [Section 2B — Buffer Cache: bread / bwrite / brelse](https://claude.ai/chat/9064ec55-8826-41d5-8ca1-c6c8917f51a5#5-section-2b--buffer-cache-bread--bwrite--brelse)
6. [Section 2C — The Log Layer: Crash Safety via WAL](https://claude.ai/chat/9064ec55-8826-41d5-8ca1-c6c8917f51a5#6-section-2c--the-log-layer-crash-safety-via-wal)
7. [Section 3 — Superblock on Disk](https://claude.ai/chat/9064ec55-8826-41d5-8ca1-c6c8917f51a5#7-section-3--superblock-on-disk)
8. [Section 3B — Block Bitmap Allocator: balloc / bfree](https://claude.ai/chat/9064ec55-8826-41d5-8ca1-c6c8917f51a5#8-section-3b--block-bitmap-allocator-balloc--bfree)
9. [Section 4 — Inode Layer: iget / iput / ialloc / bmap / readi / writei](https://claude.ai/chat/9064ec55-8826-41d5-8ca1-c6c8917f51a5#9-section-4--inode-layer)
10. [Section 5 — Directory Layer: dirlookup / dirlink](https://claude.ai/chat/9064ec55-8826-41d5-8ca1-c6c8917f51a5#10-section-5--directory-layer)
11. [Section 6 — Path Lookup: namei / nameiparent](https://claude.ai/chat/9064ec55-8826-41d5-8ca1-c6c8917f51a5#11-section-6--path-lookup-namei--nameiparent)
12. [Section 7 — Filesystem Operations: create / unlink / link](https://claude.ai/chat/9064ec55-8826-41d5-8ca1-c6c8917f51a5#12-section-7--filesystem-operations)
13. [Section 8 — File Descriptor Table: open / read / write / close](https://claude.ai/chat/9064ec55-8826-41d5-8ca1-c6c8917f51a5#13-section-8--file-descriptor-table)
14. [A Complete Transaction Walk-Through](https://claude.ai/chat/9064ec55-8826-41d5-8ca1-c6c8917f51a5#14-a-complete-transaction-walk-through)
15. [The Log and Crash Recovery](https://claude.ai/chat/9064ec55-8826-41d5-8ca1-c6c8917f51a5#15-the-log-and-crash-recovery)
16. [Indirect Blocks: How Large Files Work](https://claude.ai/chat/9064ec55-8826-41d5-8ca1-c6c8917f51a5#16-indirect-blocks-how-large-files-work)
17. [The Deferred-Free Contract: Unlink + Open Fds](https://claude.ai/chat/9064ec55-8826-41d5-8ca1-c6c8917f51a5#17-the-deferred-free-contract-unlink--open-fds)
18. [xv6 Source Correspondence Table](https://claude.ai/chat/9064ec55-8826-41d5-8ca1-c6c8917f51a5#18-xv6-source-correspondence-table)
19. [What Real xv6 Has That We Omit](https://claude.ai/chat/9064ec55-8826-41d5-8ca1-c6c8917f51a5#19-what-real-xv6-has-that-we-omit)
20. [Exploring the Simulator: Shell Commands Reference](https://claude.ai/chat/9064ec55-8826-41d5-8ca1-c6c8917f51a5#20-exploring-the-simulator-shell-commands-reference)
21. [Closing Thoughts](https://claude.ai/chat/9064ec55-8826-41d5-8ca1-c6c8917f51a5#21-closing-thoughts)

---

## 1. What Is xv6, and Why Does It Matter?

xv6 is a small, clean reimplementation of UNIX Sixth Edition (V6), written by professors at MIT for the operating systems course 6.828. The source code is around 10,000 lines of C and assembly. It boots, runs programs, handles system calls, and manages a real filesystem on real hardware (RISC-V or x86). Its filesystem is roughly 900 lines of C.

Why does it matter? Because it is the smallest complete UNIX filesystem that exists. Every real-world filesystem — ext4, btrfs, ZFS, NTFS, APFS — is a vastly more complex version of the same ideas xv6 expresses cleanly. Study xv6's filesystem and you have the mental model to understand all of them.

`mini_unix_fs_xv6.py` is a faithful Python reimplementation of xv6's filesystem, extended with the physical disk simulation from earlier versions. It is designed so that every line of Python code maps directly to a corresponding piece of xv6 C code. The simulator runs in user space — no OS calls, no real disk I/O — but the design is exact.

**xv6 filesystem source files and their Python equivalents:**

|xv6 file|Python section|What it does|
|---|---|---|
|`kernel/virtio_disk.c`|Section 2|Raw disk I/O driver|
|`kernel/bio.c`|Section 2B|Buffer cache (bread/bwrite/brelse)|
|`kernel/log.c`|Section 2C|Write-ahead log (begin_op/end_op/commit)|
|`kernel/fs.c`|Sections 3–6|Superblock, bitmap, inodes, directories, paths|
|`kernel/file.c`|Section 8|File descriptor table|
|`kernel/sysfile.c`|Section 7|System call implementations (open, link, unlink)|
|`mkfs/mkfs.c`|`FileSystem.mkfs()`|Disk formatter|

---

## 2. The Complete Stack in One Diagram

```
User types:  write /home/alice/notes.txt  "Hello"
                │
                ▼
  ┌──────────────────────────────────────────────────────────┐
  │  Section 7 — FileSystem.write_file()                     │
  │  begin_op() → namei() → itrunc() → writei() → end_op()  │
  ├──────────────────────────────────────────────────────────┤
  │  Section 6 — namei() / nameiparent()                     │
  │  "/home/alice/notes.txt" → inode 4                       │
  ├──────────────────────────────────────────────────────────┤
  │  Section 5 — dirlookup() / dirlink()                     │
  │  read dir blocks, scan 16-byte dirents for name          │
  ├──────────────────────────────────────────────────────────┤
  │  Section 4 — Inode layer                                 │
  │  iget(4) → Inode{type=FILE,nlink=1,size=0,addrs=[0]}    │
  │  _bmap(ip,0) → balloc() → data block 19                 │
  │  writei(ip,0,"Hello") → writes to block 19              │
  │  _iupdate(ip) → serialise inode 4 to disk block 7       │
  ├──────────────────────────────────────────────────────────┤
  │  Section 3B — _bitmap_alloc()                            │
  │  Read block 15 (bitmap), find free bit, set it           │
  │  log_write(15) — bitmap change is logged                 │
  ├──────────────────────────────────────────────────────────┤
  │  Section 2C — Log layer                                  │
  │  log_write(19) — data block 19 logged                    │
  │  log_write(7)  — inode block 7 logged                    │
  │  end_op(): commit → write log data → write log header    │
  │                   → install (copy to home locations)     │
  │                   → clear log header                     │
  ├──────────────────────────────────────────────────────────┤
  │  Section 2B — Buffer Cache (bcache)                      │
  │  disk_read/write → bcache.bread/bwrite                   │
  │  bflush() during commit calls _raw_write                 │
  ├──────────────────────────────────────────────────────────┤
  │  Section 2 — Raw I/O → DiskController.write(lba, data)  │
  │  lba_to_chs(19) = (C=0, H=2, S=3)                       │
  ├──────────────────────────────────────────────────────────┤
  │  Section 0A — PhysicalPlatter.write_sector(0, 2, 3)      │
  │  _storage[(0,2,3)] = b"Hello\x00..."                     │
  └──────────────────────────────────────────────────────────┘
```

Every layer does exactly one job. Every layer talks only to the layer directly below it. The filesystem layer (`writei`) never knows it is writing to a cylinder — it only knows block numbers. The controller never knows about filenames — it only knows LBA addresses.

---

## 3. Disk Layout — How Every Byte Is Organised

The disk is 256 blocks of 64 bytes each. The layout mirrors xv6's `mkfs` output:

```
Block  0      : Boot block      (unused, reserved for boot loader)
Block  1      : Superblock      (magic, geometry, region start addresses)
Block  2      : Log header      (struct logheader: n + block_nos[LOGSIZE])
Blocks 3–10   : Log data        (LOGSIZE=8 shadow copies of modified blocks)
Blocks 7–14   : Inode table     (IPB=4 inodes per block, NINODES=32 → 8 blocks)
Block  15     : Block bitmap    (1 bit per block — 0=free, 1=allocated)
Blocks 16–255 : Data blocks     (240 usable data blocks)
```

This layout was carefully chosen:

- **Boot block (0):** The BIOS or bootloader reads from here. The OS itself ignores it.
- **Superblock (1):** Fixed location so the kernel always knows where to find it on mount.
- **Log (2–10):** Adjacent to the superblock so recovery is a sequential read/write.
- **Inode table (7–14):** Right after the log. Multiple inodes per block (IPB=4) means small directories cost only one block read to list all nearby inodes.
- **Bitmap (15):** One block of bits covering the entire 256-block disk (256 bits = 32 bytes — fits easily in 64 bytes). Single-block bitmap means alloc/free never spans blocks.
- **Data (16–255):** Everything after the metadata regions.

You can inspect this layout with `explain N` in the shell for any block number, or `sb` to read the superblock.

---

## 4. Section 0 — Physical Hardware

The hardware simulation is unchanged from v2/v3: a `PhysicalPlatter` object with a `(cylinder, head, sector)` dict, a `DiskController` that translates LBA to CHS, and `lba_to_chs` / `chs_to_lba` geometry functions.

In the xv6 version, the only function the filesystem ever calls is `disk_read(blockno)` and `disk_write(blockno, data)` — which go through the buffer cache, which calls `_raw_read/_raw_write`, which call the controller. The platter is entirely hidden behind these two public functions.

This corresponds exactly to how xv6's `virtio_disk.c` provides `virtio_disk_rw(buf, write)` to the rest of the kernel, and the kernel never sees the actual disk hardware directly.

---

## 5. Section 2B — Buffer Cache: bread / bwrite / brelse

```python
class BufEntry:
    __slots__ = ('data', 'dirty', 'refcnt', 'valid')
    def __init__(self, data):
        self.data   = bytearray(data)
        self.dirty  = False
        self.refcnt = 1
        self.valid  = True
```

The buffer cache (bcache) is xv6's most important performance structure. It lives in `kernel/bio.c`. Every block read and write in the kernel goes through it.

### The Three Core Operations

**`bread(blockno)`** — the buffer read. Returns a `bytearray` copy of the block. Increments `refcnt` so the buffer won't be evicted. If the block is already in cache, this is a pure in-memory operation — zero disk I/O. On a miss, calls `_raw_read` to fetch from the platter.

**`bwrite(blockno, data)`** — stores data in cache, marks the entry `dirty=True`. No disk write happens. The log layer controls when dirty blocks actually reach the disk.

**`brelse(blockno)`** — release: decrement `refcnt`. This signals that the caller is done with the buffer. In xv6, a buffer with `refcnt == 0` is eligible for eviction when the cache is full.

### Reference Counting

In xv6, every `bread` must be paired with a `brelse`. This is the buffer cache's equivalent of `malloc/free` or `iget/iput`. If you call `bread` five times without `brelse`, the buffer's `refcnt` is 5 and it cannot be evicted.

In our simulator, `iget` calls `bread` on the inode block and then calls `bcache.brelse(blk)` immediately after deserialising, because the inode data has been copied into the `Inode` object in `_icache`. The buffer is no longer needed.

### Why the Cache Exists

Without the cache, every `dirlookup` scan reads the directory's data block from the platter on each call. In a path like `/home/alice/notes.txt`, `home`, `alice`, and `notes.txt` require three directory lookups, each potentially reading the same parent-directory blocks. With the cache, the second lookup of the same block is a dict lookup — nanoseconds instead of milliseconds.

After `mkfs` writes all metadata, the demo shows `hits=156, misses=0` for subsequent operations. Every single read is served from cache. This is the real-world impact of the buffer cache: it turns a mostly-disk-bound system into a mostly-RAM-bound system.

---

## 6. Section 2C — The Log Layer: Crash Safety via WAL

The log layer is xv6's crash safety mechanism. It lives in `kernel/log.c` and implements Write-Ahead Logging (WAL) — the same technique used by PostgreSQL, SQLite, ext4, and virtually every production filesystem and database.

### The Problem It Solves

Consider `mkdir /home`. This operation must:

1. Allocate an inode (write inode block)
2. Allocate a data block for the directory's entries (write bitmap block)
3. Write `.` and `..` entries (write directory's data block)
4. Add the entry to `/`'s directory (write `/`'s data block)

If power fails after step 2 but before step 4, the disk is inconsistent: a data block has been allocated (bitmap says "in use") but nothing points to it — it is permanently lost space. Worse, if `/`'s directory block was partially written, the filesystem is corrupt.

The log solves this by making all changes to a transaction atomic.

### The Three Phases of a Transaction

**Phase 1: `begin_op()`** Signals the start of a filesystem operation. Multiple `begin_op()` calls can be active simultaneously (group commit). Our simulator uses `outstanding` to track this.

**Phase 2: `log_write(blockno)`** Each modified block is registered with the log. Instead of writing directly to its home location, the block's buffer is pinned in cache (via `bpin`) and noted in `pending_writes`. The in-memory data is correct — it is the on-disk persistence that is deferred.

**Phase 3: `end_op()` → `commit()`** When `outstanding` drops to 0, `commit()` runs:

```python
def _commit(self):
    # 1. Write each modified block's current data to a log data block
    for i, blockno in enumerate(blocks):
        log_block = LOGSTART + 1 + i
        data = bcache.bread(blockno)
        _raw_write(log_block, data)   # sequential write to log area

    # 2. Write log header — THE COMMIT POINT
    self._write_log_header(blocks)    # this is atomic (one sector write)

    # 3. Install: copy log blocks to their home locations
    self._install_trans(blocks)

    # 4. Clear log header (transaction done, log can be reused)
    self._write_log_header([])
```

**The commit point** is the moment `_write_log_header(blocks)` writes a non-zero `n` to the log header block. If power fails before this write completes, the log header still shows `n=0` and nothing was committed — recovery ignores it. If power fails after this write, recovery finds `n > 0` and replays the log by running `_install_trans` again.

### Why This Is Crash-Safe

The key insight is that Step 2 (`_write_log_header`) is a **single sector write** to block 2. Disks guarantee that a single sector write is either fully completed or not started — it cannot be partially written. So the commit point is truly atomic.

After the commit point, the changes are safe even if power fails. Recovery will replay them. Before the commit point, nothing has been committed, and the original on-disk state is intact.

### `recover()` — Replay on Reboot

```python
def recover(self):
    raw = _raw_read(LOGSTART)
    n, *block_nos = struct.unpack(LOG_HDR_FMT, raw[:LOG_HDR_SIZE])
    blocks = block_nos[:n]
    if blocks:
        self._install_trans(blocks)   # replay
        self._write_log_header([])    # clear
```

On every mount, `recover()` reads the log header. If `n > 0`, a previous transaction committed but install was interrupted — `_install_trans` replays it. This is called in `fs.mount()` before any filesystem operation.

The demo (Phase 11) simulates this by calling `writei` inside a `begin_op` without calling `end_op`, then calling `recover()`. The recovery replays the most recent committed state, not the incomplete partial write.

---

## 7. Section 3 — Superblock on Disk

```python
class Superblock:
    MAGIC = 0x10203040

    def write_to_disk(self):
        raw = struct.pack(SB_FMT,
            self.magic, self.size, self.nblocks, self.ninodes,
            self.nlog, self.logstart, self.inodestart, self.bmapstart)
        _raw_write(1, buf)

    @classmethod
    def read_from_disk(cls):
        raw  = _raw_read(1)
        vals = struct.unpack(SB_FMT, raw[:SB_SIZE])
        ...
        if sb.magic != cls.MAGIC:
            raise OSError("Bad superblock magic")
        return sb
```

The superblock is a 32-byte structure at disk block 1. It contains everything the kernel needs to locate all other filesystem regions:

- `magic` — sanity check that this is actually our filesystem format
- `size` — total number of blocks
- `nblocks` — number of data blocks
- `ninodes` — total inode capacity
- `logstart`, `nlog` — where the log is and how many blocks it has
- `inodestart` — first inode block
- `bmapstart` — the bitmap block

`mkfs()` writes it once. `mount()` calls `Superblock.read_from_disk()` (mirroring xv6's `readsb()` in `kernel/fs.c`) and validates the magic number. After that, the in-memory `_sb` object is referenced for all region addresses.

The `magic` number serves the same purpose as the first bytes of a PNG or PDF file — it identifies the format. If you write garbage to block 1 and try to mount, the `if sb.magic != cls.MAGIC` check raises immediately rather than silently corrupting memory.

---

## 8. Section 3B — Block Bitmap Allocator: balloc / bfree

```python
def _bitmap_alloc():
    bitmap = bytearray(disk_read(BMAP_START))
    for b in range(DATA_START, TOTAL_BLOCKS):
        byte_idx = b // 8
        bit_idx  = b % 8
        if not (bitmap[byte_idx] & (1 << bit_idx)):
            bitmap[byte_idx] |= (1 << bit_idx)   # mark allocated
            disk_write(BMAP_START, bitmap)
            log.log_write(BMAP_START)             # log the bitmap change
            return b
    raise OSError("No free data blocks!")
```

The block bitmap is a single block (block 15) where each bit represents one disk block: `0` = free, `1` = allocated. With 64 bytes × 8 bits = 512 bits, it covers all 256 blocks with room to spare.

`_bitmap_alloc()` (xv6's `balloc()`) scans from `DATA_START=16` forward, looking for the first zero bit. When found, it sets the bit to 1, writes the bitmap back to cache via `disk_write`, and critically calls `log.log_write(BMAP_START)` — registering the bitmap block as part of the current transaction. Without this, a crash after allocating the bitmap but before writing the inode would leave the allocated bit set permanently (a leaked block).

`_bitmap_free()` (xv6's `bfree()`) clears the bit and calls `bcache.invalidate(b)` to evict any stale cached data for the now-freed block. This prevents a future `bread` from returning the freed block's old data.

The bitmap approach differs from v3's simple free-list stack. The bitmap has two advantages: it survives crashes (it is on disk and logged), and it allows efficient computation of which blocks are free without trusting any in-memory state.

---

## 9. Section 4 — Inode Layer

The inode layer is the heart of the filesystem. It maps inode numbers to metadata and data blocks.

### On-Disk Dinode Layout

```
DINODE_FMT = "HHIII"   — 16 bytes per dinode
  type(2) + nlink(2) + size(4) + addr(4) + indirect(4)
```

With `DINODE_SIZE=16` and `BLOCK_SIZE=64`, four dinodes pack into each disk block (`IPB=4`). Inode block and offset calculations:

```python
def _inode_block(inum):  return INODE_START + (inum - 1) // IPB
def _inode_offset(inum): return ((inum - 1) % IPB) * DINODE_SIZE
```

So inodes 1–4 are in block 7, inodes 5–8 in block 8, and so on. This packing is critical for performance — fetching one inode block brings three other nearby inodes into cache for free.

### iget() and iput() — Reference Counting

```python
def iget(inum):
    if inum in _icache:
        ip = _icache[inum]; ip.ref += 1; return ip
    # load from disk via bcache
    raw = disk_read(_inode_block(inum))
    ip  = _unpack_dinode(inum, raw, _inode_offset(inum))
    ip.ref = 1; _icache[inum] = ip
    return ip

def iput(ip):
    ip.ref -= 1
    if ip.ref == 0 and ip.nlink == 0:
        _itrunc(ip)          # free all data blocks
        ip.type = T_UNUSED
        _iupdate(ip)         # write freed state to disk
        _icache.pop(ip.inum)
```

`iget`/`iput` are xv6's inode reference counting system. Every caller of `iget` must eventually call `iput`. When `ref` reaches 0 **and** `nlink` is also 0, the inode is truly dead: `_itrunc` frees all data blocks (both direct and through the indirect block), the type is set to `T_UNUSED`, and the disk inode is updated.

This two-condition check (`ref==0 AND nlink==0`) is the deferred-free mechanism:

- `nlink` tracks directory references (how many names point here)
- `ref` tracks open file descriptors (how many fds are open)

A file is freed only when **both** reach 0. This is the exact implementation of the UNIX unlink-while-open contract.

### bmap() — Logical Block to Physical Block

```python
def _bmap(ip, bn):
    if bn < NDIRECT:
        if ip.addrs[bn] == 0:
            ip.addrs[bn] = _bitmap_alloc()
            _iupdate(ip)
        return ip.addrs[bn]

    # Indirect
    bn -= NDIRECT
    if ip.indirect == 0:
        ip.indirect = _bitmap_alloc()
        _iupdate(ip)

    ind_data = bytearray(disk_read(ip.indirect))
    addr = struct.unpack_from("I", ind_data, bn * 4)[0]
    if addr == 0:
        addr = _bitmap_alloc()
        struct.pack_into("I", ind_data, bn * 4, addr)
        disk_write(ip.indirect, ind_data)
        log.log_write(ip.indirect)
    return addr
```

`_bmap` (xv6's `bmap()`) translates a logical block number within a file to an actual disk block number. For `bn=0`, it uses the single direct pointer (`ip.addrs[0]`). For `bn >= NDIRECT`, it follows the indirect pointer: reads the indirect block (a whole disk block full of 4-byte addresses), finds the address at position `bn - NDIRECT`, and allocates a new block if it is zero.

This is how files larger than `NDIRECT × BLOCK_SIZE = 64 bytes` work. The indirect block holds `BLOCK_SIZE/4 = 16` additional addresses, allowing files up to `(1 + 16) × 64 = 1,088 bytes` — demonstrated in Phase 10 of the demo with a 160-byte file.

### readi() and writei() — The Core I/O

```python
def readi(ip, offset, n):
    while tot < n:
        logical_bn = (offset + tot) // BLOCK_SIZE
        disk_bn    = _bmap(ip, logical_bn)
        blk_data   = bytearray(disk_read(disk_bn))
        blk_off    = (offset + tot) % BLOCK_SIZE
        to_read    = min(n - tot, BLOCK_SIZE - blk_off)
        result    += blk_data[blk_off: blk_off + to_read]
        tot       += to_read
    return bytes(result)
```

`readi` (xv6's `readi()`) reads `n` bytes from inode `ip` starting at `offset`. It translates byte positions to block numbers via `_bmap`, reads each block through the buffer cache, and slices out the relevant bytes. This correctly handles reads that span multiple blocks and reads that start or end in the middle of a block.

`writei` mirrors `readi` but writes — reading each destination block, modifying the relevant bytes in place, and writing it back via `disk_write` + `log.log_write`.

---

## 10. Section 5 — Directory Layer

```python
DIRSIZ     = 14           # max filename length
DIRENT_FMT = f"H{DIRSIZ}s"   # inum(2) + name(14) = 16 bytes per entry
```

In xv6 (and our simulator), a directory is an inode with `type = T_DIR` whose data blocks contain a flat array of `struct dirent` records. Each record is 16 bytes: a 2-byte inode number and a 14-byte filename. An inode number of 0 means the slot is empty (deleted or never used).

### dirlookup()

```python
def dirlookup(dp, name):
    for off in range(0, dp.size, DIRENT_SIZE):
        raw  = readi(dp, off, DIRENT_SIZE)
        inum, name_bytes = struct.unpack(DIRENT_FMT, raw)
        if inum == 0: continue
        if name_bytes.rstrip(b"\x00").decode() == name:
            return iget(inum), off
    return None, 0
```

`dirlookup` (xv6's `dirlookup()`) scans the directory's data blocks using `readi`, comparing each non-zero dirent's name to the target. On match it returns the inode and byte offset. The offset is used by `unlink` to zero out the entry.

### dirlink()

```python
def dirlink(dp, name, inum):
    # Scan for an empty slot
    for off in range(0, dp.size, DIRENT_SIZE):
        inum_slot, _ = struct.unpack(DIRENT_FMT, readi(dp, off, DIRENT_SIZE))
        if inum_slot == 0:
            break
    else:
        off = dp.size   # append at end

    name_enc = name.encode("ascii")[:DIRSIZ]
    writei(dp, off, struct.pack(DIRENT_FMT, inum, name_enc))
```

`dirlink` (xv6's `dirlink()`) adds a new entry. It first looks for an empty slot (reusing space from deleted entries) before appending. This is important: without slot reuse, a directory that has had many files created and deleted would grow indefinitely.

---

## 11. Section 6 — Path Lookup: namei / nameiparent

```python
def _namex(path, parent):
    ip = iget(INUM_ROOT)   # always start at root

    while True:
        name, rest = _skipelem(path.lstrip("/"))
        if not name:
            if parent: raise ValueError(...)
            return ip, ""

        if parent and not _skipelem(rest)[0]:
            return ip, name   # stop at parent, return leaf name

        if not ip.is_dir():
            iput(ip); raise NotADirectoryError(...)

        next_ip, _ = dirlookup(ip, name)
        iput(ip)
        if next_ip is None:
            raise FileNotFoundError(...)
        ip = next_ip
        path = rest
```

Path resolution is at the heart of every filesystem operation. `namei` (for "name to inode") resolves a full path to its inode. `nameiparent` resolves to the parent directory, returning the leaf name separately.

`_namex` is the shared implementation. `_skipelem` peels off the next `/`-separated component from the path string. The algorithm:

1. Start at the root inode (always inode 1)
2. Peel the next component from the path
3. Look it up in the current directory via `dirlookup`
4. Release the current inode (`iput`), advance to the next
5. Repeat until path is exhausted

For `nameiparent`, the loop stops one step early — when `rest` has no more components — and returns the current directory inode plus the final name component. This is used by `create`, `link`, and `unlink` to find where to add/remove entries.

This algorithm is identical to Linux's `link_path_walk()` and xv6's `namex()`. The tree is implicit — there is no in-memory tree structure. The directory graph is walked on demand, one block read per path component.

---

## 12. Section 7 — Filesystem Operations

Every filesystem operation is wrapped in `begin_op()` / `end_op()` to make it a logged transaction:

```python
def mkdir(self, path):
    log.begin_op()
    try:
        dp, name = nameiparent(path)
        ip = ialloc(T_DIR)
        ip.nlink = 1; _iupdate(ip)
        dirlink(ip, ".",  ip.inum)
        dirlink(ip, "..", dp.inum)
        dirlink(dp, name, ip.inum)
        dp.nlink += 1; _iupdate(dp)
        iput(ip); iput(dp)
    except Exception:
        log.end_op(); raise
    log.end_op()
```

The `try/except` pattern ensures `end_op()` is always called, even on error. In xv6 the equivalent uses `goto bad` patterns in C. The important thing is that a failed operation still closes its transaction (with nothing committed, since no writes were logged).

### `unlink()` — The Full UNIX Deletion Logic

```python
def unlink(self, path):
    log.begin_op()
    dp, name = nameiparent(path)
    ip, off = dirlookup(dp, name)

    if ip.is_dir() and ip.size > 2 * DIRENT_SIZE:
        raise OSError("directory not empty")  # can't rmdir non-empty dir

    # Zero out the directory entry
    writei(dp, off, struct.pack(DIRENT_FMT, 0, b"\x00" * DIRSIZ))
    ip.nlink -= 1; _iupdate(ip)
    iput(ip); iput(dp)
    log.end_op()
    # iput will call _itrunc + free if nlink==0 and ref==0
```

The directory entry is zeroed immediately (the name disappears). `ip.nlink` decrements. The `iput` at the end decrements `ref`. If both reach 0, `iput` calls `_itrunc` — which frees the data blocks and marks the dinode `T_UNUSED` on disk. If a file descriptor is still open, `ref > 0`, so `iput` just decrements and returns; the actual free happens when the last `close()` calls `iput` again.

---

## 13. Section 8 — File Descriptor Table

```python
class FDTable:
    def open(self, path, flags="r"):
        ...
        fd = self._next_fd; self._next_fd += 1
        self._table[fd] = {
            'inum': ip.inum, 'offset': 0,
            'readable': readable, 'writable': writable,
            'ref': 1
        }
        return fd   # ip is kept ref'd until close()
```

The file descriptor table is the process-facing interface. In xv6 it is split between `struct file` (the global `ftable` array, `kernel/file.c`) and the per-process `ofile[]` array (`proc->ofile`, `kernel/proc.h`). In our simulator it is one global dict.

### open() — O_RDONLY / O_WRONLY / O_RDWR / O_CREAT

The `flags` parameter accepts `"r"`, `"w"`, and `"rw"`. If `"w"` is set and the file does not exist, it is created (mirroring `O_CREAT`). The inode ref from `namei`/`ialloc` is held in the fd entry — it will be released by `close()`.

### read() and write() — readi / writei via fd

```python
def read(self, fd, n=None):
    ip   = iget(entry['inum'])
    data = readi(ip, entry['offset'], n)
    entry['offset'] += len(data)
    iput(ip)
    return data.decode(...)

def write(self, fd, data):
    ip = iget(entry['inum'])
    log.begin_op()
    n = writei(ip, entry['offset'], data)
    log.end_op()
    entry['offset'] += n
    iput(ip)
```

`read` calls `readi` (which goes through `_bmap` → buffer cache). `write` wraps `writei` in its own transaction — each `write()` call is one atomic log commit. The offset advances automatically, enabling sequential reads and writes without the caller managing positions.

### dup() — Duplicate a File Descriptor

```python
def dup(self, fd):
    ip = iget(entry['inum'])   # increments inode ref
    new_fd = self._next_fd; self._next_fd += 1
    self._table[new_fd] = dict(entry)
    self._table[new_fd]['offset'] = 0   # independent offset
    iput(ip)
    return new_fd
```

`dup()` mirrors xv6's `sys_dup()`. The new fd refers to the same inode but has an independent offset starting at 0. The inode's ref count increases (via `iget`), so the inode won't be freed until all duplicated fds are closed. This is how pipes and `stdout` redirection work in a shell.

### close() — The Deferred-Free Path

```python
def close(self, fd):
    entry = self._table.pop(fd)
    ip    = iget(entry['inum'])   # bump ref
    iput(ip)   # release fd's reference
    iput(ip)   # release the temporary bump
    # If nlink==0 and ref==0 after these two iputs → _itrunc runs
```

`close()` calls `iput` twice: once to release the fd's held reference, once to release the temporary reference from the `iget` at the top. If `nlink` was already 0 (file was unlinked) and this was the last fd, the second `iput` will find `ref==0` and call `_itrunc`, freeing the inode and all its blocks.

---

## 14. A Complete Transaction Walk-Through

Let us trace `fs.mkdir("/home")` through every layer to see the log in action:

```
fs.mkdir("/home")
  log.begin_op()           → outstanding = 1

  nameiparent("/home")     → returns (root_inode, "home")
    [reads: block 7 (inode table) for root, block 16 (root's dir block)]

  ialloc(T_DIR)            → scans inode table, finds inum=2 free
    [reads: block 7; writes: block 7 (sets type=T_DIR)]
    log.log_write(7)       → pending=[7]

  dirlink(ip, ".", 2)      → writei to new dir's data block
    _bmap(ip, 0)           → _bitmap_alloc() → allocates block 17
    log.log_write(15)      → pending=[7,15] (bitmap block)
    disk_write(17, ...)    
    log.log_write(17)      → pending=[7,15,17] (new dir's data block)

  dirlink(ip, "..", 1)     → appends to block 17
    log.log_write(17)      → already in pending, no-op

  dirlink(root, "home", 2) → writei to root's data block (block 16)
    log.log_write(16)      → pending=[7,15,17,16]

  iput(ip); iput(root)

  log.end_op()             → outstanding = 0 → commit!
    _commit():
      # Write shadow copies to log data blocks
      _raw_write(3, cache[7])   # inode block shadow at log block 3
      _raw_write(4, cache[15])  # bitmap shadow at log block 4
      _raw_write(5, cache[17])  # new dir shadow at log block 5
      _raw_write(6, cache[16])  # root dir shadow at log block 6

      # COMMIT POINT: write log header
      _raw_write(2, {n=4, blocks=[7,15,17,16]})

      # Install: copy log data to home locations
      _raw_write(7,  log[3])    # home: inode block
      _raw_write(15, log[4])    # home: bitmap
      _raw_write(17, log[5])    # home: new directory
      _raw_write(16, log[6])    # home: root directory

      # Clear log header
      _raw_write(2, {n=0})
```

After this commit, the filesystem is fully consistent on disk. The `diskmap` command will show blocks 7, 15, 16, and 17 as written.

---

## 15. The Log and Crash Recovery

Phase 11 of the demo simulates a crash mid-transaction:

```python
log.begin_op()
ip = namei("/crash_test.txt")
writei(ip, 0, b"Partially written")
log.log_write(ip.addrs[0])
# NO end_op() — simulate power failure here
iput(ip)
log.recover()   # replays committed state
```

What happens:

- The partial `writei` only modified the buffer cache — nothing was committed to the log
- `recover()` reads the log header: `n=0` (the last transaction completed normally)
- Recovery does nothing — the previous committed state is intact on disk
- `read_file("/crash_test.txt")` returns the previously written data

This demonstrates the core WAL guarantee: uncommitted transactions are invisible to recovery. Only the commit point matters.

---

## 16. Indirect Blocks: How Large Files Work

With `NDIRECT=1`, a file with only direct blocks can hold just 64 bytes (one block). The indirect block mechanism extends this to `1 + 16 = 17` blocks = 1,088 bytes.

When `writei` calls `_bmap(ip, 1)` (logical block 1 — beyond the one direct block):

```
_bmap(ip, bn=1):
    bn -= NDIRECT   → bn = 0 (first slot in indirect block)
    if ip.indirect == 0:
        ip.indirect = _bitmap_alloc()   # allocate indirect block (say, block 20)
        _iupdate(ip)

    ind_data = disk_read(ip.indirect)   # read block 20 (all zeros initially)
    addr = unpack("I", ind_data, 0)     # = 0 (no block allocated yet)
    if addr == 0:
        addr = _bitmap_alloc()          # allocate data block (say, block 21)
        pack("I", ind_data, 0, addr)    # store 21 at slot 0 of indirect block
        disk_write(20, ind_data)        # write back indirect block
        log.log_write(20)
    return 21   # the actual data block
```

After this, inode 4's `indirect = 20`, and block 20 contains `[21, 0, 0, ...]`. The data is in block 21. The `stat` command shows both:

```
direct blks = [19]   (NDIRECT=1)
indirect    = 20
  direct[0]  LBA=19 → C=0 H=2 S=3
  indirect   LBA=20 → C=0 H=2 S=4
```

---

## 17. The Deferred-Free Contract: Unlink + Open Fds

```
fs.touch("/a.txt")          → inum=4, nlink=1
fs.link("/a.txt", "/b.txt") → inum=4, nlink=2
fd = fd_table.open("/a.txt","r")  → inum=4 ref=2 (1 from icache, 1 from open)

fs.unlink("/a.txt")   → nlink=1, iput: ref still > 0, NOT freed
fs.unlink("/b.txt")   → nlink=0, iput: ref still > 0, NOT freed
                        (file still readable via fd!)

data = fd_table.read(fd)   → readi succeeds, reads from data blocks

fd_table.close(fd)          → iput × 2: ref → 0
                              nlink=0 AND ref=0 → _itrunc() → FREE
```

The key insight: `nlink` and `ref` are separate counters. The file is freed only when the last of both reaches zero. The unlink contract — "a file remains accessible through open file descriptors even after all its names are removed" — is a direct consequence of this two-counter design. It is not a special case; it falls out naturally from the reference counting.

---

## 18. xv6 Source Correspondence Table

|Our Python function|xv6 C function|xv6 source file|
|---|---|---|
|`PhysicalPlatter.read_sector`|hardware disk|`kernel/virtio_disk.c`|
|`DiskController.read/write`|`virtio_disk_rw()`|`kernel/virtio_disk.c`|
|`BufferCache.bread`|`bread()`|`kernel/bio.c`|
|`BufferCache.bwrite`|`bwrite()`|`kernel/bio.c`|
|`BufferCache.brelse`|`brelse()`|`kernel/bio.c`|
|`BufferCache.bpin/bunpin`|`bpin()/bunpin()`|`kernel/bio.c`|
|`Log.begin_op`|`begin_op()`|`kernel/log.c`|
|`Log.log_write`|`log_write()`|`kernel/log.c`|
|`Log.end_op`|`end_op()`|`kernel/log.c`|
|`Log._commit`|`commit()`|`kernel/log.c`|
|`Log.recover`|`recover_from_log()`|`kernel/log.c`|
|`Superblock.read_from_disk`|`readsb()`|`kernel/fs.c`|
|`_bitmap_alloc`|`balloc()`|`kernel/fs.c`|
|`_bitmap_free`|`bfree()`|`kernel/fs.c`|
|`ialloc`|`ialloc()`|`kernel/fs.c`|
|`iget`|`iget()`|`kernel/fs.c`|
|`iput`|`iput()`|`kernel/fs.c`|
|`_iupdate`|`iupdate()`|`kernel/fs.c`|
|`_itrunc`|`itrunc()`|`kernel/fs.c`|
|`_bmap`|`bmap()`|`kernel/fs.c`|
|`readi`|`readi()`|`kernel/fs.c`|
|`writei`|`writei()`|`kernel/fs.c`|
|`dirlookup`|`dirlookup()`|`kernel/fs.c`|
|`dirlink`|`dirlink()`|`kernel/fs.c`|
|`namei`|`namei()`|`kernel/fs.c`|
|`nameiparent`|`nameiparent()`|`kernel/fs.c`|
|`_namex`|`namex()`|`kernel/fs.c`|
|`FileSystem.mkfs`|`mkfs.c`|`mkfs/mkfs.c`|
|`FDTable.open`|`sys_open()` + `filealloc()`|`kernel/sysfile.c` + `kernel/file.c`|
|`FDTable.read`|`fileread()`|`kernel/file.c`|
|`FDTable.write`|`filewrite()`|`kernel/file.c`|
|`FDTable.close`|`fileclose()`|`kernel/file.c`|
|`FDTable.dup`|`sys_dup()`|`kernel/sysfile.c`|
|`FileSystem.mkdir`|`sys_mkdir()`|`kernel/sysfile.c`|
|`FileSystem.link`|`sys_link()`|`kernel/sysfile.c`|
|`FileSystem.unlink`|`sys_unlink()`|`kernel/sysfile.c`|

---

## 19. What Real xv6 Has That We Omit

### Locks

Every buffer in xv6's bcache has a sleeplock (`b.lock`). Every inode has a sleeplock (`ip.lock`). The log has a spinlock. Without locks, two concurrent filesystem operations could corrupt the same data structure. Our simulator is single-threaded.

### LRU Eviction

xv6's bcache uses a doubly-linked list to implement LRU eviction: when the cache is full (NBUF=30 buffers), the least recently used unpinned buffer is recycled for the new block. Our cache is unbounded.

### Group Commit

xv6's `end_op()` implements group commit: if another operation starts while a commit is in progress, it waits and then batches its writes with the next commit. Our `outstanding` counter is correct but we don't implement the sleep/wakeup cycle.

### Device Files

xv6 supports `T_DEVICE` inode type (console, disk) alongside `T_FILE` and `T_DIR`. `writei` and `readi` have special cases that dispatch to device driver read/write functions instead of `_bmap`. We only implement `T_FILE` and `T_DIR`.

### Pipes

xv6 implements pipes as a separate `FD_PIPE` type in `struct file`. A pipe has two fds — one read end, one write end — backed by an in-memory ring buffer rather than an inode. We do not implement pipes.

### Double and Triple Indirect Blocks

Real xv6 has `NDIRECT=12` direct blocks and one indirect block for a maximum of 268 blocks (17,152 bytes with 64-byte blocks). The full xv6 supports MAXFILE = NDIRECT + NINDIRECT = 12 + 256 = 268 blocks. We have NDIRECT=1 and NINDIRECT=16 for MAXFILE=17 blocks (1,088 bytes). The algorithm is identical — just scaled down.

### Permissions and Process Context

xv6 checks that the current process has permission to read/write a file. Our filesystem accepts all operations unconditionally.

---

## 20. Exploring the Simulator: Shell Commands Reference

Run: `python mini_unix_fs_xv6.py` for demo + shell, or `--shell` for shell only.

**Filesystem (all logged via WAL):**

|Command|xv6 syscall|What it does|
|---|---|---|
|`mkdir /path`|`sys_mkdir`|Create directory|
|`touch /path`|`sys_open(O_CREATE)`|Create empty file|
|`write /path text`|`sys_open` + `filewrite`|Write/overwrite file|
|`cat /path`|`fileread`|Read file to screen|
|`link /old /new`|`sys_link`|Hard link|
|`unlink /path`|`sys_unlink`|Remove name|
|`stat /path`|`sys_fstat`|Full inode info + physical address|
|`ls [/path]`|`sys_open` + dirent scan|List directory|
|`df`|—|Filesystem statistics|
|`inodes`|—|Dump inode table from disk|
|`sb`|`readsb`|Read and print superblock|

**File Descriptors:**

|Command|xv6 function|What it shows|
|---|---|---|
|`open /path [r\|w\|rw]`|`sys_open`|Returns fd number|
|`read <fd> [N]`|`fileread`|Read N bytes at current offset|
|`fwrite <fd> text`|`filewrite`|Write at current offset|
|`seek <fd> <off> [w]`|`lseek`|Reposition offset (whence 0/1/2)|
|`dup <fd>`|`sys_dup`|Duplicate fd (independent offset)|
|`close <fd>`|`fileclose`|Close; may trigger deferred free|
|`fds`|—|Show all open fds|

**Storage Layers:**

|Command|What it shows|
|---|---|
|`log`|Log state: pending writes, commit count, on-disk header|
|`cache`|Buffer cache: refcounts, dirty flags, hex previews|
|`sync`|Flush all dirty blocks to platter|
|`explain <N>`|Full block decode: role + LBA + CHS + cache + hex|
|`lba <N>`|Quick LBA→CHS + role|
|`diskmap`|Visual grid of written vs empty sectors|
|`iolog [N]`|Last N physical I/O operations with CHS|
|`geometry`|Physical platter spec|

---

## 21. Closing Thoughts

`mini_unix_fs_xv6.py` implements, in ~2,000 lines of readable Python, the complete set of algorithms that xv6 implements in ~900 lines of C:

- **Write-ahead logging** makes filesystem mutations crash-safe. Every operation is a transaction. The commit point is one sector write. Recovery is deterministic.
- **Buffer cache with reference counting** makes repeated block reads nearly free and ensures that modified blocks are flushed in a controlled order.
- **Bitmap block allocation** tracks free blocks on disk, survives crashes, and allows `balloc`/`bfree` to work correctly within logged transactions.
- **Inode packing** (multiple inodes per block) amortises block reads across nearby file metadata accesses.
- **Indirect blocks** extend file capacity beyond what direct pointers alone allow, using exactly the same `_bmap` function as direct blocks.
- **`iget`/`iput` reference counting** plus `nlink` counting together implement the UNIX unlink contract: an open file survives deletion of its last name, because `ref > 0` prevents `_itrunc` until the last `close()`.
- **`namei`/`nameiparent`** resolve paths without any in-memory tree structure — the tree is reconstructed on demand by reading directory blocks.

The clearest way to use this simulator as a learning tool:

1. `explain 1` — read the raw superblock bytes and see them decoded
2. `explain 7` — see four packed inodes in one block
3. `explain 15` — see the bitmap block and which bits are set
4. `mkdir /test` then `log` — see the pending writes before commit
5. `touch /test/a.txt` then `open /test/a.txt w` then `fwrite 3 hello` then `close 3` — trace one file write through every layer
6. `open /test/a.txt r` then `unlink /test/a.txt` then `read 3` then `close 3` — watch the deferred-free path

After this, open xv6's source at `kernel/fs.c` and `kernel/log.c`. You will recognise every function, every data structure, every algorithm. The Python code and the xv6 C code are the same program in two languages.

---

_Essay based on `mini_unix_fs_xv6.py` — a Python simulator faithful to xv6's filesystem design._

_Primary reference: xv6, a simple Unix-like teaching operating system._ _Source: https://github.com/mit-pdos/xv6-riscv_ _Companion book: https://pdos.csail.mit.edu/6.828/2023/xv6/book-riscv-rev3.pdf_ _Concepts also from: Lions' Commentary on UNIX 6th Edition, the POSIX standard, Linux ext4 and log.c._