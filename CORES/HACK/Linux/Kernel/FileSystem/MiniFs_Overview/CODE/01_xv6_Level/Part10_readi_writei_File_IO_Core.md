# Part 10 — readi / writei (File I/O Core)

---

## The I/O Interface Above bmap

`_bmap()` translates logical block numbers to physical disk blocks. But callers don't want to think in blocks — they want to read and write byte ranges. `readi()` and `writei()` provide that interface.

They are the lowest-level I/O functions in the filesystem. Every higher-level operation — `read_file()`, directory scanning, `stat()`, `dirlookup()` — ultimately calls `readi()` or `writei()`.

---

## `readi(ip, offset, n)` — Reading Bytes from an Inode

```python
def readi(ip, offset, n):
    if offset > ip.size:
        return b""
    if offset + n > ip.size:
        n = ip.size - offset

    result = bytearray()
    tot = 0
    while tot < n:
        logical_bn = (offset + tot) // BLOCK_SIZE
        disk_bn    = _bmap(ip, logical_bn)
        blk_data   = bytearray(disk_read(disk_bn))
        bcache.brelse(disk_bn)
        blk_off  = (offset + tot) % BLOCK_SIZE
        to_read  = min(n - tot, BLOCK_SIZE - blk_off)
        result  += blk_data[blk_off: blk_off + to_read]
        tot     += to_read

    return bytes(result)
```

**Boundary check**: if `offset > ip.size`, return empty. If the read would go past the end of the file, clamp `n` to the available bytes. This prevents reading garbage beyond the file's actual content.

**The loop**: iterate until `tot` bytes have been collected. In each iteration:

1. Compute the **logical block number**: `(offset + tot) // BLOCK_SIZE`
2. Translate to **physical block number**: `_bmap(ip, logical_bn)`
3. Read the physical block from cache: `disk_read(disk_bn)`
4. Compute the **byte offset within that block**: `(offset + tot) % BLOCK_SIZE`
5. Compute how many bytes to take from this block: `min(remaining, BLOCK_SIZE - blk_off)`
6. Slice and append to result.

The key insight: reads can **cross block boundaries**. If you read 100 bytes starting at byte 50, that spans two blocks (bytes 50–63 from block 0, bytes 0–35 from block 1). The loop handles this naturally — it processes one block per iteration, taking only as many bytes as fit within that block before moving to the next.

---

## `writei(ip, offset, data)` — Writing Bytes to an Inode

```python
def writei(ip, offset, data):
    if isinstance(data, str):
        data = data.encode("utf-8")

    if offset + len(data) > MAXFILE * BLOCK_SIZE:
        raise OSError(f"Write would exceed MAXFILE limit ({MAXFILE * BLOCK_SIZE}B)")

    tot = 0
    while tot < len(data):
        logical_bn = (offset + tot) // BLOCK_SIZE
        disk_bn    = _bmap(ip, logical_bn)
        blk_data   = bytearray(disk_read(disk_bn))
        bcache.brelse(disk_bn)
        blk_off  = (offset + tot) % BLOCK_SIZE
        to_write = min(len(data) - tot, BLOCK_SIZE - blk_off)
        blk_data[blk_off: blk_off + to_write] = data[tot: tot + to_write]
        disk_write(disk_bn, blk_data)
        log.log_write(disk_bn)
        tot += to_write

    if offset + len(data) > ip.size:
        ip.size = offset + len(data)
        _iupdate(ip)

    return len(data)
```

The loop structure mirrors `readi()`. Per iteration:

1. Logical block number: `(offset + tot) // BLOCK_SIZE`
2. Physical block via `_bmap()` — allocates a new block if needed
3. Read the current block contents (needed for partial-block writes — you must not overwrite the untouched portion)
4. Splice the new data into the right position within the block
5. Write the modified block back to cache: `disk_write(disk_bn, blk_data)`
6. Log the write: `log.log_write(disk_bn)`

**The read-modify-write problem**: notice that even for writes, you start with `disk_read`. If you are writing only 10 bytes into the middle of a 64-byte block, you must first read the block so the other 54 bytes are preserved. Then overlay your 10 bytes, then write the whole block back.

**Size update**: if the write extends the file beyond its current size, update `ip.size` and call `_iupdate()` to persist the new size to disk (also logging the inode block change).

---

## The Block Crossing Arithmetic

The loop handles block boundaries through modular arithmetic. Consider writing 30 bytes at offset 50:

```
First iteration:
  offset + tot = 50
  logical_bn   = 50 // 64 = 0      (block 0)
  blk_off      = 50 % 64  = 50
  to_write     = min(30, 64-50) = min(30, 14) = 14
  → write bytes 0–13 of data into block 0 positions 50–63
  tot = 14

Second iteration:
  offset + tot = 50 + 14 = 64
  logical_bn   = 64 // 64 = 1      (block 1)
  blk_off      = 64 % 64  = 0
  to_write     = min(16, 64-0) = 16
  → write bytes 14–29 of data into block 1 positions 0–15
  tot = 30
```

The loop exits when `tot == len(data) == 30`. Two blocks were touched even though the write was only 30 bytes. The arithmetic requires no special cases for block boundaries.

---

## How readi Is Used for Directories

Directories are files. Their contents are sequences of 16-byte `dirent` structs. `dirlookup()` reads them using `readi()`:

```python
for off in range(0, dp.size, DIRENT_SIZE):
    raw = readi(dp, off, DIRENT_SIZE)
    inum, name_bytes = struct.unpack(DIRENT_FMT, raw)
```

`readi` is called with `dp` (the directory inode), `off` (byte offset), and `DIRENT_SIZE` (16). It returns exactly 16 bytes, which are then unpacked as a dirent. The directory layer doesn't know about blocks at all — `readi` handles the block arithmetic transparently.

Similarly, `dirlink()` writes dirents using `writei()`:

```python
writei(dp, off, struct.pack(DIRENT_FMT, inum, name_enc))
```

The directory, inode, and file data layers all use the same `readi`/`writei` interface, with different inode objects. This uniformity is the power of the inode abstraction.

---

## Key Differences from a Syscall-Level read()

`readi()` and `writei()` are **not** the `read(2)` and `write(2)` syscalls. They:

- Operate on inodes, not file descriptors
- Do not update a per-open offset (that's the file descriptor table's job, Part 14)
- Do not require the log to be active (callers must call `begin_op`/`end_op`)
- Return raw data, not through a userspace buffer copy

The file descriptor table in Section 8 sits on top of these functions and provides the stateful, per-process interface that matches the POSIX syscall semantics.
