# Part 13 — Filesystem Syscalls (mkdir / link / unlink / create)

---

## The Operations Layer

Below this layer: inodes, directories, path resolution, block allocation — all pure mechanics.

Above this layer: the user types `mkdir /home` or `rm notes.txt`.

This layer bridges them. It implements the high-level operations that correspond directly to UNIX syscalls: `mkdir`, `touch`/`create`, `link`, `unlink`, `write_file`, `read_file`. Each one:

1. Calls `log.begin_op()` to start a transaction
2. Uses `namei`/`nameiparent` to find the relevant inodes
3. Calls directory and inode functions to do the work
4. Calls `log.end_op()` to commit
5. Calls `iput()` on every inode it acquired

This is Section 7 in the simulator, mirroring `kernel/sysfile.c` in xv6.

---

## `mkdir(path)` — Create a Directory

```python
def mkdir(self, path):
    log.begin_op()
    try:
        dp, name = nameiparent(path)
        ip = ialloc(T_DIR)
        ip.nlink = 1
        _iupdate(ip)
        dirlink(ip, ".",  ip.inum)
        dirlink(ip, "..", dp.inum)
        dirlink(dp, name, ip.inum)
        dp.nlink += 1
        _iupdate(dp)
        iput(ip)
        iput(dp)
    except Exception:
        log.end_op()
        raise
    log.end_op()
```

Steps:
1. `nameiparent(path)` — find the parent directory (`dp`) and the new directory's name.
2. `ialloc(T_DIR)` — allocate a new inode of type directory.
3. `nlink = 1` — the new directory is referenced by one name (the entry in `dp`).
4. Add `.` entry (self-reference) and `..` entry (parent).
5. Add the new directory's name to `dp` (the parent).
6. Increment `dp.nlink` — the parent gains a subdirectory, which holds a `..` entry pointing back to it. Each subdirectory adds one hard link to its parent.
7. Update both inodes on disk, release both references.

Why `dp.nlink += 1`? Because the new directory's `..` entry points to `dp`. In UNIX, link count for a directory includes both its name in the parent and the `..` entries of all its subdirectories. A directory with two subdirectories has `nlink = 4`: its own entry in its parent, `.` in itself, and `..` in each of two children.

---

## `_create(path, itype)` — Internal File/Dir Creator

```python
def _create(self, path, itype):
    dp, name = nameiparent(path)

    existing, _ = dirlookup(dp, name)
    if existing is not None:
        iput(dp)
        iput(existing)
        raise FileExistsError(f"{path} already exists")

    ip = ialloc(itype)
    ip.nlink = 1
    _iupdate(ip)

    if itype == T_DIR:
        dp.nlink += 1
        _iupdate(dp)
        dirlink(ip, ".",  ip.inum)
        dirlink(ip, "..", dp.inum)

    dirlink(dp, name, ip.inum)
    iput(dp)
    return ip   # caller must iput
```

A shared helper for `touch()` and directory creation paths. Checks for existing name, allocates inode, adds directory structure if needed, inserts name into parent. Returns the new inode with `ref=1` — the caller is responsible for `iput`.

---

## `touch(path)` — Create an Empty File

```python
def touch(self, path):
    log.begin_op()
    try:
        ip = self._create(path, T_FILE)
        inum = ip.inum
        iput(ip)
    except Exception:
        log.end_op()
        raise
    log.end_op()
    return inum
```

Thin wrapper around `_create`. No data is written — the inode is created with `size=0` and no block pointers. The file exists but occupies zero data blocks.

---

## `link(old_path, new_path)` — Hard Link

```python
def link(self, old_path, new_path):
    log.begin_op()
    try:
        ip = namei(old_path)
        if ip.is_dir():
            iput(ip)
            log.end_op()
            raise IsADirectoryError("Cannot hard-link a directory")
        ip.nlink += 1
        _iupdate(ip)

        dp, name = nameiparent(new_path)
        dirlink(dp, name, ip.inum)
        iput(dp)
        iput(ip)
    except Exception:
        log.end_op()
        raise
    log.end_op()
```

Hard links are one of the cleanest operations in the filesystem:

1. Resolve `old_path` to its inode.
2. Increment `nlink`.
3. Add a new directory entry in `new_path`'s parent pointing to the same inode number.
4. No data is copied. No new inode is allocated.

After this, two paths refer to the same inode. Modifying the file through either path modifies the same data. Deleting either path decrements `nlink` — the file is only freed when `nlink` reaches 0.

Hard links to directories are forbidden because they would create cycles in the directory tree, making path traversal infinite.

---

## `unlink(path)` — Remove a Name

```python
def unlink(self, path):
    log.begin_op()
    try:
        dp, name = nameiparent(path)
        if name in (".", ".."):
            raise ValueError("Cannot unlink . or ..")

        ip, off = dirlookup(dp, name)
        if ip is None:
            raise FileNotFoundError(f"{path} not found")

        if ip.is_dir():
            if ip.size > 2 * DIRENT_SIZE:
                raise OSError(f"{path}: directory not empty")
            dp.nlink -= 1
            _iupdate(dp)

        # Zero out the directory entry
        empty_entry = struct.pack(DIRENT_FMT, 0, b"\x00" * DIRSIZ)
        writei(dp, off, empty_entry)
        log.log_write(_bmap(dp, off // BLOCK_SIZE))

        ip.nlink -= 1
        _iupdate(ip)
        iput(ip)
        iput(dp)
    except Exception:
        log.end_op()
        raise
    log.end_op()
```

Unlink does **not** necessarily free the inode. It:

1. Finds the directory entry (its byte offset `off` in `dp`).
2. For directories: verify empty (only `.` and `..`), decrement parent's `nlink`.
3. Zero out the directory entry (mark as deleted).
4. Decrement `ip.nlink`.
5. Call `iput(ip)`.

In `iput()`:

```python
def iput(ip):
    ip.ref -= 1
    if ip.ref == 0 and ip.nlink == 0:
        _itrunc(ip)
        ip.type = T_UNUSED
        _iupdate(ip)
        _icache.pop(ip.inum, None)
```

If `nlink` is now 0 **and** `ref` is now 0 (no open file descriptors): free the inode. If a process still has the file open (`ref > 0`), the inode stays alive. It will be freed when the last `close()` calls `iput`. This is the deferred-free contract (see Part 18).

---

## Transaction Discipline

Every operation follows the same pattern:

```python
log.begin_op()
try:
    # ... do work ...
    # ... disk_write + log.log_write for each modification ...
except Exception:
    log.end_op()    # commit empty transaction, clear log
    raise
log.end_op()        # commit full transaction
```

The `try/except` ensures `end_op()` is always called even on error. An empty transaction (no `log_write` calls) commits cleanly — the log header is written with `n=0`, which is a no-op.

---

## Summary of Inode State Changes

| Operation       | nlink change     | allocs inode | allocs blocks | frees inode  |
|----------------|------------------|--------------|---------------|--------------|
| `touch`        | +1 (start at 1)  | yes          | no            | no           |
| `mkdir`        | +1               | yes          | 1 (dir data) | no           |
| `link`         | +1               | no           | no            | no           |
| `unlink`       | -1               | no           | no           | if nlink=ref=0|
| `write_file`   | 0                | no           | yes           | no           |
| `read_file`    | 0                | no           | no            | no           |
