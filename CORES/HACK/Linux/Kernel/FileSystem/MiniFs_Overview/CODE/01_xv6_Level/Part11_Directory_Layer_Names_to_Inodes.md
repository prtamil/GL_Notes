# Part 11 — Directory Layer (Names to Inode Mapping)

---

## Directories Are Files

A directory in UNIX is a special type of file. Its type field in the inode is `T_DIR` instead of `T_FILE`. Its contents are not arbitrary bytes — they are a sequence of fixed-size records called directory entries. But it is stored on disk the same way as any file: as blocks pointed to by the inode.

This means the directory layer can use `readi()` and `writei()` for all its I/O. The block structure, the block allocator, the cache — all of that is inherited automatically. The directory layer only adds one new concept: the format of what lives inside those blocks.

---

## The Directory Entry Format

Each directory entry is 16 bytes:

```python
DIRSIZ      = 14
DIRENT_FMT  = f"H{DIRSIZ}s"   # "H14s"
DIRENT_SIZE = struct.calcsize(DIRENT_FMT)  # 2 + 14 = 16 bytes
```

Layout:
```
bytes 0–1:   inum (unsigned short, 2 bytes) — inode number
bytes 2–15:  name (14 bytes, null-padded)   — filename
```

Sixteen bytes per entry, four entries per 64-byte block:
```python
DIRENTS_PER_BLOCK = BLOCK_SIZE // DIRENT_SIZE  # 64 // 16 = 4
```

This is the same format as xv6 `struct dirent` in `kernel/fs.h`.

A deleted entry has `inum == 0`. A name of up to 14 characters is supported. Longer names are silently truncated to 14 bytes when stored.

---

## `dirlookup(dp, name)` — Finding a Name in a Directory

```python
def dirlookup(dp, name):
    assert dp.is_dir(), f"inode {dp.inum} is not a directory"

    for off in range(0, dp.size, DIRENT_SIZE):
        raw = readi(dp, off, DIRENT_SIZE)
        if len(raw) < DIRENT_SIZE:
            break
        inum, name_bytes = struct.unpack(DIRENT_FMT, raw)
        if inum == 0:
            continue   # deleted entry, skip
        entry_name = name_bytes.rstrip(b"\x00").decode("ascii", errors="replace")
        if entry_name == name:
            return iget(inum), off

    return None, 0
```

Linear scan: read each 16-byte entry, skip deleted slots (`inum == 0`), compare names. Return the inode (via `iget`) and the byte offset of the matching entry. The offset is needed by `unlink` to know where to write the deletion marker.

This is O(n) in the number of entries. Real filesystems add hash tables (ext4 htree) or B-trees (btrfs) for large directories. xv6 stays simple.

`iget(inum)` is called on the matching entry — this bumps the inode's ref count. The caller must eventually call `iput()` on the returned inode.

---

## `dirlink(dp, name, inum)` — Adding an Entry

```python
def dirlink(dp, name, inum):
    # Check name doesn't already exist
    existing, _ = dirlookup(dp, name)
    if existing is not None:
        iput(existing)
        raise FileExistsError(f"'{name}' already exists in directory")

    # Find a free slot (inum == 0) or append at end
    off = 0
    for off in range(0, dp.size, DIRENT_SIZE):
        raw = readi(dp, off, DIRENT_SIZE)
        if len(raw) < DIRENT_SIZE:
            break
        inum_slot, _ = struct.unpack(DIRENT_FMT, raw)
        if inum_slot == 0:
            break   # reuse deleted slot
    else:
        off = dp.size   # no free slot found, append

    # Write the new entry
    name_enc = name.encode("ascii")[:DIRSIZ]
    raw = struct.pack(DIRENT_FMT, inum, name_enc)
    writei(dp, off, raw)
    log.log_write(_bmap(dp, off // BLOCK_SIZE))
```

Two passes: first check for duplicates (via `dirlookup`), then find a free slot. A slot is free if its `inum == 0`. If no free slot exists, append at `dp.size`, which causes `writei()` to extend the directory file.

The new entry is packed as binary bytes with `struct.pack` and written with `writei()`. This is a regular file write at the directory level — `writei` handles block allocation and caching.

---

## The `.` and `..` Entries

Every directory contains two special entries:

```
.   → self reference (inum = this directory's inum)
..  → parent reference (inum = parent directory's inum)
```

These are created by `mkdir()` when the directory is first made:

```python
dirlink(ip, ".",  ip.inum)    # . → this dir
dirlink(ip, "..", dp.inum)    # .. → parent dir
```

For the root directory:
```python
dirlink(root, ".", INUM_ROOT)
dirlink(root, "..", INUM_ROOT)
```

Both `.` and `..` point to inode 1. The root's parent is itself.

These entries participate in path traversal: `cd ..` calls `dirlookup` on `..`, which returns the parent directory inode. This is how you navigate up the tree without storing the tree structure explicitly.

---

## Directory Deletion Semantics

`unlink()` removes a directory entry by zeroing its `inum` field:

```python
empty_entry = struct.pack(DIRENT_FMT, 0, b"\x00" * DIRSIZ)
writei(dp, off, empty_entry)
```

The slot is marked free (inum=0) but not removed from the file. The directory's size does not shrink. Future `dirlink()` calls can reuse this slot.

Physical deletion never happens — the bytes remain on disk until overwritten. This is why forensic tools can sometimes recover deleted filenames from a disk image: the name bytes may still be present even after the inum was zeroed.

---

## Directory Size and Empty-Directory Check

A freshly created directory contains exactly two entries (`.` and `..`):

```
dp.size = 2 × DIRENT_SIZE = 32 bytes
```

`unlink()` checks if a directory is empty before allowing deletion:

```python
if ip.size > 2 * DIRENT_SIZE:  # more than just . and ..
    raise OSError(f"{path}: directory not empty")
```

This is the standard UNIX behavior: you cannot `rmdir` a non-empty directory.

---

## The Naming Limit

Directory entry names are limited to 14 bytes (`DIRSIZ = 14`). This comes directly from xv6, which mirrors the original UNIX V6 limit. Modern filesystems use longer names (255 bytes in ext4) with variable-length directory entries. xv6 uses fixed-length entries for simplicity: fixed length means you can index into the directory by multiplying by `DIRENT_SIZE`, with no need to parse variable-length records.
