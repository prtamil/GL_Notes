# Part 7 — Bitmap Allocator (Space Management)

---

## The Problem: Tracking Free Blocks

The filesystem needs to allocate a new data block when writing a file and free a block when deleting a file. To do either, it must know which blocks are currently in use and which are free.

The simplest possible data structure: a bitmap — one bit per block, `0` = free, `1` = allocated.

With 256 blocks, a complete bitmap needs 256 bits = 32 bytes. That fits comfortably inside a single 64-byte block.

xv6 uses exactly this approach. The bitmap lives at a single block (`BMAP_START = 19`), and `_bitmap_alloc()`/`_bitmap_free()` manipulate individual bits within it.

---

## The Bitmap Block

The bitmap covers all 256 blocks, indexed directly by block number:

```
bit 0   → block 0   (boot)
bit 1   → block 1   (superblock)
...
bit 19  → block 19  (bitmap itself)
bit 20  → first data block
...
bit 255 → last data block
```

Blocks 0–19 (the metadata region) are marked as allocated at `mkfs()` time and never freed. `_bitmap_alloc()` only searches from `DATA_START (20)` onward.

---

## `_bitmap_alloc()` — Finding and Allocating a Free Block

```python
def _bitmap_alloc():
    bitmap = bytearray(disk_read(BMAP_START))   # read block 19

    for b in range(DATA_START, TOTAL_BLOCKS):   # scan blocks 20..255
        byte_idx = b // 8
        bit_idx  = b % 8
        if not (bitmap[byte_idx] & (1 << bit_idx)):
            # Found a free block
            bitmap[byte_idx] |= (1 << bit_idx)
            disk_write(BMAP_START, bitmap)
            log.log_write(BMAP_START)           # log the bitmap change
            # Zero out the newly allocated block
            disk_write(b, bytearray(BLOCK_SIZE))
            log.log_write(b)                    # log the zeroed block
            bcache.bflush(b)
            if IO_TRACE: print(f"  [BALLOC] allocated block {b}")
            return b

    raise OSError("No free data blocks — filesystem full!")
```

The algorithm:

1. Read bitmap block 19 from cache.
2. Scan from `DATA_START (20)` upward.
3. For each block `b`, check if its bit is clear: `not (bitmap[b//8] & (1 << b%8))`.
4. When a free bit is found, set it: `bitmap[b//8] |= (1 << b%8)`.
5. Write the modified bitmap back to cache and log it (`BMAP_START = 19`).
6. Zero out the newly allocated block (so callers don't see stale data).
7. Log the zeroed block and return the block number.

The bit math: byte index is `b // 8`, bit position within that byte is `b % 8`.

---

## `_bitmap_free(b)` — Releasing a Block

```python
def _bitmap_free(b):
    assert b >= DATA_START, f"Cannot free metadata block {b}"
    bitmap = bytearray(disk_read(BMAP_START))
    byte_idx = b // 8
    bit_idx  = b % 8
    assert (bitmap[byte_idx] & (1 << bit_idx)), f"Block {b} was not allocated!"
    bitmap[byte_idx] &= ~(1 << bit_idx)
    disk_write(BMAP_START, bitmap)
    log.log_write(BMAP_START)
    bcache.invalidate(b)
```

Clearing a bit: `bitmap[b//8] &= ~(1 << b%8)`.

The two assertions guard against:
- Double-free: freeing an already-free block
- Metadata free: freeing blocks 0–19 which are permanently reserved

`bcache.invalidate(b)` evicts the freed block from cache. Future reads of this block go to disk and get zeros (the clean state set when the block was last allocated).

---

## Why Both Operations Touch `log.log_write`

Every `disk_write` to persistent state must be followed by `log.log_write` for the same block. The bitmap is persistent state. If you allocate a block (update bitmap), start writing data to it, and power fails before the log commits, you need the bitmap change to be part of the same atomic transaction as the data write.

Pattern in `_bitmap_alloc()`:

```python
disk_write(BMAP_START, bitmap)       # update bitmap in cache
log.log_write(BMAP_START)            # include bitmap block (19) in transaction
disk_write(b, bytearray(BLOCK_SIZE)) # zero new block in cache
log.log_write(b)                     # include new block in transaction
```

Both the bitmap change and the zeroed block are committed together. On crash recovery, either both are applied or neither is.

---

## The Metadata Boundary in mkfs

`mkfs()` marks blocks 0–19 as used in the bitmap at format time:

```python
bitmap = bytearray(BLOCK_SIZE)
for b in range(DATA_START):    # range(20) = blocks 0..19
    bitmap[b // 8] |= (1 << (b % 8))
_raw_write(BMAP_START, bitmap)
```

This sets the first 20 bits. After `mkfs()`, the bitmap block's first 3 bytes look like:
```
byte 0: 0xff  → blocks 0–7 all allocated (metadata)
byte 1: 0xff  → blocks 8–15 all allocated (metadata)
byte 2: 0x0f  → blocks 16–19 allocated, blocks 20–23 free
```

The first free bit is at position 20 — `DATA_START`.

---

## Counting Free Blocks

```python
def _free_block_count():
    bitmap = bytearray(disk_read(BMAP_START))
    free = 0
    for b in range(DATA_START, TOTAL_BLOCKS):   # 20..255
        byte_idx = b // 8
        bit_idx  = b % 8
        if not (bitmap[byte_idx] & (1 << bit_idx)):
            free += 1
    return free
```

Used by `fs.df()`. Scans bits 20–255 and counts zeros. Called only for diagnostics — not on the hot path.

---

## Visualizing the Bitmap

```python
fs.explain_block(19)
```

After `mkfs()` with one file written to block 20:
```
[explain]  Block 19:
  Role        : block bitmap
  Hex[0:32]   : ffff1f00 00000000 00000000 00000000...
```

Breaking down `ffff1f00`:
- `ff` = bits 0–7 all set (blocks 0–7 = boot, superblock, log)
- `ff` = bits 8–15 all set (blocks 8–15 = log data continues)
- `1f` = bits 0–4 of byte 2 set = blocks 16–20 (still metadata 16–19, plus first data block 20 now allocated)
- `00` = blocks 21–23 free

Use `fs.explain_block(19)` after every `touch`, `write_file`, and `unlink` to watch bits flip.

---

## Comparison to the Simple Filesystem

The v1 simple filesystem (`mini_unix_fs.py`) tracks free blocks with a Python list:

```python
free_blocks = list(range(DATA_START, TOTAL_BLOCKS))
block = free_blocks.pop()
free_blocks.append(block)
```

This works but is not disk-persistent. The bitmap allocator stores its state on disk — it survives power failures. That is the essential difference: the bitmap can be recovered; the Python list cannot.
