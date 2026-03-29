# Part 2 — Disk Layout Mental Model

---

## The Disk Is a Flat Array of Blocks

The disk controller presents a flat numbered sequence of fixed-size blocks:

```
block 0
block 1
block 2
...
block 255
```

Every block is 64 bytes (`BLOCK_SIZE = SECTOR_SIZE = 64`). There are 256 total blocks. This gives a 16 KB filesystem — tiny, but structurally identical to a real one.

A block number is just an index into this array. All filesystem structures sit at specific block numbers, and everything maps back to that index.

---

## Reading the Actual Layout from the Code

Section 1 defines the layout with computed constants. The key variable assignments (lines 252–257) are the authoritative values — not the stale comments above them:

```python
LOGSTART      = 2
LOGSIZE       = 8
INODE_START   = LOGSTART + 1 + LOGSIZE   # 2 + 1 + 8 = 11
INODE_BLOCKS  = NINODES // IPB            # 32 / 4 = 8 blocks
BMAP_START    = INODE_START + INODE_BLOCKS  # 11 + 8 = 19
DATA_START    = BMAP_START + 1              # 20
```

> **Note**: Several comments in the source file say `= 2+1+4 = 7` or `LOGSIZE=4 blocks`. Those are stale. The actual Python values are `LOGSIZE=8`, `INODE_START=11`, `BMAP_START=19`, `DATA_START=20`. Run `fs.sbdump()` to verify from disk.

---

## The Layout: Every Region Has a Job

```
Block 0         : Boot block       — reserved, never used
Block 1         : Superblock       — filesystem geometry + magic number
Block 2         : Log header       — WAL commit record (LOGSTART)
Blocks 3–10     : Log data         — 8 log data blocks (LOGSIZE=8)
Blocks 11–18    : Inode table      — 32 inodes, 4 per block, 8 blocks
Block 19        : Block bitmap     — 1 bit per block, tracks free blocks
Blocks 20–255   : Data blocks      — 236 usable data blocks
```

Verify this by running `fs.mkfs()`:

```
[mkfs]  Formatted 256-block filesystem
  Superblock at block 1  (magic 0x10203040)
  Log        at blocks 2–10
  Inodes     at blocks 11–18  (32 inodes, 4 per block)
  Bitmap     at block  19
  Data       at blocks 20–255  (236 blocks)
```

---

## Derived from Constants, Not Hardcoded

The layout is computed, not assumed. Change `NINODES` from 32 to 64 and `BMAP_START` automatically shifts to accommodate the larger inode table. Every downstream constant adjusts.

```python
NINODES      = 32
IPB          = 4              # inodes per block (BLOCK_SIZE // DINODE_SIZE)
INODE_BLOCKS = NINODES // IPB # = 8 blocks
BMAP_START   = INODE_START + INODE_BLOCKS  # moves if inode table grows
DATA_START   = BMAP_START + 1              # moves if bitmap moves
```

---

## Visualizing the Layout

```
LBA     Region         Contents
---     -------        --------
  0     Boot           (empty — reserved for bootloader)
  1     Superblock     magic, size, nblocks, ninodes, nlog, logstart, ...
  2     Log Header     n_committed + block_nos[8]
3–10    Log Data       8 log data blocks (LOGSIZE=8)
11–18   Inode Table    32 dinodes packed 4 per block (INODE_START=11)
 19     Block Bitmap   1 bit per block (256 bits = 32 bytes, fits in 64B)
20–255  Data Blocks    actual file and directory contents
```

Use `fs.explain_block(n)` to decode any block:
- `fs.explain_block(2)` → log header
- `fs.explain_block(11)` → inode block (inums 1–4)
- `fs.explain_block(19)` → block bitmap
- `fs.explain_block(20)` → first data block

---

## Why This Order Matters

**Block 0** (boot) is at LBA 0 because the BIOS jumps to the first sector.

**Block 1** (superblock) must be at a fixed, known location. `readsb()` hardcodes reading block 1. If the superblock were at a variable location, you'd need another mechanism to find it — infinite regress.

**Log before inodes**: The log must be located before the filesystem starts modifying anything. Its location is stored in the superblock. On mount, xv6 reads the superblock, finds the log at block 2, and replays it before doing anything else.

**Bitmap before data**: `_bitmap_alloc()` scans from `DATA_START (20)` forward. It needs the bitmap at a known location (`BMAP_START=19`) before it can find free blocks.

**Data last**: Putting data blocks at the end means metadata regions are at small, predictable LBAs. Metadata is rarely more than a handful of blocks; data can be hundreds.

---

## The Metadata Boundary: Blocks 0–19

Blocks 0–19 are **permanently allocated**. They are never available for file data.

`mkfs()` marks them as used in the bitmap at format time:

```python
# Blank bitmap — mark metadata blocks as allocated
bitmap = bytearray(BLOCK_SIZE)
for b in range(DATA_START):    # range(20) → blocks 0..19
    bitmap[b // 8] |= (1 << (b % 8))
_raw_write(BMAP_START, bitmap)
```

`_bitmap_alloc()` therefore only scans blocks 20–255:

```python
for b in range(DATA_START, TOTAL_BLOCKS):   # range(20, 256)
```

It will never accidentally hand out a metadata block as file data.

---

## Block Numbers Are LBAs

The filesystem always works in block numbers:

```python
disk_read(blockno)
disk_write(blockno, data)
```

These are Logical Block Addresses. The disk controller translates them to `(cylinder, head, sector)` coordinates. With `BLOCK_SIZE == SECTOR_SIZE == 64`, one filesystem block equals one physical sector. Block number 19 is exactly LBA 19 which is exactly one physical sector.

---

## Summary Table

| Block(s) | Region     | Who reads it              | Who writes it             |
|----------|------------|---------------------------|---------------------------|
| 0        | Boot       | BIOS                      | mkfs (blank)              |
| 1        | Superblock | `mount()` → `readsb()`    | `mkfs()`                  |
| 2        | Log header | `recover()` at mount      | `_commit()` at end_op     |
| 3–10     | Log data   | `_install_trans()`        | `_commit()` step 1        |
| 11–18    | Inodes     | `iget()` / `ialloc()`     | `_iupdate()`              |
| 19       | Bitmap     | `_bitmap_alloc()`         | `_bitmap_alloc/free()`    |
| 20–255   | Data       | `readi()` via `_bmap()`   | `writei()` via `_bmap()`  |
