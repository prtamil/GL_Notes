# Part 9 — bmap (Logical to Physical Block Translation)

---

## The Abstraction Gap

An inode has block pointers. A file has bytes. Between them sits a translation problem: given "byte 150 of inode 2", which physical disk block contains it, and at what byte offset within that block?

`_bmap()` is the function that answers this. It maps a **logical block number** (which block of this file, counting from 0) to a **physical disk block number** (which LBA to read from the platter).

This mapping is what makes files feel like contiguous byte arrays even though their data may be scattered across many non-contiguous disk blocks.

---

## Logical vs Physical Block Numbers

A logical block number is file-relative: "block 0 of this file", "block 1 of this file". It tells you nothing about where on disk the data actually lives.

A physical block number (LBA) tells you exactly where on disk. The inode stores physical block numbers in its `addrs[0]` and `indirect` fields. `_bmap()` converts a caller's logical block number into the stored physical block number.

---

## The inode Block Pointer Structure

```python
NDIRECT   = 1                     # one direct block pointer in the inode
NINDIRECT = BLOCK_SIZE // 4       # = 64 // 4 = 16 pointers per indirect block
MAXFILE   = NDIRECT + NINDIRECT   # = 1 + 16 = 17 blocks maximum
```

Each inode has:
- `addrs[0]`: one direct block pointer — for logical block 0 (first 64 bytes of file data)
- `indirect`: pointer to an indirect block — for logical blocks 1–16

Maximum file size: `17 × 64 = 1088 bytes`.

---

## `_bmap(ip, bn)` — The Translation Function

```python
def _bmap(ip, bn):
    if bn < NDIRECT:           # bn == 0
        if ip.addrs[bn] == 0:
            b = _bitmap_alloc()   # allocate from DATA_START (20) upward
            ip.addrs[bn] = b
            _iupdate(ip)
        return ip.addrs[bn]

    # Indirect range: bn >= 1
    bn -= NDIRECT   # adjust to indirect-relative index (0..15)
    if bn >= NINDIRECT:
        raise OSError(f"File too large: block {bn + NDIRECT} exceeds MAXFILE={MAXFILE}")

    # Allocate indirect block if needed
    if ip.indirect == 0:
        ib = _bitmap_alloc()
        ip.indirect = ib
        _iupdate(ip)

    # Read indirect block, find/allocate entry at position bn
    ind_data = bytearray(disk_read(ip.indirect))
    bcache.brelse(ip.indirect)
    addr = struct.unpack_from("I", ind_data, bn * 4)[0]
    if addr == 0:
        b = _bitmap_alloc()
        struct.pack_into("I", ind_data, bn * 4, b)
        disk_write(ip.indirect, ind_data)
        log.log_write(ip.indirect)
        addr = b
    return addr
```

**Direct path** (`bn == 0`):
- Check `addrs[0]`. If zero: call `_bitmap_alloc()` to get a free data block (≥ 20), store it in `addrs[0]`, call `_iupdate()` to persist.
- Return `addrs[0]`.

**Indirect path** (`bn >= 1`):
- Adjust: `bn -= 1` (indirect-relative index 0..15).
- If `ip.indirect == 0`: allocate the indirect block itself first.
- Read the indirect block. It contains up to 16 four-byte pointers.
- Find the pointer at position `bn`: `struct.unpack_from("I", ind_data, bn * 4)`.
- If zero: allocate a new data block, write its address into the indirect block, and log it.
- Return the address.

---

## bmap Allocates On Demand

`_bmap()` is not just a lookup — it **allocates on demand**. If the block doesn't exist yet, it creates it. `writei()` can simply call `_bmap(ip, logical_bn)` without checking whether the block exists — it will after the call.

This is lazy allocation: the file occupies only the disk blocks it actually uses. A file created with `touch` has `addrs[0]=0` until the first byte is written.

---

## Walking Through an Example

After `mkfs() + touch("/notes.txt")`:
- Inode 2: `addrs=[0], indirect=0, size=0`
- First free data block: 20 (`DATA_START`)

Call `writei(inode2, 0, b"Hello")`:
- `logical_bn = 0 // 64 = 0`
- `_bmap(inode2, 0)`: bn=0 < NDIRECT, addrs[0]=0 → `_bitmap_alloc()` returns 20
- `inode2.addrs[0] = 20`, `_iupdate(inode2)` → logs block 11 (inode block)
- Returns 20

Write `b"Hello"` into block 20. The "Hello" bytes land at LBA 20:
```
lba_to_chs(20):
  c = 20 // 32 = 0
  h = (20 // 8) % 4 = 2
  s = 20 % 8 = 4
→ (C=0, H=2, S=4)
```

---

## The Two-Disk-Read Cost for Indirect Blocks

Reading any byte in the indirect range costs **two disk reads**:
1. Read the indirect block (e.g. block 21) to find the data block's address.
2. Read the data block (e.g. block 22) to get the actual bytes.

For the direct block (`addrs[0]`), only one disk read is needed — the inode's address is already loaded in the inode cache.

---

## `_itrunc()` — The Inverse of bmap

When a file is deleted, all its blocks must be freed. `_itrunc()` walks the same structure in reverse:

```python
def _itrunc(ip):
    # Free the direct block
    for i in range(NDIRECT):
        if ip.addrs[i]:
            _bitmap_free(ip.addrs[i])
            ip.addrs[i] = 0

    # Free each block referenced by the indirect block, then free the indirect block itself
    if ip.indirect:
        ind_data = bytearray(disk_read(ip.indirect))
        bcache.brelse(ip.indirect)
        for i in range(NINDIRECT):
            addr = struct.unpack_from("I", ind_data, i * 4)[0]
            if addr:
                _bitmap_free(addr)
        _bitmap_free(ip.indirect)
        ip.indirect = 0

    ip.size = 0
    _iupdate(ip)
```

The order matters: read the indirect block's contents **before** freeing the indirect block. Freeing it first would make the subsequent read return garbage.

---

## The Indirect Block Is Metadata, Not Data

The indirect block is a 64-byte disk block containing up to 16 four-byte pointers. It is not file content — it is a pointer table nested inside the inode's own pointer. `_bmap` reads it on every indirect access and modifies it when allocating a new indirect data block.

When `fs.stat("/path")` shows `indirect = 21`, that means block 21 is the pointer table, and within it you'll find the physical block numbers for logical blocks 1–16. Use `fs.explain_block(21)` to see the raw pointer bytes.
