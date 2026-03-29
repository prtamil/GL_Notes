# Part 8 — Inodes (Identity + Metadata)

---

## The Inode Is the File

In UNIX, a file is not its name. A file is its inode. The inode is a fixed-size record on disk that stores everything the kernel needs to know about a file except its name:

- What type it is (file or directory)
- How many names point to it (hard link count)
- How large it is (in bytes)
- Where its data lives (block pointers)

The name is stored separately in a directory. The inode stores the identity.

---

## The On-Disk Inode Format (dinode)

Each on-disk inode is 16 bytes, called a `dinode`:

```python
DINODE_FMT  = "HHIII"
# H = type     (2 bytes) — T_UNUSED=0, T_FILE=1, T_DIR=2
# H = nlink    (2 bytes) — hard link count
# I = size     (4 bytes) — file size in bytes
# I = addr     (4 bytes) — the ONE direct block pointer (NDIRECT=1)
# I = indirect (4 bytes) — indirect block pointer (0 = unused)
# Total: 2+2+4+4+4 = 16 bytes
DINODE_SIZE = struct.calcsize(DINODE_FMT)  # = 16
```

`NDIRECT = 1`: there is exactly **one** direct block pointer per inode.

With 64-byte blocks and 16-byte dinodes, four inodes fit per block:

```python
IPB = BLOCK_SIZE // DINODE_SIZE  # = 64 // 16 = 4
```

The inode table spans 8 blocks (`INODE_BLOCKS = NINODES // IPB = 32 // 4 = 8`), starting at block 11:

```
INODE_START = 11
Blocks 11–18: inode table (32 inodes total)
```

---

## Locating an Inode on Disk

Given an inode number `inum`, its disk location is arithmetic:

```python
def _inode_block(inum):
    return INODE_START + (inum - 1) // IPB

def _inode_offset(inum):
    return ((inum - 1) % IPB) * DINODE_SIZE
```

Example: inode 1 (root directory)
```
block  = 11 + (1-1)//4 = 11 + 0 = 11
offset = ((1-1) % 4) * 16 = 0 * 16 = 0
```
Inode 1 is at byte offset 0 of block 11.

Example: inode 2
```
block  = 11 + (2-1)//4 = 11 + 0 = 11
offset = ((2-1) % 4) * 16 = 1 * 16 = 16
```
Inode 2 is at byte offset 16 of block 11.

Example: inode 5
```
block  = 11 + (5-1)//4 = 11 + 1 = 12
offset = ((5-1) % 4) * 16 = 0 * 16 = 0
```
Inode 5 is at byte offset 0 of block 12.

Block 11 holds inodes 1–4. Block 12 holds inodes 5–8. And so on through block 18 (inodes 29–32).

---

## The In-Memory Inode

The kernel doesn't work with raw bytes. It unpacks the dinode into an in-memory `Inode` object:

```python
class Inode:
    def __init__(self, inum):
        self.inum     = inum
        self.type     = T_UNUSED
        self.nlink    = 0
        self.size     = 0
        self.addrs    = [0] * NDIRECT   # [0] — one direct block pointer
        self.indirect = 0               # indirect block pointer
        self.ref      = 0               # runtime reference count
        self.dirty    = False
```

`addrs` is a list with exactly one element (`NDIRECT=1`). `addrs[0]` is the address of the file's first (and only direct) data block.

`ref` is not on disk. It counts how many places in the running code hold a pointer to this `Inode` object. When `ref` reaches zero and `nlink` is also zero, the inode can be freed.

---

## Packing and Unpacking

```python
def _pack_dinode(inode):
    return struct.pack(DINODE_FMT,
                       inode.type, inode.nlink, inode.size,
                       inode.addrs[0],   # single direct block
                       inode.indirect)

def _unpack_dinode(inum, block_data, offset):
    raw = block_data[offset: offset + DINODE_SIZE]
    t, nlink, size, a0, indirect = struct.unpack(DINODE_FMT, raw)
    ip = Inode(inum)
    ip.type = t; ip.nlink = nlink; ip.size = size
    ip.addrs = [a0]
    ip.indirect = indirect
    return ip
```

