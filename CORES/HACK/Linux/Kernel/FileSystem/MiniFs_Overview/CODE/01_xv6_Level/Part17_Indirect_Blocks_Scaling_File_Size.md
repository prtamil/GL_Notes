# Part 17 — Indirect Blocks (Scaling File Size)

---

## The Problem With Fixed-Size Inodes

An inode is a fixed-size record on disk: 16 bytes. Yet a file can be any size. With `DINODE_FMT = "HHIII"` there is room for exactly one direct block pointer. That gives a maximum file size of 1 × 64 = 64 bytes — far too small.

The solution is indirection: instead of storing only data block addresses directly, store the address of a **pointer block** — a disk block that contains nothing but addresses of data blocks.

---

## The Pointer Structure in the Simulator

```python
NDIRECT   = 1                     # one direct block pointer in the inode
NINDIRECT = BLOCK_SIZE // 4       # = 64 // 4 = 16 pointers per indirect block
MAXFILE   = NDIRECT + NINDIRECT   # = 1 + 16 = 17 blocks maximum
```

Each inode has:
- `addrs[0]`: direct block pointer → holds the first 64 bytes of file data (logical block 0)
- `indirect`: pointer to an indirect block → for logical blocks 1–16

The indirect block is a 64-byte disk block containing 16 four-byte integers, each a physical block number:

```
indirect block layout (64 bytes):
  bytes  0– 3:  address of data block for logical block 1
  bytes  4– 7:  address of data block for logical block 2
  ...
  bytes 60–63:  address of data block for logical block 16
```

Maximum file size: `17 × 64 = 1088 bytes`.

---

## bmap's Two-Level Structure

`_bmap()` handles both levels transparently:

```python
def _bmap(ip, bn):
    if bn < NDIRECT:         # bn == 0 → direct
        if ip.addrs[bn] == 0:
            b = _bitmap_alloc()
            ip.addrs[bn] = b
            _iupdate(ip)
        return ip.addrs[bn]

    # bn >= 1 → indirect
    bn -= NDIRECT   # adjust to indirect-relative index (0..15)

    if ip.indirect == 0:
        ib = _bitmap_alloc()      # allocate the pointer block itself
        ip.indirect = ib
        _iupdate(ip)

    ind_data = bytearray(disk_read(ip.indirect))
    bcache.brelse(ip.indirect)
    addr = struct.unpack_from("I", ind_data, bn * 4)[0]
    if addr == 0:
        b = _bitmap_alloc()       # allocate a data block
        struct.pack_into("I", ind_data, bn * 4, b)
        disk_write(ip.indirect, ind_data)
        log.log_write(ip.indirect)
        addr = b
    return addr
```

For `bn=0`: direct path, return `addrs[0]`, allocate if needed.

For `bn=1`: indirect path.
- `bn -= 1` → indirect-relative index 0.
- If `ip.indirect == 0`: allocate the pointer block (e.g. gets block 21).
- Read the pointer block (block 21).
- Entry 0 (bytes 0–3) = address of logical-block-1's data. If zero, allocate (e.g. block 22).
- Return 22.

---

## The Two-Disk-Read Cost

Reading any byte in the indirect range costs two disk reads:
1. Read the indirect (pointer) block to find the data block's address.
2. Read the data block to get the actual bytes.

Direct block: only one disk read (address is already in the inode cache).

This overhead is the cost of indirection.

---

## itrunc Handles Both Levels

```python
def _itrunc(ip):
    # 1. Free the single direct block
    for i in range(NDIRECT):
        if ip.addrs[i]:
            _bitmap_free(ip.addrs[i])
            ip.addrs[i] = 0

    # 2. Read indirect block, free all data blocks it references
    if ip.indirect:
        ind_data = bytearray(disk_read(ip.indirect))
        bcache.brelse(ip.indirect)
        for i in range(NINDIRECT):
            addr = struct.unpack_from("I", ind_data, i * 4)[0]
            if addr:
                _bitmap_free(addr)
        _bitmap_free(ip.indirect)   # 3. Free the pointer block itself
        ip.indirect = 0

    ip.size = 0
    _iupdate(ip)
```

The pointer block must be read **before** it is freed. Freeing it first could overwrite its bytes.

---

## Triggering Indirect Blocks: The Demo

The demo section in `mini_unix_xv6_fs.py` writes 160 bytes to test indirect allocation:

```python
fs.touch("/bigfile.txt")
big_data = "ABCDEFGH" * 20         # 160 bytes
fs.write_file("/bigfile.txt", big_data)
fs.stat("/bigfile.txt")            # should show indirect block
```

With `BLOCK_SIZE = 64` and `NDIRECT = 1`:
- Logical block 0: bytes 0–63 → direct block `addrs[0]` (e.g. block 20)
- Logical block 1: bytes 64–127 → indirect entry 0 (e.g. block 22)
- Logical block 2: bytes 128–159 → indirect entry 1 (e.g. block 23)

Three data blocks + one pointer block = four blocks allocated total.

`stat` output:
```
[stat]  /bigfile.txt
  size        = 160 bytes
  direct blks = [20]
  indirect    = 21
    direct[0]  LBA=20 → C=0 H=2 S=4
    indirect   LBA=21 → C=0 H=2 S=5
```

`fs.explain_block(21)` shows the pointer block's hex: first 4 bytes are the LBA of block 22, next 4 are block 23, rest are zeros.

---

## Extending the Hierarchy: Double and Triple Indirect

xv6 (real C version) uses `NDIRECT=12` direct pointers plus single indirect. For larger files, a **double-indirect block** adds another nesting level:

```
inode.double_indirect → block of 16 pointers
    each pointer → block of 16 data pointers
        each → data block
```

Maximum with single indirect only: `(1 + 16) × 64 = 1088 bytes`.
Maximum with double indirect: `(1 + 16 + 16²) × 64 ≈ 17 KB`.

The simulator uses only single indirect for simplicity. The concept scales directly: `_bmap()` would add another branch for `bn >= NDIRECT + NINDIRECT`.

---

## Observing Indirect Blocks

```python
fs.touch("/big.txt")
fs.write_file("/big.txt", "X" * 70)   # 70 bytes > 64 → needs indirect
fs.stat("/big.txt")
fs.explain_block(21)   # pointer block: first 4 bytes = address of block 22
fs.explain_block(22)   # data block: bytes 64–69 = "XXXXXX"
```

The iolog will show `BALLOC` for three blocks: the first data block (direct), the pointer block (indirect), and the second data block (first indirect entry).
