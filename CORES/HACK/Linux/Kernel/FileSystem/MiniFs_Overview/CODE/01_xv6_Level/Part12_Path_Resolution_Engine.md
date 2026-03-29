# Part 12 — Path Resolution Engine

---

## The Problem: Strings to Inodes

The filesystem API works with paths like `/home/alice/notes.txt`. Everything below the API works with inode numbers. The path resolution engine bridges these two worlds.

Given a path string, it returns the inode at that path — or raises an exception if any component doesn't exist or isn't a directory.

This translation is called **namei** in UNIX. It appears in xv6 as `namei()` and `nameiparent()` in `kernel/fs.c`. The simulator implements both.

---

## The Two Entry Points

### `namei(path)` — resolve path to its inode

```python
def namei(path):
    ip, _ = _namex(path, parent=False)
    return ip
```

Returns the inode for the final component of the path. Used by `stat()`, `read_file()`, `write_file()`, `link()`.

### `nameiparent(path)` — resolve path to parent directory + leaf name

```python
def nameiparent(path):
    ip, name = _namex(path, parent=True)
    return ip, name
```

Returns the inode of the **parent directory** and the name of the final component. Used by `mkdir()`, `touch()`, `link()`, `unlink()`. These operations need to modify the parent directory (add or remove an entry) rather than access the target itself.

Both delegate to the single internal function `_namex()`.

---

## `_skipelem(path)` — Path Component Parser

```python
def _skipelem(path):
    path = path.lstrip("/")
    if not path:
        return "", ""
    slash = path.find("/")
    if slash < 0:
        return path, ""
    return path[:slash], path[slash:]
```

This mirrors xv6 `skipelem()`. It strips leading slashes and splits off the next component:

```
_skipelem("/home/alice/notes.txt")  → ("home", "/alice/notes.txt")
_skipelem("/alice/notes.txt")       → ("alice", "/notes.txt")
_skipelem("/notes.txt")             → ("notes", ".txt")? No—
_skipelem("notes.txt")              → ("notes.txt", "")
```

Actually:
```
_skipelem("alice/notes.txt")  → ("alice", "/notes.txt")
_skipelem("notes.txt")        → ("notes.txt", "")
_skipelem("")                 → ("", "")
```

The return value `("", "")` signals that the path is exhausted.

---

## `_namex(path, parent)` — The Core Walk

```python
def _namex(path, parent):
    if path.startswith("/"):
        ip = iget(INUM_ROOT)   # always start at root (inode 1)
    else:
        raise ValueError("Relative paths not supported — use absolute paths")

    while True:
        name, rest = _skipelem(path.lstrip("/") if path else "")
        if not name:
            if parent:
                iput(ip)
                raise ValueError(f"nameiparent called on root")
            return ip, ""

        # If parent=True and no more components after name → return now
        next_name, _ = _skipelem(rest)
        if parent and not next_name:
            return ip, name

        # Advance: look up name in current directory
        if not ip.is_dir():
            iput(ip)
            raise NotADirectoryError(f"'{name}' is not a directory")

        next_ip, _ = dirlookup(ip, name)
        iput(ip)

        if next_ip is None:
            raise FileNotFoundError(f"'{name}' not found")

        ip   = next_ip
        path = rest
```

The algorithm:

1. Start at root: `iget(INUM_ROOT)`.
2. Loop: parse next component with `_skipelem`.
3. If no more components (`name == ""`): return current inode (for `namei`) or raise (for `nameiparent` on root path).
4. If `parent=True` and this is the last component: return `(current_inode, name)`.
5. Verify current inode is a directory.
6. Call `dirlookup(ip, name)` to find the next inode.
7. Release reference to current inode (`iput`), move to next.
8. Repeat with remaining path.

---

## Tracing a Path Walk

Path: `/home/alice/notes.txt`, called as `namei`.

**Step 1**: Start at root (inode 1). Path = `/home/alice/notes.txt`.

```
_skipelem("home/alice/notes.txt")  → ("home", "/alice/notes.txt")
name = "home"
dirlookup(root, "home") → inode 2 (home dir)
iput(root)
ip = inode 2, path = "/alice/notes.txt"
```

**Step 2**: At inode 2 (home). Path = `/alice/notes.txt`.

```
_skipelem("alice/notes.txt")  → ("alice", "/notes.txt")
name = "alice"
dirlookup(home, "alice") → inode 3 (alice dir)
iput(home)
ip = inode 3, path = "/notes.txt"
```

**Step 3**: At inode 3 (alice). Path = `/notes.txt`.

```
_skipelem("notes.txt")  → ("notes.txt", "")
name = "notes.txt"
next_name = ""  → this is the last component
parent=False → don't stop early
dirlookup(alice, "notes.txt") → inode 4
iput(alice)
ip = inode 4, path = ""
```

**Step 4**: Path is now empty.
```
_skipelem("")  → ("", "")
name = ""      → done
return (inode 4, "")
```

`namei` returns inode 4. Three `dirlookup` calls, three `iput` calls, one inode ref alive (inode 4). The caller must eventually call `iput(inode 4)`.

---

## The Parent Walk for `nameiparent`

Path: `/home/alice/notes.txt`, called as `nameiparent`.

Steps 1 and 2 are identical. At Step 3:

```
name = "notes.txt"
next_name = ""   ← no more components
parent=True      → return now
return (inode 3, "notes.txt")
```

Returns inode 3 (alice's directory) and the string `"notes.txt"`. The caller can then:
- Call `dirlookup(inode3, "notes.txt")` to find the entry (for `unlink`)
- Call `dirlink(inode3, "notes.txt", new_inum)` to add an entry (for `link`, `touch`)

---

## inode Reference Discipline

Every `iget` must be paired with `iput`. The path walk is careful about this:

- At each step, `iput(ip)` is called before `ip = next_ip`.
- If an error occurs (not a directory, not found), `iput(ip)` is called before raising.
- The final inode (the one returned) is **not** `iput`'d — the caller owns it.

This discipline prevents reference leaks (inodes stuck in cache with `ref > 0` forever) and premature frees (inodes freed while still in use). It mirrors xv6's exact reference counting protocol.

---

## Cost of Path Resolution

Each component in the path costs:
- One `dirlookup` call
- One `readi` loop scanning directory entries
- At least one `disk_read` (the directory block)

For a three-component path like `/home/alice/notes.txt`: minimum three disk reads plus whatever `_bmap` needs to traverse indirect blocks. With a warm buffer cache, most of these reads are free (cache hits).

This cost explains why deeply nested paths are slower to resolve on cold cache, and why real kernels aggressively cache directory lookup results (the **dentry cache** or `dcache` in Linux).