`_pack_dinode` writes exactly 16 bytes. `_unpack_dinode` reads exactly 16 bytes at the correct offset within the inode block.

---

## The Inode Cache

```python
_icache: dict = {}   # inum → Inode
```

### `iget(inum)` — acquire an inode

```python
def iget(inum):
    if inum in _icache:
        ip = _icache[inum]
        ip.ref += 1
        return ip

    blk = _inode_block(inum)
    off = _inode_offset(inum)
    raw = disk_read(blk)
    bcache.brelse(blk)
    ip  = _unpack_dinode(inum, raw, off)
    ip.ref = 1
    _icache[inum] = ip
    return ip
```

Cache hit: increment ref, return. Cache miss: compute block/offset using `_inode_block`/`_inode_offset`, read block from disk (e.g. block 11), unpack the 16 bytes at the right offset, cache and return.

### `iput(ip)` — release an inode

```python
def iput(ip):
    ip.ref -= 1
    if ip.ref == 0 and ip.nlink == 0:
        _itrunc(ip)
        ip.type = T_UNUSED
        _iupdate(ip)
        _icache.pop(ip.inum, None)
```

When `ref` drops to zero AND `nlink` is also zero: free all data blocks and mark the inode unused on disk. This is the deferred-free path (see Part 18).

---

## `ialloc(itype)` — Allocating a New Inode

```python
def ialloc(itype):
    for inum in range(1, NINODES + 1):
        blk = _inode_block(inum)
        off = _inode_offset(inum)
        raw = bytearray(disk_read(blk))
        bcache.brelse(blk)
        t, = struct.unpack_from("H", raw, off)
        if t == T_UNUSED:
            raw[off: off + DINODE_SIZE] = bytes(DINODE_SIZE)
            struct.pack_into("H", raw, off, itype)
            disk_write(blk, raw)
            log.log_write(blk)
            ip = iget(inum)
            ip.type = itype; ip.nlink = 0; ip.size = 0
            ip.addrs = [0] * NDIRECT; ip.indirect = 0
            return ip
    raise OSError("No free inodes — inode table exhausted!")
```

Scans blocks 11–18 looking for a slot where `type == T_UNUSED`. When found: zero the slot, write the new type, log the inode block (e.g. block 11), and return via `iget`.

---

## `_iupdate()` — Writing an Inode Back to Disk

```python
def _iupdate(ip):
    blk  = _inode_block(ip.inum)
    off  = _inode_offset(ip.inum)
    raw  = bytearray(disk_read(blk))
    bcache.brelse(blk)
    raw[off: off + DINODE_SIZE] = _pack_dinode(ip)
    disk_write(blk, raw)
    log.log_write(blk)
    ip.dirty = False
```

Read the whole inode block, modify the 16 bytes belonging to this inode, write the whole block back. This is necessary because multiple inodes share a single block — you cannot write just one dinode without overwriting its neighbours.

---

## Reserved Inode Numbers

```python
INUM_UNUSED = 0   # inode 0 = "no entry" in directory entries
INUM_ROOT   = 1   # inode 1 = always the root directory
```

Inode 0 is never allocated. It is the null sentinel in directory entries — a slot with `inum == 0` is deleted/empty.

Inode 1 is always the root directory. Every absolute path lookup starts at inode 1:

```python
if path.startswith("/"):
    ip = iget(INUM_ROOT)    # always iget(1)
```

Root inode 1 lives at block 11, offset 0.

---

## Inspecting Inodes

```python
fs.dump_inodes()   # all non-UNUSED inodes with disk block/offset
fs.stat("/path")   # full inode info with CHS coordinates
```

`stat` output example:
```
[stat]  /notes.txt
  inum        = 2  (disk block 11, offset 16)
  type        = Regular File
  nlink       = 1
  size        = 5 bytes
  direct blks = [20]
  indirect    = 0
    direct[0]  LBA=20 → C=0 H=2 S=4 (byte 1280)
```

Inode 2 sits at block 11 offset 16. Its direct block is LBA 20, which maps to cylinder 0, head 2, sector 4 on the platter.
