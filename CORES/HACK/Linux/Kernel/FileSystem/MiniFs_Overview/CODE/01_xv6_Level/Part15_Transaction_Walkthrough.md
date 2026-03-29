# Part 15 — Transaction Walkthrough (End-to-End Write)

---

## The Goal

This part traces a single operation — `fs.write_file("/notes.txt", "Hello")` — through every layer of the stack, from the Python function call down to bytes written on the simulated platter.

This is the most concrete way to understand how all twelve layers work together.

---

## Setup

After `fs.mkfs()` + `fs.touch("/notes.txt")`:

| Inode | Path       | Block  | Offset | State |
|-------|------------|--------|--------|-------|
| 1     | /          | 11     | 0      | DIR, nlink=2, size=32, addrs=[20] |
| 2     | /notes.txt | 11     | 16     | FILE, nlink=1, size=0, addrs=[0], indirect=0 |

Root directory inode 1 lives in block 11 at offset 0.
`/notes.txt` inode 2 lives in block 11 at offset 16.
Block 20 (`DATA_START`) is the root directory's data block (holds `.` and `..` entries).
Block 21 is where the root directory's `notes.txt` entry lives (added by `touch`).

> Block numbers used by the root directory and its entry are the first allocations from `DATA_START=20`. After `mkfs`, root's data block is 20. After `touch`, the entry for notes.txt is in block 20 (if it fits) or 21.

For this walkthrough, `notes.txt` has `addrs=[0]` — no data block yet. First free block available for data: whatever `_bitmap_alloc()` finds first above `DATA_START=20` that isn't already taken.

Let's say block 22 is the first free data block (blocks 20 and 21 are used by root dir data). The bitmap block is 19.

---

## Layer 1: Filesystem API

```python
fs.write_file("/notes.txt", "Hello")
```

`FileSystem.write_file()`:

```python
def write_file(self, path, data):
    data = data.encode("utf-8")   # b"Hello"
    log.begin_op()
    try:
        ip = namei(path)          # resolve /notes.txt → inode 2
        _itrunc(ip)               # free existing blocks (addrs=[0] → nothing to do)
        writei(ip, 0, data)       # write b"Hello" at offset 0
        iput(ip)
    except Exception:
        log.end_op(); raise
    log.end_op()                  # commit transaction
```

---

## Layer 2: Path Resolution (`namei`)

`namei("/notes.txt")` → `_namex("/notes.txt", parent=False)`:

1. `iget(1)` → root inode (block 11, offset 0)
2. `_skipelem("notes.txt")` → `("notes.txt", "")`
3. `dirlookup(root, "notes.txt")`:
   - `readi(root, 0, 16)` → first dirent: `.` → inode 1
   - `readi(root, 16, 16)` → second dirent: `..` → inode 1
   - `readi(root, 32, 16)` → third dirent: `notes.txt` → inode 2 ← **match**
   - Returns `iget(2), 32`
4. `iput(root)` — release root
5. Path exhausted → return inode 2

---

## Layer 3: itrunc (Nothing to Do)

`_itrunc(inode2)`: `addrs[0] == 0` and `indirect == 0`. No blocks to free.

---

## Layer 4: writei

```python
writei(inode2, 0, b"Hello")
```

Single loop iteration (5 bytes fit in one block):

```python
logical_bn = 0 // 64 = 0
disk_bn    = _bmap(inode2, 0)   # ← allocates data block
blk_data   = disk_read(disk_bn) # all zeros (freshly allocated)
blk_data[0:5] = b"Hello"
disk_write(disk_bn, blk_data)
log.log_write(disk_bn)
```

After loop: `inode2.size = 5`, `_iupdate(inode2)`.

---

## Layer 5: bmap Allocates a Block

`_bmap(inode2, 0)`:

```python
bn = 0 < NDIRECT (1)   → direct path
inode2.addrs[0] == 0   → need to allocate

b = _bitmap_alloc()     # returns 22 (first free data block)
inode2.addrs[0] = 22
_iupdate(inode2)        # disk_write(block 11, ...) + log.log_write(11)
return 22
```

