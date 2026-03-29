# Part 14 — File Descriptor Table (Process Interface)

---

## What File Descriptors Are

When a process calls `open("/home/alice/notes.txt", O_RDWR)`, the kernel returns an integer — say, `3`. That integer is a **file descriptor**. The process uses `3` for every subsequent `read`, `write`, `seek`, and `close`. The integer hides all the complexity below it.

The file descriptor table is the data structure that maps these integers to actual filesystem state. It is the outermost layer of the filesystem stack — the interface that processes see.

In xv6, this is `kernel/file.c`. In the simulator, it is Section 8: the `FDTable` class.

---

## What the FD Table Stores

Each open file descriptor holds:

```python
{
    'inum':     int,   # which inode
    'offset':   int,   # current read/write position (bytes from start)
    'readable': bool,  # open for reading?
    'writable': bool,  # open for writing?
    'ref':      int,   # reference count (for dup)
}
```

This mirrors xv6 `struct file`:
```c
struct file {
    enum { FD_NONE, FD_PIPE, FD_INODE, FD_DEVICE } type;
    int ref;
    char readable;
    char writable;
    struct inode *ip;
    uint off;
};
```

The key field is `offset` — the current read/write position. This is per-open-file-description, not per-inode. Two processes that independently `open()` the same file each get their own `offset`. Two file descriptors from `dup()` share an inode but maintain independent offsets (in the simulator's implementation; the POSIX dup2 behavior is slightly different but the structure is the same).

---

## `open(path, flags)` — Allocating a File Descriptor

```python
def open(self, path, flags="r"):
    readable = "r" in flags
    writable = "w" in flags

    log.begin_op()
    try:
        try:
            ip = namei(path)
        except FileNotFoundError:
            if not writable:
                raise
            # O_CREATE path: file doesn't exist, writable → create it
            dp, name = nameiparent(path)
            ip = ialloc(T_FILE)
            ip.nlink = 1
            _iupdate(ip)
            dirlink(dp, name, ip.inum)
            iput(dp)

        if ip.is_dir() and writable:
            iput(ip)
            raise IsADirectoryError(f"{path} is a directory")
    except Exception:
        log.end_op()
        raise
    log.end_op()

    fd = self._next_fd
    self._next_fd += 1
    self._table[fd] = {
        'inum': ip.inum, 'offset': 0,
        'readable': readable, 'writable': writable, 'ref': 1
    }
    return fd
```

The `open()` call combines two behaviors:

- **Read mode** (`"r"`): resolve path, verify it exists, return fd.
- **Write mode** (`"w"`): resolve path. If it doesn't exist, create it (the O_CREAT behavior). If it does exist, open it (not truncated — use `write_file` for overwrite).

The `_next_fd` counter starts at 3 (0=stdin, 1=stdout, 2=stderr are reserved by convention). Each `open()` increments it. In a real OS, fd numbers are reused after `close()` — the simulator simplifies by not reusing.

The inode reference from `iget` (inside `namei` or `ialloc`) is **held alive** for the duration of the open file. This is what prevents the inode from being freed while the file is open.

---

## `read(fd, n)` — Reading Through a File Descriptor

```python
def read(self, fd, n=None):
    entry = self._table.get(fd)
    if not entry: raise OSError(f"fd {fd} not open")
    if not entry['readable']: raise PermissionError(f"fd {fd} not readable")

    ip = iget(entry['inum'])
    if n is None: n = ip.size - entry['offset']
    data = readi(ip, entry['offset'], n)
    entry['offset'] += len(data)
    iput(ip)
    return data.decode("utf-8", errors="replace")
```

Steps:
1. Look up the fd entry, check permissions.
2. Get the inode (`iget`).
3. Call `readi(ip, offset, n)` — the low-level read from Part 10.
4. Advance `entry['offset']` by the number of bytes read.
5. Release the inode (`iput`).

The offset advances automatically. A second `read(fd, 10)` reads the next 10 bytes, not the same 10. This is stateful I/O — the state lives in `entry['offset']`.

---

## `write(fd, data)` — Writing Through a File Descriptor

```python
def write(self, fd, data):
    if isinstance(data, str): data = data.encode("utf-8")
    entry = self._table.get(fd)
    ip = iget(entry['inum'])
    log.begin_op()
    try:
        n = writei(ip, entry['offset'], data)
    except Exception:
        log.end_op()
        iput(ip)
        raise
    log.end_op()
    entry['offset'] += n
    iput(ip)
```

Like `read`, but calls `writei` and wraps in `begin_op`/`end_op` (writes require a transaction). The offset advances by the number of bytes written.

---

## `seek(fd, offset, whence)` — Repositioning

```python
def seek(self, fd, offset, whence=0):
    entry = self._table.get(fd)
    ip = iget(entry['inum'])
    if   whence == 0: new_off = offset              # SEEK_SET
    elif whence == 1: new_off = entry['offset'] + offset  # SEEK_CUR
    elif whence == 2: new_off = ip.size + offset    # SEEK_END
    iput(ip)
    entry['offset'] = new_off
```

Standard lseek(2) semantics. `SEEK_END` requires reading the inode's current size. The offset is set without any I/O. Reading after a seek simply passes the new offset to `readi`.

---

## `dup(fd)` — Duplicating a File Descriptor

```python
def dup(self, fd):
    entry = self._table.get(fd)
    new_fd = self._next_fd
    self._next_fd += 1
    ip = iget(entry['inum'])   # hold another inode ref for new_fd
    self._table[new_fd] = dict(entry)
    self._table[new_fd]['offset'] = 0   # independent offset
    return new_fd
```

`dup` creates a new fd pointing to the same inode. Both fds share the same inode (same `inum`) but have independent `offset` values. The inode's `ref` count is bumped by `iget` — both fds hold a reference, and both must be closed before the inode ref drops to zero.

---

## `close(fd)` — Releasing the File Descriptor

```python
def close(self, fd):
    entry = self._table.pop(fd, None)
    if not entry: raise OSError(f"fd {fd} not open")

    inum = entry['inum']
    if inum in _icache:
        ip = _icache[inum]
        iput(ip)   # release the fd's held inode reference
```

Removes the fd entry from the table. Then calls `iput()` on the inode to release the reference held since `open()`. If `iput` finds `nlink == 0 && ref == 0`, it frees the inode (the deferred-free path).

---

## The Offset is the Key Insight

The file descriptor table's most important contribution is per-open-file state. Consider what happens without it:

- `read(fd, 10)` would need to know where to start reading.
- Multiple processes reading the same file would interfere with each other.
- `seek` would have nowhere to store the position.

The offset in the fd entry solves all three. Each `open()` creates an independent cursor. Processes can read the same file simultaneously without interfering. The position is preserved between reads.

This is why the file descriptor table exists as a separate layer rather than being merged into the inode: the inode is a shared, on-disk object. The file descriptor is a per-open, per-process, ephemeral object. Mixing their lifetimes would complicate the design enormously.

---

## Inspecting the FD Table

```python
_fd_table.dump()
```

Output:
```
[fds]  Open file table (2/20):
  FD  INUM     FLAGS  OFFSET
   3     4        r-       0
   4     4        rw      64
```

Two fds pointing to inode 4 (same file): one read-only at position 0, one read-write at position 64. This would happen after `open` + `dup` + `seek`. The `ls()` output also shows FDS count per inode — how many file descriptors currently reference each file.
