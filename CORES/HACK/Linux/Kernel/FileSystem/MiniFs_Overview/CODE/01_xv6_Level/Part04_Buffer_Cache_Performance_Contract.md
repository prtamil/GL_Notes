# Part 4 — Buffer Cache (Performance Contract)

---

## The Problem: Disk Is Slow

Every disk read takes microseconds to milliseconds. A path traversal like `/home/alice/notes.txt` touches at least three directory blocks plus three inode blocks — six disk reads minimum. If the inode for the root directory is read separately by every component of that path, you multiply the cost by three.

The buffer cache solves this. Its job is simple: **keep recently used blocks in RAM and hand them out instead of going to disk**.

This is the performance contract: the filesystem will not re-read a block from disk if it already has a valid copy in the cache.

---

## The xv6 Buffer Cache Design

In xv6, the buffer cache (`kernel/bio.c`) is a fixed-size pool of `struct buf` entries, organized as a doubly-linked LRU list. Each `struct buf` holds one block and has a reference count.

The simulator implements the same semantics with a Python dict:

```python
class BufEntry:
    __slots__ = ('data', 'dirty', 'refcnt', 'valid')
    def __init__(self, data):
        self.data   = bytearray(data)
        self.dirty  = False
        self.refcnt = 1
        self.valid  = True

class BufferCache:
    def __init__(self):
        self._cache  = {}   # blockno → BufEntry
        self.hits    = 0
        self.misses  = 0
        self.flushes = 0
```

`NBUF = 30` mirrors xv6's cache size (xv6 uses 30 in the RISC-V version).

---

## The Four Core Operations

### `bread(blockno)` — get a block

```python
def bread(self, blockno):
    if blockno in self._cache:
        e = self._cache[blockno]
        e.refcnt += 1
        self.hits += 1
        return bytearray(e.data)  # return copy

    self.misses += 1
    raw = _raw_read(blockno)       # cache miss → go to disk
    e   = BufEntry(raw)
    self._cache[blockno] = e
    return bytearray(e.data)
```

Cache hit: increment `refcnt`, return a copy of the cached data. No disk I/O.

Cache miss: call `_raw_read()` which goes through the controller to the platter. Store result in cache. Future reads hit the cache.

The returned data is a **copy**, not the cache entry itself. This prevents callers from accidentally modifying the cache by writing into the returned buffer.

### `bwrite(blockno, data)` — mark a block dirty

```python
def bwrite(self, blockno, data):
    buf = bytearray(BLOCK_SIZE)
    buf[:len(data)] = data
    if blockno in self._cache:
        self._cache[blockno].data  = buf
        self._cache[blockno].dirty = True
    else:
        e = BufEntry(buf)
        e.dirty = True
        self._cache[blockno] = e
```

`bwrite` does **not** write to disk. It updates the in-memory cache entry and marks it dirty. The actual disk write happens later when `bflush` or `bsync` is called.

This separation — updating cache vs. writing to disk — is what allows the log layer to batch multiple block writes into a single atomic transaction.

### `brelse(blockno)` — release hold on a block

```python
def brelse(self, blockno):
    if blockno in self._cache:
        self._cache[blockno].refcnt -= 1
```

Mirrors xv6 `brelse()`. Decrements the reference count. When `refcnt` reaches zero, the block becomes eligible for eviction (the simulator doesn't implement eviction since the dict grows as needed, but the semantics are preserved for correctness).

Every `bread()` must be paired with a `brelse()`. This is the resource discipline of the buffer cache.

### `bpin(blockno)` / `bunpin(blockno)` — prevent eviction

```python
def bpin(self, blockno):
    if blockno in self._cache:
        self._cache[blockno].refcnt += 1

def bunpin(self, blockno):
    if blockno in self._cache:
        self._cache[blockno].refcnt -= 1
```

The log layer calls `bpin()` on every block registered with `log_write()`. This prevents the buffer cache from evicting a modified block before the transaction commits. Without pinning, a cache eviction could flush a partially-written block to its home location before the log header is written — corrupting the atomicity guarantee.

After commit, `bunpin()` releases all pinned blocks.

---

## The Flush Operations

### `bflush(blockno)` — flush one block to disk

```python
def bflush(self, blockno):
    e = self._cache.get(blockno)
    if e and e.dirty:
        _raw_write(blockno, e.data)
        e.dirty = False
        self.flushes += 1
```

Writes one dirty block to its disk location and clears the dirty flag. Called by the log layer during commit to write log data blocks.

### `bsync()` — flush all dirty blocks

```python
def bsync(self):
    for blockno, e in self._cache.items():
        if e.dirty:
            _raw_write(blockno, e.data)
            e.dirty = False
```

Equivalent to Linux `writeback` — forces all dirty cache entries to disk. Used less often than `bflush` in normal operation.

---

## How the Filesystem Uses the Cache

The filesystem wraps the buffer cache in two thin functions:

```python
def disk_read(blockno):
    return bcache.bread(blockno)

def disk_write(blockno, data):
    bcache.bwrite(blockno, data)
```

Every filesystem function — `iget`, `dirlookup`, `_bitmap_alloc`, `readi`, `writei` — calls `disk_read` and `disk_write`. They all go through the cache. None of them ever call `_raw_read` or `_raw_write` directly.

After a `disk_read`, the caller must call `bcache.brelse(blockno)` to release the reference. This pattern appears throughout the code:

```python
raw = disk_read(blk)
bcache.brelse(blk)           # release immediately after reading
# ... use the data ...
```

---

## Cache Statistics

The buffer cache tracks three metrics:

```
hits    — how many bread() calls returned from cache
misses  — how many bread() calls required a disk read
flushes — how many dirty blocks were written to disk
```

Run `fs.cache()` to see the current state:

```
[bcache]  12 entries  hits=34 misses=12 dirty=3 flushes=9
  BLK  REF  DIRTY  HEX[0:16]
    1    0     no  40302010...
    7    0     no  02000000...
   15    0    YES  ffff0000...
```

A high hit rate means the filesystem is doing most of its work from RAM. The dirty column shows which blocks have pending writes that haven't been committed yet.

---

## Connection to Real Systems

The buffer cache in xv6 is a simplified version of the Linux page cache. In Linux, the page cache holds not just disk blocks but also file contents mapped directly into virtual memory. The same `dirty` / `writeback` / `pin` concepts apply.

PostgreSQL has its own buffer pool (`shared_buffers`) that works on exactly the same principle — a fixed-size pool of fixed-size pages, with ref counts, dirty flags, and LRU eviction. The terminology differs but the contract is identical: read from disk once, serve subsequent reads from RAM, flush on commit.