**`_bitmap_alloc()`**:
1. `disk_read(19)` — read bitmap block 19
2. Scan bits 20–255, find first clear bit (say bit 22)
3. Set bit 22: `bitmap[22//8] |= (1 << (22 % 8))`
4. `disk_write(19, bitmap)` — update bitmap in cache
5. `log.log_write(19)` — log the bitmap change (block 19)
6. `disk_write(22, zeros)` — zero out the new block in cache
7. `log.log_write(22)` — log the zeroed block
8. Return 22

---

## Layer 6: _iupdate Logs the Inode Block

`_iupdate(inode2)`:
1. `disk_read(11)` — read inode block (inodes 1–4)
2. Modify bytes 16–31 (inode 2's slot at offset 16):
   pack `type=1, nlink=1, size=5, addr=22, indirect=0`
3. `disk_write(11, modified_block)` — update in cache
4. `log.log_write(11)` — log inode block 11

---

## Layer 7: writei Writes Data and Logs It

After `_bmap` returns 22:
- `disk_read(22)` → zeros (cache hit)
- Write `b"Hello"` into bytes 0–4
- `disk_write(22, blk_data)` — update in cache
- `log.log_write(22)` — log the data block

---

## Layer 8: end_op Commits

At `log.end_op()`, `outstanding` drops to 0. `_commit()` is called.

**Pending writes**: `[11, 19, 22]` (inode block, bitmap block, data block)

**Step 1: Write log data area** (blocks 3, 4, 5)

```
_raw_write(3, bcache.bread(11))   → log data 0 ← inode block copy
_raw_write(4, bcache.bread(19))   → log data 1 ← bitmap copy
_raw_write(5, bcache.bread(22))   → log data 2 ← data block copy
```

**Step 2: Write log header (COMMIT POINT)**

```
_raw_write(2, pack(LOG_HDR_FMT, 3, [11, 19, 22, 0, 0, 0, 0, 0]))
```

Block 2 now contains: `n=3, blocks=[11,19,22,...]`. Transaction is durable.

**Step 3: Install**

```
_raw_write(11, _raw_read(3))   → inode block at LBA 11
_raw_write(19, _raw_read(4))   → bitmap at LBA 19
_raw_write(22, _raw_read(5))   → data block at LBA 22
```

**Step 4: Clear log header**

```
_raw_write(2, pack(LOG_HDR_FMT, 0, [0,0,...]))
```

---

## Layer 9: Physical Platter

Each `_raw_write(lba, data)` → `_controller.write(lba, data)` → `lba_to_chs(lba)` → `_platter.write_sector(c, h, s, data)`.

```
lba_to_chs(11):
  c = 11 // 32 = 0,  h = (11//8)%4 = 1,  s = 11%8 = 3  → (0,1,3)

lba_to_chs(19):
  c = 19 // 32 = 0,  h = (19//8)%4 = 2,  s = 19%8 = 3  → (0,2,3)

lba_to_chs(22):
  c = 22 // 32 = 0,  h = (22//8)%4 = 2,  s = 22%8 = 6  → (0,2,6)
```

Bytes `b"Hello"` are stored at `_platter._storage[(0, 2, 6)]`.

---

## Summary of All Disk Writes

| Step | LBA | CHS | What |
|------|-----|-----|------|
| Log data 0 | 3 | (0,0,3) | inode block 11 copy |
| Log data 1 | 4 | (0,0,4) | bitmap block 19 copy |
| Log data 2 | 5 | (0,0,5) | data block 22 copy |
| Commit point | 2 | (0,0,2) | log header: n=3, [11,19,22] |
| Install 1 | 11 | (0,1,3) | inode block home |
| Install 2 | 19 | (0,2,3) | bitmap home |
| Install 3 | 22 | (0,2,6) | data block home — holds "Hello" |
| Clear log | 2 | (0,0,2) | log header: n=0 |

**8 physical writes** for a 5-byte `write_file`. 3 writes would suffice without the log (inode, bitmap, data). The log adds 5 more: 3 log data copies, the commit header write, and the header clear.

---

## Verifying with Simulator Commands

```python
fs.iolog(10)          # see the last 10 physical I/Os with LBA + CHS
fs.explain_block(22)  # data block: hex shows "Hello\x00..."
fs.explain_block(11)  # inode block: inode 2 at offset 16 has addr=22, size=5
fs.explain_block(19)  # bitmap: bit 22 is set
fs.stat("/notes.txt") # full inode info with CHS coordinates
```
