# Part 18 — Deferred-Free Unlink Contract

---

## The Problem

Consider this sequence:

```
fd = open("/tmp/work.txt", "rw")
unlink("/tmp/work.txt")
# ... fd is still valid, can still read/write ...
close(fd)
# only NOW does the file's data get freed
```

This is standard UNIX behavior. `unlink()` removes the name. The file's data is freed only when there are no more open file descriptors AND no more directory entries pointing to the inode.

Many programs rely on this. A common pattern is: open a temp file, immediately unlink it (so it's cleaned up on crash), use it while the process runs, and let the kernel free it on exit. The file exists but has no name — it can only be accessed through the open file descriptor.

The simulator implements this correctly. Understanding how requires following the `nlink` and `ref` counts carefully.

---

## Two Independent Reference Counts

Every inode has two counts:

**`nlink`** (on-disk): the number of directory entries pointing to this inode. Decremented by `unlink()`. Incremented by `link()`. When zero, there is no way to find this inode through any path — it has no name.

**`ref`** (in-memory): the number of in-memory references to this inode — how many places in the code currently hold a pointer to the `Inode` object. Incremented by `iget()`. Decremented by `iput()`. When zero, no code is actively using the inode.

The inode is freed **only when both reach zero simultaneously**. The logic lives in `iput()`:

```python
def iput(ip):
    ip.ref -= 1
    if ip.ref == 0 and ip.nlink == 0:
        _itrunc(ip)
        ip.type = T_UNUSED
        _iupdate(ip)
        _icache.pop(ip.inum, None)
```

---

## The Deferred-Free Scenario Step by Step

**Step 1: Open the file**

```python
fd = _fd_table.open("/notes.txt", "rw")
```

Inside `open()`:
- `namei("/notes.txt")` → `iget(4)` → `inode4.ref = 1`
- Store in fd table: `{inum: 4, offset: 0, ...}`

State: `inode4.nlink = 1, ref = 1`

**Step 2: Unlink the file**

```python
fs.unlink("/notes.txt")
```

Inside `unlink()`:
- `dirlookup(root, "notes.txt")` → returns `iget(4)` → `inode4.ref = 2`
- Zero out directory entry in root (inum=4 slot set to inum=0)
- `inode4.nlink -= 1` → `nlink = 0`
- `_iupdate(inode4)` — write `nlink=0` to disk
- `iput(inode4)` → `ref = 1` (from 2 to 1; ref > 0 → don't free)

State: `inode4.nlink = 0, ref = 1`

The file has no name now. It cannot be found via `namei`. But the fd table still holds `{inum: 4, ...}` and the `iget` from `open()` is keeping `ref = 1`.

**Step 3: Use the file through fd**

```python
_fd_table.write(fd, "more data")
```

`iget(4)` → `ref = 2`. `writei(...)`. `iput(ip)` → `ref = 1`. The fd table's reference keeps the inode alive.

The file has no name but its data is perfectly accessible through `fd`.

**Step 4: Close the fd**

```python
_fd_table.close(fd)
```

Inside `close()`:
```python
entry = self._table.pop(fd, None)
ip = _icache[entry['inum']]
iput(ip)   # release fd's reference
```

`iput(inode4)`:
- `ref -= 1` → `ref = 0`
- `ref == 0 and nlink == 0` → TRUE
- `_itrunc(inode4)` — free all data blocks, update bitmap
- `inode4.type = T_UNUSED`
- `_iupdate(inode4)` — write freed state to disk
- Remove from `_icache`

State: inode 4 is free. Data blocks freed. Bitmap updated.

---

## The Contract Restated

```
File is freed when:
  nlink == 0    (no directory entries)
  AND ref == 0  (no open file descriptors)

unlink() decrements nlink but leaves ref alone.
close() decrements ref but leaves nlink alone.
The file survives until both reach zero.
```

This is the contract. It is what makes UNIX temp file patterns work. It is why `rm` on an open log file doesn't immediately break the logging program.

---

## Hard Links and the nlink Count

Hard links are the other side of `nlink`. Create two names for the same file:

```python
fs.touch("/a.txt")
fs.link("/a.txt", "/b.txt")
# inode.nlink = 2
```

Now:
```python
fs.unlink("/a.txt")
# inode.nlink = 1, ref = 0 → NOT freed (nlink > 0)
```

The file still exists as `/b.txt`. Its data is intact. The inode will be freed only when `/b.txt` is also unlinked AND any open fds are closed.

---

## What Happens to On-Disk Data After Free

When `_itrunc()` is called, it calls `_bitmap_free()` for each data block. The bitmap bit is cleared. The data itself is **not zeroed** on disk. It remains at those physical locations until some future `_bitmap_alloc()` assigns those blocks to a new file and overwrites them.

This is why:
1. Forensic recovery can sometimes find deleted file contents on a disk image.
2. You should use secure-erase tools (not just `rm`) for sensitive data.
3. SSDs complicate this because of wear leveling — the physical location of "cleared" data may differ from the logical address.

The simulator zeroes newly allocated blocks in `_bitmap_alloc()`:

```python
disk_write(b, bytearray(BLOCK_SIZE))   # zero out newly allocated block
```

This prevents a new file from seeing a previous file's data. But the old file's data is still at the old physical location until it's reused.

---

## Observing with the Simulator

```python
fs.mkfs()

# Create and open a file
fs.touch("/tmp.txt")
fd = _fd_table.open("/tmp.txt", "rw")
_fd_table.write(fd, "secret data")

# Unlink while open
fs.unlink("/tmp.txt")
fs.dump_inodes()    # inode still there with nlink=0, ref=1

# File still readable through fd
print(_fd_table.read(fd))  # prints "secret data"

# Close → triggers free
_fd_table.close(fd)
fs.dump_inodes()    # inode is now UNUSED
fs.explain_block(16)  # data block bytes still visible (not zeroed until reuse)
```
